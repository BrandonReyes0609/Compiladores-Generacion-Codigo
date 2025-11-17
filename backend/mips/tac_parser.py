# backend/mips/tac_parser.py
"""
Parser del TAC de TEXTO (el que muestra tu UI) -> lista de quads.

Reconoce:
- BeginFunc <name> <nlocals>
- EndFunc
- Label
- Goto Lx
- IfZ x goto Lx
- return x
- Param i, x     | Param x
- Call fn, argc
- x = Call fn, argc
- x = LoadParam i
- x = getprop obj, campo
- setprop obj, campo, valor
- x = this.campo
- x = new Clase           <<<  CORREGIDO
- x = a + b, a - b, etc
- x = a relop b
- Raw lines
"""

import re

REL_OPS = [
    (r'<=', "Le"), (r'>=', "Ge"), (r'==', "Eq"), (r'!=', "Ne"),
    (r'<', "Lt"),  (r'>', "Gt"),
]

BIN_OPS = [
    (r'\+', "Add"), (r'-', "Sub"), (r'\*', "Mul"),
    (r'/', "Div"),  (r'%', "Mod"),
]

def parse_tac_text(tac_text: str):
    quads = []

    for raw in (tac_text or "").splitlines():
        line = raw.strip()
        if not line:
            continue

        # --------- RASTROS / RAW -----------
        if (line.startswith("ActivationRecord")
            or line.startswith("FUNC ")
            or line.startswith(".frame")
            or line.startswith(".param")
            or line.startswith(".endframe")):
            quads.append(("Raw", line))
            continue

        # --------- IF x==0 GOTO L ----------
        m = re.match(r'^\s*if\s+([A-Za-z_]\w*)\s*==\s*0\s*goto\s+([A-Za-z_]\w*)\s*$', line, re.IGNORECASE)
        if m:
            quads.append(("IfZ", m.group(1), m.group(2)))
            continue

        # --------- LABEL ----------
        if line.endswith(":") and not line.startswith("."):
            quads.append(("Label", line[:-1].strip()))
            continue

        # --------- Begin/End Func ----------
        m = re.match(r'^BeginFunc\s+([A-Za-z_][\w$]*)\s+(\d+)$', line, re.IGNORECASE)
        if m:
            quads.append(("BeginFunc", m.group(1), int(m.group(2))))
            continue

        if re.match(r'^EndFunc$', line, re.IGNORECASE):
            quads.append(("EndFunc",))
            continue

        # --------- IFZ / GOTO ----------
        m = re.match(r'^IfZ\s+(.+)\s+goto\s+([A-Za-z_]\w*)$', line, re.IGNORECASE)
        if m:
            quads.append(("IfZ", m.group(1).strip(), m.group(2)))
            continue

        m = re.match(r'^Goto\s+([A-Za-z_]\w*)$', line, re.IGNORECASE)
        if m:
            quads.append(("Goto", m.group(1)))
            continue

        # --------- RETURN ----------
        m = re.match(r'^return(?:\s+(.*))?$', line, re.IGNORECASE)
        if m:
            src = (m.group(1) or "").strip()
            quads.append(("Return", src if src else None))
            continue

        # --------- PARAM ----------
        m = re.match(r'^Param\s+(\d+)\s*,\s*(.+)$', line, re.IGNORECASE)
        if m:
            quads.append(("Param", int(m.group(1)), m.group(2).strip()))
            continue

        m = re.match(r'^Param\s+(.+)$', line, re.IGNORECASE)
        if m:
            quads.append(("Param", m.group(1).strip()))
            continue

        # --------- CALL ----------
        m = re.match(r'^Call\s+([A-Za-z_][\w$]*)\s*,\s*(\d+)\s*,\s*([A-Za-z_]\w+)?$', line, re.IGNORECASE)
        if m:
            quads.append(("Call", m.group(3), m.group(1), int(m.group(2))))
            continue

        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*Call\s+([A-Za-z_][\w$]*)\s*,\s*(\d+)$', line, re.IGNORECASE)
        if m:
            quads.append(("Call", m.group(1), m.group(2), int(m.group(3))))
            continue

        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*call\s+(?:method\s+)?([A-Za-z_][\w$]*)\s*,\s*(\d+)$', line, re.IGNORECASE)
        if m:
            quads.append(("Call", m.group(1), m.group(2), int(m.group(3))))
            continue

        m = re.match(r'^call\s+(?:method\s+)?([A-Za-z_][\w$]*)\s*,\s*(\d+)$', line, re.IGNORECASE)
        if m:
            quads.append(("Call", None, m.group(1), int(m.group(2))))
            continue

        # --------- LOADPARAM ----------
        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*LoadParam\s+(\d+)$', line, re.IGNORECASE)
        if m:
            quads.append(("LoadParam", m.group(1), int(m.group(2))))
            continue

        # --------- PROPIEDADES ----------
        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*getprop\s+([A-Za-z_]\w*)\s*,\s*([A-Za-z_]\w*)$', line, re.IGNORECASE)
        if m:
            quads.append(("GetProp", m.group(1), m.group(2), m.group(3)))
            continue

        m = re.match(r'^setprop\s+([A-Za-z_]\w*)\s*,\s*([A-Za-z_]\w*)\s*,\s*(.+)$', line, re.IGNORECASE)
        if m:
            quads.append(("SetProp", m.group(1), m.group(2), m.group(3).strip()))
            continue

        # this.campo
        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*this\.([A-Za-z_]\w*)$', line, re.IGNORECASE)
        if m:
            quads.append(("GetProp", m.group(1), "this", m.group(2)))
            continue

        # ==================================================
        #         A S I G N A C I Ó N   C O M Ú N
        # ==================================================
        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*(.+)$', line)
        if m:
            dst = m.group(1)
            rhs = m.group(2).strip()

            # -------- NEW --------
            mnew = re.match(r'^new\s+([A-Za-z_]\w*)$', rhs)
            if mnew:
                quads.append(("New", dst, mnew.group(1)))
                continue

            # -------- RELACIONALES --------
            matched_rel = False
            for sym, tag in REL_OPS:
                mb = re.match(rf'^(.+)\s*{sym}\s*(.+)$', rhs)
                if mb:
                    quads.append((tag, dst, mb.group(1).strip(), mb.group(2).strip()))
                    matched_rel = True
                    break
            if matched_rel:
                continue

            # -------- BINARIOS --------
            matched_bin = False
            for sym, tag in BIN_OPS:
                mb = re.match(rf'^(.+)\s*{sym}\s*(.+)$', rhs)
                if mb:
                    quads.append((tag, dst, mb.group(1).strip(), mb.group(2).strip()))
                    matched_bin = True
                    break
            if matched_bin:
                continue

            # -------- ASIGNACIÓN SIMPLE --------
            quads.append(("Assign", dst, rhs))
            continue

        # -------- RAW por defecto --------
        quads.append(("Raw", line))

    return quads
