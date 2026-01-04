#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SZTU 新闻爬虫 - 命令行版本
"""

import sys
import os

# 添加父目录到路径，以便导入 scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import load_articles, fetch_news_pages, fetch_news_pages_with_json, fetch_articles_with_details, get_all_articles_from_index, load_articles_index
from logger_config import get_logger

logger = get_logger(__name__)


def list_articles():
    """列出所有已爬取的文章"""
    articles = get_all_articles_from_index()
    if not articles:
        logger.info("📭 暂无文章记录")
        return
    
    logger.info(f"📰 已爬取文章列表 (共 {len(articles)} 篇)")
    for i, article in enumerate(articles, 1):
        logger.info(f"{i}. 【{article.get('category', 'N/A')}】{article.get('title', 'N/A')}")
        logger.info(f"   部门: {article.get('department', 'N/A')} | 时间: {article.get('publish_time', 'N/A')}")
        
        # 显示URL链接
        url = article.get('url', '')
        if url:
            logger.info(f"   链接: {url}")
        
        filename = article.get('filename', '')
        if filename:
            logger.info(f"   文件: {filename}")


def fetch_news():
    """爬取新闻并保存完整内容"""
    while True:
        try:
            pages = int(input("请输入要爬取的页数 (1-10): "))
            if 1 <= pages <= 10:
                break
            logger.warning("❌ 页数必须在 1-10 之间")
        except ValueError:
            logger.warning("❌ 请输入正确的页数")
    
    fetch_articles_with_details(pages)


def fetch_news_json():
    """爬取新闻标题和链接，保存为 JSON"""
    while True:
        try:
            pages = int(input("请输入要爬取的页数 (1-10): "))
            if 1 <= pages <= 10:
                break
            logger.warning("❌ 页数必须在 1-10 之间")
        except ValueError:
            logger.warning("❌ 请输入正确的页数")
    
    fetch_news_pages_with_json(pages)


def search_by_url():
    """根据 URL 查询文章信息"""
    url = input("\n请输入文章 URL: ").strip()
    
    if not url:
        logger.warning("❌ URL 不能为空")
        return
    
    index = load_articles_index()
    
    if url in index:
        article_info = index[url]
        logger.info("✅ 找到文章！")
        logger.info(f"标题: {article_info.get('title', 'N/A')}")
        logger.info(f"类别: {article_info.get('category', 'N/A')}")
        logger.info(f"部门: {article_info.get('department', 'N/A')}")
        logger.info(f"发布时间: {article_info.get('publish_time', 'N/A')}")
        logger.info(f"附件: {'有' if article_info.get('has_attachment') else '无'}")
        logger.info(f"文件: {article_info.get('filename', 'N/A')}")
        logger.info(f"爬取时间: {article_info.get('fetch_time', 'N/A')}")
    else:
        logger.warning(f"❌ 未找到该 URL 的文章")


def search_by_title():
    """根据标题关键词搜索文章"""
    keyword = input("\n请输入标题关键词: ").strip()
    
    if not keyword:
        logger.warning("❌ 关键词不能为空")
        return
    
    articles = get_all_articles_from_index()
    results = [a for a in articles if keyword.lower() in a.get('title', '').lower()]
    
    if results:
        logger.info(f"✅ 找到 {len(results)} 篇相关文章：")
        for i, article in enumerate(results, 1):
            logger.info(f"{i}. {article.get('title', 'N/A')}")
            logger.info(f"   文件: {article.get('filename', 'N/A')}")
            logger.info(f"   部门: {article.get('department', 'N/A')}")
    else:
        logger.warning(f"❌ 未找到包含 '{keyword}' 的文章")


def main():
    logger.info("=" * 40)
    logger.info("📰 SZTU 新闻爬虫")
    logger.info("=" * 40)
    
    while True:
        logger.info("\n请选择操作:")
        logger.info("1. 爬取新闻标题和链接（保存为 JSON）")
        logger.info("2. 爬取完整文章（标题、内容、时间等）")
        logger.info("3. 查看已爬取的新闻")
        logger.info("4. 根据 URL 查询文章")
        logger.info("5. 根据标题搜索文章")
        logger.info("6. 启动 Web 浏览界面")
        logger.info("7. 退出")
        
        choice = input("\n请输入选项 (1-7): ").strip()
        
        if choice == "1":
            fetch_news_json()
        elif choice == "2":
            fetch_news()
        elif choice == "3":
            list_articles()
        elif choice == "4":
            search_by_url()
        elif choice == "5":
            search_by_title()
        elif choice == "6":
            import subprocess
            import sys
            logger.info("🚀 启动 Streamlit Web 应用...")
            logger.info("📱 访问地址: http://localhost:8501")
            subprocess.run([
                sys.executable, "-m", "streamlit", "run",
                os.path.join(os.path.dirname(__file__), "streamlit_app.py")
            ])
        elif choice == "7":
            logger.info("👋 再见！")
            break
        else:
            logger.warning("❌ 无效的选项")


if __name__ == "__main__":
    main()
