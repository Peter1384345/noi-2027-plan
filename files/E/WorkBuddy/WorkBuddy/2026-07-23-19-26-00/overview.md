# 龙卷风科普视频生成 — 完成总结

## 交付物

- **成片视频**：`C:\Users\Administrator\WorkBuddy\2026-07-23-19-26-00\remotion-videos\out\tornado-video.mp4`
- **规格**：H.264 / 1920×1080 / 30fps / 6900 帧 / 3 分 50 秒 / 57.2 MB
- **来源脚本**：`C:\Users\Administrator\Desktop\龙卷风科普视频脚本.docx`（汕头市科普大赛，5 幕结构）

## 做了什么

1. **解析脚本**：从 docx 提取出约 3 分 50 秒、5 幕结构的龙卷风科普脚本。
2. **搭建项目**：在 `remotion-videos/` 下创建 Remotion + React + TypeScript 项目，安装依赖并修复环境障碍。
3. **代码实现**：
   - `theme.ts`：深蓝风暴配色、本地系统字体栈
   - `ui.tsx`：共用卡片、数据滚动、SVG 漏斗、柱状图等组件
   - `Scene1~5.tsx`：5 幕视觉内容（震撼开场 / 成因 / 破坏力 / 自救 / 结尾呼吁）
   - `VideoComposition.tsx`：总合成与时间线
4. **AI B-roll**：用 AI 生成两段龙卷风氛围空镜，嵌入场头（龙卷风漏斗接地）和结尾（风暴乌云闪电）。
5. **渲染输出**：成功渲染完整 6900 帧 MP4。

## 关键环境修复

| 问题 | 解决方案 |
|------|---------|
| FFmpeg 缺失 | winget 安装 FFmpeg 8.1.2，渲染时通过环境变量指向本地二进制 |
| `@remotion/lucide-icons` 包不存在 | 改为 `lucide-react@1.26.0` |
| npm peer 依赖冲突 | 使用 `--legacy-peer-deps` |
| npm 缓存索引被锁/安装中断 | 清全局缓存，改用 `--cache=$PWD/.npmcache` 项目本地缓存，失败后 `npm rebuild` 修复 bin 链接 |
| Google Fonts 联网加载超时 | 改用本地系统字体栈（优先微软雅黑），避免渲染时联网 |
| Remotion 浏览器下载后删除临时包被沙箱拦截 | `remotion.config.ts` 中 `setBrowserExecutable` 指向已下载的 chrome-headless-shell 绝对路径 |

## 后续可选项

- 添加 TTS 解说配音
- 添加背景音乐（版权友好素材）
- 根据投放平台改为 9:16 竖屏或 1:1 方形版本
- 用更多 AI 生成空镜替换/补充中间转场
