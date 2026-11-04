# -*- coding: utf-8 -*-
"""v10-1：减页 25→20，P17 补零钱盒细节，全局修页码"""
import sys, shutil
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from lxml import etree

sys.stdout.reconfigure(encoding='utf-8')
BASE = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58"
SRC = BASE + r"/微光成炬-星火自有燎原时（终版·v9）.pptx"
DST = BASE + r"/微光成炬-星火自有燎原时（终版·v10）.pptx"
shutil.copyfile(SRC, DST)

prs = Presentation(DST)

# ---------- 1. P17 补「零钱盒」细节（18pt + 第三段） ----------
s17 = list(prs.slides)[16]
box = None
for sh in s17.shapes:
    if sh.shape_id == 147:
        box = sh
        break
if box is None:
    raise SystemExit('未找到 P17 正文框 147')

for p in box.text_frame.paragraphs:
    for r in p.runs:
        r.font.size = Pt(18)
# 复用末段段落属性，追加第三段
txBody = box.text_frame._txBody
last_p = txBody.findall(qn('a:p'))[-1]
new_p = etree.fromstring(etree.tostring(last_p))
for r in new_p.findall(qn('a:r')):
    new_p.remove(r)
r = etree.SubElement(new_p, qn('a:r'))
rPr_src = last_p.find(qn('a:r')).find(qn('a:rPr'))
r.append(etree.fromstring(etree.tostring(rPr_src)))
etree.SubElement(r, qn('a:t')).text = '车上常备一个零钱盒，老人搭公交不用找零'
txBody.append(new_p)
print('P17 已补第三段（零钱盒）并降到 18pt')

# ---------- 2. 删页：P24(23) P23(22) P19(18) P10(9) P02(1) ----------
sldIdLst = prs.slides._sldIdLst
before = len(sldIdLst)
for idx in (23, 22, 18, 9, 1):
    sldId = list(sldIdLst)[idx]
    rId = sldId.get(qn('r:id'))
    sldIdLst.remove(sldId)
    prs.part.drop_rel(rId)
print(f'已删除 5 页：{before} → {len(sldIdLst)}')

# ---------- 3. 全局修页码 ----------
import re
n = len(sldIdLst)
fixed = 0
for i, s in enumerate(prs.slides, 1):
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                t = r.text
                m = re.search(r'\d+\s*/\s*25', t)
                if m:
                    r.text = t[:m.start()] + f'{i:02d} / {n}' + t[m.end():]
                    fixed += 1
                    print(f'  页码 P{i:02d}: {t.strip()} → {r.text.strip()}')
print(f'共修 {fixed} 处页码')

prs.save(DST)
print('已保存 v10')
