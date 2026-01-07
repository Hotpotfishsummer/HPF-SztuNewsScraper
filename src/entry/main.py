#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SZTU 新闻爬虫 - 主程序入口辅助模块

此模块为初始化模块，应仅泛美可事无关的字符串和导入。
实际入口为根目录下的：
- main.py - 启动 CLI 交互模式
- service.py - 启动后台服务
"""

import sys
import os
import argparse
import subprocess

# 添加项目根目录和 src 目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'services'))

from ..core.config import get_config
from ..config.env_loader import load_env_file
from ..core.logger import get_logger

logger = get_logger(__name__)


def run_cli():
    """运行 CLI 版本（委托给根目录的 main.py）"""
    subprocess.run([
        sys.executable, 
        os.path.join(project_root, 'main.py')
    ] + sys.argv[1:])


def run_service():
    """运行服务版本（委托给根目录的 service.py）"""
    # 移除 --service 参数，其他参数传递给 service.py
    args = [arg for arg in sys.argv[1:] if arg != '--service']
    
    subprocess.run([
        sys.executable, 
        os.path.join(project_root, 'service.py')
    ] + args)


def show_info():
    """显示系统信息"""
    logger.info("=" * 60)
    logger.info("📰 SZTU 新闻爬虫 - 主入口")
    logger.info("=" * 60)
    logger.info("")
    logger.info("启动模式:")
    logger.info("  CLI 版本:")
    logger.info("    python main.py             # 启动 CLI 交互菜单（推荐）")
    logger.info("")
    logger.info("  Docker 服务版本:")
    logger.info("    python service.py         # 直接启动服务版本（推荐）")
    logger.info("")


def main():
    """主函数"""
    # 加载 .env 文件
    env_file = os.path.join(project_root, '.env')
    if os.path.exists(env_file):
        load_env_file(env_file)
    
    parser = argparse.ArgumentParser(
        description='SZTU 新闻爬虫 - 主程序入口',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
推荐用法:
  CLI 版本（本地开发/交互）:
    python main.py
    
  Docker 服务版本（容器部署）:
    python service.py
    
  Docker Compose 编排:
    docker-compose up
        """
    )
    
    parser.add_argument(
        '--service',
        action='store_true',
        help='启动 Docker 服务版本（定时调度器、API、Web UI）'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='显示启动信息'
    )
    
    # 保留向后兼容的选项
    parser.add_argument(
        '--web',
        action='store_true',
        help='（已废弃）使用 "python main.py --web" 代替'
    )
    
    parser.add_argument(
        '--mode',
        choices=['cli', 'service'],
        help='（已废弃）使用 "--service" 参数代替'
    )
    
    args, unknown = parser.parse_known_args()
    
    # 显示信息
    if args.info:
        show_info()
        sys.exit(0)
    
    try:
        if args.service or args.mode == 'service':
            # 启动服务版本
            logger.info("🚀 启动 Docker 服务版本...")
            run_service()
        else:
            # 默认启动 CLI 版本
            logger.info("🚀 启动 CLI 版本...")
            run_cli()
        logger.info("\n👋 已退出")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


