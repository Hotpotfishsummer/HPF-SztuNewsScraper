#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一的配置管理模块 (v2.0)
基于 .env 文件的环境变量配置系统
支持：环境变量 > .env 文件 > 默认值
"""

import os
import sys
from pathlib import Path
from typing import Any, Optional

# 导入 python-dotenv 库
try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ 错误：需要安装 python-dotenv 库")
    print("   请运行: pip install python-dotenv")
    sys.exit(1)

# 导入日志模块（避免循环导入）
def _get_logger():
    """延迟导入日志模块，避免循环导入"""
    try:
        from .logger import get_logger
        return get_logger(__name__)
    except ImportError:
        import logging
        return logging.getLogger(__name__)

logger = _get_logger()

# 全局配置实例
_config_instance = None


class EnvConfig:
    """基于 .env 文件的配置管理类"""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            env_file: .env 文件路径，默认为项目根目录的 .env
        """
        if env_file is None:
            # 从项目根目录查找 .env 文件
            project_root = Path(__file__).parent.parent
            env_file = project_root / ".env"
        
        self.env_file = Path(env_file)
        self._load_env()
    
    def _load_env(self):
        """加载 .env 文件"""
        if self.env_file.exists():
            load_dotenv(self.env_file, override=True)
            logger.info(f"✅ .env 文件加载成功: {self.env_file}")
        else:
            logger.warning(f"⚠️ .env 文件不存在: {self.env_file}")
    
    def get(self, key: str, default: Any = None, var_type: type = str) -> Any:
        """
        获取配置值，支持类型转换
        
        Args:
            key: 环境变量键名（大小写敏感）
            default: 默认值
            var_type: 变量类型（str, int, float, bool）
            
        Returns:
            配置值或默认值
            
        Examples:
            >>> config.get("GEMINI_API_KEY")
            >>> config.get("DIFY_TIMEOUT", 60, int)
            >>> config.get("DEBUG", False, bool)
        """
        value = os.getenv(key)
        
        if value is None:
            return default
        
        # 类型转换
        if var_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif var_type == int:
            try:
                return int(value)
            except ValueError:
                logger.warning(f"⚠️ 无法将 {key}={value} 转换为 int，使用默认值 {default}")
                return default
        elif var_type == float:
            try:
                return float(value)
            except ValueError:
                logger.warning(f"⚠️ 无法将 {key}={value} 转换为 float，使用默认值 {default}")
                return default
        else:
            return value
    
    def get_list(self, key: str, default: Optional[list] = None, sep: str = ",") -> list:
        """
        获取列表配置（逗号分隔的字符串转换为列表）
        
        Args:
            key: 环境变量键名
            default: 默认值
            sep: 分隔符，默认为逗号
            
        Returns:
            列表
            
        Examples:
            >>> config.get_list("USER_INTERESTED_TOPICS")
            ['人工智能', '开源软件', '竞技编程']
        """
        value = os.getenv(key)
        if not value:
            return default or []
        
        return [item.strip() for item in value.split(sep)]
    
    def reload(self):
        """重新加载配置"""
        self._load_env()
        logger.info("✅ 配置已重新加载")
    
    # ========== Gemini API 属性 ==========
    
    @property
    def gemini_api_key(self) -> str:
        """获取 Gemini API 密钥"""
        return self.get("GEMINI_API_KEY", "")
    
    @property
    def gemini_model(self) -> str:
        """获取 Gemini 模型名称"""
        return self.get("GEMINI_MODEL", "gemini-2.5-flash")
    
    @property
    def gemini_temperature(self) -> float:
        """获取 Gemini 温度参数"""
        return self.get("GEMINI_TEMPERATURE", 1.0, float)
    
    @property
    def gemini_max_tokens(self) -> int:
        """获取 Gemini 最大输出 token 数"""
        return self.get("GEMINI_MAX_TOKENS", 5000, int)
    
    # ========== Dify API 属性 ==========
    
    @property
    def dify_enabled(self) -> bool:
        """Dify 是否启用"""
        return self.get("DIFY_ENABLED", False, bool)
    
    @property
    def dify_api_endpoint(self) -> str:
        """获取 Dify API 端点"""
        return self.get("DIFY_API_ENDPOINT", "http://localhost:8001/v1")
    
    @property
    def dify_api_key(self) -> str:
        """获取 Dify API 密钥"""
        return self.get("DIFY_API_KEY", "")
    
    @property
    def dify_timeout(self) -> int:
        """获取 Dify 请求超时时间（秒）"""
        return self.get("DIFY_TIMEOUT", 60, int)
    
    @property
    def dify_retry_times(self) -> int:
        """获取 Dify 重试次数"""
        return self.get("DIFY_RETRY_TIMES", 3, int)
    
    @property
    def dify_retry_delay(self) -> int:
        """获取 Dify 重试延迟（秒）"""
        return self.get("DIFY_RETRY_DELAY", 2, int)
    
    # ========== 代理配置属性 ==========
    
    @property
    def proxy_enabled(self) -> bool:
        """代理是否启用"""
        return self.get("PROXY_ENABLED", False, bool)
    
    @property
    def proxy_protocol(self) -> str:
        """获取代理协议"""
        return self.get("PROXY_PROTOCOL", "http")
    
    @property
    def proxy_host(self) -> str:
        """获取代理主机"""
        return self.get("PROXY_HOST", "127.0.0.1")
    
    @property
    def proxy_port(self) -> int:
        """获取代理端口"""
        return self.get("PROXY_PORT", 7890, int)
    
    @property
    def proxy_username(self) -> str:
        """获取代理用户名"""
        return self.get("PROXY_USERNAME", "")
    
    @property
    def proxy_password(self) -> str:
        """获取代理密码"""
        return self.get("PROXY_PASSWORD", "")
    
    @property
    def proxy_url(self) -> str:
        """构建完整的代理 URL"""
        if not self.proxy_enabled:
            return None
        
        protocol = self.proxy_protocol
        host = self.proxy_host
        port = self.proxy_port
        username = self.proxy_username
        password = self.proxy_password
        
        if username and password:
            return f"{protocol}://{username}:{password}@{host}:{port}"
        else:
            return f"{protocol}://{host}:{port}"
    
    # ========== 用户信息属性 ==========
    
    @property
    def user_name(self) -> str:
        """获取用户名"""
        return self.get("USER_NAME", "")
    
    @property
    def user_student_id(self) -> str:
        """获取学号"""
        return self.get("USER_STUDENT_ID", "")
    
    @property
    def user_gender(self) -> str:
        """获取性别"""
        return self.get("USER_GENDER", "男")
    
    @property
    def user_department(self) -> str:
        """获取学院"""
        return self.get("USER_DEPARTMENT", "")
    
    @property
    def user_major(self) -> str:
        """获取专业"""
        return self.get("USER_MAJOR", "")
    
    @property
    def user_grade(self) -> str:
        """获取年级"""
        return self.get("USER_GRADE", "")
    
    @property
    def user_class(self) -> str:
        """获取班级"""
        return self.get("USER_CLASS", "")
    
    @property
    def user_student_type(self) -> str:
        """获取学生类型"""
        return self.get("USER_STUDENT_TYPE", "本科生")
    
    @property
    def user_profile(self) -> dict:
        """获取用户完整信息（字典形式）"""
        return {
            'basic_info': {
                'name': self.user_name,
                'student_id': self.user_student_id,
                'gender': self.user_gender,
            },
            'education': {
                'department': self.user_department,
                'major': self.user_major,
                'grade': self.user_grade,
                'class': self.user_class,
                'student_type': self.user_student_type,
            },
            'interests': {
                'topics': self.get_list("USER_INTERESTED_TOPICS", []),
                'keywords': self.get_list("USER_INTERESTED_KEYWORDS", []),
            },
            'dislikes': {
                'topics': self.get_list("USER_DISLIKED_TOPICS", []),
                'keywords': self.get_list("USER_DISLIKED_KEYWORDS", []),
            },
            'notification_preferences': {
                'priority_departments': self.get_list("USER_PRIORITY_DEPARTMENTS", []),
                'exclude_categories': self.get_list("USER_EXCLUDE_CATEGORIES", []),
                'receive_urgent_only': self.get("USER_RECEIVE_URGENT_ONLY", False, bool),
            }
        }
    
    # ========== 调度器配置属性 ==========
    
    @property
    def scheduler_scraper_enabled(self) -> bool:
        """爬虫任务是否启用"""
        return self.get("SCHEDULER_SCRAPER_ENABLED", True, bool)
    
    @property
    def scheduler_scraper_cron(self) -> str:
        """爬虫任务 CRON 表达式"""
        return self.get("SCHEDULER_SCRAPER_CRON", "0 0 * * *")
    
    @property
    def scheduler_scraper_pages(self) -> int:
        """爬虫任务爬取页数"""
        return self.get("SCHEDULER_SCRAPER_PAGES", 3, int)
    
    @property
    def scheduler_analyzer_enabled(self) -> bool:
        """分析任务是否启用"""
        return self.get("SCHEDULER_ANALYZER_ENABLED", True, bool)
    
    @property
    def scheduler_analyzer_cron(self) -> str:
        """分析任务 CRON 表达式"""
        return self.get("SCHEDULER_ANALYZER_CRON", "0 6 * * *")
    
    @property
    def scheduler_analyzer_batch_size(self) -> int:
        """分析任务批处理大小"""
        return self.get("SCHEDULER_ANALYZER_BATCH_SIZE", 10, int)
    
    @property
    def scheduler_cleanup_enabled(self) -> bool:
        """清理任务是否启用"""
        return self.get("SCHEDULER_CLEANUP_ENABLED", False, bool)
    
    @property
    def scheduler_cleanup_cron(self) -> str:
        """清理任务 CRON 表达式"""
        return self.get("SCHEDULER_CLEANUP_CRON", "0 3 * * 0")
    
    @property
    def scheduler_cleanup_days_to_keep(self) -> int:
        """清理任务保留天数"""
        return self.get("SCHEDULER_CLEANUP_DAYS_TO_KEEP", 30, int)
    
    @property
    def scheduler_health_check_enabled(self) -> bool:
        """健康检查任务是否启用"""
        return self.get("SCHEDULER_HEALTH_CHECK_ENABLED", True, bool)
    
    @property
    def scheduler_health_check_interval_minutes(self) -> int:
        """健康检查间隔（分钟）"""
        return self.get("SCHEDULER_HEALTH_CHECK_INTERVAL_MINUTES", 5, int)
    
    # ========== 日志配置属性 ==========
    
    @property
    def log_level(self) -> str:
        """获取日志级别"""
        return self.get("LOG_LEVEL", "INFO")
    
    @property
    def log_format(self) -> str:
        """获取日志格式"""
        return self.get("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    @property
    def timezone(self) -> str:
        """获取时区"""
        return self.get("TIMEZONE", "Asia/Shanghai")
    
    # ========== API 服务配置属性 ==========
    
    @property
    def api_host(self) -> str:
        """获取 API 主机"""
        return self.get("API_HOST", "0.0.0.0")
    
    @property
    def api_port(self) -> int:
        """获取 API 端口"""
        return self.get("API_PORT", 8000, int)
    
    @property
    def api_reload(self) -> bool:
        """API 是否启用热重载"""
        return self.get("API_RELOAD", True, bool)
    
    @property
    def streamlit_port(self) -> int:
        """获取 Streamlit 端口"""
        return self.get("STREAMLIT_PORT", 8501, int)
    
    # ========== 数据存储属性 ==========
    
    @property
    def articles_data_dir(self) -> str:
        """获取文章数据目录"""
        return self.get("ARTICLES_DATA_DIR", "articles")
    
    @property
    def logs_dir(self) -> str:
        """获取日志目录"""
        return self.get("LOGS_DIR", "logs")
    
    # ========== 开发调试属性 ==========
    
    @property
    def debug(self) -> bool:
        """是否启用调试模式"""
        return self.get("DEBUG", False, bool)
    
    @property
    def environment(self) -> str:
        """获取环境类型"""
        return self.get("ENVIRONMENT", "development")
    
    def validate(self) -> tuple:
        """
        验证配置的有效性
        
        Returns:
            (是否有效, 错误列表)
        """
        errors = []
        
        # 检查必要的 API 密钥
        if not self.gemini_api_key and not self.dify_api_key:
            errors.append("至少需要配置 GEMINI_API_KEY 或 DIFY_API_KEY")
        
        # 检查用户信息
        if not self.user_department:
            errors.append("USER_DEPARTMENT 未配置")
        
        if not self.user_major:
            errors.append("USER_MAJOR 未配置")
        
        return len(errors) == 0, errors
    
def get_config() -> EnvConfig:
    """
    获取全局配置实例（单例模式）
    
    Returns:
        EnvConfig: 配置管理实例
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = EnvConfig()
    return _config_instance


def reload_config() -> None:
    """重新加载全局配置"""
    global _config_instance
    if _config_instance is not None:
        _config_instance.reload()
    else:
        _config_instance = EnvConfig()
