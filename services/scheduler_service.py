#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调度器服务启动脚本
管理所有定时任务的启动和停止
"""

import sys
import os
import json
import signal
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger_config import get_logger
from config import get_config
from scheduler import APSchedulerImpl
from scheduler.task_runner import TaskRunner

logger = get_logger(__name__)


class SchedulerService:
    """调度器服务"""
    
    def __init__(self, schedule_config_file: str = 'schedule_config.json'):
        """初始化调度器服务
        
        Args:
            schedule_config_file: 调度器配置文件路径
        """
        self.config = get_config()
        self.schedule_config_file = schedule_config_file
        self.schedule_config: Dict[str, Any] = {}
        self.scheduler = APSchedulerImpl()
        self.task_runner = TaskRunner()
        
        self._load_schedule_config()
        self._register_jobs()
    
    def _load_schedule_config(self) -> None:
        """加载调度器配置文件"""
        if not os.path.exists(self.schedule_config_file):
            logger.warning(f"⚠️ 调度器配置文件不存在: {self.schedule_config_file}")
            return
        
        try:
            with open(self.schedule_config_file, 'r', encoding='utf-8') as f:
                self.schedule_config = json.load(f)
            logger.info(f"✅ 调度器配置加载成功")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"❌ 加载调度器配置失败: {e}")
    
    def _register_jobs(self) -> None:
        """注册定时任务"""
        scheduler_config = self.schedule_config.get('scheduler', {})
        
        if not scheduler_config.get('enabled', True):
            logger.info("⏭️ 调度器已禁用")
            return
        
        # 注册爬虫任务
        scraper_config = scheduler_config.get('scraper', {})
        if scraper_config.get('enabled', True):
            job_id = scraper_config.get('job_id', 'scraper_daily')
            schedule = scraper_config.get('schedule', {})
            params = scraper_config.get('params', {})
            
            def scraper_task():
                return self.task_runner.run_scraper_task(**params)
            
            self.scheduler.add_job(
                scraper_task,
                job_id,
                trigger=schedule.get('trigger', 'cron'),
                **{k: v for k, v in schedule.items() if k != 'trigger'}
            )
        
        # 注册分析任务
        analyzer_config = scheduler_config.get('analyzer', {})
        if analyzer_config.get('enabled', True):
            job_id = analyzer_config.get('job_id', 'analyzer_daily')
            schedule = analyzer_config.get('schedule', {})
            params = analyzer_config.get('params', {})
            
            def analyzer_task():
                return self.task_runner.run_analyzer_task(**params)
            
            self.scheduler.add_job(
                analyzer_task,
                job_id,
                trigger=schedule.get('trigger', 'cron'),
                **{k: v for k, v in schedule.items() if k != 'trigger'}
            )
        
        # 注册清理任务
        cleanup_config = scheduler_config.get('cleanup', {})
        if cleanup_config.get('enabled', False):
            job_id = cleanup_config.get('job_id', 'cleanup_weekly')
            schedule = cleanup_config.get('schedule', {})
            params = cleanup_config.get('params', {})
            
            def cleanup_task():
                return self.task_runner.run_cleanup_task(**params)
            
            self.scheduler.add_job(
                cleanup_task,
                job_id,
                trigger=schedule.get('trigger', 'cron'),
                **{k: v for k, v in schedule.items() if k != 'trigger'}
            )
        
        # 注册健康检查任务
        health_check_config = scheduler_config.get('health_check', {})
        if health_check_config.get('enabled', True):
            job_id = health_check_config.get('job_id', 'health_check')
            schedule = health_check_config.get('schedule', {})
            
            def health_check_task():
                return self.task_runner.run_health_check_task()
            
            self.scheduler.add_job(
                health_check_task,
                job_id,
                trigger=schedule.get('trigger', 'interval'),
                **{k: v for k, v in schedule.items() if k != 'trigger'}
            )
        
        logger.info(f"✅ 已注册 {len(self.scheduler.jobs)} 个任务")
    
    def start(self) -> None:
        """启动调度器服务"""
        logger.info("=" * 50)
        logger.info("🚀 启动调度器服务")
        logger.info("=" * 50)
        
        # 列出所有任务
        jobs = self.scheduler.get_jobs()
        logger.info(f"📋 已注册的任务:")
        for job in jobs:
            logger.info(f"  - {job['id']}: {job['trigger']}")
        
        # 启动调度器
        self.scheduler.start()
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("✅ 调度器服务已启动，按 Ctrl+C 停止")
        
        # 保持进程运行
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self) -> None:
        """停止调度器服务"""
        logger.info("🛑 停止调度器服务...")
        self.scheduler.stop()
        logger.info("✅ 调度器服务已停止")
    
    def _signal_handler(self, signum, frame):
        """信号处理函数"""
        logger.info(f"⚠️ 收到信号 {signum}，准备关闭...")
        self.stop()
        sys.exit(0)
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """获取任务状态
        
        Args:
            job_id: 任务ID
            
        Returns:
            任务状态
        """
        job = self.scheduler.get_job(job_id)
        if job:
            last_run = self.task_runner.get_last_run_time(job_id)
            return {
                'id': job['id'],
                'name': job['name'],
                'trigger': job['trigger'],
                'next_run_time': str(job['next_run_time']),
                'last_run_time': str(last_run) if last_run else None
            }
        return {}


def main():
    """主函数"""
    try:
        service = SchedulerService()
        service.start()
    except Exception as e:
        logger.error(f"❌ 启动调度器服务失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
