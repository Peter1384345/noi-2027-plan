# -*- coding: utf-8 -*-
"""终版 v6：删除圆环开场体系 + 影像页升级四联官媒纪实墙"""
import os, re, shutil, zipfile
from lxml import etree
from PIL import Image

U = 'u'
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
P = '{%s}' % NS['p']
R = '{%s}' % NS['r']

log = []
def say(x):
    print(x); log.append(x)

# ---------------- A. 定位并删除「圆环开场页」 ----------------
prels = open(f'{U}/ppt/_rels/presentation.xml.rels', encoding='utf-8').read()
rid2slide = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="slides/(slide\d+\.xml)"', prels))
pres = open(f'{U}/ppt/presentation.xml', encoding='utf-8').read()
sldids = re.findall(r'<p:sldId id="(\d+)" r:id="(rId\d+)"/>', pres)
order = [rid2slide[r] for _, r in sldids]
say('当前页序: ' + ', '.join(order))
target = order[1]  # 第 2 页
xml_t = open(f'{U}/ppt/slides/{target}', encoding='utf-8').read()
assert 'Groove' in xml_t, '第2页不是圆环开场页'
say(f'删除第2页 {target}（圆环开场页，Groove x{xml_t.count("Groove")}）')

# 移除 sldIdLst 条目
pres = re.sub(r'<p:sldId id="%s" r:id="%s"/>' % (sldids[1][0], sldids[1][1]), '', pres, count=1)
open(f'{U}/ppt/presentation.xml', 'w', encoding='utf-8').write(pres)

# 移除 presentation rels 条目
prels = re.sub(r'<Relationship Id="%s"[^>]*/>' % sldids[1][1], '', prels, count=1)
open(f'{U}/ppt/_rels/presentation.xml.rels', 'w', encoding='utf-8').write(prels)

# 删除 slide 文件与 rels
os.remove(f'{U}/ppt/slides/{target}')
rp = f'{U}/ppt/slides/_rels/{target}.rels'
if os.path.exists(rp): os.remove(rp)

# content-types override 移除
cp = f'{U}/[Content_Types].xml'
ct = open(cp, encoding='utf-8').read()
ct2 = re.sub(r'<Override PartName="/ppt/slides/%s"[^>]*/>' % target, '', ct)
open(cp, 'w', encoding='utf-8').write(ct2)
say(f'content-types override 移除: {len(ct)-len(ct2)} 字节')

# ---------------- B. 封面：删除圆环类形状 + 其动画 ----------------
RING_NAMES = {'Glow Halo', 'Ripple 1', 'Ripple 2', 'Ripple 3', 'Ripple 4', 'Ripple 5', 'Ripple 6',
              'Spin Outer', 'Spin Inner', 'Breath Dot'}
p1 = f'{U}/ppt/slides/slide1.xml'
root = etree.parse(p1)
spTree = root.find('.//' + P + 'cSld/' + P + 'spTree')
ring_ids = set()
for sp in list(spTree):
    nv = sp.find('.//' + P + 'cNvPr')
    if nv is not None and nv.get('name') in RING_NAMES:
        ring_ids.add(nv.get('id'))
        spTree.remove(sp)
say(f'封面删除形状: {sorted(ring_ids)}')

timing = root.find('.//' + P + 'timing')
LEAF = {P + x for x in ('set', 'animEffect', 'animScale', 'animRot', 'animMotion', 'anim', 'animClr', 'cmd', 'audio', 'video', 'play')}
removed_leaf = 0
for leaf in list(timing.iter()):
    if leaf.tag in LEAF:
        hit = [tg for tg in leaf.iter(P + 'spTgt') if tg.get('spid') in ring_ids]
        if hit:
            leaf.getparent().remove(leaf)
            removed_leaf += 1
say(f'封面删除动画叶节点: {removed_leaf}')

# 回收空容器
pruned = 0
changed = True
guard = 0
while changed and guard < 50:
    changed = False; guard += 1
    for ctn in list(timing.iter(P + 'childTnLst')):
        if len(ctn) == 0:
            par = ctn.getparent()            # p:par
            if par is None: continue
            gp = par.getparent()
            if gp is None: continue
            if gp.tag in (P + 'tnLst', P + 'timing'): continue
            # 祖先链必须是 effect 组而不是 mainSeq 根
            if par.tag == P + 'par':
                gp.remove(par); pruned += 1; changed = True
say(f'封面回收空分组: {pruned}')
root.write(p1, xml_declaration=True, encoding='UTF-8', standalone=True)

# 校验
x1 = open(p1, encoding='utf-8').read()
ids_now = set(re.findall(r'<p:cNvPr id="(\d+)"', x1))
t1 = x1[x1.find('<p:timing>'):]
dangle = sorted(set(re.findall(r'spid="(\d+)"', t1)) - ids_now)
say(f'封面 animation dangling: {dangle or 0} | 剩余 cTn: {t1.count("<p:cTn")}')

# ---------------- C. 目录页：删除凹槽环 ----------------
p4 = f'{U}/ppt/slides/slide4.xml'
x4 = open(p4, encoding='utf-8').read()
n_groove = len(re.findall(r'<p:sp><p:nvSpPr><p:cNvPr id="\d+" name="Toc Groove [AB]"/>', x4))
x4 = re.sub(r'<p:sp><p:nvSpPr><p:cNvPr id="\d+" name="Toc Groove [AB]"/>.*?</p:sp>', '', x4, flags=re.S)
open(p4, 'w', encoding='utf-8').write(x4)
say(f'目录页删除凹槽环: {n_groove} | 剩余 grpFill: {x4.count("<a:grpFill/>")} | cTn: {x4[x4.find("<p:timing>"):].count("<p:cTn")}')

# ---------------- D. 影像页：四联官媒纪实墙 ----------------
MEDIA = f'{U}/ppt/slides/media'
# 压缩为 jpg
jpgs = []
for i in range(1, 5):
    src = f'yxtv_{i}.png'
    dst = os.path.join(MEDIA, f'image3{i}.jpg')
    im = Image.open(src).convert('RGB')
    im.save(dst, 'JPEG', quality=88, optimize=True)
    jpgs.append((f'image3{i}.jpg', im.size))
    say(f'  {dst} {im.size} {os.path.getsize(dst)//1024}KB')

p16 = f'{U}/ppt/slides/slide16.xml'
x16 = open(p16, encoding='utf-8').read()
# 删除原有两张图片
x16 = re.sub(r'<p:pic><p:nvPicPr><p:cNvPr id="15[23]" name="chen_photo_[ab]\.jpg"/>.*?</p:pic>', '', x16, flags=re.S)

def pic(pid, name, rid, x, y, w, h):
    return (f'<p:pic><p:nvPicPr><p:cNvPr id="{pid}" name="{name}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rid}"/><a:srcRect l="1850" r="1850"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:ln w="9525"><a:solidFill><a:srgbClr val="C9A227"><a:alpha val="45000"/></a:srgbClr></a:solidFill></a:ln></p:spPr></p:pic>')

W1 = 329 * 9525; H1 = 192 * 9525; GAP = 8 * 9525
X1, Y1 = 53 * 9525, 157 * 9525
X2 = X1 + W1 + GAP
Y2 = Y1 + H1 + GAP
grid = (pic(152, 'yxtv_day_1.jpg', 'rId1', X1, Y1, W1, H1) +
        pic(153, 'yxtv_day_2.jpg', 'rId2', X2, Y1, W1, H1) +
        pic(8004, 'yxtv_day_3.jpg', 'rId3', X1, Y2, W1, H1) +
        pic(8005, 'yxtv_day_4.jpg', 'rId4', X2, Y2, W1, H1))
# 插到背景之后（spTree 第3个子元素后）
m = re.search(r'(<p:spTree>.*?</p:spTree>)', x16, re.S)
tree = m.group(1)
# 背景通常是第一个 sp
first = re.search(r'<p:sp>.*?</p:sp>', tree, re.S)
x16 = x16.replace(first.group(0), first.group(0) + grid, 1)

repl = [
    ('影像取自极目新闻官方报道配图（2025 年 11 月 27 日）。', '影像取自阳新县融媒体中心官方报道（2026 年 4 月 30 日）。'),
    ('极目新闻（楚天都市报）官方报道配图', '阳新县融媒体中心 · 记者跟拍的一天'),
    ('陈新超真实工作照（图片由受访者提供）', '记者跟随陈新超，记录下她忙碌的一天'),
    ('图片来源：极目新闻 2025-11-27 报道《一人一车一天奔波120余公里》', '图片来源：阳新县融媒体中心 2026-04-30 报道《乡邮路上的「铁娘子」》'),
]
for a, b in repl:
    assert a in x16, a
    x16 = x16.replace(a, b)
open(p16, 'w', encoding='utf-8').write(x16)

# rels
rp16 = f'{U}/ppt/slides/_rels/slide16.xml.rels'
r16 = open(rp16, encoding='utf-8').read()
r16 = re.sub(r'<Relationship Id="rId[34]"[^>]*/>', '', r16)
r16 = r16.replace('</Relationships>',
    '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image33.jpg" />'
    '<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image34.jpg" /></Relationships>')
r16 = r16.replace('media/image10.jpg', 'media/image31.jpg').replace('media/image11.jpg', 'media/image32.jpg')
open(rp16, 'w', encoding='utf-8').write(r16)
say('影像页 rels 更新完成')

# ---------------- E. 重新打包 ----------------
dst = '微光成炬-星火自有燎原时（终版·v6）.pptx'
if os.path.exists(dst): os.remove(dst)
zf = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
zf.write(f'{U}/[Content_Types].xml', '[Content_Types].xml')
for root_d, _, fs in os.walk(U):
    for f in fs:
        fp = os.path.join(root_d, f)
        arc = os.path.relpath(fp, U).replace('\\', '/')
        if arc == '[Content_Types].xml': continue
        zf.write(fp, arc)
zf.close()
say(f'打包完成: {dst} {os.path.getsize(dst)/1048576:.1f}MB')
