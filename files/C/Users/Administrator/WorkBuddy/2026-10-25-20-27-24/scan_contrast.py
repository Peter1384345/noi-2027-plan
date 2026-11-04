# -*- coding: utf-8 -*-
"""扫描：深色底 + 深色字（对比度不足）的 run，输出清单"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pptx import Presentation
from pptx.oxml.ns import qn

F = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_定稿.pptx"
EMU = 914400


def lum(hexv):
    r, g, b = (int(hexv[i:i + 2], 16) / 255 for i in (0, 2, 4))
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
for si, s in enumerate(list(prs.slides), 1):
    darks = []
    for sh in s.shapes:
        h = fill_hex(sh)
        if h and lum(h) < 0.30 and sh.width and sh.height:
            darks.append((sh.left, sh.top, sh.left + sh.width, sh.top + sh.height, h, sh.name))
    if not darks:
        continue
    for sh in s.shapes:
        if not sh.has_text_frame or not sh.width:
            continue
        cx = sh.left + sh.width / 2
        cy = sh.top + sh.height / 2
        bgs = [(h, nm) for (l, t, r, b, h, nm) in darks
               if l - 20000 <= cx <= r + 20000 and t - 20000 <= cy <= b + 20000]
        if not bgs:
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
                if t and lum(col) < 0.42:
                    print("P%02d  底=%s  字=%s  %-4s  %s" % (
                        si, bgs[0][0], col, round(run.font.size.pt, 1) if run.font.size else "-", t[:36]))
