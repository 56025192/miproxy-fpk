#!/bin/bash

# MiProxy 配置保存 CGI
# 接收 JSON 格式的配置并保存

echo "Content-Type: application/json"
echo ""

# 获取目录路径
APP_DIR="${TRIM_APPDEST:-/var/apps/miproxy}"
VAR_DIR="${TRIM_PKGVAR:-/var/apps/miproxy/var}"
PKGETC="${TRIM_PKGETC:-/var/apps/miproxy/etc}"
TARGET_DIR="${VAR_DIR}/target"
UI_TARGET="${VAR_DIR}/ui"
BACKUP_DIR="/tmp/miproxy_backup"

# 确保目录存在
mkdir -p "${VAR_DIR}" "${PKGETC}" "${TARGET_DIR}" "${UI_TARGET}" "${VAR_DIR}/proxy_providers"

# 读取 POST 数据
REQUEST_METHOD="${REQUEST_METHOD:-POST}"
if [ "${REQUEST_METHOD}" = "POST" ]; then
    CONTENT_LENGTH="${CONTENT_LENGTH:-0}"
    if [ "${CONTENT_LENGTH}" -gt 0 ]; then
        POST_DATA=$(cat)
    else
        POST_DATA=""
    fi
else
    POST_DATA=""
fi

# 解析 JSON（简单方式）
parse_json() {
    echo "$POST_DATA" | python3 - "$1" 2>/dev/null << 'PYEOF'
import sys, json
try:
    data = json.loads(sys.stdin.read())
    key = sys.argv[1]
    print(data.get(key, ''))
except:
    print('')
PYEOF
}

# 提取配置值
HTTP_PORT=$(parse_json "wizard_http_port")
API_PORT=$(parse_json "wizard_api_port")
SUB_TYPE=$(parse_json "wizard_sub_type")
SUB_URL=$(parse_json "wizard_sub_url")
SUB_PATH=$(parse_json "wizard_sub_path")
SECRET=$(parse_json "wizard_secret")
PROXY_USER=$(parse_json "wizard_proxy_user")
PROXY_PASS=$(parse_json "wizard_proxy_pass")
REFRESH_INTERVAL=$(parse_json "wizard_refresh_interval")

# 设置默认值
HTTP_PORT=${HTTP_PORT:-7890}
API_PORT=${API_PORT:-9090}
SUB_TYPE=${SUB_TYPE:-none}
REFRESH_INTERVAL=${REFRESH_INTERVAL:-0}

# 订阅域名前缀过滤
SUB_DOMAIN_FILTER=""
if [ "${SUB_TYPE}" = "remote" ] && [ -n "${SUB_URL}" ]; then
    domain=$(echo "${SUB_URL}" | sed -E 's|^https?://||; s|/.*$||; s|:.*$||')
    [ -n "${domain}" ] && SUB_DOMAIN_FILTER="\n    - \"${domain}\"\n    - \"*.${domain}\""
fi

# 复制二进制文件
if [ -f "${APP_DIR}/server/mihomo" ]; then
    cp -f "${APP_DIR}/server/mihomo" "${TARGET_DIR}/mihomo"
    chmod +x "${TARGET_DIR}/mihomo"
fi

# 复制 UI 文件
if [ -d "${APP_DIR}/ui/zashboard" ]; then
    mkdir -p "${UI_TARGET}/zashboard"
    cp -rf "${APP_DIR}/ui/zashboard/"* "${UI_TARGET}/zashboard/" 2>/dev/null
fi
if [ -d "${APP_DIR}/ui/metacubexd" ]; then
    mkdir -p "${UI_TARGET}/metacubexd"
    cp -rf "${APP_DIR}/ui/metacubexd/"* "${UI_TARGET}/metacubexd/" 2>/dev/null
fi
cp -f "${APP_DIR}/ui/index.html" "${UI_TARGET}/index.html" 2>/dev/null
cp -f "${APP_DIR}/ui/config" "${UI_TARGET}/config" 2>/dev/null
if [ -d "${APP_DIR}/ui/images" ]; then
    mkdir -p "${UI_TARGET}/images"
    cp -rf "${APP_DIR}/ui/images/"* "${UI_TARGET}/images/" 2>/dev/null
fi
chmod 666 "${UI_TARGET}/config" 2>/dev/null

# 复制 GEO 数据
if [ -d "${APP_DIR}/data" ]; then
    for f in geoip.dat geosite.dat Country.mmdb; do
        [ -f "${APP_DIR}/data/${f}" ] && cp -f "${APP_DIR}/data/${f}" "${VAR_DIR}/${f}"
    done
fi

# 处理订阅
SUB_CACHE_PATH="${VAR_DIR}/proxy_providers/subscription.yaml"
if [ "${SUB_TYPE}" = "remote" ] && [ -n "${SUB_URL}" ]; then
    curl -fsSL --connect-timeout 15 --max-time 60 "${SUB_URL}" -o "${SUB_CACHE_PATH}.tmp" 2>/dev/null && mv "${SUB_CACHE_PATH}.tmp" "${SUB_CACHE_PATH}"
elif [ "${SUB_TYPE}" = "local" ] && [ -n "${SUB_PATH}" ] && [ -f "${SUB_PATH}" ]; then
    cp -f "${SUB_PATH}" "${SUB_CACHE_PATH}"
fi

# 提取订阅中的配置块
extract_yaml_block() {
    python3 - "$1" "${SUB_CACHE_PATH}" 2>/dev/null << 'PYEOF'
import sys
key = sys.argv[1] + ":"
try:
    with open(sys.argv[2], 'r', encoding='utf-8') as f:
        lines = f.readlines()
except:
    sys.exit(0)
result = []
found = False
for line in lines:
    stripped = line.rstrip('\n')
    if not stripped.strip():
        if found: result.append(line)
        continue
    is_top = not stripped[0].isspace()
    if is_top:
        if stripped.startswith(key):
            found = True
            result.append(line)
        elif found:
            if stripped.startswith('-'):
                result.append(line)
            else:
                break
    elif found:
        result.append(line)
sys.stdout.write(''.join(result))
PYEOF
}

# 读取订阅配置
SUB_PROXIES=""
SUB_HOSTS=""
SUB_PG=""
SUB_RULES=""
SUB_DNS=""
SUB_BYPASS=""
SUB_PROXY_PROVIDERS=""
SUB_RULE_PROVIDERS=""

if [ -f "${SUB_CACHE_PATH}" ]; then
    SUB_PROXIES=$(extract_yaml_block "proxies")
    SUB_HOSTS=$(extract_yaml_block "hosts")
    SUB_PG=$(extract_yaml_block "proxy-groups")
    SUB_RULES=$(extract_yaml_block "rules")
    SUB_DNS=$(extract_yaml_block "dns")
    SUB_BYPASS=$(extract_yaml_block "bypass")
    SUB_PROXY_PROVIDERS=$(extract_yaml_block "proxy-providers")
    SUB_RULE_PROVIDERS=$(extract_yaml_block "rule-providers")
fi

# 生成 config.yaml
CONFIG_FILE="${VAR_DIR}/config.yaml"
{
    echo "# MiProxy 主配置"
    echo ""
    echo "mixed-port: ${HTTP_PORT}"
    echo "allow-lan: true"
    echo "mode: rule"
    echo "log-level: info"
    echo "ipv6: false"
    echo "external-controller: 0.0.0.0:${API_PORT}"
    echo "external-ui: ${UI_TARGET}"
    echo "external-ui-name: zashboard"
    [ -n "${SECRET}" ] && echo "secret: \"${SECRET}\""
    [ -n "${PROXY_USER}" ] && [ -n "${PROXY_PASS}" ] && echo "authentication:" && echo "  - \"${PROXY_USER}:${PROXY_PASS}\""
    echo "external-controller-cors:"
    echo "  allow-private-network: true"
    echo "  allow-origins: [\"*\"]"
    echo "geodata-mode: true"
    echo "geodata-loader: memconservative"
    echo "tun:"
    echo "  enable: false"
    echo "  stack: system"
    echo "  auto-route: true"
    echo "  auto-redirect: true"
    echo "  auto-detect-interface: true"
    echo "  dns-hijack: [\"any:53\", \"tcp://any:53\"]"
    
    [ -n "${SUB_PROXIES}" ] && echo "# 节点列表" && echo "${SUB_PROXIES}"
    [ -n "${SUB_HOSTS}" ] && echo "# hosts" && echo "${SUB_HOSTS}"
    
    if [ -n "${SUB_PG}" ]; then
        echo "# 代理组"
        echo "${SUB_PG}"
    else
        echo "proxy-groups:"
        echo "  - name: PROXY; type: select; proxies: [DIRECT, REJECT]"
    fi
    
    if [ -n "${SUB_RULES}" ]; then
        echo "# 路由规则"
        echo "${SUB_RULES}"
    else
        echo "rules: [\"GEOIP,CN,DIRECT\", \"MATCH,PROXY\"]"
    fi
    
    if [ -n "${SUB_DNS}" ]; then
        echo "# DNS"
        echo "${SUB_DNS}"
    else
        echo "dns:"
        echo "  enable: true; listen: 0.0.0.0:53"
        echo "  enhanced-mode: fake-ip; fake-ip-range: 198.18.0.1/16"
        echo "  fake-ip-filter: [\"+.lan\", \"+.local\"${SUB_DOMAIN_FILTER}]"
        echo "  nameserver: [223.5.5.5, 119.29.29.29, 8.8.8.8]"
    fi
    
    [ -n "${SUB_BYPASS}" ] && echo "# bypass" && echo "${SUB_BYPASS}"
    [ -n "${SUB_PROXY_PROVIDERS}" ] && echo "# proxy-providers" && echo "${SUB_PROXY_PROVIDERS}"
    [ -n "${SUB_RULE_PROVIDERS}" ] && echo "# rule-providers" && echo "${SUB_RULE_PROVIDERS}"
} > "${CONFIG_FILE}"

chmod 666 "${CONFIG_FILE}"

# 保存设置
{
    echo "wizard_http_port=${HTTP_PORT}"
    echo "wizard_api_port=${API_PORT}"
    echo "wizard_sub_type=${SUB_TYPE}"
    echo "wizard_refresh_interval=${REFRESH_INTERVAL}"
    [ -n "${SECRET}" ] && echo "wizard_secret=${SECRET}"
    [ -n "${PROXY_USER}" ] && echo "wizard_proxy_user=${PROXY_USER}"
    [ -n "${PROXY_PASS}" ] && echo "wizard_proxy_pass=${PROXY_PASS}"
    [ -n "${SUB_URL}" ] && echo "wizard_sub_url=${SUB_URL}"
    [ -n "${SUB_PATH}" ] && echo "wizard_sub_path=${SUB_PATH}"
} > "${PKGETC}/settings.conf"

chmod 666 "${PKGETC}/settings.conf" 2>/dev/null

# 清理备份标记（安装完成后）
if [ -d "${BACKUP_DIR}" ]; then
    rm -f "${BACKUP_DIR}/.preserved"
fi

# 启动 miproxy
if [ -x "${TARGET_DIR}/mihomo" ]; then
    # 停止旧进程
    pkill -x mihomo 2>/dev/null || true
    sleep 1
    # 启动新进程
    nohup "${TARGET_DIR}/mihomo" -d "${VAR_DIR}" -f "${CONFIG_FILE}" >> "${VAR_DIR}/info.log" 2>&1 &
    echo $! > "${VAR_DIR}/app.pid"
fi

# 返回成功
cat << EOF
{
    "success": true,
    "message": "配置已保存"
}
EOF
