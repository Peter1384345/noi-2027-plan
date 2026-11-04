# -*- coding: utf-8 -*-
"""Normalize code blocks in a docx: split soft-line-break code paragraphs into
one tidy paragraph per line, with consistent monospace font, left alignment,
zero paragraph spacing and light shading."""
import sys
import docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def set_shading(paragraph, fill):
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pPr.append(shd)


def is_code_paragraph(p):
    if "\n" not in p.text:
        return False
    for r in p.runs:
        if r.font.name in ("JetBrains Mono", "Consolas", "Courier New", "monospace"):
            return True
    return False


def make_code_line(paragraph_before, line):
    new_p = paragraph_before.insert_paragraph_before()
    new_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = new_p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.0
    run = new_p.add_run(line)
    run.font.name = "Consolas"
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), "Consolas")
    rFonts.set(qn("w:hAnsi"), "Consolas")
    rFonts.set(qn("w:eastAsia"), "微软雅黑")
    run.font.size = Pt(9)
    set_shading(new_p, "F2F4F7")
    return new_p


def fix(path):
    d = docx.Document(path)
    fixed = 0
    for p in list(d.paragraphs):
        if not is_code_paragraph(p):
            continue
        lines = [ln.replace("\t", "    ").rstrip() for ln in p.text.split("\n")]
        while lines and lines[-1] == "":
            lines.pop()
        if not lines:
            continue
        # insert new line-paragraphs before the original, then drop original
        for ln in lines:
            make_code_line(p, ln)
        p._element.getparent().remove(p._element)
        fixed += 1
    d.save(path)
    print("fixed code blocks:", fixed, "->", path)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        fix(arg)
