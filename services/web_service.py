#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web 服务启动脚本
启动 Streamlit 应用
"""

import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger_config import get_logger

logger = get_logger(__name__)


def start_web_service(host: str = '0.0.0.0', port: int = 8501) -> None:
    """启动 Web 服务
    
    Args:
        host: 监听的主机地址
        port: 监听的端口
    """
    logger.info("=" * 50)
    logger.info("🚀 启动 Web 服务")
    logger.info("=" * 50)
    
    # 确定 streamlit_app.py 的路径
    streamlit_app = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'src', 
        'streamlit_app.py'
    )
    
    if not os.path.exists(streamlit_app):
        logger.error(f"❌ Streamlit 应用不存在: {streamlit_app}")
        sys.exit(1)
    
    logger.info(f"📱 启动 Streamlit 应用: {streamlit_app}")
    logger.info(f"📱 访问地址: http://{host}:{port}")
    logger.info("")
    
    # 启动 Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            streamlit_app,
            "--server.address", host,
            "--server.port", str(port),
            "--logger.level", "info"
        ])
    except KeyboardInterrupt:
        logger.info("👋 Web 服务已停止")
    except Exception as e:
        logger.error(f"❌ 启动 Web 服务失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='启动 Streamlit Web 服务')
    parser.add_argument('--host', default='0.0.0.0', help='监听的主机地址')
    parser.add_argument('--port', type=int, default=8501, help='监听的端口')
    
    args = parser.parse_args()
    
    start_web_service(host=args.host, port=args.port)


if __name__ == '__main__':
    main()
