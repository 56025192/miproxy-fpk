#!/usr/bin/env python3
"""
MiProxy 配置合并脚本

设计原则：
- base.yaml 是系统基础配置，由 miproxy-fpk 管理（端口、面板、TUN、DNS、日志等）
- subscription.yaml 是用户订阅，只贡献 节点/分组/规则 等订阅字段
- 合并时使用白名单机制：subscription.yaml 中只有订阅字段会进入最终配置
- 这样无论订阅文件包含什么垃圾字段，都不会影响系统行为

允许从 subscription.yaml 进入最终配置的字段（白名单）：
  - proxies           节点列表
  - proxy-providers   节点提供者
  - proxy-groups      节点分组
  - rules             路由规则
  - rule-providers    规则提供者
"""

import sys
import os
import yaml
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


# subscription.yaml 中允许进入最终配置的字段白名单
# 其他字段（如 bind-address、allow-lan、dns、tun 等）一律剔除
ALLOWED_SUB_FIELDS = {
    'proxies',
    'proxy-providers',
    'proxy-groups',
    'rules',
    'rule-providers',
}


def clean_sub(sub_data, allowed_fields):
    """
    从 subscription.yaml 中只保留白名单字段，其他全部剔除。
    这是关键的安全机制——防止订阅文件污染系统配置。
    """
    if not isinstance(sub_data, dict):
        return {}
    cleaned = {}
    removed = []
    for k, v in sub_data.items():
        if k in allowed_fields:
            cleaned[k] = v
        else:
            removed.append(k)
    return cleaned, removed


def merge_configs(base_file, sub_file, output_file):
    """合并 base 和 subscription 配置"""
    log.info(f"读取基础配置: {base_file}")
    with open(base_file, 'r', encoding='utf-8') as f:
        base = yaml.safe_load(f) or {}

    log.info(f"基础配置字段数: {len(base)}")

    # 订阅文件不存在时，使用空配置
    sub_cleaned = {}
    sub_removed = []
    if os.path.exists(sub_file):
        log.info(f"读取订阅配置: {sub_file}")
        try:
            with open(sub_file, 'r', encoding='utf-8') as f:
                sub = yaml.safe_load(f) or {}
            
            if not isinstance(sub, dict):
                log.warning(f"subscription.yaml 格式错误：期望 dict，实际 {type(sub)}")
            else:
                # 白名单过滤：只保留订阅相关字段
                sub_cleaned, sub_removed = clean_sub(sub, ALLOWED_SUB_FIELDS)
                if sub_removed:
                    log.info(f"从订阅中剔除 {len(sub_removed)} 个非白名单字段（保护系统配置）:")
                    for k in sub_removed:
                        log.info(f"  - {k}")
        except Exception as e:
            log.warning(f"读取订阅配置失败: {e}，使用空订阅")
    else:
        log.info(f"订阅配置不存在，使用空订阅")

    # 合并：base 在前（base 字段优先），sub_cleaned 补充（白名单字段）
    merged = {**base, **sub_cleaned}

    # 写出
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# MiProxy 主配置（自动生成：base.yaml + subscription.yaml）\n")
        f.write("# 基础配置由系统管理，订阅内容可在 fnOS 应用设置面板修改\n")
        f.write(f"# base.yaml 字段: {len(base)}, subscription.yaml 白名单字段: {len(sub_cleaned)}, 冲突剔除: {len(sub_removed)}\n")
        f.write("---\n")
        yaml.dump(
            merged,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=4096
        )

    log.info(f"已生成: {output_file}")
    log.info(f"总字段数: {len(merged)}")
    log.info(f"白名单允许字段: {sorted(ALLOWED_SUB_FIELDS)}")


def main():
    if len(sys.argv) != 4:
        print("用法: merge_config.py <base.yaml> <subscription.yaml> <config.yaml>",
              file=sys.stderr)
        sys.exit(1)

    base_file = sys.argv[1]
    sub_file = sys.argv[2]
    output_file = sys.argv[3]

    if not os.path.exists(base_file):
        log.error(f"基础配置不存在: {base_file}")
        sys.exit(1)

    try:
        merge_configs(base_file, sub_file, output_file)
    except yaml.YAMLError as e:
        log.error(f"YAML 解析错误: {e}")
        sys.exit(2)
    except Exception as e:
        log.error(f"合并失败: {e}")
        sys.exit(3)


if __name__ == '__main__':
    main()
