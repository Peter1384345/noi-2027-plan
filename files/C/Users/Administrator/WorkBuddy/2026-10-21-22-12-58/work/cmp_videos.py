# -*- coding: utf-8 -*-
"""对比 PPT 内 6 段视频与 U 盘 5 段视频：哈希 + 时长 + 首帧"""
import sys, os, zipfile, hashlib, subprocess

sys.stdout.reconfigure(encoding='utf-8')
FF = r"C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"
BASE = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58"
PPT = os.path.join(BASE, '微光成炬-星火自有燎原时（终版·v9）.pptx')
OUT = os.path.join(BASE, 'work', 'vidcmp')
os.makedirs(OUT, exist_ok=True)

z = zipfile.ZipFile(PPT)
ppt_vids = [n for n in z.namelist() if '/media/' in n and n.lower().endswith('.mp4')]
for n in ppt_vids:
    p = os.path.join(OUT, os.path.basename(n))
    with open(p, 'wb') as f:
        f.write(z.read(n))

def dur(path):
    r = subprocess.run([FF, '-i', path], capture_output=True, text=True, errors='ignore')
    for line in r.stderr.splitlines():
        if 'Duration' in line:
            t = line.split('Duration:')[1].split(',')[0].strip()
            h, m, s = t.split(':')
            return int(h) * 3600 + int(m) * 60 + float(s)
    return -1

def md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()[:10]

def first_frame(path, tag):
    out = os.path.join(OUT, f'ff_{tag}.jpg')
    subprocess.run([FF, '-y', '-i', path, '-vframes', '1', '-vf', 'scale=320:-1', out],
                   capture_output=True)
    return out if os.path.exists(out) else None

rows = []
for n in sorted(ppt_vids):
    p = os.path.join(OUT, os.path.basename(n))
    rows.append((os.path.basename(n), dur(p), md5(p), first_frame(p, os.path.basename(n)[5:11])))
for i in range(1, 6):
    p = os.path.join(OUT, '..', 'usb_videos', f'hyp{i:02d}.mp4')
    p = os.path.normpath(p)
    rows.append((f'hyp{i:02d}.mp4', dur(p), md5(p), first_frame(p, f'h{i:02d}')))

for name, d, h, ff in rows:
    print(f'{name:14s}  {d:7.1f}s  md5={h}  {ff or "-"}')
