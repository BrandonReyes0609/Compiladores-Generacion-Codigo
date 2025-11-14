 """
MIPSEmitter: emite MIPS a partir de quads TAC.
Convenciones mínimas:
- $a0..$a3: parámetros
- $v0: valor de retorno
- $t0..$t9: temporales
- $sp/$fp/$ra: stack/frame/return address
- begin_function reserva stack (locals + guardar $fp/$ra), end_function lo restaura.
- Literales de texto -> .data (asciiz) y se materializan con la (la etiqueta).

Soporta (por ahora):
- BeginFunc/EndFunc/Return
- Label/Goto/IfZ
- Assign
- Add/Sub/Mul/Div
- Eq/Ne/Lt/Le/Gt/Ge (bool 0/1)
- Param (0..3)
- Call (dst opcional)
- LoadParam (x = LoadParam i)  << usado por tu TAC
- GetProp/SetProp  << placeholder no destructivo (TODO: integrar con offsets TS)
"""

from .regalloc import RegAlloc

class MIPSEmitter:
    def __init__(self):
        self.lines = []
        self.data = []
        self.current_func = None
        self.stack_size = 0
        self.label_counter = 0
        self.regs = RegAlloc()
        self.str_pool = {}  # texto -> etiqueta
        self.str_count = 0

    # ---------- Utilidades ----------
    def emit(self, s): self.lines.append(s)
    def c(self, s): self.emit("# " + s)

    def uniq_label(self, base="L"):
        self.label_counter += 1
        return f"{base}{self.label_counter}"

    def _align(self, n, a=8):
        return ((n + a - 1) // a) * a

    def _esc(self, s):
        return "\"" + s.replace("\\","\\\\").replace("\"","\\\"").replace("\n","\\n") + "\""

    def _str_label(self, text):
        if text in self.str_pool: return self.str_pool[text]
        lab = f"STR_{self.str_count}"
        self.str_count += 1
        self.str_pool[text] = lab
        return lab

    # ---------- Secciones ----------
    def emit_preamble(self):
        # imprimimos .data primero si hay strings al final en build()
        pass

    def _emit_data(self):
        if not self.str_pool: return []
        out = [".data"]
        for s, lab in self.str_pool.items():
            out.append(f"{lab}: .asciiz {self._esc(s)}")
        return out

    # ---------- Prólogo/Epílogo ----------
    def begin_function(self, name, local_bytes=0):
        self.current_func = name
        self.regs.reset()
        # Reserva: locals + guardar $fp y $ra (8 bytes)
        self.stack_size = self._align(local_bytes + 8)
        self.emit(f"\n# --- Función {name} ---")
        self.emit(f".text")
        if name == "main":
            self.emit(".globl main")
        self.emit(f"{name}:")
        self.emit(f"  addiu $sp, $sp, -{self.stack_size}")
        self.emit(f"  sw   $ra, {self.stack_size - 4}($sp)")
        self.emit(f"  sw   $fp, {self.stack_size - 8}($sp)")
        self.emit(f"  addu $fp, $sp, $zero")

    def end_function(self):
        # Restaurar y regresar
        self.emit(f"  lw   $ra, {self.stack_size - 4}($sp)")
        self.emit(f"  lw   $fp, {self.stack_size - 8}($sp)")
        self.emit(f"  addiu $sp, $sp, {self.stack_size}")
        self.emit(f"  jr   $ra")
        self.emit(f"  nop")
        self.current_func = None

    # ---------- Helpers de materialización ----------
    def _imm(self, val):
        r = self.regs.pool.acquire()
        self.emit(f"  li   {r}, {val}")
        return r

    def _mat(self, x):
        # int literal
        if isinstance(x, int): return self._imm(x)
        # nombre TAC o literal string entre comillas
        if isinstance(x, str):
            s = x.strip()
            # string literal
            if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
                lab = self._str_label(s[1:-1])
                r = self.regs.pool.acquire()
                self.emit(f"  la   {r}, {lab}")
                return r
            # bool-like
            if s == "true":  return self._imm(1)
            if s == "false": return self._imm(0)
            # número en string
            if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
                return self._imm(int(s))
            # variable/temporal
            return self.regs.get(s)
        # fallback
        r = self.regs.pool.acquire()
        self.emit(f"  move {r}, $zero")
        return r

    # ---------- Emisión de operaciones ----------
    def emit_label(self, L):
        self.emit(f"{L}:")

    def emit_goto(self, L):
        self.emit(f"  b {L}")
        self.emit("  nop")

    def emit_ifz(self, src, L):
        r = self._mat(src)
        self.emit(f"  beq  {r}, $zero, {L}")
        self.emit("  nop")

    def emit_assign(self, dst, src):
        rd = self.regs.get(dst)
        rs = self._mat(src)
        self.emit(f"  addu {rd}, {rs}, $zero")

    def emit_binary(self, op, dst, a, b):
        ra = self._mat(a); rb = self._mat(b); rd = self.regs.get(dst)
        if op == "+":   self.emit(f"  addu {rd}, {ra}, {rb}")
        elif op == "-": self.emit(f"  subu {rd}, {ra}, {rb}")
        elif op == "*": self.emit(f"  mul  {rd}, {ra}, {rb}")
        elif op == "/":
            self.emit(f"  div  {ra}, {rb}")
            self.emit(f"  mflo {rd}")
        elif op in ("==","!=","<","<=" ,">",">="):
            self._emit_cmp(op, rd, ra, rb)
        else:
            self.c(f"op no soportado: {op}")

    def _emit_cmp(self, op, rd, ra, rb):
        if op == "==":
            self.emit(f"  xor  {rd}, {ra}, {rb}")
            self.emit(f"  sltiu {rd}, {rd}, 1")
        elif op == "!=":
            self.emit(f"  xor  {rd}, {ra}, {rb}")
            self.emit(f"  sltu {rd}, $zero, {rd}")
        elif op == "<":
            self.emit(f"  slt  {rd}, {ra}, {rb}")
        elif op == "<=":
            self.emit(f"  slt  {rd}, {rb}, {ra}")
            self.emit(f"  xori {rd}, {rd}, 1")
        elif op == ">":
            self.emit(f"  slt  {rd}, {rb}, {ra}")
        elif op == ">=":
            self.emit(f"  slt  {rd}, {ra}, {rb}")
            self.emit(f"  xori {rd}, {rd}, 1")

    def emit_return(self, src=None):
        if src is not None:
            r = self._mat(src)
            self.emit(f"  addu $v0, {r}, $zero")
        self.end_function()

    # ---------- llamadas ----------
    def emit_param(self, idx, src):
        # Convención simple: 0..3 -> $a0..$a3
        r = self._mat(src)
        if 0 <= idx <= 3:
            self.emit(f"  addu $a{idx}, {r}, $zero")
        else:
            self.c(f"Param {idx} > 3 no soportado (TODO: stack)")

    def emit_call(self, dst, fn, argc):
        self.emit(f"  jal {fn}")
        self.emit(f"  nop")
        if dst:
            rd = self.regs.get(dst)
            self.emit(f"  addu {rd}, $v0, $zero")

    # ---------- extras del TAC de tu repo ----------
    def emit_loadparam(self, dst, index):
        # Soporta: x = LoadParam i  (de tus quads)
        rd = self.regs.get(dst)
        if 0 <= index <= 3:
            self.emit(f"  addu {rd}, $a{index}, $zero")
        else:
            self.c(f"LoadParam {index} > 3 no soportado (TODO: stack)")

    def emit_getprop(self, dst, obj, field):
        # Placeholder: deja 0 y comenta (integraremos con offsets de TS en tarea posterior)
        rd = self.regs.get(dst)
        self.emit(f"  move {rd}, $zero")
        self.c(f"TODO getprop {obj}.{field} (requiere layout/offsets)")

    def emit_setprop(self, obj, field, src):
        # Placeholder: no destruye y comenta
        self.c(f"TODO setprop {obj}.{field} = {src} (requiere layout/offsets)")

    # ---------- Driver ----------
    def from_quads(self, quads):
        for q in quads:
            op = q[0]

            if op == "BeginFunc":   _, name, loc = q; self.begin_function(name, loc); continue
            if op == "EndFunc":     self.end_function(); continue

            if op == "Label":       _, L = q; self.emit_label(L); continue
            if op == "Goto":        _, L = q; self.emit_goto(L); continue
            if op == "IfZ":         _, s,L = q; self.emit_ifz(s, L); continue

            if op == "Assign":      _, d,s = q; self.emit_assign(d, s); continue
            if op in ("Add","Sub","Mul","Div","Eq","Ne","Lt","Le","Gt","Ge"):
                _, d,a,b = q
                mapop = {
                    "Add":"+","Sub":"-","Mul":"*","Div":"/",
                    "Eq":"==","Ne":"!=","Lt":"<","Le":"<=","Gt":">","Ge":">="
                }
                self.emit_binary(mapop[op], d, a, b); continue

            if op == "Return":      _, s = q; self.emit_return(s); continue
            if op == "Param":       _, i,s = q; self.emit_param(i, s); continue
            if op == "Call":        _, d,f,n = q; self.emit_call(d, f, n); continue

            if op == "LoadParam":   _, d,i = q; self.emit_loadparam(d, i); continue
            if op == "GetProp":     _, d,o,f = q; self.emit_getprop(d, o, f); continue
            if op == "SetProp":     _, o,f,s = q; self.emit_setprop(o, f, s); continue

            if op == "Raw":
                # líneas no críticas (ActivationRecord, etc.)
                self.c(q[1]); continue

            # Desconocido: comenta
            self.c(f"opcode TAC no soportado: {q}")

    def build(self):
        out = []
        # .data (strings)
        out.extend(self._emit_data())
        # .text
        if self.lines:
            # si no hubo begin_function, aseguramos sección
            if not any(l.strip().startswith(".text") for l in self.lines):
                out.append(".text")
        out.extend(self.lines)
        return "\n".join(out)
