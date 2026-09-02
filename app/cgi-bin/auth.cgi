#!/bin/bash

# MiProxy 认证 CGI
# 验证用户输入的密钥是否匹配 settings.conf 中的 secret

echo "Content-Type: application/json"
echo ""

# 获取目录路径
PKGETC="${TRIM_PKGETC:-/var/apps/miproxy/etc}"
SETTINGS_FILE="${PKGETC}/settings.conf"

# 读取 POST 数据
POST_DATA=""
if [ "$REQUEST_METHOD" = "POST" ]; then
    read -n $CONTENT_LENGTH POST_DATA
fi

# 解析查询参数
ACTION="${QUERY_STRING%%&*}"
ACTION="${ACTION#action=}"

# 提取 JSON 字段
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

# ========== 登录验证 ==========
if [ "$ACTION" = "login" ]; then
    input_password=$(get_json_field "password")
    
    if [ -z "$input_password" ]; then
        cat << EOF
{
    "success": false,
    "error": "请输入密钥"
}
EOF
        exit 0
    fi
    
    # 读取保存的密钥
    saved_secret=""
    if [ -f "${SETTINGS_FILE}" ]; then
        saved_secret=$(grep '^wizard_secret=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' \n\r')
    fi
    
    # 验证（如果未设置密钥，则允许空密码登录）
    if [ -z "$saved_secret" ]; then
        # 未设置密钥，允许登录
        cat << EOF
{
    "success": true,
    "message": "验证通过（未设置密钥）"
}
EOF
    elif [ "$input_password" = "$saved_secret" ]; then
        cat << EOF
{
    "success": true,
    "message": "验证通过"
}
EOF
    else
        cat << EOF
{
    "success": false,
    "error": "密钥验证失败"
}
EOF
    fi
    exit 0
fi

# ========== 检查是否已认证 ==========
if [ "$ACTION" = "check" ]; then
    # 检查 settings.conf 中是否有密钥
    has_secret="false"
    if [ -f "${SETTINGS_FILE}" ]; then
        secret=$(grep '^wizard_secret=' "${SETTINGS_FILE}" 2>/dev/null | cut -d= -f2- | tr -d ' \n\r')
        if [ -n "$secret" ]; then
            has_secret="true"
        fi
    fi
    
    cat << EOF
{
    "has_secret": ${has_secret}
}
EOF
    exit 0
fi

# 默认
cat << EOF
{
    "success": false,
    "error": "未知操作"
}
EOF
