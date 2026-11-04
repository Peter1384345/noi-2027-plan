# -*- coding: utf-8 -*-
"""Build formatted HTML from a markdown draft (generalized pipeline Stage 2 builder)."""
import io, json, re, sys

import markdown

PLUGIN = r"C:\Users\Administrator\.workbuddy\plugins\cache\workbuddy-builtin\tencent-docx\5.5.6-wb.38337834.g5f969292.h7826dc9400fd"
MD_PATH = sys.argv[1]
OUT_PATH = sys.argv[2]
TITLE = sys.argv[3]
SUBTITLE = sys.argv[4] if len(sys.argv) > 4 else ""
EYEBROW = sys.argv[5] if len(sys.argv) > 5 else "DOCUMENT"

with io.open(PLUGIN + r"\skills\design-token\tokens\compiled\general.json", "r", encoding="utf-8") as f:
    tokens = json.load(f)
css_vars = "\n".join("    %s: %s;" % (k, v) for k, v in tokens["css_variables"].items())

with io.open(MD_PATH, "r", encoding="utf-8") as f:
    md_text = f.read()
lines = md_text.split("\n")
assert lines[0].startswith("# "), "first line must be H1"
md_body = "\n".join(lines[1:])

html_body = markdown.markdown(
    md_body,
    extensions=["tables", "fenced_code", "toc"],
    extension_configs={"toc": {"toc_depth": "2"}},
)

counter = {"n": 0}
def add_id(m):
    counter["n"] += 1
    return '<h2 id="section-%d">%s</h2>' % (counter["n"], m.group(1))
html_body = re.sub(r'<h2(?: id="[^"]*")?>(.*?)</h2>', add_id, html_body, flags=re.S)
h2s = re.findall(r'<h2 id="section-\d+">(.*?)</h2>', html_body)
toc_items = "\n".join(
    '      <li><a href="#section-%d">%s</a></li>' % (i + 1, t)
    for i, t in enumerate(h2s)
)
html_body = html_body.replace("<blockquote>\n<p>", "<blockquote>\n<p>&nbsp;&nbsp;")

# --- normalize code blocks inside HTML (defensive; markdown output only) ---
html_body = html_body.replace("\t", "    ")

HTML_TEMPLATE = open(r"C:\Users\Administrator\WorkBuddy\2026-09-15-22-10-01\output\20260915-224500-csps-guide\working\html_template.html", "r", encoding="utf-8").read()

HTML = (HTML_TEMPLATE
        .replace("@CSS_VARS@", css_vars)
        .replace("@TITLE@", TITLE)
        .replace("@SUBTITLE@", SUBTITLE)
        .replace("@EYEBROW@", EYEBROW)
        .replace("@COVER_META@", "整理自 csp.wiki CSP-S 文档板块<br>2026 年 9 月")
        .replace("@TOC_ITEMS@", toc_items)
        .replace("@BODY@", html_body))

import os
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with io.open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(HTML)

print("written:", OUT_PATH)
print("h2 sections:", len(h2s))
