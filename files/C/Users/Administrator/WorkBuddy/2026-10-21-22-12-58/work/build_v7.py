# -*- coding: utf-8 -*-
"""
v7：内容增补 + 语义去重 + 新增页动画 + 配色收敛回主题色板
- 严格保留原版页面的形状/动画（零改动）
- 仅改写我此前新增页（P08/09/10/15/16/17）与新页
"""
import sys, copy, re
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')

SRC = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v6）.pptx"
DST = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v7）.pptx"

# ============ 主题色板（全部取自原版，不引入新色） ============
RED     = 'C00000'   # 正红 · 星火
RED_D   = '8E0000'   # 深红 · 燎原
GOLD    = 'C9A227'   # 赤金
GOLD_L  = 'E8C87A'   # 柔金 · 微光
CREAM   = 'F7F4EE'   # 米白
WHITE   = 'FFFFFF'
INK     = '2A2826'   # 标题墨
BODY    = '3A3A38'   # 正文墨
SUB     = '8A8378'   # 辅助灰
FONT    = '微软雅黑'

# 我此前引入的杂色 → 原版色板
COLOR_MAP = {
    'A88016': 'C9A227',   # 暗橙 → 赤金
    '464440': '3A3A38',   # 冷灰 → 原版正文墨
    '1F2329': '2A2826',   # 冷蓝黑 → 原版标题墨
    '6E6A64': '8A8378',   # 冷灰 → 原版辅助灰
    '140000': '100000',   # 近黑 → 原版墨夜
    '150000': '100000',
}

prs = Presentation(SRC)
print(f'载入 {len(prs.slides)} 页')


# ---------------- 基础工具 ----------------
def IN(v):
    return Emu(int(round(v * 914400)))


def _set_ea(rPr, font):
    for tag in ('a:latin', 'a:ea'):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set('typeface', font)


def add_text(slide, x, y, w, h, text, size=11, color=BODY, bold=False,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=None,
             font=FONT, wrap=True):
    tb = slide.shapes.add_textbox(IN(x), IN(y), IN(w), IN(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.margin_left = 0; tf.margin_right = 0
    tf.margin_top = 0; tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    if spacing:
        p.line_spacing = spacing
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.name = font
    r.font.color.rgb = RGBColor.from_string(color)
    _set_ea(r._r.get_or_add_rPr(), font)
    return tb


def add_rect(slide, x, y, w, h, color, shape=MSO_SHAPE.RECTANGLE):
    sp = slide.shapes.add_shape(shape, IN(x), IN(y), IN(w), IN(h))
    sp.fill.solid()
    sp.fill.fore_color.rgb = RGBColor.from_string(color)
    sp.line.fill.background()
    sp.shadow.inherit = False
    if sp.has_text_frame:
        sp.text_frame.text = ''
    return sp


def add_bg(slide, color=CREAM):
    return add_rect(slide, 0, 0, 13.333, 7.5, color)


def add_kicker(slide, label, x=0.56, y=0.56, w=3.06):
    add_rect(slide, x, y, w, 0.31, RED)
    add_text(slide, x, y, w, 0.31, label, size=11, color=WHITE, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def add_title(slide, title, sub, x=0.56, y=0.95):
    add_text(slide, x, y, 8.4, 0.60, title, size=28, color=INK, bold=True)
    add_text(slide, x, y + 0.72, 11.4, 0.28, sub, size=10, color=SUB)


# ---------------- 动画：与原版一致的「出现 + 淡入」 ----------------
def _fade_item(nid, sid, delay=0):
    return (
        f'<p:par><p:cTn id="{nid}" presetID="10" presetClass="entr" presetSubtype="0" '
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
        f'</p:childTnLst></p:cTn></p:par>'
    )


def apply_fade_timing(slide, groups, base=7000):
    """groups: [[spid,...], ...] 每组一次单击，组内依次延迟出现"""
    if not groups:
        return
    nid = base
    blocks = []
    for gi, grp in enumerate(groups):
        inner = []
        for k, sid in enumerate(grp):
            nid += 3
            inner.append(_fade_item(nid, sid, delay=(0 if k == 0 else 150)))
        body = ''.join(inner)
        if gi == 0:  # 首次单击
            blocks.append(
                '<p:par><p:cTn fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
                '<p:childTnLst><p:par><p:cTn fill="hold">'
                '<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                f'<p:childTnLst>{body}</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
            )
        else:  # 之后每次单击
            blocks.append(
                '<p:par><p:cTn fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
                f'<p:childTnLst>{body}</p:childTnLst></p:cTn></p:par>'
            )
    xml = (
        f'<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        f'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        f'<p:tnLst><p:par><p:cTn id="{base-2}" dur="indefinite" restart="never" nodeType="tmRoot">'
        f'<p:childTnLst><p:seq concurrent="1" nextAc="seek">'
        f'<p:cTn id="{base-1}" dur="indefinite" nodeType="mainSeq">'
        f'<p:childTnLst>{"".join(blocks)}</p:childTnLst></p:cTn>'
        f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
        f'</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>'
    )
    sld = slide._element
    old = sld.find(qn('p:timing'))
    if old is not None:
        sld.remove(old)
    frag = etree.fromstring(xml)
    sld.append(frag)


# ---------------- 文本改写（保留原格式，重建 run） ----------------
def find_shape(slide, needle):
    for sh in slide.shapes:
        if sh.has_text_frame and needle in sh.text_frame.text:
            return sh
    return None


def rewrite(sh, paras, sz=1400, bold=True, body=BODY, accent=RED, lnspc='185000'):
    """paras: [[(text,colorOrNone),...], ...]"""
    txBody = sh.text_frame._txBody
    old_pPr = None
    for p in txBody.findall(qn('a:p')):
        pPr = p.find(qn('a:pPr'))
        if pPr is not None:
            old_pPr = copy.deepcopy(pPr)
            break
    for p in txBody.findall(qn('a:p')):
        txBody.remove(p)
    for runs in paras:
        p = etree.SubElement(txBody, qn('a:p'))
        if old_pPr is not None:
            p.append(copy.deepcopy(old_pPr))
        else:
            pPr = etree.SubElement(p, qn('a:pPr'))
            ln = etree.SubElement(pPr, qn('a:lnSpc'))
            pc = etree.SubElement(ln, qn('a:spcPct')); pc.set('val', lnspc)
        for text, col in runs:
            r = etree.SubElement(p, qn('a:r'))
            rPr = etree.SubElement(r, qn('a:rPr'))
            rPr.set('lang', 'zh-CN'); rPr.set('sz', str(sz))
            rPr.set('b', '1' if bold else '0'); rPr.set('dirty', '0')
            fill = etree.SubElement(rPr, qn('a:solidFill'))
            clr = etree.SubElement(fill, qn('a:srgbClr')); clr.set('val', col or body)
            _set_ea(rPr, FONT)
            t = etree.SubElement(r, qn('a:t')); t.text = text


def set_text(sh, text):
    """简单整体替换（单 run 文本框）"""
    ps = sh.text_frame.paragraphs
    p = ps[0]
    runs = p.runs
    if not runs:
        r = p.add_run(); r.text = text
        return
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


print('\n=== 一、语义去重 ===')

# --- P06 韩雅平人物页：把"顾虹12年"让给 P09，改讲生活与志向 ---
s6 = prs.slides[5]
sh = find_shape(s6, '三间平房，墙上贴满')
if sh:
    rewrite(sh, [
        [('三间平房，墙上贴满 ', None), ('28', RED),
         (' 张奖状。母亲患强直性脊柱炎，脊柱严重畸形，需长期服药；父亲务农，农闲时去工地打零工。', None)],
        [('住校六年，她只挑最便宜的饭菜，从不买零食，也从不和同学比吃穿——', None), ('"学生就该比学习"', RED), ('。', None)],
        [('2026 年，她被清华大学「卓越医师科学家」八年制录取。选医学，是因为她想治好母亲这样的病人。', None)],
    ])
    print('  P06 已改写（移除与 P09 重复的资助段）')

# --- P09 十二年之约：换表述，避免与 P06 旧句重合 ---
s9 = prs.slides[8]
sh = find_shape(s9, '浙江嘉善的顾虹阿姨资助她十二年')
if sh:
    set_text(sh, '从六岁那年，到高中毕业——浙江嘉善的顾虹阿姨，整整资助了她十二年。')
    print('  P09 「十二年之约」已换表述')

# --- P12 陈新超人物页：删去与 P13/P14 重复的荣誉句，补"为什么跑快递" ---
s12 = prs.slides[11]
sh = find_shape(s12, '每天清晨 5 点起床')
if sh:
    rewrite(sh, [
        [('一辆手动挡的二手厢式货车，没有空调。夏天驾驶室像蒸笼，冬天手脚冻得发硬——她开着它，在县城与水源村之间跑了五六年。', None)],
        [('2012 年，她被查出肝癌早期。后来她才红着眼眶说出接下快递点的原因——', None), ('"为了挣钱治病。"', RED)],
        [('每月四针干扰素，每针上千元。为省下注射费，她跟医生学会了自己打针，每次都扎得比医生更深，生怕药水漏掉一滴。', None)],
    ])
    print('  P12 已改写（移除与 P13/P14 重复的荣誉句）')

sh = find_shape(s12, '曾患肝癌，为省治疗费自学注射')
if sh is not None and sh is not find_shape(s12, '每天清晨 5 点起床'):
    sh._element.getparent().remove(sh._element)
    print('  P12 删除重复的"曾患肝癌…示范点"整段')

# --- P13 卡片04：去掉重复的"示范点"，专讲抗洪 ---
s13 = prs.slides[12]
sh = find_shape(s13, '2021 年网湖抗洪，她与男同志并肩扛沙袋')
if sh:
    set_text(sh, '2021 年网湖抗洪，她像男同志一样冲在前面：灌沙袋、堵漏点，夜里在堤上睡帐篷守夜。')
    print('  P13 卡片04 已改写')

# --- P14 数据页：去掉重复的抗洪，换成里程 ---
s14 = prs.slides[13]
sh = find_shape(s14, '2021 网湖抗洪')
if sh:
    set_text(sh, '近五年，这辆车跟着她跑了 20 多万公里，相当于绕赤道 5 圈')
    print('  P14 抗洪句 → 里程句')
sh = find_shape(s14, '第一次开车，40 公里开了 2 个多小时')
if sh:
    set_text(sh, '第一次开车，40 公里开了 2 个多小时，安全到家后放声大哭')
    print('  P14 首驾句已补细节')

# --- P17 卡片02：与 P16「二十八张奖状」去重，改讲方法 ---
s17 = prs.slides[16]
sh = find_shape(s17, '韩雅平的二十八张奖状')
if sh:
    set_text(sh, '韩雅平的错题本翻到卷边，一道题弄不懂就不肯放过——所谓天赋，不过是把小事做到底。')
    print('  P17 卡片02 已改写')


print('\n=== 二、新增 4 页 ===')
LAYOUT = prs.slide_masters[0].slide_layouts[0]


def new_slide():
    return prs.slides.add_slide(LAYOUT)


# ---------- NA 她的学法 ----------
def build_method():
    s = new_slide()
    g_all = []
    g_all.append([add_bg(s).shape_id])
    add_kicker(s, 'METHOD · 学习习惯')
    add_title(s, '她凭什么考出 699', 'HABITS · 把最普通的方法，做到极致')
    g_all.append([s.shapes[-3].shape_id, s.shapes[-2].shape_id, s.shapes[-1].shape_id])

    cards = [
        ('01', '提前预习', '新课先自己过一遍，带着问题进课堂——听课时心里有靶心。'),
        ('02', '当天消化', '当天的知识点当天弄懂，绝不把问题留到第二天。'),
        ('03', '错题归类', '错题本按题型分类，错一次记一次，考前只翻这一本。'),
        ('04', '定期复盘', '每周回头过一遍，薄弱的地方单独再挑出来刷一遍。'),
    ]
    xs, ys, W, H = (0.56, 6.72), (2.30, 4.20), 6.05, 1.72
    for i, (no, ttl, txt) in enumerate(cards):
        x, y = xs[i % 2], ys[i // 2]
        g = []
        g.append(add_rect(s, x, y, W, H, WHITE).shape_id)
        g.append(add_rect(s, x, y, 0.05, H, RED).shape_id)
        g.append(add_text(s, x + 0.26, y + 0.18, 0.75, 0.42, no, size=18, color=GOLD, bold=True).shape_id)
        g.append(add_text(s, x + 1.00, y + 0.20, 4.9, 0.30, ttl, size=13, color=RED, bold=True).shape_id)
        g.append(add_text(s, x + 1.00, y + 0.60, 4.85, 1.00, txt, size=10, color=BODY, spacing=1.45).shape_id)
        g_all.append(g)

    q = add_text(s, 0.56, 6.55, 12.22, 0.45,
                 '课本翻到卷边，错题本写满一本又一本——没有捷径，只有重复。',
                 size=11.5, color=SUB)
    g_all.append([q.shape_id])
    apply_fade_timing(s, g_all)
    print('  NA 她的学法 已建')


# ---------- NB 他们眼中的她 ----------
def build_voices():
    s = new_slide()
    g_all = [[add_bg(s).shape_id]]
    add_kicker(s, 'TEACHERS · 三位班主任')
    add_title(s, '他们眼中的她', 'IN THEIR WORDS · 从六年级到高三，一路看着她长大的人')
    g_all.append([s.shapes[-3].shape_id, s.shapes[-2].shape_id, s.shapes[-1].shape_id])

    rows = [
        ('刘许静 · 六年级班主任', '「从教近三十年，她是我见过最自律、最纯粹的学生。」'),
        ('王二东 · 九年级班主任', '她从来不用人催，自己把学习安排得明明白白；预习、消化、整理、复盘，一步都不落。'),
        ('程丹丹 · 高三班主任', '她话不多，可每一句都落在点子上；课本和错题本，都被她翻烂了。'),
    ]
    x, W, H = 0.56, 12.22, 1.15
    for i, (who, said) in enumerate(rows):
        y = 2.30 + i * 1.30
        g = []
        g.append(add_rect(s, x, y, W, H, WHITE).shape_id)
        g.append(add_rect(s, x, y, 0.05, H, RED).shape_id)
        g.append(add_text(s, x + 0.30, y + 0.19, 3.6, 0.28, who, size=12, color=RED, bold=True).shape_id)
        g.append(add_text(s, x + 0.30, y + 0.60, 11.5, 0.45, said, size=10.5, color=BODY, spacing=1.35).shape_id)
        g_all.append(g)

    q = add_text(s, 0.56, 6.52, 12.22, 0.45,
                 '她写在课本扉页上的一句话——"以书为梯，扛起家的希望。"',
                 size=11.5, color=GOLD, bold=True)
    g_all.append([q.shape_id])
    apply_fade_timing(s, g_all)
    print('  NB 他们眼中的她 已建')


# ---------- NC 铁娘子的一天 ----------
def build_day():
    s = new_slide()
    g_all = [[add_bg(s).shape_id]]
    add_kicker(s, 'ONE DAY · 一天的时间表')
    add_title(s, '铁娘子的一天', 'A DAY ON THE ROAD · 湖北阳新县枫林镇水源村')
    g_all.append([s.shapes[-3].shape_id, s.shapes[-2].shape_id, s.shapes[-1].shape_id])

    items = [
        ('05:00', '起床，喂鸡、给家人做早饭'),
        ('06:20', '开上那辆没有空调的二手货车出发'),
        ('07:00', '到县城分拨中心，分拣、扫码、装车'),
        ('10:00', '返回水源村快递点，卸货、分类、上架、通知取件'),
        ('午后', '骑三轮车，给行动不便的老人送货上门'),
        ('傍晚', '收车、对账，一天才算忙完'),
    ]
    xs, ys, W, H = (0.56, 6.72), (2.30, 3.48, 4.66), 6.05, 1.05
    for i, (tm, desc) in enumerate(items):
        x, y = xs[i // 3], ys[i % 3]
        g = []
        g.append(add_rect(s, x, y, W, H, WHITE).shape_id)
        g.append(add_rect(s, x, y, 0.05, H, GOLD).shape_id)
        g.append(add_text(s, x + 0.26, y + 0.24, 1.10, 0.50, tm, size=17, color=GOLD, bold=True).shape_id)
        g.append(add_text(s, x + 1.42, y + 0.22, 4.35, 0.62, desc, size=10, color=BODY, spacing=1.35,
                          anchor=MSO_ANCHOR.MIDDLE).shape_id)
        g_all.append(g)

    q = add_text(s, 0.56, 6.10, 12.22, 0.45,
                 '忙起来顾不上吃饭，头晕了就赶紧剥颗糖含着。',
                 size=11.5, color=SUB)
    g_all.append([q.shape_id])
    apply_fade_timing(s, g_all)
    print('  NC 铁娘子的一天 已建')


# ---------- ND 她记得的名字 ----------
def build_names():
    s = new_slide()
    g_all = [[add_bg(s).shape_id]]
    add_kicker(s, 'DETAILS · 包裹之外')
    add_title(s, '她记得的名字', 'MORE THAN PARCELS · 十个村里，她记着这些事')
    g_all.append([s.shapes[-3].shape_id, s.shapes[-2].shape_id, s.shapes[-1].shape_id])

    rows = [
        ('01', '她记得', '周边十个村里，谁家是独居老人、谁家有残障，她都记得姓名、电话和住址。'),
        ('02', '她捎带', '老人进城一趟不容易，她每天拖货回来顺路把菜捎上，谁家要猪肝、要猪心，她心里有数。'),
        ('03', '她分送', '每次进城买三四十个馒头，一路分送给村里的留守老人。'),
        ('04', '她垫付', '车上放着一个零钱盒，老人不会手机支付、急着用钱，她先垫上。'),
    ]
    x, W, H = 0.56, 12.22, 0.95
    for i, (no, ttl, txt) in enumerate(rows):
        y = 2.25 + i * 1.07
        g = []
        g.append(add_rect(s, x, y, W, H, WHITE).shape_id)
        g.append(add_rect(s, x, y, 0.05, H, RED).shape_id)
        g.append(add_text(s, x + 0.26, y + 0.26, 0.70, 0.42, no, size=15, color=GOLD, bold=True).shape_id)
        g.append(add_text(s, x + 1.02, y + 0.16, 1.30, 0.30, ttl, size=12, color=RED, bold=True).shape_id)
        g.append(add_text(s, x + 1.02, y + 0.50, 10.9, 0.40, txt, size=10, color=BODY).shape_id)
        g_all.append(g)

    q = add_text(s, 0.56, 6.72, 12.22, 0.42,
                 '村民谈淑萍说："她是个热心快肠的好人，有时还会塞钱给我买车票、买早餐。"',
                 size=11, color=SUB)
    g_all.append([q.shape_id])
    apply_fade_timing(s, g_all)
    print('  ND 她记得的名字 已建')


build_method()      # 索引 21 (P22)
build_voices()      # 索引 22 (P23)
build_day()         # 索引 23 (P24)
build_names()       # 索引 24 (P25)


print('\n=== 三、给此前无动画的新增页补「淡入」 ===')
for idx, name in [(7, 'P08 捷报'), (8, 'P09 托举'), (9, 'P10 接力'),
                  (15, 'P16 主题'), (16, 'P17 青马之问')]:
    s = prs.slides[idx]
    if s._element.find(qn('p:timing')) is not None:
        print(f'  {name} 已有动画，跳过')
        continue
    ids = [sh.shape_id for sh in s.shapes]
    # 背景不动画，其余按顺序逐个单击出现
    groups = [[i] for i in ids[1:]]
    apply_fade_timing(s, groups, base=8000)
    print(f'  {name} 已补 {len(groups)} 个淡入')


print('\n=== 四、重排页序 ===')
sldIdLst = prs.slides._sldIdLst
ids = list(sldIdLst)
# 现有 1..21 为新页之前的旧序；22..25 为新增 NA..ND
order = [0, 1, 2, 3, 4, 5, 6,      # P01-P07
         21,                        # NA 她的学法
         7,                         # P08 捷报
         22,                        # NB 他们眼中的她
         8, 9,                      # P09 托举、P10 接力
         10, 11,                    # P11 章节陈、P12 人物
         23,                        # NC 铁娘子的一天
         12, 13, 14,                # P13 服务站、P14 数据、P15 照片墙
         24,                        # ND 她记得的名字
         15, 16, 17, 18, 19, 20]    # P16-P21
assert len(order) == len(ids), (len(order), len(ids))
for i in order:
    sldIdLst.append(ids[i])
print(f'  新页序共 {len(ids)} 页')


print('\n=== 五、页码校准 ===')
total = len(ids)
for i, s in enumerate(prs.slides, 1):
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        t = sh.text_frame.text.strip()
        if re.fullmatch(r'\d{2} / \d{2}', t):
            set_text(sh, f'{i:02d} / {total}')
            print(f'  P{i:02d} 页码 → {i:02d} / {total}')
        elif re.fullmatch(r'PART 02 · 高山邮路 · \d+ / \d+', t):
            set_text(sh, f'PART 02 · 高山邮路 · {i:02d} / {total}')
            print(f'  P{i:02d} 章节标签 → {t.split("·")[-1].strip()} → {i:02d} / {total}')


print('\n=== 六、配色收敛 ===')
MY_PAGES = {8, 9, 10, 15, 16, 17,  # 我此前新增
            22, 23, 24, 25}       # v7 新增（重排后仍在末尾附近，按元素遍历更稳）
cnt = {}
for idx, s in enumerate(prs.slides, 1):
    for el in s._element.iter():
        v = el.get('val')
        if v and v.upper() in COLOR_MAP:
            el.set('val', COLOR_MAP[v.upper()])
            cnt[v.upper()] = cnt.get(v.upper(), 0) + 1
for k, n in sorted(cnt.items()):
    print(f'  #{k} → #{COLOR_MAP[k]}  ×{n}')

prs.save(DST)
print(f'\n已保存：{DST}')
