#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """配置管理类"""
    
    def __init__(self, config_path: str = None):
        """
        初始化配置
        
        Args:
            config_path: 配置文件路径，默认为项目根目录的 config.json
        """
        if config_path is None:
            # 获取项目根目录
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'config.json'
            )
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: 配置文件格式错误
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"配置文件格式错误: {e.msg}",
                e.doc,
                e.pos
            )
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点号分隔的嵌套键
        
        Args:
            key: 配置键，例如 'gemini.api_key' 或 'logging.level'
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值，支持点号分隔的嵌套键
        
        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self) -> None:
        """保存配置到文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    @property
    def gemini_api_key(self) -> str:
        """获取 Gemini API Key"""
        return self.get('gemini.api_key', '')
    
    @property
    def gemini_model(self) -> str:
        """获取 Gemini 模型名称"""
        return self.get('gemini.model', 'gemini-2.0-flash')
    
    @property
    def gemini_temperature(self) -> float:
        """获取 Gemini 温度参数"""
        return self.get('gemini.temperature', 0.7)
    
    @property
    def gemini_max_tokens(self) -> int:
        """获取 Gemini 最大 token 数"""
        return self.get('gemini.max_tokens', 1000)
    
    @property
    def prompts(self) -> Dict[str, str]:
        """获取所有提示词"""
        return self.get('prompts', {})
    
    def get_prompt(self, prompt_name: str) -> str:
        """
        获取指定名称的提示词（必须在 config.json 中配置）
        
        Args:
            prompt_name: 提示词名称
            
        Returns:
            提示词内容
            
        Raises:
            KeyError: 如果提示词未在配置中找到
        """
        prompt = self.get(f'prompts.{prompt_name}', None)
        if prompt is None:
            raise KeyError(
                f"❌ 提示词 'prompts.{prompt_name}' 未在 config.json 中配置。"
                f"请参考 config.json.example.json 添加配置。"
            )
        return prompt
    
    @property
    def log_level(self) -> str:
        """获取日志级别"""
        return self.get('logging.level', 'INFO')
    
    @property
    def log_format(self) -> str:
        """获取日志格式"""
        return self.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    def validate(self) -> bool:
        """
        验证配置的有效性
        
        Returns:
            配置是否有效
        """
        # 检查必需的字段
        if not self.gemini_api_key:
            print("❌ 警告: 未配置 Gemini API Key")
            return False
        
        if not self.prompts:
            print("❌ 警告: 未配置提示词")
            return False
        
        return True
    
    @property
    def proxy_enabled(self) -> bool:
        """获取代理是否启用"""
        return self.get('proxy.enabled', False)
    
    @property
    def proxy_config(self) -> Optional[Dict[str, Any]]:
        """获取代理配置"""
        if not self.proxy_enabled:
            return None
        
        proxy_dict = self.get('proxy', {})
        
        # 构建代理 URL
        protocol = proxy_dict.get('protocol', 'http')
        host = proxy_dict.get('host', '127.0.0.1')
        port = proxy_dict.get('port', 7890)
        username = proxy_dict.get('username', '')
        password = proxy_dict.get('password', '')
        
        if username and password:
            proxy_url = f"{protocol}://{username}:{password}@{host}:{port}"
        else:
            proxy_url = f"{protocol}://{host}:{port}"
        
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def get_proxy_url(self) -> Optional[str]:
        """获取代理 URL（用于 requests 库）"""
        if not self.proxy_enabled:
            return None
        
        proxy_config = self.proxy_config
        return proxy_config.get('http') if proxy_config else None


# 创建全局配置实例
_config = None


def get_config() -> Config:
    """
    获取全局配置实例
    
    Returns:
        Config 实例
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> None:
    """重新加载配置"""
    global _config
    _config = None
