# -*- coding: utf-8 -*-
"""按【小组原始版（最初草稿）】统帅式重做：15 页原封不动，只插入 7 页新页。
新页一律沿用小组原始版的视觉语言——
红渐变底(8E0000→C00000→9E0000)、纯红 FF0000 目录底、10% 米白条、米白 F7F4EE 双栏页、
Georgia 大金数字、STXingkai 书法标题、金色火焰母题、微软雅黑/仿宋正文。
"""
import sys, os, copy, re
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

DEEP   = RGBColor(0x8E, 0x00, 0x00)
RED    = RGBColor(0xFF, 0x00, 0x00)
RED2   = RGBColor(0xC0, 0x00, 0x00)
CREAM  = RGBColor(0xF7, 0xF4, 0xEE)
BANDC  = RGBColor(0xF3, 0xED, 0xDF)
GOLD   = RGBColor(0xE8, 0xC8, 0x7A)
GOLD2  = RGBColor(0xC9, 0xA2, 0x27)
DKGOLD = RGBColor(0xBE, 0x93, 0x2E)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
INK    = RGBColor(0x2A, 0x28, 0x25)
BODY   = RGBColor(0x3A, 0x3A, 0x38)
GREY   = RGBColor(0x8A, 0x83, 0x78)
YELLOW = RGBColor(0xFF, 0xFF, 0x00)

SANS  = "微软雅黑"
SERIF = "仿宋"
EN    = "Georgia"
XK    = "STXingkai"

# 原版字体元数据，逐字抄录自小组原始版：lang / panose / charset
# 用于让新页文字与原版字体识别码完全一致，避免渲染器回退成系统默认体
FONT_META = {
    "微软雅黑":  ("en-US", "020B0503020204020204", "-122"),
    "Georgia":   ("en-US", "02040502050405020303", None),
    "仿宋":      ("zh-CN", "02010609060101010101", "-122"),
    "STXingkai": ("zh-CN", None,                     None),
}

# 最老的版本：小组原始版（最初草稿）
BASE = r"D:\桌面\微光成炬_工作环境\01_初代版本\微光成炬-星火自有燎原时_小组原始版.pptx"
OUT  = r"D:\桌面\微光成炬_工作环境\06_成品输出\微光成炬-星火自有燎原时_重做版22页_终版.pptx"
VID  = r"D:\桌面\微光成炬_工作环境\02_视频素材"
IMG  = r"D:\桌面\微光成炬_工作环境\03_图片素材\人物与海报"
POST = r"D:\桌面\微光成炬_工作环境\03_图片素材\视频封面帧"


# ---------------- 基础 ----------------
def _ns(shp):
    try:
        shp.shadow.inherit = False
    except Exception:
        pass
    return shp


def _alpha_fill(shp, color, alpha_pct):
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    srgb = shp.fill._xPr.find(qn('a:solidFill')).find(qn('a:srgbClr'))
    a = parse_xml('<a:alpha %s val="%d"/>' % (nsdecls('a'), int(alpha_pct * 1000)))
    srgb.append(a)


def rect(s, x, y, w, h, fill, alpha=None, line=None, shape=MSO_SHAPE.RECTANGLE):
    shp = _ns(s.shapes.add_shape(shape, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h))))
    if fill is None:
        shp.fill.background()
    elif alpha is None:
        shp.fill.solid(); shp.fill.fore_color.rgb = fill
    else:
        _alpha_fill(shp, fill, alpha)
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line; shp.line.width = Pt(0.75)
    return shp


def red_grad(s, x, y, w, h, ang=5400000):
    """小组原始版红渐变：8E0000 → C00000 → 9E0000（三档，与 P5/P7/P11/P13 一致）"""
    shp = _ns(s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(int(x)), Emu(int(y)),
                                  Emu(int(w)), Emu(int(h))))
    shp.line.fill.background()
    xml = ('<a:gradFill %s rotWithShape="1"><a:gsLst>'
           '<a:gs pos="0"><a:srgbClr val="8E0000"/></a:gs>'
           '<a:gs pos="55000"><a:srgbClr val="C00000"/></a:gs>'
           '<a:gs pos="100000"><a:srgbClr val="9E0000"/></a:gs>'
           '</a:gsLst><a:lin ang="%d" scaled="1"/></a:gradFill>' % (nsdecls('a'), ang))
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


def grad_bg(s):
    """全屏红渐变（小组原始版标准红底）"""
    return red_grad(s, 0, 0, W, H)


def text(s, x, y, w, h, txt, size, color, font=SANS, align=PP_ALIGN.LEFT,
         spc=0, bold=True, spacing=1.2):
    tb = s.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = spacing
    r = p.add_run(); r.text = txt
    f = r.font
    f.size = Pt(size); f.bold = bold; f.color.rgb = color; f.name = font
    rPr = r._r.get_or_add_rPr()
    # 按原版逐字补全字体识别码：lang + 给 latin/ea 都写 panose/charset
    meta = FONT_META.get(font)
    if meta:
        lang, panose, charset = meta
        if lang:
            rPr.set('lang', lang)
        for tag in ('a:latin', 'a:ea'):
            el = rPr.find(qn(tag))
            if el is None:
                el = rPr.makeelement(qn(tag), {})
                rPr.append(el)
            el.set('typeface', font)
            if panose:
                el.set('panose', panose)
            if charset is not None:
                el.set('charset', charset)
    if spc:
        rPr.set('spc', str(int(spc)))
    return tb


def fade(s, x, y, w, h, color=DEEP, ang=0, a0=100000, a1=0):
    """左实右透的红色渐隐，盖在照片/视频左缘（与 P5/P7 一致）"""
    shp = _ns(s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(int(x)), Emu(int(y)),
                                 Emu(int(w)), Emu(int(h))))
    shp.line.fill.background()
    hexc = '%02X%02X%02X' % (color[0], color[1], color[2])
    xml = ('<a:gradFill %s rotWithShape="1"><a:gsLst>'
           '<a:gs pos="0"><a:srgbClr val="%s"><a:alpha val="%d"/></a:srgbClr></a:gs>'
           '<a:gs pos="100000"><a:srgbClr val="%s"><a:alpha val="%d"/></a:srgbClr></a:gs>'
           '</a:gsLst><a:lin ang="%d" scaled="0"/></a:gradFill>'
           % (nsdecls('a'), hexc, a0, hexc, a1, int(ang * 60000)))
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


def clone_shape(s, src_shape):
    """深拷贝一个非图片形状（文字/矩形）。图片请用 add_cloned_pic 重建关系。"""
    new_el = copy.deepcopy(src_shape._element)
    cNvPr = new_el.find('.//' + qn('p:cNvPr'))
    if cNvPr is not None:
        ids = [int(e.get('id')) for e in s.shapes._spTree.iter(qn('p:cNvPr'))
               if str(e.get('id', '')).isdigit()]
        nid = (max(ids) + 1) if ids else 2000
        nm = cNvPr.get('name')
        cNvPr.set('id', str(nid))
        if nm:
            cNvPr.set('name', nm.split()[0] + ' ' + str(nid))
    s.shapes._spTree.append(new_el)
    return s.shapes[-1]


def add_cloned_pic(s, src_shape, x, y, w, h):
    """提取源图片字节，用 add_picture 在新页重建（关系正确，不会丢图）"""
    from io import BytesIO
    blob = src_shape.image.blob
    return s.shapes.add_picture(BytesIO(blob), Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))


def find_pic(src_slide, name):
    for sh in src_slide.shapes:
        if sh.name == name:
            return sh
    return None


def clear(s):
    for sh in list(s.shapes):
        sh._element.getparent().remove(sh._element)


def new_slide(prs, at):
    layout = min(prs.slide_layouts, key=lambda l: len(l.placeholders))
    s = prs.slides.add_slide(layout)
    clear(s)
    lst = prs.slides._sldIdLst
    ids = list(lst)
    lst.remove(ids[-1])
    lst.insert(at, ids[-1])
    return s


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


def autoplay(slide, movie, vol=80000):
    el = slide._element
    for old in el.findall(qn('p:timing')):
        el.remove(old)
    node = parse_xml(VIDEO_TMPL.format(ns=nsdecls('p', 'a'), vol=vol, spid=movie.shape_id))
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


def _run_color_hex(run):
    try:
        return str(run.font.color.rgb)
    except Exception:
        return None


def harmonize_titles(prs):
    """按目录页四章名统一章节页：只改【黄色 PART 标签】里的
    「寒门筑梦 / 高山邮路」，使其与目录的「微光·韩雅平 / 成炬·陈新超」同名。
    1700+ 数据页的「高山邮路」是白字，不会误改。"""
    for s in prs.slides:
        for sh in s.shapes:
            if not sh.has_text_frame:
                continue
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if _run_color_hex(r) != 'FFFF00':
                        continue
                    if r.text == '寒门筑梦':
                        r.text = '微光 · 韩雅平'
                    elif r.text == '高山邮路':
                        r.text = '成炬 · 陈新超'


def replace_text(prs, old, new):
    """全文替换文字（含备注），用于按需求微调人名等。保留原 run 的字体识别码。"""
    for s in prs.slides:
        for sh in s.shapes:
            if sh.has_text_frame:
                for p in sh.text_frame.paragraphs:
                    for r in p.runs:
                        if old in r.text:
                            r.text = r.text.replace(old, new)
        if s.has_notes_slide:
            nt = s.notes_slide.notes_text_frame
            if nt is not None:
                for p in nt.paragraphs:
                    for r in p.runs:
                        if old in r.text:
                            r.text = r.text.replace(old, new)


def _is_team_page(s):
    """识别团队分工页（含'文案采编组'的页）。"""
    for sh in s.shapes:
        if sh.has_text_frame and '文案采编组' in sh.text_frame.text:
            return True
    return False


def enlarge_bold_all(prs, scale=1.12):
    """全局后处理：字号 ×scale，并重新分配字重（不再整页全加粗）。

    原做法是「所有 run 一律 bold」，一页里没有轻重对比，观感很死板。
    现按字号分档：>=24pt 大标题加粗、<=14pt 小组标注加粗（小字靠字重提清晰度）、
    15~23pt 的正文一律常规字重——字有轻重，页面才有呼吸。
    仿宋恒不加粗：它没有真粗体，合成粗会把笔画撑糊。
    团队分工页另由 polish_team 处理，这里跳过。"""
    for s in prs.slides:
        if _is_team_page(s):
            continue
        for sh in s.shapes:
            if sh.has_text_frame:
                for p in sh.text_frame.paragraphs:
                    for r in p.runs:
                        if not r.text.strip():
                            continue
                        try:
                            if r.font.size is not None:
                                r.font.size = Pt(round(r.font.size.pt * scale, 1))
                        except Exception:
                            pass
                        try:
                            _sz = r.font.size.pt if r.font.size else 18
                            if r.font.name == SERIF:
                                r.font.bold = False          # 仿宋无真粗体
                            else:
                                r.font.bold = (_sz >= 24) or (_sz <= 14)
                        except Exception:
                            pass
        if s.has_notes_slide:
            nt = s.notes_slide.notes_text_frame
            if nt is not None:
                for p in nt.paragraphs:
                    for r in p.runs:
                        if not r.text.strip():
                            continue
                        try:
                            if r.font.size is not None:
                                r.font.size = Pt(round(r.font.size.pt * scale, 1))
                        except Exception:
                            pass
                        try:
                            _sz = r.font.size.pt if r.font.size else 18
                            if r.font.name == SERIF:
                                r.font.bold = False          # 仿宋无真粗体
                            else:
                                r.font.bold = (_sz >= 24) or (_sz <= 14)
                        except Exception:
                            pass


def normalize_fonts(prs):
    """根治字体乱码（依据 GitHub red-patriot-youth / GordenPPTSkill 字体规范）：
    - 中文字符一律由 a:ea=微软雅黑 渲染，绝不落在 Georgia/STXingkai/仿宋 上；
    - 英文/数字由 a:latin 保留原设计字体（Georgia），双语各得其所；
    - 偏门字体别名归一为通用字体，移除与字体名不匹配的 panose/pitchFamily，
      避免 WPS / 在线预览按错误识别码选字体而产生豆腐块与乱字。
    """
    CJK = re.compile(r'[\u4e00-\u9fff]')
    # 仿宋是原版金句/引文的衬线字体，本身就是设计的一部分，不能归一掉；
    # 只把真正缺字的手写体（STXingkai / 华文行楷）与英文名归一到雅黑。
    ALIAS = {'STXingkai': '微软雅黑', '华文行楷': '微软雅黑',
             'Microsoft YaHei': '微软雅黑'}
    CJK_OK = ('微软雅黑', '仿宋')          # 合法中文字体白名单

    def _fix_font_el(el, fallback):
        tf = el.get('typeface') or fallback
        tf = ALIAS.get(tf, tf)
        el.set('typeface', tf)
        for a in ('panose', 'pitchFamily', 'charset'):
            if a in el.attrib:
                del el.attrib[a]

    for s in prs.slides:
        for sh in s.shapes:
            if not sh.has_text_frame:
                continue
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if not r.text.strip():
                        continue
                    rPr = r._r.get_or_add_rPr()
                    cjk = bool(CJK.search(r.text))
                    lat = rPr.find(qn('a:latin'))
                    ea = rPr.find(qn('a:ea'))
                    if lat is None:
                        lat = rPr.makeelement(qn('a:latin'), {})
                        if ea is not None:
                            ea.addprevious(lat)
                        else:
                            rPr.append(lat)
                    if ea is None:
                        ea = rPr.makeelement(qn('a:ea'), {})
                        rPr.append(ea)
                    # ① 先定中文字体：白名单内保留（仿宋是原版金句的衬线体），
                    #    其余——包括 8 处误指 Georgia 的——统一归到微软雅黑。
                    if (ea.get('typeface') or '') not in CJK_OK:
                        ea.set('typeface', '微软雅黑')
                    for a in ('panose', 'pitchFamily', 'charset'):
                        if a in ea.attrib:
                            del ea.attrib[a]
                    # ② 再定拉丁字体：含中文的 run 必须与 ea 同字体，否则「整段只认
                    #    latin」的渲染器会把中文画成豆腐块；纯拉丁 run 保留 Georgia。
                    if cjk:
                        lat.set('typeface', ea.get('typeface') or '微软雅黑')
                        for a in ('panose', 'pitchFamily', 'charset'):
                            if a in lat.attrib:
                                del lat.attrib[a]
                    else:
                        _fix_font_el(lat, 'Georgia')
                    rPr.set('lang', 'zh-CN' if cjk else 'en-US')


def split_mixed_runs(prs):
    """把「英文 + 中文」混在同一个 run 里的文字，按字形拆成独立 run。

    原版大量副标题形如 `HAN YAPING · 寒门苦读 · 圆梦清华`：一个 run 里同时有
    a:latin=Georgia 和 a:ea=微软雅黑。PowerPoint / WPS 会按脚本自动切换，
    但部分渲染器（在线预览、LibreOffice、导出引擎）整段只认 a:latin，
    中文字符就掉成豆腐块——这正是「字体乱码」的观感来源。

    拆成 run 后：中文段 latin=ea=微软雅黑（必中文字形），英文段保留 Georgia，
    任何渲染器都不会再出错，且英文的衬线质感完整保留。"""
    CJK = re.compile(r'[\u4e00-\u9fff]')

    def _seg(text):
        out, cur, kind = [], '', None
        for ch in text:
            k = 'c' if CJK.match(ch) else 'l'
            if kind is None or k == kind:
                cur += ch
            else:
                out.append((kind, cur))
                cur, kind = ch, k
            kind = k
        if cur:
            out.append((kind, cur))
        return out

    def _set(el, kind):
        rPr = el.find(qn('a:rPr'))
        if rPr is None:
            return
        ea = rPr.find(qn('a:ea'))
        if ea is None:
            ea = rPr.makeelement(qn('a:ea'), {})
            rPr.append(ea)
        keep = ea.get('typeface') or ''
        if keep not in ('微软雅黑', '仿宋'):   # 只认合法中文字体，其余归一到雅黑
            keep = '微软雅黑'
        ea.set('typeface', keep)
        for a in ('panose', 'pitchFamily', 'charset'):
            if a in ea.attrib:
                del ea.attrib[a]
        rPr.set('lang', 'zh-CN' if kind == 'c' else 'en-US')
        if kind == 'c':                      # 中文段连 latin 一起指向中文字体
            lat = rPr.find(qn('a:latin'))
            if lat is not None:
                lat.set('typeface', keep)
                for a in ('panose', 'pitchFamily', 'charset'):
                    if a in lat.attrib:
                        del lat.attrib[a]

    cnt = 0
    for s in prs.slides:
        for sh in s.shapes:
            if not sh.has_text_frame:
                continue
            for p in sh.text_frame.paragraphs:
                for r in list(p._p.findall(qn('a:r'))):
                    t = r.find(qn('a:t'))
                    if t is None or not t.text:
                        continue
                    sp = _seg(t.text)
                    if len(sp) < 2 or not any(k == 'c' for k, _ in sp):
                        continue                 # 纯中文或纯英文，无需拆
                    anchor = r
                    for kind, txt in sp:
                        new = copy.deepcopy(r)
                        nt = new.find(qn('a:t'))
                        nt.text = txt
                        nt.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                        _set(new, kind)
                        anchor.addnext(new)
                        anchor = new
                    r.getparent().remove(r)
                    cnt += 1
    print("中英混排 run 拆分:", cnt, "处")


def relax_leading(prs, target=1.32):
    """给正文段落松一行气：15~23pt 的多字正文，行距 1.2 → 1.32。

    这套稿子的正文原本贴着 1.2 倍行距，配上 18pt 字号显得拥挤发闷；
    标题、金句、短标注都不动，只放宽真正成段的说明文字。"""
    for s in prs.slides:
        for sh in s.shapes:
            if not sh.has_text_frame:
                continue
            for p in sh.text_frame.paragraphs:
                txt = "".join(r.text for r in p.runs)
                if len(txt) < 28:
                    continue
                szs = [r.font.size.pt for r in p.runs if r.font.size]
                if not szs:
                    continue
                if 14.5 <= max(szs) <= 23:
                    p.line_spacing = target


def polish_team(prs):
    """团队页字体美化：在原版字号/字距/字重层级基础上做温和微调——
    组名 13.5→14、姓名 11.25→12（维持常规字重，靠字重对比而非全加粗形成层级）、
    职责 9.4→10；保留原版疏排字距（组名 150 / 姓名职责 75），更透气温润。"""
    for s in prs.slides:
        if not _is_team_page(s):
            continue
        for sh in s.shapes:
            if not sh.has_text_frame:
                continue
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if not r.text.strip() or not r.font.size:
                        continue
                    sz = r.font.size.pt
                    if 13 <= sz <= 14:            # 组名
                        r.font.size = Pt(14)
                        r._r.get_or_add_rPr().set('spc', '150')
                    elif 11 <= sz < 12:           # 姓名 / ·主讲 / ·统筹
                        r.font.size = Pt(12)
                    elif 9 <= sz < 10:            # 职责说明
                        r.font.size = Pt(10)


def set_note(slide, txt):
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
    tf.text = txt


# ---------------- 新页（小组原始版语言） ----------------
def page_opening(s):
    """片头：黑底全屏视频，自动播放（与封面 P1 黑金氛围一致）"""
    rect(s, 0, 0, W, H, RGBColor(0x0A, 0x0A, 0x0A))
    mv = add_video(s, os.path.join(VID, "开场_微光成炬_16x9.mp4"),
                   os.path.join(POST, "poster_开场.jpg"))
    text(s, 9.30 * IN, 7.06 * IN, 3.40 * IN, 0.24 * IN, "OPENING", 9, GOLD,
         font=EN, align=PP_ALIGN.RIGHT, spc=400, bold=False)
    return mv


def page_toc(s):
    """大目录（参考 GitHub red-patriot-youth + WPS 官方目录规范重做）：
    红底 + 左侧金强调条 + 金线分隔 + 4 章节竖排列表；
    字号层级：编号 60-80pt 视觉锚点 / 章节标题 24-36pt 加粗 / 英文副标 14-18pt。
    字号为预放大值，enlarge_bold_all(×1.12) 后落入规范区间。"""
    clear(s)
    rect(s, 0, 0, W, H, RED)
    rect(s, 0.0 * IN, 0.0 * IN, 0.16 * IN, H, GOLD2, alpha=90)      # 左侧金色强调条（与小目录统一）

    # 头部
    text(s, 1.00 * IN, 0.40 * IN, 3.0 * IN, 0.20 * IN, "CONTENTS", 11, GOLD,
         font=EN, spc=600, bold=True)
    text(s, 1.00 * IN, 0.72 * IN, 5.0 * IN, 0.70 * IN, "目录", 34, BANDC,
         font=SANS, spc=200, bold=True)
    text(s, 1.00 * IN, 1.46 * IN, 6.2 * IN, 0.22 * IN, "FOUR CHAPTERS · ONE STORY", 12,
         BANDC, font=EN, spc=300, bold=False)
    text(s, 9.00 * IN, 0.46 * IN, 3.33 * IN, 0.22 * IN, "拾光者小组 · 十五人", 9, BANDC,
         align=PP_ALIGN.RIGHT, spc=200, bold=False)
    text(s, 9.00 * IN, 0.78 * IN, 3.33 * IN, 0.22 * IN, "FROM SPARK TO FLAME", 9, BANDC,
         font=EN, align=PP_ALIGN.RIGHT, spc=300, bold=False)
    rect(s, 1.00 * IN, 1.78 * IN, 11.33 * IN, 0.014 * IN, GOLD, alpha=100)   # 主金线

    ROWS = [
        ("01", "微光 · 韩雅平", "PART 01 · A LIGHT FROM A VILLAGE HOME"),
        ("02", "成炬 · 陈新超", "PART 02 · THE ROAD POSTWOMAN"),
        ("03", "燎原 · 微光成炬", "EPILOGUE · TWO GLIMMERS, ONE TORCH"),
        ("04", "致谢", "CREDITS · ACKNOWLEDGEMENTS"),
    ]
    y = 1.95 * IN
    for num, title, sub in ROWS:
        # 大编号（视觉锚点）
        text(s, 1.00 * IN, y + 0.04 * IN, 1.45 * IN, 1.05 * IN, num, 64, GOLD,
             font=EN, bold=False)
        rect(s, 2.55 * IN, y + 0.16 * IN, 0.014 * IN, 0.78 * IN, GOLD, alpha=70)
        # 章节标题 + 英文副标
        text(s, 2.82 * IN, y + 0.12 * IN, 7.4 * IN, 0.50 * IN, title, 28, BANDC,
             spc=120, bold=True)
        text(s, 2.82 * IN, y + 0.66 * IN, 8.2 * IN, 0.26 * IN, sub, 14, BANDC,
             font=EN, spc=200, bold=False)
        rect(s, 1.00 * IN, y + 1.12 * IN, 11.33 * IN, 0.008 * IN, GOLD, alpha=35)
        y += 1.20 * IN


def page_mini(s, num, over, title, items, quote):
    """小目录（按 WPS 官方规范修版）：编号 60-80pt 视觉锚点、标题 24-36pt 加粗、
    条目 14-18pt；右上大数字收在头部区内，不与卡片重叠（字号为预放大值，×1.12 后落区间）。"""
    clear(s)
    rect(s, 0, 0, W, H, RED)                                       # 红底
    rect(s, 0.0 * IN, 0.0 * IN, 0.16 * IN, H, GOLD2, alpha=90)      # 左侧金色强调条
    # 右上大数字：64pt(预)→72pt(后)，盒底 2.02in，卡片最早 2.6in 起，不重叠
    text(s, 8.60 * IN, 0.52 * IN, 3.70 * IN, 1.50 * IN, num, 64, GOLD,
         font=EN, align=PP_ALIGN.RIGHT, bold=False)
    # 顶部 over 标签
    text(s, 1.00 * IN, 0.66 * IN, 7.0 * IN, 0.20 * IN, over, 11, GOLD, font=EN, spc=600, bold=True)
    # 标题：29pt(预)→32.5pt(后)，WPS 区间 24-36
    text(s, 1.00 * IN, 1.10 * IN, 7.2 * IN, 0.66 * IN, title, 29, BANDC, font=SANS, spc=120, bold=True)
    # 金色分隔线
    rect(s, 1.00 * IN, 1.94 * IN, 5.4 * IN, 0.018 * IN, GOLD, alpha=100)
    # 项目卡片
    n = len(items)
    a_top, a_bot = 2.40 * IN, 5.66 * IN
    bh = (1.06 if n <= 2 else 0.82) * IN
    gap = (0.24 if n <= 2 else 0.18) * IN
    fs = 16                                   # 16(预)→18(后)，WPS 条目区间 14-18
    y = a_top + max(0, ((a_bot - a_top) - (n * bh + (n - 1) * gap)) / 2)
    for i, t in enumerate(items):
        rect(s, 1.00 * IN, y, 11.33 * IN, bh, BANDC, alpha=10)      # 半透明奶油卡片
        rect(s, 1.24 * IN, y + (bh - 0.56 * IN) / 2, 0.56 * IN, 0.56 * IN, GOLD, alpha=100)  # 金徽标
        text(s, 1.24 * IN, y + (bh - 0.56 * IN) / 2, 0.56 * IN, 0.56 * IN,
             "%02d" % (i + 1), 15, RED2, font=EN, align=PP_ALIGN.CENTER, bold=True)
        text(s, 2.10 * IN, y + (bh - 0.44 * IN) / 2, 10.0 * IN, 0.44 * IN,
             t, fs, BANDC, spc=40, bold=True)
        y += bh + gap
    # 底部引语
    rect(s, 1.00 * IN, 5.94 * IN, 11.33 * IN, 0.012 * IN, GOLD, alpha=100)
    text(s, 1.00 * IN, 6.14 * IN, 11.33 * IN, 0.50 * IN, quote, 14.5, BANDC, font=SERIF, spc=60, bold=False)


def page_guma(s):
    """顾妈妈：与 699 / 1700+ 同一套的数据页 —— 一个大金数字 + 大字，不堆长介绍（仿 P7）"""
    clear(s)
    grad_bg(s)
    pic_cover(s, os.path.join(IMG, "guma_portrait.jpg"), 7.92 * IN, 0, 5.42 * IN, 7.5 * IN)
    fade(s, 7.92 * IN, 0, 1.35 * IN, 7.5 * IN, DEEP, ang=0, a0=100000, a1=0)

    text(s, 0.52 * IN, 0.42 * IN, 4.60 * IN, 0.20 * IN, "PART 01 · 一封写了十二年的信", 20,
         YELLOW, spc=300, bold=True)
    text(s, 0.67 * IN, 0.94 * IN, 7.10 * IN, 4.50 * IN, "12", 270, GOLD, font=EN, spc=-400, bold=False)
    text(s, 0.67 * IN, 4.77 * IN, 4.20 * IN, 0.33 * IN, "年 · 一对一资助", 19.5, WHITE, spc=450, bold=True)
    text(s, 0.88 * IN, 5.62 * IN, 4.00 * IN, 0.19 * IN, "从 6 岁到 18 岁 · 不曾间断", 13, WHITE, spc=200, bold=False)
    text(s, 0.88 * IN, 6.83 * IN, 4.20 * IN, 0.24 * IN, "十二封长信，写满陌生人之间的牵挂", 13, WHITE, spc=200, bold=False)
    text(s, 5.10 * IN, 6.83 * IN, 3.20 * IN, 0.22 * IN, "TWELVE YEARS OF LETTERS", 9.8, GOLD,
         font=EN, spc=225, bold=False)


def page_video(s, num, part_label, big_cn, name_cn, name_en, caption_cn,
               video, poster=None, photo_x=7.01 * IN, photo_w=7.80 * IN,
               fade_x=6.32 * IN, fade_w=1.81 * IN):
    """视频页：满屏视频（16:9 完美填满）+ 左侧红渐变文字板 + 红色渐隐（仿 P5/P8 章节页）"""
    clear(s)
    mv = add_video(s, video, poster)              # 满屏 16:9 视频
    red_grad(s, 0, 0, fade_x + 0.01 * IN, H)      # 左侧不透明红渐变板，遮住视频左半
    fade(s, fade_x, 0, fade_w, H, DEEP, ang=0, a0=100000, a1=0)  # 红→透，视频自右缘浮现

    text(s, 0.62 * IN, 0.56 * IN, 3.20 * IN, 3.00 * IN, num, 150, GOLD, font=EN, bold=False)
    text(s, 0.24 * IN, 0.40 * IN, 3.60 * IN, 0.17 * IN, part_label, 13, YELLOW, spc=300, bold=True)
    text(s, 0.94 * IN, 2.46 * IN, 3.75 * IN, 1.31 * IN, big_cn, 54, WHITE, spc=200, bold=True)
    text(s, 1.00 * IN, 4.04 * IN, 3.20 * IN, 0.38 * IN, name_cn, 26, WHITE, spc=300, bold=True)
    text(s, 0.73 * IN, 4.67 * IN, 4.50 * IN, 0.18 * IN, name_en, 12, YELLOW, font=EN, spc=150, bold=False)
    text(s, 0.35 * IN, 5.43 * IN, 5.40 * IN, 0.40 * IN, caption_cn, 15, YELLOW, spc=120, bold=False)
    rect(s, 1.00 * IN, 6.72 * IN, 0.75 * IN, 0.03 * IN, GOLD)
    return mv


def page_quotes(s, flame_src):
    """两句话：米白双栏对照页，中央金色火焰母题（仿小组原始版 P12）"""
    clear(s)
    rect(s, 0, 0, W, H, CREAM)
    # 顶部红色标签
    rect(s, 0.71 * IN, 0.58 * IN, 1.89 * IN, 0.28 * IN, RED2)
    text(s, 0.88 * IN, 0.645 * IN, 1.55 * IN, 0.16 * IN, "EPILOGUE · 两句话", 9, WHITE, spc=300, bold=True)
    # 中央金色火焰母题（复用小组原始版图，按双栏页原坐标重建）
    fl = find_pic(flame_src, "图片 112")
    if fl is not None:
        add_cloned_pic(s, fl, 4.59 * IN, 2.44 * IN, 3.42 * IN, 8.32 * IN)

    # 左栏：韩雅平
    text(s, 0.10 * IN, 3.24 * IN, 5.25 * IN, 0.10 * IN,
         "韩雅平 · 寒门圆梦", 16, RED2, spc=60, bold=True)
    text(s, 0.36 * IN, 3.74 * IN, 5.21 * IN, 1.00 * IN,
         "不吃学习的苦，\n就要吃生活的苦。", 24, BODY, font=SERIF, spc=60, spacing=1.3, bold=False)
    text(s, 0.36 * IN, 5.10 * IN, 5.21 * IN, 0.26 * IN,
         "河南郏县 · 物理类 699 分 · 圆梦清华", 12, GREY, spc=90, bold=False)
    # 右栏：陈新超
    text(s, 7.87 * IN, 3.24 * IN, 5.25 * IN, 0.10 * IN,
         "陈新超 · 乡邮坚守", 16, RED2, spc=60, bold=True)
    text(s, 8.13 * IN, 3.74 * IN, 5.21 * IN, 1.00 * IN,
         "我是党员，应该做榜样。\n只要身体允许，就一直做下去。", 24, BODY, font=SERIF, spc=60, spacing=1.3, bold=False)
    text(s, 8.13 * IN, 5.10 * IN, 5.21 * IN, 0.26 * IN,
         "湖北阳新 · 乡邮员 · 荆楚楷模", 12, GREY, spc=90, bold=False)
    # 分隔细线
    rect(s, 6.51 * IN, 1.56 * IN, 0.01 * IN, 2.81 * IN, RGBColor(0x00, 0x00, 0x00), alpha=10)


# ---------------- 主流程 ----------------
def main():
    prs = Presentation(BASE)
    flame_src = prs.slides[11]          # 小组原始版双栏页，含金色火焰母题图（插入新页前先锁定）
    print("小组原始版页数:", len(prs.slides))

    s_open = new_slide(prs, 0)     # P1  开机视频
    s_guma = new_slide(prs, 8)     # P9  顾妈妈
    s_vhy  = new_slide(prs, 9)     # P10 韩雅平视频
    s_vcx  = new_slide(prs, 14)    # P15 陈新超视频
    s_quot = new_slide(prs, 15)    # P16 两句话
    s_liao = new_slide(prs, 16)    # P17 燎原小目录
    s_thx  = new_slide(prs, 18)    # P19 致谢小目录
    print("插入后:", len(prs.slides))
    sl = list(prs.slides)

    mv_open = page_opening(sl[0])
    page_toc(sl[3])
    page_guma(sl[8])
    mv_hy = page_video(sl[9], "01", "PART 01 · 寒门筑梦", "微光", "韩雅平",
                       "HAN YAPING · 寒门苦读 · 圆梦清华",
                       "镜头里的她，说出了那句让全场安静的话。",
                       os.path.join(VID, "韩雅平_699分清华采访_16x9.mp4"),
                       os.path.join(POST, "poster_韩雅平.jpg"),
                       photo_x=7.01 * IN, photo_w=7.80 * IN, fade_x=6.32 * IN, fade_w=1.81 * IN)
    mv_cx = page_video(sl[14], "02", "PART 02 · 高山邮路", "成炬", "陈新超",
                       "CHEN XINCHAO · 抗癌 · 坚守 · 送暖",
                       "一辆没空调的旧货车，开出了两万人的暖。",
                       os.path.join(VID, "陈新超_新时代的我们_荆楚楷模_高清.mp4"),
                       os.path.join(POST, "poster_陈新超.jpg"),
                       photo_x=7.75 * IN, photo_w=6.42 * IN, fade_x=6.56 * IN, fade_w=1.57 * IN)
    page_quotes(sl[15], flame_src)   # 火焰母题取自小组原始版双栏页
    page_mini(sl[16], "03", "EPILOGUE", "燎原 · 微光成炬",
              ["一张书桌，撑起一座山",
               "把邮路走成归途",
               "同一种选择"],
              "“知识改变命运；而善意，让命运有了另一条路。”")
    page_mini(sl[18], "04", "CREDITS", "致谢 · 谢谢聆听",
              ["五个小组，十五个人",
               "星火自有燎原时"],
              "十五人同行，共燃一盏灯。")

    for s_, mv in ((sl[0], mv_open), (sl[9], mv_hy), (sl[14], mv_cx)):
        autoplay(s_, mv)

    # 注意：不再执行 harmonize_titles —— 按用户要求，章节页副标题回退为原版
    # 的「寒门筑梦 / 高山邮路」（原版本身分节页与目录页章节名就不一致，属正常）

    replace_text(prs, "辛夏瑶", "陈昕越")   # 主讲人改名（同为设计师，一人兼任两职）
    replace_text(prs, " 黄淑淼/ 林泽凯", "黄淑淼 / 林泽凯")   # 原版此处漏空格，与其余行统一
    split_mixed_runs(prs)                  # 中英混排拆 run：根治豆腐块，保住英文 Georgia
    enlarge_bold_all(prs, 1.12)            # 所有字体加大加粗（团队页除外，恢复原样）
    normalize_fonts(prs)                   # 字体归一，根治乱码
    relax_leading(prs)                     # 正文行距放松，避免拥挤发闷
    polish_team(prs)                       # 团队页字体轻量美化

    NOTES = {
        0: "开场片头（约 8 秒）：自动播放，全场安静看完再翻页。",
        3: "大目录：四章，一句话带过，20 秒。",
        4: "团队分工：五个组，十五个人，8 秒带过。",
        5: "PART 01 章节页：停 3 秒，让「微光」两个字立住。",
        8: "顾妈妈：全场情绪的第一个高点，慢讲，约 55 秒。",
        9: "采访视频：先给一句引导，播 1 分钟左右。",
        14: "陈新超视频：同上，播 1 分钟左右。",
        15: "两句话：过渡页，20 秒，准备收束。",
        16: "燎原小目录：40 秒。",
        17: "尾声：两张答卷并置，50 秒收。",
        18: "致谢小目录：20 秒。",
    }
    fails = 0
    for i, s_ in enumerate(prs.slides):
        if i in NOTES:
            try:
                set_note(s_, NOTES[i])
            except Exception as e:
                fails += 1
                print("  备注失败 P%d: %s" % (i + 1, e))
    print("备注写入:", len(NOTES) - fails, "/", len(NOTES))

    prs.save(OUT)
    print("已保存:", OUT, "共", len(prs.slides), "页")


if __name__ == "__main__":
    main()
