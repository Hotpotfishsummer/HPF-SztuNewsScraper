#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SZTU 新闻爬虫 - Docker 服务版本入口

这是服务版本的独立入口，包含以下后台服务：
- 定时任务调度器（自动爬取、分析新闻）
- Streamlit Web UI
- 健康检查接口

此版本设计用于 Docker 容器部署，支持：
- 持续运行和后台维护
- 定时爬取和分析新闻
- 通过 Web UI 交互
- 健康检查和监控

用法:
    python service.py                   # 启动所有后台服务
    python service.py --scheduler-only  # 仅启动定时调度器
    python service.py --web-only        # 仅启动 Web UI
"""

import sys
import os
import signal
import time
import argparse
import subprocess
from typing import Optional, List

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 添加 src 和 services 目录到路径
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'services'))

from ..core.config import get_config
from ..config.env_loader import load_env_file
from ..core.logger import get_logger

logger = get_logger(__name__)


class ServiceProcess:
    """服务进程管理"""
    
    def __init__(self, name: str, script: str, args: Optional[List[str]] = None):
        """初始化服务进程
        
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
        """启动服务进程"""
        if self.is_running:
            logger.warning(f"⚠️ 服务已启动: {self.name}")
            return True
        
        try:
            cmd = [sys.executable, self.script] + self.args
            logger.info(f"🚀 启动服务: {self.name}")
            logger.debug(f"   命令: {' '.join(cmd)}")
            
            # 在 Docker 中保持进程前台运行
            self.process = subprocess.Popen(
                cmd,
                stdout=None,
                stderr=None,
                text=True
            )
            
            time.sleep(0.5)
            
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
        """停止服务进程"""
        if not self.is_running or not self.process:
            return True
        
        try:
            logger.info(f"🛑 停止服务: {self.name}")
            
            self.process.terminate()
            
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ 进程无响应，强制杀死: {self.name}")
                self.process.kill()
                self.process.wait()
            
            self.is_running = False
            logger.info(f"✅ 服务已停止: {self.name}")
            return True
        
        except Exception as e:
            logger.error(f"❌ 停止服务失败: {self.name}, 错误: {e}")
            return False
    
    def is_alive(self) -> bool:
        """检查进程是否还活着"""
        if not self.is_running or not self.process:
            return False
        
        return self.process.poll() is None
    
    def wait(self) -> int:
        """等待进程结束"""
        if not self.process:
            return -1
        
        return self.process.wait()


class ServiceManager:
    """服务管理器"""
    
    def __init__(self):
        """初始化服务管理器"""
        self.services: List[ServiceProcess] = []
        self.running = False
        
        # 注册信号处理器
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """处理信号"""
        logger.info(f"\n📌 收到信号 {signum}，准备关闭...")
        self.stop_all()
        sys.exit(0)
    
    def add_service(self, name: str, script: str, args: Optional[List[str]] = None) -> None:
        """添加服务
        
        Args:
            name: 服务名称
            script: 启动脚本路径
            args: 启动参数列表
        """
        service = ServiceProcess(name, script, args)
        self.services.append(service)
    
    def start_all(self) -> bool:
        """启动所有服务"""
        logger.info("=" * 60)
        logger.info("🚀 启动所有服务")
        logger.info("=" * 60)
        
        success = True
        for service in self.services:
            if not service.start():
                success = False
        
        self.running = success
        return success
    
    def start_service(self, service_name: str) -> bool:
        """启动指定的服务
        
        Args:
            service_name: 服务名称
            
        Returns:
            是否启动成功
        """
        for service in self.services:
            if service.name == service_name:
                return service.start()
        
        logger.warning(f"❌ 服务不存在: {service_name}")
        return False
    
    def stop_all(self) -> None:
        """停止所有服务"""
        logger.info("\n" + "=" * 60)
        logger.info("🛑 停止所有服务")
        logger.info("=" * 60)
        
        for service in self.services:
            if service.is_running:
                service.stop()
        
        self.running = False
    
    def monitor(self) -> None:
        """监控所有服务"""
        logger.info("\n" + "=" * 60)
        logger.info("👁️  监控服务状态")
        logger.info("=" * 60)
        
        try:
            while self.running:
                time.sleep(5)
                
                for service in self.services:
                    if service.is_running and not service.is_alive():
                        logger.warning(f"⚠️ 服务已崩溃: {service.name}")
                        logger.info(f"🔄 尝试重启服务: {service.name}")
                        service.is_running = False
                        service.start()
        
        except KeyboardInterrupt:
            logger.info("\n📌 监控中断")
            self.stop_all()
    
    def run(self) -> None:
        """运行服务管理器"""
        if self.start_all():
            self.monitor()
        else:
            logger.error("❌ 启动服务失败")
            self.stop_all()
            sys.exit(1)


def show_info():
    """显示系统信息"""
    logger.info("=" * 60)
    logger.info("📰 SZTU 新闻爬虫 - Docker 服务版本")
    logger.info("=" * 60)
    logger.info("")
    
    config = get_config()
    logger.info("🔧 系统配置:")
    logger.info(f"  - Dify 启用: {config.dify_enabled}")
    logger.info(f"  - Gemini API Key: {'✅' if config.gemini_api_key else '❌'}")
    logger.info(f"  - 日志级别: {config.log_level}")
    logger.info(f"  - 用户资料: {'✅' if config.user_profile else '❌'}")
    logger.info("")
    
    logger.info("📡 后台服务:")
    logger.info("  - 定时调度器 (Scheduler)")
    logger.info("  - Streamlit Web UI")
    logger.info("")


def run_scheduler_service():
    """运行定时任务调度器"""
    try:
        from services.scheduler_service import SchedulerService
        
        logger.info("=" * 60)
        logger.info("⏰ 启动定时任务调度器")
        logger.info("=" * 60)
        
        scheduler = SchedulerService()
        scheduler.run()
    
    except Exception as e:
        logger.error(f"❌ 调度器启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)



def run_web_service():
    """运行 Streamlit Web UI"""
    try:
        logger.info("=" * 60)
        logger.info("🌐 启动 Streamlit Web UI")
        logger.info("=" * 60)
        
        import subprocess
        
        config = get_config()
        streamlit_app_path = os.path.join(project_root, "src", "web", "streamlit_app.py")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            streamlit_app_path,
            "--server.port", str(config.streamlit_port),
            "--server.address", "0.0.0.0"
        ])
    
    except Exception as e:
        logger.error(f"❌ Web 服务启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """主函数"""
    # 加载 .env 文件
    env_file = os.path.join(project_root, '.env')
    if os.path.exists(env_file):
        load_env_file(env_file)
    
    parser = argparse.ArgumentParser(
        description='SZTU 新闻爬虫 - Docker 服务版本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python service.py                    # 启动所有服务（推荐用于 Docker）
  python service.py --scheduler-only   # 仅启动调度器
  python service.py --web-only         # 仅启动 Web UI
  python service.py --info             # 显示系统信息
        """
    )
    
    parser.add_argument(
        '--scheduler-only',
        action='store_true',
        help='仅启动定时任务调度器'
    )
    
    parser.add_argument(
        '--web-only',
        action='store_true',
        help='仅启动 Streamlit Web UI'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='显示系统信息'
    )
    
    args = parser.parse_args()
    
    # 显示系统信息
    if args.info:
        show_info()
        return
    
    try:
        if args.scheduler_only:
            # 仅运行调度器
            run_scheduler_service()
        
        elif args.web_only:
            # 仅运行 Web UI
            run_web_service()
        
        else:
            # 默认：运行所有服务
            show_info()
            
            manager = ServiceManager()
            
            # 添加所有服务
            manager.add_service(
                "scheduler",
                os.path.join(project_root, "services", "scheduler_service.py")
            )
            
            manager.add_service(
                "web",
                os.path.join(project_root, "src", "web", "streamlit_app.py")
            )
            
            # 运行服务管理器
            manager.run()
    
    except KeyboardInterrupt:
        logger.info("\n👋 已退出")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
