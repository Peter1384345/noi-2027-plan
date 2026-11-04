# -*- coding: utf-8 -*-
"""用 PIL 按真实几何/配色近似渲染某一页，用于检查排版（不是最终输出）"""
import sys
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.oxml.ns import qn

path = sys.argv[1]
idx = int(sys.argv[2]) if len(sys.argv) > 2 else 2
out = sys.argv[3] if len(sys.argv) > 3 else "preview.png"

prs = Presentation(path)
s = prs.slides[idx]
SW, SH = prs.slide_width / 914400, prs.slide_height / 914400
PXW = 1600
K = PXW / SW                      # px per inch
PXH = int(SH * K)
PT = K / 72.0                     # px per pt

img = Image.new("RGB", (PXW, PXH), (255, 255, 255))
draw = ImageDraw.Draw(img)

FONT = {
    "微软雅黑": r"C:\Windows\Fonts\msyh.ttc",
    "Microsoft YaHei": r"C:\Windows\Fonts\msyh.ttc",
    "Georgia": r"C:\Windows\Fonts\georgia.ttf",
    "仿宋": r"C:\Windows\Fonts\simfang.ttf",
    "STXingkai": r"C:\Windows\Fonts\STXINGKA.TTF",
}


def font_of(name, size_px, bold=False):
    p = FONT.get(name or "", r"C:\Windows\Fonts\msyh.ttc")
    try:
        f = ImageFont.truetype(p, max(1, int(size_px)))
        if bold:
            try:
                f.set_variation_by_name("Bold")
            except Exception:
                pass
        return f
    except Exception:
        return ImageFont.load_default()


def fill_of(sh):
    spPr = sh._element.spPr
    sf = spPr.find(qn('a:solidFill'))
    if sf is None:
        gf = spPr.find(qn('a:gradFill'))
        if gf is not None:
            gs = gf.find(qn('a:gsLst'))
            if gs is not None and len(gs):
                srgb = gs[0].find(qn('a:srgbClr'))
                if srgb is not None:
                    a = srgb.find(qn('a:alpha'))
                    alpha = int(a.get('val')) / 1000.0 if a is not None else 100
                    return "#" + srgb.get('val'), alpha
        return None, 100
    srgb = sf.find(qn('a:srgbClr'))
    if srgb is None:
        sc = sf.find(qn('a:schemeClr'))
        if sc is not None:
            return {"accent4": "#FFC000", "accent1": "#4472C4",
                    "dk1": "#000000", "lt1": "#FFFFFF"}.get(sc.get('val'), "#888888"), 100
        return None, 100
    hexv = srgb.get('val')
    a = srgb.find(qn('a:alpha'))
    alpha = int(a.get('val')) / 1000.0 if a is not None else 100
    return "#" + hexv, alpha


def blend(box, rgb, alpha):
    if alpha >= 99:
        draw.rectangle(box, fill=rgb)
    elif alpha > 0:
        region = img.crop([int(v) for v in box])
        over = Image.new("RGB", region.size, rgb)
        img.paste(Image.blend(region, over, alpha / 100.0), (int(box[0]), int(box[1])))


for sh in s.shapes:
    L, T = sh.left / 914400 * K, sh.top / 914400 * K
    W, H = (sh.width or 0) / 914400 * K, (sh.height or 0) / 914400 * K
    # 形状底色
    if sh.shape_type is not None and not sh.has_text_frame or (sh.has_text_frame and not sh.text_frame.text.strip()):
        color, alpha = fill_of(sh)
        if color:
            rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
            blend([L, T, L + W, T + H], rgb, alpha)
        continue
    color, alpha = fill_of(sh)
    if color and W > 0 and H > 0:
        rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
        blend([L, T, L + W, T + H], rgb, alpha)
    # 文本
    if not sh.has_text_frame:
        continue
    tf = sh.text_frame
    cy = T
    for para in tf.paragraphs:
        runs = para.runs
        if not runs:
            continue
        sz = (runs[0].font.size.pt if runs[0].font.size else 18)
        lnspc = para.line_spacing or 1.0
        r = runs[0]
        fname = r.font.name
        fcol = "#000000"
        try:
            if r.font.color and r.font.color.rgb:
                fcol = "#" + str(r.font.color.rgb)
        except Exception:
            pass
        f = font_of(fname, sz * PT, bool(r.font.bold))
        txt = "".join(x.text for x in runs)
        # 若为渐变字（accent4 等），按主题色近似取色
        rPr = runs[0]._r.find(qn('a:rPr'))
        if rPr is not None:
            gf = rPr.find(qn('a:gradFill'))
            sf2 = rPr.find(qn('a:solidFill'))
            src = None
            if sf2 is not None:
                src = sf2
            elif gf is not None:
                gs = gf.find(qn('a:gsLst')).find(qn('a:gs'))
                src = gs
            if src is not None:
                srgb = src.find(qn('a:srgbClr'))
                if srgb is not None:
                    fcol = "#" + srgb.get('val')
                else:
                    sc = src.find(qn('a:schemeClr'))
                    if sc is not None:
                        fcol = {"accent4": "#FFC000", "accent1": "#4472C4",
                                "dk1": "#000000", "lt1": "#FFFFFF"}.get(sc.get('val'), "#FFC000")
        # 逐字折行
        lines, cur = [], ""
        limit = W if tf.word_wrap else 1e9
        for ch in txt:
            if f.getlength(cur + ch) <= limit or not cur:
                cur += ch
            else:
                lines.append(cur)
                cur = ch
        lines.append(cur)
        lh = sz * PT * 1.20 * lnspc
        for line in lines:
            lw = f.getlength(line)
            if para.alignment is not None and int(para.alignment) == 3:  # RIGHT
                x = L + W - lw
            elif para.alignment is not None and int(para.alignment) == 2:  # CENTER
                x = L + (W - lw) / 2
            else:
                x = L
            if fcol != "#000000" or True:
                draw.text((x, cy), line, font=f, fill=fcol)
            cy += lh

img.save(out)
print("ok", out, img.size)
