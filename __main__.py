#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SZTU 新闻爬虫 - 主模块入口

支持 python -m 调用
使用方式: python -m 或 python __main__.py
"""

import sys
import os

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))

# 确保 src 目录在 Python 路径中
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 加载环境配置
from src.config.env_loader import load_env_file

env_file = os.path.join(project_root, '.env')
if os.path.exists(env_file):
    load_env_file(env_file)

# 导入主程序入口
from src.main import main

if __name__ == "__main__":
    main()
