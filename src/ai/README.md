# AI 分析模块 - Dify 工作流对接

## 概述
本模块提供与 Dify 工作流的对接接口，用于处理学校新闻的相关性分析。

## 文件结构
```
ai/
├── dify_workflow.py       # Dify 工作流处理主模块
├── test_data/             # 测试数据目录
├── README.md              # 本文件
└── analysis_records/      # 分析记录目录
```

## 工作流输入

### 输入 1: 用户资料 (String)
从 `config.json` 中的 `user_profile` 转换为 JSON 字符串

**格式：**
```json
{
  "basic_info": {
    "name": "用户名",
    "student_id": "学号",
    "gender": "性别"
  },
  "education": {
    "department": "学院",
    "major": "专业",
    "grade": "年级",
    "class": "班级"
  },
  "interests": {
    "topics": ["感兴趣的话题1", "话题2"],
    "keywords": ["关键词1", "关键词2"]
  },
  "dislikes": {
    "topics": ["不感兴趣的话题1"],
    "keywords": ["过滤关键词1"]
  }
}
```

### 输入 2: 新闻文件 (File)
待处理的新闻 JSON 文件

**格式：**
```json
{
  "title": "新闻标题",
  "content": "新闻内容详情",
  "source": "新闻来源",
  "publish_date": "发布日期",
  "url": "新闻链接(可选)"
}
```

## 工作流输出

### 预期输出格式
```json
{
  "title": "新闻标题",
  "summary": "内容总结",
  "relevance_score": 8.5,
  "relevance_reason": "评分原因说明"
}
```

## 使用方法

### 1. 在 Python 中调用

```python
from ai.dify_workflow import DifyWorkflowHandler
import json

handler = DifyWorkflowHandler()

# 准备输入
user_profile_json = json.dumps(user_profile_dict)
news_file_path = "/path/to/news.json"

# 处理工作流
result = handler.process_workflow(user_profile_json, news_file_path)
print(result)
```

### 2. 运行测试演示

```bash
python ai/dify_workflow.py
```

## 主要类和方法

### DifyWorkflowHandler

**初始化方法：**
- `__init__()` - 初始化处理器

**核心方法：**
- `process_workflow(user_profile_str, news_file_path)` - 主处理流程
- `validate_inputs(user_profile_str, news_file_path)` - 验证输入
- `parse_workflow_output(workflow_output_str)` - 解析工作流输出

**辅助方法：**
- `_prepare_analysis_data()` - 准备分析数据
- `_get_iso_timestamp()` - 获取时间戳

## 错误处理

工作流会返回标准的 JSON 错误响应：

```json
{
  "status": "error",
  "message": "错误描述",
  "errors": ["具体错误1", "具体错误2"]
}
```

常见错误：
- `用户资料 JSON 解析失败` - 用户资料格式不正确
- `新闻文件不存在` - 文件路径错误
- `新闻文件 JSON 解析失败` - 文件格式不正确
- `新闻文件缺少必需字段` - 缺少 title 或 content

## 工作流集成

在 Dify 中创建工作流时：
1. 添加两个输入节点：
   - `user_profile` (String 类型)
   - `news_file` (File 类型)

2. 在工作流中处理这两个输入

3. 返回符合格式的 JSON 输出

4. 通过 `DifyWorkflowHandler.parse_workflow_output()` 解析结果

## 日志和存储

- **日志:** 所有操作都被记录到标准日志系统
- **测试数据:** `ai/test_data/` 目录存储测试用的示例文件
- **分析记录:** `articles/analysis_records/` 目录存储分析过程中的详细记录

## 配置文件关联

该模块读取根目录的 `config.json`，特别是：
- `gemini.api_key` - 可选，用于后续 AI 分析
- `user_profile` - 用户资料配置模板
- `prompts.analyze_relevance` - 分析提示词

## 版本信息
- 创建日期: 2026-01-05
- Python 版本: 3.8+
- 依赖: google-genai, pydantic (可选)
