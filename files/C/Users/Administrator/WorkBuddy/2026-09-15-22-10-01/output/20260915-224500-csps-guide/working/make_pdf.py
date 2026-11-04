# -*- coding: utf-8 -*-
"""Render the formatted HTML to a print-ready PDF via headless Edge.

PDF embeds its fonts, so what you see is exactly what prints - no dependency
on the fonts installed in WPS/Word.
"""
import io
import os
import subprocess
import sys

PRINT_CSS = """
<style>
@page { size: A4; margin: 16mm 14mm 16mm 14mm; }
html, body {
  font-family: "SimSun", "Songti SC", "Times New Roman", serif !important;
  font-size: 10.5pt; line-height: 1.5; color: #000;
}
/* the web theme spreads CJK headings with 0.3em tracking; on paper that
   reads as "双 向 同 时 搜 索" and wastes width */
* { letter-spacing: normal !important; word-spacing: normal !important; }
pre, pre code, code {
  font-family: Consolas, "Courier New", "DejaVu Sans Mono", monospace !important;
  font-size: 8.5pt !important;
  line-height: 1.35 !important;
  white-space: pre-wrap !important;
  word-break: break-all;
  background: #f4f6f8 !important;
  border: 1px solid #c9d1d9 !important;
  border-radius: 2px;
  padding: 6px 8px !important;
  margin: 6px 0 !important;
  page-break-inside: avoid;
}
h1, h2, h3, h4 { page-break-after: avoid; page-break-inside: avoid; color: #000 !important; }
h2 { margin-top: 14pt !important; font-size: 15pt !important; }
h3 { font-size: 12.5pt !important; }
img { max-width: 100% !important; height: auto !important; page-break-inside: avoid; }
table { border-collapse: collapse; page-break-inside: avoid; width: 100%; }
th, td { border: 1px solid #999 !important; padding: 3px 6px; font-size: 9.5pt; }
p { orphans: 2; widows: 2; }
nav, .toc, .toc-list { page-break-after: always; }
a { color: #000 !important; text-decoration: none !important; }
</style>
</head>
"""

EDGE = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def find_browser():
    for p in EDGE:
        if os.path.exists(p):
            return p
    return None


def main(html_path, pdf_path):
    html = io.open(html_path, encoding="utf-8").read()
    if "</head>" in html:
        html = html.replace("</head>", PRINT_CSS, 1)
    else:
        html = PRINT_CSS.replace("</head>", "") + html
    tmp = os.path.splitext(html_path)[0] + ".print.html"
    io.open(tmp, "w", encoding="utf-8").write(html)

    browser = find_browser()
    if not browser:
        raise RuntimeError("no headless browser found (Edge/Chrome)")
    url = "file:///" + os.path.abspath(tmp).replace("\\", "/")
    cmd = [browser, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
           '--print-to-pdf=%s' % os.path.abspath(pdf_path), url]
    subprocess.run(cmd, check=True, timeout=900)
    size = os.path.getsize(pdf_path)
    print("pdf written: %s (%.1f MB)" % (pdf_path, size / 1048576.0))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
