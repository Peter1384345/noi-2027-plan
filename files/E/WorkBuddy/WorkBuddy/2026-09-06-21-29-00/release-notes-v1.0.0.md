## CSP-S 第一轮备考全攻略 v1.0.0

面向 CSP-S（提高级）第一轮认证（笔试）的一站式备考站。**零依赖、单文件、本地运行**——下载后双击 `index.html` 即可使用，断网也不受影响。

### 内容

**真题资料（`papers/`，10 个文件）**

- 2021–2024 第一轮真题 PDF 及参考答案
- 2025 第一轮试题及答案（社区整理版 .md）
- 《CSP 第一轮复习资料》45 页（认证形式、题型、大纲、分章节题库）
- CSP-S1 初赛备考指南与答题技巧

**备考站功能（`index.html`，12 个板块）**

- 在线刷题：内嵌 30 道真题单选（2024–2025 全部），即时判分
- 三段式深度题解：考点定位 / 解题过程 / 易错提醒
- 错题本 + 学习统计（localStorage 持久化，按考点统计正确率）
- 限时模考：20 分钟倒计时，交卷判分并折算 30 分制
- 考点频次：2021–2025 共 75 道选择题逐题统计，T0/T1/T2 三级优先级
- 阅读程序六大代码模式、完善程序五大算法家族
- 两轮认证对比：第一轮笔试 vs 第二轮上机所需能力清单
- 学习路线（100/200/300+/AK 分层）与学习方法论
- 冲刺计划与考场 120 分钟作战守则

### 使用方式

```bash
git clone https://github.com/Peter1384345/csp-s-first-round.git
# 双击 index.html 即可
```

在线浏览：仓库 Settings → Pages → Deploy from a branch → `main` / `/ (root)` → Save，约 1 分钟后访问 `https://peter1384345.github.io/csp-s-first-round/`。

### 数据来源与版权

CCF 官方不公开发行初赛试题，`papers/` 下 2021–2024 为社区电子重排版、2025 为民间回忆整理版，来源 [mingyush/csp](https://github.com/mingyush/csp) 与 [winterant/oi](https://github.com/winterant/oi)。试题版权归 CCF 及原整理者所有，仅供备考学习交流。

页面设计参考 [csppass.com](https://www.csppass.com/)，题解范式参考 [cspfirstround.com](https://www.cspfirstround.com/)，学习路线参考 [csp.wiki](https://csp.wiki/docs/CSP-S)。

代码与文档采用 MIT 许可证。
