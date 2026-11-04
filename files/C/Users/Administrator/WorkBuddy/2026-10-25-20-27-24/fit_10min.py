# -*- coding: utf-8 -*-
"""10 分钟时长适配：党员风采视频页转机动页移至尾声后；写入节奏备注。"""
import os
from pptx import Presentation

SRC = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时.pptx"
BAK = SRC.replace(".pptx", "_10分钟适配前备份.pptx")
if not os.path.exists(BAK):
    import shutil; shutil.copy2(SRC, BAK); print("backup ->", BAK)

prs = Presentation(SRC)
slides = list(prs.slides)
print("slides:", len(slides))

# ---------- 定位页（0-based） ----------
# 当前: 13=党员风采视频页, 14=1700+页, 15=尾声, 16-18=致谢三页(保护)
FLAG = "党员风采"
idx_dang = next(i for i, s in enumerate(slides) if "党员风采" in " ".join(
    sh.text_frame.text for sh in s.shapes if sh.has_text_frame) and "videoFile" in s._element.xml)
idx_epi = next(i for i, s in enumerate(slides) if "EPILOGUE" in " ".join(
    sh.text_frame.text for sh in s.shapes if sh.has_text_frame))
print("党员风采页 idx:", idx_dang, "| 尾声页 idx:", idx_epi)

# ---------- 1) 移动党员风采页到尾声之后 ----------
sldIdLst = prs.slides._sldIdLst
ids = list(sldIdLst)
el = ids[idx_dang]
sldIdLst.remove(el)
# 移除后尾声索引左移 1；插到尾声之后
sldIdLst.insert(idx_epi, el)   # remove 使 idx_epi 及以后左移一位，insert at idx_epi 即"尾声之后"
print("moved 党员风采 page after EPILOGUE")

# ---------- 2) 标注机动页 ----------
slides = list(prs.slides)
idx_dang_new = next(i for i, s in enumerate(slides) if "党员风采" in " ".join(
    sh.text_frame.text for sh in s.shapes if sh.has_text_frame) and "videoFile" in s._element.xml)
dang = slides[idx_dang_new]
for sh in dang.shapes:
    if not sh.has_text_frame:
        continue
    for p in sh.text_frame.paragraphs:
        for r in p.runs:
            if "党员风采：一颗爱心走邮路" in r.text:
                r.text = "视频 · 党员风采（机动 · 时间充裕时播放 3'18\"）"
            elif "黄石市广播电视台" in r.text:
                r.text = "黄石市广播电视台《领航》专栏 · 本页不计入主线 10 分钟"
print("机动页标注完成 (slide", idx_dang_new + 1, ")")

# ---------- 3) 写入节奏备注 ----------
def set_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text

budget = (
    "⏱ 全片 10 分钟节奏表（写给大家的控场参考）：\n"
    "· P1-P4 开场 / 目录 / 团队分工 —— 1'00\"\n"
    "· P5-P9 微光 · 韩雅平 —— 3'00\"（其中采访视频 34 秒）\n"
    "· P10-P14 成炬 · 陈新超 —— 4'30\"（其中纪实视频 2'46\"）\n"
    "· P15-P16 尾声收束 —— 1'00\"\n"
    "· P17-P19 致谢谢幕 —— 0'30\"\n"
    "※ P16 党员风采视频页为机动内容，仅在前方提前完成、时间充裕时播放（3'18\"）。"
)
part1_note = "⏱ 本部分预算 3'00\"：故事页 40 秒 → 699 页 30 秒 → 顾妈妈页 45 秒 → 采访视频 34 秒 → 过渡 30 秒。讲不完先砍故事页第三段。"
part2_note = "⏱ 本部分预算 4'30\"：章节页 20 秒 → 故事页 50 秒 → 服务站 50 秒 → 纪实视频 2'46\" → 数据页 45 秒。视频若卡顿，直接口播数据页。"
epi_note = "⏱ 尾声预算 1'00\"：两人各 25 秒收束 + 10 秒过渡到致谢。如已超时，直接念两句金句谢幕。"

set_notes(slides[0], budget)
set_notes(slides[4], part1_note)   # PART 01 章节页
set_notes(slides[9], part2_note)   # PART 02 章节页
set_notes(slides[idx_epi], epi_note)
print("notes written to cover / part1 / part2 / epilogue")

# ---------- 保存 ----------
try:
    prs.save(SRC); out = SRC
except PermissionError:
    out = SRC.replace(".pptx", "_10分钟版.pptx"); prs.save(out); print("原文件被占用，另存:", out)
print("saved:", out)

