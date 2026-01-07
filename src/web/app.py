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

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from core.scraper import load_articles_index
from ..core.logger import get_logger

# 获取 articles 目录路径
ARTICLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'articles')

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
        color: #ffffff;
        font-size: 1rem;
    }
    
    .article-content p {
        color: #ffffff;
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


def load_analysis_records():
    """加载所有分析记录"""
    analysis_dir = os.path.join(ARTICLES_DIR, 'analysis_records')
    analysis_index_path = os.path.join(analysis_dir, 'analysis_index.json')
    
    if not os.path.exists(analysis_index_path):
        return {}
    
    try:
        with open(analysis_index_path, 'r', encoding='utf-8') as f:
            index = json.load(f)
            return index.get('analyses', {})
    except (json.JSONDecodeError, IOError):
        return {}


def load_single_analysis(filename: str) -> dict:
    """加载单个分析记录"""
    filepath = os.path.join(ARTICLES_DIR, 'analysis_records', filename)
    
    if not os.path.exists(filepath):
        return {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


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
    
    # 侧边栏 - 模式选择
    with st.sidebar:
        st.header("🎯 浏览模式")
        view_mode = st.radio(
            "选择浏览模式",
            options=["📰 文章浏览", "🤖 AI分析结果"],
            index=0
        )
        st.divider()
    
    # 根据模式选择不同的显示
    if view_mode == "📰 文章浏览":
        show_articles_mode(articles)
    else:
        show_analysis_mode(articles)


def show_articles_mode(articles):
    """显示文章浏览模式"""
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


def show_analysis_mode(articles):
    """显示 AI 分析结果模式"""
    # 加载分析记录
    analysis_records = load_analysis_records()
    
    if not analysis_records:
        st.warning("📭 暂无分析记录，请先运行 AI 分析")
        return
    
    # 构建分析结果列表
    analyses = []
    for filename, info in analysis_records.items():
        analyses.append({
            'filename': filename,
            'news_title': info.get('news_title', ''),
            'timestamp': info.get('timestamp', ''),
            'relevance_score': info.get('relevance_score', 0),
        })
    
    # 按相关性分数排序（降序）
    analyses.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    # 侧边栏 - 过滤
    with st.sidebar:
        st.header("📋 分析记录过滤")
        
        # 搜索框
        search_query = st.text_input(
            "🔍 搜索文章标题",
            placeholder="输入关键词...",
            help="搜索分析过的文章"
        )
        
        # 相关性评分过滤
        score_range = st.slider(
            "📊 相关性评分范围",
            min_value=0,
            max_value=10,
            value=(0, 10),
            step=1,
            help="按相关性评分过滤"
        )
        
        # 排序方式
        sort_by = st.radio(
            "排序方式",
            options=["相关性 (高到低)", "相关性 (低到高)", "时间 (最新)"],
            index=0
        )
        
        st.divider()
        st.info(f"📊 共有 {len(analyses)} 篇分析记录")
    
    # 过滤分析记录
    filtered_analyses = analyses
    
    if search_query:
        filtered_analyses = [
            a for a in filtered_analyses
            if search_query.lower() in a['news_title'].lower()
        ]
    
    # 按相关性评分过滤
    filtered_analyses = [
        a for a in filtered_analyses
        if score_range[0] <= a['relevance_score'] <= score_range[1]
    ]
    
    # 按选定的方式排序
    if sort_by == "相关性 (低到高)":
        filtered_analyses.sort(key=lambda x: x['relevance_score'])
    elif sort_by == "时间 (最新)":
        filtered_analyses.sort(key=lambda x: x['timestamp'], reverse=True)
    else:  # 默认：相关性（高到低）
        filtered_analyses.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    # 主内容区域
    col1, col2 = st.columns([1.2, 2])
    
    with col1:
        st.subheader("📋 分析列表")
        
        if not filtered_analyses:
            st.info("未找到匹配的分析记录")
        else:
            # 显示分析列表
            for idx, analysis in enumerate(filtered_analyses):
                # 创建包含相关性分数的按钮标签
                score_color = "🟢" if analysis['relevance_score'] >= 5 else ("🟡" if analysis['relevance_score'] >= 3 else "🔴")
                button_label = f"{score_color} [{analysis['relevance_score']}] {analysis['news_title'][:30]}{'...' if len(analysis['news_title']) > 30 else ''}"
                
                with st.container(border=False):
                    if st.button(
                        button_label,
                        key=f"analysis_{idx}",
                        use_container_width=True
                    ):
                        st.session_state.selected_analysis = idx
            
            st.caption(f"显示 {len(filtered_analyses)} 篇分析记录")
    
    with col2:
        st.subheader("🔍 分析详情")
        
        if 'selected_analysis' not in st.session_state:
            st.markdown('<div class="empty-state"><p>👈 从左侧选择一条记录查看分析详情</p></div>', unsafe_allow_html=True)
        else:
            idx = st.session_state.selected_analysis
            if 0 <= idx < len(filtered_analyses):
                analysis_item = filtered_analyses[idx]
                full_analysis = load_single_analysis(analysis_item['filename'])
                
                if full_analysis:
                    # 显示分析头部
                    st.markdown('<div class="content-header">', unsafe_allow_html=True)
                    st.markdown(f"### {analysis_item['news_title']}")
                    
                    # 显示相关性评分
                    col_score, col_time = st.columns(2)
                    with col_score:
                        score = analysis_item['relevance_score']
                        st.metric("相关性评分", f"{score}/10", "")
                    with col_time:
                        st.caption(f"📅 分析时间: {analysis_item['timestamp']}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 显示分析结果的关键部分
                    if 'analysis_output' in full_analysis:
                        analysis_output = full_analysis['analysis_output']
                        
                        # 显示摘要
                        if 'summary' in analysis_output:
                            st.subheader("📝 摘要")
                            st.write(analysis_output['summary'])
                        
                        # 显示相关性理由
                        if 'relevance_reason' in analysis_output:
                            st.subheader("📊 相关性分析")
                            st.write(analysis_output['relevance_reason'])
                    
                    # 显示用户档案信息（如果有）
                    if 'user_profile' in full_analysis:
                        with st.expander("👤 用户档案信息"):
                            user_profile = full_analysis['user_profile']
                            
                            # 教育信息
                            if 'education' in user_profile:
                                st.markdown("**教育信息**")
                                edu = user_profile['education']
                                st.write(f"""
                                - 院系: {edu.get('department', 'N/A')}
                                - 专业: {edu.get('major', 'N/A')}
                                - 年级: {edu.get('grade', 'N/A')}
                                - 班级: {edu.get('class', 'N/A')}
                                - 学生类型: {edu.get('student_type', 'N/A')}
                                """)
                            
                            # 兴趣信息
                            if 'interests' in user_profile:
                                st.markdown("**兴趣主题**")
                                interests = user_profile['interests']
                                if 'topics' in interests:
                                    for topic in interests['topics']:
                                        st.write(f"• {topic}")
                            
                            # 不喜欢的内容
                            if 'dislikes' in user_profile:
                                st.markdown("**不感兴趣的内容**")
                                dislikes = user_profile['dislikes']
                                if 'topics' in dislikes:
                                    for topic in dislikes['topics']:
                                        st.write(f"• {topic}")
                else:
                    st.warning("无法加载完整分析记录")


if __name__ == "__main__":
    main()
