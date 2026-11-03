/* ==========================================================================
   NOI 2027 · 站点共享逻辑
   导航/页脚注入 · 全站搜索 · 进度持久化 · 倒计时 · 代码复制
   ========================================================================== */

(function () {
  "use strict";

  const NAV = [
    { h: "index.html",     t: "总览",  s: "Overview" },
    { h: "plan.html",      t: "56 周计划", s: "Plan" },
    { h: "kb.html",        t: "知识库",  s: "Knowledge Base" },
    { h: "papers.html",    t: "真题库",  s: "Papers" },
    { h: "archive.html",   t: "档案库",  s: "Archive" },
    { h: "syllabus.html",  t: "大纲",   s: "Syllabus" },
    { h: "problems.html",  t: "题单",   s: "Problems" },
    { h: "templates.html", t: "模板",   s: "Templates" },
    { h: "books.html",     t: "书单",   s: "Reading" },
    { h: "contests.html",  t: "赛历",   s: "Contests" },
    { h: "assess.html",    t: "评估",   s: "Assessment" }
  ];

  const STORE = "noi2027.progress.v1";

  function load() {
    try { return JSON.parse(localStorage.getItem(STORE)) || { weeks: {}, kp: {}, notes: {} }; }
    catch (e) { return { weeks: {}, kp: {}, notes: {} }; }
  }
  function save(d) {
    try { localStorage.setItem(STORE, JSON.stringify(d)); } catch (e) {}
  }

  const App = {
    NAV,
    data: load(),

    /* ---------- 主题 ---------- */
    initTheme() {
      const t = localStorage.getItem("noi2027.theme") || "light";
      document.documentElement.setAttribute("data-theme", t);
      this.syncThemeBtn();
    },
    toggleTheme() {
      const cur = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", cur);
      localStorage.setItem("noi2027.theme", cur);
      this.syncThemeBtn();
    },
    syncThemeBtn() {
      const b = document.getElementById("theme-btn");
      if (!b) return;
      const dark = document.documentElement.getAttribute("data-theme") === "dark";
      b.textContent = dark ? "☀" : "☾";
      b.title = dark ? "切换到浅色" : "切换到深色";
    },

    /* ---------- 布局注入 ---------- */
    mount(active) {
      const el = document.getElementById("site-head");
      if (el) {
        el.className = "site-head";
        el.innerHTML = `
          <div class="site-head-inner">
            <a class="brand" href="index.html">
              <span class="brand-seal">N</span>
              <span class="brand-txt"><b>NOI 2027 一年计划</b><span>Zero to NOI</span></span>
            </a>
            <nav class="nav">
              ${NAV.map(n => `<a href="${n.h}" class="${n.h === active ? "on" : ""}">${n.t}</a>`).join("")}
            </nav>
            <div class="head-tools">
              <button class="icon-btn" id="search-btn" title="搜索全站 (/)">⌕</button>
              <button class="icon-btn" id="theme-btn" onclick="App.toggleTheme()" title="切换主题"></button>
              <button class="icon-btn menu-btn" id="menu-btn" title="菜单">☰</button>
            </div>
          </div>`;
        document.getElementById("search-btn").onclick = () => App.openSearch();
        document.getElementById("menu-btn").onclick = () => App.openDrawer(active);
        this.syncThemeBtn();
      }

      const f = document.getElementById("site-foot");
      if (f) {
        f.className = "site-foot";
        f.innerHTML = `
          <div class="wrap">
            <div class="foot-grid">
              <div>
                <div class="brand" style="margin-bottom:12px">
                  <span class="brand-seal">N</span>
                  <span class="brand-txt"><b>NOI 2027 一年计划</b><span>Zero to NOI</span></span>
                </div>
                <p class="small" style="max-width:34ch">为黄梓涵（广东 · GD-S02743）定制的 56 周信息学奥赛作战计划。起点：CSP-S 2026 第一轮三级；终点：NOIP 2027。</p>
              </div>
              <div>
                <h5>学习路径</h5>
                <a href="plan.html">56 周计划</a>
                <a href="kb.html">知识库（73 篇）</a>
                <a href="archive.html">全量档案库</a>
                <a href="papers.html">真题库</a>
                <a href="syllabus.html">大纲全解</a>
              </div>
              <div>
                <h5>训练与资料</h5>
                <a href="problems.html">题单训练</a>
                <a href="templates.html">模板库（56）</a>
                <a href="books.html">书单资料</a>
                <a href="resources.html">本地资产</a>
                <a href="method.html">方法论</a>
              </div>
              <div>
                <h5>官方来源</h5>
                <a href="http://noi.ccf.org.cn/" target="_blank" rel="noopener">CCF NOI 官网</a>
                <a href="https://www.noi.cn/upload/resources/file/2025/04/18/NOI_Syllabus_Edition_2025.pdf" target="_blank" rel="noopener">NOI 大纲 2025</a>
                <a href="https://www.luogu.com.cn/" target="_blank" rel="noopener">洛谷</a>
                <a href="https://oi-wiki.org/" target="_blank" rel="noopener">OI Wiki</a>
              </div>
            </div>
            <div class="foot-bottom">
              <span>© 2026–2027 NOI 一年计划 · 依据 CCF NOI 大纲（2025 年修订版）编制</span>
              <span>赛历与规则以 CCF 官方当年通知为准</span>
            </div>
          </div>`;
      }
    },

    openDrawer(active) {
      let d = document.getElementById("drawer");
      if (!d) {
        d = document.createElement("div");
        d.id = "drawer"; d.className = "drawer";
        document.body.appendChild(d);
      }
      d.innerHTML = `
        <div class="drawer-head">
          <b style="font-family:var(--serif)">目录</b>
          <button class="icon-btn" onclick="document.getElementById('drawer').classList.remove('open')">✕</button>
        </div>
        ${NAV.map(n => `<a href="${n.h}">${n.t}<small>${n.s}</small></a>`).join("")}`;
      d.classList.add("open");
    },

    /* ---------- 搜索 ---------- */
    buildIndex() {
      const idx = [];
      idx.push({ t: "全量档案库 · C/D/E 三盘", s: "207,715 个文件逐条索引 · 877 篇正文 · 115 份原文件", h: "archive.html", k: "档案" });
      idx.push({ t: "GitHub 全部仓库", s: "15 个仓库 / 870 个文件逐文件直达", h: "archive.html", k: "档案" });
      if (window.WEEKS) WEEKS.forEach(w => idx.push({
        t: `第 ${w.w} 周 · ${w.t}`, s: w.kg, h: `plan.html#w${w.w}`, k: "计划"
      }));
      if (window.KB_CATALOG) KB_CATALOG.forEach(a => idx.push({
        t: a.title, s: `${a.cat} · ${(a.chars / 1000).toFixed(1)}k 字`, h: `kb.html#${a.id}`, k: "知识库"
      }));
      if (window.PAPERS) PAPERS.forEach(p => idx.push({
        t: `CSP-S ${p.year} 第一轮真题`, s: "在线作答 · 单选判分", h: "papers.html", k: "真题"
      }));
      if (window.SYLLABUS) SYLLABUS.points.forEach(p => idx.push({
        t: p[0], s: `${p[1]} · ${p[2]} 级`, h: `syllabus.html#lv${p[2]}`, k: "大纲"
      }));
      if (window.BOOKS) {
        BOOKS.official.forEach(b => idx.push({ t: b.t, s: `${b.tag} · ${b.a}`, h: "books.html", k: "官方" }));
        BOOKS.classic.forEach(b => idx.push({ t: b.t, s: `${b.tag} · ${b.a}`, h: "books.html", k: "教材" }));
      }
      if (window.TEMPLATES) TEMPLATES.forEach(t => idx.push({
        t: t.n, s: `${t.c} · ${t.lv} 级 · ${t.cx}`, h: `templates.html#tpl-${encodeURIComponent(t.n)}`, k: "模板"
      }));
      if (window.LADDER) LADDER.forEach(l => idx.push({ t: l.s, s: l.f, h: "contests.html", k: "赛事" }));
      return idx;
    },
    openSearch() {
      let layer = document.getElementById("search-layer");
      if (!layer) {
        layer = document.createElement("div");
        layer.id = "search-layer"; layer.className = "search-layer";
        layer.innerHTML = `
          <div class="search-box">
            <input id="search-input" type="text" placeholder="搜索知识点、周次、模板、书籍…（Esc 关闭）" autocomplete="off">
            <div class="search-results" id="search-results"></div>
          </div>`;
        document.body.appendChild(layer);
        layer.addEventListener("click", e => { if (e.target === layer) layer.classList.remove("open"); });
        document.getElementById("search-input").addEventListener("input", e => App.runSearch(e.target.value));
      }
      layer.classList.add("open");
      const inp = document.getElementById("search-input");
      inp.value = ""; this.runSearch("");
      setTimeout(() => inp.focus(), 30);
    },
    runSearch(q) {
      const box = document.getElementById("search-results");
      if (!box) return;
      q = (q || "").trim().toLowerCase();
      if (!q) {
        box.innerHTML = `<div class="sr-empty">输入关键词开始检索 · 已索引 ${this._idx ? this._idx.length : 0} 条</div>`;
        return;
      }
      if (!this._idx) this._idx = this.buildIndex();
      const hit = this._idx.filter(i =>
        (i.t + " " + i.s + " " + i.k).toLowerCase().includes(q)
      ).slice(0, 40);
      box.innerHTML = hit.length
        ? hit.map(i => `<a class="sr-item" href="${i.h}"><b>${i.t}</b><span>${i.k} · ${i.s}</span></a>`).join("")
        : `<div class="sr-empty">没有匹配项。试试「线段树」「二分」「第 20 周」。</div>`;
    },

    /* ---------- 进度 ---------- */
    weekDone(w) { return !!this.data.weeks[w]; },
    toggleWeek(w) {
      this.data.weeks[w] = this.weekDone(w) ? 0 : 1;
      if (!this.data.weeks[w]) delete this.data.weeks[w];
      save(this.data);
      return this.weekDone(w);
    },
    kpDone(name) { return !!this.data.kp[name]; },
    toggleKp(name) {
      if (this.data.kp[name]) delete this.data.kp[name];
      else this.data.kp[name] = 1;
      save(this.data);
      return this.kpDone(name);
    },
    stats() {
      const totalW = window.WEEKS ? WEEKS.length : 56;
      const doneW = Object.keys(this.data.weeks).length;
      const totalK = window.SYLLABUS ? SYLLABUS.points.length : 0;
      const doneK = Object.keys(this.data.kp).length;
      return {
        totalW, doneW, pctW: totalW ? Math.round(doneW / totalW * 100) : 0,
        totalK, doneK, pctK: totalK ? Math.round(doneK / totalK * 100) : 0
      };
    },
    reset() {
      if (!confirm("确定清空全部进度记录？此操作不可撤销。")) return;
      this.data = { weeks: {}, kp: {}, notes: {} };
      save(this.data);
      location.reload();
    },

    /* ---------- 工具 ---------- */
    fmtDate(s) {
      const d = new Date(s + "T00:00:00");
      return `${d.getMonth() + 1} 月 ${d.getDate()} 日`;
    },
    daysTo(s) {
      const t = new Date(s + "T00:00:00").getTime();
      return Math.ceil((t - Date.now()) / 86400000);
    },
    countdown(elId, target) {
      const el = document.getElementById(elId);
      if (!el) return;
      const tick = () => {
        let ms = new Date(target + "T08:30:00").getTime() - Date.now();
        if (ms < 0) ms = 0;
        const d = Math.floor(ms / 86400000);
        const h = Math.floor(ms % 86400000 / 3600000);
        const m = Math.floor(ms % 3600000 / 60000);
        el.innerHTML = `
          <div class="cd-cell"><b>${d}</b><span>DAYS</span></div>
          <div class="cd-cell"><b>${String(h).padStart(2, "0")}</b><span>HOURS</span></div>
          <div class="cd-cell"><b>${String(m).padStart(2, "0")}</b><span>MINS</span></div>`;
      };
      tick(); setInterval(tick, 30000);
    },
    copy(btn, text) {
      const done = () => {
        const o = btn.textContent;
        btn.textContent = "已复制"; btn.classList.add("done");
        setTimeout(() => { btn.textContent = o; btn.classList.remove("done"); }, 1400);
      };
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done);
      } else {
        const ta = document.createElement("textarea");
        ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); done(); } catch (e) {}
        document.body.removeChild(ta);
      }
    },
    esc(s) {
      return String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    }
  };

  window.App = App;

  document.addEventListener("DOMContentLoaded", () => {
    App.initTheme();
    const active = document.body.getAttribute("data-page") || "index.html";
    App.mount(active);
    App._idx = App.buildIndex();

    document.addEventListener("keydown", e => {
      if (e.key === "Escape") {
        const l = document.getElementById("search-layer");
        if (l) l.classList.remove("open");
        const d = document.getElementById("drawer");
        if (d) d.classList.remove("open");
      }
      if (e.key === "/" && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) {
        e.preventDefault(); App.openSearch();
      }
    });
  });
})();
