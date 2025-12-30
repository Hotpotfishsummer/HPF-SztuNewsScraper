#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SZTU 新闻爬虫 - 主程序入口
"""

import sys
import os
import argparse
import subprocess

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from main import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SZTU 新闻爬虫')
    parser.add_argument('--web', action='store_true', help='启动 Streamlit Web 应用')
    
    args, unknown = parser.parse_known_args()
    
    if args.web:
        # 直接启动Streamlit应用
        subprocess.run([
            "streamlit", "run",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'streamlit_app.py')
        ] + unknown)
    else:
        # 启动交互式菜单
        main()


