#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务管理器
管理多个服务的启动和停止
"""

import sys
import os
import subprocess
import signal
import time
from typing import Dict, Any, Optional, List
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger_config import get_logger

logger = get_logger(__name__)


class ServiceMode(Enum):
    """服务运行模式"""
    CLI = 'cli'                # 命令行交互模式
    SINGLE_CONTAINER = 'single'  # 单容器多进程模式（Supervisor）
    MULTI_CONTAINER = 'multi'    # 多容器编排模式（Docker Compose）


class Service:
    """服务定义"""
    
    def __init__(self, name: str, script: str, args: Optional[List[str]] = None):
        """初始化服务
        
        Args:
            name: 服务名称
            script: 启动脚本路径
            args: 启动参数列表
        """
        self.name = name
        self.script = script
        self.args = args or []
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
    
    def start(self) -> bool:
        """启动服务
        
        Returns:
            是否启动成功
        """
        if self.is_running:
            logger.warning(f"⚠️ 服务已启动: {self.name}")
            return True
        
        try:
            cmd = [sys.executable, self.script] + self.args
            logger.info(f"🚀 启动服务: {self.name}")
            logger.debug(f"   命令: {' '.join(cmd)}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 给进程一点时间来启动
            time.sleep(0.5)
            
            # 检查进程是否成功启动
            if self.process.poll() is not None:
                logger.error(f"❌ 服务启动失败: {self.name}")
                return False
            
            self.is_running = True
            logger.info(f"✅ 服务已启动: {self.name} (PID: {self.process.pid})")
            return True
        
        except Exception as e:
            logger.error(f"❌ 启动服务失败: {self.name}, 错误: {e}")
            return False
    
    def stop(self) -> bool:
        """停止服务
        
        Returns:
            是否停止成功
        """
        if not self.is_running or not self.process:
            return True
        
        try:
            logger.info(f"🛑 停止服务: {self.name}")
            
            # 首先尝试温和地停止
            self.process.terminate()
            
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # 如果温和停止失败，强制杀死
                logger.warning(f"⚠️ 温和停止失败，强制杀死进程: {self.name}")
                self.process.kill()
                self.process.wait()
            
            self.is_running = False
            logger.info(f"✅ 服务已停止: {self.name}")
            return True
        
        except Exception as e:
            logger.error(f"❌ 停止服务失败: {self.name}, 错误: {e}")
            return False
    
    def is_alive(self) -> bool:
        """检查服务是否运行中
        
        Returns:
            服务是否运行
        """
        if not self.process:
            return False
        
        return self.process.poll() is None and self.is_running


class ServiceManager:
    """服务管理器"""
    
    def __init__(self, mode: ServiceMode = ServiceMode.CLI):
        """初始化服务管理器
        
        Args:
            mode: 运行模式
        """
        self.mode = mode
        self.services: Dict[str, Service] = {}
        self._setup_services()
        self._setup_signal_handlers()
    
    def _setup_services(self) -> None:
        """设置服务"""
        services_dir = os.path.dirname(os.path.abspath(__file__))
        
        if self.mode == ServiceMode.CLI:
            # CLI 模式：只加载 CLI 交互
            # 无需在这里定义，由 run.py 处理
            pass
        
        elif self.mode == ServiceMode.SINGLE_CONTAINER:
            # 单容器模式：定义所有可用的服务
            self.services['scheduler'] = Service(
                'scheduler',
                os.path.join(services_dir, 'scheduler_service.py')
            )
            self.services['web'] = Service(
                'web',
                os.path.join(services_dir, 'web_service.py'),
                ['--host', '0.0.0.0', '--port', '8501']
            )
        
        elif self.mode == ServiceMode.MULTI_CONTAINER:
            # 多容器模式：由 Docker Compose 管理
            # 此处不需要定义
            pass
    
    def _setup_signal_handlers(self) -> None:
        """设置信号处理"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理函数"""
        logger.info(f"⚠️ 收到信号 {signum}，准备关闭所有服务...")
        self.stop_all()
        sys.exit(0)
    
    def start_service(self, service_name: str) -> bool:
        """启动单个服务
        
        Args:
            service_name: 服务名称
            
        Returns:
            是否启动成功
        """
        if service_name not in self.services:
            logger.error(f"❌ 服务不存在: {service_name}")
            return False
        
        return self.services[service_name].start()
    
    def stop_service(self, service_name: str) -> bool:
        """停止单个服务
        
        Args:
            service_name: 服务名称
            
        Returns:
            是否停止成功
        """
        if service_name not in self.services:
            logger.error(f"❌ 服务不存在: {service_name}")
            return False
        
        return self.services[service_name].stop()
    
    def start_all(self) -> bool:
        """启动所有服务
        
        Returns:
            是否全部启动成功
        """
        logger.info("=" * 50)
        logger.info(f"🚀 启动所有服务 (模式: {self.mode.value})")
        logger.info("=" * 50)
        
        success = True
        for service_name, service in self.services.items():
            if not service.start():
                success = False
        
        return success
    
    def stop_all(self) -> None:
        """停止所有服务"""
        logger.info("=" * 50)
        logger.info("🛑 停止所有服务")
        logger.info("=" * 50)
        
        for service_name, service in self.services.items():
            service.stop()
    
    def get_status(self) -> Dict[str, Any]:
        """获取所有服务状态
        
        Returns:
            服务状态字典
        """
        return {
            name: {
                'running': service.is_alive(),
                'pid': service.process.pid if service.process else None
            }
            for name, service in self.services.items()
        }
    
    def run_interactive(self) -> None:
        """以交互模式运行所有服务
        
        等待所有服务完成或用户中断
        """
        if not self.start_all():
            logger.error("❌ 启动服务失败")
            self.stop_all()
            sys.exit(1)
        
        logger.info("✅ 所有服务已启动")
        logger.info("📋 服务状态:")
        for name, status in self.get_status().items():
            status_str = "运行中" if status['running'] else "已停止"
            logger.info(f"  - {name}: {status_str} (PID: {status['pid']})")
        
        logger.info("\n按 Ctrl+C 停止所有服务...")
        
        # 保持进程运行
        try:
            while True:
                time.sleep(1)
                # 检查服务是否还在运行
                for name, service in self.services.items():
                    if not service.is_alive():
                        logger.warning(f"⚠️ 服务已停止: {name}")
        except KeyboardInterrupt:
            self.stop_all()
