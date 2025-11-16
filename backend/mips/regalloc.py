# backend/mips/regalloc.py
"""
Asignador de registros con spill a stack (Tarea 4)
- get(name) mapea nombres TAC a $t0..$t9 con política LRU.
- Si no hay libre, hace spill del registro víctima a un slot negativo desde $fp.
- temp_acquire()/temp_release() para temporales efímeros (li/la/operaciones).
- start_function(spill_bytes_hint) devuelve bytes sugeridos para el frame.
"""

from typing import Dict, Optional, Set, Tuple, List

class RegAlloc:
    _TREGS = [f"$t{i}" for i in range(10)]  # $t0..$t9

    def __init__(self):
        self._name2reg: Dict[str, str] = {}
        self._reg2name: Dict[str, str] = {}
        self._dirty: Set[str] = set()
        self._pinned: Set[str] = set()
        self._use_tick: int = 0
        self._last_use: Dict[str, int] = {}
        self._spill_slot: Dict[str, int] = {}
        self._spill_next_off: int = -4
        self._temp_inuse: Set[str] = set()
        self._tregs_free: List[str] = self._TREGS[:]
        self._frame_spill_limit: int = 0
        self._frame_spill_used: int = 0

    # -------- ciclo de vida --------
    def start_function(self, spill_bytes_hint: int = 256) -> int:
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

    # -------- internos --------
    def _touch(self, reg: str):
        self._use_tick += 1
        self._last_use[reg] = self._use_tick

    def _alloc_spill_slot(self, name: str) -> int:
        if name in self._spill_slot:
            return self._spill_slot[name]
        # reserva 4 bytes
        off = self._spill_next_off
        self._spill_next_off -= 4
        self._frame_spill_used += 4
        self._spill_slot[name] = off
        return off

    def _choose_victim_reg(self) -> Optional[str]:
        candidates = []
        for reg, name in self._reg2name.items():
            if reg in self._pinned or reg in self._temp_inuse:
                continue
            ts = self._last_use.get(reg, 0)
            candidates.append((ts, reg))
        if not candidates:
            return None
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]

    def _spill_reg(self, reg: str, store_value: bool = True) -> None:
        if reg not in self._reg2name:
            return
        name = self._reg2name[reg]
        # Nota: el emitter realiza el 'sw' cuando materializa desde spill.
        self._name2reg.pop(name, None)
        self._reg2name.pop(reg, None)
        self._dirty.discard(name)
        self._last_use.pop(reg, None)
        if reg not in self._temp_inuse and reg in self._TREGS and reg not in self._tregs_free:
            self._tregs_free.append(reg)

    # -------- API --------
    def get(self, name: str, for_write: bool = False) -> str:
        if name in self._name2reg:
            reg = self._name2reg[name]
            self._touch(reg)
            if for_write: self._dirty.add(name)
            return reg

        if self._tregs_free:
            reg = self._tregs_free.pop(0)
        else:
            victim = self._choose_victim_reg()
            if victim is None:
                victim = self._TREGS[-1]
            self._spill_reg(victim, store_value=True)
            reg = victim

        self._name2reg[name] = reg
        self._reg2name[reg] = name
        self._touch(reg)
        if for_write: self._dirty.add(name)
        return reg

    def has_spill_slot(self, name: str) -> bool:
        return name in self._spill_slot

    def spill_slot_offset(self, name: str) -> int:
        return self._alloc_spill_slot(name)

    def mark_dirty(self, name: str):
        self._dirty.add(name)

    # temporales efímeros
    def temp_acquire(self) -> str:
        if self._tregs_free:
            reg = self._tregs_free.pop(0)
            self._temp_inuse.add(reg)
            self._touch(reg)
            return reg
        victim = self._choose_victim_reg()
        if victim is None: victim = self._TREGS[-1]
        self._spill_reg(victim, store_value=True)
        self._temp_inuse.add(victim)
        self._touch(victim)
        return victim

    def temp_release(self, reg: str):
        if reg in self._temp_inuse:
            self._temp_inuse.remove(reg)
            if reg not in self._reg2name and reg in self._TREGS and reg not in self._tregs_free:
                self._tregs_free.append(reg)

    # pin/unpin (opcional)
    def pin(self, reg: str):
        if reg in self._TREGS: self._pinned.add(reg)
    def unpin(self, reg: str):
        self._pinned.discard(reg)
