#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的配置管理系统
支持：环境变量 > .env文件 > config.json > 默认值
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..core.logger import get_logger

logger = get_logger(__name__)

# 全局配置单例
_config_instance = None


class Config:
    """配置管理类"""
    
    def __init__(self, config_file: Optional[str] = None):
        """初始化配置
        
        Args:
            config_file: 配置文件路径，默认为项目根目录的 config.json
        """
        self.config_file = config_file or self._find_config_file()
        self.data: Dict[str, Any] = {}
        self._load_config()
    
    @staticmethod
    def _find_config_file() -> str:
        """查找配置文件"""
        # 尝试从项目根目录找 config.json
        candidates = [
            'config.json',
            '../../../config.json',
            os.path.join(os.path.dirname(__file__), '..', '..', 'config.json'),
        ]
        
        for candidate in candidates:
            if os.path.exists(candidate):
                return os.path.abspath(candidate)
        
        # 返回默认路径（即使不存在）
        return os.path.abspath('config.json')
    
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                logger.info(f"✅ 配置文件加载成功: {self.config_file}")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"❌ 配置文件加载失败: {e}")
                self.data = {}
        else:
            logger.warning(f"⚠️ 配置文件不存在: {self.config_file}")
            self.data = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值
        
        支持点号分隔的嵌套访问，例如: 'dify.api_key'
        
        Args:
            key: 配置键，支持嵌套 (e.g., 'dify.api_key')
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        # 首先尝试从环境变量获取（转换为大写）
        env_key = key.upper().replace('.', '_')
        if env_key in os.environ:
            return os.environ[env_key]
        
        # 然后从配置数据获取
        keys = key.split('.')
        value = self.data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值
        
        Args:
            key: 配置键，支持嵌套
            value: 配置值
        """
        keys = key.split('.')
        current = self.data
        
        # 创建嵌套结构
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def save(self) -> bool:
        """保存配置到文件
        
        Returns:
            是否保存成功
        """
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ 配置已保存: {self.config_file}")
            return True
        except IOError as e:
            logger.error(f"❌ 保存配置失败: {e}")
            return False
    
    def validate(self) -> tuple[bool, list]:
        """验证必需的配置项
        
        Returns:
            (是否有效, 错误消息列表)
        """
        errors = []
        
        # 检查必需的配置
        required_keys = [
            'gemini.api_key',  # Gemini API 必需
        ]
        
        for key in required_keys:
            if not self.get(key):
                errors.append(f"缺少必需配置: {key}")
        
        return len(errors) == 0, errors
    
    # 便捷属性访问
    @property
    def dify_enabled(self) -> bool:
        return self.get('dify.enabled', False)
    
    @property
    def dify_api_key(self) -> str:
        return self.get('dify.api_key', '')
    
    @property
    def dify_api_endpoint(self) -> str:
        return self.get('dify.api_endpoint', 'http://localhost:8001/v1')
    
    @property
    def dify_timeout(self) -> int:
        return self.get('dify.timeout', 60)
    
    @property
    def dify_retry_times(self) -> int:
        return self.get('dify.retry_times', 3)
    
    @property
    def dify_retry_delay(self) -> int:
        return self.get('dify.retry_delay', 2)
    
    @property
    def gemini_api_key(self) -> str:
        return self.get('gemini.api_key', '')
    
    @property
    def gemini_model(self) -> str:
        return self.get('gemini.model', 'gemini-2.5-flash')
    
    @property
    def user_profile(self) -> Dict:
        return self.get('user_profile', {})
    
    @property
    def proxy_enabled(self) -> bool:
        return self.get('proxy.enabled', False)
    
    @property
    def proxy_config(self) -> Dict:
        return self.get('proxy', {})
    
    @property
    def log_level(self) -> str:
        return self.get('logging.level', 'INFO')


def get_config(config_file: Optional[str] = None) -> Config:
    """获取全局配置实例（单例）
    
    Args:
        config_file: 配置文件路径，仅在第一次调用时有效
        
    Returns:
        Config 实例
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = Config(config_file)
    
    return _config_instance


def reload_config(config_file: Optional[str] = None) -> Config:
    """重新加载配置
    
    清除全局单例，重新加载配置文件
    
    Args:
        config_file: 新的配置文件路径
        
    Returns:
        新的 Config 实例
    """
    global _config_instance
    _config_instance = None
    return get_config(config_file)
