# backend/mips/emitter.py
"""
MIPSEmitter — Tarea 4 (TAC -> MIPS)

Mejoras incluidas:
- TODO el TAC de nivel superior (antes/entre/después de funciones) se ejecuta
  dentro de _program_init, y 'main' lo invoca al iniciar.
- Epílogo especial para 'main' (syscall 10).
- Redirección de builtins: toString/printString/printInteger.
- Blindaje de labels cuando el TAC define builtins (renombramos defs a $user).
- Manejo de strings: soporta correctamente "\n" y "\t" sin doble-escapar.
- Fallback: si no hay función 'main' pero sí top-level, se genera un 'main'
  mínimo que invoca _program_init y luego hace syscall 10.
"""

from .regalloc import RegAlloc


class MIPSEmitter:
    SAVE_T_REGS = True  # caller-save para $t0..$t9

    # Campos de la clase Estudiante (ajusta si cambian)
    _FIELD_OFFSETS = {
        "nombre": 0,   # ptr (string)
        "edad":   4,   # int
        "color":  8,   # ptr (string)
        "grado":  12,  # int
    }
    _STRING_FIELDS = {"nombre", "color"}

    # Builtins del runtime
    BUILTIN_REDIRECTS = {
        "toString":    "__int_to_str",  # toString(i) -> __int_to_str(i)
        "printString": "print_str",     # printString(s) -> print_str(s)
        # printInteger se maneja aparte porque retorna el entero original
    }
    BUILTIN_NAMES = {"toString", "printString", "printInteger"}

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

        # Control de boot/top-level
        self._have_boot = False
        self._boot_label = "_program_init"
        self._saw_main = False  # para fallback si no viene 'main' en TAC

    # ---------- util ----------
    def emit(self, s): self.lines.append(s)
    def c(self, s): self.emit("# " + s)
    def emit_preamble(self): return
    def uniq_label(self, base="L"):
        self.label_counter += 1
        return base + str(self.label_counter)
    def _align(self, n, a=8): return ((n + a - 1) // a) * a

    def _esc(self, s: str) -> str:
        """
        Escapa comillas y backslashes, pero respeta secuencias \n y \t
        para que el ensamblador las interprete como salto y tab reales.
        """
        # Primero escapamos backslash y comillas
        s2 = s.replace("\\", "\\\\").replace("\"", "\\\"")
        # Restauramos \n y \t (quedaron como "\\n" y "\\t")
        s2 = s2.replace("\\\\n", "\\n").replace("\\\\t", "\\t")
        return "\"" + s2 + "\""

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

    # ---------- funciones ----------
    def begin_function(self, name, local_bytes=0):
        orig = name

        # Si el TAC define un builtin, renombramos su definición del usuario
        if orig in self.BUILTIN_NAMES:
            name = orig + "$user"

        if orig in self._func_seen:
            self._func_seen[orig] += 1
            if name == orig:  # solo si no fue builtin renombrado
                name = orig + "$" + str(self._func_seen[orig])
        else:
            self._func_seen[orig] = 0

        # mapa lógico -> label real
        self._func_mangle[orig] = name

        if orig == "main":
            self._saw_main = True

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
        if name == "main":
            self.emit(".globl main")
        self.emit(name + ":")
        self.emit("  addiu $sp, $sp, -" + str(self.stack_size))
        self.emit("  sw   $ra, " + str(self.stack_size - 4) + "($sp)")
        self.emit("  sw   $fp, " + str(self.stack_size - 8) + "($sp)")
        self.emit("  addu $fp, $sp, $zero")

        # 'main' arranca llamando al boot si existe
        if name == "main" and self._have_boot:
            self.emit("  # invocar bloque top-level")
            self.emit("  jal " + self._boot_label)
            self.emit("  nop")

    def end_function(self):
        # flush de spills (defensivo)
        for name, off in self.regs._spill_slot.items():
            reg = self.regs._name2reg.get(name)
            if reg is not None:
                self.emit(f"  sw   {reg}, {off}($fp)")

        # restaurar frame
        self.emit("  lw   $ra, " + str(self.stack_size - 4) + "($sp)")
        self.emit("  lw   $fp, " + str(self.stack_size - 8) + "($sp)")
        self.emit("  addiu $sp, $sp, " + str(self.stack_size))

        if self.current_func == "main":
            # terminar programa
            self.emit("  li   $v0, 10")
            self.emit("  syscall")
        else:
            self.emit("  jr   $ra")
            self.emit("  nop")

        self.current_func = None
        self.regs.end_function()
        self._pending_args = []

    # ---------- helpers de registros/inmediatos ----------
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
            return self._imm(int(x))
        if isinstance(x, str):
            s = x.strip()

            # literal string
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

            # acceso a this.campo o obj.campo
            if "." in s:
                parts = s.split(".", 1)
                obj_name = parts[0]; field_name = parts[1]
                if obj_name == "this":
                    if field_name not in self._FIELD_OFFSETS:
                        self.c("Campo no encontrado: " + field_name)
                        return self._imm(0)
                    off = self._FIELD_OFFSETS[field_name]
                    r = self.regs.temp_acquire()
                    self.emit("  lw   " + r + ", " + str(off) + "($a0)")
                    if field_name in self._STRING_FIELDS:
                        self._stringish.add(r)
                    return r
                else:
                    reg_obj = self.regs.get(obj_name)
                    if field_name not in self._FIELD_OFFSETS:
                        self.c("Campo no encontrado: " + field_name)
                        return self._imm(0)
                    off = self._FIELD_OFFSETS[field_name]
                    r = self.regs.temp_acquire()
                    self.emit("  lw   " + r + ", " + str(off) + "(" + reg_obj + ")")
                    if field_name in self._STRING_FIELDS:
                        self._stringish.add(r)
                    return r

            # variable normal
            return self.regs.get(s)
        return self._imm(0)

    # ---------- instrucciones ----------
    def emit_label(self, L):
        self.emit(L + ":")

    def emit_goto(self, L):
        self.emit("  b " + L); self.emit("  nop")

    def emit_ifz(self, src, L):
        r = self._mat(src)
        self.emit("  beq  " + r + ", $zero, " + L); self.emit("  nop")
        self._release_if_temp(r)

    def emit_assign(self, dst, src):
        if dst == "_": return
        rs = self._mat(src)
        rd = self.regs.get(dst, for_write=True)
        self.emit("  addu " + rd + ", " + rs + ", $zero")
        self._release_if_temp(rs)
        self._mark_stringish_if(dst, src)

    def _emit_cmp(self, op, rd, ra, rb):
        if op == "<":
            self.emit("  slt   " + rd + ", " + ra + ", " + rb)
        elif op == "==":
            rt = self.regs.temp_acquire()
            self.emit("  xor   " + rt + ", " + ra + ", " + rb)
            self.emit("  sltiu " + rd + ", " + rt + ", 1")
            self.regs.temp_release(rt)
        elif op == "!=":
            rt = self.regs.temp_acquire()
            self.emit("  xor   " + rt + ", " + ra + ", " + rb)
            self.emit("  sltu  " + rd + ", $zero, " + rt)
            self.regs.temp_release(rt)
        elif op == "<=":
            self.emit("  slt   " + rd + ", " + rb + ", " + ra)
            self.emit("  xori  " + rd + ", " + rd + ", 1")
        elif op == ">":
            self.emit("  slt   " + rd + ", " + rb + ", " + ra)
        elif op == ">=":
            self.emit("  slt   " + rd + ", " + ra + ", " + rb)
            self.emit("  xori  " + rd + ", " + rd + ", 1")

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
        elif op in ("==","!=","<","<=",">",">="):
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

    # ---------- llamadas ----------
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

    def _emit_builtin_printInteger(self, dst):
        # caller-save
        self._caller_save_push()

        # primer argumento (el entero)
        args = sorted(self._pending_args, key=lambda x: x[0])
        _, reg_val = args[0]

        # __int_to_str
        self.emit("  addu $a0, " + reg_val + ", $zero")
        self.emit("  jal __int_to_str"); self.emit("  nop")

        # print_str
        self.emit("  addu $a0, $v0, $zero")
        self.emit("  jal print_str"); self.emit("  nop")

        # retorno = entero original
        self.emit("  addu $v0, " + reg_val + ", $zero")

        self._caller_save_pop()
        self._release_if_temp(reg_val)

        if dst:
            rd = self.regs.get(dst, for_write=True)
            self.emit("  addu " + rd + ", $v0, $zero")

        self._pending_args = []

    def emit_call(self, dst, fn, argc):
        fn_str = str(fn)
        if fn_str in self.BUILTIN_REDIRECTS:
            fn_str = self.BUILTIN_REDIRECTS[fn_str]

        if fn == "printInteger":
            self._emit_builtin_printInteger(dst)
            return

        self._caller_save_push()

        fn_label = self._maybe_reorder_for_method(fn_str)

        # a0..a3 y resto en stack
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

        for (_, reg) in args:
            self._release_if_temp(reg)

        if fn_label in self._func_mangle:
            self.emit("  jal " + self._func_mangle[fn_label])
        else:
            self.emit("  jal " + fn_label)
        self.emit("  nop")

        if extra_regs:
            self.emit("  addiu $sp, $sp, " + str(extra_size))

        self._caller_save_pop()

        if dst:
            rd = self.regs.get(dst, for_write=True)
            self.emit("  addu " + rd + ", $v0, $zero")

        self._pending_args = []

    def emit_loadparam(self, dst, idx):
        rd = self.regs.get(dst, for_write=True)
        if idx <= 3:
            self.emit("  addu " + rd + ", $a" + str(idx) + ", $zero")
        else:
            off = (idx - 4) * 4 + self.stack_size
            self.emit("  lw   " + rd + ", " + str(off) + "($fp)")

    def emit_getprop(self, dst, obj, field):
        if obj == "this":
            off = self._FIELD_OFFSETS.get(field, 0)
            rd = self.regs.get(dst, for_write=True)
            self.emit("  lw   " + rd + ", " + str(off) + "($a0)")
        else:
            ro = self.regs.get(obj)
            off = self._FIELD_OFFSETS.get(field, 0)
            rd = self.regs.get(dst, for_write=True)
            self.emit("  lw   " + rd + ", " + str(off) + "(" + ro + ")")
        if field in self._STRING_FIELDS: self._stringish.add(dst)

    def emit_setprop(self, obj, field, src):
        rs = self._mat(src)
        if obj == "this":
            off = self._FIELD_OFFSETS.get(field, 0)
            self.emit("  sw   " + rs + ", " + str(off) + "($a0)")
        else:
            ro = self.regs.get(obj)
            off = self._FIELD_OFFSETS.get(field, 0)
            self.emit("  sw   " + rs + ", " + str(off) + "(" + ro + ")")
        self._release_if_temp(rs)

    def emit_new(self, dst, cname):
        mapper = {"Estudiante": "newEstudiante"}
        fn = mapper.get(cname, "new" + cname)
        self.emit_call(dst, fn, len(self._pending_args))

    # ---------- driver ----------
    def _emit_quads_sequence(self, quads):
        """Emite una secuencia suponiendo que YA estamos dentro de una función."""
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

    def from_quads(self, quads):
        """
        Recolecta todos los quads fuera de funciones (antes/entre/después)
        y los emite como _program_init; luego emite cada función.
        """
        top = []
        functions = []

        inside = False
        current = []

        for q in quads:
            if q and q[0] == "BeginFunc":
                # si veníamos acumulando 'current' como función previa, guárdala
                if inside and current:
                    functions.append(current)
                    current = []
                inside = True
                current = [q]
                continue

            if q and q[0] == "EndFunc":
                if inside:
                    current.append(q)
                    functions.append(current)
                    current = []
                    inside = False
                else:
                    # EndFunc suelto: ignóralo defensivamente
                    pass
                continue

            if inside:
                current.append(q)
            else:
                top.append(q)

        # si terminó dentro de una función sin EndFunc (defensivo)
        if inside and current:
            functions.append(current)

        # Emite el boot si hay TAC top-level
        if top:
            self._have_boot = True
            self.emit("\n# --- Función " + self._boot_label + " ---")
            self.emit(".text")
            self.emit(self._boot_label + ":")
            
            # Frame de _program_init
            spill_hint = self.regs.start_function(spill_bytes_hint=256)
            self.stack_size = self._align(spill_hint + 8)
            self.emit("  addiu $sp, $sp, -" + str(self.stack_size))
            self.emit("  sw   $ra, " + str(self.stack_size - 4) + "($sp)")
            self.emit("  sw   $fp, " + str(self.stack_size - 8) + "($sp)")
            self.emit("  addu $fp, $sp, $zero")
            
            # Emitir el código del top-level
            self.current_func = self._boot_label
            self._emit_quads_sequence(top)
            
            # Epilogo de _program_init
            self.emit("  lw   $ra, " + str(self.stack_size - 4) + "($sp)")
            self.emit("  lw   $fp, " + str(self.stack_size - 8) + "($sp)")
            self.emit("  addiu $sp, $sp, " + str(self.stack_size))
            self.emit("  jr   $ra")
            self.emit("  nop")
            
            self.current_func = None
            self.regs.end_function()

        # Emite todas las funciones en orden
        for fn_chunk in functions:
            self._emit_quads_sequence(fn_chunk)

        # Fallback: si hubo top-level pero no hubo 'main', genera un main mínimo
        if self._have_boot and not self._saw_main:
            self.begin_function("main", 0)
            self.emit("  # main generado (fallback) -> invoca _program_init y sale")
            self.emit("  jal " + self._boot_label); self.emit("  nop")
            self.emit_return(None)  # esto agregará syscall 10 por ser 'main'

    def build(self):
        out = []
        out.extend(self._emit_data())
        if self.lines and not any(l.strip().startswith(".text") for l in self.lines):
            out.append(".text")
        out.extend(self.lines)
        return "\n".join(out)