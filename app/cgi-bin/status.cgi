#!/bin/bash

# MiProxy 状态检测 CGI
# 支持多种检测模式

echo "Content-Type: application/json"
echo ""

# 获取目录路径
APP_DIR="${TRIM_APPDEST:-/var/apps/miproxy}"
VAR_DIR="${TRIM_PKGVAR:-/var/apps/miproxy/var}"
PKGETC="${TRIM_PKGETC:-/var/apps/miproxy/etc}"
BACKUP_DIR="/tmp/miproxy_backup"
TARGET_DIR="${VAR_DIR}/target"

# 检查查询参数
ACTION="${QUERY_STRING%%&*}"
if [ "$ACTION" = "check=service" ]; then
    # 检查服务状态
    PID_FILE="${VAR_DIR}/app.pid"
    running="false"
    
    if [ -f "${PID_FILE}" ]; then
        pid=$(cat "${PID_FILE}" 2>/dev/null | tr -d ' ')
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            running="true"
        fi
    fi
    
    echo "{\"running\": ${running}}"
    exit 0
fi

# 默认：检查配置状态
CONFIG_FILE="${VAR_DIR}/config.yaml"
SETTINGS_FILE="${PKGETC}/settings.conf"
BACKUP_PRESERVED="${BACKUP_DIR}/.preserved"

# 检测状态
CONFIGURED="false"
HAS_BACKUP="false"
SUB_TYPE="none"
SUB_URL=""

if [ -f "${CONFIG_FILE}" ]; then
    CONFIGURED="true"
fi

if [ -f "${BACKUP_PRESERVED}" ]; then
    HAS_BACKUP="true"
fi

if [ -f "${SETTINGS_FILE}" ]; then
    SUB_TYPE=$(grep '^wizard_sub_type=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' ')
    SUB_URL=$(grep '^wizard_sub_url=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' ')
fi

# 输出 JSON
cat << EOF
{
    "configured": ${CONFIGURED},
    "has_backup": ${HAS_BACKUP},
    "sub_type": "${SUB_TYPE:-none}",
    "sub_url": "${SUB_URL}",
    "var_dir": "${VAR_DIR}",
    "backup_dir": "${BACKUP_DIR}"
}
EOF
