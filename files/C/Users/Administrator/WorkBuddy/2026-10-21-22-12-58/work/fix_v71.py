# -*- coding: utf-8 -*-
"""v7.1：修复溢出与段落残留、时间轴改行序、卡片充实、视频页节奏拉开"""
import sys, copy
from lxml import etree
from pptx import Presentation
from pptx.oxml.ns import qn
from pptx.util import Emu

sys.stdout.reconfigure(encoding='utf-8')
SRC = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v7）.pptx"
DST = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v7.1）.pptx"

prs = Presentation(SRC)
EMU = 914400


def find_shape(slide, needle):
    for sh in slide.shapes:
        if sh.has_text_frame and needle in sh.text_frame.text:
            return sh
    return None


def set_single(sh, text):
    """清空全部段落，只留一段（沿用首段 pPr 与首个 run 的 rPr）"""
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


print('=== 1. 修 P17 数据页段落残留 ===')
s = list(prs.slides)[16]
sh = find_shape(s, '第一次开车')
if sh:
    set_single(sh, '第一次开车，40 公里开了 2 个多小时，安全到家后放声大哭')
    print('  已清残留 →', sh.text_frame.text)

print('\n=== 2. 修 P14 陈新超人物页文字溢出（3段→2段） ===')
s = list(prs.slides)[13]
sh = find_shape(s, '一辆手动挡的二手厢式货车')
if sh:
    txBody = sh.text_frame._txBody
    ps = txBody.findall(qn('a:p'))
    pPr = copy.deepcopy(ps[0].find(qn('a:pPr')))
    rPr_tpl = copy.deepcopy(ps[0].find(qn('a:r')).find(qn('a:rPr')))
    for p in ps:
        txBody.remove(p)
    PARAS = [
        '她身高不足 1 米 6，却能把 50 公斤的化肥咬牙扛上肩。一辆手动挡的二手货车，没有空调——夏天像蒸笼，冬天手脚冻得发硬。',
        '2012 年查出肝癌早期。她红着眼眶说出接下快递点的原因——"为了挣钱治病。"每月四针干扰素，为省注射费，她跟医生学会了给自己打针。',
    ]
    for txt in PARAS:
        p = etree.SubElement(txBody, qn('a:p'))
        p.append(copy.deepcopy(pPr))
        r = etree.SubElement(p, qn('a:r'))
        r.append(copy.deepcopy(rPr_tpl))
        t = etree.SubElement(r, qn('a:t'))
        t.text = txt
    print(f'  已改为 {len(PARAS)} 段')

print('\n=== 3. 视频页左侧三块节奏拉开 ===')
ROW_DEF = [(1.80, 3.20, 0.06), (3.20, 4.55, 0.25), (4.55, 6.20, 0.44)]
for idx in (8, 10, 11):
    s = list(prs.slides)[idx]
    moved = 0
    for shp in s.shapes:
        if shp.top is None or shp.left is None:
            continue
        top_in = shp.top / EMU
        if shp.left / EMU > 7.0:
            continue
        for lo, hi, dy in ROW_DEF:
            if lo <= top_in < hi:
                shp.top = Emu(int(shp.top + dy * EMU))
                moved += 1
                break
    print(f'  P{idx+1:02d} 位移 {moved} 个形状')

print('\n=== 4. N1 她的学法 —— 卡片补第二句，填满版面 ===')
s = list(prs.slides)[7]
EXTRA = {
    '新课先自己过一遍': '新课先自己过一遍，带着问题进课堂——听课时心里有靶心。这个习惯，她从初中一直保持到高三。',
    '当天的知识点当天弄懂': '当天的知识点当天弄懂，绝不把问题留到第二天。实在弄不明白，第二天一早就去问老师。',
    '错题本按题型分类': '错题本按题型分类，错一次记一次，考前只翻这一本。三年下来，攒了厚厚一摞。',
    '每周回头过一遍': '每周回头过一遍，薄弱的地方单独再挑出来刷一遍。重复，是最笨也最稳的办法。',
}
n = 0
for k, v in EXTRA.items():
    sh = find_shape(s, k)
    if sh:
        set_single(sh, v)
        n += 1
print(f'  已补写 {n} 张卡片')

prs.save(DST)
print(f'\n已保存：{DST}')
