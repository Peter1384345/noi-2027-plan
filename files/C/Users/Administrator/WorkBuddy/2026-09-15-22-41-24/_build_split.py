# -*- coding: utf-8 -*-
"""Split dragon-raja-story monolithic index.html + atlas-v2.html into a multi-page site."""
import io, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(ROOT, 'dragon-raja-story')

def read(p):
    with io.open(os.path.join(REPO, p), 'r', encoding='utf-8') as f:
        return f.read()

def write(p, s):
    path = os.path.join(REPO, p)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(s)

lines = read('index.html').split('\n')  # 0-indexed; file line N = lines[N-1]

# ---------- 1. CSS ----------
css = '\n'.join(lines[15:2233])  # file lines 16..2233

# ---------- 2. sections ----------
sec_ranges = {
    'sec-relations':   (2276, 2324),
    'sec-info':        (2324, 2333),
    'sec-power':       (2333, 2347),
    'sec-plot':        (2347, 2414),
    'sec-pulse':       (2414, 2432),
    'sec-battles':     (2432, 2594),
    'sec-timeline':    (2594, 2653),
    'sec-world':       (2653, 3410),
    'sec-org':         (3410, 3646),
    'sec-alchemy':     (3646, 3738),
    'sec-quotes':      (3738, 3903),
    'sec-trivia':      (3903, 4000),
    'sec-dragons':     (4035, 4147),
    'sec-dragon-tree': (4147, 4165),
    'sec-families':    (4165, 4269),
    'sec-fates':       (4269, 4568),
    'sec-weapons':     (4568, 4666),
    'sec-scenes':      (4666, 4754),
    'sec-ranks':       (4754, 4850),
    'sec-destiny':     (4850, 4860),
}
sections = {}
for k, (a, b) in sec_ranges.items():
    sections[k] = '\n'.join(lines[a-1:b-1])

def sec_title(html):
    m = re.search(r'<h2[^>]*>(.*?)</h2>', html, re.S)
    if not m:
        return ''
    t = re.sub(r'<[^>]+>', '', m.group(1))
    return t.strip()

# ---------- 3. widgets (footer + toast + update panel) ----------
widgets = '\n'.join(lines[3999:4034])  # file lines 4000..4034

# ---------- 4. page.js ----------
js = '\n'.join(lines[4862:5171])  # file lines 4863..5171
start = js.index('// Nav active state on scroll')
end = js.index('// ===== Scroll Reveal Animation')
js = js[:start] + js[end:]
page_js = js.strip()
write('_shared/js/page.js', page_js)

# ---------- 5. patch charts.js (guard relations init) ----------
charts = read('assets/charts.js')
old = "var chart = echarts.init(document.getElementById('chart-relations'), null, { renderer: 'canvas' });"
new = ("var relationsEl = document.getElementById('chart-relations');\n"
       "  if (!relationsEl) return;\n"
       "  var chart = echarts.init(relationsEl, null, { renderer: 'canvas' });")
if old in charts:
    write('assets/charts.js', charts.replace(old, new, 1))
else:
    assert 'relationsEl' in charts, 'charts.js relations init not found and not patched'

# ---------- 6. shared CSS extras (landing + page anchors + explore v2) ----------
extra_css = '''
/* ===== Multi-page site extras ===== */
.page-anchors { display: flex; flex-wrap: wrap; gap: .45rem; margin: 0 0 1.6rem; }
.page-anchors a {
  font-size: .78rem; color: var(--muted); text-decoration: none;
  border: 1px solid var(--rule); border-radius: 999px; padding: .22rem .8rem; transition: all .25s;
}
.page-anchors a:hover { color: var(--ink); border-color: rgba(233,69,96,.5); background: rgba(233,69,96,.08); }

.landing-intro { color: var(--muted); text-align: center; max-width: 720px; margin: 0 auto 2.2rem; font-size: .95rem; }
.landing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.1rem; }
.landing-card {
  display: block; text-decoration: none; color: var(--ink);
  background: var(--glass); border: 1px solid var(--glass-border); border-radius: 16px;
  padding: 1.3rem 1.4rem; transition: transform .25s, border-color .25s, box-shadow .25s;
}
.landing-card:hover {
  transform: translateY(-4px); border-color: rgba(233,69,96,.55);
  box-shadow: 0 10px 34px rgba(233,69,96,.16);
}
.landing-card .lc-icon { font-size: 1.7rem; }
.landing-card h3 { font-size: 1.08rem; letter-spacing: .08em; margin: .5rem 0 .35rem; }
.landing-card h3 em { font-style: normal; font-size: .72rem; color: var(--accent-gold); letter-spacing: .18em; margin-left: .5rem; }
.landing-card p { color: var(--muted); font-size: .85rem; line-height: 1.7; }
.landing-card .lc-tags { margin-top: .7rem; display: flex; flex-wrap: wrap; gap: .35rem; }
.landing-card .lc-tags span {
  font-size: .7rem; color: var(--muted); border: 1px dashed var(--rule); border-radius: 4px; padding: .05rem .45rem;
}
.landing-card.gold h3 em { color: #ffd700; }
.landing-card.gold:hover { border-color: rgba(255,215,0,.55); box-shadow: 0 10px 34px rgba(255,215,0,.12); }

/* ===== Explore V2 component styles (namespaced) ===== */
.v2-head { display: flex; align-items: baseline; gap: .8rem; margin-bottom: .4rem; }
.v2-head .no { font-size: .8rem; color: var(--accent); letter-spacing: .2em; font-weight: 700; }
.v2-head h2 { font-size: 1.35rem; letter-spacing: .08em; }
.v2-desc { color: var(--muted); font-size: .9rem; margin-bottom: 1.2rem; }
.v2-card { background: var(--glass); border: 1px solid var(--glass-border); border-radius: 16px; padding: 1.4rem; box-shadow: 0 8px 30px rgba(0,0,0,.35); }
.v2-chart { width: 100%; height: 460px; }
.v2-note { color: var(--muted); font-size: .78rem; margin-top: .6rem; text-align: right; }
.v2-tree { display: flex; flex-direction: column; gap: .9rem; }
.v2-node { border-left: 2px solid rgba(233,69,96,.35); padding: .2rem 0 .2rem 1rem; }
.v2-node.q { cursor: pointer; user-select: none; transition: background .2s; border-radius: 0 10px 10px 0; }
.v2-node.q:hover { background: rgba(233,69,96,.07); }
.v2-node.q .q-text { font-weight: 700; color: var(--ink); }
.v2-node.q .q-text::after { content: ' \\25B8'; color: var(--accent); font-size: .8em; }
.v2-node.q.open .q-text::after { content: ' \\25BE'; }
.v2-node .children { display: none; margin-top: .7rem; }
.v2-node.q.open .children { display: flex; flex-direction: column; gap: .7rem; }
.v2-node.a { border-left-color: rgba(255,215,0,.45); }
.v2-node.a .a-path { color: var(--accent-gold); font-size: .8rem; letter-spacing: .1em; }
.v2-node.a .a-text { color: var(--ink); font-size: .92rem; }
.tag-spec { display: inline-block; font-size: .68rem; color: var(--muted); border: 1px dashed var(--rule); border-radius: 4px; padding: 0 .45rem; margin-left: .5rem; vertical-align: 1px; }
.draw-box { text-align: center; padding: 2.2rem 1.4rem; }
.draw-card { min-height: 130px; display: flex; align-items: center; justify-content: center; font-size: 1.15rem; line-height: 2; letter-spacing: .04em; color: var(--ink); opacity: 1; transition: opacity .35s; }
.draw-card.fade { opacity: 0; }
.draw-from { color: var(--accent-gold); font-size: .85rem; margin-top: .8rem; letter-spacing: .15em; }
.v2-btn { cursor: pointer; border: 1px solid rgba(233,69,96,.5); background: rgba(233,69,96,.12); color: var(--ink); font-family: var(--font); font-size: .9rem; letter-spacing: .2em; padding: .55rem 1.8rem; border-radius: 999px; transition: all .25s; }
.v2-btn:hover { background: rgba(233,69,96,.28); box-shadow: 0 0 18px rgba(233,69,96,.35); }
.v2-nebula { position: relative; height: 340px; overflow: hidden; }
.v2-nebula span { position: absolute; white-space: nowrap; cursor: default; transition: transform .3s, color .3s; font-weight: 700; }
.v2-nebula span:hover { transform: scale(1.18); color: #fff !important; z-index: 5; }
@media (max-width: 640px) { .v2-chart { height: 380px; } }
'''
write('_shared/css/site.css', css + extra_css)

# ---------- 7. shell builder ----------
def nav_html(active):
    items = [
        ('index.html', '首页', 'home'),
        ('characters.html', '人物', ''),
        ('story.html', '剧情', ''),
        ('world.html', '世界观', ''),
        ('moments.html', '图鉴语录', ''),
        ('fate.html', '命运', ''),
        ('explore.html', 'V2 探索台', 'gold'),
    ]
    out = ['  <nav class="nav-bar">', '    <div class="nav-inner">']
    for href, label, cls in items:
        a = ' active' if href == active else ''
        gold = ' style="color:#ffd700;border-color:rgba(255,215,0,.45)"' if cls == 'gold' else ''
        out.append('      <a class="nav-btn%s"%s href="%s">%s</a>' % (a, gold, href, label))
    out += ['    </div>', '  </nav>']
    return '\n'.join(out)

def page_shell(fname, title, desc, body, need_charts=False):
    scripts = ['<script src="_shared/js/page.js"></script>']
    if need_charts:
        scripts.insert(0, '<script src="assets/charts.js"></script>')
        scripts.insert(0, '<script>window.ECharts || document.write(\'<script src="_shared/js/echarts.min.js"><\\/script>\');</script>')
        scripts.insert(0, '<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>')
    tpl = u'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  <title>%(title)s</title>
  <meta name="description" content="%(desc)s">
  <link rel="preconnect" href="https://fonts.loli.net" crossorigin>
  <link href="https://fonts.loli.net/css2?family=Noto+Sans+SC:wght@400;700&display=swap" rel="stylesheet">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="_shared/css/site.css">
</head>
<body>

  <div class="vignette"></div>

%(body)s

  %(scripts)s
</body>
</html>
'''
    return tpl % {'title': title, 'desc': desc, 'body': body, 'scripts': '\n  '.join(scripts)}

def build_content_page(fname, title, desc, sec_ids, need_charts):
    hero_sub = desc.split('，')[0]
    parts = [nav_html(fname)]
    parts.append('''
  <div class="hero">
    <span class="beam2"></span>
    <h1>龙 族</h1>
    <div class="dragon-divider"></div>
    <div class="subtitle">%s</div>
    <div class="author">作者：江南 · 粉丝向整理</div>
  </div>''' % hero_sub)
    anchors = ''.join('        <a href="#%s">%s</a>\n' % (sid, sec_title(sections[sid]) or sid) for sid in sec_ids)
    body = [ '\n'.join(parts), '  <article class="page">', '    <div class="page-anchors reveal">', anchors, '    </div>' ]
    for sid in sec_ids:
        body.append(sections[sid])
    body.append(widgets)
    body.append('  </article>')
    write(fname, page_shell(fname, title, desc, '\n'.join(body), need_charts))

build_content_page('characters.html',
    '龙族 · 人物篇 | 关系图谱 / 角色详情 / 战力对比',
    '龙族人物可视化：核心人物关系图、角色详情档案与战力雷达对比',
    ['sec-relations', 'sec-info', 'sec-power'], True)

build_content_page('story.html',
    '龙族 · 剧情篇 | 分卷剧情 / 卷次强度 / 经典战役 / 事件时间线',
    '龙族剧情可视化：五部曲分卷剧情、卷次强度曲线、经典战役复盘与全系列事件时间线',
    ['sec-plot', 'sec-pulse', 'sec-battles', 'sec-timeline'], True)

build_content_page('world.html',
    '龙族 · 世界观篇 | 设定 / 炼金术 / 势力 / 龙王 / 家族 / 武器',
    '龙族世界观可视化：世界设定、炼金术与科技、势力组织、龙王图鉴与谱系、家族谱系、武器图鉴',
    ['sec-world', 'sec-org', 'sec-alchemy', 'sec-dragons', 'sec-dragon-tree', 'sec-families', 'sec-weapons'], True)

build_content_page('moments.html',
    '龙族 · 图鉴篇 | 经典场景 / 经典语录 / 幕后彩蛋',
    '龙族名场面与知识图鉴：经典场景、经典语录与幕后彩蛋，支持随机更新',
    ['sec-scenes', 'sec-quotes', 'sec-trivia'], False)

build_content_page('fate.html',
    '龙族 · 命运篇 | 血统评级 / 角色命运 / 命运流向',
    '龙族命运可视化：血统评级榜、主要角色命运档案与命运流向图谱',
    ['sec-ranks', 'sec-fates', 'sec-destiny'], True)

# ---------- 8. explore.html (V2, unified shell) ----------
EXPLORE_BODY = nav_html('explore.html') + u'''
  <article class="page">
    <div class="hero">
      <span class="beam2"></span>
      <h1>龙族探索台</h1>
      <div class="dragon-divider"></div>
      <div class="subtitle">羁绊矩阵 · 阅读时间轴 · 剧情抉择树 · 台词抽签 · 意象星云</div>
      <div class="author">粉丝向整理，仅供学习交流</div>
    </div>
    <div class="page-anchors reveal">
      <a href="#v2-bonds">羁绊矩阵</a>
      <a href="#v2-books">阅读时间轴</a>
      <a href="#v2-tree">抉择树</a>
      <a href="#v2-quotes">台词抽签</a>
      <a href="#v2-nebula">意象星云</a>
    </div>

    <section id="v2-bonds" class="reveal">
      <div class="v2-head"><span class="no">01</span><h2>角色羁绊矩阵</h2></div>
      <p class="v2-desc">以粉丝视角为十二位核心角色两两之间的"羁绊强度"打分（0-100，越高羁绊越深）。悬停查看评注。数值为主观整理，欢迎在仓库 Issue 中讨论修订。</p>
      <div class="v2-card">
        <div id="chart-bonds" class="v2-chart"></div>
        <div class="v2-note">数据：粉丝向主观评分 · ECharts 热力图</div>
      </div>
    </section>

    <section id="v2-books" class="reveal">
      <div class="v2-head"><span class="no">02</span><h2>系列阅读时间轴</h2></div>
      <p class="v2-desc">按剧情内时间轴排列的系列阅读地图：横轴为故事内时间先后，纵轴按作品分道。年份为约数，具体以出版信息为准。</p>
      <div class="v2-card">
        <div id="chart-books" class="v2-chart" style="height:420px"></div>
        <div class="v2-note">建议阅读顺序：I → II → III → IV → V，前传可最后补完</div>
      </div>
    </section>

    <section id="v2-tree" class="reveal">
      <div class="v2-head"><span class="no">03</span><h2>互动剧情抉择树 <span class="tag-spec">粉丝推演 · 非官方</span></h2></div>
      <p class="v2-desc">"如果当时……会怎样？"点击节点展开粉丝向的剧情推演分支。所有分支均为假设性讨论，不代表原作走向。</p>
      <div class="v2-card"><div class="v2-tree" id="tree-root"></div></div>
    </section>

    <section id="v2-quotes" class="reveal">
      <div class="v2-head"><span class="no">04</span><h2>经典台词抽签</h2></div>
      <p class="v2-desc">点击抽取一句龙族系列广为流传的句子。句子为粉丝整理，个别措辞可能与原文略有出入。</p>
      <div class="v2-card draw-box">
        <div class="draw-card" id="quote-card">「点击下方按钮，抽取一句来自龙族世界的话。」</div>
        <div class="draw-from" id="quote-from"></div>
        <div style="margin-top:1.4rem"><button class="v2-btn" id="draw-btn">抽 取</button></div>
      </div>
    </section>

    <section id="v2-nebula" class="reveal">
      <div class="v2-head"><span class="no">05</span><h2>意象星云</h2></div>
      <p class="v2-desc">龙族世界的经典意象：学院、龙类、言灵、神器与组织。鼠标悬停可放大。</p>
      <div class="v2-card v2-nebula" id="nebula"></div>
    </section>

''' + widgets + u'''  </article>

  <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
  <script>window.ECharts || document.write('<script src="_shared/js/echarts.min.js"><\\/script>');</script>
  <script>
''' + read('atlas-v2.html').split("/* ============ 数据 ============ */",1)[1].rsplit("/* ============ 滚动显现 & resize ============ */",1)[0] + u'''  /* ============ 滚动显现 & resize ============ */
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) e.target.classList.add('vis'); }), { threshold: .12 });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
  window.addEventListener('resize', () => { bondsChart.resize(); booksChart.resize(); });
  </script>'''

write('explore.html', page_shell('explore.html',
    '龙族探索台 V2 | 羁绊矩阵 / 阅读时间轴 / 抉择树 / 台词抽签',
    '龙族探索台 V2：角色羁绊矩阵热力图、系列阅读时间轴、互动剧情抉择树、经典台词抽签与意象星云',
    EXPLORE_BODY, False))

# ---------- 9. landing index.html ----------
LANDING = nav_html('index.html') + u'''
  <div class="hero">
    <span class="beam2"></span>
    <h1>龙 族</h1>
    <div class="dragon-divider"></div>
    <div class="subtitle">全系列剧情整理与人物关系图谱</div>
    <div class="author">作者：江南 · 粉丝向可视化项目</div>
  </div>

  <article class="page">
    <p class="landing-intro reveal">
      「龙族」系列小说的可视化百科：人物、剧情、世界观、名场面与命运，现已拆分为六大主题页面，各有所专、按需探索。
    </p>
    <div class="landing-grid">
      <a class="landing-card reveal" href="characters.html">
        <div class="lc-icon">🕸️</div>
        <h3>人物篇<em>CHARACTERS</em></h3>
        <p>交互式力导向关系图谱、角色详情档案与战力雷达对比。</p>
        <div class="lc-tags"><span>人物关系</span><span>角色详情</span><span>战力对比</span></div>
      </a>
      <a class="landing-card reveal" href="story.html">
        <div class="lc-icon">📖</div>
        <h3>剧情篇<em>STORY</em></h3>
        <p>五部曲分卷剧情、卷次强度曲线、经典战役复盘与全系列事件时间线。</p>
        <div class="lc-tags"><span>分卷剧情</span><span>卷次强度</span><span>经典战役</span><span>时间线</span></div>
      </a>
      <a class="landing-card reveal" href="world.html">
        <div class="lc-icon">🌍</div>
        <h3>世界观篇<em>WORLD</em></h3>
        <p>世界设定、炼金术与科技、势力组织、龙王图鉴与谱系、家族谱系、武器图鉴。</p>
        <div class="lc-tags"><span>世界观</span><span>龙王图鉴</span><span>家族谱系</span><span>武器</span></div>
      </a>
      <a class="landing-card reveal" href="moments.html">
        <div class="lc-icon">🎭</div>
        <h3>图鉴篇<em>MOMENTS</em></h3>
        <p>经典场景、经典语录与幕后彩蛋，一键随机更新新增内容。</p>
        <div class="lc-tags"><span>经典场景</span><span>经典语录</span><span>幕后彩蛋</span></div>
      </a>
      <a class="landing-card reveal" href="fate.html">
        <div class="lc-icon">🔮</div>
        <h3>命运篇<em>FATE</em></h3>
        <p>血统评级榜、主要角色命运档案与命运流向图谱。</p>
        <div class="lc-tags"><span>血统评级</span><span>角色命运</span><span>命运流向</span></div>
      </a>
      <a class="landing-card gold reveal" href="explore.html">
        <div class="lc-icon">🧭</div>
        <h3>探索台 V2<em>EXPLORE</em></h3>
        <p>角色羁绊矩阵热力图、系列阅读时间轴、互动剧情抉择树、台词抽签与意象星云。</p>
        <div class="lc-tags"><span>羁绊矩阵</span><span>阅读时间轴</span><span>抉择树</span><span>台词抽签</span><span>意象星云</span></div>
      </a>
    </div>
''' + widgets + '''  </article>
'''
write('index.html', page_shell('index.html',
    '龙族全系列剧情与人物关系',
    '龙族系列小说可视化百科首页：人物、剧情、世界观、图鉴、命运与探索台六大主题页导航',
    LANDING, False))

# ---------- 10. remove old V2 page ----------
p = os.path.join(REPO, 'atlas-v2.html')
if os.path.exists(p):
    os.remove(p)
    print('removed atlas-v2.html')

print('OK: pages built')
for f in ['index.html','characters.html','story.html','world.html','moments.html','fate.html','explore.html','_shared/css/site.css','_shared/js/page.js']:
    fp = os.path.join(REPO, f)
    print('%-24s %6d lines' % (f, sum(1 for _ in io.open(fp, encoding='utf-8'))))
