# Python 代码编写指导

本文档提供了针对 HPF-SztuNewsScraper 项目的 Python 代码编写规范和最佳实践。

## 代码风格与命名规范

遵循 PEP 8 规范，详见 copilot-instructions.md 中的代码风格部分。

### 命名规范

| 对象类型 | 规范 | 示例 |
|---------|------|------|
| 模块/文件 | snake_case | `scraper.py`, `config_loader.py` |
| 类 | PascalCase | `NewsArticle`, `SchedulerManager` |
| 函数/方法 | snake_case | `get_articles()`, `parse_html()` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| 私有变量/方法 | _snake_case 前缀 | `_internal_cache`, `_validate()` |
| 魔法变量 | __name__ 双下划线 | `__name__`, `__main__` |

### 导入顺序和分组

使用工具 `isort` 自动整理导入顺序：标准库 → 第三方库 → 本地模块，每组之间空一行。

## 类型提示

### 使用类型注解
在所有函数和方法中使用类型提示，增强代码可读性和IDE支持：

```python
from typing import Dict, List, Optional, Tuple, Union

def fetch_articles(
    url: str,
    timeout: int = 30,
    retry_count: int = 3
) -> List[Dict[str, str]]:
    """
    获取文章列表。
    
    Args:
        url: 目标URL
        timeout: 请求超时时间（秒）
        retry_count: 重试次数
        
    Returns:
        文章字典列表
    """
    pass

def parse_content(
    content: Optional[str] = None,
) -> Union[Dict, None]:
    """处理可能为None的内容"""
    pass
```

### 复杂类型使用 TypeAlias（Python 3.10+）

```python
from typing import TypeAlias

ArticleData: TypeAlias = Dict[str, Union[str, int, list]]
ConfigDict: TypeAlias = Dict[str, any]
```

## Docstring 文档

### 使用 Google 风格 Docstring

```python
def analyze_article(content: str, keywords: List[str]) -> Dict[str, int]:
    """
    分析文章内容并统计关键词出现频率。
    
    支持中文和英文关键词分析。
    
    Args:
        content: 文章内容文本
        keywords: 关键词列表
        
    Returns:
        关键词出现频率字典，格式为 {'keyword': count}
        
    Raises:
        ValueError: 当关键词列表为空时抛出
        TypeError: 当content不是字符串时抛出
        
    Example:
        >>> result = analyze_article('深圳技术大学新闻', ['深圳', '技术'])
        >>> result
        {'深圳': 1, '技术': 1}
    """
    if not keywords:
        raise ValueError("关键词列表不能为空")
    if not isinstance(content, str):
        raise TypeError("content 必须是字符串类型")
    
    # 实现逻辑
    pass
```

### 模块级 Docstring

```python
"""
新闻爬虫模块 - 负责从网络源获取和处理新闻数据。

此模块提供以下主要功能：
- 网页内容爬取
- HTML 解析和数据提取
- 数据清理和验证

依赖:
    - requests: HTTP 请求库
    - BeautifulSoup4: HTML 解析库
    
示例:
    >>> from src.core.scraper import NewsScraper
    >>> scraper = NewsScraper()
    >>> articles = scraper.fetch_articles()
"""
```

## 异常处理

### 使用特定异常

```python
def get_config_value(key: str) -> str:
    """获取配置值，找不到时抛出特定异常"""
    try:
        value = os.getenv(key)
        if value is None:
            raise KeyError(f"环境变量 '{key}' 未定义")
        return value
    except KeyError as e:
        logger.error(f"配置错误: {e}")
        raise

def parse_json_file(filepath: str) -> Dict:
    """解析JSON文件，异常处理示例"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"文件不存在: {filepath}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSON 格式错误: {e}")
        raise ValueError(f"无法解析 {filepath}") from e
```

### 不要使用裸 except

```python
# ❌ 不要这样做
try:
    result = some_function()
except:
    pass

# ✅ 这样做
try:
    result = some_function()
except (ValueError, TypeError) as e:
    logger.error(f"处理错误: {e}")
    raise
```

## 日志记录

### 使用项目的日志配置

```python
from src.core.logger import get_logger

logger = get_logger(__name__)

def process_articles(articles: List[Dict]) -> None:
    """处理文章列表"""
    logger.info(f"开始处理 {len(articles)} 篇文章")
    
    for i, article in enumerate(articles):
        try:
            # 处理逻辑
            logger.debug(f"处理文章 {i+1}/{len(articles)}")
        except Exception as e:
            logger.error(f"处理失败: {article.get('title', 'Unknown')}", exc_info=True)
            continue
    
    logger.info("文章处理完成")
```

### 日志级别使用指南

| 级别 | 用途 | 示例 |
|-----|------|------|
| DEBUG | 详细调试信息 | `logger.debug("变量值: {value}")` |
| INFO | 程序流程信息 | `logger.info("开始爬取新闻")` |
| WARNING | 警告信息 | `logger.warning("连接超时，进行重试")` |
| ERROR | 错误信息 | `logger.error("爬取失败")` |
| CRITICAL | 严重错误 | `logger.critical("应用启动失败")` |

## 配置管理

### 使用环境变量

```python
import os
from src.config.env_loader import load_env_file

# 在应用启动时加载 .env 文件
load_env_file('.env')

# 从环境变量读取配置
SCRAPER_TIMEOUT = int(os.getenv('SCRAPER_TIMEOUT', '30'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
TARGET_URL = os.getenv('TARGET_URL', 'https://news.sztu.edu.cn')
```

### 不要硬编码敏感信息

```python
# ❌ 不要这样做
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "admin123"

# ✅ 这样做
API_KEY = os.getenv('API_KEY')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')

if not API_KEY:
    raise ValueError("未设置 API_KEY 环境变量")
```

## 数据模型与验证

### 使用 Pydantic 定义数据模型

```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class Article(BaseModel):
    """新闻文章数据模型"""
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    url: str = Field(...)
    author: Optional[str] = None
    publish_date: Optional[str] = None
    category: str = Field(default="未分类")
    
    @validator('url')
    def validate_url(cls, v):
        """验证URL格式"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL 必须以 http:// 或 https:// 开头')
        return v
    
    class Config:
        """模型配置"""
        str_strip_whitespace = True  # 自动去除字符串首尾空格
        validate_assignment = True    # 设置值时验证
```

## 文件操作

### 使用 pathlib 和上下文管理器

```python
from pathlib import Path
import json

def save_articles(articles: List[Dict], filepath: str) -> None:
    """保存文章到JSON文件"""
    output_path = Path(filepath)
    
    # 确保目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 使用 with 语句自动管理文件关闭
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    logger.info(f"已保存 {len(articles)} 篇文章到 {filepath}")


def load_config(config_path: str) -> Dict:
    """从配置文件加载配置"""
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)
```

## 异步编程

### 使用 async/await（当需要异步操作时）

```python
import asyncio
from typing import List
import aiohttp

async def fetch_article_async(session: aiohttp.ClientSession, url: str) -> Dict:
    """异步获取单个文章"""
    try:
        async with session.get(url, timeout=30) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.warning(f"获取失败: {url} (状态码: {response.status})")
                return {}
    except asyncio.TimeoutError:
        logger.error(f"请求超时: {url}")
        return {}

async def fetch_articles_batch(urls: List[str]) -> List[Dict]:
    """批量异步获取文章"""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_article_async(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

## 测试编写

### 单元测试示例

```python
import unittest
from unittest.mock import patch, MagicMock
from src.core.scraper import parse_html

class TestScraper(unittest.TestCase):
    """爬虫模块测试"""
    
    def setUp(self):
        """测试前准备"""
        self.test_html = "<html><body><h1>测试</h1></body></html>"
    
    def test_parse_html_success(self):
        """测试HTML解析成功"""
        result = parse_html(self.test_html)
        self.assertIsNotNone(result)
    
    def test_parse_html_empty(self):
        """测试空HTML处理"""
        with self.assertRaises(ValueError):
            parse_html("")
    
    @patch('src.core.scraper.requests.get')
    def test_fetch_with_mock(self, mock_get):
        """测试使用Mock的网络请求"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = self.test_html
        mock_get.return_value = mock_response
        
        from src.core.scraper import fetch_url
        result = fetch_url("http://example.com")
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
```

## 代码注释

### 编写清晰的注释

```python
def calculate_similarity_score(text1: str, text2: str) -> float:
    """
    计算两个文本的相似度分数。
    
    使用余弦相似度算法计算两个文本向量之间的相似程度。
    """
    # 清理文本，移除特殊字符和多余空格
    text1_clean = clean_text(text1)
    text2_clean = clean_text(text2)
    
    # 构建向量表示
    vector1 = build_vector(text1_clean)
    vector2 = build_vector(text2_clean)
    
    # 计算余弦相似度
    similarity = calculate_cosine_similarity(vector1, vector2)
    
    return similarity
```

### 不要写冗余注释

```python
# ❌ 冗余注释
count = 0  # 设置计数器为0

# ✅ 有意义的注释
# 记录失败的爬取任务数
failed_task_count = 0
```

## 性能最佳实践

### 使用列表推导式替代循环

```python
# ❌ 低效
result = []
for article in articles:
    if article['status'] == 'published':
        result.append(article['title'])

# ✅ 更高效
result = [
    article['title'] 
    for article in articles 
    if article['status'] == 'published'
]
```

### 使用生成器处理大数据集

```python
def read_large_file(filepath: str):
    """使用生成器逐行读取大文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            yield line.strip()

# 使用
for line in read_large_file('articles.json'):
    process_line(line)
```

## 安全编程

### 输入验证

```python
def validate_user_input(user_input: str) -> str:
    """验证用户输入"""
    if not isinstance(user_input, str):
        raise TypeError("输入必须是字符串")
    
    # 检查长度
    if len(user_input) > 1000:
        raise ValueError("输入过长（最大1000字符）")
    
    # 移除危险字符
    dangerous_chars = ['<', '>', '&', '"', "'"]
    for char in dangerous_chars:
        user_input = user_input.replace(char, '')
    
    return user_input.strip()
```

### SQL注入防护

```python
# ❌ 不要这样做 - 容易SQL注入
query = f"SELECT * FROM articles WHERE title = '{user_input}'"

# ✅ 使用参数化查询
from sqlalchemy import text
query = text("SELECT * FROM articles WHERE title = :title")
result = db.execute(query, {"title": user_input})
```

## 上下文管理器

### 实现自定义上下文管理器

```python
from contextlib import contextmanager
from typing import Generator

@contextmanager
def timer(name: str) -> Generator:
    """计时上下文管理器"""
    import time
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        logger.info(f"{name} 耗时 {elapsed:.2f} 秒")

# 使用
with timer("数据处理"):
    process_large_dataset()
```

## 常见错误与解决方案

### 1. 可变默认参数

```python
# ❌ 危险 - 所有调用共享同一个列表
def append_item(item, items=[]):
    items.append(item)
    return items

# ✅ 正确
def append_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### 2. 资源泄漏

```python
# ❌ 可能泄漏文件描述符
file = open('data.json')
data = json.load(file)
# 忘记关闭文件

# ✅ 正确处理
with open('data.json', 'r') as file:
    data = json.load(file)
# 自动关闭
```

### 3. 全局变量滥用

```python
# ❌ 避免全局状态
global_cache = {}

def get_data(key):
    if key in global_cache:
        return global_cache[key]
    # ...

# ✅ 使用类或依赖注入
class DataManager:
    def __init__(self):
        self.cache = {}
    
    def get_data(self, key):
        if key in self.cache:
            return self.cache[key]
```

## 有用的工具和库推荐

### 编译和语法检查限制

⚠️ **禁止在代码编写过程中频繁使用终端命令进行编译检查**

#### 不要使用的命令
- ❌ `python -m py_compile file.py` - 不要在编写每个文件后执行
- ❌ `python -c "import module_name"` - 不要频繁验证导入
- ❌ 逐个文件执行语法检查命令

#### 何时执行编译检查
✅ **仅在以下情况执行编译检查**：
1. 修改完核心启动文件（`run.py`、`src/main.py`、`src/entry/main.py`）后，一次性检查
2. 修改完所有相关代码后，进行**最后一次**综合验证
3. 用户明确要求验证代码时
4. 代码提交前的最终检查步骤

#### 推荐做法
- ✅ 依赖 VS Code Python 扩展的实时语法检查（红色波浪线）
- ✅ 信任 IDE 的错误提示
- ✅ 在修改后让 IDE 自动检测问题
- ✅ 批量执行一次编译检查，而非逐个文件

### 代码格式化和检查工具
- `black`: 代码格式化工具
- `pylint`: 代码质量检查
- `flake8`: 风格指南检查
- `isort`: 导入排序工具

### 开发依赖安装
```bash
pip install black pylint flake8 isort pytest
```

### 使用 pre-commit hooks
```bash
# 在提交前自动检查代码
pip install pre-commit
pre-commit install
```

## 项目特定的编程建议

### 日志输出位置
- 将所有日志保存到 `logs/` 目录
- 使用项目的日志配置系统（`src.core.logger`）

### 配置文件位置
- 从项目根目录的 `.env` 文件读取配置
- 使用 `src.config.env_loader` 加载环境变量

### 数据存储
- JSON 文件存储在 `articles/` 目录
- 分析记录保存在 `articles/analysis_records/` 目录

### 模块导入
- 项目启动脚本会将 `src/` 和 `services/` 添加到路径
- 使用相对导入时确保在正确的包结构中

---

**最后更新**: 2026年1月7日  
**维护者**: HPF-SztuNewsScraper 开发团队
