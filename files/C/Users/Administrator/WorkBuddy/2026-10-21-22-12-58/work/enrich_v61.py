# -*- coding: utf-8 -*-
"""v6.1 内容丰满升级：5 页有据加料，版式与原动画零改动"""
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR
from pptx.oxml.ns import qn
import copy

F = '../微光成炬-星火自有燎原时（终版·v6）.pptx'
prs = Presentation(F)
GOLD = RGBColor(0xC9, 0xA2, 0x27)
GOLD_L = RGBColor(0xE8, 0xC8, 0x7A)
DARK = RGBColor(0x2A, 0x28, 0x25)
CREAM = RGBColor(0xF7, 0xF4, 0xEE)

def add_text(slide, x, y, w, h, lines, align_center=False):
    """lines: [(text, font, size, bold, color, italic)]"""
    tb = slide.shapes.add_textbox(Emu(x*9525), Emu(y*9525), Emu(w*9525), Emu(h*9525))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, (txt, fname, size, bold, color, italic) in enumerate(lines):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = 2 if align_center else None
        r = para.add_run(); r.text = txt
        r.font.name = fname; r.font.size = Pt(size); r.font.bold = bold
        r.font.color.rgb = color; r.font.italic = italic
        rPr = r._r.get_or_add_rPr()
        ea = rPr.makeelement(qn('a:ea'), {'typeface': fname}); rPr.append(ea)
    return tb

def get_run_color(slide, shape_name):
    for sh in slide.shapes:
        if sh.name == shape_name and sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    try: return r.font.color.rgb
                    except Exception: pass
    return None

def add_caption(slide, x, y, w, text):
    """照片底部信息条：55% 黑底 + 米白小字"""
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(x*9525), Emu(y*9525), Emu(w*9525), Emu(24*9525))
    bar.fill.solid(); bar.fill.fore_color.rgb = RGBColor(0, 0, 0)
    bar.line.fill.background()
    bar.shadow.inherit = False
    srgb = bar.fill.fore_color._xFill.find(qn('a:srgbClr'))
    a = srgb.makeelement(qn('a:alpha'), {'val': '55000'}); srgb.append(a)
    tf = bar.text_frame
    tf.margin_left = Emu(6*9525); tf.margin_top = 0; tf.margin_bottom = 0
    tf.margin_right = Emu(4*9525)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p0 = tf.paragraphs[0]
    r = p0.add_run(); r.text = text
    r.font.name = '微软雅黑'; r.font.size = Pt(9.5); r.font.bold = False
    r.font.color.rgb = CREAM
    rPr = r._r.get_or_add_rPr()
    rPr.append(rPr.makeelement(qn('a:ea'), {'typeface': '微软雅黑'}))
    return bar

# ---------- P07 · 699 页：补一句她的原话 ----------
s = prs.slides[6]
add_text(s, 84, 585, 500, 26, [
    ('「不和别人比吃穿，学生就该比学习。」', '仿宋', 16, True, GOLD, False),
    ('—— 韩雅平受访原话', '微软雅黑', 10.5, False, RGBColor(0x8A, 0x82, 0x76), False),
])
print('P07 quote added')

# ---------- P11 · 扉页02：补一行数据带 ----------
s = prs.slides[10]
c = get_run_color(s, '文本框 252') or GOLD_L
add_text(s, 40, 488, 420, 22, [
    ('120 公里 / 天  ·  近 400 件 / 天  ·  10 个村  ·  2.3 万村民', '微软雅黑', 12.5, True, c, False),
])
print('P11 stats added, color', c)

# ---------- P13 · 服务站：便民车卡补零钱盒细节 ----------
s = prs.slides[12]
done = False
for sh in s.shapes:
    if sh.has_text_frame and '教老人用手机缴费' in sh.text_frame.text:
        p0 = sh.text_frame.paragraphs[-1]
        r = p0.add_run()
        r.text = '车上常年备着一盒一元硬币，专供进城乡亲搭公交。'
        r0 = p0.runs[0]
        r.font.name = r0.font.name; r.font.size = r0.font.size
        try: r.font.color.rgb = r0.font.color.rgb
        except Exception: pass
        r.font.bold = False
        rPr = r._r.get_or_add_rPr()
        rPr.append(rPr.makeelement(qn('a:ea'), {'typeface': r0.font.name or '微软雅黑'}))
        done = True
print('P13 zero-coins detail:', done)

# ---------- P14 · 1700+ 页：补「绕赤道 5 圈」 ----------
s = prs.slides[13]
add_text(s, 84, 532, 460, 24, [
    ('邮车五年跑了 20 多万公里 —— 相当于沿赤道绕地球 5 圈', '微软雅黑', 13, True, GOLD, False),
])
print('P14 equator stat added')

# ---------- P15 · 影像页：四张照片各加信息条 ----------
s = prs.slides[14]
caps = ['① 清晨 6:20，准时驾车出发', '② 50 公斤化肥，咬牙扛上肩',
        '③ 帮老人核对单号、送货上门', '④ 满载而归，顺路帮村里捎菜']
pos = [(53, 325), (390, 325), (53, 525), (390, 525)]  # y = photo_top+192-24
for (x, y), t in zip(pos, caps):
    add_caption(s, x, y, 329, t)
print('P15 captions added')

prs.save(F)
print('saved')
