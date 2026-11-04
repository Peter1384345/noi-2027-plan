# -*- coding: utf-8 -*-
"""PPT 页面近似渲染器 v2：支持纯色/渐变填充、图片(含裁切)、文字(字号/颜色/对齐)。
用途是核对排版，不是最终出图。"""
import sys, io
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.oxml.ns import qn

P = sys.argv[1]
IDX = int(sys.argv[2])
OUT = sys.argv[3] if len(sys.argv) > 3 else "preview.png"

EMU = 914400
PXW = 1600

FONTS = {
    "微软雅黑": r"C:\Windows\Fonts\msyh.ttc",
    "Microsoft YaHei": r"C:\Windows\Fonts\msyh.ttc",
    "Georgia": r"C:\Windows\Fonts\georgia.ttf",
    "仿宋": r"C:\Windows\Fonts\simfang.ttf",
    "STXingkai": r"C:\Windows\Fonts\STXINGKA.TTF",
}
_cache = {}


def getfont(name, size_px, bold=False):
    key = (name, int(size_px), bold)
    if key in _cache:
        return _cache[key]
    path = FONTS.get(name)
    f = None
    if path:
        try:
            f = ImageFont.truetype(path, max(1, int(size_px)))
        except Exception:
            f = None
    if f is None:
        f = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", max(1, int(size_px)))
    _cache[key] = f
    return f


def parse_fill(spPr):
    """返回 ('solid',(r,g,b),alpha) / ('grad',[(pos,(r,g,b),alpha)],ang) / None"""
    if spPr is None:
        return None

    def color_of(node):
        srgb = node.find(qn('a:srgbClr'))
        if srgb is not None:
            v = srgb.get('val')
            a = srgb.find(qn('a:alpha'))
            al = int(a.get('val')) / 1000.0 if a is not None else 100.0
            return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)), al
        sc = node.find(qn('a:schemeClr'))
        if sc is not None:
            m = {"accent4": (0xFF, 0xC0, 0x00), "accent1": (0x44, 0x72, 0xC4),
                 "dk1": (0, 0, 0), "lt1": (255, 255, 255),
                 "bg1": (255, 255, 255), "bg2": (247, 244, 238),
                 "tx1": (26, 22, 20), "tx2": (74, 63, 57)}
            return m.get(sc.get('val'), (0x88, 0x88, 0x88)), 100.0
        return None, 100.0

    sf = spPr.find(qn('a:solidFill'))
    if sf is not None:
        c, a = color_of(sf)
        if c:
            return ('solid', c, a)
    gf = spPr.find(qn('a:gradFill'))
    if gf is not None:
        gs = gf.find(qn('a:gsLst'))
        stops = []
        if gs is not None:
            for g in gs.findall(qn('a:gs')):
                pos = int(g.get('pos')) / 100000.0
                c, a = color_of(g)
                if c:
                    stops.append((pos, c, a))
        lin = gf.find(qn('a:lin'))
        ang = int(lin.get('ang')) / 60000.0 if lin is not None else 0.0
        if stops:
            return ('grad', stops, ang)
    return None


def grad_image(w, h, stops, ang):
    n = 320
    line = Image.new("RGBA", (n, 1))
    px = line.load()
    for i in range(n):
        p = i / (n - 1)
        lo = stops[0]
        hi = stops[-1]
        for k in range(len(stops) - 1):
            if stops[k][0] <= p <= stops[k + 1][0]:
                lo, hi = stops[k], stops[k + 1]
                break
        span = (hi[0] - lo[0]) or 1
        t = (p - lo[0]) / span
        t = 0 if t < 0 else (1 if t > 1 else t)
        r = int(lo[1][0] + (hi[1][0] - lo[1][0]) * t)
        g = int(lo[1][1] + (hi[1][1] - lo[1][1]) * t)
        b = int(lo[1][2] + (hi[1][2] - lo[1][2]) * t)
        a = int(lo[2] + (hi[2] - lo[2]) * t)
        px[i, 0] = (r, g, b, int(a / 100.0 * 255))
    vertical = 45 <= (ang % 180) <= 135
    if vertical:
        line = line.rotate(-90, expand=True)
    return line.resize((max(1, w), max(1, h)), Image.BILINEAR)


prs = Presentation(P)
s = prs.slides[IDX]
SW, SH = prs.slide_width / EMU, prs.slide_height / EMU
K = PXW / SW
PXH = int(SH * K)
PT = K / 72.0

img = Image.new("RGB", (PXW, PXH), (255, 255, 255))
draw = ImageDraw.Draw(img)


def cust_poly(sh, L, T, W, H):
    """把 a:custGeom 的路径还原成屏幕坐标多边形；不是自由多边形则返回 None。
    WPS 里的「细红色竖标」等装饰形状外框和路径不同，按外框填充会整块铺红。"""
    try:
        sp = sh._element.find(qn('p:spPr'))
        if sp is None:
            return None
        cg = sp.find(qn('a:custGeom'))
        if cg is None:
            return None
        path = cg.find(qn('a:pathLst'))
        if path is None:
            return None
        path = path.find(qn('a:path'))
        if path is None:
            return None
        pw = float(path.get('w') or 1) or 1.0
        ph = float(path.get('h') or 1) or 1.0
        pts = []
        for node in path:
            if node.tag not in (qn('a:moveTo'), qn('a:lnTo')):
                continue
            p = node.find(qn('a:pt'))
            if p is None:
                continue
            pts.append((L + float(p.get('x')) / pw * W,
                        T + float(p.get('y')) / ph * H))
        return pts if len(pts) >= 3 else None
    except Exception:
        return None


def box_of(sh):
    return (sh.left or 0) / EMU * K, (sh.top or 0) / EMU * K, \
           (sh.width or 0) / EMU * K, (sh.height or 0) / EMU * K


def paste_rgba(layer, x, y):
    global img
    base = img.convert("RGBA")
    base.alpha_composite(layer, (int(x), int(y)))
    img = base.convert("RGB")
    globals()['draw'] = ImageDraw.Draw(img)


for sh in s.shapes:
    L, T, W, H = box_of(sh)
    st = str(sh.shape_type)

    # ---- 图片 ----
    if 'PICTURE' in st:
        try:
            im = Image.open(io.BytesIO(sh.image.blob))
            if im.mode == 'P' and im.info.get('transparency') is not None:
                im = im.convert("RGBA")
            elif im.mode not in ("RGBA", "LA"):
                im = im.convert("RGBA")
            cw, ch = im.size
            cl = (sh.crop_left or 0) * cw
            cr = (sh.crop_right or 0) * cw
            ct = (sh.crop_top or 0) * ch
            cb = (sh.crop_bottom or 0) * ch
            im = im.crop((int(cl), int(ct), int(cw - cr), int(ch - cb)))
            if W > 1 and H > 1:
                im = im.resize((max(1, int(W)), max(1, int(H))))
                paste_rgba(im, L, T)
        except Exception as e:
            pass
        continue

    # ---- 填充 ----
    fill = parse_fill(sh._element.spPr if hasattr(sh._element, 'spPr') else None)
    poly = cust_poly(sh, L, T, W, H)          # 自由多边形按真实路径画，不按外框铺满
    if fill and poly:
        if fill[0] == 'solid':
            draw.polygon(poly, fill=fill[1])
    elif fill and W > 1 and H > 1:
        if fill[0] == 'solid':
            _, c, a = fill
            if a >= 99:
                draw.rectangle([L, T, L + W, T + H], fill=c)
            elif a > 0:
                layer = Image.new("RGBA", (max(1, int(W)), max(1, int(H))), c + (int(a / 100 * 255),))
                paste_rgba(layer, L, T)
        else:
            _, stops, ang = fill
            layer = grad_image(int(W), int(H), stops, ang)
            paste_rgba(layer, L, T)
        if not sh.has_text_frame:
            continue

    if not sh.has_text_frame:
        continue

    # ---- 文字 ----
    tf = sh.text_frame
    # 先做一遍预排版，才能支持垂直居中。逐 run 取字体/颜色/字号，
    # 这样「英文 Georgia + 中文 微软雅黑」的混排才能被如实还原。
    PRE = []
    for para in tf.paragraphs:
        runs = [(r.text, r.font) for r in para.runs]
        if not any(t.strip() for t, _ in runs):
            PRE.append(None)
            continue
        base = runs[0][1]
        size_pt = (base.size.pt if base.size else 18)
        # 文本框 wrap="none"（python-pptx 读作 word_wrap=False）时不折行，只向右溢出
        MAXW = 1e9 if tf.word_wrap is False else W
        atoms = []                                   # 逐字：(字, 字体, 颜色, 字宽)
        for t, fo in runs:
            sz = (fo.size.pt if fo.size else size_pt)
            fnt = getfont(fo.name or "微软雅黑", sz * PT, bool(fo.bold))
            color = (30, 30, 30)
            try:
                color = tuple(fo.color.rgb)
            except Exception:
                pass
            for ch in t:
                atoms.append((ch, fnt, color, sz))
        lines, cur, curw = [], [], 0.0
        for ch, fnt, color, sz in atoms:
            if ch == "\n":
                lines.append(cur)
                cur, curw = [], 0.0
                continue
            w = draw.textlength(ch, font=fnt)
            if curw + w > MAXW and cur:
                lines.append(cur)
                cur, curw = [], 0.0
                if ch == " ":
                    continue
            cur.append((ch, fnt, color, w))
            curw += w
        lines.append(cur)
        ls = para.line_spacing                      # 段落行距倍数（None 表示跟随版式）
        if not isinstance(ls, float) and not isinstance(ls, int):
            ls = None
        PRE.append((lines, size_pt, str(para.alignment or ""), ls))

    def lh_of(sp, ls=None):
        return sp * PT * (ls if ls else 1.35)
    total = sum(lh_of(p[1], p[3]) * len(p[0]) for p in PRE if p)
    anchor = str(getattr(tf, 'vertical_anchor', '') or '')
    cy = T
    if 'MIDDLE' in anchor:
        cy = T + max(0, (H - total) / 2)
    elif 'BOTTOM' in anchor:
        cy = T + max(0, H - total)

    for p in PRE:
        if p is None:
            cy += 12 * PT
            continue
        lines, size_pt, al, ls = p
        lh = lh_of(size_pt, ls)
        for atoms in lines:
            wln = sum(a[3] for a in atoms)
            x = L
            if 'CENTER' in al:
                x = L + (W - wln) / 2
            elif 'RIGHT' in al:
                x = L + W - wln
            for ch, fnt, color, w in atoms:
                draw.text((x, cy), ch, font=fnt, fill=color)
                x += w
            cy += lh

img.save(OUT)
print("ok", OUT, img.size)
