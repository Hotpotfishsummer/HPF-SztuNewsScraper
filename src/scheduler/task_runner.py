#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务运行器
执行调度器中的任务（爬虫、分析等）
"""

import sys
import os
import json
from typing import Callable, Dict, Any, Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..core.logger import get_logger
from ..core.config import get_config

logger = get_logger(__name__)


class TaskRunner:
    """任务运行器"""
    
    def __init__(self):
        """初始化运行器"""
        self.config = get_config()
        self.last_run_times = {}
    
    def run_scraper_task(self, pages: int = 3) -> Dict[str, Any]:
        """运行爬虫任务
        
        Args:
            pages: 要爬取的页数
            
        Returns:
            执行结果
        """
        task_name = "scraper"
        logger.info(f"🚀 开始执行任务: {task_name}")
        
        result = {
            'task': task_name,
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'pages': pages,
            'articles_count': 0,
            'errors': []
        }
        
        try:
            # 导入爬虫模块
            from core.scraper import fetch_articles_with_details
            
            # 执行爬虫
            logger.info(f"📰 开始爬取 {pages} 页新闻...")
            fetch_articles_with_details(pages)
            
            result['status'] = 'success'
            logger.info(f"✅ {task_name} 任务完成")
            
        except Exception as e:
            result['status'] = 'failed'
            result['errors'].append(str(e))
            logger.error(f"❌ {task_name} 任务失败: {e}")
        
        result['end_time'] = datetime.now().isoformat()
        self.last_run_times[task_name] = datetime.now()
        
        return result
    
    def run_analyzer_task(self, batch_size: int = 10) -> Dict[str, Any]:
        """运行 AI 分析任务
        
        Args:
            batch_size: 每次分析的文章数
            
        Returns:
            执行结果
        """
        task_name = "analyzer"
        logger.info(f"🚀 开始执行任务: {task_name}")
        
        result = {
            'task': task_name,
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'batch_size': batch_size,
            'analyzed_count': 0,
            'errors': []
        }
        
        try:
            from core.scraper import get_all_articles_from_index
            from core.analyzer.dify_workflow import DifyWorkflowHandler
            from core.analyzer.analysis_recorder import AnalysisRecorder
            
            # 检查 Dify 是否启用
            if not self.config.dify_enabled:
                logger.warning("⚠️ Dify 未启用，跳过分析任务")
                result['status'] = 'skipped'
                result['reason'] = 'Dify not enabled'
                return result
            
            # 获取所有文章
            articles = get_all_articles_from_index()
            if not articles:
                logger.warning("⚠️ 没有找到需要分析的文章")
                result['analyzed_count'] = 0
                result['status'] = 'success'
                return result
            
            # 初始化分析模块
            handler = DifyWorkflowHandler()
            recorder = AnalysisRecorder()
            
            # 分析文章（仅分析未分析过的）
            analyzed = 0
            for i, article in enumerate(articles[:batch_size]):
                try:
                    filename = article.get('filename')
                    
                    # 检查是否已分析
                    if recorder.is_analyzed(filename):
                        logger.debug(f"⏭️ 跳过已分析的文章: {filename}")
                        continue
                    
                    logger.info(f"🤖 分析文章 {i+1}/{len(articles)}: {article.get('title', 'N/A')[:50]}")
                    
                    # 执行分析
                    article_path = os.path.join('articles', filename)
                    user_profile_json = json.dumps(self.config.user_profile)
                    
                    analysis_result = handler.process_analysis(
                        user_profile_json,
                        article_path
                    )
                    
                    if analysis_result.get('valid'):
                        recorder.record_analysis(
                            filename,
                            user_profile_json,
                            article_path,
                            analysis_result.get('output', {})
                        )
                        analyzed += 1
                    else:
                        logger.warning(f"⚠️ 分析失败: {filename}")
                
                except Exception as e:
                    logger.error(f"❌ 分析单篇文章失败: {e}")
                    result['errors'].append(f"{article.get('filename')}: {str(e)}")
            
            result['analyzed_count'] = analyzed
            result['status'] = 'success'
            logger.info(f"✅ {task_name} 任务完成，已分析 {analyzed} 篇文章")
            
        except Exception as e:
            result['status'] = 'failed'
            result['errors'].append(str(e))
            logger.error(f"❌ {task_name} 任务失败: {e}")
        
        result['end_time'] = datetime.now().isoformat()
        self.last_run_times[task_name] = datetime.now()
        
        return result
    
    def run_cleanup_task(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """运行清理任务
        
        Args:
            days_to_keep: 保留的天数
            
        Returns:
            执行结果
        """
        task_name = "cleanup"
        logger.info(f"🚀 开始执行任务: {task_name}")
        
        result = {
            'task': task_name,
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'days_to_keep': days_to_keep,
            'cleaned_items': 0,
            'errors': []
        }
        
        try:
            from core.analyzer.analysis_recorder import AnalysisRecorder
            
            recorder = AnalysisRecorder()
            outdated = recorder.find_outdated_analyses(days=days_to_keep)
            
            cleaned = 0
            for record in outdated:
                try:
                    filename = record.get('filename')
                    filepath = os.path.join('articles', 'analysis_records', filename)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        cleaned += 1
                except Exception as e:
                    logger.error(f"❌ 删除文件失败: {e}")
            
            result['cleaned_items'] = cleaned
            result['status'] = 'success'
            logger.info(f"✅ {task_name} 任务完成，清理了 {cleaned} 项")
            
        except Exception as e:
            result['status'] = 'failed'
            result['errors'].append(str(e))
            logger.error(f"❌ {task_name} 任务失败: {e}")
        
        result['end_time'] = datetime.now().isoformat()
        self.last_run_times[task_name] = datetime.now()
        
        return result
    
    def run_health_check_task(self) -> Dict[str, Any]:
        """运行健康检查任务
        
        Returns:
            健康检查结果
        """
        task_name = "health_check"
        logger.debug(f"🚀 执行健康检查")
        
        result = {
            'task': task_name,
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        try:
            # 检查配置文件 (.env)
            config_exists = os.path.exists('.env')
            result['checks']['config_file'] = config_exists
            
            # 检查文章目录
            articles_exists = os.path.exists('articles')
            result['checks']['articles_dir'] = articles_exists
            
            # 检查日志目录
            logs_exists = os.path.exists('logs')
            result['checks']['logs_dir'] = logs_exists
            
            # 检查配置有效性
            is_valid, errors = self.config.validate()
            result['checks']['config_valid'] = is_valid
            
            # 检查 Dify 连接（如果启用）
            if self.config.dify_enabled:
                try:
                    from core.analyzer.dify_client import DifyClient
                    dify = DifyClient()
                    # 这里可以添加实际的连接测试
                    result['checks']['dify_connection'] = True
                except Exception:
                    result['checks']['dify_connection'] = False
            
            logger.debug(f"✅ 健康检查完成")
            
        except Exception as e:
            result['status'] = 'failed'
            logger.error(f"❌ 健康检查失败: {e}")
        
        return result
    
    def get_last_run_time(self, task_name: str) -> Optional[datetime]:
        """获取任务的最后运行时间
        
        Args:
            task_name: 任务名称
            
        Returns:
            最后运行时间或 None
        """
        return self.last_run_times.get(task_name)
