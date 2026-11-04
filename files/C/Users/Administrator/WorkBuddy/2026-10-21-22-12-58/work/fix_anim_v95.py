# -*- coding: utf-8 -*-
"""v9.5：P18 整页动画重排（补齐 v6 遗留缺陷）+ 各页未覆盖形状性质速查"""
import sys
from lxml import etree
from pptx import Presentation
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')
F = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v9）.pptx"
prs = Presentation(F)
sl = list(prs.slides)

# ---- 速查其他页未覆盖形状是什么 ----
CHECK = {8: [3], 9: [2], 10: [2], 11: [25], 12: [48], 13: [71, 72, 73],
         14: [81, 83, 114], 16: [116], 17: [141, 142, 143, 144], 19: [3]}
print('=== 未覆盖形状速查 ===')
for pno, ids in CHECK.items():
    s = sl[pno - 1]
    for sh in s.shapes:
        if sh.shape_id in ids:
            t = sh.text_frame.text.strip().replace('\n', '/')[:26] if sh.has_text_frame else '(无文字)'
            print(f'P{pno:02d} id={sh.shape_id:<4} x={sh.left/914400:5.2f} y={sh.top/914400:5.2f} '
                  f'w={sh.width/914400:5.2f} h={sh.height/914400:5.3f} {t}')


def _fade(nid, sid, delay=0):
    return (f'<p:par><p:cTn id="{nid}" presetID="10" presetClass="entr" presetSubtype="0" '
            f'fill="hold" grpId="0" nodeType="withEffect">'
            f'<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst><p:childTnLst>'
            f'<p:set><p:cBhvr><p:cTn id="{nid+1}" dur="1" fill="hold">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl>'
            f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:to><p:strVal val="visible"/></p:to></p:set>'
            f'<p:animEffect transition="in" filter="fade"><p:cBhvr>'
            f'<p:cTn id="{nid+2}" dur="550"/>'
            f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl></p:cBhvr></p:animEffect>'
            f'</p:childTnLst></p:cTn></p:par>')


def apply(slide, groups, base):
    nid, blocks = base, []
    for gi, grp in enumerate(groups):
        inner = []
        for k, sid in enumerate(grp):
            nid += 3
            inner.append(_fade(nid, sid, 0 if k == 0 else 150))
        body = ''.join(inner)
        if gi == 0:
            blocks.append('<p:par><p:cTn fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
                          '<p:childTnLst><p:par><p:cTn fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                          f'<p:childTnLst>{body}</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>')
        else:
            blocks.append('<p:par><p:cTn fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
                          f'<p:childTnLst>{body}</p:childTnLst></p:cTn></p:par>')
    xml = ('<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
           'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
           f'<p:tnLst><p:par><p:cTn id="{base-2}" dur="indefinite" restart="never" nodeType="tmRoot">'
           '<p:childTnLst><p:seq concurrent="1" nextAc="seek">'
           f'<p:cTn id="{base-1}" dur="indefinite" nodeType="mainSeq"><p:childTnLst>{"".join(blocks)}</p:childTnLst></p:cTn>'
           '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
           '</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')
    sld = slide._element
    old = sld.find(qn('p:timing'))
    if old is not None:
        sld.remove(old)
    sld.append(etree.fromstring(xml))


# ---- P18（sl[17]）：全 19 个形状入组，按「照片两行 + 右侧叙事列 + 红带」节奏 ----
g18 = [
    [151, 155],               # 背景 + 栏目标题
    [152, 153],               # 照片第一行
    [8004, 8005],             # 照片第二行
    [156, 157, 158],          # 「铁娘子的一天」标题块
    [159, 160],               # 金点 + 引语一
    [161, 162],               # 金点 + 引语二
    [8006, 8007],             # 金点 + 第三条图注（v9.2 新增）
    [163, 164, 165],          # 红带底板 + 竖条 + 红带文字
    [154],                    # 来源署名
]
apply(sl[17], g18, base=300)

prs.save(F)
print('\nP18 动画已整页重排（9 组，19 形状全覆盖），已保存。')

# ---- 复审计 ----
prs2 = Presentation(F)
print('\n=== 复审计（仅列仍有未覆盖的页） ===')
for i, s in enumerate(prs2.slides, 1):
    tim = s._element.find(qn('p:timing'))
    shape_ids = {sh.shape_id for sh in s.shapes}
    if tim is None:
        if shape_ids:
            print(f'P{i:02d}: 无 timing（形状 {len(shape_ids)} 个）')
        continue
    covered = {int(e.get('spid')) for e in tim.iter(qn('p:spTgt'))}
    miss = shape_ids - covered
    if miss:
        print(f'P{i:02d}: 未覆盖 {sorted(miss)}')
print('审计完成。')
