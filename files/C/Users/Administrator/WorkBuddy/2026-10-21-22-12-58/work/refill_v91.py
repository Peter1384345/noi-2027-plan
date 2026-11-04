# -*- coding: utf-8 -*-
"""v9.1：P20 面板内部填实；P21 中段补一条小结带"""
import sys
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')
F = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v9）.pptx"
EMU = 914400
FONT = '微软雅黑'
GOLD, GOLD_L, RED, RED_D = 'C9A227', 'E8C87A', 'C00000', '8E0000'
WARM, WHITE, BODY, SUB = 'F3EDDF', 'FFFFFF', '3A3A38', '8A8378'

prs = Presentation(F)
sl = list(prs.slides)


def IN(v):
    return Emu(int(round(v * EMU)))


def _ea(rPr):
    for tag in ('a:latin', 'a:ea'):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set('typeface', FONT)


def find(slide, needle):
    for sh in slide.shapes:
        if sh.has_text_frame and needle in sh.text_frame.text:
            return sh
    return None


def set_body(sh, text, size):
    txBody = sh.text_frame._txBody
    ps = txBody.findall(qn('a:p'))
    pPr = ps[0].find(qn('a:pPr'))
    pPr = __import__('copy').deepcopy(pPr) if pPr is not None else None
    import copy
    rPr = None
    for p in ps:
        r = p.find(qn('a:r'))
        if r is not None and r.find(qn('a:rPr')) is not None:
            rPr = copy.deepcopy(r.find(qn('a:rPr'))); break
    for p in ps:
        txBody.remove(p)
    p = etree.SubElement(txBody, qn('a:p'))
    if pPr is not None:
        p.append(pPr)
    r = etree.SubElement(p, qn('a:r'))
    if rPr is not None:
        r.append(rPr)
    etree.SubElement(r, qn('a:t')).text = text
    for pp in sh.text_frame.paragraphs:
        pp.line_spacing = 1.8
        for rr in pp.runs:
            rr.font.size = Pt(size)


print('=== P20 面板正文加厚、数据行上提 ===')
s = sl[19]
L = find(s, '陈新超把一条邮路')
if L:
    set_body(L, '陈新超把一条邮路，走成了乡亲们的山——山不挪步，风雨不动。她扛起的不只是四百个包裹，是十个村、两万三千人的日常。抗洪她第一个上，环卫她第一个到。这样的人站在哪里，哪里就是靠山。', 12)
    print('  左栏正文加厚')
R = find(s, '韩雅平用十二年')
if R:
    set_body(R, '韩雅平用十二年，把一滴水穿成了河——水不争先，滴水穿石。她攒下的不只是二十八张奖状，是一间平房里不肯熄灭的灯。那盏灯，照着她走出平房，也照着身后的人。这样的光看着弱，却灭不掉。', 12)
    print('  右栏正文加厚')

# 数据行上提 + 上方加细线
for needle, newy in [('1700 天 · 10 个村', 4.86), ('699 分 · 28 张奖状', 4.86)]:
    sh = find(s, needle)
    if sh:
        sh.top = IN(newy)
        print(f'  {needle[:6]} 上移至 {newy}')

SP = s.shapes
for x in (0.94, 7.28):
    sp = SP.add_shape(MSO_SHAPE.RECTANGLE, IN(x), IN(4.68), IN(5.12), IN(0.012))
    sp.fill.solid(); sp.fill.fore_color.rgb = RGBColor.from_string(GOLD_L if x < 7 else GOLD)
    sp.line.fill.background(); sp.shadow.inherit = False
print('  两条细分隔线已加')

print('\n=== P21 中段补小结带 ===')
s21 = sl[20]
band = SP = s21.shapes.add_shape(MSO_SHAPE.RECTANGLE, IN(0.86), IN(5.02), IN(11.61), IN(0.62))
band.fill.solid(); band.fill.fore_color.rgb = RGBColor.from_string(WARM)
band.line.fill.background(); band.shadow.inherit = False
bar = s21.shapes.add_shape(MSO_SHAPE.RECTANGLE, IN(0.86), IN(5.02), IN(0.05), IN(0.62))
bar.fill.solid(); bar.fill.fore_color.rgb = RGBColor.from_string(RED)
bar.line.fill.background(); bar.shadow.inherit = False

tb = s21.shapes.add_textbox(IN(1.12), IN(5.02), IN(11.2), IN(0.62))
tf = tb.text_frame
tf.word_wrap = True
tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]
r = p.add_run()
r.text = '三个答案，其实是一条路：先站稳，再把小事做到底，最后把光传下去。'
r.font.size = Pt(13); r.font.bold = True; r.font.name = FONT
r.font.color.rgb = RGBColor.from_string(RED_D)
_ea(r._r.get_or_add_rPr())
print('  小结带已加')

prs.save(F)
print('\n已保存')
