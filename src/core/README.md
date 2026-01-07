# src/core - 核心基础设施模块

## 概述

`src/core` 模块包含应用程序的核心基础设施功能，包括日志、配置管理等核心服务。这层提供整个应用的基础支持，确保其他模块可以访问统一的日志和配置接口。

## 目录结构

```
src/core/
├── logger.py           # 日志配置和管理
├── config.py           # 环境变量配置管理
├── __init__.py         # 核心模块公开 API
├── scraper.py          # Web 爬虫功能（从 src 迁移）
└── analyzer/           # AI 分析模块
    ├── dify_workflow.py    # Dify 工作流处理
    └── analysis_recorder.py # 分析结果记录
```

## 核心模块说明

### logger.py - 日志管理

**功能**: 统一的日志配置和管理

**关键函数**:
- `get_logger(name, level=None) -> logging.Logger` - 获取配置好的日志对象

**特性**:
- 控制台输出 + 文件输出（logs/ 目录）
- 可配置日志级别 (LOG_LEVEL env var)
- 按日期轮转日志文件
- 防止重复处理器的注册

**使用示例**:
```python
from core.logger import get_logger

logger = get_logger(__name__)
logger.info("应用启动")
logger.error("出错了", exc_info=True)
```

### config.py - 配置管理

**功能**: 环境变量配置的统一管理，支持层级配置

**关键类**:
- `EnvConfig` - 配置对象，支持 dict-like 访问

**关键函数**:
- `get_config() -> EnvConfig` - 获取全局配置对象（单例）
- `reload_config()` - 重新加载配置

**配置层级** (优先级从高到低):
1. 环境变量
2. .env 文件
3. 硬编码默认值

**使用示例**:
```python
from core.config import get_config

config = get_config()
api_key = config.get('GEMINI_API_KEY')
dify_enabled = config.get('DIFY_ENABLED', default=False)
```

## 公开 API

通过 `src/core/__init__.py` 导出的公开接口:

```python
from core.logger import get_logger
from core.config import get_config, reload_config, EnvConfig
```

## 向后兼容性

在 `src/` 根目录下维护代理模块以支持旧的导入路径:
- `src/logger_config.py` - 重新导出 `core.logger.get_logger`
- `src/config_manager.py` - 重新导出 `core.config` 的接口

这意味着现存代码可以继续使用：
```python
from logger_config import get_logger  # 仍然可用
from config_manager import get_config  # 仍然可用
```

## 导入路径

推荐的导入方式（新代码）:
```python
from core.logger import get_logger
from core.config import get_config
```

旧的导入路径（仍支持但不推荐）:
```python
from logger_config import get_logger
from config_manager import get_config
```

## 环境变量配置

参见 `docs/CONFIG.md` 了解所有可用的环境变量和配置项。

主要环境变量:
- `LOG_LEVEL` - 日志级别 (默认: INFO)
- `LOG_FORMAT` - 日志格式
- `LOGS_DIR` - 日志目录 (默认: logs/)

## 依赖关系

- **logger.py**: 无外部依赖（仅使用标准库）
- **config.py**: 依赖 python-dotenv（.env 文件支持）
- **scraper.py**: 依赖 requests, BeautifulSoup4
- **analyzer/**: 依赖 Dify SDK

## 设计原则

1. **单一职责**: 每个模块负责一个明确的功能
2. **无循环依赖**: 避免模块间的循环导入
3. **可测试性**: 关键功能支持 mock 和单元测试
4. **后向兼容**: 通过代理模块维持旧导入路径

## 迁移历史

- v2.0: logger_config.py → core/logger.py
- v2.0: config_manager.py → core/config.py

