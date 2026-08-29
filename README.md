# miproxy-fpk

飞牛 NAS (fnOS) 上的 Mihomo 代理核心 FPK 应用包。

## 功能特性

- 🌐 **支持主流代理协议**：Shadowsocks、VMess、Trojan、Shadowsocks 等
- 🎨 **双控制面板**：Zashboard（推荐）和 MetaCubeXD
- 📦 **订阅管理**：支持远程订阅 URL 和本地订阅文件
- 🔄 **自动刷新**：可配置自动刷新订阅间隔
- 🌐 **局域网共享**：允许局域网设备通过本机代理端口上网
- 🗃️ **离线 GEO**：内置 GEO 数据库，无需联网下载

## 安装

### 方式一：直接下载 FPK（推荐）

在 [Releases](https://github.com/56025192/miproxy-fpk/releases) 页面下载 `mihomo-v2.0.3.fpk`，在 fnOS 应用中心上传安装。

### 方式二：从源码构建

1. 克隆仓库
```bash
git clone https://github.com/56025192/miproxy-fpk.git
cd miproxy-fpk
```

2. 下载 mihomo 二进制
```bash
curl -L -o app/server/miproxy https://github.com/MetaCubeX/mihomo/releases/download/v1.19.30/mihomo-linux-amd64-v1.19.30.gz
gunzip app/server/miproxy
chmod +x app/server/miproxy
```

3. 打包 FPK
```bash
fnpack build .
```

## 配置文件位置

- `/vol1/@appdata/miproxy/config.yaml` - 主配置
- `/vol1/@appdata/miproxy/subscription.yaml` - 订阅配置
- `/vol1/@appdata/miproxy/info.log` - 运行日志

## 版本历史

- **v2.0.3** - 稳定版本

## 免责声明

本应用仅提供技术实现，使用者需自行承担使用风险。
