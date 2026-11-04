# -*- coding: utf-8 -*-
"""探测 cjyun 视频播放器接口"""
import urllib.request, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
      'Referer': 'https://app.cjyun.org/'}

d = urllib.request.urlopen(urllib.request.Request(
    'https://app.cjyun.org/assets/libraries/ckplayer-x/index.js?_=20260730', headers=UA), timeout=25
).read().decode('utf-8', 'ignore')
open('idx.js', 'w', encoding='utf-8').write(d)
print('len', len(d))
hits = sorted(set(re.findall(r'["\']([^"\']*(?:api|/video/|\.php|json)[^"\']*)["\']', d)))
for h in hits[:25]:
    print('  ', h)
