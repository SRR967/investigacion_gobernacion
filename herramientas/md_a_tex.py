#!/usr/bin/env python3
"""Convierte un Markdown de borrador_reescrito/ en una sección LaTeX (skill gestor-latex).
Uso: python3 -I herramientas/md_a_tex.py borrador_reescrito/02_marco_teorico.md secciones/02_marco_teorico.tex
No inserta el «Informe de entrega» (lo que sigue a la primera línea '---')."""
import re, sys

def escape(t):
    t = t.replace("\\", "\\textbackslash{}")
    for a, b in [("&", "\\&"), ("%", "\\%"), ("#", "\\#"), ("$", "\\$"), ("_", "\\_")]:
        t = t.replace(a, b)
    return t

def loc(s):
    s = s.strip()
    s = re.sub(r"\b(pp?|art|num|par)\. ", lambda m: m.group(1) + ".~", s)
    s = s.replace("nota ", "nota~")
    return s

def cite_bracket(m):
    inner = m.group(1)
    parts = [p.strip() for p in inner.split(";")]
    items = []
    for p in parts:
        mm = re.match(r"@([a-z0-9]+)(?:,\s*(.+))?$", p)
        if not mm:
            return m.group(0)
        items.append((mm.group(1), mm.group(2)))
    if len(items) == 1:
        k, l = items[0]
        return f"\\parencite[{loc(l)}]{{{k}}}" if l else f"\\parencite{{{k}}}"
    return "\\parencites" + "".join(f"[{loc(l)}]{{{k}}}" if l else f"{{{k}}}" for k, l in items)

def inline(t):
    # marcas de pendiente -> placeholder antes de escapar
    pend = []
    def keep(m):
        pend.append(m.group(1)); return f"\x00P{len(pend)-1}\x00"
    t = re.sub(r"\[((?:FALTA FUENTE|CONFIRMAR|DATO PENDIENTE)[^\]]*)\]", keep, t)
    cites = []
    def keepc(m):
        cites.append(cite_bracket(m)); return f"\x00C{len(cites)-1}\x00"
    t = re.sub(r"\[(@[^\]]+)\]", keepc, t)
    t = re.sub(r"@([a-z][a-z0-9]+[0-9]{4}[a-z0-9]*)", lambda m: (cites.append(f"\\textcite{{{m.group(1)}}}"), f"\x00C{len(cites)-1}\x00")[1], t)
    t = escape(t)
    t = re.sub(r"«([^»]*)»", r"\\enquote{\1}", t)
    t = re.sub(r'"([^"]+)"', r"\\enquote{\1}", t)
    t = re.sub(r"\*([^*]+)\*", r"\\emph{\1}", t)
    t = re.sub(r"(\d) \\%", r"\1\\,\\%", t)
    t = re.sub(r"\((pp?)\. ", r"(\1.~", t)
    t = re.sub(r"\x00C(\d+)\x00", lambda m: cites[int(m.group(1))], t)
    t = re.sub(r"\x00P(\d+)\x00", lambda m: "\\pendiente{" + escape(pend[int(m.group(1))]) + "}", t)
    return t

def main(src, dst):
    lines = open(src, encoding="utf8").read().split("\n")
    out = [f"% GENERADO desde {src} — no editar a mano", ""]
    for ln in lines:
        if ln.strip() == "---":
            break
        if ln.startswith(">") :
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            cmd = {1: "section", 2: "subsection", 3: "subsubsection", 4: "paragraph"}[len(m.group(1))]
            title = re.sub(r"^[0-9.]+\s+", "", m.group(2))
            out.append(f"\\{cmd}{{{inline(title)}}}")
            continue
        mm = re.match(r"^(\d+)\.\s+(.*)$", ln)
        if mm:
            out.append(f"\\item {inline(mm.group(2))}")  # se envuelve abajo
            continue
        out.append(inline(ln))
    # envolver ítems consecutivos en enumerate
    res, inlist = [], False
    for l in out:
        if l.startswith("\\item "):
            if not inlist:
                res.append("\\begin{enumerate}"); inlist = True
            res.append(l)
        else:
            if inlist and l.strip() != "":
                res.append("\\end{enumerate}"); inlist = False
            res.append(l)
    if inlist: res.append("\\end{enumerate}")
    open(dst, "w", encoding="utf8").write("\n".join(res).rstrip() + "\n")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
