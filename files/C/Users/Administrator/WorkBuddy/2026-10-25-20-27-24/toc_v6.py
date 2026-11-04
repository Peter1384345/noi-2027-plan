# -*- coding: utf-8 -*-
"""① 大目录视觉升级（五栏书页式索引，内容不变）
   ② 每个部分之前插入一页「小目录」（奶白页 + 进度轴 + 本节条目）
   ③ 全部页码按最终页序重算
"""
from copy import deepcopy
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.dml.color import RGBColor

F = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_最终版.pptx"
IN = 914400

CREAM = RGBColor(0xF3, 0xED, 0xDF)
GOLD = RGBColor(0xE8, 0xC8, 0x7A)
WARM = RGBColor(0xF0, 0xC8, 0xBC)
RED = RGBColor(0xC0, 0x00, 0x00)
BG = RGBColor(0xF7, 0xF4, 0xEE)
INK = RGBColor(0x3A, 0x33, 0x30)
GREY = RGBColor(0x8A, 0x80, 0x78)
LINE = RGBColor(0xEA, 0xE0, 0xD2)
SERIF = "仿宋"

prs = Presentation(F)
slides = list(prs.slides)


def mk_rect(slide, x, y, w, h, fill=None, line=None, lw=1.0, shape=MSO_SHAPE.RECTANGLE, adj=None):
    shp = slide.shapes.add_shape(shape, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    shp.shadow.inherit = False
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(lw)
    if adj is not None:
        try:
            shp.adjustments[0] = adj
        except Exception:
            pass
    return shp


def mk_text(slide, x, y, w, h, content, size, color=CREAM, font="微软雅黑",
            align=PP_ALIGN.LEFT, spc=0, lnspc=125, bold=False):
    tb = slide.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
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


# ============================================================
# ① 大目录升级
# ============================================================
toc = slides[3]

tpl_num = None
for sh in toc.shapes:
    if sh.name.startswith(("toc",)) and sh.has_text_frame and sh.text_frame.text.strip() == "01":
        tpl_num = deepcopy(sh._element)

for sh in list(toc.shapes):
    if sh.name.startswith(("toc", "Rectangle", "TextBox")):
        sh._element.getparent().remove(sh._element)

next_id = [800]


def num_from_tpl(x, y, w, h, text, sz):
    el = deepcopy(tpl_num)
    c = el.find(qn('p:nvSpPr')).find(qn('p:cNvPr'))
    c.set('id', str(next_id[0])); next_id[0] += 1
    c.set('name', 'tocnum')
    xfrm = el.find(qn('p:spPr')).find(qn('a:xfrm'))
    xfrm.find(qn('a:off')).set('x', str(int(x))); xfrm.find(qn('a:off')).set('y', str(int(y)))
    xfrm.find(qn('a:ext')).set('cx', str(int(w))); xfrm.find(qn('a:ext')).set('cy', str(int(h)))
    tx = el.find(qn('p:txBody'))
    ps = tx.findall(qn('a:p'))
    p0 = ps[0]
    runs = p0.findall(qn('a:r'))
    keep = runs[0]
    for r in runs[1:]:
        p0.remove(r)
    keep.find(qn('a:t')).text = text
    for e2 in (keep.find(qn('a:rPr')), p0.find(qn('a:endParaRPr'))):
        if e2 is not None:
            e2.set('sz', str(int(sz * 100)))
            e2.set('spc', '0')
    for p in ps[1:]:
        tx.remove(p)
    toc.shapes._spTree.append(el)


# 页眉：目录 改仿宋（本机无华文行楷），并统一高对比配色
for sh in toc.shapes:
    if sh.name in ("文本框 122", "文本框 125", "文本框 126") and sh.has_text_frame:
        col = CREAM if sh.name == "文本框 125" else GOLD
        fnt = SERIF if sh.name == "文本框 125" else "Georgia"
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                r.font.color.rgb = col
                r.font.name = fnt
                rPr = r._r.get_or_add_rPr()
                ea = rPr.find(qn('a:ea'))
                if ea is None:
                    ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
                ea.set('typeface', fnt)

L, R = 0.93 * IN, 12.40 * IN
TOT = R - L
COLW = TOT / 5
GRID_T, GRID_B = 1.80 * IN, 6.58 * IN

# 顶部横线 + 四条竖线
mk_rect(toc, L, GRID_T, TOT, 0.012 * IN, GOLD)
for i in range(1, 5):
    mk_rect(toc, L + i * COLW - 0.004 * IN, GRID_T, 0.008 * IN, GRID_B - GRID_T, GOLD)

COLS = [
    ("01", "序章 · 团队分工", "十五人，五个小组"),
    ("02", "微光 · 韩雅平", "寒门筑梦 · 699 分圆梦清华"),
    ("03", "成炬 · 陈新超", "高山邮路 · 1700 个日夜"),
    ("04", "燎原 · 微光成炬", "两束微光，同一种选择"),
    ("05", "致谢 · 谢谢聆听", "十五人同行，共燃一盏灯"),
]
page_marks = []
for i, (num, title, sub) in enumerate(COLS):
    x0 = L + i * COLW
    tx = x0 + 0.06 * IN
    tw = COLW - 0.18 * IN
    num_from_tpl(tx, 2.04 * IN, 0.95 * IN, 0.86 * IN, num, 52)
    mk_rect(toc, tx, 2.94 * IN, 0.58 * IN, 0.018 * IN, GOLD)
    mk_text(toc, tx, 3.06 * IN, tw, 0.40 * IN, title, 18, color=CREAM, font=SERIF, spc=80)
    mk_text(toc, tx, 3.46 * IN, tw, 0.28 * IN, sub, 10, color=WARM, font="微软雅黑", spc=30)
    pm = mk_text(toc, tx, 6.30 * IN, tw, 0.22 * IN, "P00", 8.5, color=GOLD, font="Georgia", spc=80)
    page_marks.append(pm)

# 主题大标题（页眉右）
mk_text(toc, 6.05 * IN, 0.96 * IN, 6.3 * IN, 0.56 * IN, "微光成炬 · 星火自有燎原时", 23,
        color=CREAM, font="微软雅黑", spc=60)

# ============================================================
# ② 五页小目录
# ============================================================
layout = min(prs.slide_layouts, key=lambda l: len(l.placeholders))

MINI = [
    dict(key=0, over="PROLOGUE", title="序章 · 团队分工", sub="1 页 · 约 30 秒",
         items=[("团队分工 · 五个小组各司其职", 4)]),
    dict(key=1, over="PART 01", title="微光 · 韩雅平", sub="4 页 · 约 3 分钟（含 34 秒采访视频）",
         items=[("寒门筑梦 · 三间平房与 28 张奖状", 6),
                ("699 分 · 清华招生组的电话", 7),
                ("顾妈妈 · 12 年资助、365 人次", 8),
                ("视频 ·《小莉帮忙》采访", 9)]),
    dict(key=2, over="PART 02", title="成炬 · 陈新超", sub="5 页 · 约 4 分钟（含 2 分 46 秒纪实视频）",
         items=[("高山邮路 · 一辆没空调的旧货车", 11),
                ("陈新超 · 抗癌、坚守与 1700 个日夜", 12),
                ("暖心服务站 · 便民车 / 代买菜 / 抗洪", 13),
                ("视频 ·《新时代的我们》纪实", 14),
                ("党员风采 · 机动页（3 分 18 秒）", 15)]),
    dict(key=3, over="EPILOGUE", title="燎原 · 微光成炬", sub="1 页 · 约 40 秒",
         items=[("两束微光 · 同一种选择", 16),
                ("一张书桌，也能撑起一座山", 16),
                ("把邮路走成归途，把温暖送进每一户人家", 16)]),
    dict(key=4, over="CREDITS", title="致谢 · 谢谢聆听", sub="3 页 · 约 20 秒",
         items=[("特别鸣谢 · 五个小组", 17),
                ("谢谢聆听", 19)]),
]

minor_nums = {}   # (key, item_idx) -> (shape, anchor_current_index)

for m in MINI:
    s = prs.slides.add_slide(layout)
    for sh in list(s.shapes):
        sh._element.getparent().remove(sh._element)
    # 底色
    mk_rect(s, 0, 0, prs.slide_width, prs.slide_height, BG)
    # 左侧红条
    mk_rect(s, 0.93 * IN, 1.06 * IN, 0.055 * IN, 1.42 * IN, RED)
    # 眉标
    mk_text(s, 1.10 * IN, 1.02 * IN, 4.0 * IN, 0.24 * IN, m["over"], 9, color=RED,
            font="Georgia", spc=300)
    # 大标题
    mk_text(s, 1.10 * IN, 1.22 * IN, 7.2 * IN, 0.80 * IN, m["title"], 34, color=RED,
            font=SERIF, spc=80)
    # 副信息
    mk_text(s, 1.10 * IN, 2.02 * IN, 7.6 * IN, 0.28 * IN, m["sub"], 10.5, color=GREY,
            font="微软雅黑", spc=20)

    # 进度轴
    axis_y = 2.72 * IN
    mk_rect(s, L, axis_y, TOT, 0.008 * IN, LINE)
    labels = ["序章", "微光", "成炬", "燎原", "致谢"]
    for i in range(5):
        cx = L + i * (TOT / 4)
        cur = (i == m["key"])
        dot = 0.11 * IN
        mk_rect(s, cx - dot / 2, axis_y - dot / 2 + 0.004 * IN, dot, dot,
                RED if cur else BG, line=None if cur else RGBColor(0xD8, 0xC8, 0xB4),
                lw=1.0, shape=MSO_SHAPE.OVAL)
        mk_text(s, cx - 0.55 * IN, axis_y + 0.16 * IN, 1.10 * IN, 0.24 * IN,
                f"{i+1:02d} {labels[i]}", 9,
                color=RED if cur else GREY, font="微软雅黑", align=PP_ALIGN.CENTER,
                spc=40, bold=cur)

    # 条目
    y0 = 3.30 * IN
    rowh = 0.60 * IN
    for j, (txt, anchor) in enumerate(m["items"]):
        y = y0 + j * rowh
        mk_rect(s, 0.93 * IN, y + 0.20 * IN, 0.055 * IN, 0.055 * IN, RED)
        mk_text(s, 1.14 * IN, y + 0.10 * IN, 9.6 * IN, 0.32 * IN, txt, 13, color=INK,
                font="微软雅黑", spc=20)
        pm = mk_text(s, 11.30 * IN, y + 0.12 * IN, 1.10 * IN, 0.24 * IN, "P00", 9,
                     color=GREY, font="Georgia", align=PP_ALIGN.RIGHT, spc=60)
        minor_nums[(m["key"], j)] = (pm, anchor)
        mk_rect(s, 0.93 * IN, y + 0.50 * IN, TOT, 0.006 * IN, LINE)

# ============================================================
# ③ 重排页序
# ============================================================
desired = [0, 1, 2, 3, 20, 4, 5, 21, 6, 7, 8, 9, 10, 22, 11, 12, 13, 14, 15, 23, 16, 24, 17, 18, 19]
sldIdLst = prs.slides._sldIdLst
cur = list(sldIdLst)
assert len(cur) == 25, len(cur)
for el in cur:
    sldIdLst.remove(el)
for i in desired:
    sldIdLst.append(cur[i])

final_of = {ci: pos for pos, ci in enumerate(desired)}
print("final map:", final_of)

# 大目录页码
toc_pages = [
    (5, 5, True),    # 01 序章: 团队分工 idx4 -> final5
    (6, 11, False),  # 02 微光: PART01 idx5 -> 视频 idx9
    (12, 18, False), # 03 成炬: PART02 idx10 -> 党员 idx15
    (20, 20, True),  # 04 燎原: 尾声 idx16
    (22, 24, False), # 05 致谢: idx17..idx19
]
for pm, (a, b, single) in zip(page_marks, toc_pages):
    pa, pb = final_of[a] + 1, final_of[b] + 1
    pm.text_frame.paragraphs[0].runs[0].text = f"P{pa:02d}" if single else f"P{pa:02d}—{pb:02d}"

# 小目录条目页码
for (k, j), (pm, anchor) in minor_nums.items():
    pm.text_frame.paragraphs[0].runs[0].text = f"P{final_of[anchor]+1:02d}"

# 更新节奏表备注（原封面第一页的备注）
try:
    ns = slides[0].notes_slide
    tf = ns.notes_text_frame
    if tf is not None:
        tf.text = ("全片 10 分钟节奏表（控场参考）：P1 片头 5 秒（不说话）｜P2-P3 封面 10 秒｜"
                   "P4 大目录 20 秒｜P5 序章小目录 + P6 团队分工 35 秒｜P7-P12 微光·韩雅平 3 分 00 秒"
                   "（含 34 秒采访视频）｜P13-P19 成炬·陈新超 4 分 00 秒（含 2 分 46 秒纪实视频）｜"
                   "P20-P21 尾声 40 秒｜P22-P25 致谢 20 秒。小目录页每页只念一句，约 3-5 秒。"
                   "党员风采（3 分 18 秒）为机动页，时间不够直接跳过。")
        print("notes updated")
except Exception as e:
    print("notes skip:", e)

prs.save(F)
print("saved")
