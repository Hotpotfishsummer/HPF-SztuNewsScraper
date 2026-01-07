# src/cli - 命令行界面模块

## 概述

`src/cli` 模块实现应用的命令行交互界面。它包含菜单驱动的交互系统，允许用户通过简单的选项菜单来访问应用的核心功能，包括爬虫、搜索、AI 分析等。

## 目录结构

```
src/cli/
├── __init__.py         # CLI 模块初始化和导出
├── menu.py            # 交互菜单实现和所有 CLI 命令
├── commands/          # （将来）命令实现分解目录
└── utils/            # （将来）CLI 工具函数目录
```

## 核心文件说明

### menu.py - 交互菜单

**功能**: 提供所有 CLI 命令的实现和交互菜单框架

**关键函数**:

#### 菜单管理
- `show_info()` - 显示系统信息和配置状态
- `run_interactive_menu()` - 主交互菜单循环

#### 爬虫功能
- `fetch_news_json(pages=None)` - 爬取新闻标题和链接（JSON 格式）
- `fetch_news()` - 爬取完整新闻内容
- `fetch_news_json_pages(pages)` - 指定页数的 JSON 爬取
- `fetch_full_news(pages)` - 指定页数的完整爬取

#### 搜索功能
- `search_by_url()` - 按 URL 查询文章信息
- `search_by_title()` - 按标题关键词搜索
- `search_article_by_url(url)` - 直接按 URL 查询
- `search_articles_by_title(keyword)` - 直接按关键词查询

#### 文章管理
- `list_articles()` - 列出所有已爬取的文章

#### AI 分析功能
- `analyze_news_with_ai()` - AI 新闻相关性分析主函数
- `_analyze_single_article(handler, recorder, config)` - 分析单篇文章
- `_analyze_all_articles(handler, recorder, config)` - 批量分析所有文章
- `_view_analysis_history(recorder)` - 查看分析历史
- `_check_analysis_validity(recorder)` - 检查分析结果有效性

#### Web UI
- `start_web_ui()` - 启动 Streamlit Web 应用

## 交互菜单流程

```
run_interactive_menu()
  │
  └─ 显示菜单选项：
     1. 爬取新闻标题和链接（保存为 JSON）
     2. 爬取完整文章（标题、内容、时间等）
     3. 查看已爬取的新闻
     4. 根据 URL 查询文章
     5. 根据标题搜索文章
     6. 🤖 启动 AI 分析
     7. 启动 Web 浏览界面
     8. 退出
  │
  └─ 根据用户选择执行对应功能
```

## 爬虫功能流程

```
fetch_news_json()
  ├─ 提示用户输入页数（1-10）
  ├─ 验证输入
  └─ 调用 fetch_news_pages_with_json(pages)
     └─ 保存到 articles/index.json

fetch_news()
  ├─ 提示用户输入页数（1-10）
  ├─ 验证输入
  └─ 调用 fetch_articles_with_details(pages)
     └─ 保存到 articles/*.json
```

## 搜索功能流程

```
search_by_title()
  ├─ 提示用户输入关键词
  ├─ 调用 get_all_articles_from_index()
  ├─ 按关键词过滤
  └─ 显示匹配结果

search_by_url()
  ├─ 提示用户输入 URL
  ├─ 加载 articles_index
  ├─ 查找匹配的 URL
  └─ 显示文章详细信息
```

## AI 分析流程

```
analyze_news_with_ai()
  │
  ├─ 初始化处理器和记录器
  │  ├─ DifyWorkflowHandler
  │  └─ AnalysisRecorder
  │
  └─ 提示选择分析方式：
     ├─ 1: 分析单篇
     │   ├─ 列出可用文章
     │   ├─ 用户选择
     │   ├─ 检查是否已分析过
     │   ├─ 调用 DifyWorkflow 处理
     │   └─ 保存分析结果
     │
     ├─ 2: 批量分析
     │   ├─ 遍历所有文章
     │   ├─ 跳过已分析的
     │   ├─ 逐篇处理
     │   └─ 显示统计信息
     │
     ├─ 3: 查看历史
     │   ├─ 获取最近 20 条记录
     │   └─ 显示统计信息
     │
     ├─ 4: 检查有效性
     │   ├─ 查找过期分析
     │   └─ 显示警告
     │
     └─ 5: 返回主菜单
```

## 模块依赖

```
cli/menu.py
  ├─ core.logger → 日志
  ├─ core.scraper → 爬虫功能
  ├─ core.analyzer.dify_workflow → AI 处理
  ├─ core.analyzer.analysis_recorder → 结果记录
  └─ core.config → 配置管理
```

## 文件存储位置

- **爬取的文章**: `articles/*.json` - 单篇文章数据
- **文章索引**: `articles/index.json` - 文章元数据索引
- **分析记录**: `articles/analysis_records/*.json` - 分析结果
- **分析索引**: `articles/analysis_records/analysis_index.json` - 分析记录索引

## 用户交互示例

### 示例 1: 爬取新闻
```
请选择操作:
1. 爬取新闻标题和链接（保存为 JSON）
2. 爬取完整文章（标题、内容、时间等）
...
请输入选项 (1-8): 1

请输入要爬取的页数 (1-10): 3
[爬虫运行...]
✅ 爬取完成，共获得 60 篇文章
```

### 示例 2: 搜索文章
```
请输入选项 (1-8): 5
请输入标题关键词: 深圳技术大学

✅ 找到 5 篇相关文章：
1. 深圳技术大学校长致辞
   文件: abc123.json
   部门: 校长办公室
...
```

### 示例 3: AI 分析
```
请输入选项 (1-8): 6

📋 选择分析方式:
1. 分析单篇文章
2. 批量分析所有文章
...
请输入选项 (1-5): 1

📰 可分析的文章列表:
1. 新闻标题 1
2. 新闻标题 2
...
请选择文章编号: 1

🔄 正在分析: 新闻标题 1...
✅ 分析成功
📊 相关性评分: 8.5/10
```

## 设计原则

1. **用户友好**: 清晰的菜单和提示，新手可轻松使用
2. **错误处理**: 完整的输入验证和异常处理
3. **可扩展性**: 新命令可以轻松添加到菜单
4. **日志记录**: 完整的操作日志便于调试
5. **命令独立**: 各命令可独立执行，不依赖菜单框架

## 将来的改进

1. **命令分解**: 将各命令移至 `commands/` 子目录
2. **工具函数**: 提取通用工具到 `utils/` 目录
3. **命令行参数**: 支持更多直接的命令行参数而不仅仅是菜单
4. **插件系统**: 允许第三方扩展新的 CLI 命令

