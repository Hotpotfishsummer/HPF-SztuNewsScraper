# 架构设计文档

## 项目概述

SZTU 新闻爬虫系统已升级为完整的分布式服务架构，支持三种运行模式：
- **CLI 模式**：命令行交互（向后兼容）
- **单容器模式**：Docker 单容器多进程（Supervisor）
- **多容器模式**：Docker Compose 容器编排

## 分层架构设计

### 1. 配置层 (`src/config/`)

统一的配置管理系统，支持优先级加载：环境变量 > .env 文件 > config.json > 默认值

**主要组件：**
- `config.py` - 配置加载与管理（单例模式）
- `env_loader.py` - 环境变量加载器
- `config_validator.py` - 配置验证器
- `schemas/` - 各模块的配置Schema

**使用示例：**
```python
from config import get_config

config = get_config()
dify_enabled = config.dify_enabled
api_key = config.get('dify.api_key', '')
```

### 2. 核心业务层 (`src/core/`)

**保留内容：**
- `scraper.py` - 网页爬虫
- `extract_news.py` - 新闻提取
- `models.py` - 数据模型

### 3. 存储层 (`src/storage/`)

数据持久化抽象层，支持多种存储后端

**主要组件：**
- `file_storage.py` - 文件存储
- `database.py` - 数据库存储（可选）
- `index_manager.py` - 索引管理

### 4. AI 分析层 (`src/ai/`)

AI 分析功能（Dify 工作流）

**保留内容：**
- `dify_client.py` - Dify 客户端
- `dify_workflow.py` - 工作流处理
- `analysis_recorder.py` - 结果记录

### 5. 调度器层 (`src/scheduler/`)

定时任务管理，基于 APScheduler

**主要组件：**
- `base_scheduler.py` - 抽象基类
- `apscheduler_impl.py` - APScheduler 实现
- `task_runner.py` - 任务执行引擎
- `monitors/` - 任务监控与指标

**配置文件：`schedule_config.json`**

```json
{
  "scheduler": {
    "scraper": {
      "enabled": true,
      "schedule": {
        "trigger": "cron",
        "hour": 0,
        "minute": 0
      },
      "params": {"pages": 3}
    },
    "analyzer": {
      "enabled": true,
      "schedule": {
        "trigger": "cron",
        "hour": 6,
        "minute": 0
      }
    }
  }
}
```

### 6. 服务启动层 (`services/`)

独立的服务启动脚本

**主要组件：**
- `scheduler_service.py` - 调度器服务
- `web_service.py` - Web 应用服务
- `manager.py` - 服务管理器（进程管理）

### 7. API 层 (`src/api/`)

RESTful API（可选，未来扩展）

**结构：**
- `app.py` - FastAPI 应用
- `v1/` - API v1 路由
- `middleware/` - 中间件
- `schemas/` - 请求/响应 Schema

### 8. Web 层 (`src/web/`)

Streamlit Web 应用

**结构：**
- `streamlit_app.py` - 主应用
- `pages/` - 多页应用
- `components/` - 可复用组件

### 9. CLI 层 (`src/cli/`)

命令行交互接口

**结构：**
- `main.py` - CLI 主菜单
- `commands/` - 各种命令
- `utils/` - CLI 工具函数

## 三种运行模式

### 模式1：CLI 交互模式（开发）

```bash
python run.py                 # 启动交互菜单
python run.py --info          # 显示系统信息
python run.py --web           # 启动 Streamlit（向后兼容）
```

**特点：**
- 保持向后兼容性
- 支持人工交互
- 开发调试友好

### 模式2：单容器模式（小规模部署）

```bash
python run.py --mode service --service-mode single
```

**特点：**
- 单个 Docker 容器
- Supervisor 管理多个进程
- 适合小规模应用

**Docker 启动：**
```bash
docker build -f infrastructure/docker/Dockerfile.base -t sztu-scraper:latest .
docker run -it -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config.json:/app/config.json \
  sztu-scraper:latest \
  python run.py --mode service --service-mode single
```

### 模式3：多容器模式（生产环境）

```bash
docker-compose up -d
```

**特点：**
- 多个独立容器
- 完整的容器编排
- 易于扩展和维护
- 适合生产环境

**服务组成：**
- `scheduler` - 定时任务调度器
- `web` - Streamlit Web 应用

## 环境变量配置

复制 `.env.example` 为 `.env`，填入实际值：

```bash
cp .env.example .env
```

**关键环境变量：**
```
DIFY_ENABLED=true
DIFY_API_KEY=xxx
GEMINI_API_KEY=xxx
SCHEDULER_ENABLED=true
```

## 文件结构

```
HPF-SztuNewsScraper/
├── src/
│   ├── config/                 # 配置管理
│   ├── core/                   # 核心业务（爬虫、提取）
│   ├── ai/                     # AI 分析
│   ├── storage/                # 数据存储
│   ├── scheduler/              # 定时任务
│   ├── services/               # 服务接口（可选）
│   ├── api/                    # REST API（可选）
│   ├── web/                    # Streamlit 应用
│   ├── cli/                    # 命令行接口
│   ├── main.py                 # 主程序入口（兼容）
│   ├── streamlit_app.py        # 原始 Streamlit
│   ├── scraper.py              # 爬虫模块
│   ├── ai/
│   └── logger_config.py        # 日志配置
│
├── services/
│   ├── scheduler_service.py    # 调度器服务
│   ├── web_service.py          # Web 服务
│   └── manager.py              # 服务管理器
│
├── infrastructure/
│   ├── docker/
│   │   ├── Dockerfile.base
│   │   ├── Dockerfile.scheduler
│   │   └── Dockerfile.web
│   ├── health-checks/
│   │   ├── scheduler-healthcheck.py
│   │   └── web-healthcheck.py
│   └── kubernetes/             # K8s 配置（可选）
│
├── data/
│   ├── articles/               # 爬取的文章
│   ├── logs/                   # 日志文件
│   └── cache/                  # 缓存数据
│
├── docs/
│   ├── ARCHITECTURE.md         # 本文档
│   ├── DEPLOYMENT.md           # 部署指南
│   └── CONFIG.md               # 配置指南
│
├── docker-compose.yml          # Docker 编排
├── run.py                      # 主启动脚本
├── schedule_config.json        # 任务配置
├── config.json                 # 应用配置
└── requirements.txt            # 依赖列表
```

## 数据流

### 爬虫任务流程

```
定时器触发 (00:00)
    ↓
TaskRunner.run_scraper_task()
    ↓
scraper.fetch_articles_with_details()
    ↓
保存文章到 articles/ 目录
    ↓
更新索引 articles/index.json
```

### 分析任务流程

```
定时器触发 (06:00)
    ↓
TaskRunner.run_analyzer_task()
    ↓
获取未分析的文章列表
    ↓
DifyWorkflowHandler.process_analysis()
    ↓
AnalysisRecorder.record_analysis()
    ↓
保存结果到 articles/analysis_records/
```

## 扩展建议

### 1. 添加数据库支持

在 `src/storage/database.py` 中实现 SQLAlchemy：
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(os.environ.get('DATABASE_URL', 'sqlite:///app.db'))
```

### 2. 添加 Redis 缓存

在 `src/ai/cache/redis_cache.py` 中实现缓存：
```python
import redis

redis_client = redis.from_url(os.environ.get('REDIS_URL'))
```

### 3. 添加 REST API

完成 `src/api/` 实现：
```bash
python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

### 4. 添加消息队列

使用 Celery + Redis 实现异步任务：
```python
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379')
```

## 监控与日志

### 日志配置

- 日志文件：`data/logs/scraper_*.log`
- 日志级别：通过 `LOG_LEVEL` 环境变量控制
- 日志格式：包含时间戳、日志级别、消息

### 健康检查

Docker Compose 已配置健康检查：
```yaml
healthcheck:
  test: ["CMD", "python", "infrastructure/health-checks/scheduler-healthcheck.py"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### 监控指标

可在 `src/scheduler/monitors/` 中添加：
- 任务执行时间
- 任务成功/失败率
- 爬虫性能指标
- 分析结果统计

## 故障排除

### 1. 导入错误

确保 `src` 目录在 Python 路径中：
```python
import sys
sys.path.insert(0, 'src')
```

### 2. 配置文件错误

验证 `config.json` 和 `.env` 文件：
```bash
python run.py --info
```

### 3. Docker 启动失败

查看日志：
```bash
docker logs sztu-scraper-scheduler
docker logs sztu-scraper-web
```

## 参考资源

- [APScheduler 文档](https://apscheduler.readthedocs.io/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Streamlit 文档](https://docs.streamlit.io/)
- [Python logging 文档](https://docs.python.org/3/library/logging.html)
