# -*- coding: utf-8 -*-
"""扫描新闻页面，尝试提取可直接下载的 mp4 视频直链。"""
import re
import ssl
import urllib.request

PAGES = {
    "netease_fanren": "https://3g.163.com/news/article/KFC0TOKJ053469LG.html",
    "hubeidaily_tieziniang": "https://epaper.hubeidaily.net/pc/content/202605/11/content_347621.html",
    "huangshi_xiangyouhua": "https://www.huangshi.gov.cn/ztjj/cjqgwmcs/pyhjxsh/202302/t20230221_992095.html",
    "wenming_cn_kangai": "http://www.wenming.cn/sbhr_pd/20260225/42c65ee6b27244b683361f6f007d2a44/c.html",
}
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
HDRS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

report = []
for name, url in PAGES.items():
    try:
        req = urllib.request.Request(url, headers=HDRS)
        html = urllib.request.urlopen(req, timeout=20, context=CTX).read().decode("utf-8", errors="replace")
        mp4s = sorted(set(re.findall(r'https?://[^\s"\'<>\\]+?\.mp4[^\s"\'<>\\]*', html)))
        m3u8s = sorted(set(re.findall(r'https?://[^\s"\'<>\\]+?\.m3u8[^\s"\'<>\\]*', html)))
        vids = sorted(set(re.findall(r'(?:data-vid|vid)["\']?\s*[:=]\s*["\']([A-Za-z0-9]+)["\']', html)))[:5]
        report.append(f"[{name}] bytes={len(html)}\n  mp4={mp4s[:5]}\n  m3u8={m3u8s[:3]}\n  vids={vids}")
    except Exception as e:
        report.append(f"[{name}] ERROR: {e!r}")

out = "\n".join(report)
print(out)
open(r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27\output\video_scan_result.txt", "w", encoding="utf-8").write(out)
