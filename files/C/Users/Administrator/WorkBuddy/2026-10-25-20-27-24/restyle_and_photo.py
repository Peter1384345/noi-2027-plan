# -*- coding: utf-8 -*-
"""顾妈妈页配图 + 新增页字体精修（通过 edsdk 会话，保证编辑器同步）。"""
import json, subprocess, os, glob, time, shutil

SKILL = r"C:\Users\Administrator\.workbuddy\plugins\cache\workbuddy-builtin\workbuddy-pptx\5.9.2-wb.42136757.g0b5051be.hd4338c001c60\skills\workbuddy-pptx"
FID = "sid_mvnxzd7o_zjkawvmt"
EDS = os.path.join(SKILL, "scripts", "edsdk.py")
IMG = r"C:\Users\Administrator\WorkBuddy\2026-10-25-20-27-24\photos\guma_portrait.jpg"
ORIG = r"D:\桌面\总文件夹\资料整合\微光成炬-星火自有燎原时.pptx"

def call(tool, args=None, **kw):
    params = dict(kw)
    if args: params.update(args)
    params["file_id"] = FID
    p = subprocess.run(["python3", EDS, "call", tool, "--json", json.dumps(params, ensure_ascii=False)],
                       cwd=SKILL, capture_output=True, text=True)
    out = p.stdout.strip() or p.stderr.strip()
    try:
        return json.loads(out)
    except Exception:
        print("!!", tool, out[:200]); return {}

def runs_length(page, shape):
    d = call("slide_get_text", page_index=page, shape_id=shape)
    return d.get("length")

# ---------- 1) 顾妈妈页：替换左侧配图为顾虹照片 ----------
call("slide_remove_shapes", page_index=7, shape_ids=["000261"])
r = call("slide_add_image", page_index=7, x=0, y=0, w=450, h=540, image=IMG)
print("image added:", r.get("ok"), r.get("shape_id", ""))

# ---------- 2) 新增页字体精修 ----------
STYLE = {
  # page: [(shape_id, {font_size, color, bold, letter_spacing})]
  8: [("000271", dict(font_size=22, color="FFFFFF", bold=True, letter_spacing=40)),
      ("000272", dict(font_size=11, color="E8C87A", letter_spacing=80)),
      ("000274", dict(font_size=13, color="FFF8EC", letter_spacing=20))],
  12: [("0003db", dict(font_size=22, color="FFFFFF", bold=True, letter_spacing=40)),
       ("0003dc", dict(font_size=11, color="E8C87A", letter_spacing=80)),
       ("0003de", dict(font_size=13, color="FFF8EC", letter_spacing=20))],
  13: [("0004b3", dict(font_size=22, color="FFFFFF", bold=True, letter_spacing=40)),
       ("0004b4", dict(font_size=11, color="E8C87A", letter_spacing=80)),
       ("0004b6", dict(font_size=13, color="FFF8EC", letter_spacing=20))],
  7:  [("000263", dict(font_size=44, color="C00000", bold=True, letter_spacing=120)),
       ("000264", dict(font_size=11, color="8C5A3C", letter_spacing=60)),
       ("000265", dict(font_size=14, color="3A3A38", letter_spacing=10)),
       ("00026a", dict(font_size=12, color="211F1B", letter_spacing=10))],
}
for page, items in STYLE.items():
    for sid, st in items:
        n = runs_length(page, sid)
        if not n:
            print("skip", page, sid); continue
        n = n - 1 if n > 0 else n     # 去掉末尾 \r
        params = dict(index=0, count=n, font_name="微软雅黑")
        params.update(st)
        res = call("slide_set_text_property", page_index=page, shape_id=sid, **params)
        print(f"p{page+1} {sid} len={n} ->", res.get("ok"))

# ---------- 3) 保存并同步 ----------
print(call("save_file").get("notes") or "saved")
