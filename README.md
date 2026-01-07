# SZTU 新闻爬虫 v2.0

一个基于 Python 的新闻爬取系统，专门用于爬取深圳技术大学公文通网站新闻内容。

**v2.0 新特性：支持 CLI 和 Docker 服务两种部署模式，灵活应对不同场景。**

## 功能特性

- 📰 自动爬取新闻列表和完整内容
- 🔍 智能索引管理，避免重复爬取
- 💾 本地缓存管理，支持离线浏览
- 🌐 Streamlit Web 界面，美观易用
- 🤖 AI 驱动的新闻相关性分析（可选）
- 🔐 安全的文件管理和权限控制
- 📡 RESTful API 接口
- ⏰ 定时自动爬取和分析

## 两种部署模式

### 1️⃣ CLI 版本（本地交互）

适合**本地开发、测试和交互使用**。

```bash
# 启动交互菜单（推荐）
python -m src.main

# 或使用快速启动脚本
python start_cli.py
```

**支持的功能：**
- 命令行交互菜单
- 爬取新闻（列表或完整内容）
- 搜索和浏览文章
- AI 分析单篇或批量文章
- 启动 Web UI (Streamlit)

**快速命令：**
```bash
python -m src.main --list                    # 列出所有文章
python -m src.main --fetch-json 3            # 爬取 3 页新闻
python -m src.main --fetch-full 3            # 爬取 3 页完整新闻
python -m src.main --search-title "关键词"   # 按标题搜索
python -m src.main --web                     # 启动 Web UI
python -m src.main --analyze                 # 启动 AI 分析
```

### 2️⃣ Docker 服务版本（后台运行）

适合 **Docker 容器部署、持续运行和服务化**。

```bash
# 启动所有后台服务（推荐）
python service.py

# 或仅启动特定服务
python service.py --scheduler-only      # 仅启动调度器
python service.py --web-only            # 仅启动 Web UI
```

**包含的服务：**
- ⏰ **定时调度器** - 自动爬取和分析新闻
- 🌐 **FastAPI REST API** (http://localhost:8000) - 编程接口
- 💻 **Streamlit Web UI** (http://localhost:8501) - 可视化界面

## Docker Compose 部署

### 启动服务版本（推荐）

```bash
# 启动所有后台服务（一个容器）
docker-compose up service

# 或在后台运行
docker-compose up -d service
```

### 启动微服务架构（高级）

```bash
# 启动多个独立服务容器
docker-compose --profile microservices up

# 包括：scheduler + api + web（3 个容器）
docker-compose --profile microservices up -d
```

### 启动 CLI 版本

```bash
# 交互式 CLI（需要 TTY）
docker-compose run --rm cli
```

## 安装指南

### 本地开发环境

```bash
# 1. 克隆项目
git clone https://github.com/Hotpotfishsummer/HPF-SztuNewsScraper.git
cd HPF-SztuNewsScraper

# 2. 创建环境
conda env create -f environment.yml
conda activate hpf-sztu-scraper

# 或使用 pip
pip install -r requirements.txt

# 3. 配置 .env 文件
cp .env.example .env
# 编辑 .env 填入相应的配置
```

### Docker 部署

```bash
# 1. 确保已安装 Docker 和 Docker Compose

# 2. 构建镜像
docker-compose build

# 3. 启动服务
docker-compose up -d service

# 查看日志
docker-compose logs -f service
```

## 配置管理

所有配置均通过 `.env` 文件管理（v2.0 开始）：

```bash
# 复制模板
cp .env.example .env

# 编辑配置
nano .env
```

详见 [CONFIG.md](docs/CONFIG.md)

## 项目结构

```
HPF-SztuNewsScraper/
├── cli_entry.py              # CLI 版本入口 ✨ 新增
├── service_entry.py          # 服务版本入口 ✨ 新增
├── run.py                    # 主程序入口（路由）
├── requirements.txt          # Python 依赖
├── environment.yml           # Conda 环境配置
├── docker-compose.yml        # Docker 编排配置 ✨ 更新
├── .env.example              # 环境配置模板
├── README.md                 # 本文件
├── .gitignore                # git 忽略配置
├── infrastructure/           # 基础设施配置
│   └── docker/
│       ├── Dockerfile.base          # 基础镜像
│       ├── Dockerfile.cli           # CLI 版本 ✨ 新增
│       ├── Dockerfile.service       # 服务版本 ✨ 新增
│       ├── Dockerfile.scheduler     # 调度器镜像
│       └── Dockerfile.web           # Web 镜像
├── src/                      # 源代码目录
│   ├── main.py              # 命令行交互主程序
│   ├── scraper.py           # 爬虫核心模块
│   ├── config.py            # 配置管理
│   ├── logger_config.py      # 日志配置
│   ├── streamlit_app.py      # Web UI 应用
│   ├── ai/                  # AI 分析模块
│   ├── api/                 # FastAPI 应用
│   ├── cli/                 # CLI 模块
│   ├── scheduler/           # 定时调度模块
│   ├── storage/             # 存储管理
│   └── ...
├── services/                 # 微服务模块
│   ├── manager.py           # 服务管理器
│   ├── scheduler_service.py # 调度器服务
│   └── web_service.py       # Web 服务
├── articles/                # 爬取的文章存储目录
│   └── index.json          # 文章索引
├── logs/                    # 日志文件目录
├── docs/                    # 项目文档
│   ├── CONFIG.md           # 配置说明
│   ├── ARCHITECTURE.md      # 架构设计
│   └── DEPLOYMENT.md        # 部署指南
└── .trash/                 # 软删除目录（不提交到 git）
```

## 使用场景

### 场景 1：快速本地测试

```bash
python cli_entry.py --fetch-json 1
python cli_entry.py --list
python cli_entry.py --web
```

### 场景 2：定期自动爬取和分析

```bash
# 启动服务版本（后台运行）
python service_entry.py
# 或 Docker
docker-compose up -d service
```

### 场景 3：API 集成

```bash
# 启动 API 服务
python service_entry.py --api-only

# 使用 API
curl http://localhost:8000/api/v1/articles
curl -X POST http://localhost:8000/api/v1/scraper/fetch \
  -H "Content-Type: application/json" \
  -d '{"pages": 5}'
```

### 场景 4：完整微服务部署

```bash
docker-compose --profile microservices up -d
# 启动独立的 scheduler、api、web 容器，支持横向扩展
```

## 核心功能说明

### 爬取流程

1. **列表页爬取** - 从学校公文通获取新闻列表
2. **详情页爬取** - 逐一访问每篇文章获取完整内容
3. **索引管理** - 自动生成 index.json 索引文件
4. **缓存检查** - 避免重复下载已存在的文章
5. **本地存储** - 文章以 JSON 格式保存在 articles 目录

### AI 分析

支持使用 Dify Workflow 进行新闻相关性分析：

```bash
# 分析单篇文章
python cli_entry.py --analyze

# 可选：启用 AI 功能需要配置 .env 中的 DIFY_API_KEY 等
```

## 注意事项

- 爬取时请注意网站的访问频率限制
- 初次爬取可能需要较长时间，建议在空闲时间进行
- 定时任务配置详见 [CONFIG.md](docs/CONFIG.md)
- 所有敏感配置（API 密钥等）应通过 `.env` 文件管理

## 许可证

MIT License

## 作者

Hotpotfish 🐟
