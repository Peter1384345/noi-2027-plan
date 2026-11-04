# -*- coding: utf-8 -*-
"""v7 全面校验"""
import sys, re, zipfile, collections
from pptx import Presentation

sys.stdout.reconfigure(encoding='utf-8')
F = r"C:/Users/Administrator/WorkBuddy/2026-10-21-22-12-58/微光成炬-星火自有燎原时（终版·v10）.pptx"

prs = Presentation(F)
print(f'总页数：{len(prs.slides)}')

print('\n【页序 + 动画】')
for i, s in enumerate(prs.slides, 1):
    x = s._element.xml
    n = len(re.findall(r'<p:cTn ', x))
    # 取标题类文字
    title = ''
    for sh in s.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip():
            t = sh.text_frame.text.strip().split('\n')[0]
            if len(t) > 3:
                title = t[:26]
                break
    print(f'  P{i:02d}  cTn={n:<4}  {title}')

print('\n【重复扫描】')
norm = {}
for i, s in enumerate(prs.slides, 1):
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        for l in sh.text_frame.text.split('\n'):
            l = l.strip()
            k = re.sub(r"[\s，。、：；！？\"'（）()·\-—]", "", l)
            if len(k) >= 8:
                norm.setdefault(k, []).append(i)
dups = {k: v for k, v in norm.items() if len(v) > 1}
if not dups:
    print('  无跨页重复（>=8字）')
for k, v in sorted(dups.items(), key=lambda x: -len(x[0])):
    print(f'  ×{len(v)} 页{v}: {k[:56]}')

print('\n【完整性】')
z = zipfile.ZipFile(F)
bad = z.testzip()
print('  ZIP CRC:', 'OK' if bad is None else f'BAD {bad}')
ct = z.read('[Content_Types].xml').decode('utf-8')
media = [n for n in z.namelist() if n.startswith('ppt/media/')]
print(f'  媒体文件: {len(media)}')
miss = []
for n in media:
    ext = n.rsplit('.', 1)[-1].lower()
    if f'Extension="{ext}"' not in ct:
        miss.append(n)
print('  content-type 缺失:', miss or '无')

# 视频容器检查
import struct
for n in media:
    if n.lower().endswith('.mp4'):
        d = z.read(n)
        atoms = []
        p = 0
        while p + 8 <= len(d):
            sz = struct.unpack('>I', d[p:p + 4])[0]
            ty = d[p + 4:p + 8].decode('latin1', 'ignore')
            atoms.append(ty)
            if sz < 8:
                break
            p += sz
        ok = 'moov' in atoms
        print(f'  {n}: {len(d)}B atoms={atoms[:6]} moov={"OK" if ok else "缺失!"}')

# rels 断链
print('\n【rels 断链】')
names = set(z.namelist())
broken = 0
for n in names:
    if not n.endswith('.rels'):
        continue
    base = n.replace('_rels/', '').replace('.rels', '')
    d = n.rsplit('/', 1)[0].rsplit('_rels', 1)[0]
    rels = z.read(n).decode('utf-8')
    for tgt, mode in re.findall(r'Target="([^"]+)"(?:\s+TargetMode="(\w+)")?', rels):
        if mode == 'External' or tgt.startswith('http'):
            continue
        import posixpath
        full = posixpath.normpath(posixpath.join(d, tgt))
        if full not in names:
            print(f'  BROKEN {n} -> {tgt}')
            broken += 1
print('  断链数:', broken)

# 动画 spid 悬空
print('\n【动画 spid 悬空】')
for i, s in enumerate(prs.slides, 1):
    x = s._element.xml
    spids = set(re.findall(r'<p:cNvPr id="(\d+)"', x))
    used = set(re.findall(r'<p:spTgt spid="(\d+)"', x))
    dangling = used - spids
    if dangling:
        print(f'  P{i:02d} 悬空 spid: {sorted(dangling)}')
print('  （无输出即为正常）')
