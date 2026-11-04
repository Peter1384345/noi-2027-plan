# -*- coding: utf-8 -*-
"""成品校验：逐页文字、视频数量、zip 重名检查。"""
import sys, zipfile, os
sys.stdout.reconfigure(encoding='utf-8')
from pptx import Presentation

P = sys.argv[1] if len(sys.argv) > 1 else r"D:\桌面\微光成炬_工作环境\06_成品输出\微光成炬-星火自有燎原时_22页.pptx"
prs = Presentation(P)
print("页数:", len(prs.slides), " 文件大小: %.1f MB" % (os.path.getsize(P) / 1048576))
print("=" * 96)
for i, s in enumerate(prs.slides, 1):
    txts = []
    for sh in s.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip():
            txts.append(sh.text_frame.text.strip().replace("\n", " / "))
    kinds = [sh.shape_type for sh in s.shapes]
    fmts = sum(1 for k in kinds if k is not None and 'FREEFORM' in str(k))
    vids = sum(1 for sh in s.shapes if 'VIDEO' in str(sh.shape_type))
    pics = sum(1 for sh in s.shapes if 'PICTURE' in str(sh.shape_type))
    head = " | ".join(txts)[:118]
    print("P%-3d shapes=%-3d pic=%-2d vid=%d  %s" % (i, len(s.shapes), pics, vids, head))
    note = ""
    try:
        note = s.notes_slide.notes_text_frame.text.strip()
    except Exception:
        pass
    if note:
        print("      备注: %s" % note[:90])
print("=" * 96)
z = zipfile.ZipFile(P)
names = z.namelist()
dup = {n for n in names if names.count(n) > 1}
print("zip 条目 %d 个，重名: %s" % (len(names), dup if dup else "无"))
print("媒体:", ", ".join(sorted(os.path.basename(n) for n in names if n.startswith("ppt/media/")))[:200])
