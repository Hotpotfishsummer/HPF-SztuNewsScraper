#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境变量加载器
支持从 .env 文件加载环境变量
"""

import os
from pathlib import Path
from typing import Dict
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..core.logger import get_logger

logger = get_logger(__name__)


def load_env_file(env_file: str = '.env') -> Dict[str, str]:
    """加载 .env 文件中的环境变量
    
    Args:
        env_file: .env 文件路径
        
    Returns:
        加载的环境变量字典
    """
    env_vars = {}
    
    if not os.path.exists(env_file):
        logger.debug(f"⚠️ .env 文件不存在: {env_file}")
        return env_vars
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                
                # 解析 KEY=VALUE 格式
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 移除引号
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    env_vars[key] = value
                    os.environ[key] = value
        
        logger.info(f"✅ 从 {env_file} 加载了 {len(env_vars)} 个环境变量")
    except IOError as e:
        logger.error(f"❌ 加载 .env 文件失败: {e}")
    
    return env_vars


def get_env(key: str, default: str = '') -> str:
    """获取环境变量
    
    Args:
        key: 环境变量名
        default: 默认值
        
    Returns:
        环境变量值或默认值
    """
    return os.environ.get(key, default)


def require_env(*keys: str) -> bool:
    """检查必需的环境变量是否存在
    
    Args:
        *keys: 环境变量名列表
        
    Returns:
        所有必需的环境变量是否都存在
    """
    missing = [k for k in keys if k not in os.environ]
    
    if missing:
        logger.warning(f"⚠️ 缺少必需的环境变量: {', '.join(missing)}")
        return False
    
    return True
