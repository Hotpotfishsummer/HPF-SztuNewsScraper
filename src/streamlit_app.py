#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SZTU 新闻爬虫 - Streamlit Web 应用
"""

import json
import os
import sys
import streamlit as st
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import load_articles_index, ARTICLES_DIR
from logger_config import get_logger

logger = get_logger(__name__)

# 页面配置
st.set_page_config(
    page_title="SZTU 新闻浏览",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    
    .article-item {
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3498db;
        background-color: #f8f9fa;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .article-item:hover {
        background-color: #e8f4f8;
        transform: translateX(4px);
    }
    
    .article-title {
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .article-meta {
        font-size: 0.85rem;
        color: #7f8c8d;
    }
    
    .category-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background-color: #3498db;
        color: white;
        border-radius: 20px;
        font-size: 0.75rem;
        margin-right: 0.5rem;
    }
    
    .content-header {
        border-bottom: 2px solid #3498db;
        padding-bottom: 1rem;
        margin-bottom: 2rem;
    }
    
    .article-content {
        line-height: 1.8;
        color: #1a1a1a;
        font-size: 1rem;
    }
    
    .article-content p {
        color: #1a1a1a;
        margin-bottom: 1rem;
    }
    
    .article-content h1,
    .article-content h2,
    .article-content h3,
    .article-content h4,
    .article-content h5,
    .article-content h6 {
        color: #2c3e50;
    }
    
    .article-footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #ecf0f1;
        font-size: 0.85rem;
        color: #555;
    }
    
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #95a5a6;
    }
</style>
""", unsafe_allow_html=True)


def get_article_content(filename: str) -> str:
    """获取文章内容"""
    filepath = os.path.join(ARTICLES_DIR, filename)
    
    if not os.path.exists(filepath):
        return ""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            article = json.load(f)
            return article.get('content', '')
    except (json.JSONDecodeError, IOError):
        return ""


def main():
    # 页面标题
    st.title("📰 SZTU 新闻浏览系统")
    
    # 加载文章索引
    index = load_articles_index()
    
    if not index:
        st.warning("📭 暂无文章记录，请先爬取新闻")
        return
    
    # 构建文章列表
    articles = []
    for url, info in index.items():
        articles.append({
            'url': url,
            'filename': info.get('filename', ''),
            'title': info.get('title', ''),
            'category': info.get('category', ''),
            'department': info.get('department', ''),
            'publish_date': info.get('publish_date', ''),
            'publish_time': info.get('publish_time', ''),
            'fetch_time': info.get('fetch_time', ''),
            'author': info.get('author', ''),
        })
    
    # 按发布时间倒序排列
    articles.sort(key=lambda x: x.get('publish_time', ''), reverse=True)
    
    # 侧边栏
    with st.sidebar:
        st.header("📋 搜索与过滤")
        
        # 搜索框
        search_query = st.text_input(
            "🔍 搜索标题或关键词",
            placeholder="输入文章标题...",
            help="输入关键词搜索文章"
        )
        
        # 分类过滤
        categories = sorted(set(a['category'] for a in articles if a['category']))
        selected_category = st.selectbox(
            "📁 按分类过滤",
            options=['全部'] + categories,
            index=0
        )
        
        # 部门过滤
        departments = sorted(set(a['department'] for a in articles if a['department']))
        selected_department = st.selectbox(
            "🏢 按部门过滤",
            options=['全部'] + departments,
            index=0
        )
        
        st.divider()
        st.info(f"📊 共有 {len(articles)} 篇文章")
    
    # 过滤文章
    filtered_articles = articles
    
    if search_query:
        filtered_articles = [
            a for a in filtered_articles
            if search_query.lower() in a['title'].lower()
        ]
    
    if selected_category != '全部':
        filtered_articles = [a for a in filtered_articles if a['category'] == selected_category]
    
    if selected_department != '全部':
        filtered_articles = [a for a in filtered_articles if a['department'] == selected_department]
    
    # 主内容区域
    col1, col2 = st.columns([1.2, 2])
    
    with col1:
        st.subheader("📰 文章列表")
        
        if not filtered_articles:
            st.info("未找到匹配的文章")
        else:
            # 显示文章列表
            for idx, article in enumerate(filtered_articles):
                with st.container(border=False):
                    if st.button(
                        f"{article['title'][:40]}{'...' if len(article['title']) > 40 else ''}",
                        key=f"article_{idx}",
                        use_container_width=True
                    ):
                        st.session_state.selected_article = idx
            
            st.caption(f"显示 {len(filtered_articles)} 篇文章")
    
    with col2:
        st.subheader("📖 文章内容")
        
        if 'selected_article' not in st.session_state:
            st.markdown('<div class="empty-state"><p>👈 从左侧选择文章查看内容</p></div>', unsafe_allow_html=True)
        else:
            idx = st.session_state.selected_article
            if 0 <= idx < len(filtered_articles):
                article = filtered_articles[idx]
                
                # 文章头部信息
                st.markdown('<div class="content-header">', unsafe_allow_html=True)
                st.markdown(f"### {article['title']}")
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.markdown(f"<span class='category-badge'>{article['category']}</span>", unsafe_allow_html=True)
                with col_b:
                    st.caption(f"🏢 {article['department']}")
                with col_c:
                    st.caption(f"📅 {article['publish_time'] or article['publish_date']}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 文章内容
                content = get_article_content(article['filename'])
                if content:
                    st.markdown(f'<div class="article-content">{content}</div>', unsafe_allow_html=True)
                else:
                    st.warning("无法加载文章内容")
                
                # 文章底部信息
                st.markdown('<div class="article-footer">', unsafe_allow_html=True)
                st.caption(f"✍️ 作者: {article['author']}")
                st.caption(f"🕐 爬取时间: {article['fetch_time']}")
                if article['url']:
                    st.markdown(f"[🔗 查看原文]({article['url']})")
                st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
