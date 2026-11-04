# -*- coding: utf-8 -*-
"""按用户要求：给缺章节页的部分补「红底 + 大标题」的极简标题页
   ① P17「燎原」原小目录页 → 重建为宏伟标题页
   ② 致谢前插入同款「致谢」标题页
   ③ 大目录文字提亮（纯白 + 亮金），底色改与章节页同为 8E0000→C00000
   ④ 大目录页码按新页序重算
"""
import sys, copy
sys.stdout.reconfigure(encoding='utf-8')
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.dml.color import RGBColor

F = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_定稿.pptx"
IN = 914400
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
YELLOW = RGBColor(0xFF, 0xFF, 0x00)
GOLD = RGBColor(0xE8, 0xC8, 0x7A)
GOLD2 = RGBColor(0xF5, 0xCE, 0x6E)
PALE = RGBColor(0xFF, 0xF0, 0xE2)
FONT = "微软雅黑"
SERIF = "Georgia"

prs = Presentation(F)


def bg_red(s):
    shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    shp.shadow.inherit = False
    f = shp.fill
    f.gradient()
    st = f.gradient_stops
    st[0].color.rgb = RGBColor(0x8E, 0x00, 0x00); st[0].position = 0.0
    st[1].color.rgb = RGBColor(0xC0, 0x00, 0x00); st[1].position = 1.0
    f.gradient_angle = 45.0
    shp.line.fill.background()
    return shp


def rect(s, x, y, w, h, fill):
    shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    shp.shadow.inherit = False
    shp.fill.solid(); shp.fill.fore_color.rgb = fill
    shp.line.fill.background()
    return shp


def text(s, x, y, w, h, txt, size, color, font=FONT, align=PP_ALIGN.CENTER, spc=0):
    tb = s.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = 1.0
    r = p.add_run(); r.text = txt
    f = r.font
    f.size = Pt(size); f.bold = True; f.color.rgb = color; f.name = font
    rPr = r._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
    ea.set('typeface', font)
    if spc:
        rPr.set('spc', str(int(spc)))
    return tb


def build_section(s, num, eyebrow, word, sub, tagline):
    for sh in list(s.shapes):
        sh._element.getparent().remove(sh._element)
    bg_red(s)
    text(s, 0.0, 1.28 * IN, 13.333 * IN, 0.36 * IN, f"PART {num} · {eyebrow}", 20, YELLOW, spc=380)
    text(s, 0.0, 1.92 * IN, 13.333 * IN, 2.40 * IN, word, 150, WHITE, spc=120)
    rect(s, 6.0 * IN, 4.94 * IN, 1.33 * IN, 0.028 * IN, GOLD)
    text(s, 0.0, 5.16 * IN, 13.333 * IN, 0.56 * IN, sub, 34, WHITE, spc=140)
    text(s, 0.0, 5.96 * IN, 13.333 * IN, 0.40 * IN, tagline, 20, YELLOW, spc=80)


sl = list(prs.slides)
# ---- ① 燎原页：原「EPILOGUE」小目录页 ----
idx_liao = [i for i, s in enumerate(sl)
            if any(sh.has_text_frame and sh.text_frame.text.strip() == "EPILOGUE" for sh in s.shapes)]
assert len(idx_liao) == 1, idx_liao
build_section(sl[idx_liao[0]], "03", "燎原", "燎原", "微光成炬", "两束微光，同一种选择")
print("重建燎原标题页 P%d" % (idx_liao[0] + 1))

# ---- ② 致谢前插入标题页 ----
idx_thx = [i for i, s in enumerate(sl)
           if any(sh.has_text_frame and "特别鸣谢" in sh.text_frame.text for sh in s.shapes)][0]
new = prs.slides.add_slide(prs.slide_layouts[0])
for sh in list(new.shapes):
    sh._element.getparent().remove(sh._element)
build_section(new, "04", "致谢", "致谢", "特别鸣谢", "十五人同行，共燃一盏灯")

lst = prs.slides._sldIdLst
sldIds = list(lst)
moved = sldIds[-1]
lst.remove(moved)
lst.insert(idx_thx, moved)
print("插入致谢标题页 → P%d" % (idx_thx + 1))

sl = list(prs.slides)
print("页数:", len(sl))

# ---- ③ 大目录提亮 + ④ 页码重算 ----
toc = sl[3]
COLOR = {
    "目录": WHITE,
    "CONTENTS": GOLD2,
    "FOUR CHAPTERS · ONE STORY": GOLD2,
    "微光成炬 · 星火自有燎原时": WHITE,
    "一 场 关 于 坚 守 的 讲 述": RGBColor(0xFF, 0xDE, 0xB0),
    "一张书桌": WHITE, "一条邮路": WHITE, "一场奔赴": WHITE, "一路同行": WHITE,
    "微光 · 韩雅平": GOLD2, "成炬 · 陈新超": GOLD2, "燎原 · 微光成炬": GOLD2, "致谢 · 谢谢聆听": GOLD2,
    "三间平房 · 28 张奖状": PALE, "旧货车 · 1700 个日夜": PALE,
    "两张答卷 · 同一种选择": PALE, "十五人 · 共燃一盏灯": PALE,
    "拾光者小组 · 十五人": GOLD2, "FROM SPARK TO FLAME": GOLD2,
}
for sh in toc.shapes:
    if not sh.has_text_frame:
        continue
    t = sh.text_frame.text.strip()
    col = COLOR.get(t)
    if col is None and t in ("01", "02", "03", "04"):
        col = GOLD2
    if col is None:
        continue
    for p in sh.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = col

# 底色改与章节页同一红
for sh in toc.shapes:
    if sh.width and abs(sh.width - prs.slide_width) < 30000 and abs(sh.height - prs.slide_height) < 30000:
        try:
            f = sh.fill
            f.gradient()
            st = f.gradient_stops
            st[0].color.rgb = RGBColor(0x8E, 0x00, 0x00); st[0].position = 0.0
            st[1].color.rgb = RGBColor(0xC0, 0x00, 0x00); st[1].position = 1.0
            f.gradient_angle = 45.0
        except Exception as e:
            print("底色跳过:", e)


def page_of(kw, last=False):
    hits = [i for i, s in enumerate(sl) if i != 3 and
            any(sh.has_text_frame and kw in sh.text_frame.text for sh in s.shapes)]
    return (hits[-1] if last else hits[0]) + 1


p1 = page_of("PART 01 · 寒门筑梦")
p2 = page_of("PART 02 · 高山邮路")
p3 = page_of("PART 03 · 燎原")
p4 = page_of("PART 04 · 致谢")
last_thx = page_of("FROM SPARK TO FLAME", last=True)
ranges = [(p1, p2 - 1), (p2, p3 - 1), (p3, p3 + 1), (p4, last_thx)]
labels = ["一张书桌", "一条邮路", "一场奔赴", "一路同行"]
for lb, (a, b) in zip(labels, ranges):
    txt = f"P{a:02d}" if a == b else f"P{a:02d}—{b:02d}"
    print(lb, "→", txt)

# 按列顺序写回四个页码框（左起）
pbox = [sh for sh in toc.shapes
        if sh.has_text_frame and sh.text_frame.text.strip().startswith("P")
        and len(sh.text_frame.text.strip()) <= 7]
pbox.sort(key=lambda x: x.left)
for sh, (a, b) in zip(pbox, ranges):
    t = f"P{a:02d}" if a == b else f"P{a:02d}—{b:02d}"
    for p in sh.text_frame.paragraphs:
        for r in p.runs:
            r.text = t
    print("写回", t)

NOTE = ("全片 10 分钟节奏表（控场参考）：P1 片头 5 秒｜P2-P3 封面 10 秒｜P4 大目录 20 秒｜"
        "P5 团队分工 35 秒｜P6-P10 微光 · 韩雅平 3 分 00 秒（含 34 秒采访视频）｜"
        "P11-P16 成炬 · 陈新超 4 分 00 秒（含 2 分 46 秒纪实视频）｜P17-P18 燎原 · 尾声 40 秒｜"
        "P19-P22 致谢 20 秒。党员风采（3 分 18 秒，P16）为机动页，超时直接跳过。")
try:
    runs = sl[1].notes_slide.notes_text_frame.paragraphs[0].runs
    for r in runs[1:]:
        r._r.getparent().remove(r._r)
    runs[0].text = NOTE
    print("备注已更新")
except Exception as e:
    print("备注跳过:", e)

prs.save(F)
print("saved")
