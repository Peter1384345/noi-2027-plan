# -*- coding: utf-8 -*-
"""将 Atlas 可视化增强片段插入 dragon-raja-story 仓库文件。"""
import io, os, sys

BASE  = r"C:\Users\Administrator\WorkBuddy\2026-08-29-00-02-29"
PATCH = os.path.join(BASE, "patch")
REPO  = os.path.join(BASE, "dragon-raja-story")


def rd(p):
    with io.open(p, encoding="utf-8", newline="") as f:
        return f.read()


def wr(p, s):
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def fit(s, nl):
    """统一片段的换行符，与宿主文件保持一致。"""
    s = s.replace("\r\n", "\n")
    return s.replace("\n", "\r\n") if nl == "\r\n" else s


def insert_before(text, anchor, snippet, label):
    cnt = text.count(anchor)
    if cnt != 1:
        raise SystemExit("[FAIL] anchor x%d -> %s" % (cnt, label))
    return text.replace(anchor, snippet + anchor, 1)


def insert_after(text, anchor, snippet, label):
    cnt = text.count(anchor)
    if cnt != 1:
        raise SystemExit("[FAIL] anchor x%d -> %s" % (cnt, label))
    return text.replace(anchor, anchor + snippet, 1)


def main():
    # ---------- index.html ----------
    html_path = os.path.join(REPO, "index.html")
    html = rd(html_path)
    nl = "\r\n" if html.count("\r\n") > html.count("\n") - html.count("\r\n") else "\n"
    print("index.html newline = %s" % repr(nl))

    css     = fit(rd(os.path.join(PATCH, "atlas_css.html")),    nl)
    sec_pow = fit(rd(os.path.join(PATCH, "sec_power.html")),    nl)
    sec_pul = fit(rd(os.path.join(PATCH, "sec_pulse.html")),    nl)
    sec_tr  = fit(rd(os.path.join(PATCH, "sec_tree.html")),     nl)
    sec_des = fit(rd(os.path.join(PATCH, "sec_destiny.html")),  nl)

    html = insert_before(html, "  </style>", css, "style")

    # 导航项：插入到语义相邻的位置
    html = insert_before(
        html,
        '<a class="nav-btn" href="#sec-plot">分卷剧情</a>',
        '      <a class="nav-btn" href="#sec-power">战力对比</a>' + nl,
        "nav:power")
    html = insert_before(
        html,
        '<a class="nav-btn" href="#sec-battles">经典战役</a>',
        '      <a class="nav-btn" href="#sec-pulse">卷次强度</a>' + nl,
        "nav:pulse")
    html = insert_before(
        html,
        '<a class="nav-btn" href="#sec-families">家族谱系</a>',
        '      <a class="nav-btn" href="#sec-dragon-tree">龙王谱系</a>' + nl,
        "nav:tree")
    html = insert_after(
        html,
        '<a class="nav-btn" href="#sec-fates">角色命运</a>',
        nl + '      <a class="nav-btn" href="#sec-destiny">命运流向</a>',
        "nav:destiny")

    # 板块：插入到语义相邻的 section 前
    html = insert_before(html, '    <section id="sec-plot">',     sec_pow, "sec:power")
    html = insert_before(html, '    <section id="sec-battles">',  sec_pul, "sec:pulse")
    html = insert_before(html, '    <section id="sec-families">', sec_tr,  "sec:tree")
    html = insert_before(html, '  </article>',                    sec_des, "sec:destiny")

    wr(html_path, html)
    print("[OK] index.html -> %d bytes" % len(html.encode("utf-8")))

    # ---------- assets/charts.js ----------
    js_path = os.path.join(REPO, "assets", "charts.js")
    js = rd(js_path)
    js_nl = "\r\n" if js.count("\r\n") > js.count("\n") - js.count("\r\n") else "\n"
    print("charts.js newline = %s" % repr(js_nl))
    charts = fit(rd(os.path.join(PATCH, "atlas_charts.js")), js_nl)

    tail = "})();"
    idx = js.rfind(tail)
    if idx < 0:
        raise SystemExit("[FAIL] charts.js IIFE tail not found")
    js = js[:idx] + charts + js[idx:]
    wr(js_path, js)
    print("[OK] charts.js  -> %d bytes" % len(js.encode("utf-8")))

    print("DONE")


if __name__ == "__main__":
    main()
