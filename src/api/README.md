# src/api - REST API 服务模块

## 概述

`src/api` 模块实现应用的 REST API 服务，使用 FastAPI 框架提供 HTTP 接口。API 允许外部客户端以编程方式访问爬虫、分析和查询功能。

## 目录结构

```
src/api/
├── __init__.py         # API 模块初始化
├── main.py            # FastAPI 应用主配置
├── v1/                # API v1 端点
│   ├── __init__.py
│   ├── news.py        # 新闻相关端点
│   ├── analysis.py    # 分析相关端点
│   └── health.py      # 健康检查端点
└── schemas/           # 请求/响应数据模型
    └── __init__.py
```

## 核心文件说明

### main.py - FastAPI 应用配置

**功能**: 创建和配置 FastAPI 应用

**包含内容**:
- FastAPI 应用实例化
- 中间件配置（CORS、日志等）
- 路由注册
- 错误处理程序

**配置**:
- 标题: "SZTU 新闻爬虫 API"
- 版本: 从 package.json 读取
- 基础 URL: `/api`
- CORS: 允许跨域请求

### v1/news.py - 新闻端点

**功能**: 新闻爬取、查询和搜索的 REST 端点

**端点**:

#### 获取文章列表
```
GET /api/v1/news/list
GET /api/v1/news/articles

响应:
{
  "articles": [
    {
      "title": "文章标题",
      "category": "分类",
      "department": "部门",
      "publish_time": "2024-01-07",
      "url": "https://...",
      "filename": "abc123.json"
    }
  ],
  "total": 100
}
```

#### 爬取新闻
```
POST /api/v1/news/fetch

请求体:
{
  "pages": 5,        # 要爬取的页数（1-10）
  "format": "json"   # 可选：json 或 full
}

响应:
{
  "status": "success",
  "message": "已爬取 100 篇新闻",
  "count": 100,
  "timestamp": "2024-01-07T12:00:00"
}
```

#### 按 URL 搜索
```
GET /api/v1/news/search?url=https://...

响应:
{
  "found": true,
  "article": {
    "title": "...",
    "category": "...",
    ...
  }
}
```

#### 按标题搜索
```
GET /api/v1/news/search?title=关键词
GET /api/v1/news/search?q=关键词

响应:
{
  "results": [
    { "title": "...", "url": "..." },
    { "title": "...", "url": "..." }
  ],
  "count": 2
}
```

#### 获取文章详情
```
GET /api/v1/news/{article_id}

响应:
{
  "id": "abc123",
  "title": "...",
  "content": "...",
  "category": "...",
  "department": "...",
  "publish_time": "...",
  "url": "...",
  "source": "...",
  "fetch_time": "..."
}
```

### v1/analysis.py - 分析端点

**功能**: AI 分析结果的查询和管理

**端点**:

#### 获取分析历史
```
GET /api/v1/analysis/history
GET /api/v1/analysis/history?limit=20

响应:
{
  "records": [
    {
      "timestamp": "2024-01-07T12:00:00",
      "news_title": "文章标题",
      "relevance_score": 8.5,
      "summary": "内容摘要"
    }
  ],
  "total": 100
}
```

#### 获取分析统计
```
GET /api/v1/analysis/statistics

响应:
{
  "total_analyses": 150,
  "average_relevance_score": 7.2,
  "score_distribution": {
    "high": 50,      # 8-10 分
    "medium": 70,    # 5-7 分
    "low": 30        # 0-4 分
  }
}
```

#### 分析单篇文章
```
POST /api/v1/analysis/analyze

请求体:
{
  "article_id": "abc123",  # 或
  "filepath": "/path/to/file.json"
}

响应:
{
  "status": "success",
  "analysis": {
    "title": "...",
    "summary": "...",
    "relevance_score": 8.5,
    "relevance_reason": "..."
  }
}
```

#### 批量分析
```
POST /api/v1/analysis/batch

请求体:
{
  "article_ids": ["id1", "id2", ...],  # 或
  "all": true  # 分析所有文章
}

响应:
{
  "status": "success",
  "processed": 50,
  "skipped": 10,
  "failed": 2
}
```

#### 检查分析有效性
```
GET /api/v1/analysis/check-validity

响应:
{
  "valid": true,
  "outdated_count": 0,
  "warnings": []
}
```

### v1/health.py - 健康检查

**端点**:

#### 健康检查
```
GET /api/v1/health
GET /health

响应:
{
  "status": "healthy",
  "timestamp": "2024-01-07T12:00:00",
  "version": "2.0.0"
}
```

## 数据模型（Schemas）

```python
# 文章模型
class Article(BaseModel):
    id: str
    title: str
    content: str
    category: str
    department: str
    publish_time: str
    url: str
    source: str
    fetch_time: str

# 分析结果模型
class AnalysisResult(BaseModel):
    article_id: str
    relevance_score: float
    summary: str
    relevance_reason: str
    timestamp: str

# 爬虫请求模型
class FetchRequest(BaseModel):
    pages: int = 1
    format: str = "json"  # json 或 full

# 分析请求模型
class AnalysisRequest(BaseModel):
    article_id: str
    filepath: Optional[str] = None
```

## 错误处理

API 返回标准的 HTTP 状态码：

| 状态码 | 说明 |
|-------|-----|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |
| 503 | 服务暂时不可用 |

错误响应格式：
```json
{
  "status": "error",
  "message": "错误描述",
  "error_code": "INVALID_PAGES",
  "details": {}
}
```

## 身份验证和授权

当前版本（v2.0）不需要身份验证。将来的版本可能会添加：
- API Key 认证
- JWT Token 支持
- 速率限制

## 启动 API 服务

```bash
# 使用 uvicorn 启动
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# 通过服务模式启动
python src/entry/service.py --api-only

# 使用 Docker
docker-compose up api
```

## 文档和调试

FastAPI 自动生成文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 依赖关系

```
api/
  ├─ FastAPI 框架
  ├─ Uvicorn (ASGI 服务器)
  ├─ Pydantic (数据验证)
  ├─ core.logger → 日志
  ├─ core.scraper → 爬虫功能
  ├─ core.analyzer → AI 分析
  └─ core.config → 配置
```

## 部署配置

### 环境变量
- `API_HOST` - 绑定地址（默认：0.0.0.0）
- `API_PORT` - 端口（默认：8000）
- `API_WORKERS` - 工作进程数（默认：4）

### CORS 配置
允许的源由 `CORS_ORIGINS` 环境变量控制（逗号分隔）。

## 设计原则

1. **RESTful**: 遵循 REST 设计原则
2. **版本化**: API 端点按版本组织（v1, v2, ...）
3. **文档完善**: 自动生成的 OpenAPI 文档
4. **错误清晰**: 明确的错误消息和错误代码
5. **异步支持**: 使用 async/await 处理 I/O 操作

## 使用示例

### Python 客户端
```python
import requests

# 获取文章列表
response = requests.get('http://localhost:8000/api/v1/news/list')
articles = response.json()['articles']

# 爬取新闻
response = requests.post(
    'http://localhost:8000/api/v1/news/fetch',
    json={'pages': 5}
)

# 搜索文章
response = requests.get(
    'http://localhost:8000/api/v1/news/search',
    params={'title': '深圳'}
)
results = response.json()['results']
```

### cURL
```bash
# 获取健康状态
curl http://localhost:8000/api/v1/health

# 爬取新闻
curl -X POST http://localhost:8000/api/v1/news/fetch \
  -H "Content-Type: application/json" \
  -d '{"pages": 5}'

# 搜索文章
curl "http://localhost:8000/api/v1/news/search?title=重要"
```

