import zipfile, re
from lxml import etree
ns = 'http://schemas.openxmlformats.org/drawingml/2006/main'
z = zipfile.ZipFile('D:/桌面/微光成炬_工作环境/01_初代版本/微光成炬-星火自有燎原时_小组原始版.pptx')
seen = {}
for n in z.namelist():
    if not re.match(r'ppt/slides/slide\d+\.xml', n):
        continue
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
            if tf is None or tf in seen:
                continue
            seen[tf] = (lang, el.get('panose'), el.get('charset'), el.get('pitchFamily'))
print('count=', len(seen))
for tf, (lang, pano, char, pf) in seen.items():
    print(repr(tf), 'lang=%r panose=%r charset=%r pitch=%r' % (lang, pano, char, pf))
