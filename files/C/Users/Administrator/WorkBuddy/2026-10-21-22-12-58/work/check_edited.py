# -*- coding: utf-8 -*-
"""检查被我改写的页面是否有多段残留"""
import sys
from pptx import Presentation
sys.stdout.reconfigure(encoding='utf-8')
p = Presentation(r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v7）.pptx")
for idx in [5, 8, 14, 15, 16, 20]:
    s = list(p.slides)[idx]
    print(f'\n===== P{idx+1:02d} =====')
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        ps = sh.text_frame.paragraphs
        txts = [pp.text.strip() for pp in ps if pp.text.strip()]
        if len(txts) > 1:
            print(f'  [{sh.name}] {len(txts)} 段:')
            for t in txts:
                print(f'      · {t[:78]}')
