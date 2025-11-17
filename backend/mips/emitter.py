# backend/mips/emitter.py
"""
MIPSEmitter — Tarea 4 (selección de instrucciones TAC→MIPS)
-----------------------------------------------------------
Cambios clave (Opción B):
- Si la función actual es 'main', el epílogo NO hace `jr $ra`.
  En su lugar, restaura el frame y realiza `li $v0, 10` + `syscall`
  para terminar el programa en MARS sin PC inválido.
"""

from .regalloc import RegAlloc


class MIPSEmitter:
    SAVE_T_REGS = True  # caller-save para $t0..$t9

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

        self._stringish = set()

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

    def _emit_data(self):
        if not self.str_pool: return []
        out = [".data"]
        for s, lab in self.str_pool.items():
            out.append(lab + ": .asciiz " + self._esc(s))
        return out

    def begin_function(self, name, local_bytes=0):
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
        # flush de spills
        for name, off in self.regs._spill_slot.items():
            reg = self.regs._name2reg.get(name)
            if reg is not None:
                self.emit(f"  sw   {reg}, {off}($fp)")

        # restaurar frame
        self.emit("  lw   $ra, " + str(self.stack_size - 4) + "($sp)")
        self.emit("  lw   $fp, " + str(self.stack_size - 8) + "($sp)")
        self.emit("  addiu $sp, $sp, " + str(self.stack_size))

        # epílogo especial para main
        if self.current_func == "main":
            self.emit("  li   $v0, 10")
            self.emit("  syscall")
        else:
            self.emit("  jr   $ra")
            self.emit("  nop")

        self.current_func = None
        self.regs.end_function()
        self._pending_args = []

    def _is_temp(self, r): return isinstance(r, str) and r.startswith("$t")
    def _release_if_temp(self, r):
        if self._is_temp(r): self.regs.temp_release(r)

    def _imm(self, val):
        r = self.regs.temp_acquire()
        self.emit("  li   " + r + ", " + str(val))
        return r

    def _mark_stringish_if(self, dst, src_token):
        if isinstance(src_token, str):
            s = src_token.strip()
            if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
                self._stringish.add(dst)

    def _mat(self, x):
        if isinstance(x, int):
            return self._imm(x)

        if isinstance(x, str):
            s = x.strip()

            if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
                lab = self._str_label(s[1:-1])
                r = self.regs.temp_acquire()
                self.emit("  la   " + r + ", " + lab)
                return r

            if s == "this": return "$a0"

            if s == "true":  return self._imm(1)
            if s == "false": return self._imm(0)
            if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
                return self._imm(int(s))

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

            reg = self.regs.get(s, for_write=False)
            self._ensure_loaded(s, reg)
            return reg

        r = self.regs.temp_acquire()
        self.emit("  move " + r + ", $zero")
        return r

    def _ensure_loaded(self, name, reg):
        if name in self._loaded: return
        if self.regs.has_spill_slot(name):
            off = self.regs.spill_slot_offset(name)
            self.emit("  lw   " + reg + ", " + str(off) + "($fp)")
        self._loaded.add(name)

    def emit_label(self, L): self.emit(L + ":")
    def emit_goto(self, L): self.emit("  b " + L); self.emit("  nop")

    def emit_ifz(self, src, L):
        r = self._mat(src)
        self.emit("  beq  " + r + ", $zero, " + L); self.emit("  nop")
        self._release_if_temp(r)

    def emit_assign(self, dst, src):
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
        def is_lit(s):
            return isinstance(s, str) and len(s) >= 2 and s[0] == '"' and s[-1] == '"'
        if is_lit(a) or is_lit(b): return True
        if isinstance(a, str) and a in self._stringish: return True
        if isinstance(b, str) and b in self._stringish: return True
        return False

    def emit_binary(self, op, dst, a, b):
        if op == "+" and self._is_string_add(a, b):
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

    # -------- llamadas --------
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
        self._caller_save_push()

        fn_str = str(fn)
        fn_label = self._maybe_reorder_for_method(fn_str)

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
            if isinstance(fn_label, str) and (fn_label.endswith("toString") or fn_label == "__int_to_str" or fn_label == "toString"):
                self._stringish.add(dst)

        self._pending_args = []

    def _in_constructor(self) -> bool:
        n = self.current_func or ""
        return n.startswith("constructor")

    def emit_loadparam(self, dst, index):
        if isinstance(dst, str):
            self._seen_locals.add(dst)
        rd = self.regs.get(dst, for_write=True)

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

    def emit_new(self, dst, cname):
        size = len(self._FIELD_OFFSETS) * 4
        r = self.regs.get(dst, for_write=True)
        self.emit("  li   $v0, 9")
        self.emit("  li   $a0, " + str(size))
        self.emit("  syscall")
        self.emit("  move " + r + ", $v0")

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
            if op == "New":
                _, dst, cname = q; self.emit_new(dst, cname); continue
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
