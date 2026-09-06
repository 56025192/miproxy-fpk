# 故障排查手册

## 日志文件位置

| 文件 | 路径 | 说明 |
|------|------|------|
| 运行日志 | `/vol1/@appdata/miproxy/info.log` | 应用运行状态 |
| 刷新日志 | `/vol1/@appdata/miproxy/refresh_sub.log` | 订阅刷新记录 |
| mihomo 日志 | 标准输出/错误输出 | mihomo 核心日志 |

**查看日志命令：**
\`\`\`bash
# 查看运行日志
cat /vol1/@appdata/miproxy/info.log

# 实时查看日志
tail -f /vol1/@appdata/miproxy/info.log

# 查看订阅刷新日志
cat /vol1/@appdata/miproxy/refresh_sub.log
\`\`\`

---

## 常见问题排查

### 1. 服务无法启动

**症状：** 应用状态显示"已停止"，无法启动

**排查步骤：**

1. 检查日志
   \`\`\`bash
   cat /vol1/@appdata/miproxy/info.log
   \`\`\`

2. 常见错误及解决方案：

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `mihomo not found` | mihomo 二进制文件丢失 | 重新安装应用 |
| `config.yaml not found` | 配置文件不存在 | 检查配置或重新安装 |
| `port already in use` | 端口被占用 | 修改端口或关闭占用程序 |
| `permission denied` | 权限不足 | 检查文件权限 |

3. 检查配置文件语法
   \`\`\`bash
   # 备份配置
   cp /vol1/@appdata/miproxy/config.yaml /vol1/@appdata/miproxy/config.yaml.bak
   
   # 验证 YAML 语法
   python3 -c "import yaml; yaml.safe_load(open(/vol1/@appdata/miproxy/config.yaml))"
   \`\`\`

---

### 2. 订阅刷新失败

**症状：** 订阅链接无法解析 / 节点列表为空

**排查步骤：**

1. 确认订阅类型已设置为"远程订阅 URL"

2. 测试订阅链接
   \`\`\`bash
   curl -fsSL "你的订阅链接" -o /tmp/test_sub.yaml
   cat /tmp/test_sub.yaml
   \`\`\`

3. 常见问题：

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 403 Forbidden | 订阅被限制 | 添加 Referer 或 User-Agent |
| 404 Not Found | 链接错误 | 检查订阅地址 |
| Base64 解码失败 | 订阅非 Base64 编码 | 联系订阅提供商 |
| 空文件 | 订阅无效 | 更换订阅源 |

4. 检查刷新日志
   \`\`\`bash
   cat /vol1/@appdata/miproxy/refresh_sub.log
   \`\`\`

---

### 3. 控制面板无法访问

**症状：** 浏览器无法打开控制面板

**排查步骤：**

1. 确认服务正在运行
   \`\`\`bash
   # 检查进程
   ps aux | grep mihomo
   
   # 检查端口
   netstat -tlnp | grep 9090
   \`\`\`

2. 检查防火墙
   \`\`\`bash
   # 检查 9090 端口是否开放
   iptables -L -n | grep 9090
   \`\`\`

3. 从本地测试
   \`\`\`bash
   curl http://localhost:9090
   \`\`\`

4. 检查外部访问
   \`\`\`bash
   # 在其他设备上测试
   curl http://NAS_IP:9090
   \`\`\`

---

### 4. 代理无法连接

**症状：** 配置了代理但无法上网

**排查步骤：**

1. 确认代理端口
   \`\`\`bash
   # 默认代理端口 7890，检查 config.yaml 中的 port 配置
   grep "^port:" /vol1/@appdata/miproxy/config.yaml
   \`\`\`

2. 检查代理协议
   - 浏览器推荐使用 SOCKS5 或 HTTP 代理
   - 测试工具推荐使用 `curl`
   \`\`\`bash
   # 测试代理
   curl -x socks5://127.0.0.1:7890 https://www.google.com
   \`\`\`

3. 检查节点状态
   - 在控制面板中测试各节点延迟
   - 选择延迟正常的节点

---

### 5. TUN 模式问题

**症状：** 启用 TUN 后服务异常

**原因：** fnOS 环境可能不支持 TUN 功能

**解决方案：**
1. 关闭 TUN（推荐）
2. 使用浏览器插件或系统代理设置

---

### 6. 规则不生效

**症状：** 分流规则未按预期工作

**排查步骤：**

1. 检查规则配置
   \`\`\`bash
   cat /vol1/@appdata/miproxy/config.yaml | grep -A 10 "rules:"
   \`\`\`

2. 确认 GEO 数据库存在
   \`\`\`bash
   ls -la /vol1/@appdata/miproxy/data/
   \`\`\`

3. 检查规则顺序
   - 规则按顺序匹配，第一条匹配的规则生效
   - 确保 Catch-all 规则在最后

---

## 高级排查

### 启用调试日志

1. 编辑 config.yaml
   \`\`\`yaml
   log-level: debug
   \`\`\`

2. 重启服务
   \`\`\`bash
   # 在 fnOS 应用中心重启 MiProxy
   \`\`\`

### 检查 mihomo 配置

\`\`\`bash
# 验证配置文件
/vol1/@appdata/miproxy/target/mihomo -t -d /vol1/@appdata/miproxy -f /vol1/@appdata/miproxy/config.yaml
\`\`\`

---

## 获取帮助

如果以上方法无法解决问题：

1. 收集日志
   \`\`\`bash
   cat /vol1/@appdata/miproxy/info.log > ~/miproxy_log.txt
   cat /vol1/@appdata/miproxy/refresh_sub.log >> ~/miproxy_log.txt
   \`\`\`

2. [提交 Issue](https://github.com/56025192/miproxy-fpk/issues)
   - 说明问题现象
   - 附上相关日志（注意脱敏敏感信息）
   - 说明 fnOS 版本和应用版本

