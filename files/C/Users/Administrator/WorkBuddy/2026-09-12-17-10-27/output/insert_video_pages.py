# -*- coding: utf-8 -*-
"""为《微光成炬》复件添加 6 页独立视频插页（V1-V6），并移除原页面上的内嵌占位卡。"""
import os
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

BASE = r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27"
PPTX = os.path.join(BASE, "微光成炬-星火自有燎原时-复件.pptx")
POSTERS = os.path.join(BASE, "output", "videos", "posters")
LOG = os.path.join(BASE, "output", "insert_video_pages_log.txt")

# 配色（严格参照原版 PPT：正红底 + 金黄装饰 + 白字 + 黄标签 + 米白面板）
BG = (0xC0, 0x00, 0x00)          # 正红（原版章节页底色）
PANEL = (0xF7, 0xF4, 0xEE)       # 米白面板（原版浅色面板底）
PANEL_TEXT = (0xC0, 0x00, 0x00)  # 面板上的红字
GOLD = (0xE8, 0xC8, 0x7A)        # 原版装饰金（大数字/分隔线）
BORDER = (0xC9, 0xA2, 0x27)      # 原版金色描边
TEXT_MAIN = (0xFF, 0xFF, 0xFF)   # 白色主文字
TEXT_SUB = (0xF7, 0xF4, 0xEE)    # 米白正文
TEXT_DIM = (0xFF, 0xDC, 0x96)    # 浅金辅助文字
TAG_YELLOW = (0xFF, 0xFF, 0x00)  # 原版黄色小标签

VIDEOS = [
    dict(vid="V1", after=4, chapter="第一章 · 微光", title="视频 · 韩雅平独家采访",
         intro="听韩雅平亲口讲述她的故事：三间平房、28张奖状、病床上的母亲，和那张被灯光照亮的书桌。",
         points=["「家庭物质上的贫困，是我学习最大的动力」原声片段",
                 "谈学医心愿：为了治好妈妈的病",
                 "奖状墙前的少年讲述，细节比文字更动人"],
         source="央视新闻 / 封面新闻 等报道视频", dur="30–45 秒", play="单击播放 · 视频前静场3秒",
         note="【播放】单击画面播放采访片段。【讲述】播放前：\"接下来，让我们听听她本人怎么说。\"播放结束后翻页，接韩雅平人物页讲述。"),
    dict(vid="V2", after=6, chapter="第一章 · 微光", title="视频 · 清华录取官宣",
         intro="2026年7月24日，母校郏县实验高中官宣：韩雅平被清华大学录取。红榜贴出的那一刻，小山村沸腾了。",
         points=["光荣榜红榜亮相：699分，清华大学",
                 "清华、北大招生组电话先后打进那间平房",
                 "8月19日独自报到，绿色通道前与校党委书记合影"],
         source="人民日报 2026-07-27 / 学校官宣画面", dur="15–20 秒", play="单击播放 · 可与喜报截图叠化",
         note="【播放】录取官宣/迎新现场画面。【讲述】衔接数据页：\"699分，意味着什么？看这条官宣。\""),
    dict(vid="V3", after=7, chapter="第二章 · 成炬", title="视频 · 乡邮路启程（章节转场）",
         intro="镜头从河南移到湖北阳新的大山：一辆没有空调的二手货车，驶上\"快递进村\"最难走的路。",
         points=["货车出发纪实，作第二章开篇转场",
                 "十个村的邮路，从这条路开始",
                 "五年、二十多万公里，都从这一脚油门起步"],
         source="黄石政府网《偏远山村盛开的\"乡邮花\"》文内视频", dur="10–20 秒", play="建议设为自动播放作转场",
         note="【播放】建议设为自动播放。【讲述】转场词：\"第二章，成炬。把镜头从河南移到湖北阳新的大山。\""),
    dict(vid="V4", after=9, chapter="第三章 · 微光成炬", title="视频 · 快递驿站便民服务纪实",
         intro="教老人用手机缴费、帮人退网购、捎东西、指路、免费载人——她的快递点，是乡亲们的服务站。",
         points=["副驾驶每个月有二十天不空着",
                 "打过退堂鼓：接手的人只撑了三天",
                 "她笑笑，接着干"],
         source="极目新闻「凡人微光」视频版", dur="30–45 秒", play="单击播放",
         note="【播放】便民服务纪实。【讲述】\"打退堂鼓\"是情绪转折，收着说，播放后留安静一拍。"),
    dict(vid="V5", after=10, chapter="第三章 · 微光成炬", title="视频 · 山乡邮路随车实拍",
         intro="一千七百多个日夜，随车记录这条邮路：网湖大堤、盘山公路、村口等待的乡亲。",
         points=["第一次开邮车：40公里开了两个多小时，到家哭了一场",
                 "第二天，照样出发",
                 "2021年网湖抗洪，大堤上扛沙袋的人群里也有她"],
         source="湖北日报随车视频 / 极目新闻", dur="20–30 秒", play="单击播放",
         note="【播放】邮路实拍。【讲述】\"哭了一场\"之后停一拍，再讲\"第二天照样出发\"。往返120公里按2026年口径。"),
    dict(vid="V6", after=11, chapter="尾声", title="视频 · 微光成炬主题混剪",
         intro="一张书桌，撑起一座山；一条邮路，温暖两万人。两束微光相遇，就是火炬。",
         points=["韩雅平片段 × 陈新超片段 × 庞众望报道画面",
                 "微光吸引微光，微光点亮微光",
                 "收束主题：星火自有燎原时"],
         source="自制混剪（素材清单见资料汇编）", dur="40–60 秒", play="单击播放 · 结束后再出副题动画",
         note="【播放】升华混剪。【讲述】视频结束后停2秒，再出\"——星火自有燎原时\"副题动画，进入致谢。"),
]


def set_ea_font(run, name="Microsoft YaHei"):
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = rPr.makeelement(qn("a:ea"), {})
        rPr.append(ea)
    ea.set("typeface", name)


def style_run(run, size, color, bold=False):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = "Microsoft YaHei"
    run.font.color.rgb = RGBColor(*color)
    set_ea_font(run)


def add_textbox(slide, x, y, w, h):
    box = slide.shapes.add_textbox(Pt(x), Pt(y), Pt(w), Pt(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tf


def add_para(tf, text, size, color, bold=False, first=False, space_after=0, line_spacing=None):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    run = p.add_run()
    run.text = text
    style_run(run, size, color, bold)
    if space_after:
        p.space_after = Pt(space_after)
    if line_spacing:
        p.line_spacing = line_spacing
    return p


def add_rect(slide, x, y, w, h, fill=None, line=None, line_w=1.0):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Pt(x), Pt(y), Pt(w), Pt(h))
    if fill:
        shp.fill.solid()
        shp.fill.fore_color.rgb = RGBColor(*fill)
    else:
        shp.fill.background()
    if line:
        shp.line.color.rgb = RGBColor(*line)
        shp.line.width = Pt(line_w)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def move_slide(prs, from_idx, to_idx):
    lst = prs.slides._sldIdLst
    el = list(lst)[from_idx]
    lst.remove(el)
    lst.insert(to_idx, el)


def find_blank_layout(prs):
    best = None
    for layout in prs.slide_master.slide_layouts:
        n = len(layout.placeholders)
        if n == 0:
            return layout
        if best is None or n < len(best.placeholders):
            best = layout
    return best


def build_video_page(prs, layout, v):
    slide = prs.slides.add_slide(layout)
    # 清掉布局带来的占位符
    for shp in list(slide.shapes):
        if shp.is_placeholder:
            shp._element.getparent().remove(shp._element)

    # 背景（正红，与原版章节页一致）
    add_rect(slide, 0, 0, 960, 540, fill=BG)

    # 右上角大号编号装饰（Georgia 金色，原版章节页风格）
    tf = add_textbox(slide, 700, 6, 248, 96)
    p = add_para(tf, v["vid"], 80, GOLD, bold=False, first=True)
    p.alignment = PP_ALIGN.RIGHT
    for r in p.runs:
        r.font.name = "Georgia"

    # 顶部标签（原版黄色 PART 标签样式）
    tf = add_textbox(slide, 36, 34, 700, 26)
    add_para(tf, v["chapter"] + " ｜ 视频插页 " + v["vid"], 13, TAG_YELLOW, bold=True, first=True)

    # 大幅画面卡（16:9）
    png = os.path.join(POSTERS, v["vid"] + ".png")
    slide.shapes.add_picture(png, Pt(36), Pt(96), Pt(540), Pt(304))
    add_rect(slide, 36, 96, 540, 304, line=BORDER, line_w=2.0)

    # 播放提示条（米白面板 + 红字，原版浅色面板样式）
    add_rect(slide, 36, 412, 540, 34, fill=PANEL)
    tf = add_textbox(slide, 48, 419, 516, 22)
    add_para(tf, "▶ " + v["play"] + " · 视频素材到位后替换本页占位画面", 11.5, PANEL_TEXT, bold=True, first=True)

    # 右栏：标题
    tf = add_textbox(slide, 600, 96, 324, 64)
    add_para(tf, v["title"], 20, TEXT_MAIN, bold=True, first=True, line_spacing=1.1)
    # 分隔线
    add_rect(slide, 600, 164, 324, 2, fill=GOLD)
    # 简介
    tf = add_textbox(slide, 600, 178, 324, 84)
    add_para(tf, v["intro"], 12.5, TEXT_SUB, first=True, line_spacing=1.35)
    # 看点
    tf = add_textbox(slide, 600, 270, 324, 22)
    add_para(tf, "视频看点", 12.5, TAG_YELLOW, bold=True, first=True)
    tf = add_textbox(slide, 600, 294, 324, 116)
    for i, pt in enumerate(v["points"]):
        add_para(tf, "▸ " + pt, 11.5, TEXT_MAIN, first=(i == 0), space_after=5, line_spacing=1.2)
    # 来源 / 时长
    tf = add_textbox(slide, 600, 420, 324, 60)
    add_para(tf, "素材来源｜" + v["source"], 10.5, TEXT_DIM, first=True, space_after=4, line_spacing=1.2)
    add_para(tf, "建议时长｜" + v["dur"], 10.5, TEXT_DIM, line_spacing=1.2)

    # 页脚
    tf = add_textbox(slide, 36, 500, 888, 20)
    add_para(tf, "微光成炬 · 星火自有燎原时  ｜  " + v["vid"] + " 视频插页", 9.5, TEXT_DIM, first=True)

    # 演讲者备注（notes master 异常时跳过，稍后用编辑通道补写）
    try:
        ntf = slide.notes_slide.notes_text_frame
        if ntf is not None:
            ntf.text = v["note"]
        else:
            raise RuntimeError("notes_text_frame is None")
    except Exception as e:
        NOTES_FALLBACK.append((v["after"] + 1, v["note"]))
        lines.append(f"notes_fallback {v['vid']}: {e}")
    return slide


prs = Presentation(PPTX)
NOTES_FALLBACK = []
lines = [f"before_slides={len(prs.slides)}"]

layout = find_blank_layout(prs)
lines.append(f"layout_used={layout.name!r} placeholders={len(layout.placeholders)}")

# 0) 删除已有的视频插页页（从后往前）
from pptx.oxml.ns import qn as _qn


def delete_slide(prs, idx):
    id_lst = prs.slides._sldIdLst
    sldId = list(id_lst)[idx]
    prs.part.drop_rel(sldId.get(_qn("r:id")))
    id_lst.remove(sldId)


to_del = []
for i, s in enumerate(prs.slides):
    for shp in s.shapes:
        if shp.has_text_frame and "视频插页" in shp.text_frame.text:
            to_del.append(i)
            break
for i in reversed(to_del):
    delete_slide(prs, i)
lines.append(f"deleted_old_video_pages={len(to_del)}")

# 1) 移除原页面上的内嵌占位卡
removed = 0
for s in prs.slides:
    for shp in list(s.shapes):
        if shp.name and shp.name.startswith("VIDEO_PLACEHOLDER_"):
            shp._element.getparent().remove(shp._element)
            removed += 1
lines.append(f"removed_inline_placeholders={removed}")

# 2) 从后往前插入 6 页插页（保持前面索引稳定）
for v in reversed(VIDEOS):
    build_video_page(prs, layout, v)
    move_slide(prs, len(prs.slides) - 1, v["after"] + 1)

prs.save(PPTX)
lines.append(f"after_slides={len(prs.slides)} saved_size={os.path.getsize(PPTX)}")

# 3) 复核顺序与内容
prs2 = Presentation(PPTX)
check = []
for i, s in enumerate(prs2.slides):
    tag = ""
    for shp in s.shapes:
        if shp.has_text_frame:
            t = shp.text_frame.text
            if "视频插页" in t:
                tag = t.strip().split("\n")[0][:30]
                break
    check.append(f"[{i+1}]{tag}" if tag else f"[{i+1}]-")
lines.append("order: " + " ".join(check))

with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
if NOTES_FALLBACK:
    import json
    with open(os.path.join(BASE, "output", "video_page_notes_fallback.json"), "w", encoding="utf-8") as f:
        json.dump([{"page_index": p, "text": t} for p, t in NOTES_FALLBACK], f, ensure_ascii=False, indent=1)
print("DONE")
