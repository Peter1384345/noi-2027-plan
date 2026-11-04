# -*- coding: utf-8 -*-
"""安全回退：把放大后文字末端越过幻灯片安全边界（或超出盒子）的 run 恢复原字号（仍保留加粗）"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
from pptx import Presentation
from pptx.util import Pt
from PIL import ImageFont

F = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_定稿.pptx"
A = r"D:\桌面\总文件夹\资料整合\_备份_字号调整前.pptx"
EMU = 914400
SAFE_L, SAFE_R = 0.12, 13.20
FONTS = {"微软雅黑": r"C:\Windows\Fonts\msyh.ttc", "Microsoft YaHei": r"C:\Windows\Fonts\msyh.ttc",
         "仿宋": r"C:\Windows\Fonts\simfang.ttf", "Georgia": r"C:\Windows\Fonts\georgia.ttf",
         "楷体": r"C:\Windows\Fonts\simkai.ttf"}
_c = {}


def wi(txt, font, size, bold=True):
    key = (font, round(size, 1))
    path = FONTS.get(font or "", FONTS["微软雅黑"])
    if not os.path.exists(path):
        path = FONTS["微软雅黑"]
    if key not in _c:
        _c[key] = ImageFont.truetype(path, max(6, int(size * 4)))
    return _c[key].getlength(txt) / 4.0 / 72.0


pa = Presentation(A)
pb = Presentation(F)
rev = 0
for si, (sa, sb) in enumerate(zip(pa.slides, pb.slides), 1):
    for sha, shb in zip(sa.shapes, sb.shapes):
        if not sha.has_text_frame or not shb.has_text_frame:
            continue
        L = shb.left / EMU
        W = shb.width / EMU
        for pra, prb in zip(sha.text_frame.paragraphs, shb.text_frame.paragraphs):
            for ra, rb in zip(pra.runs, prb.runs):
                if not (ra.font.size and rb.font.size) or ra.font.size == rb.font.size:
                    continue
                t = rb.text.strip()
                new_sz = rb.font.size.pt
                end = L + wi(t, rb.font.name, new_sz)
                if end > SAFE_R:
                    rb.font.size = ra.font.size
                    rev += 1
                    print("P%02d 回退 %.1f→%.1f  end=%.2f  %s" % (si, new_sz, ra.font.size.pt, end, t[:30]))
print("回退:", rev)
pb.save(F)
