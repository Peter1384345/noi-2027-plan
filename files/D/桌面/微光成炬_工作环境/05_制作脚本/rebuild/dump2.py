import sys; sys.stdout.reconfigure(encoding='utf-8')
from pptx import Presentation
from pptx.oxml.ns import qn
from pptx.util import Emu
from lxml import etree
prs=Presentation(r'D:/桌面/微光成炬_工作环境/01_初代版本/微光成炬-星火自有燎原时_小组原始版.pptx')
def col_of(rPr):
    c=rPr.find(qn('a:solidFill'))
    if c is None: return None
    sc=c.find(qn('a:srgbClr'))
    if sc is None: return None
    return sc.get('val')
def fill_of(sp):
    if sp is None: return 'none'
    sf=sp.find(qn('a:solidFill'))
    if sf is not None:
        sc=sf.find(qn('a:srgbClr'))
        a=sc.find(qn('a:alpha')) if sc is not None else None
        return 'solid#%s@%s'%(sc.get('val') if sc is not None else '?', a.get('val') if a is not None else '100000')
    gf=sp.find(qn('a:gradFill'))
    if gf is not None:
        stops=[(gs.get('pos'),gs.find(qn('a:srgbClr')).get('val')) for gs in gf.findall('.//'+qn('a:gs')) if gs.find(qn('a:srgbClr')) is not None]
        return 'grad'+str(stops)
    bf=sp.find(qn('a:blipFill'))
    if bf is not None:
        bl=bf.find(qn('a:blip'))
        return 'blip#'+bl.get(qn('r:embed'))
    return 'none'
for idx in [0,1,2,4,6,7,10,11,12,13]:
    s=prs.slides[idx]
    print('\n========== PAGE %d =========='%(idx+1))
    for sh in s.shapes:
        L,T,Wd,Hh=[(v/914400 if v is not None else 0) for v in (sh.left,sh.top,sh.width,sh.height)]
        sp=sh._element.spPr
        f=fill_of(sp)
        kind=sh.shape_type
        txt=''
        if sh.has_text_frame:
            txt=' | '.join(p.text for p in sh.text_frame.paragraphs if p.text.strip())
        print('  [%s] L%.2f T%.2f W%.2f H%.2f  fill=%s'%(sh.name,L,T,Wd,Hh,f))
        if sh.has_text_frame and txt:
            for p in sh.text_frame.paragraphs:
                if not p.runs: 
                    if p.text.strip(): print('     P:',repr(p.text))
                    continue
                for r in p.runs:
                    rPr=r._r.get_or_add_rPr()
                    sz=rPr.find(qn('a:sz'))
                    spc=rPr.find(qn('a:spc'))
                    b=rPr.find(qn('a:b'))
                    print('     run %-22r font=%-10s sz=%s col=%s spc=%s bold=%s'%(r.text[:18], r.font.name, sz.get('val') if sz is not None else '?', col_of(rPr), spc.get('val') if spc is not None else '-', b is not None))
