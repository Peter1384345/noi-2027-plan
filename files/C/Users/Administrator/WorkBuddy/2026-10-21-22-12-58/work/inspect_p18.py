# -*- coding: utf-8 -*-
"""定位 P18 新增形状（金点 + 第三条图注）的 id 与覆盖情况"""
import sys
from pptx import Presentation
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')
F = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v9）.pptx"
prs = Presentation(F)
s = list(prs.slides)[17]
tim = s._element.find(qn('p:timing'))
covered = {int(e.get('spid')) for e in tim.iter(qn('p:spTgt'))}

for i, sh in enumerate(s.shapes):
    t = sh.text_frame.text.strip().replace('\n', '/')[:30] if sh.has_text_frame else ''
    mark = '✓' if sh.shape_id in covered else '✗'
    print(f'{mark} {i:2d} id={sh.shape_id:<5} x={sh.left/914400:5.2f} y={sh.top/914400:5.2f} '
          f'w={sh.width/914400:5.2f} h={sh.height/914400:5.3f} {t}')
