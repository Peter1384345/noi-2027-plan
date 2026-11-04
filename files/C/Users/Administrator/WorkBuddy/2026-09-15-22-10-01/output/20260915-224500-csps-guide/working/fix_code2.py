# -*- coding: utf-8 -*-
"""Improve code-block typography in an existing DOCX.

Fixes applied to every run of consecutive code paragraphs:
  * fixed line pitch (no per-line height drift from mixed CJK/Latin fonts)
  * left/right/top/bottom border so a block reads as one unit
  * block padding (space before first / after last line), indent from body text
  * keepNext so a block is not split across pages
  * snapToGrid disabled so the document grid cannot stretch code lines
"""
import copy
import sys

import docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

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


def _set(pPr, tag, **attrs):
    """Insert/replace a pPr child element, keeping schema order."""
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


def _sort_ppr(pPr):
    """Reorder existing pPr children to match the ECMA-376 schema order.

    Word validates element order strictly; pre-existing elements (e.g. shd
    emitted after jc) must be moved before new ones are inserted.
    """
    kids = list(pPr)
    kids.sort(key=lambda el: ORDER.index(el.tag.split("}")[-1])
              if el.tag.split("}")[-1] in ORDER else 999)
    for k in kids:
        pPr.remove(k)
    for k in kids:
        pPr.append(k)
    return pPr


def _remove(pPr, tag):
    el = pPr.find(qn("w:" + tag))
    if el is not None:
        pPr.remove(el)


def style_block(lines):
    """lines: list of consecutive code paragraphs forming one block."""
    n = len(lines)
    for i, p in enumerate(lines):
        pPr = _sort_ppr(_ppr(p))
        # fixed pitch 13pt: identical height for every line, enough for CJK
        # glyphs at 9pt (exact rules would otherwise clip them)
        _set(pPr, "spacing", before="0", after="0", line="260", lineRule="exact")
        _set(pPr, "snapToGrid", val="0")
        _set(pPr, "ind", left="170", right="0")
        _set(pPr, "jc", val="left")
        _set(pPr, "shd", val="clear", color="auto", fill="F4F6F8")

        # borders: sides on all lines, top on first, bottom on last
        pBdr = _set(pPr, "pBdr")
        for child in list(pBdr):
            pBdr.remove(child)
        for side in ("top", "left", "bottom", "right"):
            if side == "top" and i != 0:
                continue
            if side == "bottom" and i != n - 1:
                continue
            b = OxmlElement("w:" + side)
            b.set(qn("w:val"), "single")
            b.set(qn("w:sz"), "4")
            b.set(qn("w:space"), "0")
            b.set(qn("w:color"), "C9D1D9")
            pBdr.append(b)

        # keep block together: every line but the last stays with the next
        if i < n - 1:
            _set(pPr, "keepNext")
        else:
            _remove(pPr, "keepNext")

        # block padding from surrounding body text
        sp = pPr.find(qn("w:spacing"))
        if i == 0:
            sp.set(qn("w:before"), "120")
        if i == n - 1:
            sp.set(qn("w:after"), "120")


def is_code(p):
    runs = [r for r in p.runs if r.text.strip()]
    return bool(runs) and all((r.font.name or "") == "Consolas" for r in runs)


def main(path):
    d = docx.Document(path)
    paras = d.paragraphs
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
        style_block(b)
    d.save(path)
    print("styled code blocks: %d (lines: %d) -> %s" % (len(blocks), sum(len(b) for b in blocks), path))


if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p)
