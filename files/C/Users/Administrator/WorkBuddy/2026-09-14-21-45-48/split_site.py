# -*- coding: utf-8 -*-
"""Split csp-s-site/index.html into per-section pages with fade transitions."""
import os
import re
import shutil

ROOT = r"C:/Users/Administrator/WorkBuddy/2026-09-14-21-45-48/csp-s-site"
SRC = os.path.join(ROOT, "index.html")
BACKUP = os.path.join(ROOT, "single.html")
if os.path.exists(BACKUP):
    SRC = BACKUP                      # rebuild from the pristine single-page backup
    data = open(SRC, encoding="utf-8").read()
else:
    data = open(SRC, encoding="utf-8").read()
    shutil.copyfile(SRC, BACKUP)      # backup single-page version

# ---- boundaries ----
HDR_START = data.index('<header class="topbar"')
MAIN_START = data.index('<main id="top"')
FOOTER_START = data.index('<footer')
SCRIPT1 = data.index("<script>", FOOTER_START)
SCRIPT1_END = data.index("</script>", SCRIPT1) + len("</script>")
SCRIPT2 = data.index("<script>", SCRIPT1_END)
SCRIPT2_END = data.index("</script>", SCRIPT2) + len("</script>")

head_html = data[:HDR_START]                       # doctype/head/body open
header_html = data[HDR_START:MAIN_START]           # topbar
footer_html = data[FOOTER_START:SCRIPT1]           # "<footer>...</footer>" only
script1 = data[SCRIPT1:SCRIPT1_END]
script2 = data[SCRIPT2:SCRIPT2_END]

tail_after_main = footer_html.strip()

# ---- sections (contiguous inside <main>...</main>) ----
main_inner = data[MAIN_START + len("<main id=\"top\"") + 1:FOOTER_START]
sec_starts = [m.start() for m in re.finditer(r"<section\b", main_inner)]
sec_starts.append(len(main_inner))
sections = []  # (id or None, html)
for i in range(len(sec_starts) - 1):
    chunk = main_inner[sec_starts[i]:sec_starts[i + 1]]
    m = re.match(r'<section\b[^>]*?id="([a-z]+)"', chunk)
    sid = m.group(1) if m else "hero"
    sections.append((sid, chunk.rstrip()))

SEC = dict(sections)

# ---- page definitions ----
NAV_PAGES = [
    ("papers",   "papers.html",   "真题 PDF"),
    ("quiz",     "quiz.html",     "在线刷题"),
    ("freq",     "freq.html",     "考点频次"),
    ("choice",   "choice.html",   "重点清单"),
    ("read",     "read.html",     "阅读程序"),
    ("complete", "complete.html", "完善程序"),
    ("route",    "route.html",    "学习路线"),
    ("method",   "method.html",   "方法论"),
    ("plan",     "plan.html",     "冲刺计划"),
    ("battle",   "battle.html",   "考场守则"),
    ("rounds",   "rounds.html",   "两轮对比"),
    ("sites",    "sites.html",    "资源导航"),
]
ORDER = ["hero"] + [p[0] for p in NAV_PAGES]
# year section appended to freq page
PAGE_SECTIONS = {"hero": ["hero"], "freq": ["freq", "year"]}
for sid, _, _ in NAV_PAGES:
    PAGE_SECTIONS.setdefault(sid, [sid])
PAGE_FILE = {"hero": "index.html"}
PAGE_LABEL = {"hero": "首页"}
for sid, f, label in NAV_PAGES:
    PAGE_FILE[sid] = f
    PAGE_LABEL[sid] = label
PAGE_TITLES = {"hero": "CSP-S 初赛备考全攻略 · CSPSpass"}
for sid in ORDER[1:]:
    PAGE_TITLES[sid] = "CSP-S 备考 · " + PAGE_LABEL[sid] + " · CSPSpass"

# ---- anchor -> page rewrite map ----
LINK_MAP = {"top": "index.html", "hero": "index.html"}
for sid, f, _ in NAV_PAGES:
    LINK_MAP[sid] = f

TRANSITION_CSS = """<style>
/* ============ 页面过渡动画 ============ */
@keyframes pageIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
body.page-enter { animation: pageIn .3s ease both; }
html.page-exit body { opacity: 0; transform: translateY(-8px); transition: opacity .18s ease, transform .18s ease; }
@media (prefers-reduced-motion: reduce) {
  body.page-enter { animation: none; }
  html.page-exit body { transition: none; opacity: 1; transform: none; }
}
</style>
"""

TRANSITION_JS = """<script>
/* ============ 页面跳转过渡：淡出 -> 跳转，新页面淡入 ============ */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    document.body.classList.add('page-enter');
  });
  document.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a || a.target === '_blank') return;
    var href = a.getAttribute('href');
    if (!href || /^(https?:|mailto:|#|data:)/i.test(href) || /[.]pdf$/i.test(href)) return;
    e.preventDefault();
    document.documentElement.classList.add('page-exit');
    setTimeout(function () { window.location.href = href; }, 180);
  });
  window.addEventListener('pageshow', function (e) {
    if (e.persisted) {
      document.documentElement.classList.remove('page-exit');
      document.body.classList.add('page-enter');
    }
  });
})();
</script>
"""

def rewrite_links(html, own_page_file):
    def repl(m):
        anchor = m.group(1)
        if anchor in LINK_MAP:
            return 'href="' + LINK_MAP[anchor] + '"'
        return m.group(0)
    html = re.sub(r'href="#([a-zA-Z-]+)"', repl, html)
    # mark current page in nav (handle links with or without a class attribute)
    for sid, f, _ in NAV_PAGES:
        def nav_repl(m, own=(f == own_page_file)):
            tag = m.group(0)
            if own:
                if 'class="' in tag:
                    return re.sub(r'class="[^"]*"', 'class="on"', tag)
                return tag.replace('<a href', '<a class="on" href', 1)
            return re.sub(r'\s+class="[^"]*"', '', tag)
        html = re.sub(r'<a href="' + re.escape(f) + r'"[^>]*>', nav_repl, html)
    return html

def build_nav(file):
    return rewrite_links(header_html, file)

def build_pager(sid):
    idx = ORDER.index(sid)
    parts = []
    if idx > 0:
        prev = ORDER[idx - 1]
        parts.append('<a class="btn" href="' + PAGE_FILE[prev] + '">&larr; 上一部分：' + PAGE_LABEL[prev] + '</a>')
    else:
        parts.append('<span></span>')
    if idx < len(ORDER) - 1:
        nxt = ORDER[idx + 1]
        parts.append('<a class="btn primary" href="' + PAGE_FILE[nxt] + '">下一部分：' + PAGE_LABEL[nxt] + ' &rarr;</a>')
    return ('<nav aria-label="分页导航" style="margin-top:36px;display:flex;justify-content:space-between;'
            'gap:12px;flex-wrap:wrap">' + "".join(parts) + "</nav>")

def build_page(sid):
    file = PAGE_FILE[sid]
    body = build_nav(file)
    body += '\n<main id="top" class="page-main">\n\n'
    for sec_id in PAGE_SECTIONS[sid]:
        body += rewrite_links(SEC[sec_id], file) + "\n\n"
    body += build_pager(sid) + "\n"
    body += "</main>\n\n" + tail_after_main.strip() + "\n\n"   # close main + footer
    body += script1 + "\n\n"
    if sid == "quiz":
        body += script2 + "\n\n"
    body += TRANSITION_JS + "</body>\n</html>\n"

    page = head_html
    page = page.replace("<title>CSP-S 初赛备考全攻略 · CSPSpass</title>",
                        "<title>" + PAGE_TITLES[sid] + "</title>")
    page = page.replace("</head>\n", TRANSITION_CSS + "</head>\n")
    # force light-mode-independent enter animation start
    page = page.replace("<body ", '<body class="page-enter" ', 1)
    page += body
    return page

# ---- write all pages ----
for sid in ORDER:
    out = os.path.join(ROOT, PAGE_FILE[sid])
    open(out, "w", encoding="utf-8", newline="\n").write(build_page(sid))
    print("wrote", PAGE_FILE[sid], os.path.getsize(out), "bytes")

# ---- verify: no stale hash anchors left, all internal links resolve ----
files = [PAGE_FILE[s] for s in ORDER]
ok = True
for f in files:
    html = open(os.path.join(ROOT, f), encoding="utf-8").read()
    for m in re.finditer(r'href="#([a-zA-Z-]+)"', html):
        print("STALE ANCHOR", f, m.group(0)); ok = False
    for m in re.finditer(r'href="([a-z]+\.html)"', html):
        if not os.path.exists(os.path.join(ROOT, m.group(1))):
            print("BROKEN LINK", f, m.group(1)); ok = False
print("VERIFY:", "OK" if ok else "FAILED")
