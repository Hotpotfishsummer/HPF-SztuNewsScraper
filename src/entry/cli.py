#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SZTU 新闻爬虫 - CLI 交互版本入口

这是 CLI 版本的独立入口，包含以下功能：
- 爬取新闻（标题和链接，或完整内容）
- 浏览已爬取的文章
- 按 URL 或标题搜索文章
- AI 分析新闻相关性
- 启动 Web UI (Streamlit)

用法:
    python main.py                   # 启动 CLI 交互菜单
    python main.py --web            # 直接启动 Web UI
    python main.py --analyze        # 直接进入 AI 分析模式
"""

import sys
import os
import argparse

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(project_root, 'src'))

from ..core.config import get_config
from ..core.logger import get_logger
from ..cli import run_interactive_menu, show_info

logger = get_logger(__name__)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='SZTU 新闻爬虫 - CLI 版本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                  # 启动交互菜单
  python main.py --list           # 列出所有文章
  python main.py --fetch-json 3   # 爬取 3 页新闻
  python main.py --web            # 启动 Web UI
  python main.py --analyze        # 启动 AI 分析
  python main.py --info           # 显示系统信息
        """
    )
    
    parser.add_argument(
        '--web',
        action='store_true',
        help='启动 Web UI (Streamlit)'
    )
    
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='启动 AI 分析模式'
    )
    
    parser.add_argument(
        '--fetch-json',
        type=int,
        metavar='PAGES',
        help='爬取指定页数的新闻 (JSON 格式)'
    )
    
    parser.add_argument(
        '--fetch-full',
        type=int,
        metavar='PAGES',
        help='爬取指定页数的完整新闻'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='列出所有已爬取的文章'
    )
    
    parser.add_argument(
        '--search-url',
        metavar='URL',
        help='按 URL 搜索文章'
    )
    
    parser.add_argument(
        '--search-title',
        metavar='KEYWORD',
        help='按标题关键词搜索文章'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='显示系统信息'
    )
    
    args = parser.parse_args()
    
    try:
        # 显示系统信息
        if args.info:
            show_info()
            return
        
        if args.web:
            from cli import start_web_ui
            start_web_ui()
        elif args.analyze:
            from cli import analyze_news_with_ai
            analyze_news_with_ai()
        elif args.fetch_json:
            from cli import fetch_news_json_pages
            logger.info(f"🔄 爬取 {args.fetch_json} 页新闻...")
            fetch_news_json_pages(args.fetch_json)
        elif args.fetch_full:
            from cli import fetch_full_news
            logger.info(f"🔄 爬取 {args.fetch_full} 页完整新闻...")
            fetch_full_news(args.fetch_full)
        elif args.list:
            from cli import list_articles
            list_articles()
        elif args.search_url:
            from cli import search_article_by_url
            search_article_by_url(args.search_url)
        elif args.search_title:
            from cli import search_articles_by_title
            search_articles_by_title(args.search_title)
        else:
            # 默认运行交互菜单
            show_info()
            run_interactive_menu()
    
    except KeyboardInterrupt:
        logger.info("\n👋 已退出")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
