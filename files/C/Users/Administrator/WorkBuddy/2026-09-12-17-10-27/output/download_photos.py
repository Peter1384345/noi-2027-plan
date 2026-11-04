# -*- coding: utf-8 -*-
"""下载新闻配图（用作视频占位卡底图）；失败则记录，由海报脚本兜底。"""
import re
import ssl
import urllib.request
from pathlib import Path

OUT = Path(r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27\output\videos\photos")
OUT.mkdir(parents=True, exist_ok=True)
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
HDRS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Referer": "https://mp.weixin.qq.com/"}

# 韩雅平报道中的真实配图（qpic 直链，来自此前检索到的报道页）
DIRECT = {
    "han_xibao.jpg": "https://mmbiz.qpic.cn/sz_mmbiz_jpg/z8icaWS616QVic0Nwa41ZEW1k8CnFNicvvXwzMECVhmTKMRvVf3vicYpvmOov56kSawqFN12IkAEPBHSpnjvehZrZSeRD8XsLKhKVc66hLHJibAI/640?wx_fmt=jpeg",
    "han_jiangzhuang.jpg": "https://mmbiz.qpic.cn/mmbiz_jpg/z8icaWS616QU1XJMydxib0vK5mM1nsPK4Hk4YDtzffglWyHl0ad7Etu2b41hWrg7iapIP5U76Xhib6PiaY5DCTFmIbEW5hQdBtibFc3stqs/640?wx_fmt=jpeg",
}
# 陈新超报道页面，扫描文章配图
SCAN_PAGES = {
    "chen": "https://epaper.hubeidaily.net/pc/content/202605/11/content_347621.html",
    "chen2": "https://www.huangshi.gov.cn/ztjj/cjqgwmcs/pyhjxsh/202302/t20230221_992095.html",
    "chen3": "https://news.hubeidaily.net/pc/c_2220895.html",
}

def fetch(url):
    req = urllib.request.Request(url, headers=HDRS)
    return urllib.request.urlopen(req, timeout=25, context=CTX).read()

log = []
for name, url in DIRECT.items():
    try:
        data = fetch(url)
        (OUT / name).write_bytes(data)
        log.append(f"OK {name} bytes={len(data)}")
    except Exception as e:
        log.append(f"FAIL {name}: {e!r}")

for tag, page in SCAN_PAGES.items():
    try:
        html = fetch(page).decode("utf-8", errors="replace")
        imgs = re.findall(r'https?://[^\s"\'<>\\]+?\.(?:jpg|jpeg|png)[^\s"\'<>\\]*', html)
        imgs = [u for u in imgs if "logo" not in u.lower() and "icon" not in u.lower()]
        log.append(f"[{tag}] imgs_found={len(imgs)} first={imgs[:3]}")
        n = 0
        for u in imgs[:4]:
            try:
                data = fetch(u)
                if len(data) > 8000:  # 过滤小图标
                    (OUT / f"{tag}_{n}.jpg").write_bytes(data)
                    n += 1
            except Exception as e:
                log.append(f"  FAIL {tag}_{n}: {e!r}")
        log.append(f"[{tag}] saved={n}")
    except Exception as e:
        log.append(f"[{tag}] ERROR: {e!r}")

out = "\n".join(log)
print(out)
Path(r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27\output\photo_download_log.txt").write_text(out, encoding="utf-8")
