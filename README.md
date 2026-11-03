# NOI 2027 · 一年计划

> 依据《NOI 大纲（2025 年修订版）》与 CCF 赛历编制的 56 周信息学奥赛作战方案。
> 起点：CSP-S 2026 第一轮三级（广东 · GD-S02743）。终点：NOIP 2027。

## 这是什么

不是一份励志计划表，而是一份可执行、可验收、可度量的训练方案。它把大纲的 198 个知识点逐条拆进 56 周，按赛历倒排到 CSP-S 2027 与 NOIP 2027 两个实战节点。

## 页面结构

| 页面 | 内容 |
|---|---|
| `index.html` | 总览：三条硬结论、六阶段路线、知识分布、起点与终点 |
| `plan.html` | 56 周逐周任务表，可按阶段筛选、勾选打卡（localStorage） |
| `syllabus.html` | NOI 大纲 2025 修订版 10 个难度级全量条目 + 2025 年变化 |
| `books.html` | CCF 官方出版物 6 类、经典教材 13 本、在线平台 12 个 |
| `problems.html` | 题单：由本地 `CSP-JS+NOI 题单.xlsx` 重构，含题量分配模型 |
| `templates.html` | 56 个 C++ 模板，标注等级、复杂度、易错点，一键复制 |
| `contests.html` | 七级漏斗、2026–2028 赛历、六个高频疑问直答 |
| `assess.html` | 能力雷达、9 个里程碑阈值、周自检七问、评分表、止损线 |
| `resources.html` | C/D/E 三盘扫描结果、14 个 GitHub 仓库、资料使用地图 |
| `method.html` | 刻意练习闭环、对拍工程、考场时间分配、七个失败模式 |

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

```
.
├── index.html
├── plan.html
├── syllabus.html
├── books.html
├── problems.html
├── templates.html
├── contests.html
├── assess.html
├── resources.html
├── method.html
├── .nojekyll
└── assets
    ├── css/main.css
    └── js
        ├── app.js
        └── data/*.js
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

---

*本计划基于 CCF NOI 大纲（2025 年修订版）编制。赛历与规则以官方当年通知为准。*
