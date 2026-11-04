# -*- coding: utf-8 -*-
"""Stage 2: final_draft.md -> formatted HTML (doc-typeset base template + modern-minimal tokens)."""
import io, json, re, sys

import markdown

BASE = r"C:\Users\Administrator\.workbuddy\plugins\cache\workbuddy-builtin\tencent-docx\5.5.6-wb.38337834.g5f969292.h7826dc9400fd\skills\design-token\tokens\compiled\general.json"
MD_PATH = r"C:\Users\Administrator\WorkBuddy\2026-09-15-22-10-01\output\20260915-222100-informatics-docx\stage1\final_draft.md"
OUT_PATH = r"C:\Users\Administrator\WorkBuddy\2026-09-15-22-10-01\output\20260915-222100-informatics-docx\stage2\formatted-信息学竞赛知识文集.html"
TITLE = "信息学竞赛知识文集"

with io.open(BASE, "r", encoding="utf-8") as f:
    tokens = json.load(f)
css_vars = "\n".join("    %s: %s;" % (k, v) for k, v in tokens["css_variables"].items())

with io.open(MD_PATH, "r", encoding="utf-8") as f:
    md_text = f.read()

# Remove the leading H1 (goes onto the cover) and the meta bullet list after 前言 header stays as-is
lines = md_text.split("\n")
assert lines[0].startswith("# "), "first line must be H1"
lines = lines[1:]
md_body = "\n".join(lines)

html_body = markdown.markdown(
    md_body,
    extensions=["tables", "fenced_code", "toc"],
    extension_configs={"toc": {"toc_depth": "2"}},
)

# Assign section ids to h2 in document order (toc extension may already add ids)
counter = {"n": 0}
def add_id(m):
    counter["n"] += 1
    return '<h2 id="section-%d">%s</h2>' % (counter["n"], m.group(1))
html_body = re.sub(r'<h2(?: id="[^"]*")?>(.*?)</h2>', add_id, html_body, flags=re.S)

# Collect h2 texts for TOC
h2s = re.findall(r'<h2 id="section-\d+">(.*?)</h2>', html_body)
toc_items = "\n".join(
    '      <li><a href="#section-%d">%s</a></li>' % (i + 1, t)
    for i, t in enumerate(h2s)
)

# Blockquote source attribution: leading non-collapsing spaces for border-left rule
html_body = html_body.replace("<blockquote>\n<p>", "<blockquote>\n<p>&nbsp;&nbsp;")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="docx-page-size" content="A4">
  <title>@TITLE@</title>
  <style>
  :root {
@CSS_VARS@
    --page-content-width: var(--layout-maxContentWidth, 15.6cm);
    /* Local aliases */
    --fs-h1: var(--typography-fontSize-title, 24pt);
    --fs-h2: var(--typography-fontSize-h1, 18pt);
    --fs-h3: var(--typography-fontSize-h2, 15pt);
    --fs-h4: var(--typography-fontSize-h3, 13pt);
    --fs-body: var(--typography-fontSize-body, 11pt);
    --fs-small: var(--typography-fontSize-small, 9pt);
    --ff-heading: var(--typography-fontFamily-heading, "微软雅黑", sans-serif);
    --ff-body: var(--typography-fontFamily-body, "微软雅黑", sans-serif);
    --ff-mono: var(--typography-fontFamily-code, Consolas, monospace);
    --lh-body: var(--typography-lineHeight-body, 1.7);
    --lh-heading: var(--typography-lineHeight-heading, 1.3);
    --fw-bold: 600;
    --color-muted: var(--color-textSecondary, #6B7280);
    --color-bg: var(--color-background, #FFFFFF);
    --color-highlight: var(--color-codeBackground, #F9FAFB);
    --spacing-paragraph: var(--spacing-paragraph, 0.5em);
    --spacing-section: var(--spacing-sectionGap, 2em);
    --spacing-block: 1em;
    --margin-page: var(--layout-marginTop, 2.5cm);
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: var(--ff-body);
    font-size: var(--fs-body);
    line-height: var(--lh-body);
    color: var(--color-text);
    background: var(--color-bg);
    max-width: var(--page-content-width);
    margin-left: auto;
    margin-right: auto;
    padding: var(--margin-page) 0;
  }

  h1, h2, h3, h4 {
    font-family: var(--ff-heading);
    line-height: var(--lh-heading);
    font-weight: var(--fw-bold);
    color: var(--color-heading);
    margin-top: var(--spacing-section);
    margin-bottom: var(--spacing-paragraph);
  }
  h1 { font-size: var(--fs-h1); text-align: center; }
  h2 { font-size: var(--fs-h2); }
  h3 { font-size: var(--fs-h3); }
  h4 { font-size: var(--fs-h4); }

  p { margin-bottom: var(--spacing-paragraph); text-align: justify; }

  ul, ol { padding-left: var(--spacing-listIndent, 2em); margin-bottom: var(--spacing-paragraph); }
  li { margin-bottom: var(--spacing-listItemGap, 0.3em); text-align: justify; }

  pre {
    background: var(--color-highlight);
    border: 1px solid var(--color-border);
    padding: var(--spacing-block, 0.8em);
    margin-bottom: var(--spacing-block);
    overflow-x: auto;
  }
  pre, code {
    font-family: var(--ff-mono);
    font-size: var(--fs-small);
  }

  blockquote {
    border-left: 3px solid var(--color-primary);
    background: var(--color-highlight);
    padding: var(--spacing-calloutPad, 0.6em 1em);
    margin-bottom: var(--spacing-block);
  }
  blockquote p { color: var(--color-muted); margin-bottom: 0; }

  table { border-collapse: collapse; width: 100%; margin-bottom: var(--spacing-block); }
  th, td { padding: var(--spacing-cellPad, 0.5em 0.8em); border: 1px solid var(--color-border); text-align: left; }
  th { font-weight: var(--fw-bold); background: var(--color-highlight); }

  hr { border: none; border-top: 1px solid var(--color-border); margin: var(--spacing-section) 0; }

  /* Cover */
  .cover-eyebrow { text-align: center; color: var(--color-primary); font-size: var(--fs-small); font-weight: 700; letter-spacing: 0.3em; margin-top: var(--spacing-coverTop, 4em); }
  section[role="cover"] h1 { text-align: center; margin-top: var(--spacing-section); }
  .cover-subtitle { text-align: center; color: var(--color-muted); font-size: var(--fs-h4); margin-top: var(--spacing-coverGap, 1.5em); }
  .cover-meta { text-align: center; color: var(--color-muted); font-size: var(--fs-small); margin-top: var(--spacing-coverMeta, 6em); }

  /* TOC */
  .doc-toc { margin-bottom: var(--spacing-section); padding: var(--spacing-block); background: var(--color-highlight); }
  .toc-title { font-weight: var(--fw-bold); margin-bottom: var(--spacing-tocGap, 0.5em); font-size: var(--fs-h3); }
  .toc-list, .toc-list ol, .toc-list ul { list-style: none; list-style-type: none; padding-left: var(--spacing-tocIndent, 0.5em); }
  .toc-list li { margin-bottom: var(--spacing-listItemGap, 0.3em); }
  .toc-list a { color: var(--color-text); text-decoration: none; }

  @page { @bottom-center { content: counter(page); } }
  @page cover { @bottom-center { content: none; } }
  section[role="cover"] { page: cover; }
  </style>
</head>
<body>
  <section role="cover">
    <p class="cover-eyebrow">INFORMATICS&nbsp;OLYMPIAD&nbsp;COLLECTION</p>
    <h1>@TITLE@</h1>
    <p class="cover-subtitle">位运算 · 图论 · 表达式 · 排列组合 · 树链剖分 · CSP 知识点与大纲</p>
    <p class="cover-meta">汇编自博客园八篇信息学竞赛技术文章<br>2026 年 9 月</p>
  </section>
  <section role="body" data-page-restart="1">
    <nav class="doc-toc" aria-label="文档目录">
      <p class="toc-title">目录</p>
      <ol class="toc-list">
@TOC_ITEMS@
      </ol>
    </nav>
@BODY@
  </section>
</body>
</html>
"""

HTML = HTML_TEMPLATE.replace("@CSS_VARS@", css_vars).replace("@TITLE@", TITLE).replace("@TOC_ITEMS@", toc_items).replace("@BODY@", html_body)

with io.open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(HTML)

print("written:", OUT_PATH)
print("h2 sections:", len(h2s))
