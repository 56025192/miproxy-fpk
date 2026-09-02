#!/bin/bash

# MiProxy 配置状态检测 CGI
# 返回 JSON 格式的配置状态信息

echo "Content-Type: application/json"
echo ""

# 获取目录路径
APP_DIR="${TRIM_APPDEST:-/var/apps/miproxy}"
VAR_DIR="${TRIM_PKGVAR:-/var/apps/miproxy/var}"
PKGETC="${TRIM_PKGETC:-/var/apps/miproxy/etc}"
BACKUP_DIR="/tmp/miproxy_backup"

# 检查配置文件是否存在
CONFIG_FILE="${VAR_DIR}/config.yaml"
SETTINGS_FILE="${PKGETC}/settings.conf"
BACKUP_PRESERVED="${BACKUP_DIR}/.preserved"

# 默认返回值
CONFIGURED="false"
HAS_BACKUP="false"

# 检测逻辑：
# 1. 如果 VAR_DIR/config.yaml 存在 → 已配置
# 2. 如果 BACKUP_DIR/.preserved 存在 → 有保留数据（重装场景）

if [ -f "${CONFIG_FILE}" ]; then
    CONFIGURED="true"
fi

if [ -f "${BACKUP_PRESERVED}" ]; then
    HAS_BACKUP="true"
fi

# 读取保留的订阅信息（如果有）
SUB_TYPE="none"
SUB_URL=""
if [ -f "${SETTINGS_FILE}" ]; then
    SUB_TYPE=$(grep '^wizard_sub_type=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' ')
    SUB_URL=$(grep '^wizard_sub_url=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' ')
fi

# 输出 JSON
cat << EOF
{
    "configured": ${CONFIGURED},
    "has_backup": ${HAS_BACKUP},
    "sub_type": "${SUB_TYPE}",
    "sub_url": "${SUB_URL}",
    "var_dir": "${VAR_DIR}",
    "backup_dir": "${BACKUP_DIR}"
}
EOF
