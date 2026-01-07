#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本 - SZTU 新闻爬虫 CLI 模式

直接执行此脚本即可启动交互菜单
使用方式: python start_cli.py
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

# 启动 CLI
if __name__ == "__main__":
    from src.cli.menu import run_interactive_menu
    run_interactive_menu()
