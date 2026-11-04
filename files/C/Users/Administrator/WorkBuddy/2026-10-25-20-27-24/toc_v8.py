# -*- coding: utf-8 -*-
"""v8：从 _最终版.pptx（25 页干净版）重建
   ① 彻底删除「序章」小目录页（同时 drop_rel，避免 zip 重名）
   ② 大目录升级为四栏书页索引：深酒红渐变底 + 大字号全加粗 + 四块改名
   ③ 四页小目录同步放大加粗，页码按内容页精确定位
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.dml.color import RGBColor

SRC = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_最终版.pptx"
DST = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_定稿.pptx"
IN = 914400

CREAM = RGBColor(0xF7, 0xF1, 0xE3)
GOLD = RGBColor(0xE8, 0xC8, 0x7A)
WARM = RGBColor(0xF0, 0xD6, 0xC8)
RED = RGBColor(0xC0, 0x00, 0x00)
BG = RGBColor(0xF7, 0xF4, 0xEE)
INK = RGBColor(0x2E, 0x28, 0x26)
GREY = RGBColor(0x7C, 0x72, 0x6A)
LINE = RGBColor(0xEA, 0xE0, 0xD2)
SERIF = "仿宋"

prs = Presentation(SRC)
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
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = 1.12
    r = p.add_run()
    r.text = txt
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


def restyle(sh, size, color, font, spc=0, bold=True, txt=None):
    for p in sh.text_frame.paragraphs:
        runs = p.runs
        if txt is not None and runs:
            # 只保留首个 run，删掉多余 run，避免文字重复叠加
            for extra in runs[1:]:
                extra._r.getparent().remove(extra._r)
            runs = p.runs
        for r in runs:
            if txt is not None:
                r.text = txt
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.color.rgb = color
            r.font.name = font
            rPr = r._r.get_or_add_rPr()
            ea = rPr.find(qn('a:ea'))
            if ea is None:
                ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
            ea.set('typeface', font)
            if spc:
                rPr.set('spc', str(int(spc)))


# ---------------- ① 删除序章小目录页 ----------------
sl = list(prs.slides)
mini_pages = [i for i, s in enumerate(sl)
              if any(sh.has_text_frame and sh.text_frame.text.strip() in AXIS for sh in s.shapes)]
print("小目录页(1-based):", [i + 1 for i in mini_pages])
assert len(mini_pages) == 5, mini_pages
kill = mini_pages[0]
lst = prs.slides._sldIdLst
sldIds = list(lst)
rId = sldIds[kill].get(qn('r:id'))
prs.part.drop_rel(rId)
lst.remove(sldIds[kill])
print("已删除 P%d（序章小目录），余 %d 页" % (kill + 1, len(prs.slides._sldIdLst)))
sl = list(prs.slides)

# ---------------- ② 大目录重建 ----------------
toc = sl[3]
KEEP = {"矩形 117", "圆角矩形 119", "矩形 121", "矩形 124",
        "文本框 122", "文本框 125", "文本框 126"}
for sh in list(toc.shapes):
    if sh.name not in KEEP:
        sh._element.getparent().remove(sh._element)

# 背景：深酒红竖向渐变（替换纯红）
bgs = [sh for sh in toc.shapes if sh.name == "矩形 117"][0]
try:
    f = bgs.fill
    f.gradient()
    st = f.gradient_stops
    st[0].color.rgb = RGBColor(0x8C, 0x14, 0x16)
    st[0].position = 0.0
    st[1].color.rgb = RGBColor(0x53, 0x07, 0x09)
    st[1].position = 1.0
    f.gradient_angle = 90.0
    print("背景已改深酒红渐变")
except Exception as e:
    bgs.fill.solid(); bgs.fill.fore_color.rgb = RGBColor(0x7A, 0x11, 0x13)
    print("渐变失败，回落实色:", e)

for sh in toc.shapes:
    if sh.name == "文本框 122":          # CONTENTS
        restyle(sh, 13, GOLD, "Georgia", spc=250)
        sh.top = Emu(int(0.56 * IN))
    elif sh.name == "文本框 125":        # 目录
        restyle(sh, 46, CREAM, SERIF, spc=120)
        sh.left = Emu(int(1.18 * IN)); sh.top = Emu(int(0.92 * IN))
        sh.width = Emu(int(1.70 * IN)); sh.height = Emu(int(0.74 * IN))
    elif sh.name == "文本框 126":        # FOUR CHAPTERS
        restyle(sh, 11, GOLD, "Georgia", spc=220, txt="FOUR CHAPTERS · ONE STORY")
        sh.left = Emu(int(1.20 * IN)); sh.top = Emu(int(1.70 * IN))
        sh.width = Emu(int(4.20 * IN)); sh.height = Emu(int(0.22 * IN))
    elif sh.name == "矩形 124":          # 竖条
        sh.left = Emu(int(0.96 * IN)); sh.top = Emu(int(0.96 * IN))
        sh.width = Emu(int(0.045 * IN)); sh.height = Emu(int(0.66 * IN))
        sh.fill.solid(); sh.fill.fore_color.rgb = GOLD

L, R = 0.93 * IN, 12.40 * IN
TOT = R - L
COLW = TOT / 4
GT, GB = 2.10 * IN, 6.62 * IN

rect(toc, L, GT, TOT, 0.011 * IN, GOLD)
for i in range(1, 4):
    rect(toc, L + i * COLW - 0.004 * IN, GT + 0.02 * IN, 0.007 * IN, GB - GT - 0.04 * IN,
         RGBColor(0x9C, 0x3A, 0x36))
rect(toc, L, GB, TOT, 0.009 * IN, GOLD)

text(toc, 6.00 * IN, 1.08 * IN, 6.40 * IN, 0.48 * IN, "微光成炬 · 星火自有燎原时", 26,
     color=CREAM, font="微软雅黑", align=PP_ALIGN.RIGHT, spc=80)
text(toc, 6.00 * IN, 1.66 * IN, 6.40 * IN, 0.22 * IN, "一 场 关 于 坚 守 的 讲 述", 10.5,
     color=WARM, align=PP_ALIGN.RIGHT, spc=120)

COLS = [
    ("01", "一张书桌", "微光 · 韩雅平", "三间平房 · 28 张奖状"),
    ("02", "一条邮路", "成炬 · 陈新超", "旧货车 · 1700 个日夜"),
    ("03", "一场奔赴", "燎原 · 微光成炬", "两张答卷 · 同一种选择"),
    ("04", "一路同行", "致谢 · 谢谢聆听", "十五人 · 共燃一盏灯"),
]
marks = []
for i, (num, title, tag, note) in enumerate(COLS):
    x0 = L + i * COLW
    tx = x0 + 0.20 * IN
    tw = COLW - 0.36 * IN
    text(toc, tx, 2.62 * IN, 1.4 * IN, 1.10 * IN, num, 68, GOLD, font="Georgia")
    rect(toc, tx, 3.80 * IN, 0.72 * IN, 0.022 * IN, GOLD)
    text(toc, tx, 3.92 * IN, tw, 0.58 * IN, title, 30, CREAM, font=SERIF, spc=130)
    text(toc, tx, 4.72 * IN, tw, 0.30 * IN, tag, 13.5, GOLD, spc=60)
    text(toc, tx, 5.10 * IN, tw, 0.30 * IN, note, 13, WARM, spc=30)
    marks.append(text(toc, tx, 6.04 * IN, tw, 0.28 * IN, "P00", 13, GOLD,
                      font="Georgia", spc=90))

text(toc, L, 6.86 * IN, 4.5 * IN, 0.24 * IN, "拾光者小组 · 十五人", 10.5, GOLD, spc=180)
text(toc, 8.60 * IN, 6.86 * IN, 3.80 * IN, 0.24 * IN, "FROM SPARK TO FLAME", 10.5, GOLD,
     font="Georgia", align=PP_ALIGN.RIGHT, spc=280)

# ---------------- ③ 四页小目录 ----------------
MINI = [
    dict(over="PART 01", title="微光 · 韩雅平", sub="4 页 · 约 3 分钟（含 34 秒采访视频）",
         items=["寒门筑梦 · 三间平房与 28 张奖状", "699 分 · 清华招生组的一个电话",
                "顾妈妈 · 十二年，一场双向奔赴", "视频 ·《小莉帮忙》采访实录"],
         keys=["三间平房，墙上贴满 28 张奖状", "物理类 · 圆梦清华", "顾妈妈", "视频 · 60 秒看见雅平"]),
    dict(over="PART 02", title="成炬 · 陈新超", sub="5 页 · 约 4 分钟（含 2 分 46 秒纪实视频）",
         items=["陈新超 · 一辆没空调的旧货车", "一个人的暖心服务站",
                "视频 ·《新时代的我们》纪实", "1700 个日夜 · 20 万公里",
                "党员风采 · 机动页（3 分 18 秒）"],
         keys=["湖北阳新县水源村", "暖心服务站", "乡邮路上的“铁娘子”",
               "多个日夜 · 暖心邮路", "党员风采"]),
    dict(over="EPILOGUE", title="燎原 · 微光成炬", sub="P20 · 1 页 · 约 40 秒",
         items=["韩雅平 · 一张书桌，也能撑起一座山", "陈新超 · 把邮路走成归途",
                "两束微光 · 同一种选择"],
         keys=[], quote="“知识改变命运；而善意，让命运有了另一条路。”"),
    dict(over="CREDITS", title="致谢 · 谢谢聆听", sub="P22—24 · 3 页 · 约 20 秒",
         items=["特别鸣谢 · 五个小组，十五个人", "谢谢聆听 · 星火自有燎原时"],
         keys=[], quote="微光成炬，星火自有燎原时。"),
]
LABELS = ["微光", "成炬", "燎原", "致谢"]

mini_pages = [i for i, s in enumerate(sl)
              if any(sh.has_text_frame and sh.text_frame.text.strip() in AXIS for sh in s.shapes)]
print("待重建小目录:", [i + 1 for i in mini_pages])
assert len(mini_pages) == 4

item_marks = []
for k, (page_i, m) in enumerate(zip(mini_pages, MINI)):
    s = sl[page_i]
    for sh in list(s.shapes):
        sh._element.getparent().remove(sh._element)

    rect(s, 0, 0, prs.slide_width, prs.slide_height, BG)
    rect(s, 0.93 * IN, 0.96 * IN, 0.07 * IN, 1.78 * IN, RED)
    text(s, 1.20 * IN, 0.92 * IN, 4.2 * IN, 0.30 * IN, m["over"], 13, RED,
         font="Georgia", spc=320)
    text(s, 1.18 * IN, 1.16 * IN, 8.6 * IN, 0.96 * IN, m["title"], 40, RED, font=SERIF, spc=80)
    text(s, 1.22 * IN, 2.16 * IN, 8.6 * IN, 0.34 * IN, m["sub"], 14.5, GREY, spc=30)

    # 四段式章节进度条（与四栏网格同宽同分栏，当前段实心）
    axis_y = 2.96 * IN
    GREYSEG = RGBColor(0xDD, 0xCE, 0xBA)
    for i in range(4):
        sx = L + i * COLW
        on = (i == k)
        rect(s, sx, axis_y, COLW - 0.10 * IN, 0.045 * IN if on else 0.018 * IN,
             RED if on else GREYSEG)
        text(s, sx, axis_y + 0.16 * IN, COLW - 0.10 * IN, 0.28 * IN,
             f"{i+1:02d}  {LABELS[i]}", 12.5, RED if on else GREY, spc=60,
             bold=True if on else False)

    n = len(m["items"])
    top_limit = 3.74 * IN if n >= 5 else 3.88 * IN
    bot_limit = 5.50 * IN if m.get("quote") else 6.40 * IN
    rowh = min(0.82 * IN, (bot_limit - top_limit) / n)
    y0 = top_limit + ((bot_limit - top_limit) - rowh * n) / 2

    for j, txt in enumerate(m["items"]):
        y = y0 + j * rowh
        rect(s, 0.93 * IN, y + 0.24 * IN, 0.085 * IN, 0.085 * IN, RED)
        text(s, 1.22 * IN, y + 0.06 * IN, 9.2 * IN, 0.42 * IN, txt, 18, INK, spc=30)
        if m["keys"]:
            pm = text(s, 11.00 * IN, y + 0.12 * IN, 1.40 * IN, 0.30 * IN, "P00", 12.5, GREY,
                      font="Georgia", align=PP_ALIGN.RIGHT, spc=70)
            item_marks.append((pm, m["keys"][j]))
        if j < n - 1:
            sep_y = y + 0.31 * IN + (rowh - 0.25 * IN) * 0.5
            rect(s, 0.93 * IN, sep_y, TOT, 0.007 * IN, RGBColor(0xE2, 0xD5, 0xC2))

    if m.get("quote"):
        rect(s, 0.93 * IN, 5.82 * IN, TOT, 0.008 * IN, GOLD)
        text(s, 1.22 * IN, 6.00 * IN, 11.0 * IN, 0.50 * IN, m["quote"], 25, RED,
             font=SERIF, spc=70)

    rect(s, 0.93 * IN, 6.52 * IN, TOT, 0.006 * IN, LINE)
    text(s, 0.93 * IN, 6.62 * IN, 4.5 * IN, 0.24 * IN, "拾光者小组 · 十五人", 10, GREY, spc=180)
    text(s, 8.60 * IN, 6.62 * IN, 3.80 * IN, 0.24 * IN, "FROM SPARK TO FLAME", 10, GREY,
         font="Georgia", align=PP_ALIGN.RIGHT, spc=300)

# ---------------- ④ 页码重算（排除目录页与分隔页干扰） ----------------
toc_idx = set([3]) | set(mini_pages)


def page_of(kw, last=False):
    hits = [i for i, s in enumerate(sl) if i not in toc_idx and
            any(sh.has_text_frame and kw in sh.text_frame.text for sh in s.shapes)]
    if not hits:
        raise LookupError(kw)
    return (hits[-1] if last else hits[0]) + 1


p_part1 = page_of("PART 01 · 寒门筑梦")
p_part2 = page_of("PART 02 · 高山邮路")
p_epi = page_of("EPILOGUE · 尾声")
p_thx1 = page_of("FROM SPARK TO FLAME")
p_thx2 = page_of("FROM SPARK TO FLAME", last=True)
ranges = [(p_part1, page_of("视频 · 60 秒看见雅平")), (p_part2, page_of("党员风采", last=True)),
          (mini_pages[2] + 1, p_epi), (mini_pages[3] + 1, p_thx2)]
for sh, (a, b) in zip(marks, ranges):
    t = f"P{a:02d}" if a == b else f"P{a:02d}—{b:02d}"
    restyle(sh, 13, GOLD, "Georgia", spc=90, txt=t)
    print("大目录 →", t)

for sh, kw in item_marks:
    p = page_of(kw, last=(kw in ("党员风采", "FROM SPARK TO FLAME")))
    restyle(sh, 12.5, GREY, "Georgia", spc=70, txt=f"P{p:02d}")
    print("   小目录条目 %-28s → P%02d" % (kw, p))

prs.save(DST)
print("saved", DST)
