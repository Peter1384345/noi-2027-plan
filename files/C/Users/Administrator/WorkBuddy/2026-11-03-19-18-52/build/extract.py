# -*- coding: utf-8 -*-
"""从本地 docx / pdf 提取结构化内容 -> 站点 assets/data/"""
import zipfile, re, html, json, os

OUT = r"C:\Users\Administrator\WorkBuddy\2026-11-03-19-18-52\noi-2027\assets\data"
PAPERS = r"C:\Users\Administrator\WorkBuddy\2026-09-14-21-45-48\csp-s-site\papers"
os.makedirs(os.path.join(OUT, "kb"), exist_ok=True)

def clean(t):
    """移除 PDF 提取产生的孤立代理字符，避免 UTF-8 编码失败"""
    return "".join(ch for ch in t if not (0xD800 <= ord(ch) <= 0xDFFF))

def dump(name, var, obj):
    p = os.path.join(OUT, "kb", name)
    init = "window.KB=window.KB||{};" if var.startswith("KB[") else ""
    with open(p, "w", encoding="utf-8") as f:
        f.write(init + "window.%s=%s;\n" % (var, json.dumps(obj, ensure_ascii=False)))
    return p

# ============================ docx ============================
def ptext(p):
    p = re.sub(r"<w:br\s*/?>", "\n", p)
    p = re.sub(r"<w:tab/>", "\t", p)
    return html.unescape(re.sub("<[^>]+>", "", p))

def paras_of(path):
    z = zipfile.ZipFile(path)
    x = z.read("word/document.xml").decode("utf8")
    res = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", x, re.S):
        st = re.search(r'<w:pStyle w:val="([^"]+)"', p)
        style = st.group(1) if st else ""
        t = ptext(p).strip()
        if t:
            res.append((style, t))
    return res

CODE_HINT = re.compile(r"(#include|\bint\s+main\b|\bfor\s*\(|\bwhile\s*\(|\bif\s*\(|\breturn\b|"
                       r"\bcout\b|\bprintf\b|\bstruct\b|\bvoid\b|\busing namespace\b|\bscanf\b)")
CH_PUNCT = re.compile(r"[，。；：？！、（）“”《》]")

def is_code(t):
    if "\n" in t and CODE_HINT.search(t):
        return True
    if CODE_HINT.search(t) and (t.count("{") + t.count(";")) >= 2:
        return True
    return False

def is_subhead(t):
    if len(t) > 46 or "\n" in t:
        return False
    if CH_PUNCT.search(t) or t.endswith(("。", "，", "：", ".", ",", ":", "；")):
        return False
    return not is_code(t)

def to_blocks(items):
    blocks = []
    for i, (style, t) in enumerate(items):
        if style in ("Heading1", "Heading2", "Heading3"):
            blocks.append({"k": "h", "x": t})
        elif style in ("ListBullet", "ListNumber"):
            blocks.append({"k": "li", "x": t})
        elif is_code(t):
            blocks.append({"k": "code", "x": t})
        elif is_subhead(t) and (i + 1 >= len(items) or len(items[i + 1][1]) > len(t)):
            blocks.append({"k": "h4", "x": t})
        else:
            blocks.append({"k": "p", "x": t})
    return blocks

# ============================ 1. CSP-S 知识库 ============================
CAT_KEY = {"数学基础": "math", "搜索": "search", "动态规划": "dp", "数据结构": "ds",
           "图论": "graph", "字符串": "str", "指南": "guide", "杂项": "misc"}

def cat_of(title):
    for k in ("数学基础", "搜索", "动态规划", "数据结构", "图论", "字符串"):
        if title.startswith(k):
            return k
    return "指南" if title.startswith("CSP-S 指南") else "杂项"

def build_kb():
    items = paras_of(r"C:\Users\Administrator\Desktop\CSP-S知识库全集.docx")
    start = next(i for i, (s, _) in enumerate(items) if s == "Heading2")
    arts, cur = [], None
    for style, t in items[start:]:
        if style == "Heading2":
            if cur:
                arts.append(cur)
            cur = {"title": t, "items": []}
        elif cur is not None:
            cur["items"].append((style, t))
    if cur:
        arts.append(cur)

    catalog, groups = [], {}
    TOC = re.compile(r"^.{1,8}\s\d{2}\s*·\s*\S")
    CATNAME = {"CSP-S 指南", "数学基础", "搜索", "动态规划", "数据结构", "图论", "字符串", "杂项"}
    for idx, a in enumerate(arts):
        c = cat_of(a["title"])
        aid = "%s-%02d" % (CAT_KEY[c], idx)
        blocks = [b for b in to_blocks(a["items"]) if not (b["k"] == "h" and b["x"] == a["title"])]
        if c == "指南":
            blocks = [b for b in blocks
                      if not TOC.match(b["x"]) and b["x"].strip() not in CATNAME]
        text = "".join(b["x"] for b in blocks)
        groups.setdefault(c, []).append({"id": aid, "title": a["title"], "cat": c,
                                         "blocks": blocks, "chars": len(text)})
        catalog.append({"id": aid, "title": a["title"], "cat": c, "chars": len(text)})

    for c, lst in groups.items():
        dump(CAT_KEY[c] + ".js", "KB['%s']" % c, lst)
    dump("catalog.js", "KB_CATALOG", catalog)
    return catalog

# ============================ 2. 知识文集（去重）============================
def build_essays():
    items = paras_of(r"C:\Users\Administrator\Desktop\信息学竞赛知识文集.docx")
    arts, cur, seen = [], None, set()
    for style, t in items:
        m = re.match(r"^第[一二三四五六七八九十]+章\s", t)
        if m and len(t) < 40 and t not in seen:
            seen.add(t)
            if cur:
                arts.append(cur)
            cur = {"title": t, "items": []}
        elif cur is not None:
            cur["items"].append((style, t))
    if cur:
        arts.append(cur)

    out = [{"id": "essay-%02d" % i, "title": a["title"], "blocks": to_blocks(a["items"])}
           for i, a in enumerate(arts)]
    dump("essays.js", "KB['文集']", out)
    return out

# ============================ 3. 初赛知识 ============================
def build_prelim():
    items = paras_of(r"D:\桌面\总文件夹\资料整合\复习资料信息学.docx")
    blocks = to_blocks(items)
    dump("prelim.js", "KB['初赛']",
         [{"id": "prelim-00", "title": "初赛知识清单（计算机史 · 进制 · 存储 · 概念）", "blocks": blocks}])
    return blocks

# ============================ 4. CSP-S 2025 真题 ============================
def build_2025():
    items = paras_of(r"D:\桌面\总文件夹\资料整合\CSPS 2025题目.docx")
    blocks = to_blocks(items)
    dump("paper2025.js", "KB['真题2025']",
         [{"id": "p2025", "title": "CSP-S 2025 第一轮（社区整理版）", "blocks": blocks}])
    return blocks

if __name__ == "__main__":
    cat = build_kb()
    es = build_essays()
    pr = build_prelim()
    p25 = build_2025()
    tot = sum(c["chars"] for c in cat)
    print("知识库文章 %d 篇 · 正文 %d 字（约 %.1f 万）" % (len(cat), tot, tot / 10000))
    print("文集 %d 章" % len(es))
    print("初赛块 %d · 2025 真题块 %d" % (len(pr), len(p25)))
