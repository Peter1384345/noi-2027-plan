# -*- coding: utf-8 -*-
"""从原版重建复件：copy -> 15页备注 -> 插入6页视频插页(原版配色) -> 补插页备注 -> 校验。"""
import ast
import os
import shutil
import subprocess
import sys

BASE = r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27"
SRC = r"E:\Backup\Documents\xwechat_files\wxid_3pal96859htk12_1bbd\msg\file\2026-09\微光成炬-星火自有燎原时(1).pptx"
PPTX = os.path.join(BASE, "微光成炬-星火自有燎原时-复件.pptx")
OUT = os.path.join(BASE, "output")
PY = r"C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe"
PYLIBS = os.path.join(OUT, "pylibs")
LOG = os.path.join(OUT, "rebuild_all_log.txt")

lines = []

# 1) 从原版重建复件
if os.path.exists(PPTX):
    os.chmod(PPTX, 0o666)
    os.remove(PPTX)
shutil.copyfile(SRC, PPTX)
os.chmod(PPTX, 0o666)
lines.append(f"copy ok size={os.path.getsize(PPTX)}")

# 2) 提取 write_notes.py 的 NOTES
src = open(os.path.join(OUT, "write_notes.py"), encoding="utf-8").read()
tree = ast.parse(src)
NOTES = None
for node in tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "NOTES":
        NOTES = ast.literal_eval(node.value)
assert NOTES and len(NOTES) == 15, f"NOTES={len(NOTES) if NOTES else 0}"

# 3) 写 15 页备注（ntf 或 XML 兜底）
from pptx import Presentation
from pptx.oxml import parse_xml

NS = ('xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"')


def notes_sp_xml(shape_id, text):
    paras = "".join(
        f'<a:p><a:r><a:rPr lang="zh-CN" altLang="en-US" dirty="0"/><a:t>{line}</a:t></a:r></a:p>'
        for line in text.split("\n")
    )
    return (
        f"<p:sp {NS}>"
        f'<p:nvSpPr><p:cNvPr id="{shape_id}" name="Notes Placeholder {shape_id}"/>'
        f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
        f'<p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr>'
        f'<p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>{paras}</p:txBody></p:sp>'
    )


prs = Presentation(PPTX)
sid = 800
n_ok = 0
for i, text in enumerate(NOTES):
    slide = prs.slides[i]
    ns = slide.notes_slide
    ntf = ns.notes_text_frame
    if ntf is not None:
        ntf.text = text
        how = "ntf"
    else:
        sp = parse_xml(notes_sp_xml(sid, text))
        sid += 1
        ns.shapes._spTree.append(sp)
        how = "xml"
    n_ok += 1
lines.append(f"notes15 ok={n_ok} (last={how})")
prs.save(PPTX)

# 4) 插入视频插页（insert_video_pages.py 内含删除旧插页逻辑，此时无旧插页）
env = {**os.environ, "PYTHONPATH": PYLIBS}
r = subprocess.run([PY, os.path.join(OUT, "insert_video_pages.py")], capture_output=True, env=env)
lines.append("insert rc=" + str(r.returncode))
if r.returncode != 0:
    lines.append((r.stderr or b"").decode("utf-8", "replace")[-600:])
else:
    # 5) 补写插页备注
    r2 = subprocess.run([PY, os.path.join(OUT, "fix_notes_xml.py")], capture_output=True, env=env)
    lines.append("fixnotes rc=" + str(r2.returncode))
    if r2.returncode != 0:
        lines.append((r2.stderr or b"").decode("utf-8", "replace")[-400:])

# 6) 最终校验
prs2 = Presentation(PPTX)
lines.append(f"final_slides={len(prs2.slides)}")
vp = 0
for i, s in enumerate(prs2.slides):
    for shp in s.shapes:
        if shp.has_text_frame and "视频插页" in shp.text_frame.text:
            vp += 1
            break
lines.append(f"video_pages={vp}")
notes_ok = 0
for s in prs2.slides:
    if s.has_notes_slide and s.notes_slide.notes_text_frame is not None and s.notes_slide.notes_text_frame.text.strip():
        notes_ok += 1
lines.append(f"slides_with_notes={notes_ok}")
lines.append(f"final_size={os.path.getsize(PPTX)}")

with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("DONE")
