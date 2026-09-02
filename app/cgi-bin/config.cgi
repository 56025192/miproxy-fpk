#!/bin/bash

# MiProxy 配置管理 CGI
# 支持：save（保存配置）、start（启动服务）、restore（恢复备份）

echo "Content-Type: application/json"
echo ""

# 获取目录路径
APP_DIR="${TRIM_APPDEST:-/var/apps/miproxy}"
VAR_DIR="${TRIM_PKGVAR:-/var/apps/miproxy/var}"
PKGETC="${TRIM_PKGETC:-/var/apps/miproxy/etc}"
TARGET_DIR="${VAR_DIR}/target"
UI_TARGET="${VAR_DIR}/ui"
BACKUP_DIR="/tmp/miproxy_backup"
CONFIG_FILE="${VAR_DIR}/config.yaml"
LOG_FILE="${VAR_DIR}/info.log"
SCRIPT_DIR="${APP_DIR}/cmd"

# 创建日志函数
log_msg() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - webui: $1" >> "${LOG_FILE}" 2>/dev/null
}

# 读取 POST 数据
CONTENT_LENGTH=$(echo "$CONTENT_LENGTH" | tr -d ' ')
if [ -n "$CONTENT_LENGTH" ] && [ "$CONTENT_LENGTH" -gt 0 ]; then
    POST_DATA=$(cat | head -c 10240)
else
    POST_DATA=""
fi

# 解析 JSON
parse_json() {
    local key="$1"
    echo "$POST_DATA" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('$key', ''))
" 2>/dev/null
}

# 获取查询参数
ACTION="${QUERY_STRING%%&*}"
ACTION="${ACTION#*=}"
[ -z "$ACTION" ] && ACTION="${REQUEST_METHOD:-GET}"

log_msg "收到请求: action=$ACTION"

# ==================== 恢复备份 ====================
restore_backup() {
    log_msg "开始恢复备份..."
    
    mkdir -p "${VAR_DIR}" "${PKGETC}" "${TARGET_DIR}" "${UI_TARGET}" "${VAR_DIR}/proxy_providers"
    
    # 恢复配置文件
    if [ -f "${BACKUP_DIR}/config.yaml" ]; then
        cp -f "${BACKUP_DIR}/config.yaml" "${CONFIG_FILE}"
        chmod 666 "${CONFIG_FILE}" 2>/dev/null
        log_msg "配置文件已恢复"
    fi
    
    # 恢复设置
    if [ -f "${BACKUP_DIR}/settings.conf" ]; then
        cp -f "${BACKUP_DIR}/settings.conf" "${PKGETC}/settings.conf"
        chmod 666 "${PKGETC}/settings.conf" 2>/dev/null
        log_msg "设置已恢复"
    fi
    
    # 恢复订阅缓存
    if [ -d "${BACKUP_DIR}/proxy_providers" ]; then
        cp -rf "${BACKUP_DIR}/proxy_providers/"* "${VAR_DIR}/proxy_providers/" 2>/dev/null
        log_msg "订阅缓存已恢复"
    fi
    
    # 恢复 UI 数据
    if [ -d "${BACKUP_DIR}/ui" ]; then
        cp -rf "${BACKUP_DIR}/ui/"* "${UI_TARGET}/" 2>/dev/null
        log_msg "UI 数据已恢复"
    fi
    
    # 安装程序文件
    [ -f "${APP_DIR}/server/mihomo" ] && cp -f "${APP_DIR}/server/mihomo" "${TARGET_DIR}/mihomo" && chmod +x "${TARGET_DIR}/mihomo"
    log_msg "程序文件已安装"
    
    # 清理备份标记
    rm -f "${BACKUP_DIR}/.preserved"
    
    log_msg "备份恢复完成"
    echo "{\"success\": true, \"message\": \"配置已恢复\"}"
}

# ==================== 保存配置 ====================
save_config() {
    local sub_type=$(parse_json "sub_type")
    local sub_url=$(parse_json "sub_url")
    local sub_path=$(parse_json "sub_path")
    
    sub_type="${sub_type:-none}"
    
    log_msg "保存配置: sub_type=$sub_type"
    
    mkdir -p "${VAR_DIR}" "${PKGETC}" "${TARGET_DIR}" "${UI_TARGET}" "${VAR_DIR}/proxy_providers"
    
    # 安装程序文件
    [ -f "${APP_DIR}/server/mihomo" ] && cp -f "${APP_DIR}/server/mihomo" "${TARGET_DIR}/mihomo" && chmod +x "${TARGET_DIR}/mihomo"
    
    # 复制 UI
    [ -d "${APP_DIR}/ui/zashboard" ] && mkdir -p "${UI_TARGET}/zashboard" && cp -rf "${APP_DIR}/ui/zashboard/"* "${UI_TARGET}/zashboard/" 2>/dev/null
    [ -d "${APP_DIR}/ui/metacubexd" ] && mkdir -p "${UI_TARGET}/metacubexd" && cp -rf "${APP_DIR}/ui/metacubexd/"* "${UI_TARGET}/metacubexd/" 2>/dev/null
    [ -f "${APP_DIR}/ui/config" ] && cp -f "${APP_DIR}/ui/config" "${UI_TARGET}/config"
    [ -f "${APP_DIR}/ui/index.html" ] && cp -f "${APP_DIR}/ui/index.html" "${UI_TARGET}/index.html"
    [ -d "${APP_DIR}/ui/images" ] && mkdir -p "${UI_TARGET}/images" && cp -rf "${APP_DIR}/ui/images/"* "${UI_TARGET}/images/" 2>/dev/null
    chmod 666 "${UI_TARGET}/config" 2>/dev/null
    
    # 复制 GEO 数据
    [ -d "${APP_DIR}/data" ] && for f in geoip.dat geosite.dat Country.mmdb; do
        [ -f "${APP_DIR}/data/${f}" ] && cp -f "${APP_DIR}/data/${f}" "${VAR_DIR}/${f}" && chmod 666 "${VAR_DIR}/${f}" 2>/dev/null
    done
    
    # 处理订阅
    local sub_cache="${VAR_DIR}/proxy_providers/subscription.yaml"
    
    if [ "$sub_type" = "remote" ] && [ -n "$sub_url" ]; then
        log_msg "下载远程订阅: $sub_url"
        if curl -fsSL --connect-timeout 15 --max-time 60 "$sub_url" -o "${sub_cache}.tmp" 2>/dev/null; then
            mv "${sub_cache}.tmp" "${sub_cache}"
            log_msg "订阅下载成功"
        else
            log_msg "订阅下载失败，使用空配置"
            rm -f "${sub_cache}.tmp"
        fi
    elif [ "$sub_type" = "local" ] && [ -n "$sub_path" ] && [ -f "$sub_path" ]; then
        cp -f "$sub_path" "${sub_cache}"
        log_msg "本地订阅已配置"
    fi
    
    # 生成 config.yaml
    generate_config
    
    # 保存设置
    cat > "${PKGETC}/settings.conf" << EOF
wizard_sub_type=${sub_type}
wizard_sub_url=${sub_url}
wizard_sub_path=${sub_path}
wizard_http_port=7890
wizard_api_port=9090
wizard_tun_enable=false
EOF
    chmod 666 "${PKGETC}/settings.conf" 2>/dev/null
    
    log_msg "配置保存完成"
    echo "{\"success\": true, \"message\": \"配置已保存\"}"
}

# 生成配置文件
generate_config() {
    local http_port=7890
    local api_port=9090
    local sub_cache="${VAR_DIR}/proxy_providers/subscription.yaml"
    
    {
        echo "# MiProxy 主配置（由 Web UI 生成）"
        echo ""
        echo "mixed-port: ${http_port}"
        echo "allow-lan: true"
        echo "mode: rule"
        echo "log-level: info"
        echo "ipv6: false"
        echo "external-controller: 0.0.0.0:${api_port}"
        echo "external-ui: ${UI_TARGET}"
        echo "external-ui-name: zashboard"
        echo "external-controller-cors:"
        echo "  allow-private-network: true"
        echo "  allow-origins: [\"*\"]"
        echo "geodata-mode: true"
        echo "geodata-loader: memconservative"
        echo "tun:"
        echo "  enable: false"
        echo "  stack: system"
        echo "  auto-route: true"
        echo "  auto-detect-interface: true"
        echo "dns:"
        echo "  enable: true"
        echo "  listen: 0.0.0.0:53"
        echo "  enhanced-mode: fake-ip"
        echo "  fake-ip-range: 198.18.0.1/16"
        echo "  fake-ip-filter: [\"+.lan\", \"+.local\"]"
        echo "  nameserver: [223.5.5.5, 119.29.29.29, 8.8.8.8]"
        echo "proxy-groups:"
        echo "  - name: PROXY"
        echo "    type: select"
        echo "    proxies: [DIRECT, REJECT]"
        echo "rules:"
        echo "  - GEOIP,CN,DIRECT"
        echo "  - MATCH,PROXY"
    } > "${CONFIG_FILE}"
    
    chmod 666 "${CONFIG_FILE}" 2>/dev/null
    log_msg "配置文件已生成"
}

# ==================== 启动服务 ====================
start_service() {
    log_msg "启动服务..."
    
    # 检查配置文件
    if [ ! -f "${CONFIG_FILE}" ]; then
        log_msg "配置文件不存在，无法启动"
        echo "{\"success\": false, \"message\": \"配置文件不存在\"}"
        return 1
    fi
    
    # 检查程序文件
    if [ ! -x "${TARGET_DIR}/mihomo" ]; then
        log_msg "程序文件不存在"
        echo "{\"success\": false, \"message\": \"程序文件不存在\"}"
        return 1
    fi
    
    # 调用主脚本启动
    if [ -x "${SCRIPT_DIR}/main" ]; then
        bash "${SCRIPT_DIR}/main" start 2>&1 | head -5 >> "${LOG_FILE}"
        log_msg "启动命令已执行"
        echo "{\"success\": true, \"message\": \"服务启动中\"}"
    else
        log_msg "主脚本不存在"
        echo "{\"success\": false, \"message\": \"主脚本不存在\"}"
        return 1
    fi
}

# ==================== 主逻辑 ====================
case "$ACTION" in
    restore)
        restore_backup
        ;;
    save)
        save_config
        ;;
    start)
        start_service
        ;;
    *)
        echo "{\"success\": false, \"message\": \"未知操作: $ACTION\"}"
        ;;
esac
