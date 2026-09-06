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
| 🔑 **认证保护** | 支持面板密钥和代理密码双重保护 |

---

## 系统要求

| 项目 | 要求 |
|------|------|
| fnOS 版本 | ≥ 1.1.0 |
| 存储空间 | 约 100MB（不含 GEO 数据） |
| 内存 | 建议 ≥ 1GB |
| 架构 | x86_64 / arm64 |

---

## 快速开始

### 安装

1. 从 [Releases](https://github.com/56025192/miproxy-fpk/releases/latest) 下载最新 `.fpk` 安装包
2. 登录 fnOS → **应用中心** → **安装本地应用** → 上传 `.fpk` 文件
3. 按向导完成安装，选择控制面板风格

### 配置订阅

1. 进入 **MiProxy** 控制面板（默认地址：`http://NAS_IP:9090`）
2. 在「订阅管理」中添加订阅链接或选择本地配置文件
3. 设置自动刷新间隔（建议 6-12 小时）
4. 点击刷新，同步节点列表

### 配置浏览器代理

**SOCKS5 代理：**
- 服务器：`NAS_IP`
- 端口：`7891`

**HTTP 代理：**
- 服务器：`NAS_IP`
- 端口：`7890`

---

## 文档中心

📖 完整文档已迁移至 [GitHub Wiki](https://github.com/56025192/miproxy-fpk/wiki)：

- [📖 使用指南](https://github.com/56025192/miproxy-fpk/wiki/使用指南) - 控制面板详细操作说明
- [❓ 常见问题](https://github.com/56025192/miproxy-fpk/wiki/常见问题) - 常见问题解答
- [🔧 故障排查](https://github.com/56025192/miproxy-fpk/wiki/故障排查) - 问题诊断与解决方案

---

## 项目结构

```
.
├── .github/                    # GitHub Actions CI/CD 配置
│   └── workflows/
│
├── app/                        # 应用运行时目录
│   ├── server/                 # mihomo 核心程序
│   ├── data/                   # GEO 数据库 (GeoIP/GeoSite/MMDB)
│   │   ├── Country.mmdb       # IP 地理位置数据库
│   │   ├── geoip.dat          # GeoIP 数据
│   │   └── geosite.dat        # 域名规则数据库
│   └── ui/                     # 前端界面
│       ├── zashboard/          # 现代风格控制面板
│       ├── metacubexd/         # 经典风格控制面板
│       └── index.html          # 面板选择页面
│
├── cmd/                        # 生命周期脚本
│   ├── main                    # 启动/停止主脚本
│   ├── install_callback        # 安装完成回调
│   ├── install_init            # 安装初始化
│   ├── config_callback         # 配置变更回调
│   ├── config_init             # 配置初始化
│   ├── upgrade_callback        # 升级完成回调
│   ├── upgrade_init            # 升级初始化
│   ├── uninstall_callback      # 卸载回调
│   ├── uninstall_init          # 卸载初始化
│   └── refresh_sub             # 订阅刷新守护进程
│
├── config/                     # fnOS 系统配置
│   ├── privilege               # 权限声明
│   └── resource                # 资源配额
│
├── wizard/                     # 安装向导
│   ├── install                 # 安装向导脚本
│   ├── config                  # 配置向导脚本
│   └── uninstall               # 卸载向导脚本
│
├── manifest                    # FPK 应用清单
├── ICON.PNG                    # 应用图标
├── ICON_256.PNG                # 高清图标
└── README.md                   # 项目文档
```

---

## 配置文件

| 文件 | 路径 | 用途 |
|------|------|------|
| 主配置 | `/vol1/@appdata/miproxy/config.yaml` | mihomo 完整配置 |
| 基础配置 | `/vol1/@appdata/miproxy/base.yaml` | 基础运行参数 |
| 订阅配置 | `/vol1/@appdata/miproxy/subscription.yaml` | 订阅链接列表 |
| 运行日志 | `/vol1/@appdata/miproxy/info.log` | 应用运行日志 |
| 刷新日志 | `/vol1/@appdata/miproxy/refresh_sub.log` | 订阅刷新记录 |

---

## 代理端口说明

| 端口 | 协议 | 用途 |
|------|------|------|
| 7890 | HTTP | HTTP/HTTPS 代理 |
| 7891 | SOCKS5 | SOCKS5 代理（支持 UDP） |
| 9090 | HTTP | 控制面板 API |

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
  <a href="https://github.com/56025192/miproxy-fpk/releases">📦 下载地址</a> ·
  <a href="https://github.com/56025192/miproxy-fpk/wiki">📖 Wiki</a>
</p>

