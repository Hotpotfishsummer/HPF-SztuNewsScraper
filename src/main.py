#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SZTU 新闻爬虫 - 命令行版本
支持爬虫和 AI 分析功能
"""

import sys
import os
import json

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import load_articles, fetch_news_pages, fetch_news_pages_with_json, fetch_articles_with_details, get_all_articles_from_index, load_articles_index
from logger_config import get_logger
from ai.dify_workflow import DifyWorkflowHandler
from ai.analysis_recorder import AnalysisRecorder
from config import get_config

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


def analyze_news_with_ai():
    """使用 AI 分析新闻的相关性"""
    try:
        logger.info("\n" + "=" * 70)
        logger.info("🤖 AI 新闻相关性分析")
        logger.info("=" * 70)
        
        # 初始化处理器和记录器
        handler = DifyWorkflowHandler()
        recorder = AnalysisRecorder()
        config = get_config()
        
        logger.info("\n📋 选择分析方式:")
        logger.info("1. 分析单篇文章")
        logger.info("2. 批量分析所有文章")
        logger.info("3. 查看分析历史")
        logger.info("4. 检查分析结果有效性")
        logger.info("5. 返回主菜单")
        
        choice = input("\n请输入选项 (1-5): ").strip()
        
        if choice == "1":
            _analyze_single_article(handler, recorder, config)
        elif choice == "2":
            _analyze_all_articles(handler, recorder, config)
        elif choice == "3":
            _view_analysis_history(recorder)
        elif choice == "4":
            _check_analysis_validity(recorder)
        elif choice == "5":
            return
        else:
            logger.warning("❌ 无效的选项")
    
    except Exception as e:
        logger.error(f"❌ AI 分析出错: {str(e)}")
        import traceback
        traceback.print_exc()


def _analyze_single_article(handler, recorder, config):
    """分析单篇文章"""
    articles = get_all_articles_from_index()
    
    if not articles:
        logger.warning("❌ 暂无文章可分析")
        return
    
    # 列出文章
    logger.info("\n📰 可分析的文章列表:")
    for i, article in enumerate(articles, 1):
        logger.info(f"{i}. {article.get('title', 'N/A')[:50]}")
    
    try:
        choice = int(input("\n请选择文章编号: ").strip())
        if 1 <= choice <= len(articles):
            article = articles[choice - 1]
        else:
            logger.warning("❌ 无效的编号")
            return
    except ValueError:
        logger.warning("❌ 请输入正确的编号")
        return
    
    # 读取文章数据
    articles_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'articles')
    filename = article.get('filename', '')
    
    if not filename:
        logger.warning("❌ 文章文件名丢失")
        return
    
    filepath = os.path.join(articles_dir, filename)
    
    if not os.path.exists(filepath):
        logger.warning(f"❌ 文章文件不存在: {filepath}")
        return
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
    except Exception as e:
        logger.error(f"❌ 读取文章失败: {str(e)}")
        return
    
    # 获取用户资料
    user_profile = config.get('user_profile', {})
    user_profile_str = json.dumps(user_profile, ensure_ascii=False)
    
    logger.info(f"\n🔄 正在分析: {article.get('title', 'N/A')[:50]}...")
    
    # 检测文件是否已分析过（避免重复分析）
    source_filename = os.path.basename(filepath)
    if recorder.has_analysis(source_filename):
        logger.info(f"✅ 文件已完整分析过: {source_filename}")
        analysis_record = recorder.get_analysis_record(source_filename)
        if analysis_record:
            logger.info(f"   📋 分析时间: {analysis_record.get('timestamp')}")
            logger.info(f"   📊 相关性评分: {analysis_record.get('relevance_score')}")
            logger.info(f"   📝 新闻标题: {analysis_record.get('news_title')}")
        logger.info("⏭️  跳过分析（使用已有结果）")
        return
    
    logger.info(f"🆕 首次分析此文件: {source_filename}")
    
    # 处理工作流
    result_json = handler.process_workflow(user_profile_str, filepath)
    result = json.loads(result_json)
    
    if result.get('status') == 'success':
        logger.info("✅ 分析成功")
        
        analysis_data = result.get('data', {})
        logger.info(f"\n📊 分析结果:")
        logger.info(f"   标题: {analysis_data.get('title', 'N/A')}")
        logger.info(f"   摘要: {analysis_data.get('summary', 'N/A')[:100]}...")
        logger.info(f"   相关性评分: {analysis_data.get('relevance_score', 'N/A')}/10")
        logger.info(f"   评分原因: {analysis_data.get('relevance_reason', 'N/A')}")
        
        if result.get('dify_response_id'):
            logger.info(f"   Dify Response ID: {result.get('dify_response_id')}")
        
        # 记录分析结果
        try:
            record_path = recorder.record_analysis(
                user_profile=user_profile,
                news_data=news_data,
                analysis_result=analysis_data,
                news_file_path=filepath
            )
            logger.info(f"\n✅ 分析结果已记录: {record_path}")
        except Exception as e:
            logger.error(f"❌ 记录分析结果失败: {str(e)}")
    
    elif result.get('status') == 'pending_analysis':
        logger.info("⏳ Dify 未启用，工作流输入已验证...")
        logger.info("📝 输入已准备好，请在 Dify 中配置 API Key 并运行工作流处理")
        
        # 询问是否保存输入数据
        save = input("\n是否保存此分析的输入数据用于 Dify? (y/n): ").strip().lower()
        if save == 'y':
            # 保存临时输入数据
            temp_input = {
                'user_profile': user_profile,
                'news': {
                    'title': news_data.get('title'),
                    'content': news_data.get('content'),
                    'source': news_data.get('source'),
                    'publish_date': news_data.get('publish_date')
                }
            }
            
            temp_path = os.path.join(
                os.path.dirname(__file__), 'ai', 'test_data',
                f"input_{article.get('title', 'untitled')[:30]}.json"
            )
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(temp_input, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 输入数据已保存: {temp_path}")
    
    elif result.get('status') == 'error':
        logger.error(f"❌ 分析失败: {result.get('message')}")
        if result.get('errors'):
            for error in result.get('errors', []):
                logger.error(f"   - {error}")
    
    else:
        # 如果有分析结果，记录它
        if 'data' in result:
            try:
                record_path = recorder.record_analysis(
                    user_profile=user_profile,
                    news_data=news_data,
                    analysis_result=result.get('data', {}),
                    news_file_path=filepath
                )
                logger.info(f"✅ 分析结果已记录: {record_path}")
            except Exception as e:
                logger.error(f"❌ 记录分析结果失败: {str(e)}")


def _analyze_all_articles(handler, recorder, config):
    """批量分析所有文章"""
    articles = get_all_articles_from_index()
    
    if not articles:
        logger.warning("❌ 暂无文章可分析")
        return
    
    logger.info(f"\n🚀 准备批量分析 {len(articles)} 篇文章...")
    
    user_profile = config.get('user_profile', {})
    user_profile_str = json.dumps(user_profile, ensure_ascii=False)
    
    articles_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'articles')
    
    processed = 0
    skipped = 0
    failed = 0
    
    for idx, article in enumerate(articles, 1):
        filename = article.get('filename', '')
        title = article.get('title', '')
        
        if not filename:
            logger.warning(f"[{idx}/{len(articles)}] ⏭️  跳过（无文件名）: {title[:30]}...")
            skipped += 1
            continue
        
        filepath = os.path.join(articles_dir, filename)
        
        if not os.path.exists(filepath):
            logger.warning(f"[{idx}/{len(articles)}] ⏭️  跳过（文件不存在）: {title[:30]}...")
            skipped += 1
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
        except Exception as e:
            logger.error(f"[{idx}/{len(articles)}] ❌ 读取失败: {title[:30]}... ({str(e)})")
            failed += 1
            continue
        
        logger.info(f"[{idx}/{len(articles)}] 🔄 分析中: {title[:30]}...")
        
        # 检测文件是否已分析过
        source_filename = os.path.basename(filepath)
        if recorder.has_analysis(source_filename):
            logger.info(f"[{idx}/{len(articles)}] ✅ 已分析（跳过）: {title[:30]}...")
            skipped += 1
            continue
        
        try:
            result_json = handler.process_workflow(user_profile_str, filepath)
            result = json.loads(result_json)
            
            if result.get('status') == 'success':
                recorder.record_analysis(
                    user_profile=user_profile,
                    news_data=news_data,
                    analysis_result=result.get('data', {}),
                    news_file_path=filepath
                )
                logger.info(f"[{idx}/{len(articles)}] ✅ 成功")
                processed += 1
            elif result.get('status') == 'pending_analysis':
                logger.info(f"[{idx}/{len(articles)}] ⏳ 等待 Dify 处理")
                failed += 1
            else:
                logger.error(f"[{idx}/{len(articles)}] ❌ {result.get('message', '分析失败')}")
                failed += 1
        
        except Exception as e:
            logger.error(f"[{idx}/{len(articles)}] ❌ 分析异常: {str(e)}")
            failed += 1
    
    logger.info(f"\n📊 批量分析完成:")
    logger.info(f"   ✅ 成功: {processed}")
    logger.info(f"   ⏭️  跳过: {skipped}")
    logger.info(f"   ❌ 失败: {failed}")


def _view_analysis_history(recorder):
    """查看分析历史"""
    logger.info("\n📋 分析历史记录")
    
    history = recorder.get_analysis_history(limit=20)
    
    if not history:
        logger.info("📭 暂无分析记录")
        return
    
    logger.info(f"最近 {len(history)} 条记录:")
    for i, record in enumerate(history, 1):
        logger.info(f"{i}. {record.get('timestamp')} - {record.get('news_title', 'N/A')[:40]}")
        logger.info(f"   相关性评分: {record.get('relevance_score', 'N/A')}/10")
    
    # 显示统计信息
    stats = recorder.get_statistics()
    logger.info(f"\n📊 统计信息:")
    logger.info(f"   总分析数: {stats.get('total_analyses', 0)}")
    logger.info(f"   平均相关性评分: {stats.get('average_relevance_score', 0):.1f}/10")
    
    distribution = stats.get('score_distribution', {})
    logger.info(f"   高相关性 (8-10): {distribution.get('high', 0)}")
    logger.info(f"   中相关性 (5-7): {distribution.get('medium', 0)}")
    logger.info(f"   低相关性 (0-4): {distribution.get('low', 0)}")


def _check_analysis_validity(recorder):
    """检查分析结果的有效性"""
    logger.info("\n🔍 检查分析有效性")
    
    history = recorder.get_analysis_history(limit=50)
    
    if not history:
        logger.info("📭 暂无分析记录")
        return
    
    outdated = recorder.find_outdated_analyses()
    
    if outdated:
        logger.warning(f"⚠️ 发现 {len(outdated)} 个可能过期的分析结果:")
        for record in outdated:
            logger.warning(f"   - {record.get('filename')}")
            logger.warning(f"     原因: {record.get('details')}")
    else:
        logger.info("✅ 所有分析结果都是最新的")



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
        logger.info("6. 🤖 启动 AI 分析")
        logger.info("7. 启动 Web 浏览界面")
        logger.info("8. 退出")
        
        choice = input("\n请输入选项 (1-8): ").strip()
        
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
            analyze_news_with_ai()
        elif choice == "7":
            import subprocess
            import sys
            logger.info("🚀 启动 Streamlit Web 应用...")
            logger.info("📱 访问地址: http://localhost:8501")
            subprocess.run([
                sys.executable, "-m", "streamlit", "run",
                os.path.join(os.path.dirname(__file__), "streamlit_app.py")
            ])
        elif choice == "8":
            logger.info("👋 再见！")
            break
        else:
            logger.warning("❌ 无效的选项")


if __name__ == "__main__":
    main()
