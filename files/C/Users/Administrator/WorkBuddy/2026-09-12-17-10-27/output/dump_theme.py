# -*- coding: utf-8 -*-
"""提取原版 PPT 主题配色：theme1.xml 色板 + 各页背景/主要形状填充/文字颜色/字体。"""
import os
import re
import zipfile
from collections import Counter

from pptx import Presentation
from pptx.util import Pt

SRC = r"E:\Backup\Documents\xwechat_files\wxid_3pal96859htk12_1bbd\msg\file\2026-09\微光成炬-星火自有燎原时(1).pptx"
LOG = r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27\output\theme_dump.txt"

lines = []

# 1) theme1.xml 色板
with zipfile.ZipFile(SRC) as z:
    names = [n for n in z.namelist() if re.match(r"ppt/theme/theme\d+\.xml", n)]
    for n in sorted(names):
        xml = z.read(n).decode("utf-8", "replace")
        m = re.search(r"<a:clrScheme[^>]*>(.*?)</a:clrScheme>", xml, re.S)
        if m:
            seg = m.group(1)
            pairs = re.findall(r"<a:(\w+)>\s*<a:(?:srgbClr val=\"([0-9A-Fa-f]{6})\"|sysClr[^>]*lastClr=\"([0-9A-Fa-f]{6})\")", seg)
            lines.append(f"[{n}] " + ", ".join(f"{k}={v1 or v2}" for k, v1, v2 in pairs))
        fonts = re.findall(r"<a:(?:latin|ea) typeface=\"([^\"]+)\"", xml)
        lines.append(f"[{n}] fonts: {list(dict.fromkeys(fonts))[:6]}")

def color_of(el, tag):
    """从 shape xml 中找 solidFill 颜色"""
    import lxml.etree as etree
    ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
          "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
    sp = el._element
    # spPr 下的 solidFill
    fills = sp.findall(f".//{{{ns['p']}}}" + "spPr", namespaces=None) or []
    return None

from pptx.oxml.ns import qn

def shape_fill_color(shp):
    sp = shp._element
    spPr = sp.find(qn("p:spPr"))
    if spPr is None:
        return None
    sf = spPr.find(qn("a:solidFill"))
    if sf is None:
        return None
    srgb = sf.find(qn("a:srgbClr"))
    if srgb is not None:
        return "#" + srgb.get("val")
    scheme = sf.find(qn("a:schemeClr"))
    if scheme is not None:
        return "scheme:" + scheme.get("val")
    return None

def bg_of_slide(slide):
    bg = slide.background
    try:
        fill = bg.fill
        if fill.type is not None and str(fill.type) == "MSO_FILL_TYPE.SOLID (1)" or (fill.type is not None and int(fill.type) == 1):
            c = fill.fore_color
            if c.type is not None and "SCHEME" in str(c.type):
                return "scheme:" + str(c.theme_color)
            return "#" + str(c.rgb)
    except Exception:
        pass
    return None

prs = Presentation(SRC)
for i, slide in enumerate(prs.slides):
    bgs = bg_of_slide(slide)
    fills = []
    texts = []
    fonts = []
    for shp in slide.shapes:
        fc = shape_fill_color(shp)
        if fc and fc not in ("scheme:bg1",):
            fills.append(fc)
        if shp.has_text_frame:
            for p in shp.text_frame.paragraphs:
                for r in p.runs:
                    col = None
                    try:
                        if r.font.color and r.font.color.type is not None:
                            if "SCHEME" in str(r.font.color.type):
                                col = "scheme:" + str(r.font.color.theme_color)
                            else:
                                col = "#" + str(r.font.color.rgb)
                    except Exception:
                        pass
                    sz = r.font.size.pt if r.font.size else None
                    texts.append((col, sz, r.font.name, r.text[:12]))
                    if r.font.name:
                        fonts.append(r.font.name)
    lines.append(f"--- slide[{i+1}] bg={bgs} fills={Counter(fills).most_common(4)} fonts={Counter(fonts).most_common(2)}")
    for t in texts[:4]:
        lines.append(f"    text {t}")

with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("DONE")
