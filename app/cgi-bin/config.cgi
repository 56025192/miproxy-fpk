#!/bin/bash

# MiProxy 配置管理 CGI
# 支持：安装配置、保存配置、读取配置、重启服务

echo "Content-Type: application/json"
echo "Cache-Control: no-cache"
echo ""

# 获取目录路径
APP_DIR="${TRIM_APPDEST:-/var/apps/miproxy}"
VAR_DIR="${TRIM_PKGVAR:-/var/apps/miproxy/var}"
PKGETC="${TRIM_PKGETC:-/var/apps/miproxy/etc}"
TARGET_DIR="${VAR_DIR}/target"
CONFIG_FILE="${VAR_DIR}/config.yaml"
SETTINGS_FILE="${PKGETC}/settings.conf"

# 创建必要目录
mkdir -p "${VAR_DIR}" "${PKGETC}" "${TARGET_DIR}" 2>/dev/null

# 解析查询参数
ACTION="${QUERY_STRING%%&*}"
ACTION="${ACTION#action=}"

# 读取 POST 数据
POST_DATA=""
if [ "$REQUEST_METHOD" = "POST" ]; then
    read -n $CONTENT_LENGTH POST_DATA
fi

# 提取 JSON 字段的辅助函数
get_json_field() {
    local field="$1"
    echo "$POST_DATA" | python3 -c "
import sys, json
try:
    data = json.loads(sys.stdin.read())
    print(data.get('${field}', '') or '')
except:
    print('')
" 2>/dev/null
}

# ========== 1. 安装配置 ==========
if [ "$ACTION" = "install" ]; then
    http_port=$(get_json_field "http_port")
    api_port=$(get_json_field "api_port")
    secret=$(get_json_field "secret")
    sub_type=$(get_json_field "sub_type")
    sub_url=$(get_json_field "sub_url")
    sub_path=$(get_json_field "sub_path")
    refresh_interval=$(get_json_field "refresh_interval")
    
    # 默认值
    http_port=${http_port:-7890}
    api_port=${api_port:-9090}
    sub_type=${sub_type:-none}
    refresh_interval=${refresh_interval:-0}
    
    # 1. 保存设置到 settings.conf
    {
        echo "wizard_http_port=${http_port}"
        echo "wizard_api_port=${api_port}"
        [ -n "$secret" ] && echo "wizard_secret=${secret}"
        echo "wizard_sub_type=${sub_type}"
        [ -n "$sub_url" ] && echo "wizard_sub_url=${sub_url}"
        [ -n "$sub_path" ] && echo "wizard_sub_path=${sub_path}"
        echo "wizard_refresh_interval=${refresh_interval}"
    } > "${SETTINGS_FILE}"
    chmod 644 "${SETTINGS_FILE}" 2>/dev/null
    
    # 2. 复制 mihomo 二进制
    if [ -f "${APP_DIR}/server/mihomo" ]; then
        cp -f "${APP_DIR}/server/mihomo" "${TARGET_DIR}/mihomo"
        chmod +x "${TARGET_DIR}/mihomo"
    fi
    
    # 3. 复制 UI 文件
    [ -d "${APP_DIR}/ui/zashboard" ] && cp -rf "${APP_DIR}/ui/zashboard" "${VAR_DIR}/" 2>/dev/null
    [ -d "${APP_DIR}/ui/metacubexd" ] && cp -rf "${APP_DIR}/ui/metacubexd" "${VAR_DIR}/" 2>/dev/null
    [ -f "${APP_DIR}/ui/index.html" ] && cp -f "${APP_DIR}/ui/index.html" "${VAR_DIR}/" 2>/dev/null
    [ -d "${APP_DIR}/data" ] && for f in geoip.dat geosite.dat Country.mmdb; do
        [ -f "${APP_DIR}/data/${f}" ] && cp -f "${APP_DIR}/data/${f}" "${VAR_DIR}/${f}" 2>/dev/null
    done
    
    # 4. 下载远程订阅（如需要）
    sub_cache="${VAR_DIR}/proxy_providers/subscription.yaml"
    if [ "$sub_type" = "remote" ] && [ -n "$sub_url" ]; then
        mkdir -p "${VAR_DIR}/proxy_providers"
        curl -fsSL --connect-timeout 15 --max-time 60 "${sub_url}" -o "${sub_cache}" 2>/dev/null
    elif [ "$sub_type" = "local" ] && [ -n "$sub_path" ] && [ -f "$sub_path" ]; then
        mkdir -p "${VAR_DIR}/proxy_providers"
        cp -f "${sub_path}" "${sub_cache}"
    fi
    
    # 5. 生成 config.yaml
    generate_config
    
    # 6. 启动服务
    start_result="false"
    if "${APP_DIR}/cmd/main" start 2>/dev/null; then
        start_result="true"
    fi
    
    cat << EOF
{
    "success": true,
    "message": "安装完成",
    "started": ${start_result}
}
EOF
    exit 0
fi

# ========== 2. 读取配置 ==========
if [ "$ACTION" = "get" ]; then
    http_port="7890"
    api_port="9090"
    secret=""
    sub_type="none"
    sub_url=""
    sub_path=""
    refresh_interval="0"
    
    if [ -f "${SETTINGS_FILE}" ]; then
        http_port=$(grep '^wizard_http_port=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' \n\r')
        http_port=${http_port:-7890}
        api_port=$(grep '^wizard_api_port=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' \n\r')
        api_port=${api_port:-9090}
        secret=$(grep '^wizard_secret=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' \n\r')
        sub_type=$(grep '^wizard_sub_type=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' \n\r')
        sub_type=${sub_type:-none}
        sub_url=$(grep '^wizard_sub_url=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' \n\r')
        sub_path=$(grep '^wizard_sub_path=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' \n\r')
        refresh_interval=$(grep '^wizard_refresh_interval=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' \n\r')
        refresh_interval=${refresh_interval:-0}
    fi
    
    cat << EOF
{
    "success": true,
    "config": {
        "http_port": "${http_port}",
        "api_port": "${api_port}",
        "secret": "${secret}",
        "sub_type": "${sub_type}",
        "sub_url": "${sub_url}",
        "sub_path": "${sub_path}",
        "refresh_interval": "${refresh_interval}"
    }
}
EOF
    exit 0
fi

# ========== 3. 保存配置 ==========
if [ "$ACTION" = "save" ]; then
    sub_type=$(get_json_field "sub_type")
    sub_url=$(get_json_field "sub_url")
    sub_path=$(get_json_field "sub_path")
    refresh_interval=$(get_json_field "refresh_interval")
    
    sub_type=${sub_type:-none}
    refresh_interval=${refresh_interval:-0}
    
    # 更新 settings.conf
    if [ -f "${SETTINGS_FILE}" ]; then
        # 保留现有值
        http_port=$(grep '^wizard_http_port=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' \n\r')
        api_port=$(grep '^wizard_api_port=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' \n\r')
        secret=$(grep '^wizard_secret=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' \n\r')
        
        {
            echo "wizard_http_port=${http_port}"
            echo "wizard_api_port=${api_port}"
            [ -n "$secret" ] && echo "wizard_secret=${secret}"
            echo "wizard_sub_type=${sub_type}"
            [ -n "$sub_url" ] && echo "wizard_sub_url=${sub_url}"
            [ -n "$sub_path" ] && echo "wizard_sub_path=${sub_path}"
            echo "wizard_refresh_interval=${refresh_interval}"
        } > "${SETTINGS_FILE}"
    fi
    
    # 更新订阅缓存
    sub_cache="${VAR_DIR}/proxy_providers/subscription.yaml"
    if [ "$sub_type" = "remote" ] && [ -n "$sub_url" ]; then
        mkdir -p "${VAR_DIR}/proxy_providers"
        curl -fsSL --connect-timeout 15 --max-time 60 "${sub_url}" -o "${sub_cache}" 2>/dev/null
    elif [ "$sub_type" = "local" ] && [ -n "$sub_path" ] && [ -f "$sub_path" ]; then
        mkdir -p "${VAR_DIR}/proxy_providers"
        cp -f "${sub_path}" "${sub_cache}"
    fi
    
    # 重新生成 config.yaml
    generate_config
    
    cat << EOF
{
    "success": true,
    "message": "配置已保存，需要重启服务使配置生效"
}
EOF
    exit 0
fi

# ========== 4. 重启服务 ==========
if [ "$ACTION" = "restart" ]; then
    restart_result="false"
    if "${APP_DIR}/cmd/main" restart 2>/dev/null; then
        restart_result="true"
    fi
    
    cat << EOF
{
    "success": ${restart_result},
    "message": "$(if [ "$restart_result" = "true" ]; then echo "服务已重启"; else echo "重启失败"; fi)"
}
EOF
    exit 0
fi

# ========== 5. 启动服务 ==========
if [ "$ACTION" = "start" ]; then
    start_result="false"
    if "${APP_DIR}/cmd/main" start 2>/dev/null; then
        start_result="true"
    fi
    
    cat << EOF
{
    "success": ${start_result}
}
EOF
    exit 0
fi

# 默认：未知操作
cat << EOF
{
    "success": false,
    "error": "未知操作: ${ACTION}"
}
EOF

# ========== 生成配置文件的函数 ==========
generate_config() {
    local UI_TARGET="${VAR_DIR}/ui"
    
    # 读取订阅类型
    sub_type=$(grep '^wizard_sub_type=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' \n\r')
    sub_url=$(grep '^wizard_sub_url=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' \n\r')
    http_port=$(grep '^wizard_http_port=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' \n\r')
    http_port=${http_port:-7890}
    api_port=$(grep '^wizard_api_port=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' \n\r')
    api_port=${api_port:-9090}
    secret=$(grep '^wizard_secret=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' \n\r')
    
    # 订阅域名过滤
    local sub_domain_filter=""
    if [ "$sub_type" = "remote" ] && [ -n "$sub_url" ]; then
        local domain=$(echo "${sub_url}" | sed -E 's|^https?://||; s|/.*$||; s|:.*$||')
        if [ -n "$domain" ]; then
            sub_domain_filter="    - \"${domain}\"\n    - \"*.${domain}\""
        fi
    fi
    
    # 提取订阅中的配置块
    local sub_cache="${VAR_DIR}/proxy_providers/subscription.yaml"
    local sub_proxies="" sub_pg="" sub_rules="" sub_dns=""
    
    extract_yaml_block() {
        local key="$1"
        python3 - "$key" "${sub_cache}" 2>/dev/null
    }
    
    if [ -f "${sub_cache}" ]; then
        sub_proxies=$(extract_yaml_block "proxies")
        sub_pg=$(extract_yaml_block "proxy-groups")
        sub_rules=$(extract_yaml_block "rules")
        sub_dns=$(extract_yaml_block "dns")
    fi
    
    # 生成 config.yaml
    {
        echo "# MiProxy 配置文件（自动生成）"
        echo "# 生成时间: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        echo "mixed-port: ${http_port}"
        echo "allow-lan: true"
        echo "mode: rule"
        echo "log-level: info"
        echo "ipv6: false"
        echo "external-controller: 0.0.0.0:${api_port}"
        echo "external-ui: ${UI_TARGET}"
        echo "external-ui-name: zashboard"
        [ -n "$secret" ] && echo "secret: \"${secret}\""
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
        echo ""
        
        # 订阅配置
        if [ -n "${sub_proxies}" ]; then
            echo "# 节点列表"
            echo "${sub_proxies}"
        fi
        
        if [ -n "${sub_pg}" ]; then
            echo "# 代理组"
            echo "${sub_pg}"
        else
            echo "proxy-groups:"
            echo "  - name: PROXY; type: select; proxies: [DIRECT, REJECT]"
        fi
        
        if [ -n "${sub_rules}" ]; then
            echo "# 规则"
            echo "${sub_rules}"
        else
            echo "rules: [\"GEOIP,CN,DIRECT\", \"MATCH,PROXY\"]"
        fi
        
        if [ -n "${sub_dns}" ]; then
            echo "# DNS"
            echo "${sub_dns}"
        else
            echo "dns:"
            echo "  enable: true; listen: 0.0.0.0:53"
            echo "  enhanced-mode: fake-ip; fake-ip-range: 198.18.0.1/16"
            echo "  fake-ip-filter: [\"+.lan\", \"+.local\"${sub_domain_filter:+, ${domain}, \"*.${domain}\"}]"
            echo "  nameserver: [223.5.5.5, 119.29.29.29, 8.8.8.8]"
        fi
    } > "${CONFIG_FILE}"
    
    chmod 644 "${CONFIG_FILE}" 2>/dev/null
}

# YAML 块提取函数
extract_yaml_block() {
    local key="$1"
    local file="$2"
    python3 - "$key" "$file" 2>/dev/null
}

# Python 辅助脚本
python3 - "$1" "$2" 2>/dev/null <<'PYEOF'
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
