# -*- coding: utf-8 -*-
"""目录页 v5：① 补出高对比度大标题  ② 每块只留「序号 + 主题名 + 一句总结小标题 + 页码」"""
from copy import deepcopy
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.dml.color import RGBColor

F = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_新版本.pptx"
IN = 914400
CREAM = RGBColor(0xF3, 0xED, 0xDF)
GOLD = RGBColor(0xE8, 0xC8, 0x7A)
SUB = RGBColor(0xF0, 0xC8, 0xBC)
CARD = RGBColor(0xA3, 0x0E, 0x0E)

prs = Presentation(F)
toc = list(prs.slides)[3]

# ---------- 取模板（金色渐变序号 / 雅黑标题） ----------
tpl = {}
for sh in toc.shapes:
    if sh.name.startswith("toc") and sh.has_text_frame:
        t = sh.text_frame.text.strip()
        if t == "01":
            tpl["num"] = sh._element
        elif t.startswith("序章"):
            tpl["title"] = sh._element
assert "num" in tpl and "title" in tpl

# ---------- 删掉上一版的卡片与文字 ----------
for sh in list(toc.shapes):
    if sh.name.startswith(("toc", "Rectangle", "TextBox")):
        sh._element.getparent().remove(sh._element)

# ---------- 页眉：补明确的大标题颜色 + 主题大标题 ----------
def recolor(name, color):
    for sh in toc.shapes:
        if sh.name == name and sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    r.font.color.rgb = color
                ep = p._p.find(qn('a:endParaRPr'))
                if ep is not None:
                    sf = ep.find(qn('a:solidFill'))
                    if sf is None:
                        sf = ep.makeelement(qn('a:solidFill'), {})
                        ep.insert(0, sf)
                    sf.clear()
                    c = sf.makeelement(qn('a:srgbClr'), {'val': str(color)})
                    sf.append(c)

recolor("文本框 122", GOLD)     # CONTENTS
recolor("文本框 125", CREAM)    # 目录（大标题）
recolor("文本框 126", GOLD)     # FIVE CHAPTERS · ONE STORY

next_id = [700]


def from_tpl(tpl_el, x, y, w, h, text, sz=None, spc=None):
    el = deepcopy(tpl_el)
    c = el.find(qn('p:nvSpPr')).find(qn('p:cNvPr'))
    c.set('id', str(next_id[0])); next_id[0] += 1
    c.set('name', 'toc5')
    xfrm = el.find(qn('p:spPr')).find(qn('a:xfrm'))
    off, ext = xfrm.find(qn('a:off')), xfrm.find(qn('a:ext'))
    off.set('x', str(int(x))); off.set('y', str(int(y)))
    ext.set('cx', str(int(w))); ext.set('cy', str(int(h)))
    tx = el.find(qn('p:txBody'))
    ps = tx.findall(qn('a:p'))
    p0 = ps[0]
    runs = p0.findall(qn('a:r'))
    keep = runs[0]
    for r in runs[1:]:
        p0.remove(r)
    keep.find(qn('a:t')).text = text
    for el2 in (keep.find(qn('a:rPr')), p0.find(qn('a:endParaRPr'))):
        if el2 is None:
            continue
        if sz:
            el2.set('sz', str(int(sz * 100)))
        if spc is not None:
            el2.set('spc', str(int(spc)))
    for p in ps[1:]:
        tx.remove(p)
    toc.shapes._spTree.append(el)


def rect(x, y, w, h, fill, line=None, lw=1.0):
    shp = toc.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    shp.shadow.inherit = False
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(lw)
    return shp


def text(x, y, w, h, content, size, color=CREAM, font="微软雅黑",
         align=PP_ALIGN.LEFT, spc=0, lnspc=120):
    tb = toc.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
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
        f.color.rgb = color
        f.name = font
        rPr = r._r.get_or_add_rPr()
        ea = rPr.find(qn('a:ea'))
        if ea is None:
            ea = rPr.makeelement(qn('a:ea'), {})
            rPr.append(ea)
        ea.set('typeface', font)
        if spc:
            rPr.set('spc', str(int(spc)))
    return tb


# 主题大标题（页眉右侧）
text(6.05 * IN, 0.96 * IN, 6.3 * IN, 0.56 * IN, "微光成炬 · 星火自有燎原时", 23,
     color=CREAM, font="微软雅黑", spc=60)

# ---------- 五块 ----------
L0, W_ALL = 0.93 * IN, 11.47 * IN
GAP = 0.22 * IN
R1_Y, R1_H = 2.05 * IN, 2.35 * IN
R2_Y, R2_H = 4.65 * IN, 2.35 * IN
CW3 = (W_ALL - 2 * GAP) / 3
CW2 = (W_ALL - GAP) / 2

BLOCKS = [
    dict(x=L0, y=R1_Y, w=CW3, h=R1_H, num="01", title="序章 · 团队分工",
         sub="十五人，五个小组", page="P05"),
    dict(x=L0 + CW3 + GAP, y=R1_Y, w=CW3, h=R1_H, num="02", title="微光 · 韩雅平",
         sub="寒门筑梦 · 699 分圆梦清华", page="P06—10"),
    dict(x=L0 + 2 * (CW3 + GAP), y=R1_Y, w=CW3, h=R1_H, num="03", title="成炬 · 陈新超",
         sub="高山邮路 · 1700 个日夜", page="P11—16"),
    dict(x=L0, y=R2_Y, w=CW2, h=R2_H, num="04", title="燎原 · 微光成炬",
         sub="两束微光，同一种选择", page="P17"),
    dict(x=L0 + CW2 + GAP, y=R2_Y, w=CW2, h=R2_H, num="05", title="致谢 · 谢谢聆听",
         sub="十五人同行，共燃一盏灯", page="P18—20"),
]

for b in BLOCKS:
    x, y, w, h = b["x"], b["y"], b["w"], b["h"]
    rect(x, y, w, h, CARD, line=GOLD, lw=1.0)
    rect(x, y, w, 0.026 * IN, GOLD)
    from_tpl(tpl["num"], x + 0.28 * IN, y + 0.80 * IN, 0.75 * IN, 0.78 * IN, b["num"], sz=46)
    from_tpl(tpl["title"], x + 1.16 * IN, y + 0.84 * IN, w - 1.46 * IN, 0.40 * IN, b["title"], sz=20, spc=150)
    text(x + 1.16 * IN, y + 1.26 * IN, w - 1.46 * IN, 0.28 * IN, b["sub"], 12,
         color=SUB, font="微软雅黑", spc=60)
    text(x + w - 0.86 * IN, y + h - 0.52 * IN, 0.62 * IN, 0.20 * IN, b["page"], 7.5,
         color=GOLD, font="Georgia", align=PP_ALIGN.RIGHT, spc=100)

prs.save(F)
print("saved")

# ---------- 复核 ----------
p2 = Presentation(F)
sl = list(p2.slides)
print("页数:", len(sl))
t = sl[3]
for sh in t.shapes:
    if sh.has_text_frame and sh.text_frame.text.strip():
        print(f"  {str(sh.font if False else ''):1s}{sh.text_frame.text.strip()[:34]:36s} "
              f"x={sh.left/IN:5.2f} y={sh.top/IN:5.2f} w={sh.width/IN:5.2f} h={sh.height/IN:5.2f}")
