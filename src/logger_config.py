#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块 - 为全应用提供统一的日志管理
"""

import logging
import os
from datetime import datetime
from pathlib import Path


# 创建日志目录
LOGS_DIR = "logs"
Path(LOGS_DIR).mkdir(exist_ok=True)

# 日志文件路径
LOG_FILE = os.path.join(LOGS_DIR, f"scraper_{datetime.now().strftime('%Y%m%d')}.log")


def get_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    获取配置好的日志记录器
    
    Args:
        name: 日志记录器名称（通常使用模块名 __name__）
        level: 日志级别，默认为 INFO
        
    Returns:
        logging.Logger: 配置好的日志记录器实例
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加处理器
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 防止日志向上级传播
    logger.propagate = False
    
    return logger
