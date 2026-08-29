# MiProxy

基于 [mihomo](https://github.com/MetaCubeX/mihomo) 的飞牛 NAS (fnOS) FPK 应用。

## 功能特性

- 🌐 **多协议支持**：VMess、VLess、Trojan、Shadowsocks、Hysteria2 等
- 🎛️ **双控制面板**：Zashboard（现代化）/ MetaCubeXD（经典）
- 🔄 **订阅管理**：支持远程 URL 和本地文件订阅
- ⏰ **自动刷新**：可配置自动刷新间隔
- 🌐 **局域网共享**：支持局域网代理
- 📦 **离线 GEO**：内置 GEO 数据库，开箱即用

## 安装

1. 从 [Releases](https://github.com/56025192/miproxy-fpk/releases) 下载 `.fpk` 文件
2. 在 fnOS 应用中心上传安装

## 配置

安装向导中可配置：
- 控制面板选择
- 订阅来源（远程 URL 或本地文件）
- 自动刷新间隔

## 文件结构

```
miproxy-fpk/
├── manifest          # FPK 应用清单
├── cmd/
│   ├── main.sh                    # 启动/停止脚本
│   ├── install_callback.sh        # 安装回调
│   ├── config_callback.sh         # 配置更新回调
│   ├── upgrade_callback.sh        # 升级回调
│   ├── uninstall_callback.sh      # 卸载回调
│   ├── merge_config.py           # 配置合并脚本
│   └── refresh_subscription_loop.sh  # 订阅刷新守护进程
├── config/
│   ├── privilege    # 权限配置
│   └── resource     # 资源配额
├── wizard/
│   ├── config       # 设置向导
│   ├── install      # 安装向导
│   └── uninstall    # 卸载向导
├── app/
│   ├── server/      # mihomo 核心
│   ├── data/        # GEO 数据库
│   └── ui/         # 控制面板
└── README.md
```

## 配置文件位置

- 主配置：`/vol1/@appdata/miproxy/config.yaml`
- 基础配置：`/vol1/@appdata/miproxy/base.yaml`
- 订阅配置：`/vol1/@appdata/miproxy/subscription.yaml`
- 日志：`/vol1/@appdata/miproxy/info.log`

## 版本历史

- **v2.1.6** - 代码优化与清理
  - 修复 refresh_subscription_loop.sh 硬编码路径
  - 移除不必要的 shares 配置
  
- **v2.1.5** - 修复配置合并问题
  - 修复 install_callback 中 merge_config.py 路径问题
  
- **v2.1.4** - 初始稳定版

## License

MIT License
