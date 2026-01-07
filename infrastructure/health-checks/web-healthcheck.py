#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web 应用健康检查脚本
检查 Streamlit Web 应用是否正常运行
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src'))

from logger_config import get_logger

logger = get_logger(__name__)


def health_check():
    """执行健康检查
    
    Returns:
        0 if healthy, 1 if unhealthy
    """
    try:
        # 检查 Streamlit 应用文件是否存在
        streamlit_app = os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'src',
            'streamlit_app.py'
        )
        
        if not os.path.exists(streamlit_app):
            logger.error(f"❌ Streamlit 应用不存在: {streamlit_app}")
            return 1
        
        # 尝试导入关键模块
        try:
            import streamlit
            logger.info("✅ Streamlit 依赖正常")
        except ImportError as e:
            logger.error(f"❌ Streamlit 依赖缺失: {e}")
            return 1
        
        # 检查配置文件
        config_file = os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'config.json'
        )
        
        if not os.path.exists(config_file):
            logger.warning(f"⚠️ 配置文件不存在: {config_file}")
            # 不是致命错误，可以使用默认配置
        
        logger.info("✅ Web 应用健康检查通过")
        return 0
    
    except Exception as e:
        logger.error(f"❌ 健康检查失败: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(health_check())
