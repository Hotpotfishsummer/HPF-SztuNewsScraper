#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务调度器基类
定义调度器的基本接口
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, List, Optional
from datetime import datetime

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..core.logger import get_logger

logger = get_logger(__name__)


class BaseScheduler(ABC):
    """调度器基类"""
    
    def __init__(self):
        """初始化调度器"""
        self.jobs: Dict[str, Any] = {}
        self.is_running = False
    
    @abstractmethod
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
            trigger: 触发器类型 ('cron', 'interval', 'date')
            **kwargs: 触发器参数
        """
        pass
    
    @abstractmethod
    def remove_job(self, job_id: str) -> None:
        """移除定时任务
        
        Args:
            job_id: 任务ID
        """
        pass
    
    @abstractmethod
    def start(self) -> None:
        """启动调度器"""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """停止调度器"""
        pass
    
    @abstractmethod
    def pause_job(self, job_id: str) -> None:
        """暂停任务
        
        Args:
            job_id: 任务ID
        """
        pass
    
    @abstractmethod
    def resume_job(self, job_id: str) -> None:
        """恢复任务
        
        Args:
            job_id: 任务ID
        """
        pass
    
    @abstractmethod
    def get_jobs(self) -> List[Dict[str, Any]]:
        """获取所有任务
        
        Returns:
            任务列表
        """
        pass
    
    @abstractmethod
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """获取单个任务信息
        
        Args:
            job_id: 任务ID
            
        Returns:
            任务信息或 None
        """
        pass
