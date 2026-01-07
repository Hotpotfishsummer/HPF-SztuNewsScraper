#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置验证器
验证配置的完整性和有效性
"""

import sys
import os
from typing import List, Dict, Any, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..core.logger import get_logger

logger = get_logger(__name__)


class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate_dify_config(dify_config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证 Dify 配置
        
        Args:
            dify_config: Dify 配置字典
            
        Returns:
            (是否有效, 错误消息列表)
        """
        errors = []
        
        if dify_config.get('enabled', False):
            if not dify_config.get('api_key'):
                errors.append("Dify API Key 不能为空")
            
            if not dify_config.get('api_endpoint'):
                errors.append("Dify API 端点不能为空")
            
            timeout = dify_config.get('timeout', 0)
            if timeout <= 0:
                errors.append("Dify 超时时间必须大于 0")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_gemini_config(gemini_config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证 Gemini 配置
        
        Args:
            gemini_config: Gemini 配置字典
            
        Returns:
            (是否有效, 错误消息列表)
        """
        errors = []
        
        if not gemini_config.get('api_key'):
            errors.append("Gemini API Key 不能为空")
        
        if not gemini_config.get('model'):
            errors.append("Gemini 模型不能为空")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_user_profile(user_profile: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证用户资料配置
        
        Args:
            user_profile: 用户资料字典
            
        Returns:
            (是否有效, 错误消息列表)
        """
        errors = []
        
        # 检查基本结构
        if 'basic_info' not in user_profile:
            errors.append("用户资料缺少 basic_info")
        
        if 'education' not in user_profile:
            errors.append("用户资料缺少 education")
        
        if 'interests' not in user_profile:
            errors.append("用户资料缺少 interests")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_proxy_config(proxy_config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证代理配置
        
        Args:
            proxy_config: 代理配置字典
            
        Returns:
            (是否有效, 错误消息列表)
        """
        errors = []
        
        if proxy_config.get('enabled', False):
            if not proxy_config.get('host'):
                errors.append("代理主机不能为空")
            
            port = proxy_config.get('port', 0)
            if port <= 0 or port > 65535:
                errors.append("代理端口必须在 1-65535 之间")
            
            protocol = proxy_config.get('protocol', 'http')
            if protocol not in ['http', 'https', 'socks5']:
                errors.append(f"不支持的代理协议: {protocol}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_scheduler_config(scheduler_config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证调度器配置
        
        Args:
            scheduler_config: 调度器配置字典
            
        Returns:
            (是否有效, 错误消息列表)
        """
        errors = []
        
        if 'scraper' in scheduler_config:
            scraper = scheduler_config['scraper']
            
            if scraper.get('enabled', False):
                if not scraper.get('schedule'):
                    errors.append("爬虫定时表达式不能为空")
                
                if scraper.get('pages', 0) <= 0:
                    errors.append("爬虫页数必须大于 0")
        
        if 'analyzer' in scheduler_config:
            analyzer = scheduler_config['analyzer']
            
            if analyzer.get('enabled', False):
                if not analyzer.get('schedule'):
                    errors.append("分析器定时表达式不能为空")
        
        return len(errors) == 0, errors


def validate_config(config_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """验证完整配置
    
    Args:
        config_data: 配置字典
        
    Returns:
        (是否有效, 错误消息列表)
    """
    all_errors = []
    
    # 验证 Gemini 配置
    if 'gemini' in config_data:
        valid, errors = ConfigValidator.validate_gemini_config(config_data['gemini'])
        all_errors.extend(errors)
    else:
        all_errors.append("缺少 Gemini 配置")
    
    # 验证 Dify 配置
    if 'dify' in config_data:
        valid, errors = ConfigValidator.validate_dify_config(config_data['dify'])
        all_errors.extend(errors)
    
    # 验证用户资料
    if 'user_profile' in config_data:
        valid, errors = ConfigValidator.validate_user_profile(config_data['user_profile'])
        all_errors.extend(errors)
    
    # 验证代理配置
    if 'proxy' in config_data:
        valid, errors = ConfigValidator.validate_proxy_config(config_data['proxy'])
        all_errors.extend(errors)
    
    # 验证调度器配置
    if 'scheduler' in config_data:
        valid, errors = ConfigValidator.validate_scheduler_config(config_data['scheduler'])
        all_errors.extend(errors)
    
    return len(all_errors) == 0, all_errors
