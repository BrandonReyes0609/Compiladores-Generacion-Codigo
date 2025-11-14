# backend/mips/emitter.py
"""
MIPSEmitter — Tareas 2 y 3 integradas (versión mejorada)
--------------------------------------------------------
Convenciones (ABI simple):
- $a0..$a3: primeros 4 argumentos.
- Argumentos >= 4: los empuja el CALLER en su stack justo antes del 'jal'.
- $v0: valor de retorno.
- $t0..$t9: caller-save (se salvan y restauran alrededor de cada 'jal').

Frame del CALLEE:
    addiu $sp, $sp, -FRAME
    sw   $ra, FRAME-4($sp)
    sw   $fp, FRAME-8($sp)
    addu $fp, $sp, $zero
  donde FRAME = align(locals + spill_hint + 8, 8)

Acceso a parámetros en el CALLEE:
- LoadParam i:
    i in [0..3]  -> $a i
    i >= 4       -> lw rd,  fp + FRAME + 4*(i-4)   (extras que dejó el CALLER)

Spill:
- El RegAlloc proporciona slots de spill NEGATIVOS desde $fp.
- Al materializar una variable con slot, hacemos 'lw reg, off($fp)' (lazy load).
- Los literales inmediatos/strings usan temporales efímeros (temp_acquire/release).

Mejoras clave:
- Asignación a campos sin punto en LHS: 'campo = expr' se trata como 'this.campo = expr'.
- Lectura de nombres ambiguos de campo en RHS:
    * si existe 'p_campo' visible (parámetro), usa ese;
    * en caso contrario, usa 'this.campo'.
- Llamadas 'method X': reordena argumentos para poner el receptor (último Param) en $a0.
- Cada 'Param' se congela en un temporal independiente para evitar que se pisen antes del 'jal'.
"""

from .regalloc import RegAlloc


class MIPSEmitter:
    SAVE_T_REGS = True  # caller-save para $t0..$t9

    # Offsets de ejemplo (ajústalo por clase si tienes layouts distintos)
    _FIELD_OFFSETS = {
        "nombre": 0,    # ptr
        "edad":   4,    # int
        "color":  8,    # ptr
        "grado":  12,   # int
    }

    def __init__(self):
        self.lines = []
        self.current_func = None
        self.stack_size = 0
        self.label_counter = 0

        self.regs = RegAlloc()   # asignador con spill
        self.str_pool = {}       # texto -> etiqueta .data
        self.str_count = 0

        self._loaded = set()       # nombres TAC ya cargados desde spill en esta función
        self._pending_args = []    # lista de (idx, reg_congelado)
        self._func_seen = {}       # nombre original -> contador de sobrecargas
        self._func_mangle = {}     # nombre original -> nombre mangled
        self._seen_locals = set()  # variables vistas/definidas en la función (incluye p_*)

    # -------- utilidades base --------
    def emit(self, s):
        self.lines.append(s)

    def c(self, s):
        self.emit("# " + s)

    def emit_preamble(self):  # hook por si quieres emitir start-up
        return

    def uniq_label(self, base="L"):
        self.label_counter = self.label_counter + 1
        return base + str(self.label_counter)

    def _align(self, n, a=8):
        return ((n + a - 1) // a) * a

    def _esc(self, s):
        return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n") + "\""

    def _str_label(self, text):
        if text in self.str_pool:
            return self.str_pool[text]
        lab = "STR_" + str(self.str_count)
        self.str_count = self.str_count + 1
        self.str_pool[text] = lab
        return lab

    # -------- secciones/data --------
    def _emit_data(self):
        if not self.str_pool:
            return []
        out = [".data"]
        # Dicts en Py3 preservan orden de inserción (determinista)
        for s, lab in self.str_pool.items():
            out.append(lab + ": .asciiz " + self._esc(s))
        return out

    # -------- prólogo/epílogo --------
    def begin_function(self, name, local_bytes=0):
        # mangle para sobrecargas (constructor, etc.)
        orig = name
        if orig in self._func_seen:
            self._func_seen[orig] = self._func_seen[orig] + 1
            name = orig + "$" + str(self._func_seen[orig])
        else:
            self._func_seen[orig] = 0
        self._func_mangle[orig] = name

        self.current_func = name
        self._loaded.clear()
        self._pending_args = []
        self._seen_locals = set()

        spill_hint = self.regs.start_function(spill_bytes_hint=256)
        real_locals = local_bytes + spill_hint

        self.stack_size = self._align(real_locals + 8)
        self.emit("\n# --- Función " + name + " ---")
        self.emit(".text")
        if name == "main":
            self.emit(".globl main")
        self.emit(name + ":")
        self.emit("  addiu $sp, $sp, -" + str(self.stack_size))
        self.emit("  sw   $ra, " + str(self.stack_size - 4) + "($sp)")
        self.emit("  sw   $fp, " + str(self.stack_size - 8) + "($sp)")
        self.emit("  addu $fp, $sp, $zero")

    def end_function(self):
        self.emit("  lw   $ra, " + str(self.stack_size - 4) + "($sp)")
        self.emit("  lw   $fp, " + str(self.stack_size - 8) + "($sp)")
        self.emit("  addiu $sp, $sp, " + str(self.stack_size))
        self.emit("  jr   $ra")
        self.emit("  nop")
        self.current_func = None
        self.regs.end_function()
        self._pending_args = []

    # -------- helpers de temporales --------
    def _is_temp(self, r):
        return isinstance(r, str) and r.startswith("$t")

    def _release_if_temp(self, r):
        if self._is_temp(r):
            self.regs.temp_release(r)

    # -------- materialización segura --------
    def _imm(self, val):
        r = self.regs.temp_acquire()
        self.emit("  li   " + r + ", " + str(val))
        return r

    def _mat(self, x):
        """
        Materializa 'x' (inmediato, string, nombre TAC o 'obj.campo') en un registro.
        Prioridad importante:
          1) literales con comillas
          2) 'this'
          3) booleanos / enteros
          4) nombre de campo sin punto (prefiere p_campo; si no, this.campo)
          5) 'obj.campo'
          6) nombre TAC
        """
        # inmediato (int)
        if isinstance(x, int):
            return self._imm(x)

        if isinstance(x, str):
            s = x.strip()

            # 1) literal string (con comillas) — manejar ANTES que '.'
            if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
                lab = self._str_label(s[1:-1])
                r = self.regs.temp_acquire()
                self.emit("  la   " + r + ", " + lab)
                return r

            # 2) 'this' en métodos (objeto actual)
            if s == "this":
                return "$a0"

            # 3) booleanos/enteros
            if s == "true":
                return self._imm(1)
            if s == "false":
                return self._imm(0)
            if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
                return self._imm(int(s))

            # 4) nombre igual a un campo, sin punto: usa p_<campo> si existe; si no, this.<campo>
            if "." not in s and s in self._FIELD_OFFSETS:
                alt = "p_" + s
                if alt in self._seen_locals:
                    regp = self.regs.get(alt, for_write=False)
                    self._ensure_loaded(alt, regp)
                    return regp
                off = self._FIELD_OFFSETS[s]
                r = self.regs.temp_acquire()
                self.emit("  lw   " + r + ", " + str(off) + "($a0)")
                return r

            # 5) acceso con punto: obj.campo
            if "." in s:
                left, right = s.split(".", 1)
                # base
                if left == "this":
                    base = "$a0"
                    base_is_temp = False
                else:
                    base = self._mat(left)
                    base_is_temp = self._is_temp(base)
                # offset
                off = self._FIELD_OFFSETS.get(right, None)
                if off is None:
                    self.c("campo desconocido '" + right + "', usando offset 0")
                    off = 0
                r = self.regs.temp_acquire()
                self.emit("  lw   " + r + ", " + str(off) + "(" + base + ")")
                if base_is_temp:
                    self.regs.temp_release(base)
                return r

            # 6) nombre TAC (variable)
            reg = self.regs.get(s, for_write=False)
            self._ensure_loaded(s, reg)
            return reg

        # fallback: 0
        r = self.regs.temp_acquire()
        self.emit("  move " + r + ", $zero")
        return r

    def _ensure_loaded(self, name, reg):
        if name in self._loaded:
            return
        if self.regs.has_spill_slot(name):
            off = self.regs.spill_slot_offset(name)  # offset NEGATIVO desde $fp
            self.emit("  lw   " + reg + ", " + str(off) + "($fp)")
        self._loaded.add(name)

    # -------- emisión básica --------
    def emit_label(self, L):
        self.emit(L + ":")

    def emit_goto(self, L):
        self.emit("  b " + L)
        self.emit("  nop")

    def emit_ifz(self, src, L):
        r = self._mat(src)
        self.emit("  beq  " + r + ", $zero, " + L)
        self.emit("  nop")
        self._release_if_temp(r)

    def emit_assign(self, dst, src):
        # LHS campo simple -> this.campo = src
        if isinstance(dst, str) and ('.' not in dst) and (dst in self._FIELD_OFFSETS):
            self.emit_setprop("this", dst, src)
            return

        # Asignación normal a variable local/TAC
        if isinstance(dst, str):
            self._seen_locals.add(dst)

        rd = self.regs.get(dst, for_write=True)
        rs = self._mat(src)
        self.emit("  addu " + rd + ", " + rs + ", $zero")
        self._release_if_temp(rs)

    def _emit_cmp(self, op, rd, ra, rb):
        if op == "==":
            self.emit("  xor  " + rd + ", " + ra + ", " + rb)
            self.emit("  sltiu " + rd + ", " + rd + ", 1")
        elif op == "!=":
            self.emit("  xor  " + rd + ", " + ra + ", " + rb)
            self.emit("  sltu " + rd + ", $zero, " + rd)
        elif op == "<":
            self.emit("  slt  " + rd + ", " + ra + ", " + rb)
        elif op == "<=":
            self.emit("  slt  " + rd + ", " + rb + ", " + ra)
            self.emit("  xori " + rd + ", " + rd + ", 1")
        elif op == ">":
            self.emit("  slt  " + rd + ", " + rb + ", " + ra)
        elif op == ">=":
            self.emit("  slt  " + rd + ", " + ra + ", " + rb)
            self.emit("  xori " + rd + ", " + rd + ", 1")

    def emit_binary(self, op, dst, a, b):
        ra = self._mat(a)
        rb = self._mat(b)
        rd = self.regs.get(dst, for_write=True)
        if op == "+":
            self.emit("  addu " + rd + ", " + ra + ", " + rb)
        elif op == "-":
            self.emit("  subu " + rd + ", " + ra + ", " + rb)
        elif op == "*":
            self.emit("  mul  " + rd + ", " + ra + ", " + rb)
        elif op == "/":
            self.emit("  div  " + ra + ", " + rb)
            self.emit("  mflo " + rd)
        elif op == "%":
            self.emit("  div  " + ra + ", " + rb)
            self.emit("  mfhi " + rd)
        elif op in ("==", "!=", "<", "<=", ">", ">="):
            self._emit_cmp(op, rd, ra, rb)
        else:
            self.c("op no soportado: " + op)
        self._release_if_temp(ra)
        self._release_if_temp(rb)

    def emit_return(self, src=None):
        if src is not None:
            r = self._mat(src)
            self.emit("  addu $v0, " + r + ", $zero")
            self._release_if_temp(r)
        self.end_function()

    # -------- caller-save / llamadas --------
    def _caller_save_push(self):
        if not self.SAVE_T_REGS:
            return 0
        size = 10 * 4
        self.emit("  addiu $sp, $sp, -" + str(size))
        for i in range(10):
            self.emit("  sw   $t" + str(i) + ", " + str(i * 4) + "($sp)")
        return size

    def _caller_save_pop(self):
        if not self.SAVE_T_REGS:
            return 0
        for i in range(10):
            self.emit("  lw   $t" + str(i) + ", " + str(i * 4) + "($sp)")
        size = 10 * 4
        self.emit("  addiu $sp, $sp, " + str(size))
        return size

    def emit_param(self, idx_or_src, maybe_src=None):
        """
        Congela el valor del parámetro en este momento.
        Soporta:
        - Param sin índice:  ("Param", src)    -> idx secuencial
        - Param con índice:  ("Param", idx, src)
        Cada 'Param' materializa su PROPIO registro temporal (no se pisan).
        """
        if maybe_src is None:
            idx = len(self._pending_args)
            src = idx_or_src
        else:
            idx = int(idx_or_src)
            src = maybe_src

        r_val = self._mat(src)  # puede materializar literal, var, this, obj.campo
        r_freeze = self.regs.temp_acquire()
        self.emit("  addu " + r_freeze + ", " + r_val + ", $zero")
        self._release_if_temp(r_val)

        # Guardamos el temporal congelado; NO se libera hasta después del 'call'
        self._pending_args.append((idx, r_freeze))

    def _maybe_reorder_for_method(self, fn_label_str):
        """
        Si 'fn_label_str' viene como 'method X', reordena los argumentos
        asumiendo que el ÚLTIMO Param es el receptor (this) y debe ir en $a0.
        Devuelve el nombre real de la función sin 'method '.
        """
        if isinstance(fn_label_str, str) and fn_label_str.startswith("method "):
            real = fn_label_str.split(" ", 1)[1].strip()
            if self._pending_args:
                idx_last, reg_last = self._pending_args[-1]
                others = self._pending_args[:-1]
                reordered = [(0, reg_last)]
                for k, pair in enumerate(others):
                    reordered.append((k + 1, pair[1]))
                self._pending_args = reordered
            return real
        return fn_label_str

    def emit_call(self, dst, fn, argc):
        # 1) caller-save
        self._caller_save_push()

        # 2) soporte opcional "method <nombre>"
        fn_str = str(fn)
        fn_label = self._maybe_reorder_for_method(fn_str)

        # 3) preparar argumentos (ya están congelados como registros)
        args = sorted(self._pending_args, key=lambda x: x[0])
        a_regs = []
        extra_regs = []
        for (idx, reg) in args:
            if idx <= 3:
                a_regs.append((idx, reg))   # $a0..$a3
            else:
                extra_regs.append(reg)      # a partir del 4to van en stack

        # empujar extras (en orden creciente: idx=4,5,6,...) -> 0($sp),4($sp)...
        extra_size = 0
        if len(extra_regs) > 0:
            extra_size = 4 * len(extra_regs)
            self.emit("  addiu $sp, $sp, -" + str(extra_size))
            for k in range(0, len(extra_regs)):
                self.emit("  sw   " + extra_regs[k] + ", " + str(k * 4) + "($sp)")

        # cargar $a0..$a3
        for (idx, r) in a_regs:
            self.emit("  addu $a" + str(idx) + ", " + r + ", $zero")

        # 4) jal
        mangled = self._func_mangle.get(fn_label, fn_label)
        self.emit("  jal " + mangled)
        self.emit("  nop")

        # 5) limpiar extras y restaurar $t*
        if extra_size > 0:
            self.emit("  addiu $sp, $sp, " + str(extra_size))
        self._caller_save_pop()

        # liberar los registros congelados de los parámetros
        for (_, r) in a_regs:
            self._release_if_temp(r)
        for r in extra_regs:
            self._release_if_temp(r)

        # 6) retorno
        if dst:
            rd = self.regs.get(dst, for_write=True)
            self.emit("  addu " + rd + ", $v0, $zero")

        # limpiar buffer de args
        self._pending_args = []

    # -------- TAC específicos del proyecto --------
    def emit_loadparam(self, dst, index):
        # registrar como variable visible de la función
        if isinstance(dst, str):
            self._seen_locals.add(dst)

        rd = self.regs.get(dst, for_write=True)
        if 0 <= index <= 3:
            self.emit("  addu " + rd + ", $a" + str(index) + ", $zero")
        else:
            # Extras del caller por encima del frame actual:
            # Están justo "encima" del frame del callee, así que desde $fp sumamos el tamaño del frame
            # y luego el desplazamiento 4*(index-4).
            off = self.stack_size + 4 * (index - 4)
            self.emit("  lw   " + rd + ", " + str(off) + "($fp)")

    def emit_getprop(self, dst, obj, field):
        """Lee un campo desde 'obj' (o 'this') en 'dst'."""
        rd = self.regs.get(dst, for_write=True)
        # base
        if obj == "this":
            rbase = "$a0"
            base_is_temp = False
        else:
            rbase = self._mat(obj)
            base_is_temp = self._is_temp(rbase)
        # offset
        off = self._FIELD_OFFSETS.get(field, None)
        if off is None:
            self.c("campo desconocido '" + str(field) + "', usando offset 0")
            off = 0
        self.emit("  lw   " + rd + ", " + str(off) + "(" + rbase + ")")
        if base_is_temp:
            self.regs.temp_release(rbase)

    def emit_setprop(self, obj, field, src):
        """Escribe 'src' en el campo 'field' de 'obj' (o 'this')."""
        if obj == "this":
            rbase = "$a0"
            base_is_temp = False
        else:
            rbase = self._mat(obj)
            base_is_temp = self._is_temp(rbase)
        rsrc = self._mat(src)
        off = self._FIELD_OFFSETS.get(field, None)
        if off is None:
            self.c("campo desconocido '" + str(field) + "', usando offset 0")
            off = 0
        self.emit("  sw   " + rsrc + ", " + str(off) + "(" + rbase + ")")
        if base_is_temp:
            self.regs.temp_release(rbase)
        self._release_if_temp(rsrc)

    # -------- driver principal --------
    def from_quads(self, quads):
        for q in quads:
            op = q[0]
            if op == "BeginFunc":
                _, name, loc = q
                self.begin_function(name, loc); continue
            if op == "EndFunc":
                self.end_function(); continue
            if op == "Label":
                _, L = q; self.emit_label(L); continue
            if op == "Goto":
                _, L = q; self.emit_goto(L); continue
            if op == "IfZ":
                _, s, L = q; self.emit_ifz(s, L); continue
            if op == "Assign":
                _, d, s = q; self.emit_assign(d, s); continue
            if op in ("Add", "Sub", "Mul", "Div", "Mod", "Eq", "Ne", "Lt", "Le", "Gt", "Ge"):
                _, d, a, b = q
                mapop = {
                    "Add": "+", "Sub": "-", "Mul": "*", "Div": "/", "Mod": "%",
                    "Eq": "==", "Ne": "!=", "Lt": "<", "Le": "<=", "Gt": ">", "Ge": ">="
                }
                self.emit_binary(mapop[op], d, a, b); continue
            if op == "Return":
                # Soporta Return sin valor
                if len(q) == 1:
                    self.emit_return(None)
                else:
                    _, s = q; self.emit_return(s)
                continue
            if op == "Param":
                # ("Param", src)  o  ("Param", idx, src)
                if len(q) == 3:
                    _, i, s = q; self.emit_param(i, s)
                elif len(q) == 2:
                    _, s = q; self.emit_param(s)
                else:
                    self.c("Param mal formado: " + str(q))
                continue
            if op == "Call":
                _, d, f, n = q; self.emit_call(d, f, n); continue
            if op == "LoadParam":
                _, d, i = q; self.emit_loadparam(d, i); continue
            if op == "GetProp":
                _, d, o, f = q; self.emit_getprop(d, o, f); continue
            if op == "SetProp":
                _, o, f, s = q; self.emit_setprop(o, f, s); continue
            if op == "Raw":
                self.c(q[1]); continue
            self.c("opcode TAC no soportado: " + str(q))

    def build(self):
        out = []
        out.extend(self._emit_data())
        # Si nadie emitió .text (poco probable), garantízalo:
        if self.lines and not any(l.strip().startswith(".text") for l in self.lines):
            out.append(".text")
        out.extend(self.lines)
        return "\n".join(out)
