# -*- coding: utf-8 -*-
"""生成 6 张 16:9 视频占位卡海报 v2（修正播放按钮与竖图构图）。"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PHOTO = r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27\output\videos\photos"
OUT = r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27\output\videos\posters"
os.makedirs(OUT, exist_ok=True)

W, H = 1280, 720
GOLD = (201, 162, 39)
FONT_PATH = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"


def font(size, bold=False):
    try:
        return ImageFont.truetype(FONT_BOLD if bold else FONT_PATH, size)
    except OSError:
        return ImageFont.truetype(FONT_PATH, size)


def cover(img, w, h):
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale + 0.5), int(ih * scale + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return img.crop((left, top, left + w, top + h))


def dark_base():
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / H
        for x in range(W):
            px[x, y] = (int(22 + 18 * t), int(30 + 26 * t), int(48 + 38 * t))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W * 0.55, -H * 0.3, W * 1.25, H * 0.6), fill=(190, 60, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    return Image.blend(img, Image.composite(glow, img, Image.new("L", (W, H), 90)), 0.5)


def portrait_layout(img):
    """竖图：裁掉右侧 UI 栏 -> 背景模糊放大 + 前景按高居中"""
    iw, ih = img.size
    if ih > iw:  # 竖图
        img = img.crop((0, 0, int(iw * 0.8), ih))  # 去掉右侧抖音UI栏
    iw, ih = img.size
    bg = cover(img, W, H).filter(ImageFilter.GaussianBlur(40))
    bg = Image.eval(bg, lambda v: int(v * 0.40))  # 压暗
    scale = (H - 60) / ih
    nw, nh = int(iw * scale), int(ih * scale)
    fg = img.resize((nw, nh), Image.LANCZOS)
    canvas = bg.copy()
    canvas.paste(fg, ((W - nw) // 2, (H - nh) // 2))
    return canvas


def landscape_layout(img):
    """横图：cover 铺满"""
    return cover(img, W, H)


def draw_play_button(canvas):
    """金色圆环 + 半透明黑内圆 + 白色三角（在 overlay 上合成）"""
    cx, cy, r = W // 2, H // 2 - 14, 74
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(60, 8, 8, 150))
    od.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD + (255,), width=5)
    tr = 28
    od.polygon(
        [(cx - tr * 0.55, cy - tr), (cx - tr * 0.55, cy + tr), (cx + tr, cy)],
        fill=(255, 255, 255, 255),
    )
    return Image.alpha_composite(canvas.convert("RGBA"), overlay)


def darken(canvas, base_alpha=120, bottom_extra=90):
    overlay = Image.new("RGBA", (W, H), (48, 6, 6, base_alpha))
    grad = Image.new("L", (1, H))
    for y in range(H):
        t = y / H
        grad.putpixel((0, y), int(bottom_extra * max(0, (t - 0.45) / 0.55)))
    alpha = Image.new("RGBA", (W, H), (60, 8, 8, 0))
    alpha.putalpha(grad.resize((W, H)))
    return Image.alpha_composite(canvas.convert("RGBA"), Image.alpha_composite(overlay, alpha))


SPECS = [
    ("V1", None, "视频位 V1 · 人物采访", "韩雅平 · 独家采访",
     "校服女孩圆梦清华的亲口讲述", "建议时长 30–45 秒"),
    ("V2", "han_xibao.jpg", "视频位 V2 · 录取官宣", "清华录取官宣现场",
     "郏县实验高中光荣榜 · 2026年7月24日", "建议时长 15–20 秒"),
    ("V3", "chen3_2.jpg", "视频位 V3 · 章节转场", "陈新超 · 乡邮路启程",
     "《偏远山村的\"乡邮花\"》纪实片段", "建议时长 10–20 秒"),
    ("V4", "chen3_1.jpg", "视频位 V4 · 服务纪实", "快递驿站 · 便民服务纪实",
     "教老人缴费 · 帮人退网购 · 免费载人", "建议时长 30–45 秒"),
    ("V5", "chen3_0.jpg", "视频位 V5 · 邮路实拍", "山乡邮路 · 随车实拍",
     "十个村 · 两万三千名乡亲 · 二十多万公里", "建议时长 20–30 秒"),
    ("V6", None, "视频位 V6 · 升华混剪", "微光成炬 · 主题混剪",
     "两束微光 · 汇成一支火炬", "建议时长 40–60 秒"),
]

for vid, photo, label, title, sub, dur in SPECS:
    if photo:
        img = Image.open(os.path.join(PHOTO, photo)).convert("RGB")
        base = portrait_layout(img) if img.size[1] > img.size[0] else landscape_layout(img)
    else:
        base = dark_base()

    canvas = darken(base)
    canvas = draw_play_button(canvas)
    d = ImageDraw.Draw(canvas)

    # 金色双线边框
    m = 14
    d.rectangle((m, m, W - m, H - m), outline=GOLD, width=4)
    d.rectangle((m + 10, m + 10, W - m - 10, H - m - 10), outline=GOLD + (110,), width=1)

    # 顶部标签
    f_label = font(26, bold=True)
    tw = d.textlength(label, font=f_label)
    pad = 18
    ly = 44
    d.rounded_rectangle((44, ly - 10, 44 + tw + pad * 2, ly + 42), radius=26, fill=(192, 0, 0, 245))
    d.text((44 + pad, ly), label, font=f_label, fill=(255, 255, 255))

    # 底部标题 + 副题
    f_title = font(52, bold=True)
    f_sub = font(30)
    f_dur = font(26, bold=True)
    ty = H - 168
    d.text((56, ty), title, font=f_title, fill=(255, 250, 240))
    d.text((58, ty + 68), sub, font=f_sub, fill=(247, 244, 238))

    note = dur + " · 视频素材待替换"
    nw2 = d.textlength(note, font=f_dur)
    d.text((W - 56 - nw2, H - 66), note, font=f_dur, fill=(255, 220, 150))

    out_path = os.path.join(OUT, f"{vid}.png")
    canvas.convert("RGB").save(out_path, "PNG")
    print(f"OK {vid}")

print("DONE")
