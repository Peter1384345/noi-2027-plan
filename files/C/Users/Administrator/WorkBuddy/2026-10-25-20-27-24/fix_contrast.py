# -*- coding: utf-8 -*-
"""修低对比度：深红卡片上的深色字 → 暖白；原有红色强调 → 金色"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

F = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_定稿.pptx"
CREAM = RGBColor(0xFF, 0xF3, 0xE8)
GOLD = RGBColor(0xE8, 0xC8, 0x7A)
SKIP = {3, 4, 7, 13, 19, 21, 22, 23, 24}
EMU = 914400


def lum(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def fill_hex(sh):
    try:
        sp = sh._element.spPr
    except Exception:
        return None
    sf = sp.find(qn('a:solidFill'))
    src = sf
    if src is None:
        gf = sp.find(qn('a:gradFill'))
        if gf is not None:
            gs = gf.find(qn('a:gsLst'))
            if gs is not None and len(gs):
                src = gs[0]
    if src is None:
        return None
    c = src.find(qn('a:srgbClr'))
    return c.get('val') if c is not None else None


prs = Presentation(F)
n = 0
for si, s in enumerate(list(prs.slides)):
    if si in SKIP:
        continue
    darks = []
    for sh in s.shapes:
        h = fill_hex(sh)
        if h and lum(h) < 0.30 and sh.width and sh.height:
            darks.append((sh.left, sh.top, sh.left + sh.width, sh.top + sh.height))
    if not darks:
        continue
    for sh in s.shapes:
        if not sh.has_text_frame or not sh.width:
            continue
        cx = sh.left + sh.width / 2
        cy = sh.top + sh.height / 2
        if not any(l - 20000 <= cx <= r + 20000 and t - 20000 <= cy <= b + 20000
                   for (l, t, r, b) in darks):
            continue
        for pa in sh.text_frame.paragraphs:
            for run in pa.runs:
                t = run.text.strip()
                if not t:
                    continue
                try:
                    col = str(run.font.color.rgb)
                except Exception:
                    continue
                if lum(col) >= 0.45:
                    continue
                run.font.color.rgb = GOLD if col.upper() in ("C00000", "FF0000", "A00000") else CREAM
                n += 1
print("改色 run:", n)
prs.save(F)
