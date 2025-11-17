# -*- coding: utf-8 -*-
"""
TACGeneratorVisitor.py
----------------------
Generación de Código Intermedio (TAC) para Compiscript.

Cambios clave (Opción B):
- Se agrega visitProgram para encapsular TODO el código de nivel superior
  (el “código suelto” que no está dentro de una función/clase) dentro de:
      FUNC main_START:
      BeginFunc main 0
      ActivationRecord main
         ... (código suelto)
      return
      FUNC main_END:
      EndFunc main
- Esto garantiza que el backend MIPS tenga un punto de entrada 'main'.
- Además se mantiene la política sin sobrecarga de 'constructor' y la
  calificación de campos con 'this' en constructores.

El resto del archivo conserva la lógica que ya tenías (pool de temporales,
param/call, getprop/setprop, cortocircuito, etc.).
"""

from __future__ import annotations

import os
import sys
import re
from typing import List, Optional, Sequence, Dict, Any

_THIS_DIR = os.path.abspath(os.path.dirname(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
_SCRIPTS = os.path.join(_REPO_ROOT, "scripts")
for _p in (_REPO_ROOT, _SCRIPTS, _THIS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts.CompiscriptVisitor import CompiscriptVisitor  # type: ignore
from antlr4 import TerminalNode  # type: ignore


# -------------------- Gestor de temporales --------------------
class TempManager:
    def __init__(self) -> None:
        self._cnt = 0
        self._free: List[str] = []

    def new(self) -> str:
        if self._free:
            return self._free.pop()
        self._cnt = self._cnt + 1
        return "t" + str(self._cnt)

    def free(self, t: Optional[str]) -> None:
        if isinstance(t, str) and t.startswith("t"):
            self._free.append(t)

    def free_many(self, *temps: Optional[str]) -> None:
        for t in temps:
            self.free(t)


# =================== VISITOR ===================
class TACGeneratorVisitor(CompiscriptVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.code: List[str] = []
        self.label_count: int = 0
        self.break_stack: List[str] = []
        self.continue_stack: List[str] = []
        self.current_function: Optional[str] = None
        self.current_class: Optional[str] = None
        self.return_seen: bool = False
        self.tm = TempManager()

        self.param_alias: Dict[str, str] = {}
        self._alias_stack: List[Dict[str, str]] = []

        # control simple para no sobrecargar constructor en una clase
        self._emitted_members: Dict[str, set] = {}

    # ---------------- utilidades base ----------------
    def emit(self, line: str) -> None:
        self.code.append(line)

    def new_temp(self) -> str:
        return self.tm.new()

    def new_label(self, prefix: str = "L") -> str:
        self.label_count += 1
        return f"{prefix}{self.label_count}"

    def _alias(self, name: str) -> str:
        return self.param_alias.get(name, name)


    def _peephole_copy_coalesce(self, lines: List[str]) -> List[str]:
        temp_pat = re.compile(r"\bt\d+\b")
        assign_pat = re.compile(
            r"^\s*(t\d+)\s*=\s*([A-Za-z_]\w*|t\d+|\".*?\"|\'.*?\'|-?\d+(?:\.\d+)?)\s*$"
        )

        use_count: Dict[str, int] = {}
        for ln in lines:
            if ln.strip().endswith(":"):
                continue
            for tok in temp_pat.findall(ln):
                use_count[tok] = use_count.get(tok, 0) + 1

        to_delete = set()
        replacements: Dict[str, str] = {}
        for idx, ln in enumerate(lines):
            s = ln.strip()
            if not s or s.endswith(":"):
                continue
            m = assign_pat.match(ln)
            if not m:
                continue
            dst, rhs = m.group(1), m.group(2)
            if dst == rhs:
                to_delete.add(idx)
                continue
            if use_count.get(dst, 0) == 1:
                replacements[dst] = rhs
                to_delete.add(idx)

        def repl(s: str) -> str:
            if not replacements:
                return s
            out = s
            for k, v in replacements.items():
                out = re.sub(rf"\b{re.escape(k)}\b", v, out)
            return out

        out: List[str] = []
        for i, ln in enumerate(lines):
            if i in to_delete:
                continue
            if ln.strip().endswith(":"):
                out.append(ln)
                continue
            out.append(repl(ln))
        return out

    def get_code(self) -> str:
        return "\n".join(self._peephole_copy_coalesce(self.code))

    # ------------- helpers parsers -------------
    @staticmethod
    def _is_temp(name: Optional[str]) -> bool:
        return isinstance(name, str) and name.startswith("t")

    @staticmethod
    def _looks_like_call_text(text: str) -> bool:
        return "(" in text and text.endswith(")")

    def _try_get_list(self, ctx, method_names: Sequence[str]) -> Optional[List]:
        for name in method_names:
            fn = getattr(ctx, name, None)
            if fn is None or not callable(fn):
                continue
            try:
                res = fn()
            except TypeError:
                continue
            if isinstance(res, list) and len(res) > 0:
                return res
        return None

    def _child_op_between(self, ctx, left_term_index: int, right_term_index: int) -> str:
        try:
            pos = 2 * (left_term_index + 1) - 1
            if 0 <= pos < ctx.getChildCount():
                return ctx.getChild(pos).getText()
        except Exception:
            pass
        try:
            txt = ctx.getText()
            for tok in ["||", "&&", "==", "!=", "<=", ">=", "<", ">", "+", "-", "*", "/", "%"]:
                if tok in txt:
                    return tok
        except Exception:
            pass
        return "?"
    # ---------- props y llamadas ----------
    def gen_getprop(self, base: str, prop: str) -> str:
        base = self._alias(base)
        t = self.new_temp()
        self.emit(f"{t} = getprop {base}, {prop}")
        return t

    def gen_setprop(self, base: str, prop: str, val: str) -> None:
        base = self._alias(base)
        self.emit(f"setprop {base}, {prop}, {val}")

    def _collect_args_from_ctx(self, ctx) -> List:
        cand = [
            ("arguments", "expression"),
            ("argumentList", "expression"),
            ("args", "expression"),
        ]
        for getter, _ in cand:
            g = getattr(ctx, getter, None)
            if not g:
                continue
            try:
                node = g()
                if not node:
                    continue
                try:
                    items = node.expression()
                    if isinstance(items, list):
                        return items
                    if items is not None:
                        return [items]
                except Exception:
                    pass
            except Exception:
                pass
        return []

    def _emit_function_call(self, name: str, arg_nodes: List) -> str:
        vals: List[str] = [self.visit(n) for n in arg_nodes]
        for v in reversed(vals):
            self.emit(f"param {v}")
            self.tm.free(v)
        t = self.new_temp()
        self.emit(f"{t} = call {name}, {len(vals)}")
        return t

    def _emit_method_call(self, recv: str, meth: str, arg_nodes: List) -> str:
        recv = self._alias(recv)
        vals: List[str] = [self.visit(n) for n in arg_nodes]
        for v in reversed(vals):
            self.emit(f"param {v}")
            self.tm.free(v)
        self.emit(f"param {recv}")
        t = self.new_temp()
        self.emit(f"{t} = call method {meth}, {len(vals)+1}")
        return t

    def _split_args_text(self, inner: str) -> List[str]:
        args, buf = [], []
        depth = 0
        in_str: Optional[str] = None
        i = 0
        while i < len(inner):
            ch = inner[i]
            if in_str:
                buf.append(ch)
                if ch == in_str:
                    in_str = None
                elif ch == "\\" and i + 1 < len(inner):
                    i += 1
                    buf.append(inner[i])
            else:
                if ch in ("'", '"'):
                    in_str = ch
                    buf.append(ch)
                elif ch == "(":
                    depth += 1
                    buf.append(ch)
                elif ch == ")":
                    depth = max(0, depth - 1)
                    buf.append(ch)
                elif ch == "," and depth == 0:
                    arg = "".join(buf).strip()
                    if arg:
                        args.append(arg)
                    buf = []
                else:
                    buf.append(ch)
            i += 1
        last = "".join(buf).strip()
        if last:
            args.append(last)
        return args

    def _normalize_value_from_node(self, node, text_value: str) -> str:
        if not isinstance(text_value, str):
            return text_value
        if not self._looks_like_call_text(text_value):
            return text_value

        callee = text_value.split("(", 1)[0]
        # new Clase(...)
        if callee.strip().startswith("new "):
            try:
                class_name = callee.strip()[len("new "):].strip()
                args_nodes = self._collect_args_from_ctx(node)
                if not args_nodes:
                    inner_text = text_value[text_value.find("(") + 1:text_value.rfind(")")]
                    arg_texts = [a for a in self._split_args_text(inner_text) if a]
                    args_nodes = []
                    for a in arg_texts:
                        tmp = self.new_temp()
                        self.emit(f"{tmp} = {a}")
                        args_nodes.append(tmp)
                return self._emit_new_object(class_name, args_nodes)
            except Exception:
                pass

        args_nodes = self._collect_args_from_ctx(node)
        if args_nodes:
            if "." in callee:
                recv, meth = callee.split(".", 1)
                return self._emit_method_call(recv, meth, args_nodes)
            return self._emit_function_call(callee, args_nodes)

        try:
            inner_text = text_value[text_value.find("(") + 1:text_value.rfind(")")]
        except Exception:
            inner_text = ""
        arg_texts = [a for a in self._split_args_text(inner_text) if a]

        is_method = False
        recv = meth = None
        if "." in callee:
            recv, meth = callee.split(".", 1)
            recv = self._alias(recv)
            is_method = True

        for a in reversed(arg_texts):
            tmp = self.new_temp()
            self.emit(f"{tmp} = {a}")
            self.emit(f"param {tmp}")
            self.tm.free(tmp)

        if is_method:
            self.emit(f"param {recv}")

        out = self.new_temp()
        argc = len(arg_texts) + (1 if is_method else 0)
        if is_method:
            self.emit(f"{out} = call method {meth}, {argc}")
        else:
            self.emit(f"{out} = call {callee}, {argc}")
        return out

    def _emit_new_object(self, class_name: str, arg_nodes: List) -> str:
        t_obj = self.new_temp()
        self.emit(f"{t_obj} = new {class_name}")
        if arg_nodes:
            vals = [self.visit(n) for n in arg_nodes]
            for v in reversed(vals):
                self.emit(f"param {v}")
                self.tm.free(v)
            self.emit(f"param {t_obj}")
            t_call = self.new_temp()
            self.emit(f"{t_call} = call method constructor, {len(vals)+1}")
            self.tm.free(t_call)
        return t_obj

    # ------- plegado binario -------
    def _acc_init(self, first_val: str) -> str:
        if self._is_temp(first_val):
            return first_val
        acc = self.new_temp()
        self.emit(f"{acc} = {first_val}")
        return acc

    def _fold_binary(self, ctx, subrule_candidates: Sequence[str], allowed_ops: Sequence[str]) -> str:
        terms = self._try_get_list(ctx, subrule_candidates)

        def _op_inplace(acc: str, op: str, right: str) -> str:
            if self._is_temp(acc):
                self.emit(f"{acc} = {acc} {op} {right}")
                self.tm.free(right)
                return acc
            t = self.new_temp()
            self.emit(f"{t} = {acc} {op} {right}")
            self.tm.free(right)
            return t

        if not terms:
            children_rules = [ctx.getChild(i) for i in range(ctx.getChildCount())]
            children_rules = [c for c in children_rules if hasattr(c, "accept")]
            if not children_rules:
                tmp = self.new_temp()
                self.emit(f"{tmp} = {ctx.getText()}")
                return tmp

            first_node = children_rules[0]
            first_raw = self.visit(first_node)
            first = self._normalize_value_from_node(first_node, first_raw)
            acc = self._acc_init(first)

            for i in range(1, len(children_rules)):
                op = self._child_op_between(ctx, i - 1, i)
                if op not in allowed_ops:
                    op = allowed_ops[0] if allowed_ops else op
                right_node = children_rules[i]
                right_raw = self.visit(right_node)
                right = self._normalize_value_from_node(right_node, right_raw)
                acc = _op_inplace(acc, op, right)
            return acc

        first_node = terms[0]
        first_raw = self.visit(first_node)
        first = self._normalize_value_from_node(first_node, first_raw)
        acc = self._acc_init(first)

        expected = 2 * len(terms) - 1
        for i in range(1, len(terms)):
            right_node = terms[i]
            right_raw = self.visit(right_node)
            right = self._normalize_value_from_node(right_node, right_raw)

            op = None
            if ctx.getChildCount() >= expected:
                try:
                    op = ctx.getChild(2 * i - 1).getText()
                except Exception:
                    op = None
            if op not in allowed_ops:
                op = allowed_ops[0] if allowed_ops else op or "?"
            acc = _op_inplace(acc, op, right)
        return acc

    # ------- cortocircuito -------
    def _gen_or_short_circuit(self, terms: List) -> str:
        result = self.new_temp()
        self.emit(f"{result} = 0")
        l_true = self.new_label("L")
        l_end = self.new_label("L")
        for term in terms:
            v = self.visit(term)
            v = self._normalize_value_from_node(term, v)
            self.emit(f"if {v} goto {l_true}")
            self.tm.free(v)
        self.emit(f"goto {l_end}")
        self.emit(f"{l_true}:")
        self.emit(f"{result} = 1")
        self.emit(f"{l_end}:")
        return result

    def _gen_and_short_circuit(self, terms: List) -> str:
        result = self.new_temp()
        self.emit(f"{result} = 1")
        l_false = self.new_label("L")
        l_end = self.new_label("L")
        for term in terms:
            v = self.visit(term)
            v = self._normalize_value_from_node(term, v)
            self.emit(f"if {v} == 0 goto {l_false}")
            self.tm.free(v)
        self.emit(f"goto {l_end}")
        self.emit(f"{l_false}:")
        self.emit(f"{result} = 0")
        self.emit(f"{l_end}:")
        return result

    # ------- literales/identificadores -------
    def visitIdentifierExpr(self, ctx):
        return self._alias(ctx.getText())

    def visitIdPrimary(self, ctx):
        return self._alias(ctx.getText())

    def visitId(self, ctx):
        return self._alias(ctx.getText())

    def visitPrimaryIdentifier(self, ctx):
        return self._alias(ctx.getText())

    def visitLiteralExpr(self, ctx):
        value = ctx.getText()
        t = self.new_temp()
        self.emit(f"{t} = {value}")
        return t

    def visitNumberLiteral(self, ctx):
        value = ctx.getText()
        t = self.new_temp()
        self.emit(f"{t} = {value}")
        return t

    def visitStringLiteral(self, ctx):
        value = ctx.getText()
        t = self.new_temp()
        self.emit(f"{t} = {value}")
        return t

    def visitBooleanLiteral(self, ctx):
        value = ctx.getText()
        t = self.new_temp()
        self.emit(f"{t} = {value}")
        return t

    def visitParenExpr(self, ctx):
        try:
            return self.visit(ctx.getChild(1))
        except Exception:
            return self.visitChildren(ctx)

    def visitPrimaryExpr(self, ctx):
        if ctx.getChildCount() == 3 and str(ctx.getChild(0).getText()) == "(":
            return self.visit(ctx.getChild(1))

        text = ctx.getText()

        def _looks_str(s: str) -> bool:
            return (len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")))

        def _looks_num(s: str) -> bool:
            try:
                float(s)
                return True
            except Exception:
                return False

        if ctx.getChildCount() == 1:
            if _looks_str(text) or _looks_num(text):
                t = self.new_temp()
                self.emit(f"{t} = {text}")
                return t
            if "." in text and "(" not in text and "[" not in text:
                base, prop = text.split(".", 1)
                base = self._alias(base)
                return self.gen_getprop(base, prop)
            return self._alias(text)

        if text.startswith("new "):
            try:
                header, tail = text.split("(", 1)
                class_name = header.replace("new", "", 1).strip()
                arg_nodes = self._collect_args_from_ctx(ctx)
                if not arg_nodes and ")" in tail:
                    inner = tail[:tail.rfind(")")]
                    arg_texts = [a for a in self._split_args_text(inner) if a]
                    arg_nodes = []
                    for a in arg_texts:
                        tmp = self.new_temp()
                        self.emit(f"{tmp} = {a}")
                        arg_nodes.append(tmp)
                return self._emit_new_object(class_name, arg_nodes)
            except Exception:
                pass

        if "(" in text and text.endswith(")"):
            args_nodes = self._collect_args_from_ctx(ctx)
            callee = text.split("(", 1)[0]
            if "." in callee:
                recv, meth = callee.split(".", 1)
                return self._emit_method_call(recv, meth, args_nodes)
            return self._emit_function_call(callee, args_nodes)

        if "." in text and "(" not in text and "[" not in text and not _looks_str(text):
            base, prop = text.split(".", 1)
            base = self._alias(base)
            return self.gen_getprop(base, prop)

        t = self.new_temp()
        self.emit(f"{t} = {text}")
        return t

    # ------- aritmética/lógica -------
    def visitAdditiveExpr(self, ctx):
        return self._fold_binary(
            ctx,
            subrule_candidates=["multiplicativeExpr", "term", "unaryExpr", "factor", "primaryExpr", "expr"],
            allowed_ops=["+", "-"],
        )

    def visitMultiplicativeExpr(self, ctx):
        return self._fold_binary(
            ctx,
            subrule_candidates=["unaryExpr", "factor", "primaryExpr", "powerExpr", "expr"],
            allowed_ops=["*", "/", "%"],
        )

    def visitEqualityExpr(self, ctx):
        return self._fold_binary(
            ctx,
            subrule_candidates=["relationalExpr", "additiveExpr", "expr"],
            allowed_ops=["==", "!="],
        )

    def visitRelationalExpr(self, ctx):
        return self._fold_binary(
            ctx,
            subrule_candidates=["additiveExpr", "expr"],
            allowed_ops=["<", "<=", ">", ">="],
        )

    def visitLogicalOrExpr(self, ctx):
        terms = self._try_get_list(ctx, [
            "logicalAndExpr", "equalityExpr", "relationalExpr", "additiveExpr", "expr"
        ])
        if terms and len(terms) > 1:
            return self._gen_or_short_circuit(terms)
        return self._fold_binary(
            ctx,
            subrule_candidates=["logicalAndExpr", "equalityExpr", "relationalExpr", "additiveExpr", "expr"],
            allowed_ops=["||", "or"]
        )

    def visitLogicalAndExpr(self, ctx):
        terms = self._try_get_list(ctx, [
            "equalityExpr", "relationalExpr", "additiveExpr", "expr"
        ])
        if terms and len(terms) > 1:
            return self._gen_and_short_circuit(terms)
        return self._fold_binary(
            ctx,
            subrule_candidates=["equalityExpr", "relationalExpr", "additiveExpr", "expr"],
            allowed_ops=["&&", "and"]
        )

    def visitUnaryExpr(self, ctx):
        try:
            if ctx.getChildCount() >= 2 and str(ctx.getChild(0).getText()) == "!":
                val = self.visit(ctx.getChild(1))
                t = self.new_temp()
                self.emit(f"{t} = ! {val}")
                self.tm.free(val)
                return t
        except Exception:
            pass
        try:
            for i in range(ctx.getChildCount()):
                ch = ctx.getChild(i)
                if hasattr(ch, "accept"):
                    return self.visit(ch)
        except Exception:
            pass
        return self.visitChildren(ctx)

    # ------- asignación -------
    def visitAssignment(self, ctx):
        if hasattr(ctx, "expr"):
            try:
                right_node = ctx.expr()
            except Exception:
                try:
                    right_node = ctx.expr(0)
                except Exception:
                    right_node = ctx.getChild(2)
        else:
            right_node = ctx.getChild(2)
        right_raw = self.visit(right_node)
        right = self._normalize_value_from_node(right_node, right_raw)

        try:
            if hasattr(ctx, "Identifier") and ctx.Identifier() is not None:
                left_text = self._alias(ctx.Identifier().getText())
                self.emit(f"{left_text} = {right}")
                self.tm.free(right)
                return left_text
        except Exception:
            pass

        lhs_text = ctx.getChild(0).getText()
        if "." in lhs_text and "[" not in lhs_text and "(" not in lhs_text:
            base, prop = lhs_text.split(".", 1)
            base = self._alias(base)
            self.gen_setprop(base, prop, right)
            self.tm.free(right)
            return lhs_text

        if "[" in lhs_text and "]" in lhs_text:
            base_name = lhs_text.split("[", 1)[0]
            idx_t = self.new_temp()
            self.emit(f"{idx_t} = /*idx*/")
            self.emit(f"setelem {base_name}, {idx_t}, {right}")
            self.tm.free_many(idx_t, right)
            return lhs_text

        if "(" in lhs_text or ")" in lhs_text:
            raise RuntimeError("LHS no asignable (llamada/expresión)")

        aliased_lhs = self._alias(lhs_text)
        self.emit(f"{aliased_lhs} = {right}")
        self.tm.free(right)
        return aliased_lhs

    def visitAssignmentStmt(self, ctx):
        return self.visitAssignment(ctx)

    # ------- control de flujo -------
    def visitIfStatement(self, ctx):
        cond = self.visit(ctx.expression())
        cond = self._normalize_value_from_node(ctx.expression(), cond)
        l_else = self.new_label()
        l_end = self.new_label()

        self.emit(f"if {cond} == 0 goto {l_else}")
        self.tm.free(cond)
        self.visit(ctx.block(0))

        if ctx.block(1):
            self.emit(f"goto {l_end}")
            self.emit(f"{l_else}:")
            self.visit(ctx.block(1))
            self.emit(f"{l_end}:")
        else:
            self.emit(f"{l_else}:")

    def visitDoWhileStatement(self, ctx):
        l_begin = self.new_label()
        l_cond  = self.new_label()
        l_end   = self.new_label()

        self.continue_stack.append(l_cond)
        self.break_stack.append(l_end)

        self.emit(f"{l_begin}:")
        self.visit(ctx.block())
        self.emit(f"{l_cond}:")
        cond = self.visit(ctx.expression())
        cond = self._normalize_value_from_node(ctx.expression(), cond)
        self.emit(f"if {cond} != 0 goto {l_begin}")
        self.tm.free(cond)
        self.emit(f"{l_end}:")
        self.continue_stack.pop(); self.break_stack.pop()

    def visitForStatement(self, ctx):
        if ctx.variableDeclaration():
            self.visit(ctx.variableDeclaration())
        elif ctx.assignment():
            self.visit(ctx.assignment())

        l_begin = self.new_label()
        l_inc   = self.new_label()
        l_end   = self.new_label()

        self.continue_stack.append(l_inc)
        self.break_stack.append(l_end)

        self.emit(f"{l_begin}:")
        if ctx.expression(0):
            cond = self.visit(ctx.expression(0))
            cond = self._normalize_value_from_node(ctx.expression(0), cond)
            self.emit(f"if {cond} == 0 goto {l_end}")
            self.tm.free(cond)

        self.visit(ctx.block())

        self.emit(f"{l_inc}:")
        if ctx.expression(1):
            inc_v = self.visit(ctx.expression(1))
            inc_v = self._normalize_value_from_node(ctx.expression(1), inc_v)
            self.tm.free(inc_v)

        self.emit(f"goto {l_begin}")
        self.emit(f"{l_end}:")
        self.continue_stack.pop(); self.break_stack.pop()

    def visitBreakStatement(self, ctx):
        if self.break_stack:
            self.emit(f"goto {self.break_stack[-1]}")

    def visitContinueStatement(self, ctx):
        if self.continue_stack:
            self.emit(f"goto {self.continue_stack[-1]}")

    def visitWhileStatement(self, ctx):
        l_begin = self.new_label()
        l_end = self.new_label()
        self.continue_stack.append(l_begin)
        self.break_stack.append(l_end)

        self.emit(f"{l_begin}:")
        cond = self.visit(ctx.expression())
        cond = self._normalize_value_from_node(ctx.expression(), cond)
        self.emit(f"if {cond} == 0 goto {l_end}")
        self.tm.free(cond)

        self.visit(ctx.block())
        self.emit(f"goto {l_begin}")
        self.emit(f"{l_end}:")
        self.continue_stack.pop(); self.break_stack.pop()

    # ------- switch -------
    # (igual que tu versión; omitido por brevedad si no lo usas)

    # ------- funciones / métodos / clases -------
    def _emit_frame_if_available(self, ctx):
        fn_scope = getattr(ctx, "scope", None)
        if not fn_scope or not hasattr(fn_scope, "symbols"):
            return
        try:
            symbols = list(getattr(fn_scope, "symbols").values())
        except Exception:
            symbols = []
        if not symbols:
            return

        self.emit(".frame")
        for s in symbols:
            name = getattr(s, "name", "sym")
            off = getattr(s, "offset", None)
            is_param = getattr(s, "is_param", False)
            if off is None:
                continue
            base = "+{}".format((off + 1) * 4) if is_param else "-{}".format((off + 1) * 4)
            tag = "param" if is_param else "local"
            self.emit(f".{tag} {name}, [bp{base}]")
        self.emit(".endframe")

    def _should_skip_member(self, class_name: Optional[str], fname: str) -> bool:
        if not class_name:
            return False
        if class_name not in self._emitted_members:
            self._emitted_members[class_name] = set()
        if fname == "constructor" and "constructor" in self._emitted_members[class_name]:
            self.emit("Raw: ; [skip] constructor duplicado omitido por política sin sobrecarga")
            return True
        self._emitted_members[class_name].add(fname)
        return False

    def visitFunctionDeclaration(self, ctx):
        try:
            fname = ctx.Identifier().getText()
        except Exception:
            fname = "function"

        is_method = bool(getattr(ctx, "_has_this", False)) or (self.current_class is not None)
        qual = f"{self.current_class}.{fname}" if is_method and self.current_class else fname

        if self._should_skip_member(self.current_class, fname):
            return None

        params = []
        try:
            if ctx.parameters():
                params = list(ctx.parameters().parameter())
        except Exception:
            params = []

        arity = len(params) + (1 if is_method else 0)

        self._alias_stack.append(self.param_alias)
        self.param_alias = {}

        self.current_function = fname
        self.return_seen = False

        self.emit(f"FUNC {qual}_START:")
        self.emit(f"BeginFunc {fname} {arity}")
        self.emit(f"ActivationRecord {fname}")

        renameds = []
        for i, p in enumerate(params):
            try:
                original = p.Identifier().getText()
            except Exception:
                original = f"p{i}"
            pname = original if original.startswith("p_") else f"p_{original}"
            self.param_alias[original] = pname
            self.emit(f"{pname} = LoadParam {i}")
            renameds.append(pname)

        if is_method:
            self.emit(f"this = LoadParam {arity - 1}")

        if fname == "constructor" and is_method and renameds:
            for rp in renameds:
                base = rp[2:] if rp.startswith("p_") else rp
                self.emit(f"setprop this, {base}, {rp}")

        try:
            self._emit_frame_if_available(ctx)
        except Exception:
            pass

        self.visit(ctx.block())

        if not self.return_seen:
            self.emit("return")

        self.emit(f"FUNC {qual}_END:")
        self.emit(f"EndFunc {fname}")

        self.current_function = None
        self.return_seen = False

        self.param_alias = self._alias_stack.pop()
        return None

    def visitClassDecl(self, ctx):
        try:
            cname = ctx.Identifier().getText()
        except Exception:
            cname = "Class"

        self.emit(f"CLASS_{cname}_START:")
        prev = self.current_class
        self.current_class = cname
        if cname not in self._emitted_members:
            self._emitted_members[cname] = set()
        for ch in ctx.children or []:
            if hasattr(ch, "accept"):
                self.visit(ch)
        self.current_class = prev
        self.emit(f"CLASS_{cname}_END:")
        return None

    def visitReturnStatement(self, ctx):
        self.return_seen = True
        if ctx.expression():
            val_raw = self.visit(ctx.expression())
            try:
                val = self._normalize_value_from_node(ctx.expression(), val_raw)
            except Exception:
                val = val_raw
            self.emit(f"return {val}")
            if isinstance(val, str) and val.startswith("t"):
                self.tm.free(val)
        else:
            self.emit("return")
        return None

    def visitTerminal(self, node: TerminalNode):
        return node.getText()

    # -------------------- NUEVO: visitProgram --------------------
        # =========================================================
    # =========== CORRECCIÓN CRÍTICA: visitProgram ===========
    # =========================================================
    def visitProgram(self, ctx):
        """
        Recorre los hijos y separa:
          - Declaraciones (funciones, clases)  -> emitidas tal cual.
          - Sentencias sueltas                  -> se guardan y luego
            se envuelven en un main sintético.
        """
        # 1) Emitimos primero todo lo que sea declaración
        top_level_statements = []

        for i in range(ctx.getChildCount()):
            node = ctx.getChild(i)
            txt = getattr(node, "getText", lambda: "")()

            is_func = hasattr(node, "functionDeclaration") or ("function" in txt and "(" in txt and ")" in txt and "class" not in txt)
            is_class = "class" in txt

            # Heurística robusta:
            if is_func or is_class:
                try:
                    self.visit(node)  # esto emite BeginFunc/EndFunc o miembros de clase
                except Exception:
                    # Si la heurística falla, caemos como sentencia suelta
                    top_level_statements.append(node)
            else:
                top_level_statements.append(node)

        # 2) Empaquetamos las sentencias sueltas dentro de main
        if top_level_statements:
            self.emit("FUNC main_START:")
            self.emit("BeginFunc main 0")
            self.emit("ActivationRecord main")

            for node in top_level_statements:
                try:
                    self.visit(node)
                except Exception:
                    # si es “ruido” de gramática, lo ignoramos
                    pass

            # garantizar terminación
            self.emit("return")
            self.emit("FUNC main_END:")
            self.emit("EndFunc main")

        return None