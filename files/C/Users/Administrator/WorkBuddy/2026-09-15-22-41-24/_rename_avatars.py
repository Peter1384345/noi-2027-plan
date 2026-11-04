# -*- coding: utf-8 -*-
"""Rename generated avatars to assets/avatar_<key>.png based on prompt keywords."""
import io, os, re, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(ROOT, 'dragon-raja-story')
GEN = os.path.join(REPO, 'assets', '_gen')

MAPPING = [
    ('少年路明非', 'lumingfei'),
    ('路鸣泽', 'lumingze'),
    ('诺诺', 'nuonuo'),
    ('青年楚子航', 'chuzihang'),
    ('恺撒', 'kaisa'),
    ('绘梨衣', 'huiliyi'),
    ('夏弥', 'xiami'),
    ('源稚生', 'yuanzhisheng'),
    ('源稚女', 'yuanzhinv'),
    ('芬格尔', 'feneger'),
    ('少女零', 'ling'),
    ('昂热', 'angre'),
    ('赫尔佐格', 'heierzhuoge'),
    ('酒德麻衣', 'jiudemayi'),
    ('上杉越', 'shangshanyue'),
    ('路麟城', 'lulincheng'),
    ('陈雯雯', 'qiaoweini'),
    ('楚天骄', 'chutianjiao'),
    ('薯片妞', 'nuodong'),
    ('苏小妍', 'suxiaoyan'),
    ('酒德亚纪', 'jiudeyaji'),
    ('诺玛', 'nuoma'),
    ('牛仔模样', 'fulameier'),
    ('叶胜', 'yesheng'),
    ('曼斯', 'mansi'),
    ('古德里安', 'gudelian'),
    ('施耐德', 'shinaide'),
    ('康斯坦丁', 'kangstanding'),
    ('诺顿', 'nuodun'),
    ('芬里厄', 'fenlier'),
    ('白王', 'baiwang'),
    ('奥丁', 'aoding'),
    ('乔薇尼', 'qiaoweini2'),
    ('苏茜', 'suxi'),
    ('樱井小暮', 'yingjingxiaomu'),
    ('矢吹樱', 'yablowying'),
    ('帕西', 'paxijiatuosuo'),
    ('梅涅克', 'meiniieke'),
]

files = []
for dirpath, _, names in os.walk(GEN):
    for n in names:
        if n.lower().endswith('.png'):
            files.append(os.path.join(dirpath, n))

print('generated files found:', len(files))
done = {}
for kw, key in MAPPING:
    hits = [f for f in files if kw in os.path.basename(f)]
    if len(hits) != 1:
        print('ERROR: keyword %-8s matched %d files' % (kw, len(hits)))
        for h in hits:
            print('   ', os.path.basename(h))
        sys.exit(1)
    src = hits[0]
    dst = os.path.join(REPO, 'assets', 'avatar_%s.png' % key)
    shutil.copyfile(src, dst)
    done[key] = dst

print('renamed OK:', len(done))
# sanity: all expected avatar files exist now
missing = [k for _, k in MAPPING if not os.path.exists(os.path.join(REPO, 'assets', 'avatar_%s.png' % k))]
print('missing:', missing if missing else 'none')
shutil.rmtree(GEN)
print('staging removed')
