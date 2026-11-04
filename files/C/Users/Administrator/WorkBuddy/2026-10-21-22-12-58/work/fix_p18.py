# -*- coding: utf-8 -*-
"""P18 照片墙：红块内文字改为白字、去掉重复的来源署名行"""
import sys
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Emu

sys.stdout.reconfigure(encoding='utf-8')
F = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v7）.pptx"
prs = Presentation(F)
s = list(prs.slides)[17]

sp = {x.name: x for x in s.shapes}

# 1) 删掉与左下有重复的来源署名
if 'sp15' in sp:
    el = sp['sp15']._element
    el.getparent().remove(el)
    print('已删除重复署名 sp15')

# 2) 红块内那行改为白字加粗，并在色块内垂直居中
if 'sp14' in sp:
    t = sp['sp14']
    t.top = Emu(int(5.28 * 914400))
    for p in t.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = RGBColor.from_string('FFFFFF')
            r.font.bold = True
            r.font.size = None
    # 显式设字号（12pt），保证在 0.78in 色块内单行
    for p in t.text_frame.paragraphs:
        for r in p.runs:
            from pptx.util import Pt
            r.font.size = Pt(11.5)
    print('sp14 → 白字加粗，已垂直居中')

prs.save(F)
print('已保存')

# 复核
prs2 = Presentation(F)
for x in list(prs2.slides)[17].shapes:
    if x.has_text_frame and x.text_frame.text.strip():
        print(f'  {x.name:<6} y={x.top/914400:5.2f} h={x.height/914400:4.2f}  {x.text_frame.text.strip()[:44]}')
