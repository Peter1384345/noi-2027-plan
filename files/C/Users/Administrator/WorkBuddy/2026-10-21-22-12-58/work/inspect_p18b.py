# -*- coding: utf-8 -*-
"""检查 P18 的组合形状与 timing 节点规模；对比 v6 对应页"""
import sys
from pptx import Presentation
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')
F = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v9）.pptx"
prs = Presentation(F)
s = list(prs.slides)[17]
sld = s._element

# 是否有 grpSp
grps = sld.findall('.//' + qn('p:grpSp'))
print(f'P18 组合形状数量: {len(grps)}')

tim = sld.find(qn('p:timing'))
sets = tim.findall('.//' + qn('p:set'))
effects = tim.findall('.//' + qn('p:animEffect'))
tgts = tim.findall('.//' + qn('p:spTgt'))
print(f'P18 timing: set={len(sets)} animEffect={len(effects)} spTgt={len(tgts)}')
print('覆盖 spid:', sorted({int(e.get("spid")) for e in tgts}))

# 对比 v6 同位置页：找含「铁娘子的一天」的页
import glob
for f6 in [r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/work/微光成炬-星火自有燎原时（终版·v6）.pptx"]:
    p6 = Presentation(f6)
    for i, ss in enumerate(p6.slides, 1):
        txt = ' '.join(sh.text_frame.text for sh in ss.shapes if sh.has_text_frame)
        if '铁娘子' in txt:
            t6 = ss._element.find(qn('p:timing'))
            n6 = len(t6.findall('.//' + qn('p:animEffect'))) if t6 is not None else 0
            c6 = sorted({int(e.get('spid')) for e in t6.iter(qn('p:spTgt'))}) if t6 is not None else []
            ids6 = [sh.shape_id for sh in ss.shapes]
            print(f'\nv6 P{i:02d}（含铁娘子）: animEffect={n6}')
            print('  v6 覆盖 spid:', c6)
            print('  v6 形状 ids :', ids6)
            print('  v6 未覆盖   :', sorted(set(ids6) - set(c6)))
