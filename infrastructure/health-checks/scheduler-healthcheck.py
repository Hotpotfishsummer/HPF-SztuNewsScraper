#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调度器健康检查脚本
检查调度器服务是否正常运行
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src'))

from logger_config import get_logger
from scheduler import APSchedulerImpl

logger = get_logger(__name__)


def health_check():
    """执行健康检查
    
    Returns:
        0 if healthy, 1 if unhealthy
    """
    try:
        # 检查调度器配置文件是否存在
        schedule_config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'schedule_config.json'
        )
        
        if not os.path.exists(schedule_config_path):
            logger.error(f"❌ 调度器配置文件不存在: {schedule_config_path}")
            return 1
        
        # 尝试初始化调度器（测试依赖）
        try:
            scheduler = APSchedulerImpl()
            logger.info("✅ 调度器依赖正常")
        except ImportError as e:
            logger.error(f"❌ 调度器依赖缺失: {e}")
            return 1
        
        # 检查日志目录
        logs_dir = os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'data',
            'logs'
        )
        
        if not os.path.exists(logs_dir):
            try:
                os.makedirs(logs_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"❌ 无法创建日志目录: {e}")
                return 1
        
        logger.info("✅ 调度器健康检查通过")
        return 0
    
    except Exception as e:
        logger.error(f"❌ 健康检查失败: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(health_check())
