# -*- coding: utf-8 -*-
"""逐页导出初代 PPT 的形状/文字/字体/配色，用于复刻版式。"""
import sys, io
from pptx import Presentation
from pptx.util import Emu
from pptx.enum.shapes import MSO_SHAPE_TYPE

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
EMU = 914400.0

def color_of(node):
    from pptx.dml.color import MSO_THEME_COLOR
    try:
        if node is None:
            return None
        fill = node.fill
        if fill.type is None:
            return None
        if fill.type == 1:  # solid
            c = fill.fore_color
            try:
                return '#%02X%02X%02X' % (c.rgb[0], c.rgb[1], c.rgb[2])
            except Exception:
                return 'theme:%s' % c.theme_color
        if fill.type == 3:  # gradient
            stops = []
            for s in fill.gradient_stops:
                try:
                    stops.append('#%02X%02X%02X(%.2f)' % (s.color.rgb[0], s.color.rgb[1], s.color.rgb[2], s.position))
                except Exception:
                    stops.append('?')
            return 'grad[%s]@%.0f' % ('→'.join(stops), fill.gradient_angle if fill.gradient_angle is not None else -1)
    except Exception as e:
        return 'err'
    return 'other'

def run_info(r):
    f = r.font
    sz = f.size.pt if f.size else None
    try:
        col = '#%02X%02X%02X' % (f.color.rgb[0], f.color.rgb[1], f.color.rgb[2])
    except Exception:
        col = '?'
    spc = None
    try:
        el = r._r.find('{http://schemas.openxmlformats.org/drawingml/2006/main}rPr')
        if el is not None:
            spc = el.get('spc')
    except Exception:
        pass
    return 'sz=%.1f b=%s col=%s font=%s spc=%s | %r' % (
        sz or -1, 'Y' if f.bold else '-', col, f.name, spc, r.text[:60])

path = sys.argv[1] if len(sys.argv) > 1 else '微光成炬-星火自有燎原时_初代.pptx'
prs = Presentation(path)
for i, s in enumerate(prs.slides, 1):
    print('=' * 100)
    print('PAGE %d   shapes=%d' % (i, len(s.shapes)))
    for j, sh in enumerate(s.shapes):
        kind = str(sh.shape_type).split('.')[-1] if sh.shape_type is not None else '?'
        line = '  [%02d] %-12s %-14s L%5.2f T%5.2f W%5.2f H%5.2f  fill=%s' % (
            j, sh.name[:12], kind,
            sh.left / EMU if sh.left is not None else -1,
            sh.top / EMU if sh.top is not None else -1,
            sh.width / EMU if sh.width is not None else -1,
            sh.height / EMU if sh.height is not None else -1,
            color_of(sh))
        print(line)
        if sh.has_text_frame:
            for para in sh.text_frame.paragraphs:
                if not para.text.strip():
                    continue
                align = str(para.alignment).split('.')[-1] if para.alignment else '-'
                print('        ¶ align=%s runs=%d' % (align, len(para.runs)))
                for r in para.runs[:4]:
                    print('          ' + run_info(r))
