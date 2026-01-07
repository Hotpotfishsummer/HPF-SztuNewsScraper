#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用入口模块
包含 CLI、Service、主入口三种启动方式

导入指南：
- 从 src.entry.main 导入主入口功能
- 从 src.entry.cli 导入 CLI 版本
- 从 src.entry.service 导入服务版本

推荐用法：
    python cli_entry.py              # 启动 CLI 版本
    python service_entry.py          # 启动服务版本
    python run.py [--service]        # 通过主入口启动
"""

from .main import run_cli, run_service, show_info

__all__ = ['run_cli', 'run_service', 'show_info']
