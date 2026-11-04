# -*- coding: utf-8 -*-
"""把正文页上过小的标签/脚注（<=11.2pt）放大并加粗；用字宽测量确保不会新增换行"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
from pptx import Presentation
from pptx.util import Pt
from PIL import ImageFont

F = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_定稿.pptx"
EMU = 914400
FONTS = {
    "微软雅黑": r"C:\Windows\Fonts\msyh.ttc",
    "Microsoft YaHei": r"C:\Windows\Fonts\msyh.ttc",
    "仿宋": r"C:\Windows\Fonts\simfang.ttf",
    "Georgia": r"C:\Windows\Fonts\georgia.ttf",
    "楷体": r"C:\Windows\Fonts\simkai.ttf",
}
_cache = {}


def w_of(txt, font, size_pt, bold):
    key = (font, round(size_pt, 1), bold)
    path = FONTS.get(font or "", FONTS["微软雅黑"])
    if not os.path.exists(path):
        path = FONTS["微软雅黑"]
    if key not in _cache:
        f = ImageFont.truetype(path, max(6, int(size_pt * 4)))
        _cache[key] = f
    f = _cache[key]
    return f.getlength(txt) / 4.0 / 72.0        # inch


prs = Presentation(F)
TOC = {3, 4, 7, 13, 19, 21}
changed = 0
skipped = 0
for si, s in enumerate(list(prs.slides)):
    if si in TOC:
        continue
    for sh in s.shapes:
        if not sh.has_text_frame or not sh.width:
            continue
        boxw = sh.width / EMU
        for pa in sh.text_frame.paragraphs:
            for r in pa.runs:
                t = r.text.strip()
                if not t or not r.font.size:
                    continue
                sz = r.font.size.pt
                if sz > 11.2:
                    continue
                new = min(12.5, sz + 2.0)
                fname = r.font.name
                if w_of(t, fname, new, True) <= boxw - 0.06:
                    r.font.size = Pt(round(new, 1))
                    r.font.bold = True
                    changed += 1
                else:
                    r.font.bold = True
                    skipped += 1
print("放大 %d 处，仅加粗（宽度不足）%d 处" % (changed, skipped))
prs.save(F)
print("saved")
