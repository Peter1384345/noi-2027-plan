# -*- coding: utf-8 -*-
"""末次修订：P17 里程句压到单行"""
import sys, copy
from lxml import etree
from pptx import Presentation
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')
F = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v7）.pptx"
prs = Presentation(F)

s = list(prs.slides)[16]
hit = None
for sh in s.shapes:
    if sh.has_text_frame and '近五年，这辆车跟着她' in sh.text_frame.text:
        hit = sh
        break
if hit is None:
    print('未找到目标文本框')
    sys.exit(1)

txBody = hit.text_frame._txBody
ps = txBody.findall(qn('a:p'))
pPr = copy.deepcopy(ps[0].find(qn('a:pPr'))) if ps[0].find(qn('a:pPr')) is not None else None
rPr_tpl = None
for p in ps:
    r = p.find(qn('a:r'))
    if r is not None and r.find(qn('a:rPr')) is not None:
        rPr_tpl = copy.deepcopy(r.find(qn('a:rPr')))
        break
for p in ps:
    txBody.remove(p)
p = etree.SubElement(txBody, qn('a:p'))
if pPr is not None:
    p.append(pPr)
r = etree.SubElement(p, qn('a:r'))
if rPr_tpl is not None:
    r.append(rPr_tpl)
t = etree.SubElement(r, qn('a:t'))
t.text = '五年 20 多万公里，绕赤道 5 圈'

print('P17 →', hit.text_frame.text.strip(), f'| 盒宽 {hit.width/914400:.2f}in')
prs.save(F)
print('已保存')
