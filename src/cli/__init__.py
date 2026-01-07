#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SZTU 新闻爬虫 - CLI 模块
包含命令行交互菜单和相关功能
"""

from .menu import (
    run_interactive_menu,
    show_info,
    list_articles,
    fetch_news,
    fetch_news_json,
    fetch_news_json_pages,
    fetch_full_news,
    search_by_url,
    search_by_title,
    search_article_by_url,
    search_articles_by_title,
    analyze_news_with_ai,
    start_web_ui
)

__all__ = [
    'run_interactive_menu',
    'show_info',
    'list_articles',
    'fetch_news',
    'fetch_news_json',
    'fetch_news_json_pages',
    'fetch_full_news',
    'search_by_url',
    'search_by_title',
    'search_article_by_url',
    'search_articles_by_title',
    'analyze_news_with_ai',
    'start_web_ui'
]
