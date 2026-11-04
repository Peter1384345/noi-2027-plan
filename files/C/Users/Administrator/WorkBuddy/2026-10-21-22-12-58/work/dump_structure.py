# -*- coding: utf-8 -*-
"""dump 全片结构：每页形状、文字、视频、动画规模"""
import sys
from pptx import Presentation
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')
F = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v9）.pptx"
prs = Presentation(F)

for i, s in enumerate(prs.slides, 1):
    tim = s._element.find(qn('p:timing'))
    n_anim = len(tim.findall('.//' + qn('p:animEffect'))) if tim is not None else 0
    vids = []
    texts = []
    for sh in s.shapes:
        if sh.shape_type == 16 or sh.__class__.__name__ == 'Movie':
            vids.append(sh.shape_id)
        if sh.has_text_frame:
            t = sh.text_frame.text.strip().replace('\n', ' / ')
            if t:
                texts.append(t)
    head = texts[1] if len(texts) > 1 else (texts[0] if texts else '')
    print(f'--- P{i:02d}  动画节点={n_anim:3d}  视频={vids}')
    for t in texts[:6]:
        print(f'    {t[:60]}')
    if len(texts) > 6:
        print(f'    …共 {len(texts)} 个文本框')
