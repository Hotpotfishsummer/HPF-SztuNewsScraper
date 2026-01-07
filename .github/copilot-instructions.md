# HPF-SztuNewsScraper Copilot 指导文件

## 项目概述

这是一个新闻爬虫项目，用于从深圳技术大学新闻网站爬取和分析新闻内容。

**项目名称**: HPF-SztuNewsScraper  
**主要语言**: Python 3.x  
**框架**: FastAPI, Streamlit, APScheduler

## 项目结构

```
HPF-SztuNewsScraper/
├── src/              # 核心源代码
│   ├── main.py       # 应用主入口 (CLI菜单启动器)
│   ├── entry/        # 程序入口模块
│   │   ├── main.py   # 主程序入口（启动脚本）
│   │   ├── cli.py    # CLI 应用入口
│   │   └── service.py # 服务启动器
│   ├── cli/          # 命令行交互工具
│   │   ├── menu.py   # 交互菜单
│   │   ├── commands/ # 命令处理模块
│   │   └── utils/    # CLI 工具函数
│   ├── core/         # 核心功能模块
│   │   ├── scraper.py    # 网络爬虫模块
│   │   ├── logger.py     # 日志配置
│   │   ├── config.py     # 核心配置
│   │   └── analyzer/     # 文章分析引擎
│   ├── config/       # 配置管理
│   │   ├── config.py # 配置类定义
│   │   ├── env_loader.py # .env 加载器
│   │   ├── config_validator.py # 配置验证器
│   │   └── schemas/  # 配置 schema 定义
│   ├── api/          # FastAPI 应用
│   │   └── app.py    # FastAPI 主应用
│   ├── web/          # Web UI (Streamlit)
│   │   ├── app.py    # Streamlit 应用
│   │   ├── pages/    # 页面模块
│   │   └── components/ # 组件模块
│   ├── scheduler/    # 定时任务调度
│   │   ├── base_scheduler.py # 调度器基类
│   │   ├── apscheduler_impl.py # APScheduler 实现
│   │   ├── task_runner.py # 任务执行器
│   │   └── monitors/ # 监控模块
│   ├── storage/      # 数据存储
│   │   └── manager.py # 存储管理器
│   └── test/         # 单元测试
├── services/         # 微服务模块
│   ├── manager.py
│   ├── scheduler_service.py
│   └── web_service.py
├── infrastructure/   # 基础设施配置
│   ├── docker/       # Docker 配置
│   └── health-checks/ # 健康检查脚本
├── articles/         # 爬取的文章数据 (JSON 格式)
│   └── analysis_records/ # 分析记录
├── docs/            # 文档
│   ├── ARCHITECTURE.md  # 架构文档
│   ├── CONFIG.md       # 配置说明
│   └── DEPLOYMENT.md   # 部署指南
├── .env             # 环境配置（单一配置文件）
├── .env.example     # 配置模板
├── requirements.txt  # Python 依赖
├── environment.yml  # Conda 环境配置
├── docker-compose.yml # Docker Compose 配置
├── main.py          # 兼容性启动脚本
├── run.py           # 应用启动脚本
├── service.py       # 服务启动脚本
└── README.md        # 项目说明
```

## 开发规范

### 代码风格
- 遵循 PEP 8 规范
- 使用 Python 类型提示
- 函数和模块需要有 docstring 注释

### 文件命名
- Python 模块使用 `snake_case`（小写加下划线）
- 类名使用 `PascalCase`
- 常量使用 `UPPER_SNAKE_CASE`

### 文档规范
⚠️ **所有文档必须使用 Markdown (.md) 格式**
- 所有项目文档、说明、配置指南等都必须使用 `.md` 格式
- 禁止使用 `.txt`、`.py`、`.json` 或其他非 Markdown 格式来编写文档
- 包括：README、配置说明、架构文档、部署指南、变更日志等
- 可在 `docs/` 目录中组织各类文档
- Markdown 文件应包含清晰的标题、目录和代码块（使用适当的语言标记）

### 导入顺序
1. 标准库
2. 第三方库
3. 本地项目模块

### 配置管理规范
⚠️ **重要：从 v2.0 起，只使用 .env 文件进行配置**
- 所有配置参数都在 `.env` 文件中定义
- 复制 `.env.example` 为 `.env` 并填入实际值
- **不要将 .env 文件提交到 Git**（已在 .gitignore 中）
- 不要在代码中硬编码敏感信息（API 密钥、密码等）
- 参考 `docs/CONFIG.md` 了解所有可用配置项

### 文件删除规范
⚠️ **禁止真正删除文件，必须使用软删除机制**
- **所有删除操作都应将文件移动到根目录下的 `.trash/` 文件夹**
- 适用范围：工具调用删除、MCP 删除、在终端使用代码实现的删除、终端命令删除
- 具体要求：
  - 不允许使用 `os.remove()` 直接删除文件
  - 不允许使用 `rm` 或 `del` 命令真正删除文件
  - 不允许使用工具直接删除文件（如 upgrade_delete_file 等）
  - 应该使用 `shutil.move()` 或相应命令将文件移动到 `.trash/` 目录
- `.trash/` 目录无需提交到 git（应在 .gitignore 中）
- 这样做可以保留文件恢复的可能性

## 核心模块说明

### 爬虫模块 (src/scraper.py)
- 负责网页爬取和数据提取
- 返回结构化的文章数据

### API 服务 (src/api/)
- FastAPI 应用
- RESTful API 端点
- 路由在 `v1` 版本目录

### Web UI (src/web/streamlit_app.py)
- Streamlit 应用
- 用户交互界面
- 实时数据展示

### 调度器 (src/scheduler/)
- APScheduler 定时任务
- 周期性爬取和分析

### AI 功能 (src/ai/)
- 文章分析和处理
- 自然语言处理功能

## 常见任务

### 添加新的 API 端点
1. 在 `src/api/v1/` 目录创建新路由
2. 使用 FastAPI 路由装饰器 `@router.get()` 或 `@router.post()`
3. 在主应用中注册路由

### 修改爬虫逻辑
- 编辑 `src/scraper.py`
- 遵循现有的错误处理和日志记录模式
- 更新配置中的目标选择器

### 添加新的定时任务
1. 在 `src/scheduler/` 创建新任务模块
2. 继承现有的任务基类（如存在）
3. 在调度器中注册任务

### 调整配置
- 编辑 `config.json` 文件
- 参考 `config.json.example.json` 了解配置项
- 在 `src/config.py` 中添加新的配置字段

## 依赖管理

- 依赖列表：`requirements.txt`
- Conda 环境：`environment.yml`
- 当前环境：`hpf-sztu-scraper`
- 配置文件：`.env` (详见 docs/CONFIG.md)

安装依赖：
```bash
pip install -r requirements.txt
```

## 文件删除规范

⚠️ **禁止真正删除文件，必须使用软删除机制**
- **所有删除操作都应将文件移动到根目录下的 `.trash/` 文件夹**
- 适用范围：工具调用删除、MCP 删除、在终端使用代码实现的删除、终端命令删除
- 具体要求：
  - 不允许使用 `os.remove()` 直接删除文件
  - 不允许使用 `rm` 或 `del` 命令真正删除文件
  - 不允许使用工具直接删除文件（如 upgrade_delete_file 等）
  - 应该使用 `shutil.move()` 或相应命令将文件移动到 `.trash/` 目录
- `.trash/` 目录无需提交到 git（应在 .gitignore 中）
- 这样做可以保留文件恢复的可能性

## 测试和验证

### 编译检查规范
⚠️ **避免频繁执行编译检查以提高效率**

**禁止进行的操作**：
- ❌ 不要在每个代码修改后立即运行 `python -m py_compile` 检查
- ❌ 不要为每个单独的文件执行编译验证
- ❌ 不要批量编译整个模块目录来验证更改

**何时执行编译检查**：
- ✅ 仅当代码修改完成后的最后一步进行 **一次性综合检查**
- ✅ 修改核心模块（如主入口文件 `run.py` 或 `src/main.py`）且不确定是否有语法错误时
- ✅ 在用户明确要求执行验证时
- ✅ 提交代码前的最终验证步骤

**最佳实践**：
- 依赖 IDE 的实时语法检查（红色波浪线）而不是手动编译
- 在修改完所有相关文件后，统一进行一次编译验证
- 使用 VS Code 的 Python 扩展自动检测语法错误
- 优先信任代码审查而非频繁的自动化检查

**编译检查命令**（仅在必要时使用）：
```bash
# 单个文件检查
python -m py_compile file_path.py

# 多个文件一次性检查（修改完成后）
python -m py_compile file1.py file2.py file3.py

# 整个项目检查（最后验证）
python -m py_compile run.py src/main.py
```

## 调试和日志

- 日志配置：`src/logger_config.py`
- 日志文件：`logs/` 目录
- 使用标准 logging 模块记录信息

## 环境信息

- Python 版本：3.x
- 操作系统：Windows (当前)
- 数据格式：主要使用 JSON

## Copilot 行为规则

### 文档生成规则
⚠️ **禁止在没有用户明确指引的情况下生成任何文档**
- 不主动生成 markdown 文件来总结或记录更改
- 不主动创建项目文档、变更日志或说明文件
- 只有在用户明确要求创建、生成或更新特定文档时才执行

### 配置管理规则
- 仅使用 `.env` 文件管理所有环境配置
- 旧的 `config.json` 和 `schedule_config.json` 已迁移至 `.trash/` 目录
- 所有新的配置需求都应该通过 `.env` 变量实现

### 终端命令语法规则
⚠️ **在 Windows 环境中使用标准 PowerShell 语法**
- 当前工作环境为 Windows，终端使用 PowerShell（pwsh）
- 路径使用反斜杠 `\` 或正斜杠 `/`（PowerShell 两者都支持）
- 目录分隔：使用 `\` 作为目录分隔符（如 `C:\Users\...`）
- 变量引用：使用 `$variable` 语法（如 `$HOME`, `$PSScriptRoot`）
- 路径变量：使用 `$PWD` 代替 `pwd` 的输出
- 环境变量：使用 `$env:VAR_NAME` 访问（如 `$env:PYTHONPATH`）
- 条件判断：使用 PowerShell 语法（`if (-not $condition)` 而非 `if [ ... ]`）
- 管道操作：使用 PowerShell 管道语法 `|` 进行对象处理
- 推荐命令：优先使用 PowerShell 原生命令（如 `Get-ChildItem` 替代 `ls`、`dir`）
- 示例命令：
  ```powershell
  # 激活 Conda 环境
  conda activate hpf-sztu-scraper
  
  # 获取当前目录
  $PSScriptRoot
  Get-Location
  
  # 设置环境变量
  $env:PYTHONPATH = "C:\Users\...\src"
  
  # 运行 Python 脚本
  python main.py
  python -m pip install -r requirements.txt
  ```

### 编译检查执行规则
⚠️ **最小化编译检查执行，优化Agent效率**
- 不在修改每个文件后执行编译检查
- 不为常规代码修改进行逐个文件验证
- 代码编写时依赖 IDE 的实时错误检测而非频繁的编译验证
- 仅在以下情况执行编译检查：
  1. 所有相关代码修改完成后，进行一次性最终验证
  2. 修改的是关键文件（如 `run.py` 或 `src/main.py`）且不确定语法时
  3. 用户明确要求进行验证时
  4. 代码提交前的最终检查步骤
- 编译检查应该批量进行（多个文件一起检查），而不是逐个文件执行
- 信任 VS Code Python 扩展的实时语法检查能力

## 与 Copilot 协作的建议

在请求代码建议时，请明确指出：
1. 修改的是哪个模块
2. 期望的功能或修复内容
3. 是否需要考虑向后兼容性
4. 是否需要更新配置或文档

---

*此文件定期更新，以反映项目的最新情况。*
