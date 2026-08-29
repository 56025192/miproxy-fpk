# mihomo-fpk

飞牛 NAS (fnOS) 上的 Mihomo 代理核心 FPK 应用包。

## 功能特性

- 🌐 **支持主流代理协议**：Shadowsocks (SIP002)、ShadowsocksR、Snell、V2Ray (VMess/VLESS)、Trojan、Tuic、Hysteria2 等
- 🎨 **双控制面板**：Zashboard（推荐）和 MetaCubeXD
- 📦 **订阅管理**：支持远程订阅 URL 和本地订阅文件
- 🔄 **自动刷新**：可配置自动刷新订阅间隔（1/6/12/24 小时）
- 🌐 **局域网共享**：允许局域网设备通过本机代理端口上网
- 🔒 **安全配置**：支持 API 密钥认证
- 📊 **灵活模式**：规则模式 / 全局模式 / 直连模式
- 🗃️ **离线 GEO**：内置 GEO 数据库，无需联网下载

## 安装

1. 在 fnOS 应用中心下载 FPK 文件
2. 安装时配置控制面板和订阅

## 配置文件位置

- `/vol1/@appdata/mihomo/config.yaml` - mihomo 主配置
- `/vol1/@appdata/mihomo/subscription.yaml` - 订阅配置
- `/vol1/@appdata/mihomo/info.log` - 运行日志

## 版本历史

- **v2.0.3** - 稳定版本，控制面板切换、订阅管理、自动刷新

## 免责声明

本应用仅提供技术实现，使用者需自行承担使用风险。
