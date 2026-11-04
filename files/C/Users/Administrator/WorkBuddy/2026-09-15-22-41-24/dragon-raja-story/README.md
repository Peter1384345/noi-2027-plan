# Dragon Raja Story

> 龙族全系列剧情与人物关系可视化网页

![License](https://img.shields.io/badge/license-MIT-blue)
![Status](https://img.shields.io/badge/status-active-brightgreen)

## 项目简介

「龙族」系列小说剧情梳理与人物关系可视化网站。通过交互式关系图谱和时间线，展现龙族世界中错综复杂的人物关系与剧情脉络。

## 在线访问

**GitHub Pages:** https://peter1384345.github.io/dragon-raja-story/

## 功能特色

- 🕸️ **人物关系图谱** — 基于 ECharts 的交互式力导向图，直观展示角色关系网络
- 📖 **全系列剧情梳理** — 按册/按部整理剧情脉络与关键事件
- 🎭 **角色档案** — 主要人物详细信息与出场作品
- 🔍 **关系探索** — 悬停高亮、点击详情、多层关系追溯
- 🎨 **沉浸式界面** — 龙族世界观风格的视觉设计

## 技术实现

- 多页面纯前端实现，按主题拆分（人物 / 剧情 / 世界观 / 图鉴 / 命运 / 探索台）
- 共享样式与脚本（`_shared/`），各页面按需加载 ECharts
- **ECharts** 关系图可视化（CDN 加载）
- **Mermaid** 流程图与时间线
- 响应式布局，支持桌面与移动端

## 项目结构

`
dragon-raja-story/
├── index.html          # 首页（六大主题页导航）
├── characters.html     # 人物篇：关系图谱 / 角色详情 / 战力对比
├── story.html          # 剧情篇：分卷剧情 / 卷次强度 / 经典战役 / 时间线
├── world.html          # 世界观篇：设定 / 炼金术 / 势力 / 龙王 / 家族 / 武器
├── moments.html        # 图鉴篇：经典场景 / 语录 / 彩蛋
├── fate.html           # 命运篇：血统评级 / 角色命运 / 命运流向
├── explore.html        # 探索台 V2：羁绊矩阵 / 阅读时间轴 / 抉择树 / 台词抽签
├── _shared/css/site.css# 全站共享样式
├── _shared/js/page.js  # 全站共享脚本（语录池 / 更新系统）
├── _shared/js/         # 共享库（ECharts / Mermaid 本地兜底）
├── assets/             # 图片与图表脚本 charts.js
├── .nojekyll           # GitHub Pages 禁用 Jekyll
└── vercel.json         # Vercel 部署配置
`

## 本地预览

直接用浏览器打开 index.html 即可。

或使用本地静态服务器：

`ash
npx serve .
`

## 部署

- **GitHub Pages** — 自动从 main 分支根目录部署
- **Vercel** — 已配置 ercel.json，导入项目即可部署

## 相关作品

「龙族」系列小说作者：江南

> 本项目为粉丝向剧情梳理与人物关系整理，仅供学习交流使用。
> 小说版权归原作者所有。

## License

[MIT](LICENSE)