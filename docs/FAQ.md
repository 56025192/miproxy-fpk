# 常见问题 FAQ

<details>
<summary><b>Q1: 安装后无法打开控制面板？</b></summary>

**A:** 检查以下几点：
1. 确认 MiProxy 服务已启动（fnOS 应用管理中查看状态）
2. 检查端口是否被占用（默认 9090）
3. 尝试清除浏览器缓存后重试
4. 检查防火墙设置

</details>

<details>
<summary><b>Q2: 订阅链接解析失败？</b></summary>

**A:** 
- 确认订阅链接是 **Clash 格式**
- 检查订阅链接是否需要认证（Token/密码）
- 尝试在浏览器中直接打开订阅链接
- 部分机场订阅有验证码，请手动更新

</details>

<details>
<summary><b>Q3: TUN 模式无法启用？</b></summary>

**A:**
- TUN 需要内核支持，fnOS 环境下可能不可用
- 建议关闭 TUN，使用普通代理模式
- 普通模式已能满足大多数使用场景

</details>

<details>
<summary><b>Q4: 节点延迟很高/无法连接？</b></summary>

**A:**
1. 在控制面板中测试各节点延迟
2. 切换到延迟更低的节点
3. 检查本地网络环境
4. 尝试更换订阅源

</details>

<details>
<summary><b>Q5: 自动刷新不生效？</b></summary>

**A:**
1. 确认已开启自动刷新（设置间隔 > 0）
2. 检查日志文件 `/vol1/@appdata/miproxy/info.log`
3. 确认订阅类型为"远程订阅 URL"
4. 手动点击刷新测试

</details>

<details>
<summary><b>Q6: 如何卸载 MiProxy？</b></summary>

**A:**
1. 在 fnOS 应用中心停止 MiProxy
2. 点击卸载
3. 用户数据（如需保留）位于 `/vol1/@appdata/miproxy/`
4. 卸载后配置文件夹不会自动删除

</details>

<details>
<summary><b>Q7: 面板密钥是什么？和代理密码有什么区别？</b></summary>

**A:**
| 密钥类型 | 用途 | 设置位置 |
|----------|------|----------|
| 面板密钥 | 访问控制面板的密码 | 安装向导 / 配置向导 |
| 代理密码 | 连接代理服务器的用户名/密码 | 安装向导 / 配置向导 |

- 面板密钥：访问 Dashboard 时输入
- 代理密码：浏览器/软件连接代理时输入

</details>

<details>
<summary><b>Q8: 支持哪些代理协议？</b></summary>

**A:**
MiProxy 基于 mihomo 内核，支持以下协议：
- VMess
- VLESS
- Trojan
- Shadowsocks (ss)
- Shadowsocks 2022 (ss2022)
- Hysteria / Hysteria2
- WireGuard
- Tuic

> ⚠️ 订阅必须为 Clash 格式

</details>

<details>
<summary><b>Q9: 如何更新 MiProxy？</b></summary>

**A:**
1. 前往 [Releases](https://github.com/56025192/miproxy-fpk/releases) 下载新版 FPK
2. 在 fnOS 应用中心上传新版本
3. 升级过程中配置不会丢失
4. 建议升级前备份重要配置

</details>

<details>
<summary><b>Q10: GEO 数据库是什么？</b></summary>

**A:**
| 文件 | 用途 |
|------|------|
| Country.mmdb | IP 地理位置数据库，用于分流 |
| geosite.dat | 域名规则数据库，分流规则依赖此文件 |
| geoip.dat | IP 规则数据库（GeoIP） |

GEO 数据库用于实现智能分流，如"大陆常用网站直连，海外网站走代理"。

</details>

---

*还有其他问题？[提交 Issue](https://github.com/56025192/miproxy-fpk/issues)*

