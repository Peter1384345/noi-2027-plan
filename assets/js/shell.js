/* ==========================================================================
   NOI 2027 · 单页应用外壳（shell）
   把 13 个板块合成一个页面：hash 路由 + 视图按需加载 + 脚本按序执行
   所有内容都来自同一仓库内的静态文件，无外部依赖
   ========================================================================== */

(function () {
  "use strict";

  var VIEWS = {};
  (window.App ? App.NAV : []).forEach(function (v) { VIEWS[v.id] = v; });

  var cache = {};       // id -> { nodes, styles, scripts }
  var loadedSrc = {};   // 已执行过的外链脚本
  var curId = null;
  var bar = null;
  var warmed = false;

  function $(id) { return document.getElementById(id); }

  /* ---------------- 顶部进度条 ---------------- */
  function barEl() {
    if (!bar) {
      bar = document.createElement("div");
      bar.className = "view-bar";
      document.body.appendChild(bar);
    }
    return bar;
  }
  function barStart() {
    var b = barEl();
    b.style.opacity = "1";
    b.style.width = "18%";
    setTimeout(function () { b.style.width = "68%"; }, 220);
  }
  function barDone() {
    var b = barEl();
    b.style.width = "100%";
    setTimeout(function () { b.style.opacity = "0"; b.style.width = "0"; }, 260);
  }

  /* ---------------- 路由解析 ---------------- */
  function parse() {
    var raw = (location.hash || "").replace(/^#\/?/, "");
    if (!raw) return { id: "overview", anchor: "" };
    var parts = raw.split("/");
    var id = parts.shift() || "overview";
    var anchor = parts.join("/");
    if (!VIEWS[id]) return { id: "overview", anchor: "" };
    return { id: id, anchor: anchor };
  }

  /* ---------------- 抓取并解析视图 ---------------- */
  function fetchView(id) {
    if (cache[id]) return Promise.resolve(cache[id]);
    var v = VIEWS[id];
    return fetch(v.f, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.text();
    }).then(function (text) {
      var doc = new DOMParser().parseFromString(text, "text/html");
      var nodes = [];
      Array.prototype.forEach.call(doc.body.children, function (n) {
        if (n.tagName === "SCRIPT") return;
        if (n.id === "site-head" || n.id === "site-foot") return;
        nodes.push(n);
      });
      var styles = Array.prototype.map.call(doc.querySelectorAll("style"), function (s) {
        return s.textContent;
      });
      var scripts = Array.prototype.map.call(doc.querySelectorAll("script"), function (s) {
        var src = s.getAttribute("src");
        return { src: src, text: src ? "" : s.textContent };
      }).filter(function (s) {
        // app.js 由外壳统一提供，不在视图内重复执行
        return !(s.src && /(^|\/)app\.js(\?|$)/.test(s.src));
      });
      cache[id] = { nodes: nodes, styles: styles, scripts: scripts };
      return cache[id];
    });
  }

  /* ---------------- 监听器生命周期 ----------------
     视图脚本会往 window/document 上挂 hashchange、resize 等监听器。
     若不清除，切换一次积一层，旧视图的回调会作用在已被替换的 DOM 上。
     做法：挂载期间记录注册行为，下次挂载前统一下线。            */
  var bound = [];
  var hooked = [];

  function capture() {
    [window, document].forEach(function (t) {
      if (t.__origAdd) return;
      t.__origAdd = t.addEventListener;
      t.__origRemove = t.removeEventListener;
      hooked.push(t);
      t.addEventListener = function (type, fn, opt) {
        if (fn) bound.push([t, type, fn, opt]);
        return t.__origAdd.call(t, type, fn, opt);
      };
    });
  }

  function restore() {
    hooked.forEach(function (t) {
      if (t.__origAdd) { t.addEventListener = t.__origAdd; delete t.__origAdd; }
      if (t.__origRemove) { delete t.__origRemove; }
    });
    hooked = [];
  }

  function release() {
    bound.forEach(function (b) {
      try { b[0].removeEventListener(b[1], b[2], b[3]); } catch (e) { /* 忽略 */ }
    });
    bound = [];
    restore();
  }

  /* ---------------- 后台预热：预取其余视图的 HTML ---------------- */
  // 视图 HTML 加起来只有一百多 KB，首屏就绪后逐个预取，之后切换基本瞬时
  function warm() {
    if (warmed) return;
    warmed = true;
    var ids = Object.keys(VIEWS).filter(function (k) { return !cache[k]; });
    var i = 0;
    function next() {
      if (i >= ids.length) return;
      fetchView(ids[i++]).catch(function () {}).then(function () { setTimeout(next, 80); });
    }
    setTimeout(next, 600);
  }

  /* ---------------- 按序执行脚本 ---------------- */
  var seq = 0;

  // 每个视图脚本都写成 document.addEventListener("DOMContentLoaded", init)。
  // 若直接派发 DOMContentLoaded，残留的旧监听器也会被唤醒，此时 DOM 已换 → 报错。
  // 故把注册点改写成一次性事件名，每轮挂载唯一，旧监听器永远收不到。
  function runInline(text, evName) {
    var src = String(text).replace(
      /document\.addEventListener\(\s*(["'])DOMContentLoaded\1\s*,/g,
      'document.addEventListener("' + evName + '",'
    );
    var el = document.createElement("script");
    el.textContent = src;
    document.body.appendChild(el);
    if (el.parentNode) el.parentNode.removeChild(el);
  }

  function runScripts(list, evName) {
    return list.reduce(function (p, s) {
      return p.then(function () {
        if (s.src) {
          if (loadedSrc[s.src]) return null;
          loadedSrc[s.src] = true;
          return new Promise(function (res) {
            var el = document.createElement("script");
            el.src = s.src;
            el.onload = res;
            el.onerror = res;   // 单个依赖失败不阻断整个视图
            document.body.appendChild(el);
          });
        }
        runInline(s.text, evName);
        return null;
      });
    }, Promise.resolve());
  }

  /* ---------------- 挂载视图 ---------------- */
  function mount(id, data, anchor) {
    release();                       // 下线上一视图的全局监听器

    var view = $("view");
    view.classList.add("loading");
    view.innerHTML = "";
    var frag = document.createDocumentFragment();
    data.nodes.forEach(function (n) { frag.appendChild(n.cloneNode(true)); });
    view.appendChild(frag);

    var sid = "st-" + id;
    if (!$(sid) && data.styles.length) {
      var st = document.createElement("style");
      st.id = sid;
      st.textContent = data.styles.join("\n");
      document.head.appendChild(st);
    }

    var evName = "view:mount:" + (++seq);
    capture();                       // 开始记录本视图注册的监听器
    return runScripts(data.scripts, evName).then(function () {
      restore();
      document.dispatchEvent(new Event(evName));   // 只唤醒本轮注册的初始化
      view.classList.remove("loading");
      afterMount(anchor);
    }, function (e) {
      restore();
      throw e;
    });
  }

  function afterMount(anchor) {
    window.scrollTo(0, 0);
    if (!anchor) return;
    var target = anchor;
    function jump() {
      var t = $(target);
      if (!t) { try { t = $(decodeURIComponent(target)); } catch (e) {} }
      if (t) t.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    // 视图内容多为脚本渲染，留出两拍：首拍定位，二次校正（图片/字体撑开高度后）
    setTimeout(jump, 120);
    setTimeout(jump, 560);
  }

  /* ---------------- 主流程 ---------------- */
  var token = 0;
  var chain = Promise.resolve();   // 挂载串行队列

  function go() {
    var r = parse();
    var v = VIEWS[r.id];
    document.title = v.t + " · NOI 2027 一年计划";

    if (r.id === curId) {
      App.setActive(r.id);
      afterMount(r.anchor);
      return;
    }

    // 视图挂载必须串行：src 脚本是异步的，两轮挂载交叠会让监听器记录错位
    var my = ++token;
    barStart();
    chain = chain.then(function () {
      if (my !== token) return null;          // 已被更新的路由取代
      return fetchView(r.id).then(function (data) {
        if (my !== token) return null;
        curId = r.id;
        return mount(r.id, data, r.anchor);
      });
    }).then(function () {
      if (my !== token) return;
      barDone();
      App.setActive(r.id);
      App._idx = null;
      warm();
    }).catch(function (err) {
      if (my !== token) return;
      barDone();
      $("view").innerHTML =
        '<section class="section"><div class="wrap"><div class="note">' +
        "该板块加载失败（" + String(err.message || err) + "）。<br>" +
        '可直接访问 <a href="' + v.f + '">' + v.f + "</a> 或刷新重试。</div></div></section>";
    });
  }

  window.addEventListener("hashchange", go);

  /* ---------------- 站内链接拦截：不再整页跳转 ---------------- */
  function viewOfFile(file) {
    if (file === "index.html" || file === "") return "overview";
    var keys = Object.keys(VIEWS);
    for (var i = 0; i < keys.length; i++) {
      var f = VIEWS[keys[i]].f;
      if (f.split("/").pop() === file) return keys[i];
    }
    return null;
  }

  document.addEventListener("click", function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest ? e.target.closest("a[href]") : null;
    if (!a) return;
    var href = a.getAttribute("href");
    if (!href || /^(https?:|mailto:|tel:|javascript:)/i.test(href)) return;

    var url;
    try { url = new URL(href, location.href); } catch (err) { return; }
    if (url.origin !== location.origin) return;

    var m = /^#\/([a-z]+)(?:\/(.*))?$/.exec(url.hash || "");
    if (m && VIEWS[m[1]]) {
      e.preventDefault();
      var next = "#/" + m[1] + (m[2] ? "/" + m[2] : "");
      if (location.hash === next) { afterMount(m[2] || ""); return; }
      // 改 hash 而不是直接渲染：让视图自己的 hashchange 逻辑（如知识库换篇）也生效
      location.hash = next;
      return;
    }
    var file = url.pathname.split("/").pop();
    var id = viewOfFile(file);
    if (!id) return;
    e.preventDefault();
    Router.go(id, (url.hash || "").replace(/^#\/?/, ""));
  });

  document.addEventListener("DOMContentLoaded", function () {
    // 首次进入：无 hash 时补一个，保证地址栏与视图一致
    if (!location.hash) {
      try { history.replaceState(null, "", "#/overview"); } catch (e) { location.hash = "#/overview"; }
    }
    go();
  });

  // 暴露给外部（例如首页卡片、页脚链接）做程序化跳转
  window.Router = {
    go: function (id, anchor) { location.hash = "#/" + id + (anchor ? "/" + anchor : ""); },
    refresh: go
  };
})();
