# -*- coding: utf-8 -*-
"""Download remote images referenced by the HTML and rewrite src to local paths.

Rationale: html-to-docx fetches remote <img> during conversion; a failing or
slow fetch aborts the run and silently truncates the document. Pre-downloading
makes conversion deterministic and embeds the original figures.
"""
import io, os, re, sys, time
import urllib.request

HTML = sys.argv[1]
ASSETS = os.path.join(os.path.dirname(HTML), "assets")
os.makedirs(ASSETS, exist_ok=True)

html = io.open(HTML, encoding="utf-8").read()
srcs = []
for m in re.finditer(r'<img[^>]*src="([^"]+)"', html):
    if m.group(1) not in srcs:
        srcs.append(m.group(1))

mapping = {}
ok = fail = skipped = 0
for i, src in enumerate(srcs):
    ext = src.split("?")[0].rsplit(".", 1)[-1].lower()
    if ext == "svg":
        # Word cannot embed SVG reliably: keep an explicit figure caption
        skipped += 1
        mapping[src] = None
        continue
    name = "img_%03d.%s" % (i + 1, "png" if ext in ("apng", "gif", "png", "jpg", "jpeg", "webp") else ext)
    path = os.path.join(ASSETS, name)
    if not os.path.exists(path):
        try:
            req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=30).read()
            if len(data) < 1000:
                raise RuntimeError("too small: %d bytes" % len(data))
            open(path, "wb").write(data)
            ok += 1
        except Exception as e:
            print("FAIL", src, e)
            fail += 1
            mapping[src] = None
            continue
    mapping[src] = path.replace("\\", "/")
    time.sleep(0.05)

# rewrite HTML
def repl(m):
    tag = m.group(0)
    src = m.group(1)
    local = mapping.get(src)
    if local:
        return tag.replace(src, local)
    # unresolvable image -> explicit text placeholder (no broken layout)
    alt = re.search(r'alt="([^"]*)"', tag)
    alt = alt.group(1) if alt else "图示"
    return '<p>[图示：%s]（%s）</p>' % (alt, src)

html2 = re.sub(r'<img[^>]*src="([^"]+)"[^>]*/?>', repl, html)
io.open(HTML, "w", encoding="utf-8").write(html2)
print("images: total=%d downloaded=%d failed=%d placeholder=%d" % (len(srcs), ok, fail, skipped + fail))
