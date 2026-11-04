# -*- coding: utf-8 -*-
"""v10-2b：章节页氛围视频 v2 —— 更深底、强暗角、稀疏细金尘（无人物）"""
import sys, os, subprocess
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
FF = r"C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"
OUT = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/work/fx"
os.makedirs(OUT, exist_ok=True)

W, H, FPS, DUR = 1600, 900, 25, 12
NF = FPS * DUR


def hex2rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
RX = (XX - W / 2) / (W / 2)
RY = (YY - H / 2) / (H / 2)
RAD = np.sqrt(RX ** 2 + RY ** 2) / 1.414


def base_frame(stops, angle=0.58, vig=0.62, gain=0.86):
    t = (XX / W) * angle + (YY / H) * (1 - angle)
    c0, c1, c2 = [hex2rgb(s) for s in stops]
    out = np.zeros((H, W, 3), dtype=np.float32)
    m1 = t < 0.55
    k1 = (t[m1] / 0.55)[:, None]
    out[m1] = c0 * (1 - k1) + c1 * k1
    m2 = ~m1
    k2 = ((t[m2] - 0.55) / 0.45)[:, None]
    out[m2] = c1 * (1 - k2) + c2 * k2
    out *= gain
    out *= (1 - vig * RAD ** 2)[:, :, None]
    return out


def gauss_blob(size, sigma):
    ax = np.arange(size, dtype=np.float32) - (size - 1) / 2
    return np.exp(-(ax[:, None] ** 2 + ax[None, :] ** 2) / (2 * sigma ** 2))


def render(stops, seed, n_part, gold, name, big_n=6, gain=0.86, vig=0.62):
    rng = np.random.default_rng(seed)
    base = base_frame(stops, gain=gain, vig=vig)
    c_gold = hex2rgb(gold)

    px = rng.uniform(0, W, n_part)
    py = rng.uniform(0, H, n_part)
    rad = rng.uniform(0.7, 2.2, n_part)
    spd = rng.uniform(2.5, 11, n_part)
    amp = rng.uniform(2, 14, n_part)
    pha = rng.uniform(0, 2 * np.pi, n_part)
    alp = rng.uniform(0.12, 0.5, n_part)

    # 大颗粒柔尘（深度感）
    bx = rng.uniform(0, W, big_n)
    by = rng.uniform(0, H, big_n)
    br = rng.uniform(30, 90, big_n)
    bs = rng.uniform(3, 9, big_n)
    bph = rng.uniform(0, 2 * np.pi, big_n)

    kernels = {}
    for i in range(n_part):
        r = rad[i] * 2.4
        key = round(r * 2, 1)
        if key not in kernels:
            s = max(5, int(key * 2) | 1)
            kernels[key] = (gauss_blob(s, r), s)
    big_k = {i: gauss_blob(int(br[i] * 2) | 1, br[i] / 2.2) for i in range(big_n)}

    cmd = [FF, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
           '-r', str(FPS), '-i', '-', '-an',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '26',
           '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
           os.path.join(OUT, f'{name}.mp4')]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)

    for f in range(NF):
        t = f / FPS
        frame = base.copy()

        # 柔尘大光斑（低频呼吸）
        for i in range(big_n):
            x = bx[i] + 40 * np.sin(2 * np.pi * t / (DUR * 1.7) + bph[i])
            y = (by[i] - bs[i] * t) % (H + 200) - 100
            k = big_k[i]
            s = k.shape[0]
            x0, y0 = int(x - s // 2), int(y - s // 2)
            xa, ya = max(0, x0), max(0, y0)
            xb, yb = min(W, x0 + s), min(H, y0 + s)
            if xa >= xb or ya >= yb:
                continue
            kk = k[ya - y0:yb - y0, xa - x0:xb - x0][:, :, None]
            a = 0.10 + 0.05 * np.sin(2 * np.pi * t / DUR + bph[i])
            frame[ya:yb, xa:xb] += kk * a * c_gold * 0.45

        # 细金尘
        for i in range(n_part):
            x = px[i] + amp[i] * np.sin(2 * np.pi * t / (DUR * 0.7) + pha[i])
            y = (py[i] - spd[i] * t) % (H + 80) - 40
            tw = 0.35 + 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * t * 0.35 + pha[i] * 3))
            a = alp[i] * tw
            r = rad[i] * 2.4
            key = round(r * 2, 1)
            k, s = kernels[key]
            x0, y0 = int(x - s // 2), int(y - s // 2)
            xa, ya = max(0, x0), max(0, y0)
            xb, yb = min(W, x0 + s), min(H, y0 + s)
            if xa >= xb or ya >= yb:
                continue
            kk = k[ya - y0:yb - y0, xa - x0:xb - x0][:, :, None]
            frame[ya:yb, xa:xb] += kk * a * c_gold

        # 极轻微胶片颗粒，压住渐变色带
        frame += rng.normal(0, 1.6, (H, W, 1)).astype(np.float32)
        np.clip(frame, 0, 255, out=frame)
        pr.stdin.write(frame.astype(np.uint8).tobytes())
    pr.stdin.close()
    pr.wait()
    p = os.path.join(OUT, f'{name}.mp4')
    print(f'{name}.mp4  {os.path.getsize(p)/1048576:.2f} MB')


render(['6A0000', '9C0000', '760000'], seed=11, n_part=120, gold='E8C87A',
       name='fx_part01', gain=0.82, vig=0.66)
render(['5E0000', '8E0000', '6A0000'], seed=42, n_part=150, gold='C9A227',
       name='fx_part02', gain=0.80, vig=0.68)
