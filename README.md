# MiProxy

<div align="center">

![Logo](https://img.shields.io/badge/MiProxy-mihomo-blue?style=for-the-badge)
[![GitHub Release](https://img.shields.io/github/v/release/56025192/miproxy-fpk?style=for-the-badge)](https://github.com/56025192/miproxy-fpk/releases)
[![Download](https://img.shields.io/github/downloads/56025192/miproxy-fpk/total?style=for-the-badge)](https://github.com/56025192/miproxy-fpk/releases)
[![License](https://img.shields.io/github/license/56025192/miproxy-fpk?style=for-the-badge)](LICENSE)

**把飞牛 NAS 变成你的私人代理网关**

基于 [mihomo](https://github.com/MetaCubeX/mihomo) 内核，一键开启 TUN 全局代理，订阅自动更新，流量完全私有

</div>

---

> 还在为每台设备单独配置代理烦恼？一台永不离线的 NAS，就是你最稳定的代理节点。

---

## 为什么是 MiProxy

| 痛点 | MiProxy 的答案 |
|------|---------------|
| 手机、电脑、TV 每台都要配代理 | **TUN 模式**接管全局，所有设备零配置联网 |
| 订阅节点经常失效要手动更新 | **自动定时刷新**，睡一觉醒来自动同步最新节点 |
| 云服务贵、第三方节点不稳 | **自建代理网关**，NAS 24 小时开着，节点自己选 |
| 流量经过第三方，数据不放心 | **流量完全私有**，经过你自己的磁盘再出去 |

---

## 功能特性

- **TUN 全局代理** — 开启后整个局域网设备流量自动走代理，无需逐台配置
- **订阅自动更新** — 支持远程订阅 URL / 本地配置文件，可设 1-24 小时自动刷新
- **双控制面板** — [Zashboard](https://github.com/Zephyruso/zashboard)（极简现代）/ [MetaCubeXD](https://github.com/MetaCubexD/MetaCubeXD)（功能全面），安装时任选
- **全协议支持** — VMess / VLESS / Trojan / Shadowsocks / Hysteria2 等主流代理协议
- **智能路由** — 内置 GeoIP / GeoSite / MMDB 数据库，国内外流量自动分流
- **DNS 防泄露** — 启用 strict-route，DnS 请求完全由代理处理，无泄露风险
- **TUN 参数可调** — 可在安装向导中选择开启/关闭 TUN 模式

---

## 系统要求

| 项目 | 要求 |
|------|------|
| fnOS 版本 | ≥ 1.1.0 |
| 架构 | x86_64 / arm64 |
| 安装包大小 | ~35 MB |
| 运行内存 | 建议 ≥ 512MB |

---

## 快速开始

### 1. 安装

从 [Releases](https://github.com/56025192/miproxy-fpk/releases/latest) 下载对应架构的 `.fpk` 文件，登录 fnOS → **应用中心** → **安装本地应用** → 上传文件，按向导完成安装。

### 2. 配置订阅

安装完成后进入控制面板（默认 `http://NAS_IP:9090`），在「订阅管理」中粘贴订阅链接或上传本地配置文件，点击刷新即可同步节点。

### 3. 开启 TUN 模式（可选）

在向导中选择开启 TUN 模式，NAS 将接管局域网所有设备的代理流量，无需在每台设备上配置代理地址。

---

## 代理端口说明

| 端口 | 协议 | 用途 |
|------|------|------|
| 7890 | HTTP | HTTP/HTTPS 代理，手动代理时使用 |
| 9090 | HTTP | 控制面板 API |

---

## 项目结构

```
miproxy-fpk/
├── app/
│   ├── server/          # mihomo 内核
│   ├── data/            # GeoIP / GeoSite / Country.mmdb
│   └── ui/              # Zashboard + MetaCubeXD 双面板
├── cmd/
│   ├── main             # 启停管理脚本
│   ├── install_callback  # 安装后配置生成
│   └── refresh_sub       # 订阅刷新守护进程
├── config/
│   └── privilege         # 权限声明（root 权限运行 TUN）
└── wizard/              # 安装向导
```

---

## 更新日志

### v2.7.0
- ⚡ **TUN 配置全面优化**：`strict-route` 防止 DNS 泄露、`gso` 吞吐性能提升、网卡名固定为 `miproxy`
- 🛡️ **新增升级日志文件**：`upgrade_init.log` / `upgrade_callback.log`，升级过程可独立追踪
- 🔧 **日志模块重构**：分离 mihomo 重启日志（写入 `info.log`）与订阅刷新记录（写入 `refresh_sub.log`），避免日志混杂
- 🐛 修复 mihomo 重启日志与订阅刷新日志混写问题
- 🐛 修复 echo 语句语法错误导致的日志记录失败
- 🐛 修复 `refresh_sub` 中重复定义 `MIHOMO_LOG` 变量问题
- 🔄 自动同步 mihomo / 前端最新二进制文件
- 📖 全面重写 README，突出 TUN 全局代理 + NAS 私有网关核心价值

### v2.6.39
- 🛡️ TUN 配置全面优化：新增 `strict-route` 防 DNS 泄露、`gso` 吞吐优化、网卡命名固定为 `miproxy`
- 🐛 修复订阅节点提取失败问题（heredoc bug）
- 🐛 修复 mihomo 二进制路径错误导致启动失败

### v2.6.38
- ✨ 新增控制面板选择页面，安装时自由选择 Zashboard 或 MetaCubeXD

[查看全部版本](https://github.com/56025192/miproxy-fpk/releases)


---

## 技术栈

- **代理内核**：[mihomo](https://github.com/MetaCubeX/mihomo) by MetaCubeX
- **控制面板**：[Zashboard](https://github.com/Zephyruso/zashboard) / [MetaCubeXD](https://github.com/MetaCubexD/MetaCubeXD)
- **运行环境**：飞牛 fnOS ≥ 1.1.0

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=56025192/miproxy-fpk&type=Date)](https://star-history.com/#56025192/miproxy-fpk&Date)

---

## 许可证

本项目仅供学习交流使用，请遵守当地法律法规。

---

<p align="center">
  <a href="https://github.com/56025192">👤 作者</a> ·
  <a href="https://github.com/56025192/miproxy-fpk/releases">📦 下载</a> ·
  <a href="https://github.com/56025192/miproxy-fpk/issues">🐛 问题反馈</a>
</p>
