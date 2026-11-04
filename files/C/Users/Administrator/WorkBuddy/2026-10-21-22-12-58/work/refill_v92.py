# -*- coding: utf-8 -*-
"""v9.2：P18 补第三条图注，红带下移，右侧列铺满"""
import sys
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')
F = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v9）.pptx"
EMU = 914400
FONT = '微软雅黑'
GOLD, BODY = 'C9A227', '3A3A38'

prs = Presentation(F)
s = list(prs.slides)[17]

# 红带下移
for sh in s.shapes:
    if sh.has_text_frame and '记者跟随陈新超' in sh.text_frame.text:
        sh.top = Emu(int(6.02 * EMU)); print('  红带下移至 6.02')
    elif sh.name == 'sp12' or (sh.shape_type == 1 and abs(sh.width / EMU - 4.72) < 0.05 and abs(sh.top / EMU - 5.08) < 0.05):
        sh.top = Emu(int(6.02 * EMU)); print('  红带底板下移')

# 第三枚圆点 + 图注
dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Emu(int(8.18 * EMU)), Emu(int(5.17 * EMU)),
                         Emu(int(0.10 * EMU)), Emu(int(0.10 * EMU)))
dot.fill.solid(); dot.fill.fore_color.rgb = RGBColor.from_string(GOLD)
dot.line.fill.background(); dot.shadow.inherit = False

tb = s.shapes.add_textbox(Emu(int(8.39 * EMU)), Emu(int(5.05 * EMU)),
                          Emu(int(4.58 * EMU)), Emu(int(0.78 * EMU)))
tf = tb.text_frame
tf.word_wrap = True
tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
p = tf.paragraphs[0]
r = p.add_run()
r.text = '四张照片，是记者跟拍一天里挑出的四个时刻：清晨出发、分拣装车、核对单号、满载而归。'
r.font.size = Pt(9.5); r.font.name = FONT
r.font.color.rgb = RGBColor.from_string(BODY)
rPr = r._r.get_or_add_rPr()
for tag in ('a:latin', 'a:ea'):
    el = rPr.find(qn(tag))
    if el is None:
        el = etree.SubElement(rPr, qn(tag))
    el.set('typeface', FONT)
print('  第三条图注已加')

prs.save(F)
print('已保存')
