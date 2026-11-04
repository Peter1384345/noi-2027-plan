# -*- coding: utf-8 -*-
"""向《微光成炬》复件 PPT 的 6 个视频位嵌入占位卡图片（python-pptx 兜底）。"""
import os
from pptx import Presentation
from pptx.util import Pt

BASE = r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27"
PPTX = os.path.join(BASE, "微光成炬-星火自有燎原时-复件.pptx")
POSTERS = os.path.join(BASE, "output", "videos", "posters")
LOG = os.path.join(BASE, "output", "embed_log.txt")

# (slide_index 0-based, V编号, x, y, w, h) 单位 pt
SLOTS = [
    (4,  "V1", 620, 170, 300, 169),
    (6,  "V2", 610, 330, 310, 174),
    (7,  "V3", 615, 175, 300, 169),
    (9,  "V4", 25,  340, 240, 135),
    (10, "V5", 620, 330, 300, 169),
    (11, "V6", 30,  415, 250, 141),
]

prs = Presentation(PPTX)
lines = [f"slides={len(prs.slides)}"]

ok = 0
for idx, vid, x, y, w, h in SLOTS:
    slide = prs.slides[idx]
    png = os.path.join(POSTERS, f"{vid}.png")
    pic = slide.shapes.add_picture(png, Pt(x), Pt(y), Pt(w), Pt(h))
    pic.name = f"VIDEO_PLACEHOLDER_{vid}"
    ok += 1
    lines.append(f"OK {vid} slide[{idx}] name={pic.name} pos=({x},{y}) size=({w}x{h})")

prs.save(PPTX)
lines.append(f"saved ok={ok}/6 size={os.path.getsize(PPTX)} bytes")

# 复核：重新打开数占位 shape
prs2 = Presentation(PPTX)
found = []
for i, s in enumerate(prs2.slides):
    for shp in s.shapes:
        if shp.name and shp.name.startswith("VIDEO_PLACEHOLDER_"):
            found.append(f"slide[{i}]:{shp.name}")
lines.append("verify: " + ("; ".join(found) if found else "NONE"))

with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("DONE")
