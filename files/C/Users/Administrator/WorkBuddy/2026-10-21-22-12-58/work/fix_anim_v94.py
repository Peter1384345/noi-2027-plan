# -*- coding: utf-8 -*-
"""v9.4：按新形状结构重排 P20 / P21 动画，并全片审计未入动画的形状"""
import sys
from lxml import etree
from pptx import Presentation
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')
F = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v9）.pptx"
prs = Presentation(F)
sl = list(prs.slides)


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


# ---- P20（sl[19]）：背景+标题 / 左栏(含金线15060) / 右栏(含金线15061) / 底部结语 ----
g20 = [
    [8051, 8052, 8053, 8054, 8055],
    [8056, 8057, 8058, 8059, 8060, 15060],
    [8061, 8062, 8063, 8064, 8065, 15061],
    [8066, 8067, 8068, 8069],
]
apply(sl[19], g20, base=100)

# ---- P21（sl[20]）：背景+标题 / 三张卡 / 底部两行 / 小结带(带+红条+文字) ----
g21 = [
    [186, 187, 188, 189],
    [190, 191, 192, 193, 194],
    [195, 196, 197, 198, 199],
    [200, 201, 202, 203, 204],
    [205, 206, 207],
    [8066, 8067, 8068],
]
apply(sl[20], g21, base=200)

prs.save(F)
print('已重写 P20 / P21 动画并保存。')

# ---- 全片审计：形状 id 是否都被 timing 覆盖 ----
prs2 = Presentation(F)
print('\n=== 未入动画的形状（全片） ===')
for i, s in enumerate(prs2.slides, 1):
    sld = s._element
    tim = sld.find(qn('p:timing'))
    shape_ids = {sh.shape_id for sh in s.shapes}
    if tim is None:
        if shape_ids:
            print(f'P{i:02d}: 无 timing，形状 {len(shape_ids)} 个全部未覆盖')
        continue
    covered = {int(e.get('spid')) for e in tim.iter(qn('p:spTgt'))}
    miss = shape_ids - covered
    if miss:
        print(f'P{i:02d}: 未覆盖 {sorted(miss)}')
print('审计完成。')
