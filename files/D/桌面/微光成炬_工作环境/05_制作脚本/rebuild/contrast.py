# -*- coding: utf-8 -*-
"""扫描文字与其所在背景的对比度，列出看不清的地方。"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pptx import Presentation
from pptx.oxml.ns import qn

P = sys.argv[1]
prs = Presentation(P)
EMU = 914400


def lum(c):
    def f(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def fill_rgb(sh):
    spPr = getattr(sh._element, 'spPr', None)
    if spPr is None:
        return None
    for tag in ('a:solidFill', 'a:gradFill'):
        node = spPr.find(qn(tag))
        if node is None:
            continue
        srgb = node.find(qn('a:srgbClr'))
        if srgb is None:
            gs = node.find(qn('a:gsLst'))
            if gs is not None:
                g0 = gs.find(qn('a:gs'))
                if g0 is not None:
                    srgb = g0.find(qn('a:srgbClr'))
        if srgb is not None:
            v = srgb.get('val')
            return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))
    return None


for i, s in enumerate(prs.slides, 1):
    # 找整页底
    bg = None
    for sh in s.shapes:
        if sh.width and sh.height and sh.width >= prs.slide_width * 0.95 and sh.height >= prs.slide_height * 0.95:
            bg = fill_rgb(sh)
            break
    if bg is None:
        bg = (255, 255, 255)
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if not r.text.strip():
                    continue
                try:
                    c = tuple(r.font.color.rgb)
                except Exception:
                    continue
                rt = ratio(c, bg)
                if rt < 2.2:
                    print("P%-3d 对比度%.2f  字#%02X%02X%02X 底#%02X%02X%02X  %.1fpt  %r"
                          % (i, rt, c[0], c[1], c[2], bg[0], bg[1], bg[2],
                             (r.font.size.pt if r.font.size else -1), r.text[:34]))
