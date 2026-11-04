# -*- coding: utf-8 -*-
"""v10-4c：精准移除 tnLst/tmRoot 层的 python-pptx 媒体节点，保留 mainSeq 内自动播放节点"""
import sys
from pptx import Presentation
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')
F = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v10）.pptx"
prs = Presentation(F)


def ancestors(el, stop):
    out, node = [], el
    while True:
        node = node.getparent()
        if node is None or node is stop:
            return out
        out.append(node.tag.split('}')[-1])


for pno in (4, 11):
    s = list(prs.slides)[pno - 1]
    tim = s._element.find(qn('p:timing'))
    vids = list(tim.iter(qn('p:video')))
    print(f'--- P{pno:02d} 节点 {len(vids)} 个')
    for v in vids:
        chain = ancestors(v, tim)
        if 'seq' not in chain:
            v.getparent().remove(v)
            print('    移除 tmRoot 层节点（祖先链: %s）' % '/'.join(chain))
    vids = list(tim.iter(qn('p:video')))
    assert len(vids) == 1, f'P{pno} 剩余 {len(vids)} 个'
    v = vids[0]
    mctn = v.find(qn('p:cMediaNode')).find(qn('p:cTn'))
    cond = mctn.find(qn('p:stCondLst')).find(qn('p:cond'))
    cond.set('delay', '0')
    cond.set('evt', 'onBegin')
    mctn.set('repeatCount', 'indefinite')
    spid = v.find(qn('p:cMediaNode')).find(qn('p:tgtEl')).find(qn('p:spTgt')).get('spid')
    tmRoot = tim.find(qn('p:tnLst')).find(qn('p:par'))
    seq_cnt = len(tmRoot.findall('.//' + qn('p:seq')))
    print(f'    ✓ 保留 spid={spid} | delay=0 evt=onBegin repeatCount=indefinite | seq 数={seq_cnt}')

prs.save(F)
print('已保存')
