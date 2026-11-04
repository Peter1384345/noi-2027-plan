# -*- coding: utf-8 -*-
"""试探 cjyun video 播放接口"""
import urllib.request, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
      'Referer': 'https://www.hbtv.com.cn/'}

for u in ['https://app.cjyun.org/video/player/video?sid=13687',
          'https://app.cjyun.org/video/player/video?vid=13687',
          'https://app.cjyun.org/video/player/stream?stream_id=13687',
          'https://app.cjyun.org/video/player/config?sid=13687']:
    try:
        d = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25).read().decode('utf-8', 'ignore')
        print('==', u, len(d))
        print('   ', d[:400].replace('\n', ' '))
        for m in set(re.findall(r'(https?:[^"\'\\ ]+\.(?:mp4|m3u8|flv))', d)):
            print('    MP4>', m)
    except Exception as e:
        print(u, 'ERR', str(e)[:70])
