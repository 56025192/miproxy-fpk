#!/bin/bash
# MiProxy 订阅刷新守护进程
#
# 每 N 秒检查一次订阅（远程 URL 或本地文件），发现变化就重新生成 config.yaml 并重启 miproxy。
# 由 cmd/main 在 start 时启动，stop 时清理。
#
# 配置（环境变量）：
#   SUBSCRIPTION_URL    远程订阅 URL（优先）
#   SUBSCRIPTION_PATH   本地订阅文件路径
#   REFRESH_INTERVAL    刷新间隔（秒），默认 21600（6 小时），0 表示禁用
#   VAR_DIR             miproxy 数据目录（${TRIM_PKGVAR}）
#   SCRIPT_DIR          cmd 目录（脚本所在目录）

set -u

VAR_DIR="${VAR_DIR:-/vol1/@appdata/miproxy}"
SCRIPT_DIR="${SCRIPT_DIR:-/var/apps/miproxy/cmd}"
LOG_FILE="${VAR_DIR}/subscription_refresh.log"
PID_FILE="${VAR_DIR}/refresh_subscription.pid"
LOCK_FILE="${VAR_DIR}/refresh_subscription.lock"

SUBSCRIPTION_URL="${SUBSCRIPTION_URL:-}"
SUBSCRIPTION_PATH="${SUBSCRIPTION_PATH:-}"
REFRESH_INTERVAL="${REFRESH_INTERVAL:-21600}"

# 写出自己的 PID（让 main stop 时能找到）
echo $$ > "${PID_FILE}"

log_msg() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "${LOG_FILE}"
}

compute_hash() {
    sha256sum "$1" 2>/dev/null | awk '{print $1}'
}

# 检查是否仍是当前最新 PID（被 restart-refresh 时旧的会主动退）
is_current() {
    local current_pid
    current_pid=$(head -n 1 "${PID_FILE}" 2>/dev/null | tr -d '[:space:]')
    [ "${current_pid}" = "$$" ]
}

# 把订阅内容写入 subscription.yaml；返回 0 表示有更新，1 表示无变化或失败
refresh_subscription() {
    local new_file="${VAR_DIR}/subscription.yaml.new"
    local old_hash=""
    local new_hash=""

    if [ -n "${SUBSCRIPTION_URL}" ]; then
        if ! curl -fsSL --max-time 60 "${SUBSCRIPTION_URL}" -o "${new_file}" 2>>"${LOG_FILE}"; then
            log_msg "❌ 远程订阅拉取失败: ${SUBSCRIPTION_URL}"
            rm -f "${new_file}"
            return 1
        fi
    elif [ -n "${SUBSCRIPTION_PATH}" ] && [ -f "${SUBSCRIPTION_PATH}" ]; then
        if ! cp -f "${SUBSCRIPTION_PATH}" "${new_file}" 2>>"${LOG_FILE}"; then
            log_msg "❌ 本地订阅复制失败: ${SUBSCRIPTION_PATH}"
            rm -f "${new_file}"
            return 1
        fi
    else
        log_msg "未配置订阅来源或文件不存在，跳过刷新"
        return 1
    fi

    if [ ! -s "${new_file}" ]; then
        log_msg "❌ 订阅内容为空，跳过"
        rm -f "${new_file}"
        return 1
    fi

    if ! python3 -c "import yaml; yaml.safe_load(open('${new_file}', encoding='utf-8'))" 2>/dev/null; then
        log_msg "❌ 订阅 yaml 格式错误，跳过"
        rm -f "${new_file}"
        return 1
    fi

    if [ -f "${VAR_DIR}/subscription.yaml" ]; then
        old_hash=$(compute_hash "${VAR_DIR}/subscription.yaml")
    fi
    new_hash=$(compute_hash "${new_file}")

    if [ "${old_hash}" = "${new_hash}" ]; then
        log_msg "✅ 订阅内容未变化（hash=${new_hash:0:12}…）"
        rm -f "${new_file}"
        return 1
    fi

    log_msg "🔄 检测到订阅更新（hash: ${old_hash:0:12}… → ${new_hash:0:12}…）"
    mv "${new_file}" "${VAR_DIR}/subscription.yaml"
    chmod 666 "${VAR_DIR}/subscription.yaml"
    return 0
}

# 重新生成 config.yaml 并重启 miproxy
restart_miproxy() {
    log_msg "重新生成 config.yaml ..."
    if ! python3 "${SCRIPT_DIR}/merge_config.py" \
            "${VAR_DIR}/base.yaml" \
            "${VAR_DIR}/subscription.yaml" \
            "${VAR_DIR}/config.yaml" >>"${LOG_FILE}" 2>&1; then
        log_msg "❌ merge_config.py 失败，跳过重启"
        return 1
    fi
    chmod 666 "${VAR_DIR}/config.yaml"

    log_msg "重启 miproxy ..."
    bash "${SCRIPT_DIR}/main" stop >>"${LOG_FILE}" 2>&1 || true
    sleep 2
    bash "${SCRIPT_DIR}/main" start >>"${LOG_FILE}" 2>&1
    log_msg "✅ miproxy 已重启"
    return 0
}

cleanup() {
    log_msg "守护进程退出"
    rm -f "${PID_FILE}" "${LOCK_FILE}"
    exit 0
}
trap cleanup EXIT INT TERM

log_msg "════════════════════════════════════════"
log_msg "订阅刷新守护进程启动"
log_msg "  PID: $$"
log_msg "  VAR_DIR: ${VAR_DIR}"
log_msg "  URL: ${SUBSCRIPTION_URL:-（未设置）}"
log_msg "  PATH: ${SUBSCRIPTION_PATH:-（未设置）}"
log_msg "  刷新间隔: ${REFRESH_INTERVAL} 秒"
log_msg "════════════════════════════════════════"

# 启动后立即检查一次（不等第一次 tick）
sleep 5
if is_current && refresh_subscription; then
    restart_miproxy
fi

# 主循环
while true; do
    # 阻塞 sleep
    sleep "${REFRESH_INTERVAL}" 2>/dev/null || sleep 60

    # 不是当前 PID 就退出（被 restart-refresh 时旧的会主动退）
    if ! is_current; then
        log_msg "检测到新的守护进程接管，退出"
        exit 0
    fi

    if refresh_subscription; then
        restart_miproxy
    fi
done