# -*- coding: utf-8 -*-
"""v10-2：生成章节页氛围特效视频（深红渐变 + 金色微光粒子，无人物）"""
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


def base_frame(stops, angle=0.55, vignette=0.38):
    """三段渐变 + 暗角"""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = (xx / W) * angle + (yy / H) * (1 - angle)
    c0, c1, c2 = [hex2rgb(s) for s in stops]
    out = np.zeros((H, W, 3), dtype=np.float32)
    m1 = t < 0.55
    k1 = (t[m1] / 0.55)[:, None]
    out[m1] = c0 * (1 - k1) + c1 * k1
    m2 = ~m1
    k2 = ((t[m2] - 0.55) / 0.45)[:, None]
    out[m2] = c1 * (1 - k2) + c2 * k2
    # 暗角
    rx = (xx - W / 2) / (W / 2)
    ry = (yy - H / 2) / (H / 2)
    r = np.sqrt(rx ** 2 + ry ** 2) / 1.414
    out *= (1 - vignette * r ** 2)[:, :, None]
    return out


def gauss_blob(size, sigma):
    ax = np.arange(size, dtype=np.float32) - (size - 1) / 2
    g = np.exp(-(ax[:, None] ** 2 + ax[None, :] ** 2) / (2 * sigma ** 2))
    return g


def render(stops, seed, n_part=190, gold='E8C87A', gold2='C9A227', name='fx'):
    rng = np.random.default_rng(seed)
    base = base_frame(stops)
    c_a, c_b = hex2rgb(gold), hex2rgb(gold2)

    # 粒子参数
    px = rng.uniform(0, W, n_part)
    py = rng.uniform(0, H, n_part)
    rad = rng.uniform(1.2, 4.4, n_part)
    spd = rng.uniform(4, 22, n_part)          # 每秒上浮像素
    amp = rng.uniform(4, 26, n_part)          # 横向摆动
    pha = rng.uniform(0, 2 * np.pi, n_part)
    alp = rng.uniform(0.25, 1.0, n_part)
    big = rng.random(n_part) > 0.88           # 少量大颗粒

    # 预渲染光斑
    kernels = {}
    for i in range(n_part):
        r = rad[i] * (3.0 if big[i] else 2.2)
        key = round(r * 2, 1)
        if key not in kernels:
            s = max(5, int(key * 2) | 1)
            kernels[key] = (gauss_blob(s, r), s)

    cmd = [FF, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
           '-r', str(FPS), '-i', '-', '-an',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '24',
           '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
           os.path.join(OUT, f'{name}.mp4')]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)

    for f in range(NF):
        t = f / FPS
        frame = base.copy()
        # 缓慢呼吸的整体光晕
        glow = 0.05 + 0.035 * np.sin(2 * np.pi * t / DUR)
        frame += frame * glow
        for i in range(n_part):
            x = px[i] + amp[i] * np.sin(2 * np.pi * t / (DUR * 0.6) + pha[i])
            y = (py[i] - spd[i] * t) % (H + 120) - 60
            tw = 0.55 + 0.45 * np.sin(2 * np.pi * t * 0.45 + pha[i] * 2)
            a = alp[i] * tw
            r = rad[i] * (3.0 if big[i] else 2.2)
            key = round(r * 2, 1)
            k, s = kernels[key]
            x0, y0 = int(x - s // 2), int(y - s // 2)
            xa, ya = max(0, x0), max(0, y0)
            xb, yb = min(W, x0 + s), min(H, y0 + s)
            if xa >= xb or ya >= yb:
                continue
            kk = k[ya - y0:yb - y0, xa - x0:xb - x0][:, :, None]
            col = (c_a if big[i] else c_b)[None, None, :]
            frame[ya:yb, xa:xb] += kk * a * col * (0.9 if big[i] else 0.55)
        np.clip(frame, 0, 255, out=frame)
        pr.stdin.write(frame.astype(np.uint8).tobytes())
    pr.stdin.close()
    pr.wait()
    p = os.path.join(OUT, f'{name}.mp4')
    print(f'{name}.mp4  {os.path.getsize(p)/1048576:.2f} MB')


# PART 01 韩雅平：暖金微光（原版深红渐变 #8E0000→#C00000→#9E0000）
render(['8E0000', 'C00000', '9E0000'], seed=11, n_part=200,
       gold='E8C87A', gold2='C9A227', name='fx_part01')

# PART 02 陈新超：略沉的赤金 + 更多尘埃（邮路尘土感）
render(['7E0000', 'B00000', '8E0000'], seed=42, n_part=230,
       gold='C9A227', gold2='A88016', name='fx_part02')
