# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pptx import Presentation
D = "D:/桌面/总文件夹/资料整合/"
prs = Presentation(D + "微光成炬-星火自有燎原时_最终版.pptx")
sl = list(prs.slides)
for idx in (3, 4):
    s = sl[idx]
    print("### P%02d  shapes=%d  size=%dx%d" % (idx+1, len(s.shapes), prs.slide_width, prs.slide_height))
    for sh in s.shapes:
        t = sh.text_frame.text.replace("\n"," / ")[:40] if sh.has_text_frame else ""
        print("   %-22s %-18s L=%.2f T=%.2f W=%.2f H=%.2f | %s" % (
            sh.name, str(sh.shape_type)[:18],
            sh.left/914400, sh.top/914400, sh.width/914400, sh.height/914400, t))
