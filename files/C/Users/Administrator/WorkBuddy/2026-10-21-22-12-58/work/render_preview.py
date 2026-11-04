# -*- coding: utf-8 -*-
"""粗渲染 PPTX 页面为 PNG（仅用于版面自检，非最终效果）。"""
import sys, os
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from PIL import Image, ImageDraw, ImageFont

FONTS = {
    '微软雅黑': ('C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/msyhbd.ttc'),
    'Georgia': ('C:/Windows/Fonts/georgia.ttf', 'C:/Windows/Fonts/georgiab.ttf'),
    '仿宋': ('C:/Windows/Fonts/simfang.ttf', 'C:/Windows/Fonts/simfang.ttf'),
}
SCALE = 1.4


def font_for(name, size, bold):
    reg, bd = FONTS.get(name, FONTS['微软雅黑'])
    path = bd if bold and os.path.exists(bd) else reg
    try:
        return ImageFont.truetype(path, max(1, int(size * SCALE)))
    except Exception:
        return ImageFont.load_default()


def rgb(c):
    s = str(c)
    return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))


def wrap(draw, text, fnt, maxw):
    lines, cur = [], ''
    for ch in text:
        t = cur + ch
        if draw.textlength(t, font=fnt) > maxw and cur:
            lines.append(cur)
            cur = ch
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines or ['']


def render(prs, idx, out):
    s = prs.slides[idx]
    W, H = int(960 * SCALE), int(540 * SCALE)
    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)
    for sh in s.shapes:
        try:
            x = (sh.left or 0) / 12700 * SCALE
            y = (sh.top or 0) / 12700 * SCALE
            w = (sh.width or 0) / 12700 * SCALE
            h = (sh.height or 0) / 12700 * SCALE
        except Exception:
            continue
        # 填充
        fill = None
        try:
            if sh.fill.type is not None and sh.fill.type == 1:
                fill = rgb(sh.fill.fore_color.rgb)
        except Exception:
            fill = None
        line = None
        try:
            if sh.line.color and sh.line.color.type is not None:
                line = rgb(sh.line.color.rgb)
        except Exception:
            line = None
        if sh.shape_type == MSO_SHAPE_TYPE.PICTURE:
            fill = (225, 222, 214)
        if sh.shape_type == MSO_SHAPE_TYPE.MEDIA:
            fill = (24, 22, 20)
        if fill or line:
            geom = None
            try:
                g = sh._element.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}prstGeom')
                geom = g.get('prst') if g is not None else None
            except Exception:
                geom = None
            if geom in ('ellipse',):
                d.ellipse([x, y, x + w, y + h], fill=fill, outline=line, width=1)
            else:
                d.rectangle([x, y, x + w, y + h], fill=fill, outline=line, width=1)
        # 文本
        if not sh.has_text_frame:
            continue
        tf = sh.text_frame
        cy = y
        for p in tf.paragraphs:
            if not p.runs:
                cy += 6 * SCALE
                continue
            r0 = p.runs[0]
            size = (r0.font.size.pt if r0.font.size else 12)
            bold = bool(r0.font.bold)
            try:
                fname = r0.font.name or '微软雅黑'
            except Exception:
                fname = '微软雅黑'
            col = (30, 35, 41)
            try:
                if r0.font.color and r0.font.color.type is not None:
                    col = rgb(r0.font.color.rgb)
            except Exception:
                pass
            fnt = font_for(fname, size, bold)
            text = ''.join(r.text for r in p.runs)
            ls = p.line_spacing or 1.2
            for ln in wrap(d, text, fnt, w):
                tw = d.textlength(ln, font=fnt)
                if p.alignment == PP_ALIGN.CENTER:
                    tx = x + (w - tw) / 2
                elif p.alignment == PP_ALIGN.RIGHT:
                    tx = x + w - tw
                else:
                    tx = x
                d.text((tx, cy), ln, font=fnt, fill=col)
                cy += size * ls * SCALE
    img.save(out)
    return out


if __name__ == '__main__':
    prs = Presentation(sys.argv[1])
    pages = [int(x) for x in sys.argv[2].split(',')]
    os.makedirs('.workbuddy/tmp/preview', exist_ok=True)
    for p in pages:
        out = f'.workbuddy/tmp/preview/p{p:02d}.png'
        render(prs, p - 1, out)
        print(out)
