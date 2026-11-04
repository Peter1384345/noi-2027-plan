# -*- coding: utf-8 -*-
"""大目录 P4：改回「奶油底 + 每章一条白横条」的书页索引版式，
   字体全部调深（深酒红序号 / 近黑标题 / 深灰英文小字）"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.dml.color import RGBColor

F = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_定稿.pptx"
IN = 914400
PAGE = RGBColor(0xF7, 0xF4, 0xEE)
BAND = RGBColor(0xFF, 0xFF, 0xFF)
EDGE = RGBColor(0xD6, 0xC7, 0xB2)
DEEPRED = RGBColor(0x8B, 0x00, 0x00)
INK = RGBColor(0x1A, 0x16, 0x14)
GREY = RGBColor(0x6B, 0x5F, 0x57)
GOLD = RGBColor(0xC8, 0xA2, 0x5A)
SERIF = "仿宋"

prs = Presentation(F)


def rect(s, x, y, w, h, fill, shape=MSO_SHAPE.RECTANGLE):
    shp = s.shapes.add_shape(shape, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    shp.shadow.inherit = False
    if fill is None:
        shp.fill.background()
        shp.line.color.rgb = EDGE
        shp.line.width = Pt(1.1)
    else:
        shp.fill.solid(); shp.fill.fore_color.rgb = fill
        shp.line.fill.background()
    return shp


def text(s, x, y, w, h, txt, size, color, font="微软雅黑", align=PP_ALIGN.LEFT, spc=0, bold=True):
    tb = s.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = 1.0
    r = p.add_run(); r.text = txt
    f = r.font
    f.size = Pt(size); f.bold = bold; f.color.rgb = color; f.name = font
    rPr = r._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
    ea.set('typeface', font)
    if spc:
        rPr.set('spc', str(int(spc)))
    return tb


sl = list(prs.slides)
toc = sl[3]
for sh in list(toc.shapes):
    sh._element.getparent().remove(sh._element)

rect(toc, 0, 0, prs.slide_width, prs.slide_height, PAGE)
rect(toc, 1.00 * IN, 0.62 * IN, 0.44 * IN, 0.014 * IN, DEEPRED)
text(toc, 1.52 * IN, 0.52 * IN, 3.0 * IN, 0.22 * IN, "CONTENTS", 11, DEEPRED,
     font="Georgia", spc=260)
text(toc, 1.20 * IN, 0.86 * IN, 1.85 * IN, 0.78 * IN, "目录", 38, DEEPRED, font=SERIF, spc=110)
text(toc, 3.05 * IN, 1.14 * IN, 4.0 * IN, 0.22 * IN, "FOUR CHAPTERS · ONE STORY", 11, GREY,
     font="Georgia", spc=220)
text(toc, 6.90 * IN, 0.92 * IN, 5.43 * IN, 0.42 * IN, "微光成炬 · 星火自有燎原时", 22, INK,
     align=PP_ALIGN.RIGHT, spc=70)
text(toc, 6.90 * IN, 1.44 * IN, 5.43 * IN, 0.22 * IN, "一 场 关 于 坚 守 的 讲 述", 11, GREY,
     align=PP_ALIGN.RIGHT, spc=120)

ROWS = [
    ("01", "微光 · 韩雅平", "PART 01 · A LIGHT FROM A VILLAGE HOME", "P06—10"),
    ("02", "成炬 · 陈新超", "PART 02 · THE ROAD POSTWOMAN", "P11—16"),
    ("03", "燎原 · 微光成炬", "EPILOGUE · TWO GLIMMERS, ONE TORCH", "P17—18"),
    ("04", "致谢", "CREDITS · ACKNOWLEDGEMENTS", "P19—22"),
]
y0 = 2.42 * IN
bh = 0.88 * IN
gap = 0.14 * IN
for i, (num, title, sub, pg) in enumerate(ROWS):
    y = y0 + i * (bh + gap)
    rect(toc, 1.00 * IN, y, 11.33 * IN, bh, None)          # 白底 + 细边
    text(toc, 1.20 * IN, y + 0.13 * IN, 1.10 * IN, 0.62 * IN, num, 44, DEEPRED,
         font="Georgia")
    rect(toc, 2.42 * IN, y + 0.17 * IN, 0.022 * IN, 0.54 * IN, GOLD)
    text(toc, 2.62 * IN, y + 0.15 * IN, 6.20 * IN, 0.36 * IN, title, 24, INK, spc=40)
    text(toc, 2.62 * IN, y + 0.53 * IN, 8.20 * IN, 0.24 * IN, sub, 11, GREY,
         font="Georgia", spc=90)
    text(toc, 10.60 * IN, y + 0.28 * IN, 1.62 * IN, 0.32 * IN, pg, 13, DEEPRED,
         font="Georgia", align=PP_ALIGN.RIGHT, spc=80)

text(toc, 1.00 * IN, 6.74 * IN, 4.5 * IN, 0.22 * IN, "拾光者小组 · 十五人", 11, GREY, spc=180)
text(toc, 9.40 * IN, 6.74 * IN, 2.93 * IN, 0.22 * IN, "FROM SPARK TO FLAME", 11, GREY,
     font="Georgia", align=PP_ALIGN.RIGHT, spc=280)

prs.save(F)
print("大目录已改为浅底深色索引版，共 %d 页" % len(prs.slides))
