# program/type_check_visitor.py
from __future__ import annotations
from typing import Optional

# --- ParseTree (solo para type hints; tolerante si no existe) ---
try:
    from antlr4.tree.Tree import ParseTree  # type: ignore
except Exception:  # pragma: no cover
    class ParseTree:  # type: ignore
        pass

# --- Tipos / Símbolos mínimos (no forzamos dependencia de rutas) ---
try:
    # si estamos dentro de /program
    from .symbol_table import SymbolTable
except Exception:
    # si se importa por ruta raíz
    from program.symbol_table import SymbolTable  # type: ignore

# --- Visitor base tolerante ---
try:
    from scripts.CompiscriptVisitor import CompiscriptVisitor
except Exception:  # fallback muy simple
    class CompiscriptVisitor:  # type: ignore
        def visitChildren(self, node):
            result = None
            for i in range(getattr(node, "getChildCount", lambda: 0)()):
                c = node.getChild(i)
                if hasattr(c, "accept"):
                    result = c.accept(self)
            return result


class TypeCheckVisitor(CompiscriptVisitor):
    """
    Visitor de chequeo semántico “liviano” que puede trabajar:
      1) con inyección de dependencias (symbol_table, emitter), o
      2) de forma autónoma (si no se le pasan, él crea lo mínimo).

    Esto evita el error:
      TypeCheckVisitor.__init__() missing required positional arguments: 'symbol_table' and 'emitter'

    Parámetros
    ----------
    symbol_table : SymbolTable | None
        Tabla de símbolos compartida. Si es None, se crea una nueva.
    emitter : object | None
        Emisor/IR/TAC opcional. Si es None, el visitor igual funciona;
        simplemente no intentará emitir nada que dependa del emisor.
    """
    def __init__(self,
                 symbol_table: Optional[SymbolTable] = None,
                 emitter: Optional[object] = None):
        super().__init__()
        # Dependencias (opcionales)
        self.symbol_table: SymbolTable = symbol_table if symbol_table is not None else SymbolTable()
        self.emitter = emitter

        # Estado de análisis
        self.errors = []
        self._current_function = None
        self._current_class = None

    # -------- APIs de utilidad --------
    def add_error(self, msg: str, ctx: Optional[ParseTree] = None):
        if ctx is not None and hasattr(ctx, "start"):
            try:
                line = ctx.start.line
                col = ctx.start.column
                self.errors.append("linea " + str(line) + ":" + str(col) + " " + str(msg))
                return
            except Exception:
                pass
        self.errors.append(str(msg))

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    # --------- Ejemplos de visitas mínimas (no-op seguros) ----------
    # Mantengo estos métodos “seguros” para que puedas enchufarlo sin romper tu pipeline.
    def visitProgram(self, ctx):
        # Recorremos hijos; los sub-visitors harán el trabajo
        return self.visitChildren(ctx)

    def visitFunctionDeclaration(self, ctx):
        # Si tienes lógica de funciones, puedes registrar aquí en symbol_table
        # y actualizar self._current_function. Por ahora, no-op seguro:
        return self.visitChildren(ctx)

    def visitClassDeclaration(self, ctx):
        # Registra clases/campos si deseas. Por ahora, no-op seguro:
        return self.visitChildren(ctx)

    def visitReturnStatement(self, ctx):
        # Chequeos de tipo de retorno irían aquí. Por ahora, no-op:
        return self.visitChildren(ctx)

    def visitVariableDeclaration(self, ctx):
        # Puedes sincronizar con tu SymbolTable si hace falta.
        return self.visitChildren(ctx)

    def visitCallExpr(self, ctx):
        # Chequeo de aridad/tipos de argumentos si lo requieres.
        return self.visitChildren(ctx)

    # Cualquier nodo no manejado explícitamente
    def visitChildren(self, node):
        return super().visitChildren(node)
