# -*- coding: utf-8 -*-
"""估算文本框是否溢出（按宽度/字号推算每行字数）"""
import sys, re, unicodedata
from pptx import Presentation
sys.stdout.reconfigure(encoding='utf-8')

F = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v11）.pptx"
prs = Presentation(F)
EMU = 914400


def width_units(s):
    """中文/全角按 1.0，半角按 0.5"""
    w = 0.0
    for ch in s:
        w += 1.0 if unicodedata.east_asian_width(ch) in ('W', 'F') else 0.55
    return w


print(f'{"页":<5}{"形状":<14}{"盒宽":>6}{"盒高":>6}{"字号":>6}{"需求行":>7}{"可容行":>7}  状态  文本')
issues = []
for i, s in enumerate(prs.slides, 1):
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        txt = sh.text_frame.text.strip()
        if not txt:
            continue
        w_in = sh.width / EMU
        h_in = sh.height / EMU
        # 取首个 run 字号（pt）
        sz = 12.0
        for p in sh.text_frame.paragraphs:
            if p.runs and p.runs[0].font.size:
                sz = p.runs[0].font.size.pt
                break
        # 每行可容纳的"字宽单位"
        per_line = max(1.0, (w_in * 72.0) / sz)
        need = 0
        for para in sh.text_frame.paragraphs:
            t = para.text
            if not t:
                need += 0.5
                continue
            need += max(1, -(-width_units(t) // per_line))
        avail = max(1.0, (h_in * 72.0) / (sz * 1.45))
        bad = need > avail + 0.4
        if bad:
            issues.append((i, sh.name, w_in, h_in, sz, need, avail, txt[:46]))
        print(f'P{i:<4}{sh.name[:13]:<14}{w_in:>6.2f}{h_in:>6.2f}{sz:>6.0f}{need:>7.1f}{avail:>7.1f}  {"溢出!" if bad else "ok":<5}{txt[:40]}')

print('\n=== 疑似溢出 ===')
for it in issues:
    print(f'  P{it[0]:02d} {it[1]} 盒{it[2]:.2f}x{it[3]:.2f}in {it[4]:.0f}pt 需{it[5]:.1f}行/容{it[6]:.1f}行 → {it[7]}')
if not issues:
    print('  无')
