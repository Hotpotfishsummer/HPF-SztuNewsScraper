# 环境配置指南

## 配置系统概览

从 v2.0 开始，本项目采用 **统一的 .env 文件** 管理所有配置，简化配置体系并提高安全性。

### 配置优先级

```
环境变量 (最高优先级)
    ↓
.env 文件
    ↓
默认值 (最低优先级)
```

## 快速开始

### 1. 准备配置文件

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env，填入你的实际配置
# 重点需要配置的项：
# - GEMINI_API_KEY 或 DIFY_API_KEY
# - USER_* 开头的用户信息
# - 代理配置（如果需要）
```

### 2. 常见注意事项

- **不要提交 .env 到 git**（已在 .gitignore 中）
- **不要在代码中硬编码 API 密钥**
- **.env 文件与版本控制**：使用 `.env.example` 作为模板

## 详细配置说明

### 一、日志配置

```env
LOG_LEVEL=INFO                                          # 日志级别
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
TIMEZONE=Asia/Shanghai                                  # 系统时区
```

| 参数 | 说明 | 示例值 |
|------|------|--------|
| `LOG_LEVEL` | 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL） | INFO |
| `TIMEZONE` | 时区（CRON 任务和日志时间戳） | Asia/Shanghai |

---

### 二、AI 和 API 配置

#### Gemini API

```env
GEMINI_API_KEY=YOUR_API_KEY_HERE                        # Gemini API 密钥
GEMINI_MODEL=gemini-2.5-flash                           # 模型版本
GEMINI_TEMPERATURE=1.0                                  # 温度参数（0.0-2.0）
GEMINI_MAX_TOKENS=5000                                  # 最大输出令牌数
```

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `GEMINI_API_KEY` | Google API 密钥 | - |
| `GEMINI_MODEL` | 模型选择 | gemini-2.5-flash |
| `GEMINI_TEMPERATURE` | 温度（越小越确定） | 0.7-1.0 |
| `GEMINI_MAX_TOKENS` | 最大输出令牌 | 5000 |

#### Dify API

```env
DIFY_ENABLED=true                                       # 是否启用
DIFY_API_ENDPOINT=http://100.69.225.112:8080/v1         # API 端点
DIFY_API_KEY=app-YOUR_KEY_HERE                          # API 密钥
DIFY_TIMEOUT=60                                         # 超时时间（秒）
DIFY_RETRY_TIMES=3                                      # 重试次数
DIFY_RETRY_DELAY=2                                      # 重试延迟（秒）
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `DIFY_ENABLED` | 启用 Dify 服务 | true |
| `DIFY_API_ENDPOINT` | API 端点地址 | - |
| `DIFY_API_KEY` | API 密钥 | - |
| `DIFY_TIMEOUT` | 请求超时 | 60 秒 |
| `DIFY_RETRY_TIMES` | 失败重试次数 | 3 |
| `DIFY_RETRY_DELAY` | 重试等待时间 | 2 秒 |

---

### 三、网络代理配置

```env
PROXY_ENABLED=true                                      # 是否启用代理
PROXY_PROTOCOL=http                                     # 代理协议
PROXY_HOST=127.0.0.1                                    # 代理主机
PROXY_PORT=7897                                         # 代理端口
PROXY_USERNAME=                                         # 代理用户名（可选）
PROXY_PASSWORD=                                         # 代理密码（可选）
```

| 参数 | 说明 | 示例 |
|------|------|------|
| `PROXY_ENABLED` | 启用代理 | true/false |
| `PROXY_PROTOCOL` | 协议类型 | http/https/socks5 |
| `PROXY_HOST` | 代理地址 | 127.0.0.1 |
| `PROXY_PORT` | 代理端口 | 7890 |
| `PROXY_USERNAME` | 用户名（可选） | - |
| `PROXY_PASSWORD` | 密码（可选） | - |

---

### 四、用户个人信息

#### 基本信息

```env
USER_NAME=张三                                          # 你的名字
USER_STUDENT_ID=2024001234                              # 学号
USER_GENDER=男                                          # 性别
```

#### 教育背景

```env
USER_DEPARTMENT=计算机学院                              # 所在学院
USER_MAJOR=计算机科学与技术                             # 专业
USER_GRADE=2024级                                       # 年级
USER_CLASS=1班                                          # 班级
USER_STUDENT_TYPE=本科生                                # 学生类型
```

#### 兴趣和偏好

```env
# 逗号分隔，不需要空格
USER_INTERESTED_TOPICS=人工智能,开源软件,竞技编程       # 感兴趣的主题
USER_INTERESTED_KEYWORDS=算法,编程,数据结构             # 感兴趣的关键词

USER_DISLIKED_TOPICS=体育赛事,娱乐八卦                   # 不感兴趣的主题
USER_DISLIKED_KEYWORDS=运动会,明星                       # 过滤的关键词
```

#### 通知偏好

```env
USER_PRIORITY_DEPARTMENTS=计算机学院,教务处             # 优先部门（逗号分隔）
USER_EXCLUDE_CATEGORIES=体育活动,文艺演出               # 排除的类别（逗号分隔）
USER_RECEIVE_URGENT_ONLY=false                          # 仅接收紧急通知
```

---

### 五、定时任务调度

所有 CRON 表达式使用标准格式：`分 小时 日 月 周`

#### 爬虫任务

```env
SCHEDULER_SCRAPER_ENABLED=true                          # 是否启用
SCHEDULER_SCRAPER_JOB_ID=scraper_daily                   # 任务ID
SCHEDULER_SCRAPER_CRON=0 0 * * *                        # CRON表达式（每天00:00）
SCHEDULER_SCRAPER_PAGES=3                               # 爬取页数
```

#### 分析任务

```env
SCHEDULER_ANALYZER_ENABLED=true                         # 是否启用
SCHEDULER_ANALYZER_JOB_ID=analyzer_daily                 # 任务ID
SCHEDULER_ANALYZER_CRON=0 6 * * *                       # CRON表达式（每天06:00）
SCHEDULER_ANALYZER_BATCH_SIZE=10                        # 单次处理数量
```

#### 清理任务

```env
SCHEDULER_CLEANUP_ENABLED=false                         # 是否启用
SCHEDULER_CLEANUP_JOB_ID=cleanup_weekly                  # 任务ID
SCHEDULER_CLEANUP_CRON=0 3 * * 0                        # 每周一03:00
SCHEDULER_CLEANUP_DAYS_TO_KEEP=30                       # 保留天数
```

#### 健康检查

```env
SCHEDULER_HEALTH_CHECK_ENABLED=true                     # 是否启用
SCHEDULER_HEALTH_CHECK_JOB_ID=health_check               # 任务ID
SCHEDULER_HEALTH_CHECK_INTERVAL_MINUTES=5               # 检查间隔（分钟）
```

**CRON 表达式示例**：

| 表达式 | 说明 |
|--------|------|
| `0 0 * * *` | 每天 00:00 |
| `0 6 * * *` | 每天 06:00 |
| `0 3 * * 0` | 每周一 03:00 |
| `0 0 1 * *` | 每月 1 日 00:00 |
| `*/15 * * * *` | 每 15 分钟 |

---

### 六、应用服务配置

#### FastAPI 服务

```env
API_HOST=0.0.0.0                                        # 监听地址
API_PORT=8000                                           # 监听端口
API_RELOAD=true                                         # 热重启（开发用）
```

#### Streamlit Web UI

```env
STREAMLIT_PORT=8501                                     # 监听端口
```

#### 调度器服务

```env
SCHEDULER_LOG_LEVEL=INFO                                # 日志级别
```

---

### 七、数据存储和路径

```env
ARTICLES_DATA_DIR=articles                              # 文章数据目录
LOGS_DIR=logs                                           # 日志目录
```

---

### 八、开发和调试

```env
DEBUG=false                                             # 调试模式
ENVIRONMENT=development                                # 环境：development/production
```

---

## 详细配置说明

### 详细配置说明

#### Dify 配置

```bash
# Dify 平台启用标志
DIFY_ENABLED=false

# Dify API 端点（本地部署示例）
DIFY_API_ENDPOINT=http://localhost:8001/v1

# Dify API 密钥
DIFY_API_KEY=your-api-key-here

# API 超时时间（秒）
DIFY_TIMEOUT=60

# 重试次数
DIFY_RETRY_TIMES=3

# 重试延迟（秒）
DIFY_RETRY_DELAY=2
```

#### Gemini 配置

```bash
# Google Gemini API 密钥
GEMINI_API_KEY=your-api-key-here

# 模型选择
GEMINI_MODEL=gemini-2.5-flash

# 温度参数（0.0-2.0，值越小结果越确定）
GEMINI_TEMPERATURE=1.0

# 最大输出令牌数
GEMINI_MAX_TOKENS=5000
```

#### 日志配置

```bash
# 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# 日志文件位置
LOG_FILE=data/logs/scraper.log

# 日志最大大小（字节）
LOG_MAX_SIZE=10485760  # 10MB

# 保留日志文件数
LOG_BACKUP_COUNT=5
```

#### 调度器配置

```bash
# 启用调度器
SCHEDULER_ENABLED=true

# 时区（用于 Cron 表达式）
SCHEDULER_TIMEZONE=Asia/Shanghai

# 调度器类型：apscheduler
SCHEDULER_TYPE=apscheduler

# 误触发宽限时间（秒）
SCHEDULER_MISFIRE_GRACE_TIME=15
```

#### 爬虫配置

```bash
# 默认爬取页数
SCRAPER_DEFAULT_PAGES=3

# 连接超时（秒）
SCRAPER_TIMEOUT=30

# 重试次数
SCRAPER_RETRY_TIMES=3

# 重试延迟（秒）
SCRAPER_RETRY_DELAY=2

# 请求头 User-Agent
SCRAPER_USER_AGENT=Mozilla/5.0...
```

#### 分析器配置

```bash
# 默认批处理大小
ANALYZER_BATCH_SIZE=10

# 分析结果保存位置
ANALYZER_OUTPUT_DIR=data/articles/analysis_records

# 并发数（如果支持）
ANALYZER_CONCURRENT=1
```

#### Web 应用配置

```bash
# Web 服务主机
WEB_HOST=0.0.0.0

# Web 服务端口
WEB_PORT=8501

# Streamlit 主题
STREAMLIT_CLIENT_THEME_PRIMARY_COLOR=#FF6B6B

# 禁用收集用户数据
STREAMLIT_LOGGER_MESSAGE_RETENTION=1
```

#### API 配置（可选）

```bash
# API 服务启用
API_ENABLED=false

# API 主机
API_HOST=0.0.0.0

# API 端口
API_PORT=8000

# API 密钥
API_KEY=your-api-key

# CORS 允许来源
API_CORS_ORIGINS=http://localhost:3000
```

#### 代理配置（可选）

```bash
# HTTP 代理
HTTP_PROXY=http://proxy.example.com:8080

# HTTPS 代理
HTTPS_PROXY=https://proxy.example.com:8443

# 不需要代理的主机
NO_PROXY=localhost,127.0.0.1
```

### 2. config.json 配置文件

```json
{
  "gemini": {
    "api_key": "your-api-key",
    "model": "gemini-2.5-flash",
    "temperature": 1.0,
    "max_tokens": 5000,
    "top_p": 0.9,
    "top_k": 40
  },
  
  "dify": {
    "enabled": false,
    "api_endpoint": "http://localhost:8001/v1",
    "api_key": "your-api-key",
    "timeout": 60,
    "retry_times": 3,
    "retry_delay": 2,
    "workflow_id": "news-analysis-workflow"
  },
  
  "user_profile": {
    "education": {
      "department": "计算机学院",
      "major": "计算机科学与技术",
      "grade": "2024级",
      "school": "深圳技术大学"
    },
    
    "interests": {
      "topics": [
        "人工智能",
        "开源软件",
        "云计算",
        "区块链"
      ],
      "keywords": [
        "算法",
        "编程",
        "数据结构",
        "系统设计"
      ]
    },
    
    "dislikes": {
      "topics": [
        "体育赛事",
        "娱乐八卦",
        "房产买卖"
      ],
      "keywords": [
        "运动",
        "明星",
        "房价"
      ]
    },
    
    "reading_preferences": {
      "preferred_length": "long",  // short, medium, long
      "preferred_difficulty": "medium",  // easy, medium, hard
      "preferred_sources": ["技术博客", "学术论文"],
      "language": "zh"
    }
  },
  
  "scraper": {
    "pages": 3,
    "timeout": 30,
    "retry_times": 3,
    "retry_delay": 2
  },
  
  "analyzer": {
    "batch_size": 10,
    "output_dir": "data/articles/analysis_records"
  },
  
  "logging": {
    "level": "INFO",
    "file": "data/logs/scraper.log",
    "max_size": 10485760,
    "backup_count": 5
  },
  
  "scheduler": {
    "enabled": true,
    "timezone": "Asia/Shanghai",
    "misfire_grace_time": 15
  }
}
```

#### config.json 各字段说明

##### gemini 配置
- `api_key`: Google Gemini API 密钥（必需）
- `model`: 使用的模型（默认: gemini-2.5-flash）
- `temperature`: 输出的随机性（0-2）
- `max_tokens`: 最大输出令牌数
- `top_p`: 核心采样参数
- `top_k`: Top-K 采样参数

##### dify 配置
- `enabled`: 是否启用 Dify（默认: false）
- `api_endpoint`: Dify 服务地址
- `api_key`: Dify API 密钥
- `timeout`: 请求超时时间
- `retry_times`: 失败重试次数
- `retry_delay`: 重试延迟
- `workflow_id`: 工作流 ID

##### user_profile 配置

###### education（教育背景）
- `department`: 学院/系名称
- `major`: 专业名称
- `grade`: 年级
- `school`: 学校名称

###### interests（兴趣爱好）
- `topics`: 感兴趣的主题列表
- `keywords`: 感兴趣的关键词列表

###### dislikes（不感兴趣的内容）
- `topics`: 不感兴趣的主题列表
- `keywords`: 不感兴趣的关键词列表

###### reading_preferences（阅读偏好）
- `preferred_length`: 偏好文章长度（short/medium/long）
- `preferred_difficulty`: 偏好难度等级（easy/medium/hard）
- `preferred_sources`: 偏好的信息来源
- `language`: 语言偏好

### 3. schedule_config.json 配置

```json
{
  "scheduler": {
    "scraper": {
      "enabled": true,
      "description": "每日 00:00 爬取新闻",
      "schedule": {
        "trigger": "cron",
        "hour": 0,
        "minute": 0,
        "second": 0,
        "timezone": "Asia/Shanghai"
      },
      "params": {
        "pages": 3
      }
    },
    
    "analyzer": {
      "enabled": true,
      "description": "每日 06:00 分析新闻",
      "schedule": {
        "trigger": "cron",
        "hour": 6,
        "minute": 0,
        "second": 0,
        "timezone": "Asia/Shanghai"
      },
      "params": {
        "batch_size": 10
      }
    },
    
    "cleanup": {
      "enabled": false,
      "description": "每周日 03:00 清理过期数据",
      "schedule": {
        "trigger": "cron",
        "day_of_week": "0",
        "hour": 3,
        "minute": 0,
        "timezone": "Asia/Shanghai"
      },
      "params": {
        "days_to_keep": 30
      }
    },
    
    "health_check": {
      "enabled": true,
      "description": "每 5 分钟检查一次系统健康状态",
      "schedule": {
        "trigger": "interval",
        "minutes": 5
      }
    }
  }
}
```

#### Cron 表达式说明

```python
# 格式: trigger + (year | month | day | week | hour | minute | second)

# 常见示例
"trigger": "cron",
"hour": 0, "minute": 0              # 每日 00:00
"hour": "0-6", "minute": 0          # 每日 00:00-06:00（每小时）
"hour": "*/2"                       # 每 2 小时
"day_of_week": "0", "hour": 0      # 每周一 00:00
"day": "1", "hour": 0              # 每月 1 日 00:00

# Interval 触发器示例
"trigger": "interval",
"minutes": 5                        # 每 5 分钟
"hours": 1                          # 每小时
"days": 1                           # 每天
```

### 4. 配置验证

应用启动时自动验证配置：

```python
# 验证项目
- Dify 配置（如果启用）
  - API 端点可访问性
  - API 密钥有效性
  
- Gemini 配置
  - API 密钥有效性
  
- 用户资料
  - 教育背景完整性
  - 兴趣关键词非空
  
- 代理配置（如果配置）
  - 代理地址格式正确
  - 代理可访问性
  
- 调度器配置
  - 任务配置格式正确
  - Cron 表达式有效
```

验证失败处理：
```bash
# 如果验证失败，应用会：
# 1. 记录详细错误信息
# 2. 禁用相关功能（而不是整个应用崩溃）
# 3. 继续以已验证的配置运行
```

## 常见配置场景

### 场景 1：本地开发（CLI 模式）

```bash
# .env
GEMINI_API_KEY=your-key
LOG_LEVEL=DEBUG
SCHEDULER_ENABLED=false

# config.json
{
  "gemini": {
    "api_key": "your-key",
    "model": "gemini-2.5-flash"
  },
  "user_profile": { ... },
  "dify": { "enabled": false }
}

# 启动
python run.py
```

### 场景 2：单服务器部署（Docker 单容器）

```bash
# .env
GEMINI_API_KEY=your-key
DIFY_ENABLED=true
DIFY_API_ENDPOINT=http://dify-server:8001/v1
DIFY_API_KEY=your-dify-key
LOG_LEVEL=INFO
SCHEDULER_ENABLED=true

# 启动
docker build -t scraper .
docker run -d --name scraper -p 8501:8501 -v data:/app/data scraper
```

### 场景 3：生产环境部署（Docker Compose）

```bash
# .env
GEMINI_API_KEY=${GEMINI_KEY}  # 使用 GitHub Secrets
DIFY_ENABLED=true
DIFY_API_ENDPOINT=http://dify:8001/v1
DIFY_API_KEY=${DIFY_KEY}
LOG_LEVEL=WARNING
SCHEDULER_ENABLED=true
WEB_HOST=0.0.0.0
WEB_PORT=8501

# config.json
# 只保留必要配置，其他由环境变量覆盖

# 启动
docker-compose up -d
```

## 配置热加载

应用支持配置文件热加载（不需要重启）：

```python
from src.config import reload_config

# 修改 config.json 后
reload_config()

# 立即应用新配置（某些配置需要重启服务生效）
```

> 注意：热加载对以下配置立即生效：
> - Dify/Gemini API 密钥
> - 用户资料
> - 日志级别
> 
> 以下配置需要重启服务：
> - 调度器配置
> - Web 服务端口

## 配置备份与版本控制

### 备份配置

```bash
# 备份所有配置
tar czf config_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  config.json \
  schedule_config.json \
  .env

# 提交到版本控制（注意安全）
git add config.json schedule_config.json
git commit -m "Update configuration"

# 不提交敏感信息
echo ".env" >> .gitignore
```

### 恢复配置

```bash
# 从备份恢复
tar xzf config_backup_20240101_120000.tar.gz

# 验证配置
python run.py --info
```

## 安全建议

### 1. 密钥管理

```bash
# ✅ 推荐：使用环境变量
export GEMINI_API_KEY="sk-..."

# ✅ 推荐：使用 .env 文件（Git 忽略）
GEMINI_API_KEY=sk-...

# ❌ 不推荐：在 config.json 中存储密钥
{"gemini": {"api_key": "sk-..."}}  // 容易被提交到 Git
```

### 2. 权限管理

```bash
# 保护敏感文件权限
chmod 600 .env
chmod 600 config.json
chmod 600 schedule_config.json

# Docker 中使用 secrets
docker secret create gemini_key -
docker service create \
  --secret gemini_key \
  -e GEMINI_API_KEY_FILE=/run/secrets/gemini_key \
  scraper
```

### 3. 代理配置

```bash
# 如果使用代理，配置用户名密码
HTTP_PROXY=http://username:password@proxy:8080
HTTPS_PROXY=https://username:password@proxy:8443
```

## 排查配置问题

### 问题 1：配置无法生效

```bash
# 检查优先级
# 1. 查看环境变量是否被覆盖
env | grep DIFY

# 2. 检查 .env 文件是否被加载
cat .env

# 3. 检查 config.json 语法
python -m json.tool config.json

# 4. 重新加载配置
python run.py --reload-config
```

### 问题 2：配置验证失败

```bash
# 查看详细错误信息
python run.py --info

# 输出应该显示：
# ✓ Gemini API: OK
# ✓ User Profile: OK
# ✓ Dify API: SKIPPED (disabled)
# ✓ Scheduler: OK
```

### 问题 3：敏感信息泄露

```bash
# 检查是否提交了密钥
git log -p --all -- config.json | grep -i "api_key"

# 撤销提交（谨慎操作）
git reset --hard HEAD~1

# 从 Git 历史中删除敏感文件
git filter-branch --tree-filter 'rm -f config.json' HEAD
```

## 配置参考

### 最小配置（仅爬虫）

```json
{
  "user_profile": {
    "education": {
      "department": "学院",
      "major": "专业"
    },
    "interests": {
      "topics": ["话题"],
      "keywords": ["关键词"]
    }
  }
}
```

### 标准配置（爬虫 + 分析）

```json
{
  "gemini": {
    "api_key": "your-key",
    "model": "gemini-2.5-flash"
  },
  "user_profile": { ... },
  "scheduler": {
    "enabled": true
  }
}
```

### 完整配置（所有功能）

见本文档上面的完整 config.json 示例。

