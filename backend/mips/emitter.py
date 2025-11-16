# backend/mips/emitter.py
"""
MIPSEmitter — Tarea 4 (selección de instrucciones TAC→MIPS)
-----------------------------------------------------------
Novedades clave en esta versión:
- Respeta $a0 como 'this' en cualquier constructor* (LoadParam i -> $a{i+1}).
- Concatenación de strings en el emisor: si el '+' involucra literales o
  valores marcados como "stringish", reescribe a:
      Param a; Param b; dst = Call __strcat_new, 2
  (usa runtime.s).
- Marca automática de variables "stringish":
    * asignaciones desde literales "..."
    * GetProp de campos string (nombre, color)
    * resultados de Call a toString / __int_to_str
    * concatenaciones string (+)
- Soporte de getprop/setprop con offsets fijos por campo.
- Reordenamiento de argumentos para 'call method X' (último Param = this -> $a0).
- Caller-save de $t0..$t9 alrededor de cada jal.
"""

from .regalloc import RegAlloc


class MIPSEmitter:
    SAVE_T_REGS = True  # caller-save para $t0..$t9

    # Layout de ejemplo para 'Persona/Estudiante' (ajusta si la clase cambia)
    _FIELD_OFFSETS = {
        "nombre": 0,    # ptr (string)
        "edad":   4,    # int
        "color":  8,    # ptr (string)
        "grado":  12,   # int
    }
    _STRING_FIELDS = {"nombre", "color"}

    def __init__(self):
        self.lines = []
        self.current_func = None
        self.stack_size = 0
        self.label_counter = 0

        self.regs = RegAlloc()
        self.str_pool = {}
        self.str_count = 0

        self._loaded = set()
        self._pending_args = []
        self._func_seen = {}
        self._func_mangle = {}
        self._seen_locals = set()

        # rastreo simple de "variables que son string"
        self._stringish = set()

    # -------- utilidades base --------
    def emit(self, s): self.lines.append(s)
    def c(self, s): self.emit("# " + s)
    def emit_preamble(self): return
    def uniq_label(self, base="L"):
        self.label_counter += 1
        return base + str(self.label_counter)
    def _align(self, n, a=8): return ((n + a - 1) // a) * a
    def _esc(self, s):
        return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n") + "\""
    def _str_label(self, text):
        if text in self.str_pool: return self.str_pool[text]
        lab = "STR_" + str(self.str_count); self.str_count += 1
        self.str_pool[text] = lab; return lab

    # -------- secciones/data --------
    def _emit_data(self):
        if not self.str_pool: return []
        out = [".data"]
        for s, lab in self.str_pool.items():
            out.append(lab + ": .asciiz " + self._esc(s))
        return out

    # -------- prólogo/epílogo --------
    def begin_function(self, name, local_bytes=0):
        # mangle simple para sobrecargas (constructor, etc.)
        orig = name
        if orig in self._func_seen:
            self._func_seen[orig] += 1
            name = orig + "$" + str(self._func_seen[orig])
        else:
            self._func_seen[orig] = 0
        self._func_mangle[orig] = name

        self.current_func = name
        self._loaded.clear()
        self._pending_args = []
        self._seen_locals = set()
        self._stringish = set()

        spill_hint = self.regs.start_function(spill_bytes_hint=256)
        real_locals = local_bytes + spill_hint
        self.stack_size = self._align(real_locals + 8)

        self.emit("\n# --- Función " + name + " ---")
        self.emit(".text")
        if name == "main": self.emit(".globl main")
        self.emit(name + ":")
        self.emit("  addiu $sp, $sp, -" + str(self.stack_size))
        self.emit("  sw   $ra, " + str(self.stack_size - 4) + "($sp)")
        self.emit("  sw   $fp, " + str(self.stack_size - 8) + "($sp)")
        self.emit("  addu $fp, $sp, $zero")

    def end_function(self):
        self.emit("  lw   $ra, " + str(self.stack_size - 4) + "($sp)")
        self.emit("  lw   $fp, " + str(self.stack_size - 8) + "($sp)")
        self.emit("  addiu $sp, $sp, " + str(self.stack_size))
        self.emit("  jr   $ra"); self.emit("  nop")
        self.current_func = None
        self.regs.end_function()
        self._pending_args = []

    # -------- helpers de temporales --------
    def _is_temp(self, r): return isinstance(r, str) and r.startswith("$t")
    def _release_if_temp(self, r):
        if self._is_temp(r): self.regs.temp_release(r)

    # -------- materialización segura --------
    def _imm(self, val):
        r = self.regs.temp_acquire()
        self.emit("  li   " + r + ", " + str(val))
        return r

    def _mark_stringish_if(self, dst, src_token):
        # literal
        if isinstance(src_token, str):
            s = src_token.strip()
            if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
                self._stringish.add(dst)

    def _mat(self, x):
        """
        Materializa 'x' (inmediato, string, nombre TAC o 'obj.campo') en un registro.
        """
        if isinstance(x, int):
            return self._imm(x)

        if isinstance(x, str):
            s = x.strip()

            # literal string
            if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
                lab = self._str_label(s[1:-1])
                r = self.regs.temp_acquire()
                self.emit("  la   " + r + ", " + lab)
                return r

            # 'this'
            if s == "this": return "$a0"

            # bool/int inmediatos
            if s == "true":  return self._imm(1)
            if s == "false": return self._imm(0)
            if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
                return self._imm(int(s))

            # nombre igual a campo (p_<campo> preferente)
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

            # acceso obj.campo
            if "." in s:
                left, right = s.split(".", 1)
                if left == "this":
                    base = "$a0"; base_temp = False
                else:
                    base = self._mat(left); base_temp = self._is_temp(base)
                off = self._FIELD_OFFSETS.get(right, 0)
                r = self.regs.temp_acquire()
                self.emit("  lw   " + r + ", " + str(off) + "(" + base + ")")
                if base_temp: self.regs.temp_release(base)
                return r

            # nombre TAC
            reg = self.regs.get(s, for_write=False)
            self._ensure_loaded(s, reg)
            return reg

        # fallback 0
        r = self.regs.temp_acquire()
        self.emit("  move " + r + ", $zero")
        return r

    def _ensure_loaded(self, name, reg):
        if name in self._loaded: return
        if self.regs.has_spill_slot(name):
            off = self.regs.spill_slot_offset(name)
            self.emit("  lw   " + reg + ", " + str(off) + "($fp)")
        self._loaded.add(name)

    # -------- emisión básica --------
    def emit_label(self, L): self.emit(L + ":")
    def emit_goto(self, L): self.emit("  b " + L); self.emit("  nop")

    def emit_ifz(self, src, L):
        r = self._mat(src)
        self.emit("  beq  " + r + ", $zero, " + L); self.emit("  nop")
        self._release_if_temp(r)

    def emit_assign(self, dst, src):
        # LHS campo simple -> this.campo = expr
        if isinstance(dst, str) and ('.' not in dst) and (dst in self._FIELD_OFFSETS):
            self.emit_setprop("this", dst, src)
            return

        if isinstance(dst, str): self._seen_locals.add(dst)
        self._mark_stringish_if(dst, src)

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

    def _is_string_add(self, a, b):
        # literal inmediato
        def is_lit(s):
            return isinstance(s, str) and len(s) >= 2 and s[0] == '"' and s[-1] == '"'
        if is_lit(a) or is_lit(b): return True
        # variables marcadas como stringish
        if isinstance(a, str) and a in self._stringish: return True
        if isinstance(b, str) and b in self._stringish: return True
        return False

    def emit_binary(self, op, dst, a, b):
        # concatenación de strings
        if op == "+" and self._is_string_add(a, b):
            # Congelar parámetros y llamar a runtime.__strcat_new
            self.emit_param(a)
            self.emit_param(b)
            self.emit_call(dst, "__strcat_new", 2)
            if isinstance(dst, str): self._stringish.add(dst)
            return

        ra = self._mat(a); rb = self._mat(b)
        rd = self.regs.get(dst, for_write=True)
        if op == "+":   self.emit("  addu " + rd + ", " + ra + ", " + rb)
        elif op == "-": self.emit("  subu " + rd + ", " + ra + ", " + rb)
        elif op == "*": self.emit("  mul  " + rd + ", " + ra + ", " + rb)
        elif op == "/":
            self.emit("  div  " + ra + ", " + rb); self.emit("  mflo " + rd)
        elif op == "%":
            self.emit("  div  " + ra + ", " + rb); self.emit("  mfhi " + rd)
        elif op in ("==", "!=", "<", "<=", ">", ">="):
            self._emit_cmp(op, rd, ra, rb)
        else:
            self.c("op no soportado: " + op)
        self._release_if_temp(ra); self._release_if_temp(rb)

    def emit_return(self, src=None):
        if src is not None:
            r = self._mat(src)
            self.emit("  addu $v0, " + r + ", $zero")
            self._release_if_temp(r)
        self.end_function()

    # -------- caller-save / llamadas --------
    def _caller_save_push(self):
        if not self.SAVE_T_REGS: return 0
        size = 10 * 4
        self.emit("  addiu $sp, $sp, -" + str(size))
        for i in range(10):
            self.emit("  sw   $t" + str(i) + ", " + str(i * 4) + "($sp)")
        return size

    def _caller_save_pop(self):
        if not self.SAVE_T_REGS: return 0
        for i in range(10):
            self.emit("  lw   $t" + str(i) + ", " + str(i * 4) + "($sp)")
        size = 10 * 4
        self.emit("  addiu $sp, $sp, " + str(size))
        return size

    def emit_param(self, idx_or_src, maybe_src=None):
        """
        Congela el valor del parámetro en este momento.
        Soporta:
          Param <src>            -> índice secuencial
          Param <i>, <src>       -> índice explícito
        """
        if maybe_src is None:
            idx = len(self._pending_args)
            src = idx_or_src
        else:
            idx = int(idx_or_src); src = maybe_src

        r_val = self._mat(src)
        r_freeze = self.regs.temp_acquire()
        self.emit("  addu " + r_freeze + ", " + r_val + ", $zero")
        self._release_if_temp(r_val)
        self._pending_args.append((idx, r_freeze))

    def _maybe_reorder_for_method(self, fn_label_str):
        """
        Si 'fn_label_str' es 'method X', reordena params para que el ÚLTIMO Param
        sea el receptor (this) y vaya en $a0.
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
        # caller-save
        self._caller_save_push()

        # soporte 'method '
        fn_str = str(fn)
        fn_label = self._maybe_reorder_for_method(fn_str)

        # preparar a0..a3 + extras
        args = sorted(self._pending_args, key=lambda x: x[0])
        a_regs, extra_regs = [], []
        for (idx, reg) in args:
            if idx <= 3: a_regs.append((idx, reg))
            else: extra_regs.append(reg)

        extra_size = 0
        if extra_regs:
            extra_size = 4 * len(extra_regs)
            self.emit("  addiu $sp, $sp, -" + str(extra_size))
            for k in range(len(extra_regs)):
                self.emit("  sw   " + extra_regs[k] + ", " + str(k * 4) + "($sp)")

        for (idx, r) in a_regs:
            self.emit("  addu $a" + str(idx) + ", " + r + ", $zero")

        mangled = self._func_mangle.get(fn_label, fn_label)
        self.emit("  jal " + mangled); self.emit("  nop")

        if extra_size > 0: self.emit("  addiu $sp, $sp, " + str(extra_size))
        self._caller_save_pop()

        for (_, r) in a_regs: self._release_if_temp(r)
        for r in extra_regs:  self._release_if_temp(r)

        if dst:
            rd = self.regs.get(dst, for_write=True)
            self.emit("  addu " + rd + ", $v0, $zero")
            # Heurística: si la función suena a toString/int->string, marca stringish
            if isinstance(fn_label, str) and (fn_label.endswith("toString") or fn_label == "__int_to_str" or fn_label == "toString"):
                self._stringish.add(dst)

        self._pending_args = []

    # -------- TAC específicos --------
    def _in_constructor(self) -> bool:
        n = self.current_func or ""
        return n.startswith("constructor")

    def emit_loadparam(self, dst, index):
        if isinstance(dst, str):
            self._seen_locals.add(dst)
        rd = self.regs.get(dst, for_write=True)

        # En constructores, los parámetros del usuario empiezan en $a1 (a0=this)
        adj = int(index)
        if self._in_constructor():
            adj += 1

        if 0 <= adj <= 3:
            self.emit("  addu " + rd + ", $a" + str(adj) + ", $zero")
        else:
            off = self.stack_size + 4 * (adj - 4)
            self.emit("  lw   " + rd + ", " + str(off) + "($fp)")

    def emit_getprop(self, dst, obj, field):
        rd = self.regs.get(dst, for_write=True)
        if obj == "this":
            rbase = "$a0"; base_temp = False
        else:
            rbase = self._mat(obj); base_temp = self._is_temp(rbase)
        off = self._FIELD_OFFSETS.get(field, 0)
        self.emit("  lw   " + rd + ", " + str(off) + "(" + rbase + ")")
        if base_temp: self.regs.temp_release(rbase)
        # marcar stringish si el campo es string
        if field in self._STRING_FIELDS:
            self._stringish.add(dst)

    def emit_setprop(self, obj, field, src):
        if obj == "this":
            rbase = "$a0"; base_temp = False
        else:
            rbase = self._mat(obj); base_temp = self._is_temp(rbase)
        rsrc = self._mat(src)
        off = self._FIELD_OFFSETS.get(field, 0)
        self.emit("  sw   " + rsrc + ", " + str(off) + "(" + rbase + ")")
        if base_temp: self.regs.temp_release(rbase)
        self._release_if_temp(rsrc)

    # -------- driver principal --------
    def from_quads(self, quads):
        for q in quads:
            op = q[0]
            if op == "BeginFunc":
                _, name, loc = q; self.begin_function(name, loc); continue
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
            if op in ("Add","Sub","Mul","Div","Mod","Eq","Ne","Lt","Le","Gt","Ge"):
                _, d, a, b = q
                mapop = {"Add":"+","Sub":"-","Mul":"*","Div":"/","Mod":"%",
                         "Eq":"==","Ne":"!=","Lt":"<","Le":"<=","Gt":">","Ge":">="}
                self.emit_binary(mapop[op], d, a, b); continue
            if op == "Return":
                if len(q) == 1: self.emit_return(None)
                else: _, s = q; self.emit_return(s)
                continue
            if op == "Param":
                if len(q) == 3: _, i, s = q; self.emit_param(i, s)
                elif len(q) == 2: _, s = q; self.emit_param(s)
                else: self.c("Param mal formado: " + str(q))
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
        if self.lines and not any(l.strip().startswith(".text") for l in self.lines):
            out.append(".text")
        out.extend(self.lines)
        return "\n".join(out)
