#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
导出主要的配置接口
"""

import sys
import os

# 向上导入 config_manager 代理模块
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# 导入上级配置管理器
import config_manager as _config_mgr
from .env_loader import load_env_file, get_env, require_env

# 重新导出配置管理接口
get_config = _config_mgr.get_config
reload_config = _config_mgr.reload_config
EnvConfig = _config_mgr.EnvConfig

__all__ = [
    'get_config',
    'reload_config',
    'EnvConfig',
    'load_env_file',
    'get_env',
    'require_env',
]
