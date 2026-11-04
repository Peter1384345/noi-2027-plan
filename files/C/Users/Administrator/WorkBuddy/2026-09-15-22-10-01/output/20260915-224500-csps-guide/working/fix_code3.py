# -*- coding: utf-8 -*-
"""Rebuild code blocks as ONE paragraph per block (WPS/Word compatible).

Why: rendering each code line as its own paragraph relies on the client
drawing paragraph borders/shading consistently. WPS renders that as broken
stripes, and when the monospace font is missing the space-based indentation
collapses. Instead:

  * one paragraph per code block, lines separated by <w:br/>
  * indentation expressed with <w:tab/> on fixed tab stops -> alignment no
    longer depends on font metrics
  * widely available fonts (Consolas with a Song/Courier fallback set)
  * single border + single shading for the whole block
"""
import sys

import docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT_ASCII = "Consolas"
FONT_EASTASIA = "宋体"
SIZE = "18"          # 9pt
PITCH = "260"        # 13pt exact line pitch
FILL = "F4F6F8"
BORDER = "C9D1D9"
TAB = 360            # 0.63cm per indent level (4 spaces at 9pt monospace)

ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr",
         "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd",
         "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
         "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN",
         "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind",
         "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc",
         "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl",
         "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"]


def _ppr(p):
    pPr = p._p.find(qn("w:pPr"))
    if pPr is None:
        pPr = OxmlElement("w:pPr")
        p._p.insert(0, pPr)
    return pPr


def _sort_ppr(pPr):
    kids = list(pPr)
    kids.sort(key=lambda el: ORDER.index(el.tag.split("}")[-1])
              if el.tag.split("}")[-1] in ORDER else 999)
    for k in list(pPr):
        pPr.remove(k)
    for k in kids:
        pPr.append(k)
    return pPr


def _set(pPr, tag, **attrs):
    el = pPr.find(qn("w:" + tag))
    if el is None:
        el = OxmlElement("w:" + tag)
        idx = ORDER.index(tag)
        pos = None
        for child in pPr:
            name = child.tag.split("}")[-1]
            if name in ORDER and ORDER.index(name) > idx:
                pos = list(pPr).index(child)
                break
        if pos is None:
            pPr.append(el)
        else:
            pPr.insert(pos, el)
    for k, v in attrs.items():
        el.set(qn("w:" + k), v)
    return el


def _rpr():
    rPr = OxmlElement("w:rPr")
    f = OxmlElement("w:rFonts")
    f.set(qn("w:ascii"), FONT_ASCII)
    f.set(qn("w:hAnsi"), FONT_ASCII)
    f.set(qn("w:eastAsia"), FONT_EASTASIA)
    f.set(qn("w:cs"), FONT_ASCII)
    rPr.append(f)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), SIZE)
    rPr.append(sz)
    szcs = OxmlElement("w:szCs")
    szcs.set(qn("w:val"), SIZE)
    rPr.append(szcs)
    return rPr


def _line_run(text, newline):
    r = OxmlElement("w:r")
    r.append(_rpr())
    stripped = text.lstrip(" ")
    level = (len(text) - len(stripped)) // 4
    for _ in range(level):
        r.append(OxmlElement("w:tab"))
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = stripped
    r.append(t)
    if newline:
        r.append(OxmlElement("w:br"))
    return r


def format_block(p):
    pPr = _sort_ppr(_ppr(p))
    _set(pPr, "pStyle", val="Code") if False else None
    _set(pPr, "spacing", before="120", after="120", line=PITCH, lineRule="exact")
    _set(pPr, "snapToGrid", val="0")
    _set(pPr, "ind", left="170", right="0")
    _set(pPr, "jc", val="left")
    _set(pPr, "shd", val="clear", color="auto", fill=FILL)
    pBdr = _set(pPr, "pBdr")
    for child in list(pBdr):
        pBdr.remove(child)
    for side in ("top", "left", "bottom", "right"):
        b = OxmlElement("w:" + side)
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), "4")
        b.set(qn("w:space"), "2")
        b.set(qn("w:color"), BORDER)
        pBdr.append(b)
    tabs = _set(pPr, "tabs")
    for child in list(tabs):
        tabs.remove(child)
    for i in range(1, 11):
        t = OxmlElement("w:tab")
        t.set(qn("w:val"), "left")
        t.set(qn("w:pos"), str(TAB * i))
        tabs.append(t)


def is_code(p):
    runs = [r for r in p.runs if r.text.strip()]
    return bool(runs) and all((r.font.name or "") == "Consolas" for r in runs)


def merge(lines):
    """Merge consecutive code paragraphs into the first one."""
    first = lines[0]
    texts = [p.text for p in lines]
    for r in list(first.runs):
        r._r.getparent().remove(r._r)
    for i, txt in enumerate(texts):
        first._p.append(_line_run(txt, newline=(i != len(texts) - 1)))
    for p in lines[1:]:
        parent = p._p.getparent()
        if parent is not None:
            parent.remove(p._p)
    format_block(first)
    return first


def main(path):
    d = docx.Document(path)
    paras = list(d.paragraphs)
    blocks, cur = [], []
    for p in paras:
        if is_code(p):
            cur.append(p)
        else:
            if cur:
                blocks.append(cur)
                cur = []
    if cur:
        blocks.append(cur)
    for b in blocks:
        merge(b)
    d.save(path)
    print("merged code blocks: %d (lines: %d) -> %s"
          % (len(blocks), sum(len(b) for b in blocks), path))


if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p)
