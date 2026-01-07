#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APScheduler 调度器实现
"""

import sys
import os
from typing import Callable, Dict, Any, List, Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..core.logger import get_logger
from scheduler.base_scheduler import BaseScheduler

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False

logger = get_logger(__name__)


class APSchedulerImpl(BaseScheduler):
    """APScheduler 实现"""
    
    def __init__(self):
        """初始化调度器"""
        super().__init__()
        
        if not APSCHEDULER_AVAILABLE:
            logger.error("❌ APScheduler 未安装，请运行: pip install apscheduler")
            raise ImportError("apscheduler is required")
        
        self.scheduler = BackgroundScheduler()
    
    def add_job(
        self,
        func: Callable,
        job_id: str,
        trigger: str = 'cron',
        **kwargs
    ) -> None:
        """添加定时任务
        
        Args:
            func: 要执行的函数
            job_id: 任务ID
            trigger: 触发器类型 ('cron', 'interval')
            **kwargs: 触发器参数
        """
        try:
            if trigger == 'cron':
                # Cron 表达式格式: second minute hour day month day_of_week
                # 例如: '0 0 * * *' 表示每天午夜 00:00:00
                cron_trigger = CronTrigger(**kwargs)
                self.scheduler.add_job(
                    func,
                    'cron',
                    id=job_id,
                    trigger=cron_trigger,
                    replace_existing=True,
                    misfire_grace_time=15  # 任务延迟执行的宽限期（秒）
                )
            elif trigger == 'interval':
                # Interval 触发器：例如 seconds=60 表示每 60 秒执行一次
                self.scheduler.add_job(
                    func,
                    'interval',
                    id=job_id,
                    replace_existing=True,
                    misfire_grace_time=15,
                    **kwargs
                )
            else:
                logger.error(f"❌ 不支持的触发器类型: {trigger}")
                return
            
            logger.info(f"✅ 任务已添加: {job_id} (trigger={trigger}, kwargs={kwargs})")
            self.jobs[job_id] = {
                'func': func,
                'trigger': trigger,
                'kwargs': kwargs
            }
        except Exception as e:
            logger.error(f"❌ 添加任务失败: {job_id}, 错误: {e}")
    
    def remove_job(self, job_id: str) -> None:
        """移除任务
        
        Args:
            job_id: 任务ID
        """
        try:
            self.scheduler.remove_job(job_id)
            self.jobs.pop(job_id, None)
            logger.info(f"✅ 任务已移除: {job_id}")
        except Exception as e:
            logger.error(f"❌ 移除任务失败: {job_id}, 错误: {e}")
    
    def start(self) -> None:
        """启动调度器"""
        if self.is_running:
            logger.warning("⚠️ 调度器已启动")
            return
        
        try:
            self.scheduler.start()
            self.is_running = True
            logger.info("✅ 调度器已启动")
        except Exception as e:
            logger.error(f"❌ 启动调度器失败: {e}")
    
    def stop(self) -> None:
        """停止调度器"""
        if not self.is_running:
            logger.warning("⚠️ 调度器未启动")
            return
        
        try:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("✅ 调度器已停止")
        except Exception as e:
            logger.error(f"❌ 停止调度器失败: {e}")
    
    def pause_job(self, job_id: str) -> None:
        """暂停任务
        
        Args:
            job_id: 任务ID
        """
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.pause()
                logger.info(f"✅ 任务已暂停: {job_id}")
            else:
                logger.warning(f"⚠️ 任务不存在: {job_id}")
        except Exception as e:
            logger.error(f"❌ 暂停任务失败: {job_id}, 错误: {e}")
    
    def resume_job(self, job_id: str) -> None:
        """恢复任务
        
        Args:
            job_id: 任务ID
        """
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.resume()
                logger.info(f"✅ 任务已恢复: {job_id}")
            else:
                logger.warning(f"⚠️ 任务不存在: {job_id}")
        except Exception as e:
            logger.error(f"❌ 恢复任务失败: {job_id}, 错误: {e}")
    
    def get_jobs(self) -> List[Dict[str, Any]]:
        """获取所有任务
        
        Returns:
            任务列表
        """
        jobs_list = []
        for job in self.scheduler.get_jobs():
            jobs_list.append({
                'id': job.id,
                'name': job.name,
                'trigger': str(job.trigger),
                'next_run_time': job.next_run_time,
                'func_ref': f"{job.func.__module__}:{job.func.__name__}"
            })
        return jobs_list
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """获取单个任务信息
        
        Args:
            job_id: 任务ID
            
        Returns:
            任务信息或 None
        """
        job = self.scheduler.get_job(job_id)
        if job:
            return {
                'id': job.id,
                'name': job.name,
                'trigger': str(job.trigger),
                'next_run_time': job.next_run_time,
                'func_ref': f"{job.func.__module__}:{job.func.__name__}"
            }
        return None
