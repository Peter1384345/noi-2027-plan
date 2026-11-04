# -*- coding: utf-8 -*-
"""① 删掉「序章」块与其小目录页 ② 四栏重排、字号加大、全部加粗 ③ 四块改名 ④ 页码重算"""
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.dml.color import RGBColor

F = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_定稿.pptx"
IN = 914400
CREAM = RGBColor(0xF3, 0xED, 0xDF)
GOLD = RGBColor(0xE8, 0xC8, 0x7A)
WARM = RGBColor(0xF6, 0xD9, 0xCF)
RED = RGBColor(0xC0, 0x00, 0x00)
BG = RGBColor(0xF7, 0xF4, 0xEE)
INK = RGBColor(0x2E, 0x28, 0x26)
GREY = RGBColor(0x7C, 0x72, 0x6A)
LINE = RGBColor(0xEA, 0xE0, 0xD2)
SERIF = "仿宋"

prs = Presentation(F)
sl = list(prs.slides)

AXIS = {"01 序章", "02 微光", "03 成炬", "04 燎原", "05 致谢"}


def rect(s, x, y, w, h, fill, line=None, lw=1.0, shape=MSO_SHAPE.RECTANGLE):
    shp = s.shapes.add_shape(shape, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    shp.shadow.inherit = False
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line; shp.line.width = Pt(lw)
    return shp


def text(s, x, y, w, h, txt, size, color, font="微软雅黑", align=PP_ALIGN.LEFT,
         spc=0, bold=True):
    tb = s.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]; p.alignment = align
    p.line_spacing = 1.15
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


# ---------------- ① 删除序章小目录页 ----------------
mini_pages = [i for i, s in enumerate(sl)
              if any(sh.has_text_frame and sh.text_frame.text.strip() in AXIS for sh in s.shapes)]
print("小目录页:", [i + 1 for i in mini_pages])
first_mini = mini_pages[0]
el = prs.slides._sldIdLst[first_mini]
prs.slides._sldIdLst.remove(el)
print("已删除序章小目录页 (原 P%d)" % (first_mini + 1))

sl = list(prs.slides)

# ---------------- ② 大目录重建（四栏 / 加粗 / 加大） ----------------
toc = sl[3]
for sh in list(toc.shapes):
    if sh.name.startswith(("toc", "Rectangle", "TextBox")):
        sh._element.getparent().remove(sh._element)

L, R = 0.93 * IN, 12.40 * IN
TOT = R - L
COLW = TOT / 4
GRID_T, GRID_B = 1.80 * IN, 6.86 * IN

rect(toc, L, GRID_T, TOT, 0.012 * IN, GOLD)
for i in range(1, 4):
    rect(toc, L + i * COLW - 0.004 * IN, GRID_T, 0.008 * IN, GRID_B - GRID_T, GOLD)
rect(toc, L, GRID_B, TOT, 0.008 * IN, GOLD)

# 页眉配色（目录 / CONTENTS / FIVE CHAPTERS）
for sh in toc.shapes:
    if sh.name in ("文本框 122", "文本框 125", "文本框 126") and sh.has_text_frame:
        col = CREAM if sh.name == "文本框 125" else GOLD
        fnt = SERIF if sh.name == "文本框 125" else "Georgia"
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                r.font.color.rgb = col
                r.font.name = fnt
                r.font.bold = True
                r.font.size = Pt(40 if sh.name == "文本框 125" else (10.5 if sh.name == "文本框 122" else 11))
                rPr = r._r.get_or_add_rPr()
                ea = rPr.find(qn('a:ea'))
                if ea is None:
                    ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
                ea.set('typeface', fnt)

text(toc, 6.05 * IN, 0.96 * IN, 6.3 * IN, 0.56 * IN, "微光成炬 · 星火自有燎原时", 24,
     color=CREAM, font="微软雅黑", spc=60)

COLS = [
    ("01", "微光 · 一张书桌", "韩雅平 · 699 分圆梦清华"),
    ("02", "成炬 · 一条邮路", "陈新超 · 1700 个日夜"),
    ("03", "燎原 · 一片星火", "两束微光，同一种选择"),
    ("04", "致谢 · 一盏灯", "十五人同行，共燃一盏灯"),
]
marks = []
for i, (num, title, sub) in enumerate(COLS):
    x0 = L + i * COLW
    tx = x0 + 0.10 * IN
    tw = COLW - 0.26 * IN
    text(toc, tx, 2.96 * IN, 1.6 * IN, 1.08 * IN, num, 60, GOLD, font="Georgia")
    rect(toc, tx, 4.12 * IN, 0.66 * IN, 0.02 * IN, GOLD)
    text(toc, tx, 4.24 * IN, tw, 0.52 * IN, title, 23, CREAM, font=SERIF, spc=60)
    text(toc, tx, 4.82 * IN, tw, 0.34 * IN, sub, 13, WARM, spc=40)
    marks.append(text(toc, tx, 5.36 * IN, tw, 0.26 * IN, "P00", 10, GOLD, font="Georgia", spc=80))

text(toc, L, 6.96 * IN, 4.5 * IN, 0.24 * IN, "拾光者小组 · 十五人", 9, GOLD, spc=150)
text(toc, 8.6 * IN, 6.96 * IN, 3.8 * IN, 0.24 * IN, "FROM SPARK TO FLAME", 9, GOLD,
     font="Georgia", align=PP_ALIGN.RIGHT, spc=250)

# ---------------- ③ 四页小目录重建 ----------------
MINI = [
    dict(over="PART 01", title="微光 · 韩雅平", sub="4 页 · 约 3 分钟（含 34 秒采访视频）",
         items=["寒门筑梦 · 三间平房与 28 张奖状", "699 分 · 清华招生组的电话",
                "顾妈妈 · 12 年资助、365 人次", "视频 ·《小莉帮忙》采访"]),
    dict(over="PART 02", title="成炬 · 陈新超", sub="5 页 · 约 4 分钟（含 2 分 46 秒纪实视频）",
         items=["高山邮路 · 一辆没空调的旧货车", "陈新超 · 抗癌、坚守与 1700 个日夜",
                "暖心服务站 · 便民车 / 代买菜 / 抗洪", "视频 ·《新时代的我们》纪实",
                "党员风采 · 机动页（3 分 18 秒）"]),
    dict(over="EPILOGUE", title="燎原 · 微光成炬", sub="1 页 · 约 40 秒",
         items=["两束微光 · 同一种选择", "一张书桌，也能撑起一座山",
                "把邮路走成归途，把温暖送进每一户人家"]),
    dict(over="CREDITS", title="致谢 · 谢谢聆听", sub="3 页 · 约 20 秒",
         items=["特别鸣谢 · 五个小组", "谢谢聆听"]),
]
LABELS = ["微光", "成炬", "燎原", "致谢"]

mini_pages = [i for i, s in enumerate(sl)
              if any(sh.has_text_frame and sh.text_frame.text.strip() in AXIS for sh in s.shapes)]
print("待重建小目录:", [i + 1 for i in mini_pages])

item_marks = []   # (shape, keyword)
KEYS = [
    ["三间平房，墙上贴满 28 张奖状", "物理类 · 圆梦清华", "顾妈妈", "视频 · 60 秒看见雅平"],
    ["湖北阳新县水源村", "暖心服务站", "乡邮路上的“铁娘子”", "1700+", "党员风采"],
    ["EPILOGUE · 尾声", "EPILOGUE · 尾声", "EPILOGUE · 尾声"],
    ["FROM SPARK TO FLAME", "谢谢聆听"],
]

for page_i, m in zip(mini_pages, MINI):
    s = sl[page_i]
    for sh in list(s.shapes):
        sh._element.getparent().remove(sh._element)
    rect(s, 0, 0, prs.slide_width, prs.slide_height, BG)
    rect(s, 0.93 * IN, 1.02 * IN, 0.06 * IN, 1.55 * IN, RED)
    text(s, 1.12 * IN, 0.98 * IN, 4.0 * IN, 0.26 * IN, m["over"], 10, RED, font="Georgia", spc=300)
    text(s, 1.12 * IN, 1.18 * IN, 7.6 * IN, 0.86 * IN, m["title"], 36, RED, font=SERIF, spc=60)
    text(s, 1.12 * IN, 2.12 * IN, 8.0 * IN, 0.30 * IN, m["sub"], 12, GREY, spc=20)

    axis_y = 2.86 * IN
    rect(s, L, axis_y, TOT, 0.008 * IN, LINE)
    cur = page_i - mini_pages[0] if page_i >= mini_pages[0] else 0
    cur = mini_pages.index(page_i)
    for i in range(4):
        cx = L + i * (TOT / 3)
        on = (i == cur)
        d = 0.13 * IN
        rect(s, cx - d / 2, axis_y - d / 2 + 0.004 * IN, d, d,
             RED if on else BG, line=None if on else RGBColor(0xD8, 0xC8, 0xB4), lw=1.2,
             shape=MSO_SHAPE.OVAL)
        text(s, cx - 0.65 * IN, axis_y + 0.18 * IN, 1.30 * IN, 0.26 * IN,
             f"{i+1:02d} {LABELS[i]}", 11, RED if on else GREY, align=PP_ALIGN.CENTER, spc=40)

    y0 = 3.40 * IN
    rowh = 0.64 * IN
    for j, txt in enumerate(m["items"]):
        y = y0 + j * rowh
        rect(s, 0.93 * IN, y + 0.22 * IN, 0.07 * IN, 0.07 * IN, RED)
        text(s, 1.18 * IN, y + 0.08 * IN, 9.4 * IN, 0.36 * IN, txt, 15, INK, spc=20)
        pm = text(s, 11.10 * IN, y + 0.12 * IN, 1.30 * IN, 0.26 * IN, "P00", 10.5, GREY,
                  font="Georgia", align=PP_ALIGN.RIGHT, spc=60)
        item_marks.append((pm, KEYS[mini_pages.index(page_i)][j]))
        rect(s, 0.93 * IN, y + 0.54 * IN, TOT, 0.006 * IN, LINE)

    rect(s, 0.93 * IN, 6.60 * IN, TOT, 0.006 * IN, LINE)
    text(s, 0.93 * IN, 6.70 * IN, 4.5 * IN, 0.24 * IN, "拾光者小组 · 十五人", 9, GREY, spc=150)
    text(s, 8.6 * IN, 6.70 * IN, 3.8 * IN, 0.24 * IN, "FROM SPARK TO FLAME", 9, GREY,
         font="Georgia", align=PP_ALIGN.RIGHT, spc=250)

# ---------------- ④ 页码重算 ----------------
def page_of(keyword, last=False):
    hits = [i for i, s in enumerate(sl)
            if any(sh.has_text_frame and keyword in sh.text_frame.text for sh in s.shapes)]
    if not hits:
        raise LookupError(keyword)
    return hits[-1] if last else hits[0]

p_part1 = page_of("PART 01 · 寒门筑梦")
p_vid1 = page_of("视频 · 60 秒看见雅平")
p_part2 = page_of("PART 02 · 高山邮路", last=False)
p_flag = page_of("党员风采", last=True)
p_epi = page_of("EPILOGUE · 尾声")
p_thx_first = page_of("FROM SPARK TO FLAME")
p_thx_last = page_of("FROM SPARK TO FLAME", last=True)

ranges = [(p_part1, p_vid1), (p_part2, p_flag), (p_epi, p_epi), (p_thx_first, p_thx_last)]
for sh, (a, b) in zip(marks, ranges):
    t = f"P{a+1:02d}" if a == b else f"P{a+1:02d}—{b+1:02d}"
    for p in sh.text_frame.paragraphs:
        for r in p.runs:
            r.text = t

for sh, kw in item_marks:
    p = page_of(kw, last=(kw in ("党员风采", "FROM SPARK TO FLAME", "谢谢聆听")))
    for para in sh.text_frame.paragraphs:
        for r in para.runs:
            r.text = f"P{p+1:02d}"

prs.save(F)
print("saved")

# ---------------- 复核 ----------------
p2 = Presentation(F)
sl2 = list(p2.slides)
print("页数:", len(sl2))
print("大目录:", [sh.text_frame.text for sh in sorted(
    [x for x in sl2[3].shapes if x.has_text_frame and x.text_frame.text.strip().startswith("P")],
    key=lambda x: x.left)])
for i, s in enumerate(sl2, 1):
    tx = [sh.text_frame.text.strip() for sh in s.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
    if any(t in AXIS for t in tx):
        print(f"P{i:02d} 小目录 {tx[1] if len(tx)>1 else ''} | 页码 {[t for t in tx if t.startswith('P') and len(t)<8]}")
