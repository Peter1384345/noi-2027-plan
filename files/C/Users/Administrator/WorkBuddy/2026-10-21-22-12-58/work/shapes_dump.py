# -*- coding: utf-8 -*-
"""导出每页形状骨架：name / 位置尺寸 / 填充 / 文字"""
import sys
from pptx import Presentation
from pptx.util import Emu

sys.stdout.reconfigure(encoding='utf-8')
SRC = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v6）.pptx"
prs = Presentation(SRC)
print("画布 EMU:", prs.slide_width, "x", prs.slide_height,
      "=", prs.slide_width / 914400, "x", prs.slide_height / 914400, "英寸")


def fill_of(sh):
    try:
        f = sh.fill
        if f.type is not None and f.type == 1:  # solid
            return str(f.fore_color.rgb)
    except Exception:
        pass
    try:
        xml = sh._element.xml
        import re
        m = re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', xml)
        if m:
            return ",".join("#" + x for x in m[:3])
    except Exception:
        pass
    return "-"


for i, slide in enumerate(prs.slides, 1):
    print("\n" + "=" * 78)
    print(f"P{i:02d}  形状数={len(slide.shapes)}")
    print("=" * 78)
    for sh in slide.shapes:
        try:
            x, y = sh.left or 0, sh.top or 0
            w, h = sh.width or 0, sh.height or 0
            pos = f"({x/914400:5.2f},{y/914400:5.2f}) {w/914400:5.2f}x{h/914400:5.2f}"
        except Exception:
            pos = "?"
        txt = ""
        if sh.has_text_frame:
            txt = sh.text_frame.text.replace("\n", "⏎")[:46]
        print(f"  [{sh.shape_type}] {sh.name[:26]:<26} {pos}  {fill_of(sh)[:22]:<22} {txt}")
