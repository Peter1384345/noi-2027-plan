# -*- coding: utf-8 -*-
"""下载候选报道图片并输出尺寸信息"""
import urllib.request, os, sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
      'Referer': 'https://www.hbtv.com.cn/'}

URLS = [
    ('hbtv_a', 'https://img.cjyun.org/a/10008/202610/16626f08b0b38c3f958aacb79b2d2615.jpeg'),
    ('hbtv_b', 'https://img.cjyun.org/a/10008/202610/575ae454f81e93085f1b4a47f9f6b6cb.jpeg'),
    ('hbtv_c', 'https://img.cjyun.org/a/10008/202610/df9319d6c09b8ea789725f774c97fadf.jpeg'),
    ('yxtv_d', 'https://res.cjyun.org/a/10104/202405/bee00d38957b48445dda6ed371af4791.jpeg'),
]

os.makedirs('cand', exist_ok=True)
for name, u in URLS:
    out = f'cand/{name}.jpg'
    try:
        req = urllib.request.Request(u, headers=UA)
        data = urllib.request.urlopen(req, timeout=30).read()
        open(out, 'wb').write(data)
        im = Image.open(out)
        print(f'{name}: {len(data)} bytes  {im.size[0]}x{im.size[1]}  {im.mode}')
    except Exception as e:
        print(name, 'ERR', str(e)[:90])
