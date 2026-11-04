# -*- coding: utf-8 -*-
"""v12：在 v11（真原版+内容）基础上，为两人各加 1 页「微光影像」（每人 2 个视频）"""
import sys, shutil, copy
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from lxml import etree

sys.stdout.reconfigure(encoding='utf-8')
BASE = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58"
SRC = BASE + r"/微光成炬-星火自有燎原时（终版·v11）.pptx"
DST = BASE + r"/微光成炬-星火自有燎原时（终版·v12）.pptx"
W = BASE + r"/work"
shutil.copyfile(SRC, DST)
prs = Presentation(DST)
sl = list(prs.slides)
EMU = 914400
FONT = '微软雅黑'

layout = sl[9].slide_layout          # 沿用服务站页的版式（背景一致）


def set_run(r, text, size, color, bold=False):
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = RGBColor.from_string(color)
    r.font.name = FONT
    rPr = r._r.get_or_add_rPr()
    for tag in ('a:latin', 'a:ea'):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set('typeface', FONT)


def add_text(slide, x, y, w, h, lines, size, color, bold=False, spc=None):
    tb = slide.shapes.add_textbox(Emu(int(x * EMU)), Emu(int(y * EMU)),
                                  Emu(int(w * EMU)), Emu(int(h * EMU)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
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
    """groups: [[spid,...],...]；第一组 delay=0（进页即显），其余逐次点击。
    autoplay_spids 中的视频写入自动播放+循环媒体节点。"""
    blocks = []
    nid = 100
    # 第一组：进页即显（delay=0）
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


def video_page(tag_line, title, vL, vR, capL, capR, autoplay):
    s = prs.slides.add_slide(layout)
    tag = add_text(s, 0.90, 0.55, 4.5, 0.25, [tag_line], 9.75, 'C9A227')
    ttl = add_text(s, 0.90, 0.92, 11.5, 0.75, [title], 28, '2A2826', bold=True)
    mL = s.shapes.add_movie(vL['path'], Emu(int(0.90 * EMU)), Emu(int(2.05 * EMU)),
                            Emu(int(5.55 * EMU)), Emu(int(3.12 * EMU)),
                            poster_frame_image=vL['poster'], mime_type='video/mp4')
    mR = s.shapes.add_movie(vR['path'], Emu(int(6.88 * EMU)), Emu(int(2.05 * EMU)),
                            Emu(int(5.55 * EMU)), Emu(int(3.12 * EMU)),
                            poster_frame_image=vR['poster'], mime_type='video/mp4')
    cL = add_text(s, 0.90, 5.42, 5.55, 1.5, capL, 11.5, '3A3A38')
    cR = add_text(s, 6.88, 5.42, 5.55, 1.5, capR, 11.5, '3A3A38')
    apply_timing(s, [[tag.shape_id, ttl.shape_id, mL.shape_id, mR.shape_id],
                     [cL.shape_id], [cR.shape_id]],
                 autoplay_spids=autoplay)
    return s, mL, mR


# ---- 页 A：韩雅平（真实新闻视频，点击播放） ----
sA, _, _ = video_page(
    'VIDEO · 微光影像',
    '两个瞬间：电话打进平房，行李踏上进京路',
    {'path': W + '/vidcmp/media1.mp4', 'poster': W + '/fxv2/poster_h1.jpg'},
    {'path': W + '/vidcmp/media5.mp4', 'poster': W + '/fxv2/poster_h5.jpg'},
    ['放榜凌晨，清华招生组的电话直接打进了那三间平房。',
     '那一刻，所有咬着牙的坚持都有了回音——机会从不辜负准备了很多年的人。'],
    ['八月底，她独自去清华报到；父亲申请助学贷款，不让善意再多添一分负担。',
     '真正的托举，是帮一个人学会自己站稳。'],
    autoplay=())

# ---- 页 B：陈新超（纪实照片缓推，自动播放+循环） ----
sB, _, _ = video_page(
    'VIDEO · 微光影像',
    '邮路上的一天：满载而去，满载而归',
    {'path': W + '/fxv2/cj_kb_a.mp4', 'poster': W + '/fxv2/poster_a.jpg'},
    {'path': W + '/fxv2/cj_kb_b.mp4', 'poster': W + '/fxv2/poster_b.jpg'},
    ['镜头跟拍她的一天：清晨分拣装车，再为留守老人把包裹送上门。',
     '所谓坚守，就是把别人眼里的小事，日复一日做到位。'],
    ['满载而归的路上，她记着十个村的每一户人家。',
     '山高路远，她把邮路走成了乡亲们最放心的归途。'],
    autoplay='both')

# 修正页 B 自动播放标记（上面传了字符串，这里按真实 spid 重写 timing）
auto_ids = [sh.shape_id for sh in sB.shapes if sh.shape_type == 16]
apply_timing(sB, [[sh.shape_id for sh in sB.shapes][:4],
                  [sh.shape_id for sh in sB.shapes][4:5],
                  [sh.shape_id for sh in sB.shapes][5:6]],
             autoplay_spids=auto_ids)

# ---- 调整页序：A → P08 位置（原 P07 之后），B → 原陈新超段末尾（原 P11 之后） ----
lst = prs.slides._sldIdLst
ids = list(lst)
newA, newB = ids[15], ids[16]          # 刚加的两页在末尾
lst.remove(newA); lst.remove(newB)
# 目标顺序：0..6(原P01-07) + A + 7..10(原P08-11) + B + 11..14(原P12-15)
anchor7 = list(lst)[6]
anchor7.addnext(newA)
anchorB = list(lst)[11]                # 原 P11 现在在索引 11
anchorB.addnext(newB)

prs.save(DST)
print('页序:', [i for i in range(len(list(prs.slides)))])
print('已保存 v12（17 页）')
