#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块 - 为全应用提供统一的日志管理
基于 .env 文件的日志配置
"""

import logging
import os
from datetime import datetime
from pathlib import Path

# 从 .env 文件加载配置
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 获取日志配置（从 .env 或使用默认值）
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGS_DIR = os.getenv('LOGS_DIR', 'logs')

# 创建日志目录
Path(LOGS_DIR).mkdir(exist_ok=True)

# 日志文件路径
LOG_FILE = os.path.join(LOGS_DIR, f"scraper_{datetime.now().strftime('%Y%m%d')}.log")

# 将字符串日志级别转换为 logging 常量
LOG_LEVEL_MAP = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}
LOG_LEVEL_NUMERIC = LOG_LEVEL_MAP.get(LOG_LEVEL.upper(), logging.INFO)


def get_logger(name: str, level: int = None) -> logging.Logger:
    """
    获取配置好的日志记录器
    
    Args:
        name: 日志记录器名称（通常使用模块名 __name__）
        level: 日志级别，默认使用 .env 配置的 LOG_LEVEL
        
    Returns:
        logging.Logger: 配置好的日志记录器实例
    """
    if level is None:
        level = LOG_LEVEL_NUMERIC
    
    logger = logging.getLogger(name)
    
    # 避免重复添加处理器
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
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
