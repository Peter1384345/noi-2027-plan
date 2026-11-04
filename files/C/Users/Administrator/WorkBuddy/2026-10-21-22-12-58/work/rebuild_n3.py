# -*- coding: utf-8 -*-
"""清空并重建 N3「铁娘子的一天」，采用行优先阅读顺序"""
import sys
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')
SRC = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v7.1）.pptx"
DST = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v7）.pptx"

RED, GOLD, CREAM = 'C00000', 'C9A227', 'F7F4EE'
WHITE, INK, BODY, SUB = 'FFFFFF', '2A2826', '3A3A38', '8A8378'
FONT = '微软雅黑'
EMU = 914400

prs = Presentation(SRC)
slide = list(prs.slides)[14]


def IN(v):
    return Emu(int(round(v * EMU)))


def _ea(rPr):
    for tag in ('a:latin', 'a:ea'):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set('typeface', FONT)


def add_text(x, y, w, h, text, size=11, color=BODY, bold=False,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=None):
    tb = slide.shapes.add_textbox(IN(x), IN(y), IN(w), IN(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0
    tf.margin_top = 0; tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    if spacing:
        p.line_spacing = spacing
    r = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = bold; r.font.name = FONT
    r.font.color.rgb = RGBColor.from_string(color)
    _ea(r._r.get_or_add_rPr())
    return tb


def add_rect(x, y, w, h, color):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, IN(x), IN(y), IN(w), IN(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = RGBColor.from_string(color)
    sp.line.fill.background(); sp.shadow.inherit = False
    return sp


def _fade(nid, sid, delay=0):
    return (
        f'<p:par><p:cTn id="{nid}" presetID="10" presetClass="entr" presetSubtype="0" '
        f'fill="hold" grpId="0" nodeType="withEffect">'
        f'<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst><p:childTnLst>'
        f'<p:set><p:cBhvr><p:cTn id="{nid+1}" dur="1" fill="hold">'
        f'<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
        f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl>'
        f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
        f'<p:to><p:strVal val="visible"/></p:to></p:set>'
        f'<p:animEffect transition="in" filter="fade"><p:cBhvr>'
        f'<p:cTn id="{nid+2}" dur="550"/>'
        f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl></p:cBhvr></p:animEffect>'
        f'</p:childTnLst></p:cTn></p:par>')


def apply_timing(groups, base=9500):
    nid = base
    blocks = []
    for gi, grp in enumerate(groups):
        inner = []
        for k, sid in enumerate(grp):
            nid += 3
            inner.append(_fade(nid, sid, 0 if k == 0 else 150))
        body = ''.join(inner)
        if gi == 0:
            blocks.append('<p:par><p:cTn fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
                          '<p:childTnLst><p:par><p:cTn fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                          f'<p:childTnLst>{body}</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>')
        else:
            blocks.append('<p:par><p:cTn fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
                          f'<p:childTnLst>{body}</p:childTnLst></p:cTn></p:par>')
    xml = ('<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
           'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
           f'<p:tnLst><p:par><p:cTn id="{base-2}" dur="indefinite" restart="never" nodeType="tmRoot">'
           '<p:childTnLst><p:seq concurrent="1" nextAc="seek">'
           f'<p:cTn id="{base-1}" dur="indefinite" nodeType="mainSeq"><p:childTnLst>{"".join(blocks)}</p:childTnLst></p:cTn>'
           '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
           '</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')
    sld = slide._element
    old = sld.find(qn('p:timing'))
    if old is not None:
        sld.remove(old)
    sld.append(etree.fromstring(xml))


# ---------- 清空旧形状 ----------
spTree = slide.shapes._spTree
removed = 0
for el in list(spTree):
    if el.tag in (qn('p:sp'), qn('p:pic'), qn('p:graphicFrame'), qn('p:grpSp'), qn('p:cxnSp')):
        spTree.remove(el)
        removed += 1
print(f'清除旧形状 {removed} 个')

# ---------- 重建 ----------
G = []
G.append([add_rect(0, 0, 13.333, 7.5, CREAM).shape_id])

k = add_rect(0.56, 0.56, 3.06, 0.31, RED)
kl = add_text(0.56, 0.56, 3.06, 0.31, 'ONE DAY · 一天的时间表', size=11, color=WHITE,
              bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
tt = add_text(0.56, 0.95, 8.4, 0.60, '铁娘子的一天', size=28, color=INK, bold=True)
sb = add_text(0.56, 1.67, 11.4, 0.28, 'A DAY ON THE ROAD · 湖北阳新县枫林镇水源村', size=10, color=SUB)
G.append([k.shape_id, kl.shape_id, tt.shape_id, sb.shape_id])

items = [
    ('05:00', '起床，喂鸡、给家人做早饭'),
    ('06:20', '开上那辆没有空调的二手货车出发'),
    ('07:00', '到县城分拨中心，分拣、扫码、装车'),
    ('10:00', '返回水源村快递点，卸货、分类、上架、通知取件'),
    ('午后', '骑三轮车，给行动不便的老人送货上门'),
    ('傍晚', '收车、对账，一天才算忙完'),
]
XS, YS = (0.56, 6.72), (2.30, 3.48, 4.66)
W, H = 6.05, 1.05
for i, (tm, desc) in enumerate(items):
    x, y = XS[i % 2], YS[i // 2]          # 行优先：先左后右，再换行
    g = []
    g.append(add_rect(x, y, W, H, WHITE).shape_id)
    g.append(add_rect(x, y, 0.05, H, GOLD).shape_id)
    g.append(add_text(x + 0.26, y + 0.24, 1.10, 0.50, tm, size=17, color=GOLD, bold=True).shape_id)
    g.append(add_text(x + 1.42, y + 0.22, 4.35, 0.62, desc, size=10, color=BODY,
                      spacing=1.35, anchor=MSO_ANCHOR.MIDDLE).shape_id)
    G.append(g)
    print(f'  {tm} → ({x:.2f}, {y:.2f})')

q = add_text(0.56, 6.10, 12.22, 0.45, '忙起来顾不上吃饭，头晕了就赶紧剥颗糖含着。', size=11.5, color=SUB)
G.append([q.shape_id])

apply_timing(G)
print(f'动画组 {len(G)} 个')

prs.save(DST)
print(f'已保存：{DST}')
