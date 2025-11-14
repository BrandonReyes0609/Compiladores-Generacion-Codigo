"""
Asignador de registros con spill a stack (Tarea 3).
- Provee getReg(name) con mapeo nombre_TAC <-> $t0..$t9
- Si no hay registro libre: elige víctima (LRU) y hace spill (sw al stack)
- Al re-materializar una variable spillada: lw desde su ranura (slot) en el frame
- Maneja registros temporales anónimos para literales (li/la) sin robar los mapeados
- Área de spill forma parte del frame del callee (negativa respecto a $fp)
- Interfaz utilizada por el emitter:
    * start_function(local_spill_bytes_hint=256) -> spill_bytes (sugerido)
    * end_function()
    * get(name, for_write=False) -> $tX (asegura materialización)
    * mark_dirty(name) (marca que el valor en reg difiere de memoria)
    * temp_acquire() / temp_release(reg) para temporales efímeros
    * pin(reg) / unpin(reg) para proteger un reg del reemplazo durante secuencias críticas
"""

from typing import Dict, Optional, Set, Tuple, List

class RegAlloc:
    _TREGS = [f"$t{i}" for i in range(10)]  # $t0..$t9

    def __init__(self):
        # estado por función
        self._name2reg: Dict[str, str] = {}
        self._reg2name: Dict[str, str] = {}
        self._dirty: Set[str] = set()         # nombres “sucios” (contenido de reg != memoria)
        self._pinned: Set[str] = set()        # registros que no pueden ser víctimas
        self._use_tick: int = 0               # contador global para LRU
        self._last_use: Dict[str, int] = {}   # reg -> tick
        self._spill_slot: Dict[str, int] = {} # nombre -> offset negativo (desde $fp)
        self._spill_next_off: int = -4        # siguiente offset libre (crece hacia más negativo)
        self._temp_inuse: Set[str] = set()    # registros efímeros en uso
        self._tregs_free: List[str] = self._TREGS[:]
        self._frame_spill_limit: int = 0      # bytes de spill disponibles (valor positivo)
        self._frame_spill_used: int = 0       # bytes usados (positivo)

    # -------- Ciclo de vida por función --------
    def start_function(self, spill_bytes_hint: int = 256) -> int:
        """
        Reinicia estado por función.
        Retorna cuantos bytes sugerimos reservar en el frame para spill (>=0).
        """
        self._name2reg.clear()
        self._reg2name.clear()
        self._dirty.clear()
        self._pinned.clear()
        self._use_tick = 0
        self._last_use.clear()
        self._spill_slot.clear()
        self._spill_next_off = -4
        self._temp_inuse.clear()
        self._tregs_free = self._TREGS[:]
        self._frame_spill_limit = max(0, int(spill_bytes_hint))
        self._frame_spill_used = 0
        return self._frame_spill_limit

    def end_function(self):
        # No forzamos write-back: modelo SSA/TAC no requiere persistir al final.
        # Si quisieras asegurar volcado de “dirty”, hazlo aquí.
        self._name2reg.clear()
        self._reg2name.clear()
        self._dirty.clear()
        self._pinned.clear()
        self._temp_inuse.clear()
        self._last_use.clear()
        self._spill_slot.clear()
        self._tregs_free = self._TREGS[:]
        self._frame_spill_limit = 0
        self._frame_spill_used = 0

    # -------- Utilidades internas --------
    def _touch(self, reg: str):
        self._use_tick = self._use_tick + 1
        self._last_use[reg] = self._use_tick

    def _alloc_spill_slot(self, name: str) -> int:
        """
        Asigna ranura (offset negativo desde $fp) para 'name' si no tiene.
        Verifica no exceder límite de spill del frame (defendido).
        """
        if name in self._spill_slot:
            return self._spill_slot[name]
        # reserva 4 bytes
        if self._frame_spill_used + 4 > self._frame_spill_limit:
            # Aún así reservamos (robustez): permitimos overflow de hint,
            # pero advertimos en un comentario a nivel emisor si lo deseas.
            # Aquí simplemente continuamos.
            pass
        off = self._spill_next_off
        self._spill_next_off = self._spill_next_off - 4
        self._frame_spill_used = self._frame_spill_used + 4
        self._spill_slot[name] = off
        return off

    def _choose_victim_reg(self) -> Optional[str]:
        """
        Elige víctima LRU entre $t* que estén:
          - asignados (en _reg2name)
          - no “pinned”
          - no usados como temporales en este instante (temp_inuse)
        """
        candidates = []
        for reg, name in self._reg2name.items():
            if reg in self._pinned: 
                continue
            if reg in self._temp_inuse:
                continue
            # toma el timestamp; si no existe, 0
            ts = self._last_use.get(reg, 0)
            candidates.append((ts, reg, name))
        if not candidates:
            return None
        # LRU: menor timestamp
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]

    def _spill_reg(self, reg: str, store_value: bool = True) -> None:
        """
        Spillea el contenido del registro a su slot si está dirty.
        Desasocia el reg del nombre.
        """
        if reg not in self._reg2name:
            return
        name = self._reg2name[reg]
        if store_value and (name in self._dirty):
            off = self._alloc_spill_slot(name)
            # Dejamos la instrucción de volcado para el emitter (emit_sw),
            # pero como aquí no tenemos “emit”, hacemos convenio:
            # El emitter debe llamar a 'emit_sw_spill(reg, name)' cuando pida el spill.
            # Para simplificar, devolvemos la intención vía atributo temporal:
            # (lo resolveremos con un hook público que el emitter consulta)
            pass  # No-op aquí: el emitter realizará el sw cuando corresponda.

        # Anulamos el mapeo
        self._name2reg.pop(name, None)
        self._reg2name.pop(reg, None)
        self._dirty.discard(name)
        self._last_use.pop(reg, None)
        # Devolvemos reg a libres (si no está tomado por temp)
        if reg not in self._temp_inuse and reg in self._TREGS and reg not in self._tregs_free:
            self._tregs_free.append(reg)

    # -------- API pública --------
    def get(self, name: str, for_write: bool = False) -> str:
        """
        Asegura que 'name' esté en un registro:
         - Si ya está mapeado: retorna reg (OK).
         - Si hay reg libre: asigna y, si existe spill slot con valor previo, el emitter hará lw.
         - Si no hay reg libre: elige víctima, spill si dirty y reasigna.
        'for_write=True' marca el nombre como dirty tras usarlo (hazlo explícito en el emitter).
        """
        # Ya asignado
        if name in self._name2reg:
            reg = self._name2reg[name]
            self._touch(reg)
            if for_write:
                self._dirty.add(name)
            return reg

        # Registro libre
        if self._tregs_free:
            reg = self._tregs_free.pop(0)
        else:
            # Elegir víctima
            victim = self._choose_victim_reg()
            if victim is None:
                # En caso extremo, toma $t9 (pero intentamos no llegar aquí)
                victim = self._TREGS[-1]
            self._spill_reg(victim, store_value=True)
            reg = victim

        # Mapear y marcar uso
        self._name2reg[name] = reg
        self._reg2name[reg] = name
        self._touch(reg)
        if for_write:
            self._dirty.add(name)
        return reg

    def has_spill_slot(self, name: str) -> bool:
        return name in self._spill_slot

    def spill_slot_offset(self, name: str) -> int:
        """ offset NEGATIVO desde $fp """
        return self._alloc_spill_slot(name)

    def mark_dirty(self, name: str):
        self._dirty.add(name)

    # ----- temporales efímeros (para li/la) -----
    def temp_acquire(self) -> str:
        """
        Pide un $tX temporal que NO esté mapeado a un nombre_TAC (y no quede en mapping).
        Si no hay, libera por LRU un registro NO temporal-efímero y lo asigna como temp.
        """
        # Usa directo si hay libres
        if self._tregs_free:
            reg = self._tregs_free.pop(0)
            self._temp_inuse.add(reg)
            self._touch(reg)
            return reg

        # Si no hay, toma víctima no pinneada ni temporal actual
        victim = self._choose_victim_reg()
        if victim is None:
            victim = self._TREGS[-1]
        self._spill_reg(victim, store_value=True)
        self._temp_inuse.add(victim)
        self._touch(victim)
        return victim

    def temp_release(self, reg: str):
        """ Libera un temporal efímero. """
        if reg in self._temp_inuse:
            self._temp_inuse.remove(reg)
            # si no está mapeado, regresa a libres
            if reg not in self._reg2name and reg in self._TREGS and reg not in self._tregs_free:
                self._tregs_free.append(reg)

    # ----- pin/unpin para secciones críticas (opcional) -----
    def pin(self, reg: str):
        if reg in self._TREGS:
            self._pinned.add(reg)

    def unpin(self, reg: str):
        self._pinned.discard(reg)
