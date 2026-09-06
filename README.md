# MiProxy

<div align="center">

![Logo](https://img.shields.io/badge/MiProxy-mihomo-blue?style=for-the-badge)
[![GitHub Release](https://img.shields.io/github/v/release/56025192/miproxy-fpk?style=for-the-badge)](https://github.com/56025192/miproxy-fpk/releases)
[![Download](https://img.shields.io/github/downloads/56025192/miproxy-fpk/total?style=for-the-badge)](https://github.com/56025192/miproxy-fpk/releases)
[![License](https://img.shields.io/github/license/56025192/miproxy-fpk?style=for-the-badge)](LICENSE)

**基于 [mihomo](https://github.com/MetaCubeX/mihomo) 内核的飞牛 fnOS 代理应用**

</div>

---

## 功能特性

| 特性 | 说明 |
|------|------|
| 🌐 **多协议支持** | VMess / VLess / Trojan / Shadowsocks / Hysteria2 等主流代理协议 |
| 🎛️ **双控制面板** | Zashboard（现代简洁）/ MetaCubeXD（功能全面），安装时自由选择 |
| 🔄 **订阅管理** | 支持远程订阅 URL 和本地配置文件，自动定时刷新 |
| 📊 **GEO 数据库** | 内置 GeoIP / GeoSite / MMDB，开箱即用 |
| 🔒 **安全隔离** | 依托 fnOS 权限体系，配置数据安全存储 |
| 🌐 **局域网共享** | 支持局域网设备通过本机代理上网 |

> ⚠️ **兼容性说明**：目前仅支持 Clash 格式订阅链接。

---

## 快速开始

### 安装

1. 从 [Releases](https://github.com/56025192/miproxy-fpk/releases/latest) 下载最新 `.fpk` 安装包
2. 登录 fnOS → **应用中心** → **安装本地应用** → 上传 `.fpk` 文件
3. 按向导完成安装，选择控制面板风格

### 配置订阅

1. 进入 **MiProxy** 控制面板
2. 在「订阅管理」中添加订阅链接或选择本地配置文件
3. 设置自动刷新间隔（建议 6-12 小时）
4. 点击刷新，同步节点列表

---

## 目录结构

\`\`\`
miproxy-fpk/
├── manifest              # FPK 应用清单
├── cmd/                  # 生命周期脚本
│   ├── main.sh           # 启动/停止
│   ├── install_callback.sh
│   ├── config_callback.sh
│   ├── upgrade_callback.sh
│   ├── uninstall_callback.sh
│   └── refresh_subscription_loop.sh  # 订阅刷新守护进程
├── config/               # fnOS 配置
│   ├── privilege
│   └── resource
├── wizard/               # 安装向导
│   ├── config
│   ├── install
│   └── uninstall
├── app/
│   ├── server/           # mihomo 核心
│   ├── data/            # GEO 数据库
│   └── ui/              # 控制面板前端
└── README.md
\`\`\`

---

## 配置文件

| 文件 | 路径 | 用途 |
|------|------|------|
| 主配置 | `/vol1/@appdata/miproxy/config.yaml` | mihomo 完整配置 |
| 基础配置 | `/vol1/@appdata/miproxy/base.yaml` | 基础运行参数 |
| 订阅配置 | `/vol1/@appdata/miproxy/subscription.yaml` | 订阅链接列表 |
| 运行日志 | `/vol1/@appdata/miproxy/info.log` | 应用运行日志 |

---

## 更新日志

### v2.6.38
- ✨ 新增控制面板选择页面，安装时可自由选择 Zashboard 或 MetaCubeXD
- 🔧 优化订阅解析逻辑

### v2.6.37
- 🐛 修复 cmd 目录路径问题

### v2.6.36
- ♻️ 重构 refresh_sub，摆脱脚本路径依赖

[查看全部更新](https://github.com/56025192/miproxy-fpk/releases)

---

## 技术栈

- **内核**：[mihomo](https://github.com/MetaCubeX/mihomo) (MetaCubeX)
- **前端**：[Zashboard](https://github.com/Zephyruso/zashboard) / [MetaCubeXD](https://github.com/MetaCubexD/MetaCubeXD)
- **平台**：飞牛 fnOS (≥1.1.0)
- **格式**：FPK (tar 打包)

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=56025192/miproxy-fpk&type=Date)](https://star-history.com/#56025192/miproxy-fpk&Date)

---

## 许可证

本项目仅供学习交流使用，请遵守当地法律法规。

---

<p align="center">
  <a href="https://github.com/56025192">👤 作者主页</a> ·
  <a href="https://github.com/56025192/miproxy-fpk/issues">🐛 问题反馈</a> ·
  <a href="https://github.com/56025192/miproxy-fpk/releases">📦 下载地址</a>
</p>

