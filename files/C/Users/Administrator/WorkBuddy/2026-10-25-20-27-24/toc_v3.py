# -*- coding: utf-8 -*-
"""① 片头移到第 1 页；② 目录页改为实色卡片重做（不依赖透明度，预览/放映不走样）"""
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
CARD = RGBColor(0xA3, 0x0E, 0x0E)   # 实色深红卡片

prs = Presentation(F)
slides = list(prs.slides)

# ---------- ① 片头页（当前第 3 页）移到最前 ----------
sldIdLst = prs.slides._sldIdLst
ids = list(sldIdLst)
movie_idx = next(i for i, sl in enumerate(list(prs.slides)) if any(sh.shape_type == 16 for sh in sl.shapes))
if movie_idx != 0:
    node = ids[movie_idx]
    sldIdLst.remove(node)
    sldIdLst.insert(0, node)
print("片头位置:", movie_idx, "-> 0")

# ---------- ② 重做目录页（现在是第 4 页） ----------
toc = list(prs.slides)[3]

# 先从现有 toc 元素里取模板（保持金色渐变序号/雅黑标题/Georgia 英文的原始格式）
tpl = {}
for sh in toc.shapes:
    if sh.name.startswith("toc") and sh.has_text_frame:
        t = sh.text_frame.text.strip()
        if t == "01":
            tpl["num"] = sh._element
        elif t.startswith("序章"):
            tpl["title"] = sh._element
        elif t.startswith("PROLOGUE"):
            tpl["en"] = sh._element
assert len(tpl) == 3, tpl.keys()

# 删除上一版我加的所有形状（原版形状都是中文名，不会误删）
for sh in list(toc.shapes):
    if sh.name.startswith(("toc", "Rectangle", "TextBox")):
        sh._element.getparent().remove(sh._element)

next_id = [500]


def from_tpl(tpl_el, x, y, w, h, text, sz=None, spc=None):
    el = deepcopy(tpl_el)
    c = el.find(qn('p:nvSpPr')).find(qn('p:cNvPr'))
    c.set('id', str(next_id[0])); next_id[0] += 1
    c.set('name', 'toc2')
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
    for tag, el2 in (('a:rPr', keep.find(qn('a:rPr'))), ('a:endParaRPr', p0.find(qn('a:endParaRPr')))):
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
         align=PP_ALIGN.LEFT, lnspc=145, spc=0, bold=False):
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
        f.bold = bold
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


L0, W_ALL = 0.93 * IN, 11.47 * IN
GAP = 0.22 * IN
R1_Y, R1_H = 1.98 * IN, 2.40 * IN
R2_Y, R2_H = 4.56 * IN, 2.40 * IN
CW3 = (W_ALL - 2 * GAP) / 3
CW2 = (W_ALL - GAP) / 2

BLOCKS = [
    dict(x=L0, y=R1_Y, w=CW3, h=R1_H, num="01", page="P05",
         title="序章 · 团队分工", en="PROLOGUE · TEAM OF 15",
         items=["拾光者小组 · 十五人",
                "五组分工：采写 / 设计 / 素材 / 审校 / 统筹",
                "从采写到合成的讲述脉络",
                "全片 10 分钟 · 3 段人物视频"]),
    dict(x=L0 + CW3 + GAP, y=R1_Y, w=CW3, h=R1_H, num="02", page="P06—10",
         title="微光 · 韩雅平", en="PART 01 · A VILLAGE LIGHT",
         items=["寒门筑梦 · 699 分圆梦清华",
                "三间平房，墙上 28 张奖状",
                "顾妈妈：12 年资助、365 人次",
                "视频 ·《小莉帮忙》采访"]),
    dict(x=L0 + 2 * (CW3 + GAP), y=R1_Y, w=CW3, h=R1_H, num="03", page="P11—16",
         title="成炬 · 陈新超", en="PART 02 · THE ROAD POSTWOMAN",
         items=["高山邮路 · 一个人的服务站",
                "1700 天 · 120 公里 · 10 个村",
                "便民车 / 代买菜 / 抗洪守堤",
                "视频 ·《新时代的我们》",
                "党员风采 · 机动页"]),
    dict(x=L0, y=R2_Y, w=CW2, h=R2_H, num="04", page="P17",
         title="燎原 · 微光成炬", en="EPILOGUE · TWO GLIMMERS",
         items=["寒门与邮路，两条路，同一种倔强",
                "一张书桌，也能撑起一座山。",
                "把邮路走成归途，把温暖送进每一户人家。",
                "两束微光，同一种选择 —— 星火自有燎原时。"]),
    dict(x=L0 + CW2 + GAP, y=R2_Y, w=CW2, h=R2_H, num="05", page="P18—20",
         title="致谢 · 谢谢聆听", en="CREDITS · ACKNOWLEDGEMENTS",
         items=["特别鸣谢：文案采编 / 视觉设计 / 素材与主讲 / 数据与审校 / 合成与统筹",
                "感谢每一位讲述者：韩雅平 · 顾虹 · 陈新超",
                "十五人同行，共燃一盏灯。"]),
]

for b in BLOCKS:
    x, y, w, h = b["x"], b["y"], b["w"], b["h"]
    rect(x, y, w, h, CARD, line=GOLD, lw=1.0)          # 实色卡片 + 金边
    rect(x, y, w, 0.026 * IN, GOLD)                     # 顶部金条
    from_tpl(tpl["num"], x + 0.27 * IN, y + 0.16 * IN, 0.70 * IN, 0.56 * IN, b["num"], sz=30)
    from_tpl(tpl["title"], x + 1.04 * IN, y + 0.24 * IN, w - 1.36 * IN, 0.36 * IN, b["title"], sz=16, spc=150)
    from_tpl(tpl["en"], x + 1.04 * IN, y + 0.65 * IN, w - 1.36 * IN, 0.20 * IN, b["en"], sz=7.5, spc=100)
    rect(x + 0.30 * IN, y + 0.92 * IN, w - 0.60 * IN, 0.011 * IN, GOLD)   # 内部分隔细线
    text(x + w - 0.80 * IN, y + 0.26 * IN, 0.64 * IN, 0.18 * IN, b["page"], 7.5,
         color=GOLD, font="Georgia", align=PP_ALIGN.RIGHT, spc=100)
    items = ["· " + it for it in b["items"]]
    text(x + 0.32 * IN, y + 1.02 * IN, w - 0.64 * IN, h - 1.20 * IN, items, 10,
         color=CREAM, font="微软雅黑", lnspc=138, spc=50)

# 页眉下的一句话说明（实色，不用透明度）
text(1.00 * IN, 1.58 * IN, 9.0 * IN, 0.26 * IN,
     "从一间平房到一条邮路 —— 五个部分，拼成同一个故事", 10,
     color=RGBColor(0xF2, 0xCF, 0xC5), font="微软雅黑", spc=30)

prs.save(F)
print("saved", F)

# ---------- 复核 ----------
p2 = Presentation(F)
sl = list(p2.slides)
print("总页数:", len(sl))
for i, s in enumerate(sl[:6], 1):
    mv = [x for x in s.shapes if x.shape_type == 16]
    tx = " | ".join(x.text_frame.text.replace("\n", " ")[:24] for x in s.shapes
                    if x.has_text_frame and x.text_frame.text.strip())[:60]
    print(f"P{i}: movie={len(mv)}  {tx}")
print("...")
for i in (17, 18, 19):
    tx = " | ".join(x.text_frame.text.replace("\n", " ")[:24] for x in sl[i].shapes
                    if x.has_text_frame and x.text_frame.text.strip())[:60]
    print(f"P{i+1}: {tx}")
