import zipfile, re
from lxml import etree
ns = 'http://schemas.openxmlformats.org/drawingml/2006/main'
NEW = 'D:/桌面/微光成炬_工作环境/06_成品输出/微光成炬-星火自有燎原时_重做版22页_按目录统一_修复字体.pptx'
ORIG = 'D:/桌面/微光成炬_工作环境/01_初代版本/微光成炬-星火自有燎原时_小组原始版.pptx'

# 原版逐字元数据基准
BASE = {
    '微软雅黑':  ('en-US', '020B0503020204020204', '-122'),
    'Georgia':   ('en-US', '02040502050405020303', None),
    '仿宋':      ('zh-CN', '02010609060101010101', '-122'),
    'STXingkai': ('zh-CN', None, None),
}

def scan(pptx):
    z = zipfile.ZipFile(pptx)
    res = {}
    for n in z.namelist():
        if not re.match(r'ppt/slides/slide\d+\.xml', n):
            continue
        sid = int(re.search(r'slide(\d+)\.xml', n).group(1))
        root = etree.fromstring(z.read(n))
        for r in root.iter('{%s}r' % ns):
            rPr = r.find('{%s}rPr' % ns)
            if rPr is None:
                continue
            lang = rPr.get('lang')
            for tag in ('latin', 'ea'):
                el = rPr.find('{%s}%s' % (ns, tag))
                if el is None:
                    continue
                tf = el.get('typeface')
                if tf is None:
                    continue
                res.setdefault(sid, {}).setdefault(tf, set()).add(
                    (lang, el.get('panose'), el.get('charset')))
    return res

new = scan(NEW)
# 物理 slide16-22 是新页（插入的 7 页）
print('=== 新页(slide16-22) 字体识别码核对 ===')
bad = 0
for sid in range(16, 23):
    for tf, vals in new.get(sid, {}).items():
        for (lang, pano, char) in vals:
            exp = BASE.get(tf)
            if exp is None:
                continue
            ok = (lang == exp[0]) and (pano == exp[1]) and (char == exp[2])
            flag = 'OK ' if ok else 'BAD'
            if not ok:
                bad += 1
            print(f'  s{sid} {tf:<10} lang={lang} panose={pano} charset={char} [{flag}]')
print('新页字体识别码不符项数:', bad)

# 完整性 + 视频自动播放
import zipfile as zf
z = zf.ZipFile(NEW)
print('zip完整性:', 'OK' if z.testzip() is None else 'BAD', '| 条目:', len(z.namelist()))
vid = 0
for n in z.namelist():
    if re.match(r'ppt/slides/_rels/slide\d+\.xml\.rels', n) and 'relationships/media' in z.read(n).decode('utf-8','ignore'):
        sid = int(re.search(r'slide(\d+)\.xml', n).group(1))
        xml = z.read(f'ppt/slides/slide{sid}.xml').decode('utf-8','ignore')
        if 'cMediaNode' in xml:
            vid += 1
print('自动播放视频页数:', vid)
