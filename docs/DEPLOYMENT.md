# 部署指南

SZTU 新闻爬虫支持两种主要部署模式：**CLI 版本**（本地交互）和 **服务版本**（Docker 后台运行）。

## 目录

- [CLI 版本部署](#cli-版本部署本地交互)
- [服务版本部署](#服务版本部署docker-后台)
- [Docker Compose 部署](#docker-compose-部署推荐)
- [配置管理](#配置管理)
- [常见问题](#常见问题)

---

## CLI 版本部署（本地交互）

### 环境要求

- Python 3.8+
- Conda（可选）

### 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/Hotpotfishsummer/HPF-SztuNewsScraper.git
cd HPF-SztuNewsScraper

# 2. 创建虚拟环境（推荐）
conda env create -f environment.yml
conda activate hpf-sztu-scraper

# 或使用 pip：
pip install -r requirements.txt

# 3. 配置环境
cp .env.example .env
# 编辑 .env，填入实际的 API Key 和配置

# 4. 启动 CLI
python cli_entry.py
```

### CLI 命令示例

```bash
# 启动交互菜单
python cli_entry.py

# 爬取新闻
python cli_entry.py --fetch-json 5          # 爬取 5 页（JSON 格式）
python cli_entry.py --fetch-full 3          # 爬取 3 页（完整内容）

# 浏览文章
python cli_entry.py --list                  # 列出所有文章
python cli_entry.py --search-title "关键词" # 按标题搜索

# 启动 Web UI
python cli_entry.py --web

# AI 分析
python cli_entry.py --analyze               # 启动 AI 分析模式

# 显示系统信息
python cli_entry.py --info
```

---

## 服务版本部署（Docker 后台）

### 环境要求

- Docker 20.10+
- Docker Compose 1.29+（可选，但推荐）

### 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/Hotpotfishsummer/HPF-SztuNewsScraper.git
cd HPF-SztuNewsScraper

# 2. 配置环境
cp .env.example .env
# 编辑 .env，填入实际的配置

# 3. 启动服务版本
python service_entry.py

# 或在后台运行
nohup python service_entry.py > logs/service.log 2>&1 &
```

### 服务命令示例

```bash
# 启动所有服务（推荐）
python service_entry.py

# 仅启动调度器
python service_entry.py --scheduler-only

# 仅启动 API
python service_entry.py --api-only

# 仅启动 Web UI
python service_entry.py --web-only

# 显示系统信息
python service_entry.py --info
```

### 访问方式

- **Streamlit Web UI**: http://localhost:8501
- **FastAPI REST API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

---

## Docker Compose 部署（推荐）

### 环境要求

- Docker 20.10+
- Docker Compose 1.29+

### 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/Hotpotfishsummer/HPF-SztuNewsScraper.git
cd HPF-SztuNewsScraper

# 2. 构建镜像
docker-compose build

# 3. 配置环境
cp .env.example .env
# 编辑 .env

# 4. 启动服务
docker-compose up -d service

# 5. 查看日志
docker-compose logs -f service

# 6. 停止服务
docker-compose down
```

### 部署选项

#### 选项 1: 服务版本（推荐）

一个容器运行所有服务（调度器 + API + Web UI）：

```bash
docker-compose up -d service
```

**优点：**
- 简单易管理
- 资源消耗少
- 适合小到中型部署

#### 选项 2: 微服务版本（高级）

多个独立容器，每个容器运行一个服务：

```bash
docker-compose --profile microservices up -d
```

启动 3 个容器：
- `sztu-scraper-scheduler` - 定时调度器
- `sztu-scraper-api` - FastAPI REST API
- `sztu-scraper-web` - Streamlit Web UI

**优点：**
- 支持独立扩展
- 服务隔离
- 适合大型部署

#### 选项 3: CLI 版本

交互式命令行版本（需要 TTY）：

```bash
docker-compose run --rm cli
```

### Docker 命令示例

```bash
# 启动特定服务
docker-compose up -d service

# 启动微服务
docker-compose --profile microservices up -d

# 查看日志
docker-compose logs -f [service_name]
docker-compose logs service -f --tail 100

# 执行命令
docker-compose exec service python cli_entry.py --list

# 停止服务
docker-compose stop
docker-compose down                # 删除容器
docker-compose down -v             # 删除容器和卷

# 重启服务
docker-compose restart service
```

### 数据持久化

通过 Docker 卷实现数据持久化：

```yaml
volumes:
  - ./articles:/app/articles        # 爬取的文章
  - ./logs:/app/logs                # 日志文件
  - ./.env:/app/.env                # 环境配置
```

数据将被保存在主机的 `articles/` 和 `logs/` 目录中。

---

## 配置管理

### 环境变量（.env）

所有配置通过 `.env` 文件管理（v2.0 开始）：

```bash
cp .env.example .env
# 编辑配置
```

详见 [CONFIG.md](CONFIG.md)

### 主要配置项

```env
# 日志配置
LOG_LEVEL=INFO

# Dify Workflow（AI 分析）
DIFY_ENABLED=false
DIFY_API_ENDPOINT=http://localhost:8001/v1
DIFY_API_KEY=your-api-key

# Gemini API（AI 模型）
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=gemini-2.5-flash

# 用户资料（用于 AI 分析）
USER_PROFILE='{"education": {...}, "interests": {...}}'
```

详细配置说明见 [CONFIG.md](CONFIG.md)

---

## 常见问题

### Q1: CLI 版本和服务版本的区别？

| 特性 | CLI 版本 | 服务版本 |
|------|---------|---------|
| 启动方式 | 交互菜单 | 后台服务 |
| 使用场景 | 本地开发/测试 | 容器部署 |
| 定时任务 | ❌ | ✅ |
| REST API | ❌ | ✅ |
| Web UI | ✅ 可选启动 | ✅ 自动启动 |

### Q2: 如何在生产环境中持续运行？

**推荐方案：**

```bash
# 方案 1: Docker Compose
docker-compose up -d service

# 方案 2: systemd service（Linux）
sudo vim /etc/systemd/system/sztu-scraper.service
# 配置并启动
sudo systemctl start sztu-scraper
sudo systemctl enable sztu-scraper

# 方案 3: 后台进程
nohup python service_entry.py > logs/service.log 2>&1 &
```

### Q3: 如何调整定时任务的频率？

编辑 `.env` 文件中的调度配置或参考 [CONFIG.md](CONFIG.md)

### Q4: 如何查看日志？

```bash
# CLI 版本：输出到控制台

# 服务版本：
docker-compose logs -f service
# 或查看日志文件
tail -f logs/application.log
```

### Q5: 如何重置数据？

```bash
# 保留配置，删除爬取的文章和分析结果
rm -rf articles logs data

# 使用 Docker Compose
docker-compose down -v              # 删除所有卷
docker-compose up -d service        # 重新启动
```

### Q6: 支持哪些 Python 版本？

- Python 3.8+（推荐 Python 3.10+）
- 使用 `python --version` 检查

### Q7: 如何更新项目？

```bash
git pull origin main
docker-compose build --no-cache
docker-compose up -d service
```

---

## 性能优化建议

### 1. 调整爬虫并发度

编辑 `.env` 中的 `SCRAPER_CONCURRENT_REQUESTS` 参数

### 2. 定时任务优化

- 避免在业务高峰期爬取
- 设置合理的请求间隔，尊重目标网站

### 3. 存储优化

- 定期清理过期的分析结果
- 考虑使用数据库存储大量文章

### 4. 资源限制（Docker）

编辑 `docker-compose.yml`：

```yaml
service:
  resources:
    limits:
      cpus: '1'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

---

## 故障排除

### 问题: 爬取超时

**解决:**
1. 检查网络连接
2. 增加 `SCRAPER_TIMEOUT` 参数
3. 减少 `SCRAPER_CONCURRENT_REQUESTS`

### 问题: 内存不足

**解决:**
1. 减少并发数
2. 定期清理缓存
3. 增加 Docker 内存限制

### 问题: API 无法访问

**解决:**
```bash
# 检查容器状态
docker-compose ps

# 检查日志
docker-compose logs api

# 检查端口占用
netstat -tlnp | grep 8000
```

---

## 监控和健康检查

### 健康检查

```bash
# 检查 API 健康状态
curl http://localhost:8000/health

# 检查 Web UI
curl http://localhost:8501/_stcore/health

# Docker Compose 自动健康检查
docker-compose ps
```

### 日志监控

```bash
# 实时监控日志
tail -f logs/application.log

# 查看特定日期的日志
grep "2024-01-15" logs/application.log
```

---

更新时间：2024 年 1 月
版本：v2.0

### schedule_config.json 配置

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
      "params": {
        "pages": 3
      }
    },
    "analyzer": {
      "enabled": true,
      "schedule": {
        "trigger": "cron",
        "hour": 6,
        "minute": 0
      },
      "params": {
        "batch_size": 10
      }
    }
  }
}
```

### .env 环境变量

```bash
# Dify 配置
DIFY_ENABLED=false
DIFY_API_ENDPOINT=http://localhost:8001/v1
DIFY_API_KEY=your-api-key

# Gemini 配置
GEMINI_API_KEY=your-api-key

# 日志级别
LOG_LEVEL=INFO

# 调度器配置
SCHEDULER_ENABLED=true
SCHEDULER_TIMEZONE=Asia/Shanghai

# Web 应用配置
WEB_HOST=0.0.0.0
WEB_PORT=8501
```

## 部署模式对比

| 特性 | CLI 模式 | 单容器模式 | 多容器模式 |
|------|--------|---------|---------|
| 启动方式 | `python run.py` | `python run.py --mode service` | `docker-compose up` |
| 进程管理 | 手动 | Supervisor | Docker |
| 扩展性 | 低 | 中 | 高 |
| 资源占用 | 低 | 低 | 中 |
| 适用场景 | 开发 | 小规模 | 生产 |
| 部署难度 | 简单 | 中等 | 简单 |

## 在线运行监控

### 查看任务状态

在 CLI 模式中：
```
选项 6 -> AI 分析 -> 3 查看分析历史
```

在 Web 应用中：
- 访问 `http://localhost:8501`
- 切换到 "📊 分析结果" 标签

### Docker 中查看日志

```bash
# 查看调度器日志
docker logs -f sztu-scraper-scheduler

# 查看 Web 应用日志
docker logs -f sztu-scraper-web

# 实时监控
docker stats
```

## 常见问题

### 1. Dify API 连接失败

**症状：** 分析任务报错 "连接 Dify API 失败"

**解决方案：**
- 检查 `DIFY_API_ENDPOINT` 是否正确
- 检查 `DIFY_API_KEY` 是否有效
- 确保 Dify 服务正在运行：`curl http://localhost:8001/v1/workflows`

### 2. 爬虫任务失败

**症状：** 爬虫任务报错，无法获取新闻

**解决方案：**
- 检查网络连接
- 检查目标网站是否可访问
- 查看代理配置（如果使用代理）
- 查看日志文件：`data/logs/`

### 3. 容器启动失败

**症状：** `docker-compose up` 失败

**解决方案：**
```bash
# 查看详细错误
docker-compose up --no-detach

# 检查依赖
docker ps -a

# 清理旧容器
docker-compose down -v
docker-compose up -d
```

### 4. 权限错误

**症状：** "Permission denied" 错误

**解决方案：**
```bash
# Linux/Mac
chmod +x services/*.py
chmod +x infrastructure/health-checks/*.py

# Docker
docker exec -u root sztu-scraper-scheduler chown -R 1000:1000 /app/data
```

### 5. 内存不足

**症状：** 容器被杀死，日志显示 "Killed"

**解决方案：**
```yaml
# docker-compose.yml 中添加资源限制
services:
  scheduler:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

## 性能优化

### 1. 爬虫性能

```json
{
  "scraper": {
    "params": {
      "pages": 10,           // 增加爬取页数
      "timeout": 30,         // 增加超时时间
      "retry_times": 5       // 增加重试次数
    }
  }
}
```

### 2. 分析性能

```json
{
  "analyzer": {
    "params": {
      "batch_size": 50,      // 增加批处理大小
      "concurrent": 5        // 并发数（如果支持）
    }
  }
}
```

### 3. 数据库优化

使用 PostgreSQL 替代 SQLite：
```bash
DATABASE_URL=postgresql://user:password@localhost/sztu_scraper
```

## 备份与恢复

### 备份数据

```bash
# 备份所有数据
docker-compose exec scheduler tar czf /app/data/backup.tar.gz \
  /app/data/articles \
  /app/data/logs

# 复制到本地
docker cp sztu-scraper-scheduler:/app/data/backup.tar.gz ./
```

### 恢复数据

```bash
# 复制备份到容器
docker cp backup.tar.gz sztu-scraper-scheduler:/app/data/

# 解压
docker-compose exec scheduler tar xzf /app/data/backup.tar.gz -C /
```

## 生产环境检查清单

- [ ] 配置 `config.json` 中的所有必需项
- [ ] 配置 `.env` 环境变量
- [ ] 测试 Dify API 连接
- [ ] 测试 Gemini API 连接
- [ ] 配置定时任务时间
- [ ] 设置日志级别为 INFO 或 WARNING
- [ ] 配置备份策略
- [ ] 设置监控告警
- [ ] 准备灾难恢复方案
- [ ] 进行负载测试

## 监控与告警

### Prometheus 指标（可选）

```bash
# 在 Dockerfile 中添加
RUN pip install prometheus-client

# 在应用中添加指标收集
from prometheus_client import Counter, Histogram

scraper_tasks = Counter('scraper_tasks_total', 'Total scraper tasks')
analysis_duration = Histogram('analysis_duration_seconds', 'Analysis duration')
```

### 告警规则（可选）

```yaml
# alerting_rules.yml
groups:
  - name: scraper
    rules:
      - alert: ScraperTaskFailed
        expr: increase(scraper_tasks_failed_total[5m]) > 0
        annotations:
          summary: "Scraper task failed"
```

## 技术支持

- 查看日志：`docker logs sztu-scraper-scheduler`
- 检查配置：`python run.py --info`
- 提交问题：[GitHub Issues](https://github.com/Hotpotfishsummer/HPF-SztuNewsScraper/issues)
