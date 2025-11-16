# program/ir_emitter.py
from __future__ import annotations
from typing import List, Dict, Optional

"""
=====================
IR (TAC) Emitter v1.2
=====================

Emite TAC de alto nivel con las siguientes convenciones:

- Funciones:
  BeginFunc <name> <nparams>
  ActivationRecord <name>
  EndFunc <name>

- Parámetros/llamadas:
  param <value>
  tX = call <func>, <argc>
  tX = call method <meth>, <argc>   # si fue invocada como método
  call <func>, <argc>               # si no capturas retorno
  call method <meth>, <argc>

- Acceso a propiedades:
  getprop <base>, <campo>          -> tX = getprop base, campo
  setprop <base>, <campo>, <val>   -> setprop base, campo, val
  (En métodos, el "base" típico será "this")

- Primitivas aritméticas:
  tX = tA + tB
  tX = tA - tB
  tX = tA * tB
  tX = tA / tB
  tX = tA % tB

- String helpers:
  __strcat_new(a, b)
  __int_to_string(x)

- Objetos:
  tX = new <ClassName>

Este emisor solo arma el TAC; tu backend MIPS ya puede mapear cada mnemónico.

No usa f-strings. Intenta mantener el estilo simple y directo.
"""

class IREmitter:
    def __init__(self):
        self.lines: List[str] = []
        self.class_stack: List[str] = []
        # Layout de campos por clase si lo necesitas para el backend
        self.class_fields: Dict[str, Dict[str, int]] = {}

    # ==============
    # Infraestructura
    # ==============
    def enter_class(self, class_name: str) -> None:
        self.class_stack.append(class_name)
        if class_name not in self.class_fields:
            self.class_fields[class_name] = {}

    def leave_class(self, class_name: str) -> None:
        if len(self.class_stack) > 0 and self.class_stack[-1] == class_name:
            self.class_stack.pop()

    def begin_func(self, name: str, nparams: int, is_method: bool, needs_this: bool) -> None:
        self.lines.append("FUNC " + str(name) + "_START:")
        self.lines.append("BeginFunc " + str(name) + " " + str(nparams))
        self.lines.append("ActivationRecord " + str(name))
        # Nota: el manejo explícito de LoadParam lo hará tu backend;
        # aquí asumimos que el parser/visitor colocará los 'param' en llamadas.

    def emit_activation_record(self, name: str) -> None:
        # Visual; ya se imprime arriba.
        pass

    def end_func(self, name: str) -> None:
        self.lines.append("FUNC " + str(name) + "_END:")
        self.lines.append("EndFunc " + str(name))

    # ============
    # Expresiones
    # ============
    def emit_load_int(self, tdest: str, value: int) -> None:
        self.lines.append(tdest + " = " + str(value))

    def emit_load_str(self, tdest: str, quoted: str) -> None:
        # quoted viene con comillas del parser
        self.lines.append(tdest + " = " + str(quoted))

    def emit_concat(self, tdest: str, a: str, b: str) -> None:
        # Modelo de concatenación con helper de runtime
        # tdest = a + b
        self.lines.append(tdest + " = " + str(a) + " + " + str(b))

    def emit_add(self, tdest: str, a: str, b: str) -> None:
        self.lines.append(tdest + " = " + str(a) + " + " + str(b))

    def emit_sub(self, tdest: str, a: str, b: str) -> None:
        self.lines.append(tdest + " = " + str(a) + " - " + str(b))

    def emit_mul(self, tdest: str, a: str, b: str) -> None:
        self.lines.append(tdest + " = " + str(a) + " * " + str(b))

    def emit_div(self, tdest: str, a: str, b: str) -> None:
        self.lines.append(tdest + " = " + str(a) + " / " + str(b))

    def emit_mod(self, tdest: str, a: str, b: str) -> None:
        self.lines.append(tdest + " = " + str(a) + " % " + str(b))

    # toString / coerciones
    def emit_to_string(self, tdest: str, val: str) -> None:
        # Llama al builtin toString(val)
        self.lines.append("param " + str(val))
        self.lines.append(tdest + " = call toString, 1")

    # ============
    # Propiedades
    # ============
    def emit_getprop(self, tdest: str, base: str, field: str) -> None:
        self.lines.append(tdest + " = getprop " + str(base) + ", " + str(field))

    def emit_setprop(self, base: str, field: str, val: str) -> None:
        self.lines.append("setprop " + str(base) + ", " + str(field) + ", " + str(val))

    # ============
    # Asignaciones
    # ============
    def emit_assign_local(self, name: str, val: str) -> None:
        self.lines.append(str(name) + " = " + str(val))

    # =======
    # Llamada
    # =======
    def emit_param(self, val: str) -> None:
        self.lines.append("param " + str(val))

    def emit_call(self, fname: str, argc: int) -> None:
        self.lines.append("call " + str(fname) + ", " + str(argc))

    def emit_call_assign(self, tdest: str, fname: str, argc: int) -> None:
        self.lines.append(tdest + " = call " + str(fname) + ", " + str(argc))

    def emit_call_method(self, tdest: str, mname: str, argc: int) -> None:
        self.lines.append(tdest + " = call method " + str(mname) + ", " + str(argc))

    # =======
    # Retorno
    # =======
    def emit_return(self, val: Optional[str]) -> None:
        if val is None:
            self.lines.append("return")
            return
        self.lines.append("return " + str(val))

    def emit_return_zero(self) -> None:
        t = "t_zero"
        self.lines.append(t + " = 0")
        self.lines.append("return " + t)

    def emit_return_empty_string(self) -> None:
        t = "t_empty"
        self.lines.append(t + " = " + "\"\"")
        self.lines.append("return " + t)

    # =======
    # Objetos
    # =======
    def emit_new_object(self, tdest: str, class_name: str) -> None:
        self.lines.append(tdest + " = new " + str(class_name))

    # ===========
    # Depuración
    # ===========
    def dump(self) -> str:
        return "\n".join(self.lines)
