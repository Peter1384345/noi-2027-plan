# -*- coding: utf-8 -*-
"""把开场视频作为新的一页插到封面之后（第 3 页），另存为新版本"""
from pptx import Presentation
from pptx.util import Emu
from lxml import etree
import hashlib

BASE = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_目录改版.pptx"
DST = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_新版本.pptx"
VIDEO = r"C:\Users\Administrator\WorkBuddy\2026-10-25-20-27-24\videos\开场_微光成炬_16x9.mp4"
POSTER = r"C:\Users\Administrator\WorkBuddy\2026-10-25-20-27-24\photos\poster_opening.jpg"

prs = Presentation(BASE)

# 选一个占位符最少的版式
layout = min(prs.slide_layouts, key=lambda l: len(l.placeholders))
print("use layout:", layout.name, len(layout.placeholders))
slide = prs.slides.add_slide(layout)
for sh in list(slide.shapes):
    sh._element.getparent().remove(sh._element)

movie = slide.shapes.add_movie(
    VIDEO, Emu(0), Emu(0), Emu(prs.slide_width), Emu(prs.slide_height),
    poster_frame_image=POSTER, mime_type="video/mp4")
print("movie shape id", movie.shape_id, movie.name)

# 移到第 3 页（封面两页之后）
sldIdLst = prs.slides._sldIdLst
ids = list(sldIdLst)
sldIdLst.remove(ids[-1])
sldIdLst.insert(2, ids[-1])

# 演讲者备注
try:
    tf = slide.notes_slide.notes_text_frame
    if tf is not None:
        tf.text = "开场片头（约 5 秒）：画面自动播放一次，先不说话，让火星走完再翻到目录页。"
        print("notes ok")
    else:
        print("notes 占位符缺失，跳过")
except Exception as e:
    print("notes skip:", e)

prs.save(DST)
print("saved", DST)

# ---- 复核 ----
pa = Presentation(BASE)
pb = Presentation(DST)
print("页数:", len(pa.slides), "->", len(pb.slides))
for i in (0, 1):
    ha = hashlib.md5(pa.slides[i]._element.xml.encode()).hexdigest()
    hb = hashlib.md5(pb.slides[i]._element.xml.encode()).hexdigest()
    print(f"P{i+1}: {'一致' if ha == hb else '不一致!!'}")
for i in range(16, 19):
    ha = hashlib.md5(pa.slides[i]._element.xml.encode()).hexdigest()
    hb = hashlib.md5(pb.slides[i + 1]._element.xml.encode()).hexdigest()
    print(f"原P{i+1} -> 新P{i+2}: {'一致' if ha == hb else '不一致!!'}")
for i, s in enumerate(pb.slides[:5], 1):
    txt = " / ".join(sh.text_frame.text.replace("\n", " ") for sh in s.shapes
                     if sh.has_text_frame and sh.text_frame.text.strip())[:70]
    mv = [sh for sh in s.shapes if sh.shape_type == 16]
    print(f"新P{i}: shapes={len(s.shapes)} movie={len(mv)} {txt}")
