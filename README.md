# NOI 2027 · 一年计划

> 依据《NOI 大纲（2025 年修订版）》与 CCF 赛历编制的 56 周信息学奥赛作战方案。
> 起点：CSP-S 2026 第一轮三级（广东 · GD-S02743）。终点：NOIP 2027。

**在线访问**：https://peter1384345.github.io/noi-2027-plan/

## 这是什么

不是一份励志计划表，而是一份可执行、可验收、可度量的训练方案。它把大纲的 198 个知识点逐条拆进 56 周，按赛历倒排到 CSP-S 2027 与 NOIP 2027 两个实战节点。

## 页面结构

**统一入口**：`app.html` —— 单页应用外壳。13 个板块都在同一个页面内切换（`#/计划`、`#/知识库`…），不整页跳转；视图内容按需从同仓库的静态文件装配。`index.html` 只做一次重定向到 `app.html`。

每个板块同时保留独立页面，便于深链接与书签直接访问：

| 页面 | 内容 |
|---|---|
| `app.html` | 工作台外壳：13 个视图的 hash 路由、按需加载、全局搜索、进度与主题 |
| `views/overview.html` | 总览：三条硬结论、六阶段路线、知识分布、起点与终点 |
| `plan.html` | 56 周逐周任务表，可按阶段筛选、勾选打卡（localStorage） |
| `kb.html` | 站内知识库：73 篇正文 30.4 万字，全文检索、代码高亮、标记已读 |
| `papers.html` | 真题库：2022/2023 在线作答判分，2025 全文 |
| `syllabus.html` | NOI 大纲 2025 修订版 10 个难度级全量条目 + 2025 年变化 |
| `books.html` | CCF 官方出版物 6 类、经典教材 13 本、在线平台 12 个 |
| `problems.html` | 题单：由本地 `CSP-JS+NOI 题单.xlsx` 重构，含题量分配模型 |
| `templates.html` | 56 个 C++ 模板，标注等级、复杂度、易错点，一键复制 |
| `contests.html` | 七级漏斗、2026–2028 赛历、六个高频疑问直答 |
| `assess.html` | 能力雷达、9 个里程碑阈值、周自检七问、评分表、止损线 |
| `resources.html` | C/D/E 三盘扫描结论、11 类高价值资料、GitHub 仓库清单、资料使用地图 |
| `archive.html` | 资料仓库：1,133 个文件实体（770 MB）已全部入库，目录浏览、MiniSearch 模糊搜索、PDF（原生阅读器）/Word/Excel/代码在线预览与下载 |
| `method.html` | 刻意练习闭环、对拍工程、考场时间分配、七个失败模式 |

### 外壳的工作方式

- 路由：`#/<视图>` 或 `#/<视图>/<锚点>`，如 `#/plan/w20`、`#/kb/ds-31`、`#/templates/tpl-并查集`
- 装配：`fetch` 目标页面 → `DOMParser` 取 `body` 内容（剔除共享头部/页脚/脚本）→ 注入 `#view` → 按序执行该页脚本
- 隔离：挂载期间记录视图注册到 `window`/`document` 的监听器，切走时统一下线，避免回调作用在已销毁的 DOM 上
- 幂等：视图脚本的 `DOMContentLoaded` 初始化在注入后统一派发，`app.js` 的引导只执行一次
- 站内链接一律拦截为路由跳转；`?open=` 等旧参数仍生效


## 核心判断

1. **一年到 NOI 正赛，时间上不成立。** 省选在每年 3–4 月、NOI 在 7 月。2026 年 11 月起步，2027 年 3 月的省选只剩 4 个月。本计划的目标是 12 个月内建成 NOI 级知识体系并拿下 NOIP 一等奖，正赛窗口锁定 2028 年 7 月。
2. **决定省一的是 T1 和 T2，不是 T4。** 400 分制下，省一线 150–200 分 = T1 满分 + T2 满分或 70% + T3 部分分。
3. **刷题量不等于进步量。** 真正指标是一次 AC 率与错题重做成功率。

## 技术说明

纯静态站点，零依赖、零构建：

- 原生 HTML / CSS / JavaScript，无框架、无 CDN 依赖（字体走系统栈）
- 数据层分离在 `assets/js/data/`：`weeks.js`、`syllabus.js`、`books.js`、`templates.js`、`contests.js`
- 进度持久化用 `localStorage`（键 `noi2027.progress.v1`），主题偏好同样本地保存
- 支持全站搜索（按 `/` 唤起）、深浅色切换、打印样式
- 资料仓库由 `../build/scan_assets.py`、`scan_github.py`、`ingest_files.py` 生成：文件实体在 `files/`，清单在 `assets/data/files/manifest.js`
- 在线预览依赖 `vendor/` 内四个开源项目（MIT / Apache-2.0 / BSD），全部本地 vendor 化、运行时不联网；PDF 交给浏览器原生阅读器：

  | 插件 | 版本 | 用途 |
  | --- | --- | --- |
  | MiniSearch | 6.3.0 | 文件名/路径模糊检索（前缀 + 0.2 容错，文件名权重 2 倍） |
  | docx-preview + JSZip | 0.3.2 / 3.10.1 | Word 排版还原（分页、表格、图片） |
  | SheetJS | 0.18.5 | Excel 多工作表切换、CSV |
  | Prism | 1.29.0 + C/C++ 组件 | 代码高亮；C++ 组件必须先加载 `prism-c.min.js`，否则静默失效 |

```
.
├── app.html               # 单页工作台外壳（统一入口）
├── index.html             # 仅做一次重定向到 app.html
├── views/overview.html    # 总览视图（外壳按需加载）
├── plan.html
├── kb.html
├── papers.html
├── syllabus.html
├── books.html
├── problems.html
├── templates.html
├── contests.html
├── assess.html
├── resources.html
├── method.html
├── 404.html
├── .nojekyll
├── files/                 # 资料文件实体（按 C/ D/ E/ 原始目录结构）
├── vendor/                # 开源插件：MiniSearch / docx-preview + JSZip / SheetJS / Prism
└── assets
    ├── css/main.css
    ├── js
    │   ├── app.js         # 导航注入、全局搜索、进度持久化、主题
    │   ├── shell.js       # 单页路由、视图装配、监听器隔离
    │   └── data/*.js
    ├── data/kb/*.js       # 站内正文（73 篇 / 30.4 万字）与真题数据
    └── data/files/manifest.js   # 资料仓库清单（1,133 个文件）
```

## 数据来源

- NOI 大纲（2025 年修订版）官方 PDF · noi.cn
- CCF NOI 官网 · noi.ccf.org.cn（赛历、条例、获奖公告）
- 本地资料：`CSP-S知识库全集`、`信息学竞赛知识文集`、`CSP-JS+NOI 题单`、`NOI2025.pdf`、CSP-S 2021–2024 第一轮真题
- 赛历日期按 CCF 历年惯例推算，具体以当年官方通知为准

## 更新方式

```bash
git add -A
git commit -m "更新内容"
git push
```

GitHub Pages 会自动重建，约 1 分钟后生效。

**本机 Windows 注意**：本机代理对 HTTPS 做了中间人，裸 `git push` / `git fetch` 会报 `schannel: ... CRYPT_E_NO_REVOCATION_CHECK`（证书吊销检查无法完成）；只换 OpenSSL 后端又会报 `unable to get local issuer certificate (20)`。本机实测可用的写法是显式指定 OpenSSL 后端并跳过证书校验：

```bash
GIT_SSL_NO_VERIFY=true git -c http.sslBackend=openssl -c http.sslVerify=false push origin main
```

若网络把 git 通道整体阻断，还有完全不依赖 `git push` 的备用方案 `../build/apipush.py`（GitHub Git Data API）：它把 `git diff --name-only 51036ec HEAD` 列出的变更文件按字节创建 blob，再组装 tree / commit 并更新远端 `main`。该脚本位于本机工作区、不随仓库分发；重复使用时应把其中的基线 `51036ec` 改成当前 HEAD。

---

*本计划基于 CCF NOI 大纲（2025 年修订版）编制。赛历与规则以官方当年通知为准。*
