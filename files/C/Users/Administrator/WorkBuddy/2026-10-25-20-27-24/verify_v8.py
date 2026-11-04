# -*- coding: utf-8 -*-
"""对 _定稿.pptx 做整体校验：① 与 _最终版 逐页文字比对（除删除页与目录页）② 修备注节奏表 ③ 视频/媒体完整性"""
import sys, zipfile
sys.stdout.reconfigure(encoding='utf-8')
from pptx import Presentation

A = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_最终版.pptx"
B = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时_定稿.pptx"

a = list(Presentation(A).slides)
pb = Presentation(B)
b = list(pb.slides)

# 最终版第 5 页（index 4，序章小目录）被删；1-based 对照
pairs = [(i, i if i < 4 else i - 1) for i in range(len(a)) if i != 4]
bad = 0
for ia, ib in pairs:
    ta = [sh.text_frame.text for sh in a[ia].shapes if sh.has_text_frame]
    tb = [sh.text_frame.text for sh in b[ib].shapes if sh.has_text_frame]
    if ta != tb:
        tag = "目录页(已重建)" if ib in (3, 6, 12, 18, 20) else "!!! 内容被改动"
        if ib not in (3, 6, 12, 18, 20):
            bad += 1
        print("P%02d → P%02d  %s" % (ia + 1, ib + 1, tag))
print("内容页异常数:", bad, "| 总页数:", len(b))

# 媒体完整性
for path in (A, B):
    with zipfile.ZipFile(path) as z:
        m = [n for n in z.namelist() if n.startswith("ppt/media/")]
        print(path.split("_")[-1], "媒体文件:", len(m), "| 视频:", len([x for x in m if x.endswith(".mp4")]))

# ---- 修备注：节奏表 ----
NOTE = ("全片 10 分钟节奏表（控场参考）：P1 片头 5 秒｜P2-P3 封面 10 秒｜P4 大目录 20 秒｜"
        "P5 团队分工 35 秒｜P6-P11 微光 · 韩雅平 3 分 00 秒（含 34 秒采访视频）｜"
        "P12-P18 成炬 · 陈新超 4 分 00 秒（含 2 分 46 秒纪实视频）｜P19-P20 尾声 40 秒｜"
        "P21-P24 致谢 20 秒。小目录页每页只念一句，约 3-5 秒；"
        "党员风采（3 分 18 秒，P18）为机动页，超时直接跳过。")
tf = b[1].notes_slide.notes_text_frame
tf.paragraphs[0].runs[0].text = NOTE

tf2 = b[19].notes_slide.notes_text_frame
for p in tf2.paragraphs:
    for r in p.runs:
        r.text = r.text.replace("机动页(P15)", "机动页(P18)")

pb.save(B)
print("备注已更新")
