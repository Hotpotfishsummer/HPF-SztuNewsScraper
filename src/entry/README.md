# src/entry - 应用入口模块

## 概述

`src/entry` 模块包含所有应用程序的入口点。这是用户与应用交互的起点，根据启动方式不同，将控制流委托给相应的子系统（CLI、Service 或 Web）。

## 目录结构

```
src/entry/
├── __init__.py         # 入口模块初始化和导出
├── main.py            # 主路由器和启动分配器
├── cli.py             # CLI 模式入口
└── service.py         # 服务模式入口
```

## 核心文件说明

### main.py - 主路由器

**功能**: 应用的主入口点，负责参数解析和启动模式选择

**关键函数**:
- `main()` - 主入口函数，解析命令行参数并路由
- `run_cli()` - 启动 CLI 交互模式（委托给 cli_entry.py）
- `run_service()` - 启动服务模式（委托给 service_entry.py）
- `show_info()` - 显示系统信息和可用选项

**支持的启动参数**:
- `--info` - 显示启动信息
- `--service` - 启动服务模式
- `--mode MODE` - 指定启动模式（cli/service）

**执行流程**:
```
main()
  ├─ 解析命令行参数
  ├─ 加载配置 (.env)
  ├─ 初始化日志
  └─ 根据参数选择：
     ├─ --info → show_info()
     ├─ --service → run_service() → subprocess(service_entry.py)
     └─ (default) → run_cli() → subprocess(cli_entry.py)
```

**使用示例**:
```bash
# 显示系统信息
python src/entry/main.py --info

# 启动 CLI 交互模式
python src/entry/main.py

# 启动服务模式（后台服务）
python src/entry/main.py --service
```

### cli.py - CLI 入口

**功能**: CLI 模式的启动和参数处理

**关键函数**:
- `main()` - CLI 主函数，处理 CLI 特定的参数

**支持的子命令**:
- `--web` - 启动 Web UI（Streamlit）
- `--analyze` - 启动 AI 分析模式
- `--fetch-json` - 爬取新闻（JSON 格式）
- `--fetch-full` - 爬取完整新闻
- `--list` - 列出已爬取的文章
- `--search-url URL` - 按 URL 搜索
- `--search-title KEYWORD` - 按标题搜索
- `--info` - 显示 CLI 信息

**执行流程**:
```
cli.py
  ├─ 加载配置
  ├─ 初始化日志
  └─ 根据参数选择操作：
     ├─ --web → 启动 Streamlit
     ├─ --analyze → 启动 AI 分析
     ├─ --fetch-json PAGES → 爬取 JSON
     ├─ --fetch-full PAGES → 爬取完整文章
     ├─ --list → 列表显示
     ├─ --search-* → 搜索功能
     └─ (default) → 交互菜单 run_interactive_menu()
```

**使用示例**:
```bash
# 启动交互菜单
python src/entry/cli.py

# 爬取 5 页新闻
python src/entry/cli.py --fetch-json 5

# 搜索标题中包含"重要"的文章
python src/entry/cli.py --search-title 重要
```

### service.py - 服务模式入口

**功能**: 后台服务模式的启动和管理多个子服务

**关键类**:
- `ServiceProcess(cmd, name)` - 单个服务进程管理
  - `start()` - 启动服务
  - `stop()` - 停止服务
  - `is_alive()` - 检查是否运行
  - `wait()` - 等待服务完成

- `ServiceManager(services)` - 多服务协调器
  - `start_all()` - 启动所有服务
  - `stop_all()` - 停止所有服务
  - `wait_all()` - 等待所有服务完成
  - 自动重启崩溃的服务

**关键函数**:
- `run_scheduler_service()` - 启动任务调度器
- `run_api_service()` - 启动 FastAPI REST 服务
- `run_web_service()` - 启动 Streamlit Web UI
- `main()` - 服务主函数

**支持的参数**:
- `--scheduler-only` - 仅启动调度器
- `--api-only` - 仅启动 API
- `--web-only` - 仅启动 Web UI
- `--info` - 显示服务信息

**执行流程**:
```
service.py
  ├─ 加载配置
  ├─ 初始化日志
  ├─ 根据参数选择要启动的服务：
  │  ├─ --scheduler-only → 仅启动 SchedulerService
  │  ├─ --api-only → 仅启动 APIService
  │  ├─ --web-only → 仅启动 WebService
  │  └─ (default) → 启动所有三个服务
  │
  └─ ServiceManager 管理生命周期：
     ├─ 启动所有选中的服务
     ├─ 监控和自动重启
     ├─ 处理信号（SIGTERM、SIGINT）
     └─ 等待所有服务完成
```

**使用示例**:
```bash
# 启动所有服务（调度器、API、Web UI）
python src/entry/service.py

# 仅启动 FastAPI 服务
python src/entry/service.py --api-only

# 仅启动调度器和 Web UI
python src/entry/service.py --scheduler-only --web-only
```

## 启动流程关系图

```
运行用户命令
    ↓
┌─────────────────────────┐
│ run.py (根目录代理)      │
│ cli_entry.py (根目录代理)│
│ service_entry.py (代理)  │
└──────────┬──────────────┘
           ↓
┌─────────────────────────┐
│ src/entry/main.py      │
│ src/entry/cli.py       │
│ src/entry/service.py   │
└──────────┬──────────────┘
           ↓
┌─────────────────────────┐
│ src/cli/menu.py (菜单) │
│ src/scheduler/  (调度)  │
│ src/api/  (REST API)   │
│ src/web/  (Streamlit)  │
└─────────────────────────┘
```

## 根目录代理脚本

为了保持简洁的启动界面，在项目根目录保留代理脚本：

- `run.py` - 委托给 `src/entry/main.py`
- `cli_entry.py` - 委托给 `src/entry/cli.py`
- `service_entry.py` - 委托给 `src/entry/service.py`

## 设计原则

1. **单一职责**: 每个入口模块负责一种启动模式
2. **委托模式**: 使用 subprocess 来隔离各启动模式
3. **向后兼容**: 保留根目录代理脚本确保旧脚本继续工作
4. **灵活配置**: 通过命令行参数控制行为
5. **日志和监控**: 完整的日志记录和进程监控

## 依赖关系

- `src/core/` - 日志和配置
- `src/cli/` - CLI 菜单实现
- `src/scheduler/` - 任务调度
- `src/api/` - REST API 服务
- `src/web/` - Web UI

## 迁移历史

- v2.0: 从根目录迁移 run.py → src/entry/main.py
- v2.0: 从根目录迁移 cli_entry.py → src/entry/cli.py
- v2.0: 从根目录迁移 service_entry.py → src/entry/service.py

