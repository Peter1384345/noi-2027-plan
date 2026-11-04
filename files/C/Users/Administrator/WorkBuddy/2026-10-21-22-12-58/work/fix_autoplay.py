# -*- coding: utf-8 -*-
"""v10-4：修正 P04/P11 媒体节点重复——只保留一个，改为自动播放 + 循环"""
import sys
from pptx import Presentation
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')
F = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v10）.pptx"
prs = Presentation(F)

for pno in (4, 11):
    s = list(prs.slides)[pno - 1]
    tim = s._element.find(qn('p:timing'))
    vids = list(tim.iter(qn('p:video')))
    print(f'--- P{pno:02d} 媒体节点数: {len(vids)}')
    if len(vids) > 1:
        # 删除我手工插入的那个外层 par（其 stCondLst delay="0"）
        for v in vids:
            par = v.getparent().getparent().getparent()   # p:par
            cond = par.find(qn('p:stCondLst')).find(qn('p:cond'))
            if cond is not None and cond.get('delay') == '0':
                par.getparent().remove(par)
                print('    已移除手工插入的重复节点')
                break
        vids = list(tim.iter(qn('p:video')))
    # 剩下的唯一节点：delay=0 + 循环
    v = vids[0]
    media_ctn = v.find(qn('p:cMediaNode')).find(qn('p:cTn'))
    cond = media_ctn.find(qn('p:stCondLst')).find(qn('p:cond'))
    cond.set('delay', '0')
    cond.set('evt', 'onBegin')
    media_ctn.set('repeatCount', 'indefinite')
    spid = v.find(qn('p:cMediaNode')).find(qn('p:tgtEl')).find(qn('p:spTgt')).get('spid')
    print(f'    唯一节点 → spid={spid}  delay=0 evt=onBegin  repeatCount=indefinite  节点数={len(list(tim.iter(qn("p:video"))))}')

prs.save(F)
print('已保存修正')
