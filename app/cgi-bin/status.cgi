#!/bin/bash

# MiProxy 状态检测 CGI
# 用于检测安装状态和服务运行状态

echo "Content-Type: application/json"
echo "Cache-Control: no-cache"
echo ""

# 获取目录路径
APP_DIR="${TRIM_APPDEST:-/var/apps/miproxy}"
VAR_DIR="${TRIM_PKGVAR:-/var/apps/miproxy/var}"
PKGETC="${TRIM_PKGETC:-/var/apps/miproxy/etc}"

# 检查查询参数
ACTION="${QUERY_STRING%%&*}"

# 1. 检查服务状态
if [ "$ACTION" = "check=service" ] || [ "$ACTION" = "service" ]; then
    PID_FILE="${VAR_DIR}/app.pid"
    LOG_FILE="${VAR_DIR}/info.log"
    running="false"
    pid=""
    
    if [ -f "${PID_FILE}" ]; then
        pid=$(cat "${PID_FILE}" 2>/dev/null | tr -d ' \n\r')
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            running="true"
        fi
    fi
    
    # 额外检查：尝试连接 API 端口
    if [ "$running" = "false" ]; then
        api_port=$(grep '^wizard_api_port=' "${PKGETC}/settings.conf" 2>/dev/null | cut -d= -f2- | tr -d ' ')
        api_port=${api_port:-9090}
        if curl -sf -m 2 "http://127.0.0.1:${api_port}/configs" > /dev/null 2>&1; then
            running="true"
        fi
    fi
    
    cat << EOF
{
    "running": ${running},
    "pid": "${pid}"
}
EOF
    exit 0
fi

# 2. 检查安装状态（默认）
CONFIG_FILE="${VAR_DIR}/config.yaml"
SETTINGS_FILE="${PKGETC}/settings.conf"

installed="false"
if [ -f "${CONFIG_FILE}" ] && [ -s "${CONFIG_FILE}" ]; then
    installed="true"
fi

# 读取配置信息
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
    "installed": ${installed},
    "config": {
        "http_port": "${http_port}",
        "api_port": "${api_port}",
        "secret": "${secret}",
        "sub_type": "${sub_type}",
        "sub_url": "${sub_url}",
        "sub_path": "${sub_path}",
        "refresh_interval": "${refresh_interval}"
    },
    "var_dir": "${VAR_DIR}",
    "etc_dir": "${PKGETC}"
}
EOF
