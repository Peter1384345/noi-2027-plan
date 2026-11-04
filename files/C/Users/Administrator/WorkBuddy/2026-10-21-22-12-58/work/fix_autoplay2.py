# -*- coding: utf-8 -*-
"""v10-4b：删除 tnLst 层非法媒体节点，保留 mainSeq 内的自动播放节点"""
import sys
from pptx import Presentation
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')
F = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v10）.pptx"
prs = Presentation(F)

for pno in (4, 11):
    s = list(prs.slides)[pno - 1]
    tim = s._element.find(qn('p:timing'))
    print(f'--- P{pno:02d}  初始媒体节点 {len(list(tim.iter(qn("p:video"))))} 个')
    for v in list(tim.iter(qn('p:video'))):
        par = v.getparent().getparent().getparent()      # p:par
        if par.getparent().tag == qn('p:tnLst'):
            par.getparent().remove(par)
            print('    已删除 tnLst 下的非标准节点（python-pptx 生成）')
            break
    vids = list(tim.iter(qn('p:video')))
    assert len(vids) == 1, f'P{pno} 节点数异常: {len(vids)}'
    v = vids[0]
    mctn = v.find(qn('p:cMediaNode')).find(qn('p:cTn'))
    cond = mctn.find(qn('p:stCondLst')).find(qn('p:cond'))
    cond.set('delay', '0')
    cond.set('evt', 'onBegin')
    mctn.set('repeatCount', 'indefinite')
    spid = v.find(qn('p:cMediaNode')).find(qn('p:tgtEl')).find(qn('p:spTgt')).get('spid')
    # tnLst 只应有一个 par（tmRoot）
    print(f'    保留节点 spid={spid}  自动播放(delay=0/onBegin)  循环(repeatCount=indefinite)  '
          f'tnLst 直接 par 数={len(tim.find(qn("p:tnLst")).findall(qn("p:par")))}')

prs.save(F)
print('已保存')
