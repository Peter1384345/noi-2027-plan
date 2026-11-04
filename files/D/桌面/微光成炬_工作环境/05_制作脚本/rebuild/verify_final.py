import zipfile, re
from lxml import etree
from pptx import Presentation
ns = 'http://schemas.openxmlformats.org/drawingml/2006/main'
NEW = 'D:/桌面/微光成炬_工作环境/06_成品输出/微光成炬-星火自有燎原时_重做版22页_按原版_修复字体.pptx'
BASE = {
    '微软雅黑':  ('en-US', '020B0503020204020204', '-122'),
    'Georgia':   ('en-US', '02040502050405020303', None),
    '仿宋':      ('zh-CN', '02010609060101010101', '-122'),
    'STXingkai': ('zh-CN', None, None),
}
z = zipfile.ZipFile(NEW)
print('zip完整性:', 'OK' if z.testzip() is None else 'BAD', '| 条目:', len(z.namelist()))

# 视频自动播放
vid = 0
for n in z.namelist():
    if re.match(r'ppt/slides/_rels/slide\d+\.xml\.rels', n) and 'relationships/media' in z.read(n).decode('utf-8','ignore'):
        sid = int(re.search(r'slide(\d+)\.xml', n).group(1))
        if 'cMediaNode' in z.read(f'ppt/slides/slide{sid}.xml').decode('utf-8','ignore'):
            vid += 1
print('自动播放视频页数:', vid)

# 新页字体识别码核对
res = {}
for n in z.namelist():
    if not re.match(r'ppt/slides/slide\d+\.xml', n): continue
    sid = int(re.search(r'slide(\d+)\.xml', n).group(1))
    root = etree.fromstring(z.read(n))
    for r in root.iter('{%s}r' % ns):
        rPr = r.find('{%s}rPr' % ns)
        if rPr is None: continue
        lang = rPr.get('lang')
        for tag in ('latin','ea'):
            el = rPr.find('{%s}%s' % (ns, tag))
            if el is None: continue
            tf = el.get('typeface')
            if tf is None: continue
            res.setdefault(sid, {}).setdefault(tf, set()).add((lang, el.get('panose'), el.get('charset')))
bad = 0
for sid in range(16, 23):
    for tf, vals in res.get(sid, {}).items():
        for (lang, pano, char) in vals:
            exp = BASE.get(tf)
            if exp and (lang, pano, char) != exp:
                bad += 1; print('  BAD s%d %s' % (sid, tf))
print('新页字体识别码不符项数:', bad)

# 章节标题文本
prs = Presentation(NEW)
print('总页数:', len(prs.slides))
titles = {}
for i, s in enumerate(prs.slides, 1):
    for sh in s.shapes:
        if sh.has_text_frame:
            for para in sh.text_frame.paragraphs:
                for r in para.runs:
                    if r.text.strip() in ('寒门筑梦','高山邮路','微光 · 韩雅平','成炬 · 陈新超'):
                        titles.setdefault(i, set()).add(r.text.strip())
for i in sorted(titles):
    print(f'  P{i}:', ' / '.join(sorted(titles[i])))
