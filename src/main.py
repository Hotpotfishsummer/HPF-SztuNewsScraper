#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SZTU 新闻爬虫 - 命令行版本（简化启动器）
主要功能已迁移至 src/cli/menu.py，本文件保留供直接导入使用
"""

from .core.logger import get_logger
from .cli.menu import run_interactive_menu

logger = get_logger(__name__)


def main():
    """主入口：启动交互菜单"""
    logger.info("启动 SZTU 新闻爬虫 - CLI 交互模式...")
    run_interactive_menu()


if __name__ == "__main__":
    main()
