---
tags:
  - 网络安全
  - 渗透测试
  - BurpSuite
created: 2026-08-15
updated: 2026-08-15
---

# Burp Suite 渗透测试工具

> Burp Suite Professional 版本，含 JDK 21 环境、汉化补丁、激活工具。

## 文件位置

**原始路径：** `C:\Users\Administrator\Desktop\总文件夹\资料整合\Burpsuite\`

## 包含内容

| 文件 | 说明 |
|------|------|
| burpsuite_pro.jar | Burp Suite Pro 主体程序 |
| BurpLoaderKeygen.jar | 加载器与注册机 |
| BurpSuiteLoader.jar | Burp Suite 加载器 |
| jdk-21.0.3/ | JDK 21 运行环境 |
| BurpSuite-cn.vbs | 中文汉化启动脚本 |
| BurpSuite.vbs | 英文启动脚本 |
| start.bat | 启动批处理 |
| start-cn.bat | 中文启动批处理 |
| keygen.bat | 注册机批处理 |
| reset_license.bat | 重置许可证批处理 |
| Config_yaml.yaml | 配置文件 |
| BurpSuite.ico | 程序图标 |
| log/ | 日志目录 |

## 使用方法

1. 确保已安装 JDK 21（路径内自带 `jdk-21.0.3`）
2. 运行 `keygen.bat` 生成许可证
3. 使用 `start-cn.bat` 启动中文版 或 `start.bat` 启动英文版
4. 如需重置许可证，运行 `reset_license.bat`

## 功能概述

- **代理抓包**：拦截和修改 HTTP/HTTPS 请求
- **漏洞扫描**：自动检测 Web 应用安全漏洞
- **Intruder**：暴力破解与自动化攻击
- **Repeater**：手动重发和修改请求
- **Decoder**：编码解码工具
- **Comparer**：响应比对工具
- **Sequencer**：随机性分析工具

---

## 相关笔记

- [[网络安全工具]] — 网安工具与漏洞库总览
- [[360系统急救箱]] — 系统修复与病毒急救
- [[机器学习数据集]] — VOC/YOLO 数据集
- [[激光切割课件]] — 激光切割技术教学
- [[Mixly源代码]] — 图形化编程项目

---
  - 分类/编程网安
> **注意：** 此工具仅用于授权的安全测试与学习研究。请遵守相关法律法规。