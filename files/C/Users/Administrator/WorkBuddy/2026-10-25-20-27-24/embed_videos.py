# -*- coding: utf-8 -*-
"""向《微光成炬》PPT 嵌入 3 个视频页（复制原页底版保持风格），并做少量文字修改。"""
import copy, os, shutil, sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from PIL import Image, ImageDraw, ImageFont

SRC = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时.pptx"
BAK = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_原始备份.pptx"
VID_DIR = r"C:\Users\Administrator\WorkBuddy\2026-10-25-20-27-24\videos"
GOLD = RGBColor(0xE8, 0xC8, 0x7A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GRAY = RGBColor(0xCC, 0xCC, 0xCC)

# ---------- 备份 ----------
if not os.path.exists(BAK):
    shutil.copy2(SRC, BAK)
    print("backup ->", BAK)

prs = Presentation(SRC)
N = len(prs.slides)
assert N == 15, f"unexpected slide count {N}"

# ---------- 生成视频封面图 ----------
def poster(text, out):
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), (24, 22, 26))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 640, W, H], fill=(60, 40, 34))
    try:
        f1 = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 56)
        f2 = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 30)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    d.text((W // 2, 300), text, font=f1, fill=(232, 200, 122), anchor="mm")
    d.text((W // 2, 390), "点击画面播放", font=f2, fill=(220, 220, 220), anchor="mm")
    # play button
    cx, cy, r = W // 2, 520, 44
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(232, 200, 122), width=5)
    d.polygon([(cx - 14, cy - 24), (cx - 14, cy + 24), (cx + 26, cy)], fill=(232, 200, 122))
    img.save(out)

p_a = os.path.join(VID_DIR, "poster_a.png")
p_b = os.path.join(VID_DIR, "poster_b.png")
p_c = os.path.join(VID_DIR, "poster_c.png")
poster("韩雅平 · 699 分清华采访", p_a)
poster("陈新超 · 乡邮路上的铁娘子", p_b)
poster("陈新超 · 党员风采", p_c)

# ---------- 复制页面 ----------
def duplicate_slide(prs, source):
    dest = prs.slides.add_slide(source.slide_layout)
    for sh in list(dest.shapes):
        sh._element.getparent().remove(sh._element)
    rid_map = {}
    for rid, rel in source.part.rels.items():
        if rel.is_external:
            continue
        rt = rel.reltype
        if rt.endswith("/image") or rt.endswith("/media") or rt.endswith("/video"):
            rid_map[rid] = dest.part.relate_to(rel.target_part, rt)
    src_tree = source.shapes._spTree
    dst_tree = dest.shapes._spTree
    for child in src_tree:
        tag = child.tag
        if tag.endswith("}nvGrpSpPr") or tag.endswith("}grpSpPr"):
            continue
        dst_tree.append(copy.deepcopy(child))
    for el in dst_tree.iter():
        for k, v in list(el.attrib.items()):
            if (k.endswith("}embed") or k.endswith("}link") or k.endswith("}id")) and v in rid_map:
                el.set(k, rid_map[v])
    return dest

def delete_from(shape_list, keep_idx):
    for j in sorted(set(range(len(shape_list))) - set(keep_idx), reverse=True):
        el = shape_list[j]._element
        el.getparent().remove(el)

def set_header(sh, text):
    tf = sh.text_frame
    p = tf.paragraphs[0]
    runs = p.runs
    if runs:
        runs[0].text = text
        for r in runs[1:]:
            r._r.getparent().remove(r._r)
    else:
        p.add_run().text = text

def add_text(slide, x, y, w, h, lines, size=12.5, color=WHITE, bold=False, align=PP_ALIGN.LEFT, spacing=1.15):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        p.space_after = Pt(6)
        r = p.add_run()
        r.text = line
        r.font.name = "微软雅黑"
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
    return tb

slides = list(prs.slides)
s7 = slides[6]   # 韩雅平 699 页（版式底版 A）
s11 = slides[10] # 陈新超 1700+ 页（版式底版 B/C）

# ---------- 页 A：韩雅平视频页 ----------
A = duplicate_slide(prs, s7)
shp = list(A.shapes)          # 复制后顺序同 s7
delete_from(shp, keep_idx={0, 1, 2, 3})   # 保留背景/右图/渐变/栏目标头
add_text(A, 0.62, 0.95, 6.2, 0.6, ["视频 · 60 秒看见雅平"], size=24, bold=True)
add_text(A, 0.63, 1.52, 6.2, 0.3, ["河南广电《小莉帮忙》采访 · 人民日报转载"], size=11.5, color=GOLD)
A.shapes.add_movie(os.path.join(VID_DIR, "韩雅平_699分清华采访_小莉帮忙.mp4"),
                   Inches(0.55), Inches(2.05), Inches(5.95), Inches(3.35),
                   poster_frame_image=p_a, mime_type="video/mp4")
add_text(A, 0.55, 5.62, 6.1, 1.7, [
    "“知识改变命运，我要通过学习改变家庭现状，一定会让父母过上好日子。”",
    "“不吃学习的苦，就要吃生活的苦；当达到一定的高度，才能更好地掌控手机。”",
    "“学到哭也不放弃。”"],
    size=12.5, color=WHITE)

# ---------- 页 B：陈新超视频页（新时代的我们） ----------
B = duplicate_slide(prs, s11)
shp = list(B.shapes)
header_b = shp[3]
delete_from(shp, keep_idx={0, 1, 2, 3})
set_header(header_b, "PART 02 · 高山邮路 · 视频纪实")
add_text(B, 0.62, 0.95, 6.2, 0.6, ["视频 · 乡邮路上的“铁娘子”"], size=24, bold=True)
add_text(B, 0.63, 1.52, 6.2, 0.3, ["湖北广电《新时代的我们》专栏纪实"], size=11.5, color=GOLD)
B.shapes.add_movie(os.path.join(VID_DIR, "陈新超_新时代的我们_荆楚楷模_高清.mp4"),
                   Inches(0.55), Inches(2.05), Inches(5.95), Inches(3.35),
                   poster_frame_image=p_b, mime_type="video/mp4")
add_text(B, 0.55, 5.62, 6.2, 1.7, [
    "1 个人 · 1 辆旧货车 · 1700 多天 · 20 多万公里 · 10 个村 · 2.3 万群众",
    "“只要身体允许，我就会一直做下去。”",
    "2026 年第一批“中国好人榜”候选人 · “荆楚楷模”"],
    size=12.5, color=WHITE)

# ---------- 页 C：陈新超党员风采视频页 ----------
C = duplicate_slide(prs, s11)
shp = list(C.shapes)
header_c = shp[3]
delete_from(shp, keep_idx={0, 1, 2, 3})
set_header(header_c, "PART 02 · 高山邮路 · 党员风采")
add_text(C, 0.62, 0.95, 6.2, 0.6, ["视频 · 党员风采：一颗爱心走邮路"], size=24, bold=True)
add_text(C, 0.63, 1.52, 6.2, 0.3, ["黄石市广播电视台《领航》专栏"], size=11.5, color=GOLD)
C.shapes.add_movie(os.path.join(VID_DIR, "陈新超_党员风采_一颗爱心走邮路_黄石台.mp4"),
                   Inches(0.55), Inches(2.05), Inches(5.95), Inches(3.35),
                   poster_frame_image=p_c, mime_type="video/mp4")
add_text(C, 0.55, 5.62, 6.2, 1.7, [
    "2010 年确诊肝癌早期，为省费用自学注射干扰素，与病魔抗争十余载",
    "2022 年成为阳新首个快递行业党支部里唯一的女党员",
    "“我是党员，应该做榜样。”"],
    size=12.5, color=WHITE)

# ---------- 调整页序 ----------
sldIdLst = prs.slides._sldIdLst
ids = list(sldIdLst)                     # 0..14 原页, 15=A, 16=B, 17=C
order = ids[0:7] + [ids[15]] + ids[7:10] + [ids[16], ids[17]] + ids[10:15]
for el in order:
    sldIdLst.remove(el)
for el in order:
    sldIdLst.append(el)

# ---------- 保存 ----------
try:
    prs.save(SRC)
    out = SRC
except PermissionError:
    out = SRC.replace(".pptx", "_嵌入视频版.pptx")
    prs.save(out)
    print("原文件被占用，另存为:", out)
print("saved:", out)
print("total slides:", len(prs.slides))
