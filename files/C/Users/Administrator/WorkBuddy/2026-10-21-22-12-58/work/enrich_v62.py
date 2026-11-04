# -*- coding: utf-8 -*-
"""v6.2 内容定稿：撤两处重复，补三处独有实证细节"""
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

F = '../微光成炬-星火自有燎原时（终版·v6）.pptx'
prs = Presentation(F)
GOLD = RGBColor(0xC9, 0xA2, 0x27)
CREAM = RGBColor(0xF7, 0xF4, 0xEE)
MUTED = RGBColor(0x9A, 0x92, 0x86)

def drop_shape(sh):
    sh._element.getparent().remove(sh._element)

def add_text(slide, x, y, w, h, lines):
    tb = slide.shapes.add_textbox(Emu(x*9525), Emu(y*9525), Emu(w*9525), Emu(h*9525))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, (txt, fname, size, bold, color) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = p.add_run(); r.text = txt
        r.font.name = fname; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color
        rPr = r._r.get_or_add_rPr()
        rPr.append(rPr.makeelement(qn('a:ea'), {'typeface': fname}))
    return tb

# 1) 撤：P07 引语（与 P08 捷报页卡片重复）
n = 0
for sh in list(prs.slides[6].shapes):
    if sh.has_text_frame and '不和别人比吃穿' in sh.text_frame.text and sh.name.startswith('TextBox'):
        drop_shape(sh); n += 1
print('P07 移除重复引语:', n)

# 2) 撤：P11 数据带（与 P12 人物页数据行重复）
n = 0
for sh in list(prs.slides[10].shapes):
    if sh.has_text_frame and '120 公里 / 天' in sh.text_frame.text:
        drop_shape(sh); n += 1
print('P11 移除重复数据带:', n)

# 3) 补：P13 服务站 · 代买菜卡加「腊鱼腊肉寄子女」
n = 0
for sh in prs.slides[12].shapes:
    if sh.has_text_frame and '菜比昨天的新鲜' in sh.text_frame.text:
        p0 = sh.text_frame.paragraphs[-1]
        r0 = p0.runs[0]
        r = p0.add_run(); r.text = '她还常帮留守老人，把腊鱼腊肉寄给城里打工的子女。'
        r.font.name = r0.font.name; r.font.size = r0.font.size; r.font.bold = False
        try: r.font.color.rgb = r0.font.color.rgb
        except Exception: pass
        r._r.get_or_add_rPr().append(r._r.makeelement(qn('a:ea'), {'typeface': r0.font.name or '微软雅黑'}))
        n += 1
print('P13 腊鱼腊肉:', n)

# 4) 补：P14 1700+ 页 · 快递点成驿站
add_text(prs.slides[13], 84, 566, 470, 22, [
    ('快递点成了乡亲们的休闲驿站，还有村民自发前来打扫卫生', '微软雅黑', 12.5, False, MUTED),
])
print('P14 驿站细节 added')

# 5) 补：P02 副封面 · 一句定位副题
s2 = prs.slides[1]
mk = None
for sh in s2.shapes:
    if sh.has_text_frame and '拾光者' in sh.text_frame.text:
        mk = sh
if mk is not None:
    y = mk.top // 9525 + mk.height // 9525 + 10
    add_text(s2, mk.left // 9525, y, max(mk.width // 9525, 360), 24, [
        ('一堂关于微光、涓流与高山的汇报课', '仿宋', 15, False, GOLD),
    ])
    print('P02 副题 added at y', y)
else:
    print('P02 制作者 shape not found')

prs.save(F)
print('saved')
