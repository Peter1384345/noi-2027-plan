# -*- coding: utf-8 -*-
"""修 P05 团队分工页的对比度：色条上的组名/姓名/职责原为「红底红字/灰字」，改为浅色"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Pt

F = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_定稿.pptx"
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT = RGBColor(0xFF, 0xE4, 0xD8)
DARKR = RGBColor(0x6B, 0x10, 0x10)
MIDR = RGBColor(0x86, 0x24, 0x1C)

prs = Presentation(F)
s = [x for x in prs.slides if any(sh.has_text_frame and sh.text_frame.text.strip()=="OUR TEAM · 团队分工" for sh in x.shapes)][0]
n = 0
for sh in s.shapes:
    if not sh.has_text_frame:
        continue
    L = sh.left / 914400
    T = sh.top / 914400
    W = sh.width / 914400
    if L < 4.80 or T < 1.60:
        continue
    gold_row = T >= 5.30
    duty = W > 4.0
    for p in sh.text_frame.paragraphs:
        for r in p.runs:
            if not r.text.strip():
                continue
            if gold_row:
                r.font.color.rgb = MIDR if duty else DARKR
            else:
                r.font.color.rgb = LIGHT if duty else WHITE
            r.font.bold = True
            n += 1
print("改色 run 数:", n)
prs.save(F)
