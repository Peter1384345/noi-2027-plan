# -*- coding: utf-8 -*-
"""直接在 XML 层向 6 页视频插页的 notes slide 添加 body 占位符并写入备注文本。"""
import json
import os
from xml.sax.saxutils import escape

from pptx import Presentation
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsmap

BASE = r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27"
PPTX = os.path.join(BASE, "微光成炬-星火自有燎原时-复件.pptx")
FALLBACK = os.path.join(BASE, "output", "video_page_notes_fallback.json")
LOG = os.path.join(BASE, "output", "fix_notes_xml_log.txt")

NS = ('xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"')


def notes_sp_xml(shape_id, text):
    paras = "".join(
        f"<a:p><a:r><a:rPr lang=\"zh-CN\" altLang=\"en-US\" dirty=\"0\"/><a:t>{escape(line)}</a:t></a:r></a:p>"
        for line in text.split("\n")
    )
    return (
        f"<p:sp {NS}>"
        f"<p:nvSpPr>"
        f"<p:cNvPr id=\"{shape_id}\" name=\"Notes Placeholder {shape_id}\"/>"
        f"<p:cNvSpPr><a:spLocks noGrp=\"1\"/></p:cNvSpPr>"
        f"<p:nvPr><p:ph type=\"body\" idx=\"1\"/></p:nvPr>"
        f"</p:nvSpPr>"
        f"<p:spPr/>"
        f"<p:txBody><a:bodyPr/><a:lstStyle/>{paras}</p:txBody>"
        f"</p:sp>"
    )


with open(FALLBACK, encoding="utf-8") as f:
    items = json.load(f)

prs = Presentation(PPTX)
lines = [f"slides={len(prs.slides)}"]
sid = 900
ok = 0
for it in items:
    slide = prs.slides[it["page_index"]]
    ns = slide.notes_slide
    ntf = ns.notes_text_frame
    if ntf is not None:
        ntf.text = it["text"]
        how = "ntf"
    else:
        sp = parse_xml(notes_sp_xml(sid, it["text"]))
        sid += 1
        ns.shapes._spTree.append(sp)
        how = "xml"
    ok += 1
    lines.append(f"page[{it['page_index']}] ok via {how}")

prs.save(PPTX)
lines.append(f"saved ok={ok}/{len(items)} size={os.path.getsize(PPTX)}")

# 复核
prs2 = Presentation(PPTX)
found = []
for it in items:
    s = prs2.slides[it["page_index"]]
    if s.has_notes_slide:
        t = s.notes_slide.notes_text_frame.text if s.notes_slide.notes_text_frame else ""
        found.append(f"page[{it['page_index']}] len={len(t)}")
lines.append("verify: " + "; ".join(found))

with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("DONE")
