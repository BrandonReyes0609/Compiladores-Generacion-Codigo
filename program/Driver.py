# program/Driver.py
from __future__ import annotations
import sys, time, re, json
from pathlib import Path
from typing import List, Dict, Any

# --- Rutas robustas ---
HERE    = Path(__file__).resolve().parent          # .../program
ROOT    = HERE.parent                               # repo raíz
SCRIPTS = ROOT / "scripts"                          # .../scripts
for p in (ROOT, SCRIPTS, HERE):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)

# --- Import seguro de ANTLR/gramática ---
def _import_antlr_modules():
    try:
        from scripts.CompiscriptLexer import CompiscriptLexer
        from scripts.CompiscriptParser import CompiscriptParser
        try:
            from scripts.CompiscriptVisitor import CompiscriptVisitor  # opcional
        except Exception:
            class CompiscriptVisitor: pass
        return CompiscriptLexer, CompiscriptParser, CompiscriptVisitor
    except Exception as e:
        msg = (
            "No se encontró CompiscriptLexer/Parser en /scripts.\n"
            "Genera los archivos con:\n\n"
            "  java -jar antlr-4.13.1-complete.jar "
            "-Dlanguage=Python3 -visitor -o scripts grammar/Compiscript.g4\n"
        )
        raise ImportError(msg + f"\nDetalle: {e}")

CompiscriptLexer, CompiscriptParser, _ = _import_antlr_modules()

from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

# --- Núcleo semántico/TAC (nuestros) ---
from program.symbol_table import SymbolTable
from program.type_check_visitor import TypeCheckVisitor
from program.TACGeneratorVisitor import TACGeneratorVisitor

# --- Backend MIPS ---
try:
    from backend.mips.tac_parser import parse_tac_text
    from backend.mips.emitter import MIPSEmitter
except Exception:
    parse_tac_text = None
    MIPSEmitter = None


# ---------- Listener de errores sintácticos ----------
class CollectingErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors: List[Dict[str, Any]] = []
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append({"sev":"error","line":int(line),"col":int(column),"msg":str(msg)})

# ---------- Utilidades ----------
_ERR_PAT = [
    re.compile(r".*?\b(linea|línea|line)\b\s+(\d+)\s*[: ,]\s*(\d+)\s*[:\-]?\s*(.+)", re.IGNORECASE),
]

def _semantic_str_to_struct(errs: List[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for s in errs or []:
        s = s.strip()
        m = None
        for p in _ERR_PAT:
            m = p.match(s)
            if m: break
        if m:
            out.append({"sev":"error","line":int(m.group(2)),"col":int(m.group(3)),"msg":m.group(4).strip()})
        else:
            out.append({"sev":"error","line":None,"col":None,"msg":s})
    return out

def _format_timing_line(timings: Dict[str, int], ok: bool) -> str:
    tag = "OK" if ok else "ERR"
    return (f"{tag}Parse {timings.get('parse_ms',0)} ms | "
            f"Semántica {timings.get('semantic_ms',0)} ms | "
            f"IR {timings.get('ir_ms',0)} ms | ASM {timings.get('asm_ms',0)} ms")

def _format_messages(errors: List[Dict[str, Any]], timings: Dict[str, int], tac_ok: bool) -> str:
    head = _format_timing_line(timings, ok=(len(errors) == 0 and tac_ok))
    if not errors:
        suf = "🔹 TAC generado correctamente." if tac_ok else ""
        return (head + ("\n" if suf else "") + suf + ("\n✅ Compilación sin errores." if tac_ok else "")).strip()
    body = "\n".join(f"line {e.get('line','-')}:{e.get('col','-')} {e.get('msg','')}" for e in errors)
    return (head + "\n" + body).strip()


# ============================================================
#            P O S T - P A S S   D E   T A C
#  (1) Reescribe sumas de strings: x = a + b
#      --> Param a ; Param b ; x = call __strcat_new, 2
#  (2) Reescribe 'call toString, 1' por '__int_to_str' si el arg es int
#      (no toca 'call method toString, N').
# ============================================================

_STR_FIELDS = {"nombre", "color"}        # campos string más comunes en tu modelo
_INTISH_HINT = {"edad", "grado", "prom"} # campos/temps usualmente int

def _is_quoted_string(tok: str) -> bool:
    tok = tok.strip()
    return len(tok) >= 2 and tok[0] == '"' and tok[-1] == '"'

def _token_name(tok: str) -> str:
    return tok.strip()

def _rewrite_tac_text(ir: str) -> str:
    lines = [ln.rstrip() for ln in (ir or "").splitlines()]
    if not lines:
        return ir

    # --- 1) Análisis de "stringish" variables (muy conservador) ---
    stringish: set[str] = set()

    # Marca por asignación desde literal y por getprop de campos string
    assign_re = re.compile(r'^([A-Za-z_]\w*)\s*=\s*(.+)$')
    getprop_re = re.compile(r'^([A-Za-z_]\w*)\s*=\s*getprop\s+([A-Za-z_]\w*)\s*,\s*([A-Za-z_]\w*)$', re.IGNORECASE)
    call_strcat_new_re = re.compile(r'^([A-Za-z_]\w*)\s*=\s*call\s+__strcat_new\s*,\s*2$', re.IGNORECASE)

    for ln in lines:
        m = assign_re.match(ln)
        if m:
            dst, rhs = m.group(1), m.group(2).strip()
            if _is_quoted_string(rhs):
                stringish.add(dst)
            # x = this.campo
            m2 = re.match(r'^this\.([A-Za-z_]\w*)$', rhs)
            if m2 and (m2.group(1) in _STR_FIELDS):
                stringish.add(dst)
            continue
        m = getprop_re.match(ln)
        if m and (m.group(3) in _STR_FIELDS):
            stringish.add(m.group(1)); continue
        m = call_strcat_new_re.match(ln)
        if m:
            stringish.add(m.group(1)); continue

    # --- 2) Reescritura de x = a + b cuando hay strings ---
    plus_re = re.compile(r'^([A-Za-z_]\w*)\s*=\s*(.+)\s*\+\s*(.+)$')
    out: list[str] = []
    for ln in lines:
        m = plus_re.match(ln)
        if not m:
            out.append(ln)
            continue

        dst = _token_name(m.group(1))
        a   = _token_name(m.group(2))
        b   = _token_name(m.group(3))

        a_is_str = _is_quoted_string(a) or (a in stringish) or (a in _STR_FIELDS)
        b_is_str = _is_quoted_string(b) or (b in stringish) or (b in _STR_FIELDS)

        if a_is_str or b_is_str:
            out.append("Param " + a)
            out.append("Param " + b)
            out.append(dst + " = call __strcat_new, 2")
            stringish.add(dst)
        else:
            out.append(ln)  # suma aritmética normal

    # --- 3) Reescritura de 'call toString, 1' (no method) ---
    final: list[str] = []
    i = 0
    while i < len(out):
        ln = out[i]
        m_call = re.match(r'^([A-Za-z_]\w*)\s*=\s*call\s+toString\s*,\s*1$', ln, re.IGNORECASE)
        if m_call:
            dst = m_call.group(1)
            # busca el Param inmediatamente anterior
            j = len(final) - 1
            arg_tok = None
            while j >= 0:
                prev = final[j].strip()
                m_param = re.match(r'^Param\s+(.+)$', prev, re.IGNORECASE)
                if m_param:
                    arg_tok = _token_name(m_param.group(1))
                    break
                # si encuentra otra cosa que no sea comentarios/Raw simples, corta
                break
            # decide si es int-ish
            if arg_tok is not None:
                is_intish = False
                if arg_tok in _INTISH_HINT: is_intish = True
                if _is_quoted_string(arg_tok): is_intish = False
                if arg_tok in stringish: is_intish = False
                # literal entero
                if re.match(r'^-?\d+$', arg_tok): is_intish = True

                if is_intish:
                    final.append(dst + " = call __int_to_str, 1")
                    stringish.add(dst)
                    i += 1
                    continue
            # si no se decide, se deja igual
            final.append(ln)
            i += 1
            continue

        # no tocar: 'call method toString, N'
        final.append(ln)
        i += 1

    return "\n".join(final)


# ---------- API principal para el IDE ----------
def parse_code_from_string(source: str) -> Dict[str, Any]:
    t0 = time.perf_counter()

    lexer = CompiscriptLexer(InputStream(source))
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)

    syn = CollectingErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(syn)

    tree = parser.program()  # regla inicial
    parse_tree_str = tree.toStringTree(recog=parser)

    t1 = time.perf_counter()

    # Semántico si no hay errores sintácticos
    sem_struct: List[Dict[str, Any]] = []
    symbols_tree = None
    analyzer_errors: List[str] = []
    if not syn.errors:
        type_checker = TypeCheckVisitor()
        type_checker.visit(tree)
        analyzer_errors = type_checker.errors[:]
        sem_struct = _semantic_str_to_struct(analyzer_errors)
        try:
            symbols_tree = type_checker.global_scope.to_dict()
        except Exception:
            symbols_tree = None
        try:
            type_checker.global_scope.export_json(str(ROOT / "symbol_table.json"))
        except Exception:
            pass

    t2 = time.perf_counter()

    # IR/TAC
    ir  = ""
    asm = ""
    tac_ok = False
    if not syn.errors and not analyzer_errors:
        tac = TACGeneratorVisitor()
        tac.visit(tree)
        ir = tac.get_code()

        # === APLICAR POST-PASS DE REESCRITURA ===
        ir = _rewrite_tac_text(ir)

        tac_ok = True

    t3 = time.perf_counter()

    # ASM (MIPS)
    t_asm_start = time.perf_counter()
    if tac_ok and parse_tac_text is not None and MIPSEmitter is not None:
        try:
            quads = parse_tac_text(ir)
            emitter = MIPSEmitter()
            emitter.emit_preamble()
            emitter.from_quads(quads)
            asm = emitter.build()
        except Exception as e:
            asm = "# Error al emitir MIPS: " + str(e)
    elif tac_ok:
        asm = "# Backend MIPS no disponible (faltan backend/mips/*)."
    t_asm_end = time.perf_counter()

    timings = {
        "parse_ms":    round((t1 - t0) * 1000),
        "semantic_ms": round((t2 - t1) * 1000),
        "ir_ms":       round((t3 - t2) * 1000) if tac_ok else 0,
        "asm_ms":      round((t_asm_end - t_asm_start) * 1000) if tac_ok else 0,
    }

    all_errors = syn.errors + sem_struct
    messages = _format_messages(all_errors, timings, tac_ok)

    return {
        "parse_tree": parse_tree_str,
        "messages": messages,
        "actions": "",
        "ir": ir,
        "asm": asm,
        "errors": all_errors,
        "symbols": symbols_tree,
        "timings": timings,
    }

# ---------- CLI ----------
def main(argv):
    src_path = ROOT / "program.cps"
    if len(argv) > 1:
        src_path = Path(argv[1]).resolve()

    try:
        code = Path(src_path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        code = Path(src_path).read_text(encoding="latin-1")

    out = parse_code_from_string(code)
    print(out["messages"])
    if out.get("ir"):
        print("\n=== TAC ===\n" + out["ir"])
    if out.get("asm"):
        print("\n=== ASM (MIPS) ===\n" + out["asm"])

if __name__ == '__main__':
    main(sys.argv)
