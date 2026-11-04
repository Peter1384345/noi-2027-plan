# -*- coding: utf-8 -*-
"""v13：从 v11（真原版+内容）重建两页影像，按素材真实比例排版
   P08 韩雅平：两块 9:16 竖屏（素材本身为竖屏）
   P13 陈新超：两块 16:9 横屏（真实新闻影像 + 纪实照片缓推）"""
import sys, shutil
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree

sys.stdout.reconfigure(encoding='utf-8')
BASE = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58"
SRC = BASE + r"/微光成炬-星火自有燎原时（终版·v11）.pptx"
DST = BASE + r"/微光成炬-星火自有燎原时（终版·v13）.pptx"
W = BASE + r"/work"
shutil.copyfile(SRC, DST)
prs = Presentation(DST)
EMU = 914400
FONT = '微软雅黑'
layout = list(prs.slides)[9].slide_layout


def set_run(r, text, size, color, bold=False, spc=None):
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = RGBColor.from_string(color)
    r.font.name = FONT
    rPr = r._r.get_or_add_rPr()
    if spc:
        rPr.set('spc', str(spc))
    for tag in ('a:latin', 'a:ea'):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set('typeface', FONT)


def add_text(slide, x, y, w, h, lines, size, color, bold=False, align_center=False):
    tb = slide.shapes.add_textbox(Emu(int(x * EMU)), Emu(int(y * EMU)),
                                  Emu(int(w * EMU)), Emu(int(h * EMU)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if align_center:
            from pptx.enum.text import PP_ALIGN
            p.alignment = PP_ALIGN.CENTER
        set_run(p.add_run(), line, size, color, bold)
    return tb


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


def apply_timing(slide, groups, autoplay_spids=()):
    blocks, nid = [], 100
    inner = []
    for k, sid in enumerate(groups[0]):
        nid += 3
        inner.append(_fade(nid, sid, 0 if k == 0 else 120))
    for spid in autoplay_spids:
        nid += 3
        inner.append(
            f'<p:video><p:cMediaNode vol="80000" showWhenStopped="0" numSld="1">'
            f'<p:cTn id="{nid}" fill="hold" display="0" repeatCount="indefinite">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
            f'<p:endCondLst><p:cond evt="onStopAudio" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:endCondLst>'
            f'</p:cTn><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cMediaNode></p:video>')
    blocks.append('<p:par><p:cTn fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                  f'<p:childTnLst>{"".join(inner)}</p:childTnLst></p:cTn></p:par>')
    for grp in groups[1:]:
        inner = []
        for k, sid in enumerate(grp):
            nid += 3
            inner.append(_fade(nid, sid, 0 if k == 0 else 120))
        blocks.append('<p:par><p:cTn fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
                      f'<p:childTnLst>{"".join(inner)}</p:childTnLst></p:cTn></p:par>')
    xml = ('<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
           'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
           '<p:tnLst><p:par><p:cTn id="98" dur="indefinite" restart="never" nodeType="tmRoot">'
           '<p:childTnLst><p:seq concurrent="1" nextAc="seek">'
           '<p:cTn id="99" dur="indefinite" nodeType="mainSeq">'
           f'<p:childTnLst>{"".join(blocks)}</p:childTnLst></p:cTn>'
           '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
           '</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')
    sld = slide._element
    old = sld.find(qn('p:timing'))
    if old is not None:
        sld.remove(old)
    sld.append(etree.fromstring(xml))


def make_page(tag_line, title, videos, caps, autoplay=()):
    """videos: [(path, poster, x, y, w, h)]; caps: [(x,y,w,lines)]"""
    s = prs.slides.add_slide(layout)
    tg = add_text(s, 0.90, 0.55, 4.5, 0.25, [tag_line], 9.75, 'C9A227')
    tt = add_text(s, 0.90, 0.90, 11.5, 0.70, [title], 26, '2A2826', bold=True)
    movies = []
    for path, poster, x, y, w, h in videos:
        m = s.shapes.add_movie(path, Emu(int(x * EMU)), Emu(int(y * EMU)),
                               Emu(int(w * EMU)), Emu(int(h * EMU)),
                               poster_frame_image=poster, mime_type='video/mp4')
        movies.append(m)
    caps_shapes = []
    for x, y, w, lines in caps:
        caps_shapes.append(add_text(s, x, y, w, 0.75, lines, 11, '3A3A38', align_center=True))
    # 底部细线
    ln = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(int(0.90 * EMU)), Emu(int(7.02 * EMU)),
                            Emu(int(11.53 * EMU)), Emu(int(0.012 * EMU)))
    ln.fill.solid(); ln.fill.fore_color.rgb = RGBColor.from_string('E0CFA0')
    ln.line.fill.background(); ln.shadow.inherit = False

    g0 = [tg.shape_id, tt.shape_id] + [m.shape_id for m in movies]
    groups = [g0, [caps_shapes[0].shape_id], [caps_shapes[1].shape_id]]
    apply_timing(s, groups, autoplay_spids=autoplay)
    return s


# ---------- P08 韩雅平：两块 9:16 竖屏（素材为竖屏） ----------
VH = 4.60
VW = VH * 9 / 16          # 2.5875
GAP = 1.70
left_x = (13.333 - (VW * 2 + GAP)) / 2
right_x = left_x + VW + GAP
sA = make_page(
    'VIDEO · 微光影像',
    '两个瞬间：电话打进平房，行李踏上进京路',
    [(W + '/vidcmp/media1.mp4', W + '/fxv2/poster_h1.jpg', left_x, 1.35, VW, VH),
     (W + '/vidcmp/media5.mp4', W + '/fxv2/poster_h5.jpg', right_x, 1.35, VW, VH)],
    [(left_x - 0.85, 6.08, VW + 1.70,
      ['放榜凌晨，清华招生组的电话直接打进了那三间平房。',
       '那一刻，所有咬着牙的坚持都有了回音。']),
     (right_x - 0.85, 6.08, VW + 1.70,
      ['八月底，她独自去清华报到；父亲申请助学贷款。',
       '真正的托举，是帮一个人学会自己站稳。'])])

# ---------- P13 陈新超：两块 16:9 横屏（真实新闻影像 + 纪实照片缓推） ----------
VW2, VH2 = 5.55, 3.12
sB = make_page(
    'VIDEO · 微光影像',
    '邮路上的一天：从分拣台到返程的车',
    [(W + '/fxv2/cj_real.mp4', W + '/fxv2/poster_att2.jpg', 0.90, 1.70, VW2, VH2),
     (W + '/fxv2/cj_kb_b.mp4', W + '/fxv2/poster_b.jpg', 6.88, 1.70, VW2, VH2)],
    [(0.90, 5.06, VW2,
      ['镜头里她一边分拣一边说："心里特别的高兴。"',
       '把包裹递到老人手上的人，才知道这句话有多重。']),
     (6.88, 5.06, VW2,
      ['满载而归的路上，她记着十个村的每一户人家。',
       '山高路远，她把邮路走成了乡亲们最放心的归途。'])])

# 陈新超页：右侧照片缓推视频自动播放（重写时序，带上自动播放节点）
shapes = list(sB.shapes)
tag_s, ttl_s, mL, mR, capL, capR = shapes[0], shapes[1], shapes[2], shapes[3], shapes[4], shapes[5]
apply_timing(sB,
             [[tag_s.shape_id, ttl_s.shape_id, mL.shape_id, mR.shape_id],
              [capL.shape_id], [capR.shape_id]],
             autoplay_spids=[mR.shape_id])

# ---------- 页序：A 放 P08，B 放 P13 ----------
lst = prs.slides._sldIdLst
ids = list(lst)
newA, newB = ids[15], ids[16]
lst.remove(newA); lst.remove(newB)
list(lst)[6].addnext(newA)
list(lst)[11].addnext(newB)

prs.save(DST)
print('已保存 v13（17 页）')
