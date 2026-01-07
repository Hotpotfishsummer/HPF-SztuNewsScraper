# src/scheduler - 任务调度模块

## 概述

`src/scheduler` 模块使用 APScheduler 实现定时任务调度。它支持周期性爬虫、定时分析和其他背景任务，可在服务模式下作为后台守护进程运行。

## 目录结构

```
src/scheduler/
├── __init__.py         # 调度模块初始化
├── scheduler_service.py    # 调度器服务主类
├── tasks.py            # 定时任务定义
└── jobs/              # （将来）任务分类目录
    ├── scraper_jobs.py
    ├── analysis_jobs.py
    └── maintenance_jobs.py
```

## 核心文件说明

### scheduler_service.py - 调度器服务

**功能**: 管理 APScheduler 实例和任务生命周期

**关键类**:
- `SchedulerService` - 调度器服务主类

**关键方法**:
- `__init__()` - 初始化调度器
- `start()` - 启动调度器
- `stop()` - 停止调度器
- `add_job()` - 添加新任务
- `remove_job()` - 删除任务
- `get_job(job_id)` - 获取任务信息
- `list_jobs()` - 列出所有任务

**生命周期**:
```
启动
  │
  ├─ 初始化 APScheduler
  ├─ 加载持久化的任务
  ├─ 启动调度线程
  ├─ 定期检查和执行任务
  └─ 更新任务状态
  
停止
  │
  ├─ 停止调度线程
  ├─ 保存任务状态
  ├─ 清理资源
  └─ 记录日志
```

### tasks.py - 任务定义

**功能**: 定义所有定时任务的具体实现

**关键任务**:

#### 爬虫任务
- `task_fetch_daily_news()` - 每日爬取新闻
  - 触发器: 每天 8:00 AM
  - 说明: 爬取最新的新闻并保存
  
- `task_fetch_weekly_full()` - 每周完整爬虫
  - 触发器: 每周一 0:00 AM
  - 说明: 执行完整的多页爬虫以获取所有新闻

#### 分析任务
- `task_analyze_daily()` - 每日 AI 分析
  - 触发器: 每天 9:00 AM
  - 说明: 分析新爬取的未分析文章
  
- `task_analyze_batch()` - 批量分析任务
  - 触发器: 每周五 22:00 PM
  - 说明: 批量分析所有新文章

#### 维护任务
- `task_cleanup_old_logs()` - 清理过期日志
  - 触发器: 每周日 3:00 AM
  - 说明: 删除超过 30 天的日志文件
  
- `task_backup_data()` - 备份数据
  - 触发器: 每天 23:00 PM
  - 说明: 备份重要数据文件

- `task_check_analysis_validity()` - 检查分析有效性
  - 触发器: 每周一 1:00 AM
  - 说明: 检查分析结果是否需要更新

#### 健康检查
- `task_health_check()` - 系统健康检查
  - 触发器: 每 10 分钟一次
  - 说明: 检查存储、配置、网络等系统状态

## 任务配置

### 从环境变量配置任务

```env
# 启用/禁用特定任务
SCHEDULER_ENABLE_FETCH=true
SCHEDULER_ENABLE_ANALYSIS=true
SCHEDULER_ENABLE_MAINTENANCE=true

# 任务频率配置
SCHEDULER_FETCH_HOURS=6        # 每隔 6 小时爬一次
SCHEDULER_ANALYSIS_HOURS=12    # 每隔 12 小时分析一次
SCHEDULER_CLEANUP_DAYS=7       # 清理 7 天前的数据

# 任务时间配置
SCHEDULER_DAILY_FETCH_TIME=08:00      # 每天 8 点
SCHEDULER_DAILY_ANALYSIS_TIME=09:00   # 每天 9 点
SCHEDULER_WEEKLY_BACKUP_DAY=sunday     # 每周日备份
SCHEDULER_WEEKLY_BACKUP_TIME=23:00     # 晚上 11 点
```

## 任务状态管理

### 任务状态
- `PENDING` - 等待执行
- `RUNNING` - 正在执行
- `SUCCESS` - 执行成功
- `FAILED` - 执行失败
- `SKIPPED` - 已跳过
- `PAUSED` - 已暂停

### 查看任务状态
```python
from scheduler import SchedulerService

scheduler = SchedulerService()
jobs = scheduler.list_jobs()

for job in jobs:
    print(f"Job: {job['id']}")
    print(f"  Status: {job['status']}")
    print(f"  Next Run: {job['next_run_time']}")
    print(f"  Last Run: {job['last_run_time']}")
    print(f"  Last Result: {job['last_result']}")
```

## 任务执行日志

所有任务执行都被记录，包括：

- **执行开始**: 任务名、触发器、参数
- **执行过程**: 关键步骤和中间结果
- **执行结束**: 结果、耗时、错误信息

日志存储位置: `logs/scheduler.log`

### 日志示例
```
[2024-01-07 08:00:00] INFO - Starting job: task_fetch_daily_news
[2024-01-07 08:01:30] INFO - Fetched 60 articles
[2024-01-07 08:02:00] INFO - Saved to articles/
[2024-01-07 08:02:05] INFO - Job completed successfully (elapsed: 125s)
```

## 错误处理和重试

### 自动重试
失败的任务支持自动重试：

```python
@scheduler_service.task(
    trigger='cron',
    hour='8',
    minute='0',
    retry_count=3,
    retry_delay=300  # 300 秒后重试
)
def task_fetch_daily_news():
    try:
        fetch_articles_with_details(pages=1)
    except Exception as e:
        logger.error(f"Failed to fetch news: {e}")
        raise  # 抛出异常触发重试
```

### 失败通知
任务失败时可发送通知：

```env
# 失败通知配置
SCHEDULER_FAILURE_NOTIFICATION=email
SCHEDULER_FAILURE_EMAIL=admin@example.com
```

## 启动调度器

### 作为服务运行
```bash
# 启动服务模式（包括调度器）
python src/entry/service.py

# 仅启动调度器
python src/entry/service.py --scheduler-only
```

### 直接运行
```python
from scheduler import SchedulerService

scheduler = SchedulerService()
scheduler.start()

# 保持主线程运行
import signal
signal.pause()  # Unix/Linux
```

## 监控和管理

### Web Dashboard（将来功能）
访问 http://localhost:8000/scheduler/dashboard 查看：
- 任务列表和状态
- 执行历史
- 性能统计
- 日志查看

### 命令行工具（将来功能）
```bash
# 列出所有任务
python tools/scheduler_cli.py list

# 运行特定任务
python tools/scheduler_cli.py run task_fetch_daily_news

# 暂停任务
python tools/scheduler_cli.py pause task_id

# 删除任务
python tools/scheduler_cli.py remove task_id
```

## 性能优化

### 并发执行
多个任务可以并发执行（由 APScheduler 管理）：

```env
# 最大并发任务数
SCHEDULER_MAX_WORKERS=4
```

### 优先级
任务可以设置优先级，高优先级任务优先执行：

```python
@scheduler_service.task(priority=10)  # 高优先级
def task_fetch_daily_news():
    ...

@scheduler_service.task(priority=1)   # 低优先级
def task_cleanup_old_logs():
    ...
```

### 超时保护
长时间运行的任务有超时保护：

```python
@scheduler_service.task(timeout=3600)  # 1 小时超时
def task_long_running():
    ...
```

## 持久化

任务状态和配置可以持久化存储：

- **存储位置**: `data/scheduler_state.json`
- **自动保存**: 每次任务更新后自动保存
- **恢复**: 服务启动时自动恢复任务

## 依赖关系

```
scheduler/
  ├─ apscheduler (任务调度框架)
  ├─ core.logger → 日志
  ├─ core.config → 配置
  ├─ core.scraper → 爬虫功能
  ├─ core.analyzer → AI 分析
  └─ storage → 数据存储
```

## 常见任务场景

### 场景 1: 每天早上 8 点爬虫，9 点分析
```env
SCHEDULER_FETCH_HOURS=24
SCHEDULER_DAILY_FETCH_TIME=08:00
SCHEDULER_ANALYSIS_HOURS=24
SCHEDULER_DAILY_ANALYSIS_TIME=09:00
```

### 场景 2: 每小时爬虫，每 6 小时分析
```env
SCHEDULER_FETCH_HOURS=1
SCHEDULER_ANALYSIS_HOURS=6
```

### 场景 3: 仅在工作时间运行（9-17点）
```env
SCHEDULER_WORKING_HOURS_ONLY=true
SCHEDULER_WORK_START_HOUR=9
SCHEDULER_WORK_END_HOUR=17
```

## 故障排除

### 任务不执行
```
检查清单:
1. 调度器已启动？ check logs/scheduler.log
2. 任务已添加？ python tools/scheduler_cli.py list
3. 触发时间已到？ 检查任务的 next_run_time
4. 网络/权限问题？ 查看任务日志的具体错误
```

### 任务执行缓慢
```
优化建议:
1. 减少并发任务数
2. 增加 SCHEDULER_MAX_WORKERS
3. 使用优先级调整关键任务
4. 检查爬虫/分析是否有网络瓶颈
```

