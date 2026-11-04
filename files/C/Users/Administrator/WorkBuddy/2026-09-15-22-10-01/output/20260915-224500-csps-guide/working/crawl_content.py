# -*- coding: utf-8 -*-
"""Crawl all 60 csp.wiki CSP-S sub-pages, convert <article> HTML to Markdown."""
import io, json, os, re, sys, time
import urllib.request
from bs4 import BeautifulSoup, NavigableString, Tag

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from latex_clean import latex_to_text

BASE = "https://csp.wiki/docs/CSP-S/"
MAIN_URL = "https://csp.wiki/docs/CSP-S"
SECTIONS = [
    ("0-MathBasics", 10),
    ("1-Search", 5),
    ("2-DP", 9),
    ("3-DS", 12),
    ("4-Graph", 15),
    ("5-String", 5),
    ("6-Extra", 4),
]
NUMS = {
    "0-MathBasics": ["01","02","03","04","05","06","07","08","09","10"],
    "1-Search": ["01","02","03","04","05"],
    "2-DP": ["01","02","03","04","05","06","07","08","99"],
    "3-DS": ["01","02","03","04","05","06","07","08","09","10","11","12"],
    "4-Graph": ["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15"],
    "5-String": ["01","02","03","04","05"],
    "6-Extra": ["01","02","03","04"],
}

def fetch(url, tries=2):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            return urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(1.0)

def inline_text(node):
    """Convert inline content to markdown text."""
    if isinstance(node, NavigableString):
        return str(node)
    if not isinstance(node, Tag):
        return ""
    if node.name in ("strong", "b"):
        t = "".join(inline_text(c) for c in node.children).strip()
        return "**%s**" % t if t else ""
    if node.name in ("em", "i"):
        t = "".join(inline_text(c) for c in node.children).strip()
        return "*%s*" % t if t else ""
    if node.name == "code":
        t = node.get_text()
        return "`%s`" % t.strip() if t.strip() else ""
    if node.name == "img":
        alt = node.get("alt", "") or ""
        src = node.get("src", "") or ""
        if src.startswith("/"):
            src = "https://csp.wiki" + src
        return "![%s](%s)" % (alt, src) if src else alt
    if node.name == "br":
        return " "
    if node.name == "a":
        return "".join(inline_text(c) for c in node.children)
    if node.name in ("span", "sup", "sub", "kbd", "mark"):
        # KaTeX / annotations: keep visible text
        return "".join(inline_text(c) for c in node.children)
    return "".join(inline_text(c) for c in node.children)

def render_table(tb):
    rows = []
    for tr in tb.find_all("tr"):
        cells = [inline_text(td).strip().replace("\n", " ") for td in tr.find_all(["td", "th"])]
        rows.append(cells)
    if not rows:
        return ""
    ncol = max(len(r) for r in rows)
    for r in rows:
        while len(r) < ncol:
            r.append("")
    out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * ncol]
    for r in rows[1:]:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)

def render_code(pre):
    # language from ancestor div class
    lang = ""
    parent = pre.parent
    while parent is not None and getattr(parent, "get", None):
        cls = " ".join(parent.get("class") or [])
        m = re.search(r"language-([\w+-]+)", cls)
        if m:
            lang = m.group(1)
            break
        parent = parent.parent
    text = pre.get_text()
    text = text.replace("\t", "    ")
    lines = [ln.rstrip() for ln in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    while lines and lines[0] == "":
        lines.pop(0)
    return "```%s\n%s\n```" % (lang, "\n".join(lines))

def emit(out, text):
    """Append text; multi-line (converted formulas) become separate blocks."""
    text = text.strip()
    if not text:
        return
    if "\n" in text:
        for ln in text.split("\n"):
            ln = ln.strip()
            if ln:
                out.append(ln)
    else:
        out.append(text)


def render_block(node, out):
    if isinstance(node, NavigableString):
        t = str(node).strip()
        if t:
            out.append(t)
        return
    if not isinstance(node, Tag):
        return
    name = node.name
    cls = " ".join(node.get("class") or [])
    if name in ("h1",):
        return  # page title handled separately
    if name == "h2":
        out.append("### " + inline_text(node).strip())
        return
    if name in ("h3", "h4", "h5", "h6"):
        # deeper source headings -> bold lead line (avoid h4-to-h4 adjacency)
        t = inline_text(node).strip()
        if t:
            out.append("**%s**" % t)
        return
    if name == "p":
        emit(out, inline_text(node))
        return
    if name == "img":
        alt = node.get("alt", "") or ""
        src = node.get("src", "") or ""
        if src.startswith("/"):
            src = "https://csp.wiki" + src
        if src:
            out.append("![%s](%s)" % (alt, src))
        return
    if name == "pre":
        out.append(render_code(node))
        return
    if name == "table":
        t = render_table(node)
        if t:
            out.append(t)
        return
    if name in ("ul", "ol"):
        idx = 1
        for li in node.find_all("li", recursive=False):
            marker = "- " if name == "ul" else "%d. " % idx
            idx += 1
            # split nested lists out of the li text
            nested = []
            for sub in li.find_all(["ul", "ol"], recursive=False):
                nested.append(sub)
                sub.extract()
            text = inline_text(li).strip()
            if text:
                out.append("  " + marker + text) if False else out.append(marker + text)
            for sub in nested:
                idx2 = 1
                for li2 in sub.find_all("li", recursive=False):
                    m2 = "- " if sub.name == "ul" else "%d. " % idx2
                    idx2 += 1
                    t2 = inline_text(li2).strip()
                    if t2:
                        out.append("  " + m2 + t2)
        return
    if name == "blockquote":
        inner = []
        for c in node.children:
            render_block(c, inner)
        for ln in "\n".join(inner).split("\n"):
            out.append("> " + ln)
        return
    if name == "hr":
        out.append("---")
        return
    if name in ("nav", "footer", "button", "style", "script", "form"):
        return
    if "vp-doc" in cls and name == "div":
        pass
    # generic container: recurse
    for c in node.children:
        render_block(c, out)

def page_to_md(path):
    return html_to_md(fetch(BASE + path))


def html_to_md(html):
    soup = BeautifulSoup(html, "html.parser")
    art = soup.find("article")
    if art is None:
        raise RuntimeError("no article")
    # page h1 as title
    h1 = art.find("h1")
    title = h1.get_text(strip=True) if h1 else path
    # drop edit/footer links & buttons & prev/next nav & breadcrumbs
    for el in art.find_all(class_=re.compile("edit-link|footer|meta|breadcrumb|pagination|prev-next")):
        el.decompose()
    for a in art.find_all("a"):
        t = a.get_text(strip=True)
        if t in ("Previous Page", "Next Page"):
            a.decompose()
    # KaTeX: replace rendered duplication with original LaTeX annotation
    for kat in art.find_all(class_="katex"):
        ann = kat.find("annotation", attrs={"encoding": "application/x-tex"})
        if ann is not None:
            # convert LaTeX source to readable text so DOCX shows no raw markup
            kat.replace_with(" %s " % latex_to_text(ann.get_text()))
        else:
            kat.decompose()
    out = []
    for c in art.children:
        render_block(c, out)
    body = "\n\n".join(x for x in out if x.strip())
    # cleanup junk lines: page-number headers like "3 DS", duplicated title, empty artifacts
    lines = [ln.strip() for ln in body.split("\n")]
    while lines and (re.match(r"^\d+\s+[A-Za-z]{1,12}$", lines[0]) or lines[0] == title or lines[0] == ""):
        lines.pop(0)
    while lines and lines[-1] in ("Previous Page", "Next Page", ""):
        lines.pop()
    lines = [ln for ln in lines if ln not in ("Previous Page", "Next Page")]
    return title, "\n".join(lines)

def main():
    all_md = {}
    errors = {}
    # main guide page (same source pipeline, full original text)
    try:
        title, body = html_to_md(fetch(MAIN_URL))
        all_md["__main__"] = {"title": title, "body": body}
        print("OK __main__", len(body))
    except Exception as e:
        errors["__main__"] = str(e)
        print("ERR __main__", e)
    for sec, n in SECTIONS:
        for num in NUMS[sec]:
            path = "%s/%s" % (sec, num)
            try:
                title, body = page_to_md(path)
                all_md[path] = {"title": title, "body": body}
                print("OK", path, len(body))
            except Exception as e:
                errors[path] = str(e)
                print("ERR", path, e)
            time.sleep(0.15)
    json.dump({"pages": all_md, "errors": errors},
              io.open(r"C:\Users\Administrator\WorkBuddy\2026-09-15-22-10-01\output\20260915-224500-csps-guide\working\csp_content.json", "w", encoding="utf-8"),
              ensure_ascii=False)
    print("total ok:", len(all_md), "errors:", len(errors))

if __name__ == "__main__":
    main()
