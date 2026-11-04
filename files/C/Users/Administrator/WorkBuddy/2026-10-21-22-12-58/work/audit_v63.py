# -*- coding: utf-8 -*-
"""v6.3 体检：逐页文案 + 全档配色频次 + 重复句扫描"""
import re, zipfile, collections, sys, io
from pptx import Presentation

sys.stdout.reconfigure(encoding='utf-8')
SRC = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v6）.pptx"

prs = Presentation(SRC)

print("=" * 70)
print("【一】逐页文案清单")
print("=" * 70)
all_text = []
for i, slide in enumerate(prs.slides, 1):
    lines = []
    for sh in slide.shapes:
        if sh.has_text_frame:
            t = sh.text_frame.text.strip()
            if t:
                lines += [x.strip() for x in t.split("\n") if x.strip()]
        if sh.has_table:
            for row in sh.table.rows:
                for c in row.cells:
                    t = c.text.strip()
                    if t:
                        lines.append(t)
    all_text.append((i, lines))
    print(f"\n--- P{i:02d} ({len(lines)} 段) ---")
    for l in lines:
        print("   ", l)

print()
print("=" * 70)
print("【二】重复文案扫描（跨页完全相同/高度相似）")
print("=" * 70)
norm = {}
for i, lines in all_text:
    for l in lines:
        k = re.sub(r"[\s，。、：；！？“”\"'（）()·\-—]", "", l)
        if len(k) >= 6:
            norm.setdefault(k, []).append(i)
dups = {k: v for k, v in norm.items() if len(v) > 1}
if not dups:
    print("未发现跨页完全重复（>=6字）")
for k, v in sorted(dups.items(), key=lambda x: -len(x[0])):
    print(f"  ×{len(v)} 页{v}: {k[:60]}")

print()
print("=" * 70)
print("【三】全档配色频次")
print("=" * 70)
z = zipfile.ZipFile(SRC)
cnt = collections.Counter()
per_slide = {}
for n in z.namelist():
    if not (n.startswith("ppt/slides/slide") and n.endswith(".xml")):
        continue
    s = z.read(n).decode("utf-8")
    cols = re.findall(r'val="([0-9A-Fa-f]{6})"', s)
    c = collections.Counter(cols)
    per_slide[n] = c
    cnt.update(cols)

print(f"{'色值':<10}{'全档':>6}   出现页")
for col, n in cnt.most_common(30):
    pages = ",".join(sorted({re.search(r"slide(\d+)", k).group(1) for k, v in per_slide.items() if v.get(col)}))
    print(f"#{col:<9}{n:>6}   P{pages}")
