# -*- coding: utf-8 -*-
"""把 P17「燎原」/ P19「致谢」这两页恢复成「每部分开头那张小目录」的版式，
   并把字体颜色整体调深（深酒红 + 近黑的正文，奶白底）"""
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

BG = RGBColor(0xF7, 0xF4, 0xEE)
DEEPRED = RGBColor(0x8B, 0x00, 0x00)      # 深酒红（标题/眉标/强调）
INK = RGBColor(0x1A, 0x16, 0x14)          # 近黑正文
SUB = RGBColor(0x4A, 0x3F, 0x39)          # 深棕灰副文
GREY = RGBColor(0x6B, 0x5F, 0x57)
LINE = RGBColor(0xD9, 0xC7, 0xB0)
GOLD = RGBColor(0xC8, 0xA2, 0x5A)
SERIF = "仿宋"
L, R = 0.93 * IN, 12.40 * IN
TOT, COLW = R - L, (R - L) / 4
LABELS = ["微光", "成炬", "燎原", "致谢"]

prs = Presentation(F)


def rect(s, x, y, w, h, fill, shape=MSO_SHAPE.RECTANGLE):
    shp = s.shapes.add_shape(shape, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    shp.shadow.inherit = False
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
    p.line_spacing = 1.12
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


def build(s, k, num, over, title, sub, items, quote):
    for sh in list(s.shapes):
        sh._element.getparent().remove(sh._element)

    rect(s, 0, 0, prs.slide_width, prs.slide_height, BG)
    rect(s, 0.93 * IN, 0.96 * IN, 0.075 * IN, 1.80 * IN, DEEPRED)

    text(s, 1.22 * IN, 0.92 * IN, 4.4 * IN, 0.30 * IN, over, 13, DEEPRED,
         font="Georgia", spc=340)
    text(s, 9.85 * IN, 0.42 * IN, 2.55 * IN, 1.95 * IN, num, 118,
         RGBColor(0xF0, 0xE7, 0xD6), font="Georgia", align=PP_ALIGN.RIGHT)
    text(s, 1.20 * IN, 1.14 * IN, 9.4 * IN, 1.02 * IN, title, 44, DEEPRED, font=SERIF, spc=50)
    text(s, 1.24 * IN, 2.24 * IN, 9.4 * IN, 0.34 * IN, sub, 14.5, SUB, spc=40)

    # 四段式章节进度条
    ay = 3.02 * IN
    for i in range(4):
        sx = L + i * COLW
        on = (i == k)
        rect(s, sx, ay, COLW - 0.10 * IN, 0.048 * IN if on else 0.018 * IN,
             DEEPRED if on else RGBColor(0xD9, 0xC9, 0xB6))
        text(s, sx, ay + 0.17 * IN, COLW - 0.10 * IN, 0.28 * IN,
             f"{i+1:02d}  {LABELS[i]}", 12.5, DEEPRED if on else GREY, spc=60)

    n = len(items)
    top, bot = 3.92 * IN, 5.46 * IN
    rowh = min(0.80 * IN, (bot - top) / n)
    y0 = top + ((bot - top) - rowh * n) / 2
    for j, t in enumerate(items):
        y = y0 + j * rowh
        rect(s, 0.93 * IN, y + 0.235 * IN, 0.095 * IN, 0.095 * IN, DEEPRED)
        text(s, 1.24 * IN, y + 0.06 * IN, 9.6 * IN, 0.42 * IN, t, 18, INK, spc=30)
        if j < n - 1:
            rect(s, 0.93 * IN, y + rowh - 0.12 * IN, TOT, 0.007 * IN, LINE)

    rect(s, 0.93 * IN, 5.86 * IN, TOT, 0.009 * IN, GOLD)
    text(s, 1.24 * IN, 6.06 * IN, 11.0 * IN, 0.46 * IN, quote, 25, DEEPRED, font=SERIF, spc=70)

    rect(s, 0.93 * IN, 6.62 * IN, TOT, 0.006 * IN, LINE)
    text(s, 0.93 * IN, 6.72 * IN, 4.5 * IN, 0.22 * IN, "拾光者小组 · 十五人", 10, GREY, spc=200)
    text(s, 8.60 * IN, 6.72 * IN, 3.80 * IN, 0.22 * IN, "FROM SPARK TO FLAME", 10, GREY,
         font="Georgia", align=PP_ALIGN.RIGHT, spc=320)


sl = list(prs.slides)
i_liao = [i for i, s in enumerate(sl)
          if any(sh.has_text_frame and sh.text_frame.text.strip() == "PART 03 · 燎原" for sh in s.shapes)][0]
i_thx = [i for i, s in enumerate(sl)
         if any(sh.has_text_frame and sh.text_frame.text.strip() == "PART 04 · 致谢" for sh in s.shapes)][0]

build(sl[i_liao], 2, "03", "EPILOGUE", "燎原 · 微光成炬", "两张答卷 · 同一种选择 · 约 40 秒",
      ["韩雅平 · 一张书桌，也能撑起一座山",
       "陈新超 · 把邮路走成归途",
       "两束微光 · 同一种选择"],
      "“知识改变命运；而善意，让命运有了另一条路。”")

build(sl[i_thx], 3, "04", "CREDITS", "致谢 · 谢谢聆听", "五组同行 · 十五个人 · 约 20 秒",
      ["特别鸣谢 · 五个小组，十五个人",
       "谢谢聆听 · 星火自有燎原时"],
      "十五人同行，共燃一盏灯。")

prs.save(F)
print("已重建 P%d / P%d，共 %d 页" % (i_liao + 1, i_thx + 1, len(prs.slides)))
