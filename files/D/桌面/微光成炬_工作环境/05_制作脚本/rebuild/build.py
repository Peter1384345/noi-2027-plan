# -*- coding: utf-8 -*-
"""从初代重做《微光成炬 · 星火自有燎原时》22 页版本。

保留初代的内容与页面原型，重建目录体系（大目录 + 小目录），
补入顾妈妈页、两页视频、过渡金句页，并把封面统一到深红渐变。
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn, nsdecls
from pptx.oxml import parse_xml
from pptx.dml.color import RGBColor

IN = 914400
W, H = 13.333 * IN, 7.5 * IN

# ---------- 配色 ----------
DEEP  = RGBColor(0x8E, 0x00, 0x00)
RED2  = RGBColor(0xC0, 0x00, 0x00)
DEEPRED = RGBColor(0x8B, 0x00, 0x00)
CREAM = RGBColor(0xF7, 0xF4, 0xEE)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
INK   = RGBColor(0x1A, 0x16, 0x14)
INK2  = RGBColor(0x2A, 0x28, 0x25)
SUB   = RGBColor(0x4A, 0x3F, 0x39)
GREY  = RGBColor(0x8A, 0x83, 0x78)
GOLD  = RGBColor(0xE8, 0xC8, 0x7A)
GOLD2 = RGBColor(0xC9, 0xA2, 0x27)
EDGE  = RGBColor(0xD6, 0xC7, 0xB2)
LINE  = RGBColor(0xD9, 0xC7, 0xB0)
YELLOW = RGBColor(0xFF, 0xFF, 0x00)

SERIF = "仿宋"
SANS  = "微软雅黑"
EN    = "Georgia"

BASE = r"D:\桌面\微光成炬_工作环境\01_初代版本\微光成炬-星火自有燎原时_初代.pptx"
OUT  = r"D:\桌面\微光成炬_工作环境\06_成品输出\微光成炬-星火自有燎原时_重做版22页.pptx"
VID  = r"D:\桌面\微光成炬_工作环境\02_视频素材"
IMG  = r"D:\桌面\微光成炬_工作环境\03_图片素材\人物与海报"


# ---------- 基础绘图 ----------
def _noshadow(shp):
    try:
        shp.shadow.inherit = False
    except Exception:
        pass
    return shp


def rect(s, x, y, w, h, fill, line=None, lw=1.0, shape=MSO_SHAPE.RECTANGLE):
    shp = _noshadow(s.shapes.add_shape(shape, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h))))
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line; shp.line.width = Pt(lw)
    return shp


def grad_bg(s, c1=DEEP, c2=RED2, ang=45.0):
    shp = _noshadow(s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Emu(int(W)), Emu(int(H))))
    shp.line.fill.background()
    shp.fill.gradient()
    st = shp.fill.gradient_stops
    st[0].color.rgb = c1; st[0].position = 0.0
    st[1].color.rgb = c2; st[1].position = 1.0
    try:
        shp.fill.gradient_angle = ang
    except Exception:
        pass
    return shp


def text(s, x, y, w, h, txt, size, color, font=SANS, align=PP_ALIGN.LEFT,
         spc=0, bold=True, spacing=1.12, anchor=MSO_ANCHOR.TOP):
    tb = s.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = spacing
    r = p.add_run(); r.text = txt
    f = r.font
    f.size = Pt(size); f.bold = bold; f.color.rgb = color; f.name = font
    rPr = r._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
    ea.set('typeface', font)
    if spc:
        rPr.set('spc', str(int(spc)))
    return tb


def rich(s, x, y, w, h, parts, size, color, font=SANS, spacing=1.5, bold=True, spc=30):
    """一段里混排多色：parts = [(txt, color|None), ...]"""
    tb = s.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.line_spacing = spacing
    for txt, col in parts:
        r = p.add_run(); r.text = txt
        f = r.font
        f.size = Pt(size); f.bold = bold
        f.color.rgb = col if col is not None else color
        f.name = font
        rPr = r._r.get_or_add_rPr()
        ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
        ea.set('typeface', font)
        if spc:
            rPr.set('spc', str(int(spc)))
    return tb


def pic_cover(s, path, x, y, w, h):
    from PIL import Image
    pic = s.shapes.add_picture(path, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    iw, ih = Image.open(path).size
    tgt, src = w / h, iw / ih
    if src > tgt:
        f = (1 - tgt / src) / 2
        pic.crop_left = f; pic.crop_right = f
    else:
        f = (1 - src / tgt) / 2
        pic.crop_top = f; pic.crop_bottom = f
    return pic


def fade(s, x, y, w, h, color=CREAM, ang=0, a0=0, a1=100000):
    """透明→实色的渐隐块，用来把照片“溶”进页面（实心块会留下硬边）"""
    shp = _noshadow(s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(int(x)), Emu(int(y)),
                                       Emu(int(w)), Emu(int(h))))
    shp.line.fill.background()
    hexc = '%02X%02X%02X' % (color[0], color[1], color[2])
    xml = (
        '<a:gradFill %s rotWithShape="1"><a:gsLst>'
        '<a:gs pos="0"><a:srgbClr val="%s"><a:alpha val="%d"/></a:srgbClr></a:gs>'
        '<a:gs pos="100000"><a:srgbClr val="%s"><a:alpha val="%d"/></a:srgbClr></a:gs>'
        '</a:gsLst><a:lin ang="%d" scaled="0"/></a:gradFill>'
        % (nsdecls('a'), hexc, a0, hexc, a1, int(ang * 60000))
    )
    spPr = shp._element.spPr
    for tag in ('a:noFill', 'a:solidFill', 'a:gradFill', 'a:blipFill', 'a:pattFill', 'a:grpFill'):
        for el in spPr.findall(qn(tag)):
            spPr.remove(el)
    g = parse_xml(xml)
    ln = spPr.find(qn('a:ln'))
    if ln is not None:
        ln.addprevious(g)
    else:
        spPr.append(g)
    return shp


def clear(s):
    for sh in list(s.shapes):
        sh._element.getparent().remove(sh._element)


# ---------- 幻灯片增删 ----------
def new_slide(prs, at):
    layout = min(prs.slide_layouts, key=lambda l: len(l.placeholders))
    s = prs.slides.add_slide(layout)
    clear(s)
    lst = prs.slides._sldIdLst
    ids = list(lst)
    lst.remove(ids[-1])
    lst.insert(at, ids[-1])
    return s


def reorder(prs, order):
    lst = prs.slides._sldIdLst
    ids = list(lst)
    for el in ids:
        lst.remove(el)
    for i in order:
        lst.append(ids[i])


# ---------- 视频自动播放 ----------
VIDEO_TMPL = (
    '<p:timing {ns}><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
    '<p:childTnLst><p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq">'
    '<p:childTnLst><p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
    '<p:childTnLst><p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
    '<p:childTnLst><p:video><p:cMediaNode vol="{vol}"><p:cTn id="5" fill="hold" display="0">'
    '<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
    '<p:endCondLst><p:cond evt="onStopAudio" delay="0"/></p:endCondLst></p:cTn>'
    '<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cMediaNode></p:video></p:childTnLst>'
    '</p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
    '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
    '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
    '</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>'
)


def autoplay(slide, movie_shape, vol=80000):
    el = slide._element
    for old in el.findall(qn('p:timing')):
        el.remove(old)
    xml = VIDEO_TMPL.format(ns=nsdecls('p', 'a'), vol=vol, spid=movie_shape.shape_id)
    node = parse_xml(xml)
    ext = el.find(qn('p:extLst'))
    if ext is not None:
        ext.addprevious(node)
    else:
        el.append(node)


def add_video(slide, path, poster=None):
    kw = dict(mime_type="video/mp4")
    if poster and os.path.exists(poster):
        kw["poster_frame_image"] = poster
    return slide.shapes.add_movie(path, Emu(0), Emu(0), Emu(int(W)), Emu(int(H)), **kw)


# ================= 新页面 =================
def page_opening(s):
    """P1 片头视频"""
    rect(s, 0, 0, W, H, RGBColor(0x0A, 0x0A, 0x0A))
    mv = add_video(s, os.path.join(VID, "开场_微光成炬_16x9.mp4"),
                   os.path.join(IMG, "poster_opening.jpg"))
    text(s, 0.62 * IN, 7.10 * IN, 5.0 * IN, 0.22 * IN, "OPENING · 拾光者小组", 9,
         RGBColor(0x51, 0x51, 0x51), font=SANS, spc=300)
    return mv


def page_toc(s):
    """P4 大目录：奶白底 + 四条白横条索引"""
    clear(s)
    rect(s, 0, 0, W, H, CREAM)
    rect(s, 1.00 * IN, 0.62 * IN, 0.44 * IN, 0.014 * IN, DEEPRED)
    text(s, 1.52 * IN, 0.52 * IN, 3.0 * IN, 0.22 * IN, "CONTENTS", 11, DEEPRED, font=EN, spc=260)
    text(s, 1.20 * IN, 0.86 * IN, 1.85 * IN, 0.78 * IN, "目录", 38, DEEPRED, font=SERIF, spc=110)
    text(s, 3.05 * IN, 1.14 * IN, 4.6 * IN, 0.22 * IN, "FOUR CHAPTERS · ONE STORY", 11, GREY,
         font=EN, spc=220)
    text(s, 6.90 * IN, 0.92 * IN, 5.43 * IN, 0.42 * IN, "微光成炬 · 星火自有燎原时", 22, INK,
         align=PP_ALIGN.RIGHT, spc=70)
    text(s, 6.90 * IN, 1.44 * IN, 5.43 * IN, 0.22 * IN, "一 场 关 于 坚 守 的 讲 述", 11, GREY,
         align=PP_ALIGN.RIGHT, spc=120)

    ROWS = [
        ("01", "微光 · 韩雅平", "PART 01 · A LIGHT FROM A VILLAGE HOME", "P06—10"),
        ("02", "成炬 · 陈新超", "PART 02 · THE ROAD POSTWOMAN", "P11—16"),
        ("03", "燎原 · 微光成炬", "EPILOGUE · TWO GLIMMERS, ONE TORCH", "P17—18"),
        ("04", "致谢", "CREDITS · ACKNOWLEDGEMENTS", "P19—22"),
    ]
    y0, bh, gap = 2.40 * IN, 0.90 * IN, 0.13 * IN
    for i, (num, title, sub, pg) in enumerate(ROWS):
        y = y0 + i * (bh + gap)
        rect(s, 1.00 * IN, y, 11.33 * IN, bh, WHITE, line=EDGE, lw=1.1)
        text(s, 1.20 * IN, y + 0.14 * IN, 1.10 * IN, 0.62 * IN, num, 44, DEEPRED, font=EN)
        rect(s, 2.42 * IN, y + 0.18 * IN, 0.022 * IN, 0.54 * IN, GOLD2)
        text(s, 2.62 * IN, y + 0.11 * IN, 6.20 * IN, 0.34 * IN, title, 24, INK, spc=40)
        text(s, 2.62 * IN, y + 0.57 * IN, 8.20 * IN, 0.22 * IN, sub, 10.5, GREY, font=EN, spc=90)
        text(s, 10.60 * IN, y + 0.29 * IN, 1.62 * IN, 0.32 * IN, pg, 13, DEEPRED, font=EN,
             align=PP_ALIGN.RIGHT, spc=80)

    text(s, 1.00 * IN, 6.74 * IN, 4.5 * IN, 0.22 * IN, "拾光者小组 · 十五人", 11, GREY, spc=180)
    text(s, 9.40 * IN, 6.74 * IN, 2.93 * IN, 0.22 * IN, "FROM SPARK TO FLAME", 11, GREY,
         font=EN, align=PP_ALIGN.RIGHT, spc=280)


def page_guma(s):
    """P9 顾妈妈 —— 镜像韩雅平人物页的版式"""
    clear(s)
    rect(s, 0, 0, W, H, CREAM)
    pic_cover(s, os.path.join(IMG, "guma_portrait.jpg"), 0, 0, 6.25 * IN, 7.5 * IN)
    grad = fade(s, 4.90 * IN, -0.02 * IN, 2.00 * IN, 7.54 * IN, CREAM, ang=0)

    text(s, 6.60 * IN, 0.92 * IN, 5.73 * IN, 0.78 * IN, "顾妈妈", 45, DEEPRED, spc=750)
    text(s, 7.44 * IN, 1.94 * IN, 5.73 * IN, 0.24 * IN,
         "—— 浙江嘉善 · “爱心妈妈” 顾虹 · 十二年之约", 12, SUB, spc=140)

    # 三段正文放在同一个文本框里，段间距才均匀
    tb = s.shapes.add_textbox(Emu(int(6.60 * IN)), Emu(int(2.30 * IN)),
                              Emu(int(5.73 * IN)), Emu(int(3.92 * IN)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    PARAS = [
        [("2014 年，", None), ("6 岁", DEEPRED),
         ("的韩雅平在镜头里说“想上学”。嘉善的顾虹看到后开始一对一资助——这一资助，就是", None),
         ("十二年", DEEPRED), ("。", None)],
        [("十二年间，两人只靠书信往来。她没去过河南，却记得雅平每一年的成绩；雅平没见过她，却叫了十二年“顾妈妈”。", None)],
        [("699 分出来那天，顾妈妈在电话那头哭了。后来她把雅平的故事讲给身边的人听，又有", None),
         ("50 位爱心人士", DEEPRED), ("加入了助学。", None)],
    ]
    for i, parts in enumerate(PARAS):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = 1.62
        p.space_after = Pt(16)
        for txt, col in parts:
            r = p.add_run(); r.text = txt
            f = r.font
            f.size = Pt(15); f.bold = True
            f.color.rgb = col if col is not None else RGBColor(0x3A, 0x3A, 0x38)
            f.name = SANS
            rPr = r._r.get_or_add_rPr()
            ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
            ea.set('typeface', SANS)
            rPr.set('spc', '30')

    rect(s, 6.71 * IN, 6.34 * IN, 5.69 * IN, 0.96 * IN, WHITE)
    rect(s, 6.67 * IN, 6.31 * IN, 0.06 * IN, 1.02 * IN, RED2)
    rich(s, 6.94 * IN, 6.46 * IN, 5.30 * IN, 0.70 * IN,
         [("“", None), ("我叫了她十二年“顾妈妈”。她让我知道，我不是一个人在往前走。", None), ("”", None)],
         11.8, RGBColor(0x21, 0x1F, 0x1B), spacing=1.4)


def page_video(s, title, sub, source, video, poster=None):
    """视频播放页：黑底 + 全屏视频 + 底部字幕条"""
    clear(s)
    rect(s, 0, 0, W, H, RGBColor(0x0A, 0x0A, 0x0A))
    mv = add_video(s, video, poster)
    bar = rect(s, 0, 6.92 * IN, W, 0.58 * IN, RGBColor(0x00, 0x00, 0x00))
    # 半透明
    sp = bar.fill._xPr.find(qn('a:solidFill'))
    if sp is not None:
        clr = sp.find(qn('a:srgbClr'))
        if clr is not None:
            alpha = parse_xml('<a:alpha %s val="72000"/>' % nsdecls('a'))
            clr.append(alpha)
    text(s, 0.78 * IN, 7.06 * IN, 7.2 * IN, 0.26 * IN, title, 13, WHITE, spc=120)
    text(s, 8.60 * IN, 7.08 * IN, 4.0 * IN, 0.24 * IN, source, 9.5,
         RGBColor(0xB8, 0xB8, 0xB8), align=PP_ALIGN.RIGHT, spc=80)
    text(s, 0.78 * IN, 6.42 * IN, 7.2 * IN, 0.30 * IN, sub, 15, GOLD, spc=140)
    return mv


def page_quotes(s):
    """P16 过渡：两句话"""
    clear(s)
    rect(s, 0, 0, W, H, CREAM)
    rect(s, 1.00 * IN, 0.62 * IN, 0.44 * IN, 0.014 * IN, DEEPRED)
    text(s, 1.52 * IN, 0.52 * IN, 4.0 * IN, 0.22 * IN, "TWO VOICES", 11, DEEPRED, font=EN, spc=260)
    text(s, 1.20 * IN, 0.86 * IN, 8.0 * IN, 0.80 * IN, "两句话", 38, DEEPRED, font=SERIF, spc=110)

    blocks = [
        (1.10 * IN, 5.35 * IN, "不吃学习的苦，就要吃生活的苦。", "韩雅平 · 河南郏县 · 699 分圆梦清华"),
        (7.05 * IN, 5.60 * IN, "我是党员，应该做榜样。只要身体允许，我就会一直做下去。",
         "陈新超 · 湖北阳新 · 乡邮员 · 荆楚楷模"),
    ]
    for x, bw, txt, sig in blocks:
        text(s, x, 1.86 * IN, 1.2 * IN, 1.0 * IN, "“", 90, RGBColor(0xE3, 0xD2, 0xBC), font=SERIF)
        text(s, x, 3.00 * IN, bw, 2.10 * IN, txt, 26, INK, font=SERIF, spc=50, spacing=1.62)
        rect(s, x, 4.86 * IN, 0.62 * IN, 0.014 * IN, GOLD2)
        text(s, x, 5.04 * IN, bw, 0.28 * IN, sig, 12, RGBColor(0x6B, 0x5F, 0x57), spc=90)

    rect(s, 6.72 * IN, 1.90 * IN, 0.008 * IN, 3.30 * IN, LINE)
    rect(s, 1.00 * IN, 6.36 * IN, 11.33 * IN, 0.008 * IN, LINE)
    text(s, 1.20 * IN, 6.52 * IN, 11.0 * IN, 0.40 * IN, "两束微光，同一种选择。", 22, DEEPRED,
         font=SERIF, spc=140)


def page_mini(s, k, num, over, title, sub, items, quote):
    """小目录页（燎原 / 致谢）"""
    clear(s)
    L, R = 0.93 * IN, 12.40 * IN
    TOT, COLW = R - L, (R - L) / 4
    LABELS = ["微光", "成炬", "燎原", "致谢"]

    rect(s, 0, 0, W, H, CREAM)
    rect(s, 0.93 * IN, 0.96 * IN, 0.075 * IN, 1.80 * IN, DEEPRED)
    text(s, 1.22 * IN, 0.92 * IN, 4.4 * IN, 0.30 * IN, over, 13, DEEPRED, font=EN, spc=340)
    text(s, 9.85 * IN, 0.42 * IN, 2.55 * IN, 1.95 * IN, num, 118, RGBColor(0xF0, 0xE7, 0xD6),
         font=EN, align=PP_ALIGN.RIGHT)
    text(s, 1.20 * IN, 1.14 * IN, 9.4 * IN, 1.02 * IN, title, 44, DEEPRED, font=SERIF, spc=50)
    text(s, 1.24 * IN, 2.24 * IN, 9.4 * IN, 0.34 * IN, sub, 14.5, SUB, spc=40)

    ay = 3.02 * IN
    for i in range(4):
        sx = L + i * COLW
        on = (i == k)
        rect(s, sx, ay, COLW - 0.10 * IN, 0.048 * IN if on else 0.018 * IN,
             DEEPRED if on else RGBColor(0xD9, 0xC9, 0xB6))
        text(s, sx, ay + 0.17 * IN, COLW - 0.10 * IN, 0.28 * IN, "%02d  %s" % (i + 1, LABELS[i]),
             12.5, DEEPRED if on else RGBColor(0x6B, 0x5F, 0x57), spc=60)

    n = len(items)
    top, bot = 3.92 * IN, 5.46 * IN
    rowh = min(0.80 * IN, (bot - top) / n)
    y0 = top + ((bot - top) - rowh * n) / 2
    for j, t in enumerate(items):
        y = y0 + j * rowh
        rect(s, 0.93 * IN, y + 0.235 * IN, 0.095 * IN, 0.095 * IN, DEEPRED)
        text(s, 1.24 * IN, y + 0.06 * IN, 9.6 * IN, 0.42 * IN, t, 18, INK, spc=30)
        if j < n - 1:
            rect(s, 0.93 * IN, y + rowh - 0.12 * IN, TOT, 0.007 * IN, LINE)

    rect(s, 0.93 * IN, 5.86 * IN, TOT, 0.009 * IN, GOLD2)
    text(s, 1.24 * IN, 6.06 * IN, 11.0 * IN, 0.46 * IN, quote, 25, DEEPRED, font=SERIF, spc=70)
    rect(s, 0.93 * IN, 6.62 * IN, TOT, 0.006 * IN, LINE)
    text(s, 0.93 * IN, 6.72 * IN, 4.5 * IN, 0.22 * IN, "拾光者小组 · 十五人", 10,
         RGBColor(0x6B, 0x5F, 0x57), spc=200)
    text(s, 8.60 * IN, 6.72 * IN, 3.80 * IN, 0.22 * IN, "FROM SPARK TO FLAME", 10,
         RGBColor(0x6B, 0x5F, 0x57), font=EN, align=PP_ALIGN.RIGHT, spc=320)


def fix_cover(s):
    """封面左上角原本压着火炬与右侧照片：把署名与副题移到上方空白区"""
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        t = sh.text_frame.text.replace("\n", "").strip()
        if "制作者" in t:
            sh.left, sh.top = Emu(int(0.66 * IN)), Emu(int(0.42 * IN))
            sh.width, sh.height = Emu(int(5.2 * IN)), Emu(int(0.34 * IN))
            for p in sh.text_frame.paragraphs:
                p.alignment = PP_ALIGN.LEFT
                p.line_spacing = 1.0
                for r in p.runs:
                    r.font.size = Pt(17)
                    r.font.color.rgb = GOLD
        elif "星火自有燎原时" in t:
            sh.left, sh.top = Emu(int(0.66 * IN)), Emu(int(0.76 * IN))
            sh.width, sh.height = Emu(int(7.6 * IN)), Emu(int(0.56 * IN))
            for p in sh.text_frame.paragraphs:
                p.alignment = PP_ALIGN.LEFT
                p.line_spacing = 1.0
                for r in p.runs:
                    r.font.size = Pt(27)
                    r.font.color.rgb = WHITE


def fix_p22_panel(s):
    """「谢谢聆听」背后的色块是主题色 bg2，红底上会成一条突兀的浅灰带，
    改成与全片一致的奶白。"""
    for sh in s.shapes:
        if (sh.width or 0) > 12 * IN and 3.0 * IN < (sh.top or 0) < 4.0 * IN:
            try:
                sh.fill.solid()
                sh.fill.fore_color.rgb = CREAM
            except Exception:
                pass


def fix_thx_line(s):
    """致谢页那句「十五人同行，共燃一盏灯」原来是一整行，右半截被火炬压住；
    改成两行排在左侧空白处。"""
    for sh in s.shapes:
        if not sh.has_text_frame or "十五人同行" not in sh.text_frame.text:
            continue
        sh.left, sh.top = Emu(int(0.95 * IN)), Emu(int(3.42 * IN))
        sh.width, sh.height = Emu(int(4.30 * IN)), Emu(int(1.30 * IN))
        tf = sh.text_frame
        tf.word_wrap = True
        p0 = tf.paragraphs[0]
        for r in list(p0.runs)[1:]:
            p0._p.remove(r._r)
        r0 = p0.runs[0]
        r0.text = "十五人同行，"
        r0.font.size = Pt(34)
        r0.font.color.rgb = YELLOW
        p1 = tf.add_paragraph()
        r1 = p1.add_run()
        r1.text = "共燃一盏灯"
        f = r1.font
        f.size = Pt(34); f.bold = True; f.name = SANS; f.color.rgb = YELLOW
        rPr = r1._r.get_or_add_rPr()
        ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
        ea.set('typeface', SANS)
        rPr.set('spc', '300')


def fix_thx_credits(s):
    """鸣谢名单原来居中横排，被中间的火炬从中间劈开；挪到左栏成块"""
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        t = sh.text_frame.text.replace("\n", "")
        if t.startswith("特别") and "鸣谢" in t:
            sh.left, sh.top = Emu(int(0.95 * IN)), Emu(int(5.62 * IN))
            sh.width, sh.height = Emu(int(4.30 * IN)), Emu(int(1.10 * IN))
            tf = sh.text_frame
            tf.word_wrap = True
            for p in tf.paragraphs:
                p.alignment = PP_ALIGN.LEFT
                p.line_spacing = 1.45
                for r in p.runs:
                    r.font.size = Pt(11)
        elif t.startswith("——星火自有燎原时"):
            sh.left = Emu(int(8.85 * IN))
            sh.width = Emu(int(4.40 * IN))
            for p in sh.text_frame.paragraphs:
                p.line_spacing = 1.15
                for r in p.runs:
                    r.font.size = Pt(23)


def fix_p12_stats(s):
    """P12 底部数据条：原来每个数字/单位各占一个窄框，单位全被挤成两行、
    还压到引用条上；重新做成一整行混排。"""
    TOKENS = {"1700+", "天", "120", "公里", "公里/天", "/", "400", "件包裹", "10", "个村"}
    for sh in list(s.shapes):
        if not sh.has_text_frame:
            continue
        t = sh.text_frame.text.strip().replace(" ", "")
        if t in TOKENS and (sh.top or 0) > 5.9 * IN:
            sh._element.getparent().remove(sh._element)

    GOLDD = RGBColor(0x8B, 0x5E, 0x00)
    PARTS = [("1700+", RED2), (" 天    ", GOLDD),
             ("120", RED2), (" 公里/天    ", GOLDD),
             ("400", RED2), (" 件包裹    ", GOLDD),
             ("10", RED2), (" 个村", GOLDD)]

    # 按真实字宽自适应：从 23/14.5 起，超宽就整体缩
    from PIL import ImageFont
    def measure(num_pt, unit_pt):
        total = 0.0
        for i, (txt, _) in enumerate(PARTS):
            pt = num_pt if i % 2 == 0 else unit_pt
            f = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", int(pt * 120 / 72.0))
            total += f.getlength(txt) + len(txt) * 0.4 * 120 / 72.0 / 4  # 粗体 + 4/100pt 字间距
        return total / 120.0  # inch

    num_pt, unit_pt = 20.0, 13.0
    print("P12 数据条实测字宽 %.2f in → 数字 %.1fpt / 单位 %.1fpt" % (measure(num_pt, unit_pt), num_pt, unit_pt))

    tb = s.shapes.add_textbox(Emu(int(6.71 * IN)), Emu(int(6.06 * IN)),
                              Emu(int(6.62 * IN)), Emu(int(0.42 * IN)))
    tf = tb.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.line_spacing = 1.0
    for i, (txt, col) in enumerate(PARTS):
        r = p.add_run(); r.text = txt
        f = r.font
        f.size = Pt(num_pt if i % 2 == 0 else unit_pt)
        f.bold = True; f.color.rgb = col; f.name = SANS
        rPr = r._r.get_or_add_rPr()
        ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
        ea.set('typeface', SANS)
        rPr.set('spc', '40')


def fix_p12_quote(s):
    """引用条里两行字原来贴着底边被切，抬高并略降字号"""
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        if sh.text_frame.text.strip().startswith('"我是党员'):
            sh.top = Emu(int(6.79 * IN))
            sh.height = Emu(int(0.52 * IN))
            for p in sh.text_frame.paragraphs:
                p.line_spacing = 1.25
                for r in p.runs:
                    r.font.size = Pt(14.5)


def fix_p12_sub(s):
    """副标题原来是黄色，压在米白底上基本看不见"""
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        if sh.text_frame.text.strip().startswith("——湖北阳新县"):
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    r.font.color.rgb = RGBColor(0x6B, 0x4A, 0x12)


def set_note(slide, txt):
    """写入演讲者备注；缺 body 占位符时先补一个（初代的 notes 页没有占位符）"""
    ns = slide.notes_slide
    tf = ns.notes_text_frame
    if tf is None:
        tree = ns.shapes._spTree
        ids = [int(e.get('id')) for e in tree.iter(qn('p:cNvPr')) if e.get('id', '').isdigit()]
        nid = (max(ids) + 1) if ids else 2
        sp = parse_xml(
            '<p:sp %s><p:nvSpPr><p:cNvPr id="%d" name="Notes Placeholder %d"/>'
            '<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            '<p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr>'
            '<p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
            % (nsdecls('p', 'a'), nid, nid))
        tree.append(sp)
        tf = ns.notes_text_frame
    if tf is None:
        raise RuntimeError("notes placeholder 仍不可用")
    tf.text = txt


# ================= 主流程 =================
def main():
    prs = Presentation(BASE)
    print("初代页数:", len(prs.slides))

    # 1) 红封面排到第一，其余保持原序
    reorder(prs, [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
    print("重排后:", len(prs.slides))

    # 2) 按最终位置插入新页（升序插，索引累加可控）
    s_open = new_slide(prs, 0)      # P1
    s_guma = new_slide(prs, 8)      # P9
    s_vhy  = new_slide(prs, 9)      # P10
    s_vcx  = new_slide(prs, 14)     # P15
    s_quot = new_slide(prs, 15)     # P16
    s_liao = new_slide(prs, 16)     # P17
    s_thx  = new_slide(prs, 18)     # P19
    print("插入后:", len(prs.slides))
    sl = list(prs.slides)

    # 3) 封面改深红渐变（原 #FF0000 太刺眼）
    cover = sl[1]
    done = False
    for sh in cover.shapes:
        if sh.width and sh.height and sh.width >= W * 0.98 and sh.height >= H * 0.98:
            sh.fill.gradient()
            st = sh.fill.gradient_stops
            st[0].color.rgb = DEEP; st[0].position = 0.0
            st[1].color.rgb = RED2; st[1].position = 1.0
            try:
                sh.fill.gradient_angle = 45.0
            except Exception:
                pass
            done = True
            break
    print("封面渐变:", "ok" if done else "未找到底版")

    # 4) 构建新页
    mv_open = page_opening(sl[0])
    page_toc(sl[3])
    page_guma(sl[8])
    mv_hy = page_video(sl[9], "韩雅平 · 她说的那句话",
                       "《小莉帮忙》采访片段",
                       "视频来源：河南广播电视台《小莉帮忙》",
                       os.path.join(VID, "韩雅平_699分清华采访_16x9.mp4"),
                       None)
    mv_cx = page_video(sl[14], "陈新超 · 邮路上的十二年",
                       "湖北广电《新时代的我们》· 荆楚楷模",
                       "视频来源：湖北广播电视台《新时代的我们》",
                       os.path.join(VID, "陈新超_新时代的我们_荆楚楷模_高清.mp4"),
                       os.path.join(IMG, "frame_16x9.png"))
    page_quotes(sl[15])
    page_mini(sl[16], 2, "03", "EPILOGUE", "燎原 · 微光成炬", "两张答卷 · 同一种选择 · 约 40 秒",
              ["韩雅平 · 一张书桌，也能撑起一座山",
               "陈新超 · 把邮路走成归途",
               "两束微光 · 同一种选择"],
              "“知识改变命运；而善意，让命运有了另一条路。”")
    page_mini(sl[18], 3, "04", "CREDITS", "致谢 · 谢谢聆听", "五组同行 · 十五个人 · 约 20 秒",
              ["特别鸣谢 · 五个小组，十五个人",
               "谢谢聆听 · 星火自有燎原时"],
              "十五人同行，共燃一盏灯。")

    # 5) 三处视频设为进入页面自动播放
    for s_, mv in ((sl[0], mv_open), (sl[9], mv_hy), (sl[14], mv_cx)):
        autoplay(s_, mv)

    # 5b) 封面署名/副题挪位；P22 浅灰带改奶白
    fix_cover(sl[1])
    fix_cover(sl[2])
    fix_p22_panel(sl[21])
    fix_thx_line(sl[19])
    fix_thx_line(sl[20])
    fix_thx_credits(sl[19])
    fix_thx_credits(sl[20])

    # 5c) P12 数据条重做 + 副标题改深色
    fix_p12_stats(sl[11])
    fix_p12_sub(sl[11])
    fix_p12_quote(sl[11])

    # 5c) P14 说明文字框过窄，导致「10 个 / 村」这种难看的断行
    for sh in sl[13].shapes:
        if sh.has_text_frame and sh.text_frame.text.startswith("一辆没空调"):
            sh.width = Emu(int(5.55 * IN))
            print("P14 说明文字框放宽:", sh.width / IN)

    # 5c) 小字统一抬到 10.5pt 并加粗（新做的页与刻意的小字跳过）
    SKIP = {0, 3, 9, 14, 15, 16, 18}
    bumped = 0
    for i, s_ in enumerate(prs.slides):
        if i in SKIP:
            continue
        for sh in s_.shapes:
            if not sh.has_text_frame:
                continue
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if r.font.size and r.font.size.pt < 10.5 and r.text.strip():
                        r.font.size = Pt(10.5)
                        r.font.bold = True
                        bumped += 1
    print("小字抬升:", bumped, "处")

    # 6) 清掉初代遗留的旧页码残字（形如「· 10 / 13」）
    import re
    pat = re.compile(r'·\s*\d+\s*/\s*\d+')
    killed = 0
    for s_ in prs.slides:
        for sh in s_.shapes:
            if not sh.has_text_frame:
                continue
            for p in sh.text_frame.paragraphs:
                for r in list(p.runs):
                    if pat.search(r.text):
                        p._p.remove(r._r)
                        killed += 1
    print("清除旧页码残字:", killed, "处")

    # 7) 备注
    NOTES = {
        0: "开场片头（约 8 秒）：自动播放，全场安静看完再翻页。",
        3: "大目录：四章，一句话带过即可，20 秒。",
        4: "团队分工：五个组，十五个人，8 秒带过。",
        5: "PART 01 章节页：停 3 秒，让「微光」两个字立住。",
        8: "顾妈妈：全场情绪的第一个高点，慢讲，约 55 秒。",
        9: "采访视频：播放前先给一句引导，播 1 分钟左右。",
        14: "陈新超视频：同上，播 1 分钟左右。",
        15: "两句话：过渡页，20 秒，准备收束。",
        16: "燎原小目录：40 秒。",
        17: "尾声：两张答卷并置，50 秒收。",
        18: "致谢小目录：20 秒。",
    }
    fails = 0
    for i, s_ in enumerate(prs.slides):
        if i not in NOTES:
            continue
        try:
            set_note(s_, NOTES[i])
        except Exception as e:
            fails += 1
            print("  备注写入失败 P%d: %s" % (i + 1, e))
    print("备注写入:", len(NOTES) - fails, "/", len(NOTES))

    prs.save(OUT)
    print("已保存:", OUT, "共", len(prs.slides), "页")


if __name__ == "__main__":
    main()
