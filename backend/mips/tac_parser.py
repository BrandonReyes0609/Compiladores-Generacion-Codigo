# backend/mips/tac_parser.py
"""
Parser del TAC de TEXTO (el que muestra tu UI) -> lista de quads.

Reconoce líneas comunes en tu salida actual:
- BeginFunc <name> <nlocals>
- EndFunc
- Label: "<algo>:"         (no confunde .data/.text)
- Goto <Lx>
- IfZ <src> goto <Lx>      o 'if x == 0 goto Lx'
- x = y
- x = a (+|-|*|/|%) b
- x = a (==|!=|<|<=|>|>=) b
- Return [x]
- Param <i>, <src>   o   Param <src>
- Call <fn>, <argc>           | dst = Call <fn>, <argc>
  (permite minúsculas y 'method':  call method saludar, 1)
- x = LoadParam <i>
- x = getprop obj, campo
- setprop obj, campo, valor
- x = this.campo  -> GetProp x, this, campo
- ActivationRecord / .frame / .param / .endframe / "FUNC ..._START/END:" -> Raw
"""

import re

REL_OPS = [
    (r'<=', "Le"), (r'>=', "Ge"), (r'==', "Eq"), (r'!=', "Ne"),
    (r'<',  "Lt"), (r'>',  "Gt"),
]
BIN_OPS = [
    (r'\+', "Add"), (r'-', "Sub"), (r'\*', "Mul"), (r'/', "Div"), (r'%', "Mod"),
]

def parse_tac_text(tac_text: str):
    quads = []

    for raw in (tac_text or "").splitlines():
        line = raw.strip()
        if not line: continue

        # Comentarios/huellas del generador
        if (line.startswith("ActivationRecord")
            or line.startswith("FUNC ")
            or line.startswith(".frame")
            or line.startswith(".param")
            or line.startswith(".endframe")):
            quads.append(("Raw", line)); continue

        # if x == 0 goto Lx
        m = re.match(r'^\s*if\s+([A-Za-z_]\w*)\s*==\s*0\s*goto\s+([A-Za-z_]\w*)\s*$', line, re.IGNORECASE)
        if m: quads.append(("IfZ", m.group(1), m.group(2))); continue

        # Label (evitar .data/.text)
        if line.endswith(":") and not line.startswith("."):
            quads.append(("Label", line[:-1].strip())); continue

        # Begin/End
        m = re.match(r'^BeginFunc\s+([A-Za-z_][\w$]*)\s+(\d+)$', line, re.IGNORECASE)
        if m: quads.append(("BeginFunc", m.group(1), int(m.group(2)))); continue
        if re.match(r'^EndFunc$', line, re.IGNORECASE):
            quads.append(("EndFunc",)); continue

        # IfZ / Goto explícitos
        m = re.match(r'^IfZ\s+(.+)\s+goto\s+([A-Za-z_]\w*)$', line, re.IGNORECASE)
        if m: quads.append(("IfZ", m.group(1).strip(), m.group(2))); continue
        m = re.match(r'^Goto\s+([A-Za-z_]\w*)$', line, re.IGNORECASE)
        if m: quads.append(("Goto", m.group(1))); continue

        # Return
        m = re.match(r'^return(?:\s+(.*))?$', line, re.IGNORECASE)
        if m:
            s = (m.group(1) or "").strip()
            quads.append(("Return", s if s else None))
            continue

        # Param (con/sin índice)
        m = re.match(r'^Param\s+(\d+)\s*,\s*(.+)$', line, re.IGNORECASE)
        if m: quads.append(("Param", int(m.group(1)), m.group(2).strip())); continue
        m = re.match(r'^Param\s+(.+)$', line, re.IGNORECASE)
        if m: quads.append(("Param", m.group(1).strip())); continue

        # Call variantes
        m = re.match(r'^Call\s+([A-Za-z_][\w$]*)\s*,\s*(\d+)\s*,\s*([A-Za-z_]\w+)?$', line, re.IGNORECASE)
        if m: quads.append(("Call", m.group(3), m.group(1), int(m.group(2)))); continue
        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*Call\s+([A-Za-z_][\w$]*)\s*,\s*(\d+)$', line, re.IGNORECASE)
        if m: quads.append(("Call", m.group(1), m.group(2), int(m.group(3)))); continue
        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*call\s+(?:method\s+)?([A-Za-z_][\w$]*)\s*,\s*(\d+)$', line, re.IGNORECASE)
        if m: quads.append(("Call", m.group(1), m.group(2), int(m.group(3)))); continue
        m = re.match(r'^call\s+(?:method\s+)?([A-Za-z_][\w$]*)\s*,\s*(\d+)$', line, re.IGNORECASE)
        if m: quads.append(("Call", None, m.group(1), int(m.group(2)))); continue

        # LoadParam
        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*LoadParam\s+(\d+)$', line, re.IGNORECASE)
        if m: quads.append(("LoadParam", m.group(1), int(m.group(2)))); continue

        # Propiedades
        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*getprop\s+([A-Za-z_]\w*)\s*,\s*([A-Za-z_]\w*)$', line, re.IGNORECASE)
        if m: quads.append(("GetProp", m.group(1), m.group(2), m.group(3))); continue
        m = re.match(r'^setprop\s+([A-Za-z_]\w*)\s*,\s*([A-Za-z_]\w*)\s*,\s*(.+)$', line, re.IGNORECASE)
        if m: quads.append(("SetProp", m.group(1), m.group(2), m.group(3).strip())); continue
        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*this\.([A-Za-z_]\w*)$', line, re.IGNORECASE)
        if m: quads.append(("GetProp", m.group(1), "this", m.group(2))); continue

        # Asignaciones y binarios/relacionales
        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*(.+)$', line)
        if m:
            dst = m.group(1); rhs = m.group(2).strip()

            # relacionales
            matched_rel = False
            for sym, tag in REL_OPS:
                mb = re.match(rf'^(.+)\s*{sym}\s*(.+)$', rhs)
                if mb:
                    quads.append((tag, dst, mb.group(1).strip(), mb.group(2).strip()))
                    matched_rel = True; break
            if matched_rel: continue

            # binarios
            matched_bin = False
            for sym, tag in BIN_OPS:
                mb = re.match(rf'^(.+)\s*{sym}\s*(.+)$', rhs)
                if mb:
                    quads.append((tag, dst, mb.group(1).strip(), mb.group(2).strip()))
                    matched_bin = True; break
            if matched_bin: continue

            # asignación simple
            quads.append(("Assign", dst, rhs))
            continue

        # por defecto: conserva línea
        quads.append(("Raw", line))

    return quads
