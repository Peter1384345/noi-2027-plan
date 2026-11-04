# -*- coding: utf-8 -*-
"""检查 P05/P13 章节页背景结构，以及 P09 现有视频的 timing 写法"""
import sys
from pptx import Presentation
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')
F = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v9）.pptx"
prs = Presentation(F)
sl = list(prs.slides)

for pno in (5, 13):
    s = sl[pno - 1]
    sld = s._element
    bg = sld.find(qn('p:cSld')).find(qn('p:bg'))
    print(f'=== P{pno:02d}  background 元素: {"有 p:bg" if bg is not None else "无（用版式背景）"}')
    if bg is not None:
        print('   ', etree_str := __import__('lxml.etree', fromlist=['tostring']).tostring(bg).decode()[:300])
    for i, sh in enumerate(s.shapes):
        fill = ''
        try:
            if sh.fill.type is not None and str(sh.fill.type) == 'MSO_FILL_TYPE.SOLID (1)':
                fill = f' solid={sh.fill.fore_color.rgb}'
        except Exception:
            pass
        print(f'  {i:2d} id={sh.shape_id:<4} {sh.left/914400:5.2f},{sh.top/914400:5.2f} '
              f'{sh.width/914400:5.2f}x{sh.height/914400:5.2f}{fill}')

print('\n=== P09 timing 中含 media 的片段 ===')
tim = sl[8]._element.find(qn('p:timing'))
from lxml import etree
xml = etree.tostring(tim).decode()
for tag in ('p:video', 'p:audio'):
    import re
    for m in re.finditer(f'<{tag}[ >].*?</{tag}>', xml, re.S):
        print(m.group(0)[:900], '\n---')
