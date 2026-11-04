# -*- coding: utf-8 -*-
"""目录页重构：把 5 条细横线列表改成 5 个与主题对应的分块卡片（3+2 网格）"""
import sys
from copy import deepcopy
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.dml.color import RGBColor

SRC = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时.pptx"
DST = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_目录改版.pptx"

CREAM = RGBColor(0xF3, 0xED, 0xDF)
GOLD = RGBColor(0xE8, 0xC8, 0x7A)

IN = 914400

prs = Presentation(SRC)
s = prs.slides[2]

# ---------- 抽取原设计元素作模板（保持金色渐变序号、雅黑标题、Georgia 英文） ----------
tpl_num = deepcopy(s.shapes[8]._element)
tpl_title = deepcopy(s.shapes[10]._element)
tpl_en = deepcopy(s.shapes[11]._element)

# ---------- 删除旧的 5 组列表元素（id 222–245） ----------
for sh in list(s.shapes):
    if 222 <= sh.shape_id <= 245:
        sh._element.getparent().remove(sh._element)

next_id = [300]


def _unique(el, name="toc"):
    cNvPr = el.find(qn('p:nvSpPr')).find(qn('p:cNvPr'))
    cNvPr.set('id', str(next_id[0]))
    next_id[0] += 1
    cNvPr.set('name', name)


def _place(el, x, y, w, h):
    xfrm = el.find(qn('p:spPr')).find(qn('a:xfrm'))
    off, ext = xfrm.find(qn('a:off')), xfrm.find(qn('a:ext'))
    off.set('x', str(int(x)))
    off.set('y', str(int(y)))
    ext.set('cx', str(int(w)))
    ext.set('cy', str(int(h)))


def _alpha(srgb, pct):
    a = srgb.makeelement(qn('a:alpha'), {'val': str(int(pct * 1000))})
    srgb.append(a)


def from_tpl(tpl, x, y, w, h, text, sz=None, spc=None):
    el = deepcopy(tpl)
    _unique(el)
    _place(el, x, y, w, h)
    txBody = el.find(qn('p:txBody'))
    ps = txBody.findall(qn('a:p'))
    p0 = ps[0]
    runs = p0.findall(qn('a:r'))
    keep = runs[0]
    for r in runs[1:]:
        p0.remove(r)
    keep.find(qn('a:t')).text = text
    for tag in ('a:rPr', 'a:endParaRPr'):
        rPr = keep.find(qn(tag)) if tag == 'a:rPr' else p0.find(qn(tag))
        if rPr is None:
            continue
        if sz:
            rPr.set('sz', str(int(sz * 100)))
        if spc is not None:
            rPr.set('spc', str(int(spc * 100)))
    for p in ps[1:]:
        txBody.remove(p)
    s.shapes._spTree.append(el)
    return el


def card(x, y, w, h):
    shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    shp.shadow.inherit = False
    shp.fill.solid()
    shp.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    sf = shp._element.spPr.find(qn('a:solidFill'))
    _alpha(sf.find(qn('a:srgbClr')), 7)
    shp.line.color.rgb = CREAM
    shp.line.width = Pt(0.75)
    ln = shp._element.spPr.find(qn('a:ln'))
    _alpha(ln.find(qn('a:solidFill')).find(qn('a:srgbClr')), 30)
    # 去掉 autoshape 自带的多余段落样式
    return shp


def accent(x, y, w=1.05 * IN, h=0.022 * IN):
    shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    shp.shadow.inherit = False
    shp.fill.solid()
    shp.fill.fore_color.rgb = GOLD
    sf = shp._element.spPr.find(qn('a:solidFill'))
    _alpha(sf.find(qn('a:srgbClr')), 62)
    shp.line.fill.background()
    return shp


def text(x, y, w, h, content, size, color=CREAM, alpha=100, font="微软雅黑",
         align=PP_ALIGN.LEFT, lnspc=145, spc=0, bold=False):
    tb = s.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    lines = content if isinstance(content, list) else [content]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = lnspc / 100.0
        r = p.add_run()
        r.text = line
        f = r.font
        f.size = Pt(size)
        f.bold = bold
        f.color.rgb = color
        f.name = font
        rPr = r._r.get_or_add_rPr()
        # 中文字体
        ea = rPr.find(qn('a:ea'))
        if ea is None:
            ea = rPr.makeelement(qn('a:ea'), {})
            rPr.append(ea)
        ea.set('typeface', font)
        if spc:
            rPr.set('spc', str(int(spc * 100)))
        if alpha < 100:
            sf = rPr.find(qn('a:solidFill'))
            _alpha(sf.find(qn('a:srgbClr')), alpha)
    return tb


# ---------- 版面 ----------
L0, W_ALL = 0.93 * IN, 11.47 * IN
GAP = 0.22 * IN
R1_Y, R1_H = 2.04 * IN, 2.32 * IN
R2_Y, R2_H = 4.56 * IN, 2.32 * IN
CW3 = (W_ALL - 2 * GAP) / 3
CW2 = (W_ALL - GAP) / 2

BLOCKS = [
    dict(x=L0, y=R1_Y, w=CW3, h=R1_H, num="01", page="04",
         title="序章 · 团队分工",
         en="PROLOGUE · OUR TEAM OF FIFTEEN",
         items=["拾光者小组 · 十五人",
                "五组分工：采写 / 设计 / 素材 / 审校 / 统筹",
                "从采写到合成的讲述脉络"]),
    dict(x=L0 + CW3 + GAP, y=R1_Y, w=CW3, h=R1_H, num="02", page="05—09",
         title="微光 · 韩雅平",
         en="PART 01 · A LIGHT FROM A VILLAGE HOME",
         items=["寒门筑梦 · 699 分圆梦清华",
                "三间平房，墙上 28 张奖状",
                "顾妈妈：12 年资助、365 人次",
                "视频 ·《小莉帮忙》采访"]),
    dict(x=L0 + 2 * (CW3 + GAP), y=R1_Y, w=CW3, h=R1_H, num="03", page="10—15",
         title="成炬 · 陈新超",
         en="PART 02 · THE ROAD POSTWOMAN",
         items=["高山邮路 · 一个人的服务站",
                "1700 天 · 120 公里 · 10 个村",
                "便民车 / 代买菜 / 抗洪守堤",
                "视频 ·《新时代的我们》",
                "党员风采 · 机动页"]),
    dict(x=L0, y=R2_Y, w=CW2, h=R2_H, num="04", page="16",
         title="燎原 · 微光成炬",
         en="EPILOGUE · TWO GLIMMERS, ONE TORCH",
         items=["一张书桌，也能撑起一座山。",
                "把邮路走成归途，把温暖送进每一户人家。",
                "两束微光，同一种选择 —— 星火自有燎原时。"]),
    dict(x=L0 + CW2 + GAP, y=R2_Y, w=CW2, h=R2_H, num="05", page="17—19",
         title="致谢 · 谢谢聆听",
         en="CREDITS · ACKNOWLEDGEMENTS",
         items=["特别鸣谢：文案采编 / 视觉设计 / 素材与主讲 / 数据与审校 / 合成与统筹",
                "十五人同行，共燃一盏灯。"]),
]

for b in BLOCKS:
    x, y, w, h = b["x"], b["y"], b["w"], b["h"]
    card(x, y, w, h)
    accent(x + 0.30 * IN, y)                      # 顶部金色短线
    from_tpl(tpl_num, x + 0.28 * IN, y + 0.24 * IN, 0.62 * IN, 0.50 * IN, b["num"], sz=25)
    from_tpl(tpl_title, x + 0.99 * IN, y + 0.31 * IN, w - 1.28 * IN, 0.34 * IN, b["title"], sz=15, spc=150)
    from_tpl(tpl_en, x + 0.99 * IN, y + 0.70 * IN, w - 1.28 * IN, 0.20 * IN, b["en"], sz=7, spc=150)
    text(x + w - 0.66 * IN, y + 0.30 * IN, 0.52 * IN, 0.18 * IN, "P" + b["page"], 7,
         color=GOLD, alpha=58, font="Georgia", align=PP_ALIGN.RIGHT, spc=100)
    items = ["· " + it for it in b["items"]]
    text(x + 0.60 * IN, y + 1.00 * IN, w - 0.82 * IN, h - 1.18 * IN, items, 8.5,
         color=CREAM, alpha=80, font="微软雅黑", lnspc=150, spc=20)

# 目录页眉下方补一句主线说明
text(1.00 * IN, 1.60 * IN, 8.6 * IN, 0.24 * IN,
     "从一间平房到一条邮路 —— 五个部分，拼成同一个故事", 10,
     color=CREAM, alpha=52, font="微软雅黑", spc=30)

prs.save(DST)
print("saved:", DST)

# ---------- 复核 ----------
p2 = Presentation(DST)
print("slides:", len(p2.slides))
s2 = p2.slides[2]
for sh in s2.shapes:
    print(f"{sh.name:14s} L={sh.left/IN:6.2f} T={sh.top/IN:6.2f} W={sh.width/IN:6.2f} H={sh.height/IN:6.2f}"
          + ("  | " + sh.text_frame.text.replace("\n", " / ")[:60] if sh.has_text_frame and sh.text_frame.text.strip() else ""))
