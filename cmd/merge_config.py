#!/usr/bin/env python3
"""
DEPRECATED: 此脚本已被 cmd/install_callback 和 cmd/config_callback 取代。

miproxy-fpk v3 之后，config.yaml 由 bash 脚本直接在 callback 中生成，
不再需要 base.yaml + subscription.yaml 的两阶段合并。

保留此文件仅为防止历史引用；如果被调用则直接退出。

参考:
  - cmd/install_callback   (写整个 config.yaml)
  - cmd/config_callback    (重写整个 config.yaml)
  - MetaCubeX GitBook: docs/proxy-providers.md
"""
import sys
sys.exit(0)