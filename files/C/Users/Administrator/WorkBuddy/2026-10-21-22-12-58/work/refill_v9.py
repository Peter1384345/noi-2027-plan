# -*- coding: utf-8 -*-
"""v9：让每一页看起来都充实 —— 重排 P20 主题页，加高 P15 卡片，放大 P18 照片，加厚 P21"""
import sys
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')
SRC = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v8）.pptx"
DST = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v9）.pptx"
EMU = 914400
FONT = '微软雅黑'
RED, RED_D, GOLD, GOLD_L = 'C00000', '8E0000', 'C9A227', 'E8C87A'
CREAM, WARM, WHITE = 'F7F4EE', 'F3EDDF', 'FFFFFF'
INK, BODY, SUB = '2A2826', '3A3A38', '8A8378'

prs = Presentation(SRC)
sl = list(prs.slides)


def IN(v):
    return Emu(int(round(v * EMU)))


def _ea(rPr):
    for tag in ('a:latin', 'a:ea'):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set('typeface', FONT)


def add_text(slide, x, y, w, h, text, size=11, color=BODY, bold=False,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=None):
    tb = slide.shapes.add_textbox(IN(x), IN(y), IN(w), IN(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    if spacing:
        p.line_spacing = spacing
    r = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = bold; r.font.name = FONT
    r.font.color.rgb = RGBColor.from_string(color)
    _ea(r._r.get_or_add_rPr())
    return tb


def add_rect(slide, x, y, w, h, color):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, IN(x), IN(y), IN(w), IN(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = RGBColor.from_string(color)
    sp.line.fill.background(); sp.shadow.inherit = False
    return sp


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


def apply_timing(slide, groups, base=15000):
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


def clear(slide):
    spTree = slide.shapes._spTree
    n = 0
    for el in list(spTree):
        if el.tag in (qn('p:sp'), qn('p:pic'), qn('p:graphicFrame'), qn('p:grpSp'), qn('p:cxnSp')):
            spTree.remove(el); n += 1
    return n


# ============================================================
print('=== 重建 P20 主题页：双栏对比面板铺满版面 ===')
s20 = sl[19]
print('  清除旧形状', clear(s20))

G = []
G.append([add_rect(s20, 0, 0, 13.333, 7.5, CREAM).shape_id])

k = add_rect(s20, 0.56, 0.56, 3.06, 0.31, RED)
kl = add_text(s20, 0.56, 0.56, 3.06, 0.31, 'THEME · 本期主题', size=11, color=WHITE,
              bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
tt = add_text(s20, 0.56, 0.95, 8.4, 0.60, '高山不语，涓流不息', size=28, color=INK, bold=True)
sb = add_text(s20, 8.60, 1.22, 4.18, 0.26, 'HIGH MOUNTAINS · LONG STREAMS',
              size=10, color=GOLD, align=PP_ALIGN.RIGHT)
G.append([k.shape_id, kl.shape_id, tt.shape_id, sb.shape_id])

PANELS = [
    # (x, fill, no_color, ttl_color, body_color, stat_color, no, ttl, body, stat)
    (0.56, RED_D, GOLD_L, WHITE, WHITE, GOLD_L, '01', '「高山」· 一个人的高度',
     '陈新超把一条邮路，走成了乡亲们的山——山不挪步，风雨不动。她扛起的不只是四百个包裹，是十个村、两万三千人的日常。抗洪她第一个上，环卫她第一个到。',
     '1700 天 · 10 个村 · 2.3 万人'),
    (6.90, WHITE, GOLD, RED_D, BODY, RED, '02', '「涓流」· 一滴水的长度',
     '韩雅平用十二年，把一滴水穿成了河——水不争先，滴水穿石。她攒下的不只是二十八张奖状，是一间平房里不肯熄灭的灯。那盏灯，照着她走出平房，也照着身后的人。',
     '699 分 · 28 张奖状 · 12 年'),
]
PY, PW, PH = 1.95, 5.88, 3.55
for x, fill, nc, tc, bc, sc, no, ttl, body, stat in PANELS:
    g = []
    g.append(add_rect(s20, x, PY, PW, PH, fill).shape_id)
    g.append(add_text(s20, x + 0.38, PY + 0.28, 1.0, 0.50, no, size=26, color=nc, bold=True).shape_id)
    g.append(add_text(s20, x + 0.38, PY + 0.98, 5.12, 0.34, ttl, size=17, color=tc, bold=True).shape_id)
    g.append(add_text(s20, x + 0.38, PY + 1.50, 5.12, 1.55, body, size=11, color=bc, spacing=1.55).shape_id)
    g.append(add_text(s20, x + 0.38, PY + 3.02, 5.12, 0.30, stat, size=10.5, color=sc, bold=True).shape_id)
    G.append(g)
    print(f'  面板 {no} 建立')

G.append([add_rect(s20, 0.56, 5.72, 12.22, 0.02, GOLD).shape_id])
l1 = add_text(s20, 0.56, 5.88, 12.22, 0.42, '高山是担当的高度，涓流是坚持的长度。', size=19, color=INK, bold=True)
G.append([l1.shape_id])
l2 = add_text(s20, 0.56, 6.40, 12.22, 0.36,
              '一个人站成山，一滴水汇成河——这就是我们想讲的「微光成炬」。', size=12, color=BODY)
l3 = add_text(s20, 0.56, 6.94, 12.22, 0.26,
              'THE 2026 YOUTH MARXIST TRAINING PROGRAM · 青马班主题汇报', size=9, color=GOLD)
G.append([l2.shape_id, l3.shape_id])
apply_timing(s20, G)
print('  动画重建完成')

# ============================================================
print('=== 重排 P15 时间轴：卡片加高铺到底 ===')
s15 = sl[14]
print('  清除旧形状', clear(s15))

G = [[add_rect(s15, 0, 0, 13.333, 7.5, CREAM).shape_id]]
k = add_rect(s15, 0.56, 0.56, 3.06, 0.31, RED)
kl = add_text(s15, 0.56, 0.56, 3.06, 0.31, 'ONE DAY · 一天的时间表', size=11, color=WHITE,
              bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
tt = add_text(s15, 0.56, 0.95, 8.4, 0.60, '铁娘子的一天', size=28, color=INK, bold=True)
sb = add_text(s15, 0.56, 1.67, 11.4, 0.28, 'A DAY ON THE ROAD · 湖北阳新县枫林镇水源村', size=10, color=SUB)
G.append([k.shape_id, kl.shape_id, tt.shape_id, sb.shape_id])

ITEMS = [
    ('05:00', '起床，喂鸡、给家人做早饭——这是一天里唯一属于她自己家的时间'),
    ('06:20', '开上那辆没有空调的二手货车出发——夏天像蒸笼，冬天手脚冻得发硬'),
    ('07:00', '到县城分拨中心，分拣、扫码、装车——她常常比工作人员到得还早'),
    ('10:00', '返回水源村快递点，卸货、分类、上架、通知取件——额头上的汗没干过'),
    ('午后', '骑三轮车，给行动不便的老人送货上门——子女寄回的年货，也一并捎到'),
    ('傍晚', '收车、对账，一天才算忙完——运的不只是快递，更是远方家人的牵挂'),
]
XS, YS, W, H = (0.56, 6.72), (2.30, 3.66, 5.02), 6.05, 1.30
for i, (tm, desc) in enumerate(ITEMS):
    x, y = XS[i % 2], YS[i // 2]
    g = []
    g.append(add_rect(s15, x, y, W, H, WHITE).shape_id)
    g.append(add_rect(s15, x, y, 0.05, H, GOLD).shape_id)
    g.append(add_text(s15, x + 0.26, y + 0.40, 1.10, 0.50, tm, size=17, color=GOLD, bold=True).shape_id)
    g.append(add_text(s15, x + 1.42, y + 0.26, 4.35, 0.78, desc, size=10.5, color=BODY,
                      spacing=1.45, anchor=MSO_ANCHOR.MIDDLE).shape_id)
    G.append(g)
q = add_text(s15, 0.56, 6.62, 12.22, 0.40, '忙起来顾不上吃饭，头晕了就赶紧剥颗糖含着。', size=11.5, color=SUB)
G.append([q.shape_id])
apply_timing(s15, G)
print('  6 格加高至 1.30in，动画重建')

# ============================================================
print('=== P18 照片墙：四张放大铺满左半区 ===')
s18 = sl[17]
POS = [(0.55, 1.58), (4.20, 1.58), (0.55, 3.96), (4.20, 3.96)]
i = 0
for sh in s18.shapes:
    if sh.shape_type == 13 and sh.name.startswith('yxtv_day'):
        sh.left, sh.top = IN(POS[i][0]), IN(POS[i][1])
        sh.width, sh.height = IN(3.55), IN(2.28)
        i += 1
print(f'  放大 {i} 张照片至 3.55×2.28in')
for sh in s18.shapes:
    if sh.has_text_frame and '影像取自阳新县融媒体中心' in sh.text_frame.text:
        sh.top = IN(6.42)

# ============================================================
print('=== P21 青马之问：三卡各补一句 ===')
s21 = sl[20]
import copy
def find(slide, needle):
    for sh in slide.shapes:
        if sh.has_text_frame and needle in sh.text_frame.text:
            return sh
    return None

def set_single(sh, text):
    txBody = sh.text_frame._txBody
    ps = txBody.findall(qn('a:p'))
    pPr = copy.deepcopy(ps[0].find(qn('a:pPr'))) if ps[0].find(qn('a:pPr')) is not None else None
    rPr = None
    for p in ps:
        r = p.find(qn('a:r'))
        if r is not None and r.find(qn('a:rPr')) is not None:
            rPr = copy.deepcopy(r.find(qn('a:rPr'))); break
    for p in ps:
        txBody.remove(p)
    p = etree.SubElement(txBody, qn('a:p'))
    if pPr is not None:
        p.append(pPr)
    r = etree.SubElement(p, qn('a:r'))
    if rPr is not None:
        r.append(rPr)
    etree.SubElement(r, qn('a:t')).text = text

for old, new in [
    ('陈新超的每一次出发', '陈新超的每一次出发，先想的都是"乡亲们还需要我"。十年邮路、两万乡亲，她把"人民"两个字，走成了一条具体的路。所谓立场，不在纸上，在走过的每一步里。'),
    ('韩雅平的错题本翻到卷边', '韩雅平的错题本翻到卷边，一道题弄不懂就不肯放过。所谓天赋，不过是把预习、消化、复盘这些小事，一天不落地做到底。真正的差距，从来不在天赋。'),
    ('我们问自己', '我们问自己：如果有一天有能力了，会不会也伸手拉一把身后的人？这道题，他俩已经替我们答了一半——剩下的，该我们写了。'),
]:
    sh = find(s21, old)
    if sh:
        set_single(sh, new); print('  ✓', old[:8])

prs.save(DST)
print(f'\n已保存：{DST}')
