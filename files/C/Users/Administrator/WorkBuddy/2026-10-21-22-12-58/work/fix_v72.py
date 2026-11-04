# -*- coding: utf-8 -*-
"""v7.2：修 P17 文本框长度溢出；N3 时间轴改为「先行后列」阅读顺序"""
import sys, copy
from lxml import etree
from pptx import Presentation
from pptx.oxml.ns import qn
from pptx.util import Emu

sys.stdout.reconfigure(encoding='utf-8')
SRC = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v7.1）.pptx"
DST = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v7）.pptx"
EMU = 914400
prs = Presentation(SRC)


def find_shape(slide, needle):
    for sh in slide.shapes:
        if sh.has_text_frame and needle in sh.text_frame.text:
            return sh
    return None


def set_single(sh, text):
    txBody = sh.text_frame._txBody
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
    t.text = text


print('=== 1. P17 里程句缩短到单行 ===')
s = list(prs.slides)[16]
sh = find_shape(s, '近五年，这辆车跟着她')
if sh:
    set_single(sh, '五年 20 多万公里，绕赤道 5 圈')
    print('  →', sh.text_frame.text.strip(), f'(盒宽 {sh.width/EMU:.2f}in)')

print('\n=== 2. N3 时间轴改行序 ===')
s = list(prs.slides)[14]
TIMES = ['05:00', '06:20', '07:00', '10:00', '午后', '傍晚']
# 现有位置（列优先）→ 目标位置（行优先）
COLS, ROWS = (0.56, 6.72), (2.30, 3.48, 4.66)
CW, CH = 6.05, 1.05

cards = []
for i, t in enumerate(TIMES):
    lb = find_shape(s, t)
    if lb is None:
        print(f'  ! 未找到 {t}')
        continue
    # 卡片锚点 = 该时间标签所在卡片左上角（标签在 x+0.26, y+0.24）
    ox, oy = lb.left / EMU - 0.26, lb.top / EMU - 0.24
    cards.append((t, ox, oy))

for i, (t, ox, oy) in enumerate(cards):
    nx, ny = COLS[i % 2], ROWS[i // 2]
    dx, dy = nx - ox, ny - oy
    if abs(dx) < 1e-6 and abs(dy) < 1e-6:
        print(f'  {t}: 无需移动')
        continue
    moved = 0
    for shp in s.shapes:
        if shp.left is None or shp.top is None:
            continue
        x, y = shp.left / EMU, shp.top / EMU
        # 落在旧卡片范围内才移动（含卡片本体、竖条、文字）
        if ox - 0.06 <= x <= ox + CW + 0.06 and oy - 0.06 <= y <= oy + CH + 0.06:
            shp.left = Emu(int((x + dx) * EMU))
            shp.top = Emu(int((y + dy) * EMU))
            moved += 1
    print(f'  {t}: ({ox:.2f},{oy:.2f}) → ({nx:.2f},{ny:.2f})  移动 {moved} 形状')

print('\n=== 3. 校验 N3 阅读顺序 ===')
for sh in s.shapes:
    if sh.has_text_frame:
        t = sh.text_frame.text.strip()
        if t in TIMES:
            print(f'  {t:<6} x={sh.left/EMU:5.2f} y={sh.top/EMU:5.2f}')

prs.save(DST)
print(f'\n已保存：{DST}')
