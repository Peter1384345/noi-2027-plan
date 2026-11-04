# -*- coding: utf-8 -*-
"""v9 校验：与 _最终版 逐页比对（应只有 6 张目录页不同）+ 修备注节奏表 + 媒体完整性"""
import sys, zipfile
sys.stdout.reconfigure(encoding='utf-8')
from pptx import Presentation

A = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_最终版.pptx"
B = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_定稿.pptx"

a = list(Presentation(A).slides)
pb = Presentation(B)
b = list(pb.slides)
TOC = {3, 4, 7, 13, 19, 21}
print("页数:", len(a), "→", len(b))

bad = 0
for i, (sa, sb) in enumerate(zip(a, b)):
    ta = [sh.text_frame.text for sh in sa.shapes if sh.has_text_frame]
    tb = [sh.text_frame.text for sh in sb.shapes if sh.has_text_frame]
    if ta != tb:
        if i in TOC:
            print("P%02d  目录页(已重建)" % (i + 1))
        else:
            bad += 1
            print("P%02d  !!! 内容被改动" % (i + 1))
print("非目录页异常:", bad)

for path in (A, B):
    with zipfile.ZipFile(path) as z:
        m = [n for n in z.namelist() if n.startswith("ppt/media/")]
        names = z.namelist()
        dup = [k for k in set(names) if names.count(k) > 1]
        print(path.split("_")[-1], "媒体:", len(m), "视频:", len([x for x in m if x.endswith(".mp4")]),
              "重名:", dup or "无")

NOTE = ("全片 10 分钟节奏表（控场参考）：P1 片头 5 秒｜P2-P3 封面 10 秒｜P4 大目录 20 秒｜"
        "P5 序章 15 秒｜P6 团队分工 35 秒｜P7-P12 微光 · 韩雅平 3 分 00 秒（含 34 秒采访视频）｜"
        "P13-P19 成炬 · 陈新超 4 分 00 秒（含 2 分 46 秒纪实视频）｜P20-P21 尾声 40 秒｜"
        "P22-P25 致谢 20 秒。小目录页每页只念一句，约 3-5 秒；"
        "党员风采（3 分 18 秒，P19）为机动页，超时直接跳过。")
runs = b[1].notes_slide.notes_text_frame.paragraphs[0].runs
for r in runs[1:]:
    r._r.getparent().remove(r._r)
runs[0].text = NOTE

tf2 = b[20].notes_slide.notes_text_frame
for p in tf2.paragraphs:
    for r in p.runs:
        t = r.text.replace("机动页(P15)", "机动页(P19)").replace("机动页(P18)", "机动页(P19)")
        r.text = t

pb.save(B)
print("备注已更新")
