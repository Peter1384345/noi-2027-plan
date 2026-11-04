# -*- coding: utf-8 -*-
"""协调性修订 + 扩展：删悬空占位、修拼写、去过时页码、新增顾妈妈故事页。"""
import copy, os
from copy import deepcopy
from pptx import Presentation
from pptx.oxml.ns import qn

SRC = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时.pptx"
BAK = SRC.replace(".pptx", "_修订前备份.pptx")
if not os.path.exists(BAK):
    import shutil; shutil.copy2(SRC, BAK); print("backup ->", BAK)

prs = Presentation(SRC)
print("slides before:", len(prs.slides))

# ---------- 工具 ----------
def duplicate_slide(prs, source):
    dest = prs.slides.add_slide(source.slide_layout)
    for sh in list(dest.shapes):
        sh._element.getparent().remove(sh._element)
    rid_map = {}
    for rid, rel in source.part.rels.items():
        if rel.is_external: continue
        rt = rel.reltype
        if rt.endswith("/image") or rt.endswith("/media") or rt.endswith("/video"):
            rid_map[rid] = dest.part.relate_to(rel.target_part, rt)
    src_tree, dst_tree = source.shapes._spTree, dest.shapes._spTree
    for child in src_tree:
        if child.tag.endswith("}nvGrpSpPr") or child.tag.endswith("}grpSpPr"):
            continue
        dst_tree.append(copy.deepcopy(child))
    for el in dst_tree.iter():
        for k, v in list(el.attrib.items()):
            if (k.endswith("}embed") or k.endswith("}link") or k.endswith("}id")) and v in rid_map:
                el.set(k, rid_map[v])
    return dest

def set_text_keep_style(sh, lines):
    """替换形状全部文本，保留原第一段的 pPr 与 run 样式。lines: list[str]"""
    txBody = sh.text_frame._txBody
    paras = txBody.findall(qn("a:p"))
    tmpl = paras[0]
    ppr = tmpl.find(qn("a:pPr"))
    run_tmpl = None
    for r in tmpl.iter(qn("a:r")):
        run_tmpl = r; break
    for p in paras:
        txBody.remove(p)
    for line in lines:
        p = tmpl.makeelement(qn("a:p"), {})
        if ppr is not None:
            p.append(deepcopy(ppr))
        if run_tmpl is not None:
            r = deepcopy(run_tmpl)
            r.find(qn("a:t")).text = line
            p.append(r)
        else:
            t = p.makeelement(qn("a:t"), {}); t.text = line; p.append(t)
        txBody.append(p)

def replace_in_shape(sh, old, new):
    if not sh.has_text_frame: return False
    hit = False
    for p in sh.text_frame.paragraphs:
        for r in p.runs:
            if old in r.text:
                r.text = r.text.replace(old, new); hit = True
    return hit

slides = list(prs.slides)

# ---------- 1) 时间线页：删除悬空 "......" ----------
s10 = slides[9]
for sh in list(s10.shapes):
    if sh.has_text_frame and sh.text_frame.text.strip() == "......":
        sh._element.getparent().remove(sh._element)
        print("removed stray '......' on slide 10")

# ---------- 2) 服务站页：修拼写 ----------
fixed = False
for sh in slides[10].shapes:
    if replace_in_shape(sh, "MOE THAN DELIVERY", "MORE THAN DELIVERY"):
        fixed = True
print("typo fixed:", fixed)

# ---------- 3) 1700+ 页：去过时页码 ----------
fixed2 = False
for sh in slides[13].shapes:
    if replace_in_shape(sh, "· 10 / 13", "· 暖心邮路"):
        fixed2 = True
print("stale page counter fixed:", fixed2)

# ---------- 4) 新增“顾妈妈”故事页（复制韩雅平故事页版式） ----------
donor = slides[5]           # 韩雅平故事页
D = duplicate_slide(prs, donor)
shp = list(D.shapes)        # 顺序同 donor
# [3] 大标题 [4] 副标题 [5] 正文 [10] 金句
set_text_keep_style(shp[3], ["顾妈妈"])
set_text_keep_style(shp[4], ["——浙江嘉善 · 爱心妈妈顾虹 · 一场 12 年的双向奔赴"])
set_text_keep_style(shp[5], [
    "2014 年，29 岁的顾虹从志愿者协会的照片里记住了 6 岁的雅平，当即驱车 900 多公里赶到谢庄小学。",
    "那一封以“顾妈妈”开头的信，开启了一场 12 年的爱心长跑：每学期的信、每月的电话、每一笔按时到位的资助，陪着雅平从小学走进清华园。得知分数那天，雅平第一时间拨通的电话，正是打给顾妈妈的。",
    "16 年来，顾虹累计资助学生 365 人次，捐赠善款物资 25 万余元；在她的影响下，50 位爱心人士加入助学队伍，累计帮扶 1680 人次。",
])
set_text_keep_style(shp[10], ["“我就想着，我只能在求学的这条路上，让她走得更稳一些。”——顾虹"])
print("new 'Gu Mama' slide added")

# ---------- 5) 页序：把新页插到第 7 页（699 页）之后 ----------
sldIdLst = prs.slides._sldIdLst
ids = list(sldIdLst)                 # 0..17 原有, 18=新页
order = ids[0:7] + [ids[18]] + ids[7:18]
for el in list(sldIdLst):
    sldIdLst.remove(el)
for el in order:
    sldIdLst.append(el)

# ---------- 保存 ----------
try:
    prs.save(SRC); out = SRC
except PermissionError:
    out = SRC.replace(".pptx", "_修订版.pptx"); prs.save(out); print("原文件被占用，另存:", out)
print("saved:", out, "| total slides:", len(prs.slides))
