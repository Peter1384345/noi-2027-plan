# -*- coding: utf-8 -*-
"""提取 PDF 真题 -> 结构化题目；补充初赛资料文章"""
import re, json, os
from pypdf import PdfReader

OUT = r"C:\Users\Administrator\WorkBuddy\2026-11-03-19-18-52\noi-2027\assets\data"
PAPERS = r"C:\Users\Administrator\WorkBuddy\2026-09-14-21-45-48\csp-s-site\papers"
os.makedirs(os.path.join(OUT, "kb"), exist_ok=True)

def clean(t):
    return "".join(ch for ch in t if not (0xD800 <= ord(ch) <= 0xDFFF))

def dump(name, var, obj):
    init = "window.KB=window.KB||{};" if var.startswith("KB[") else ""
    with open(os.path.join(OUT, "kb", name), "w", encoding="utf-8") as f:
        f.write(init + "window.%s=%s;\n" % (var, json.dumps(obj, ensure_ascii=False)))

FOOT = re.compile(r"第\s*\d+\s*页[，,]?\s*共\s*\d+\s*页|CCF CSP-S \d{4} 第一轮 C\+\+语言试题|"
                  r"\d{4} CCF 非专业级别软件能力认证第一轮|（CSP-S1）提高级 C\+\+语言试题|"
                  r"认证时间：\d{4} 年 \d+ 月 \d+ 日 [\d:~]+")

def read_pdf(path):
    r = PdfReader(path)
    txt = "\n".join((p.extract_text() or "") for p in r.pages)
    txt = clean(txt)
    txt = FOOT.sub("", txt)
    txt = re.sub(r"[ \t]+\n", "\n", txt)
    txt = re.sub(r"\n{2,}", "\n", txt)
    return txt

def split_sections(txt):
    marks = [("单选", r"一、\s*单项选择题"), ("阅读", r"二、\s*阅读程序"), ("完善", r"三、\s*完善程序")]
    pos = sorted((m.start(), name) for name, pat in marks for m in [re.search(pat, txt)] if m)
    secs = {}
    for i, (s, name) in enumerate(pos):
        e = pos[i + 1][0] if i + 1 < len(pos) else len(txt)
        secs[name] = txt[s:e]
    return secs

def parse_questions(sec):
    parts = re.split(r"(?m)(?:(?<=\n)|^)\s*(\d{1,2})\s*[.．、]\s*", sec)
    out, seen = [], set()
    for i in range(1, len(parts) - 1, 2):
        try:
            no = int(parts[i])
        except ValueError:
            continue
        body = parts[i + 1].strip()
        if len(body) < 8 or no in seen:
            continue
        seen.add(no)
        marks = list(re.finditer(r"(?<![A-Za-z])([A-D])\s*[.．、]\s*", body))
        opts = []
        if len(marks) >= 2:
            stem = body[:marks[0].start()].strip()
            for j, m in enumerate(marks):
                e = marks[j + 1].start() if j + 1 < len(marks) else len(body)
                v = body[m.end():e].strip()
                if len(v) > 200:      # 选项里塞了整段代码 -> 视为无结构，退回整题
                    opts = []
                    stem = body
                    break
                opts.append({"k": m.group(1), "v": v})
        else:
            stem = body
        out.append({"no": no, "stem": stem, "opts": opts})
    return out

def build(year, qfile, afile=None):
    txt = read_pdf(qfile)
    secs = split_sections(txt)
    res = {"year": year, "sections": [], "answers": {}}
    for key, label in [("单选", "一、单项选择题"), ("阅读", "二、阅读程序"), ("完善", "三、完善程序")]:
        if key in secs:
            qs = parse_questions(secs[key])
            if qs:
                res["sections"].append({"key": key, "label": label, "qs": qs})
    if afile and os.path.exists(afile):
        letters = re.findall(r"(?<![A-Za-z])([A-D])(?![A-Za-z])", read_pdf(afile))
        if len(letters) >= 15:
            res["answers"] = {str(i + 1): letters[i] for i in range(15)}
            res["answerNote"] = "单选答案由官方答案 PDF 自动提取；阅读程序与完善程序请核对原卷。"
    return res

def build_guide():
    arts = []
    p1 = os.path.join(PAPERS, "CSP-S1_初赛备考指南与答题技巧.pdf")
    if os.path.exists(p1):
        blocks = [{"k": "p", "x": x.strip()} for x in read_pdf(p1).split("\n") if x.strip()]
        arts.append({"id": "prelim-guide", "title": "初赛备考指南与答题技巧", "blocks": blocks})
    p2 = os.path.join(PAPERS, "CSP第一轮复习资料_45页.pdf")
    if os.path.exists(p2):
        blocks = []
        for x in read_pdf(p2).split("\n"):
            x = x.strip()
            if not x or re.match(r"^第\s*\d+\s*页\s*共\s*\d+\s*页$", x):
                continue
            if len(x) < 30 and not re.search(r"[。，；:：]$", x) and not re.search(r"\d", x):
                blocks.append({"k": "h4", "x": x})
            else:
                blocks.append({"k": "p", "x": x})
        arts.append({"id": "prelim-45", "title": "CSP 第一轮复习资料（45 页）", "blocks": blocks})
    return arts

if __name__ == "__main__":
    papers = []
    for y in ("2022", "2023"):
        p = build(y, os.path.join(PAPERS, "CSP-S_%s_第一轮试题.pdf" % y),
                  os.path.join(PAPERS, "CSP-S_%s_第一轮答案.pdf" % y))
        papers.append(p)
        print(y, "题数", sum(len(s["qs"]) for s in p["sections"]), "答案", len(p["answers"]))

    guide = build_guide()
    dump("papers.js", "PAPERS", papers)
    dump("guide2.js", "KB['初赛资料']", guide)
    print("初赛资料文章", len(guide), "| 字节", sum(b["x"].__len__() for a in guide for b in a["blocks"]))

    q = papers[1]["sections"][0]["qs"][0]
    print("\n样例题干:", q["stem"][:110])
    for o in q["opts"][:2]:
        print("  ", o["k"], o["v"][:60])
    print("分布:", {s["key"]: len(s["qs"]) for s in papers[1]["sections"]})
