# -*- coding: utf-8 -*-
"""Assemble final markdown: main guide + full text of all 60 sub-pages."""
import io, json, os, re, sys

WORK = r"C:\Users\Administrator\WorkBuddy\2026-09-15-22-10-01\output\20260915-224500-csps-guide\working"
sys.path.insert(0, WORK)
from latex_clean import latex_to_text
OUT = r"C:\Users\Administrator\WorkBuddy\2026-09-15-22-10-01\output\20260915-224500-csps-guide\stage1\final_full.md"

data = json.load(io.open(WORK + r"\csp_content.json", encoding="utf-8"))
pages = data["pages"]

SECTION_LABEL = {
    "0-MathBasics": "数学基础",
    "1-Search": "搜索",
    "2-DP": "动态规划",
    "3-DS": "数据结构",
    "4-Graph": "图论",
    "5-String": "字符串",
    "6-Extra": "杂项",
}
SECTIONS = ["0-MathBasics", "1-Search", "2-DP", "3-DS", "4-Graph", "5-String", "6-Extra"]

def clean(body):
    # normalize: remove stray zero-width chars, collapse >2 blank lines
    body = body.replace("\u200b", "")
    body = re.sub(r"\n{3,}", "\n\n", body)
    body = body.strip()
    # split over-long paragraphs (>500 chars) at sentence boundaries
    out_lines = []
    in_code = False
    for ln in body.split("\n"):
        if ln.lstrip().startswith("```"):
            in_code = not in_code
            out_lines.append(ln)
            continue
        if not in_code and "\\" in ln:
            # leftover raw LaTeX outside KaTeX nodes -> readable text
            ln = latex_to_text(ln)
        if in_code:
            out_lines.append(ln)
            continue
        if len(ln) <= 500 or ln.startswith(("#", "|", "```", "- ", "> ", "  ")):
            out_lines.append(ln)
            continue
        # first split at sentence ends, then at commas as fallback
        pieces = re.split(r"(?<=[。！？；!?;])", ln)
        refined = []
        for p in pieces:
            if len(p) <= 450:
                refined.append(p)
                continue
            sub = re.split(r"(?<=[，,、])", p)
            buf = ""
            for q in sub:
                if buf and len(buf) + len(q) > 400:
                    refined.append(buf)
                    buf = q
                else:
                    buf += q
            if buf:
                refined.append(buf)
        # merge short pieces up, then emit each segment as its own
        # markdown paragraph (blank line between) so they stay separate
        buf = ""
        segs = []
        for p in refined:
            if buf and len(buf) + len(p) > 450:
                segs.append(buf)
                buf = p
            else:
                buf += p
        if buf:
            segs.append(buf)
        for s in segs:
            out_lines.append(s)
            out_lines.append("")
    return "\n".join(out_lines)

parts = []
parts.append("# CSP-S 指南与知识库全集")

# main guide page, full original text
main = pages.get("__main__")
if main:
    parts.append("## %s" % (main["title"] or "CSP-S 指南"))
    parts.append(clean(main["body"]))

sec_no = 1
for key in SECTIONS:
    nums = {
        "0-MathBasics": ["01","02","03","04","05","06","07","08","09","10"],
        "1-Search": ["01","02","03","04","05"],
        "2-DP": ["01","02","03","04","05","06","07","08","99"],
        "3-DS": ["01","02","03","04","05","06","07","08","09","10","11","12"],
        "4-Graph": ["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15"],
        "5-String": ["01","02","03","04","05"],
        "6-Extra": ["01","02","03","04"],
    }[key]
    for i, num in enumerate(nums, 1):
        path = "%s/%s" % (key, num)
        pg = pages[path]
        title = pg["title"] or path
        body = clean(pg["body"])
        if not body:
            continue
        parts.append("## %s %s · %s" % (SECTION_LABEL[key], num, title))
        parts.append(body)
    sec_no += 1

md = "\n\n".join(parts) + "\n"

def split_list_item(ln):
    """Split an over-long list item into several items at sentence ends."""
    m = re.match(r"^(\s*(?:[-*]|\d+\.)\s+)", ln)
    indent = m.group(1)
    text = ln[len(indent):]
    pieces = re.split(r"(?<=[。！？；!?;])", text)
    segs, buf = [], ""
    for p in pieces:
        if buf and len(buf) + len(p) > 420:
            segs.append(buf)
            buf = p
        else:
            buf += p
    if buf:
        segs.append(buf)
    return [indent + s for s in segs]

SKIP = re.compile(r"^\s*(#|\||[-*]\s|\d+\.\s|>|```)")
PLAIN = re.compile(r"^\s*(#|\||[-*]|\d+\.|>|```|\s)")

def normalize(text):
    """Global pass: break over-long paragraphs (list items and
    multi-line LaTeX blocks merged by the converter)."""
    lines = text.split("\n")
    out, i, in_fence = [], 0, False
    while i < len(lines):
        ln = lines[i]
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(ln)
            i += 1
            continue
        if in_fence:
            out.append(ln)
            i += 1
            continue
        if re.match(r"^\s*[-*]\s+", ln) and len(ln) > 500:
            out.extend(split_list_item(ln))
            i += 1
            continue
        # group of consecutive plain lines forming one paragraph
        if ln.strip() and not SKIP.match(ln):
            group = [ln]
            j = i + 1
            while j < len(lines) and lines[j].strip() and not SKIP.match(lines[j]):
                group.append(lines[j])
                j += 1
            if sum(len(g) for g in group) > 500 and len(group) > 1:
                for g in group:
                    out.append(g)
                    out.append("")
                i = j
                continue
        out.append(ln)
        i += 1
    return "\n".join(out)

md = normalize(md)
io.open(OUT, "w", encoding="utf-8").write(md)
print("written:", OUT)
print("chars:", len(md))
