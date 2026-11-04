# -*- coding: utf-8 -*-
"""v9.3：按新形状结构重排 P20 / P21 动画，避免装饰件提前露出"""
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


print('=== P20 形状顺序 ===')
s20 = sl[19]
ids20 = []
for i, sh in enumerate(s20.shapes):
    t = ''
    if sh.has_text_frame:
        t = sh.text_frame.text.strip().replace('\n', '/')[:24]
    print(f'  {i:2d} id={sh.shape_id:<5} h={sh.height/914400:5.3f} w={sh.width/914400:5.2f} {t}')
    ids20.append(sh.shape_id)

print('\n=== P21 形状顺序 ===')
s21 = sl[20]
ids21 = []
for i, sh in enumerate(s21.shapes):
    t = ''
    if sh.has_text_frame:
        t = sh.text_frame.text.strip().replace('\n', '/')[:24]
    print(f'  {i:2d} id={sh.shape_id:<5} h={sh.height/914400:5.3f} w={sh.width/914400:5.2f} {t}')
    ids21.append(sh.shape_id)
