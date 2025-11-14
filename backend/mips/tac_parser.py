"""
Parser del TAC de TEXTO (el que muestra tu UI) -> lista de quads.

Reconoce líneas comunes en tu salida actual:
- BeginFunc <name> <nlocals>
- EndFunc
- Label: "<algo>:"
- Goto <Lx>
- IfZ <src> goto <Lx>
- x = y
- x = a + b   (Add/Sub/Mul/Div)
- Return [x]
- Param <i>, <src>      (por si aparece)
- Call <fn>, <argc>, <dst> (o variantes)
- x = LoadParam <i>
- x = getprop this, campo
- setprop obj, campo, valor
- ActivationRecord <name>   (se ignora como Raw)
- FUNC <name>_START/END:    (se ignoran como Raw)
"""

import re

BIN_OPS = [
    (r'\+', "Add"),
    (r'-',  "Sub"),
    (r'\*', "Mul"),
    (r'/',  "Div"),
]

def _is_int(tok):
    return tok.isdigit() or (tok.startswith("-") and tok[1:].isdigit())

def parse_tac_text(tac_text: str):
    quads = []
    for raw in (tac_text or "").splitlines():
        line = raw.strip()
        if not line:
            continue

        # Label:
        if line.endswith(":"):
            lab = line[:-1].strip()
            quads.append(("Label", lab))
            continue

        # BeginFunc name nlocals
        m = re.match(r'^BeginFunc\s+([A-Za-z_]\w*)\s+(\d+)$', line)
        if m:
            quads.append(("BeginFunc", m.group(1), int(m.group(2))))
            continue

        if line == "EndFunc":
            quads.append(("EndFunc",))
            continue

        # IfZ x goto L
        m = re.match(r'^IfZ\s+(.+)\s+goto\s+([A-Za-z_]\w*)$', line, re.IGNORECASE)
        if m:
            quads.append(("IfZ", m.group(1).strip(), m.group(2)))
            continue

        # Goto L
        m = re.match(r'^Goto\s+([A-Za-z_]\w*)$', line, re.IGNORECASE)
        if m:
            quads.append(("Goto", m.group(1)))
            continue

        # Return [x]
        m = re.match(r'^return(?:\s+(.*))?$', line, re.IGNORECASE)
        if m:
            s = (m.group(1) or "").strip()
            quads.append(("Return", s if s else None))
            continue

        # Param i, src
        m = re.match(r'^Param\s+(\d+)\s*,\s*(.+)$', line, re.IGNORECASE)
        if m:
            quads.append(("Param", int(m.group(1)), m.group(2).strip()))
            continue

        # Call f, argc, dst  (acepta variantes "dst = Call f, argc")
        m = re.match(r'^Call\s+([A-Za-z_]\w*)\s*,\s*(\d+)\s*,\s*([A-Za-z_]\w+)?$', line, re.IGNORECASE)
        if m:
            quads.append(("Call", m.group(3), m.group(1), int(m.group(2))))
            continue
        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*Call\s+([A-Za-z_]\w*)\s*,\s*(\d+)$', line, re.IGNORECASE)
        if m:
            quads.append(("Call", m.group(1), m.group(2), int(m.group(3))))
            continue

        # x = LoadParam i
        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*LoadParam\s+(\d+)$', line, re.IGNORECASE)
        if m:
            quads.append(("LoadParam", m.group(1), int(m.group(2))))
            continue

        # x = getprop obj, field
        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*getprop\s+([A-Za-z_]\w*)\s*,\s*([A-Za-z_]\w*)$', line, re.IGNORECASE)
        if m:
            quads.append(("GetProp", m.group(1), m.group(2), m.group(3)))
            continue

        # setprop obj, field, src
        m = re.match(r'^setprop\s+([A-Za-z_]\w*)\s*,\s*([A-Za-z_]\w*)\s*,\s*(.+)$', line, re.IGNORECASE)
        if m:
            quads.append(("SetProp", m.group(1), m.group(2), m.group(3).strip()))
            continue

        # x = y | x = a (+|-|*|/) b
        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*(.+)$', line)
        if m:
            dst = m.group(1)
            rhs = m.group(2).strip()

            # binarios
            matched_bin = False
            for sym, tag in BIN_OPS:
                mb = re.match(rf'^(.+)\s*{sym}\s*(.+)$', rhs)
                if mb:
                    quads.append((tag, dst, mb.group(1).strip(), mb.group(2).strip()))
                    matched_bin = True
                    break
            if matched_bin:
                continue

            # asignación simple
            quads.append(("Assign", dst, rhs))
            continue

        # líneas informativas que no afectan (ActivationRecord, FUNC x_START/END, etc.)
        if line.startswith("ActivationRecord") or line.startswith("FUNC "):
            quads.append(("Raw", line))
            continue

        # Si llegamos aquí, no lo conocemos: lo dejamos como Raw (no rompe)
        quads.append(("Raw", line))

    return quads
