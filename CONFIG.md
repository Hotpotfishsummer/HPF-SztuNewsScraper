# 配置说明

本项目使用 `config.json` 作为配置文件。

## 快速开始

### 1. 复制配置模板
```bash
cp config.json.example.json config.json
```

### 2. 编辑配置文件
打开 `config.json` 并填入你的配置信息：

```json
{
  "gemini": {
    "api_key": "YOUR_ACTUAL_API_KEY",
    "model": "gemini-2.5-flash",
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "proxy": {
    "enabled": false,
    "protocol": "http",
    "host": "127.0.0.1",
    "port": 7890
  },
  "user_profile": {
    "name": "用户名",
    "student_id": "学号",
    "department": "所属部门",
    "major": "专业",
    "interests": ["感兴趣的领域1"],
    "relevant_keywords": ["相关关键词1"]
  },
  "prompts": {
    "analyze_relevance": "自定义的分析提示词"
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

## 配置字段说明

### gemini 配置
- **api_key** (必需): 你的 Gemini API Key
  - 从 [Google AI Studio](https://aistudio.google.com/app/apikey) 获取
- **model** (可选): 使用的 Gemini 模型，默认 `gemini-2.5-flash`
- **temperature** (可选): 模型温度参数（0-2），控制输出的随机性，默认 `0.7`
- **max_tokens** (可选): 最大输出 token 数，默认 `1000`

### proxy 配置
用于配置 HTTP/HTTPS 代理（用于访问被限制的 Gemini API）

- **enabled** (可选): 是否启用代理，默认 `false`
- **protocol** (可选): 代理协议，默认 `http`，可选值: `http`, `https`, `socks5`
- **host** (可选): 代理服务器地址，默认 `127.0.0.1`
- **port** (可选): 代理服务器端口，默认 `7890`
- **username** (可选): 代理用户名（如果需要认证）
- **password** (可选): 代理密码（如果需要认证）

**常见代理工具配置**：

**Clash/Clash for Windows**：
```json
{
  "proxy": {
    "enabled": true,
    "protocol": "http",
    "host": "127.0.0.1",
    "port": 7890
  }
}
```

**V2Ray**：
```json
{
  "proxy": {
    "enabled": true,
    "protocol": "http",
    "host": "127.0.0.1",
    "port": 10809
  }
}
```

**Shadowsocks + privoxy**：
```json
{
  "proxy": {
    "enabled": true,
    "protocol": "http",
    "host": "127.0.0.1",
    "port": 8118
  }
}
```

**带认证的代理**：
```json
{
  "proxy": {
    "enabled": true,
    "protocol": "http",
    "host": "proxy.example.com",
    "port": 3128,
    "username": "username",
    "password": "password"
  }
}
```

### user_profile 配置
用户的个人和教育信息，用于个性化分析文章相关性。

**basic_info** - 基本信息：
- **name**: 用户名
- **student_id**: 学号
- **gender**: 性别 (男/女/其他，可选)

**education** - 教育信息：
- **department**: 所属部门/学院
- **major**: 专业
- **grade**: 年级 (如 "2024级")
- **class**: 班级号 (如 "1班")
- **student_type**: 学生类型 (本科生/研究生/博士生，默认 "本科生")

**interests** - 兴趣偏好：
- **topics** (数组): 感兴趣的领域 (如 ["人工智能", "开源软件"])
- **keywords** (数组): 相关关键词 (如 ["算法", "编程", "数据结构"])

**dislikes** - 不感兴趣内容 ⭐ **新增**：
- **topics** (数组): 不感兴趣的领域 (如 ["体育赛事", "娱乐八卦"])
- **keywords** (数组): 想过滤的关键词 (如 ["运动会", "明星"])

**notification_preferences** - 通知偏好设置 ⭐ **新增**：
- **priority_departments** (数组): 优先关注的部门 (如 ["计算机学院", "教务处"])
- **exclude_categories** (数组): 排除的通知类别 (如 ["体育活动", "文艺演出"])
- **receive_urgent_only** (布尔值): 仅接收紧急通知，默认 `false`

### prompts 配置
- **analyze_relevance**: 文章相关性分析提示词模板

提示词中可以使用以下占位符，会被自动替换为实际值：
- `{user_name}` - 用户名
- `{student_id}` - 学号
- `{department}` - 部门
- `{major}` - 专业
- `{interests}` - 兴趣领域
- `{relevant_keywords}` - 相关关键词
- `{title}` - 文章标题
- `{content}` - 文章内容

### logging 配置
- **level**: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)，默认 `INFO`
- **format**: 日志输出格式，默认包含时间、模块名、日志级别和消息

## 在代码中使用配置

### 基本用法
```python
from src.config import get_config

# 获取配置实例
config = get_config()

# 获取 API Key
api_key = config.gemini_api_key

# 获取代理配置
if config.proxy_enabled:
    proxy_url = config.get_proxy_url()
    print(f"使用代理: {proxy_url}")

# 获取用户信息
user_profile = config.get('user_profile', {})
print(f"用户: {user_profile.get('name')}")

# 获取提示词
prompt = config.get_prompt('analyze_relevance')
```

### AI 分析器使用
```python
from src.structured_ai_summarizer import StructuredAISummarizer
import json

# 初始化分析器（自动使用代理配置）
analyzer = StructuredAISummarizer()

# 加载文章
with open('articles/example.json', 'r', encoding='utf-8') as f:
    article = json.load(f)

# 分析文章
result = analyzer.analyze_article(article)
if result['status'] == 'success':
    print(f"相关性评分: {result['data']['relevance_score']}/10")
```

## 用户信息配置详解 ⭐ **更新说明**

为了更精准地分析文章相关性，新版本增强了用户配置结构：

### 分层结构优势
```json
"user_profile": {
  "basic_info": {      // 基本个人信息
    "name": "...",
    "student_id": "...",
    "gender": "..."
  },
  "education": {       // 教育背景信息
    "department": "...",
    "major": "...",
    "grade": "2024级",
    "class": "1班",
    "student_type": "本科生"
  },
  "interests": {       // 感兴趣的内容
    "topics": [...],
    "keywords": [...]
  },
  "dislikes": {        // 不感兴趣的内容（新增）
    "topics": [...],
    "keywords": [...]
  },
  "notification_preferences": {  // 通知偏好（新增）
    "priority_departments": [...],
    "exclude_categories": [...],
    "receive_urgent_only": false
  }
}
```

### 新增字段详解

**年级和班级 - 精确定位**
- 系统能识别同年级同班的班级通知
- 示例：教务处发布"2024级计算机1班"相关通知时，可精确匹配

**不感兴趣的领域 (dislikes) - 主动过滤**
- 避免推送你完全不关心的内容
- 示例：如果不感兴趣"体育赛事"，所有运动会通知都会自动降分
- 应用场景：你是理工科学生，不需要艺术类选修课通知

**通知偏好 (notification_preferences) - 智能分发**
- **priority_departments**: 优先关注的部门（提升这些部门通知的相关分）
- **exclude_categories**: 完全排除的通知类别（相关性评分为 0）
- **receive_urgent_only**: 仅看紧急通知（用于考试周、找工作等关键时期）

### 使用示例

**学生A - 计算机专业学生的配置**
```json
{
  "basic_info": {
    "name": "张三",
    "student_id": "2024001234",
    "gender": "男"
  },
  "education": {
    "department": "计算机学院",
    "major": "计算机科学与技术",
    "grade": "2024级",
    "class": "1班",
    "student_type": "本科生"
  },
  "interests": {
    "topics": ["人工智能", "算法竞赛", "开源项目"],
    "keywords": ["编程", "Python", "竞赛", "实习"]
  },
  "dislikes": {
    "topics": ["体育运动", "娱乐八卦"],
    "keywords": ["运动会", "明星", "综艺"]
  },
  "notification_preferences": {
    "priority_departments": ["计算机学院", "教务处", "学生处"],
    "exclude_categories": ["文艺演出", "体育活动"],
    "receive_urgent_only": false
  }
}
```
**效果**: 
- ✅ 关于算法竞赛的通知 → 分数高
- ✅ 计算机学院学科竞赛 → 分数高  
- ❌ 校运会选手报名 → 自动过滤
- ❌ 文艺演出邀请 → 自动过滤

**学生B - 考试周特殊配置**
```json
{
  "notification_preferences": {
    "priority_departments": ["教务处", "学生处"],
    "exclude_categories": ["文艺演出", "体育活动"],
    "receive_urgent_only": true  // 仅看紧急通知
  }
}
```
**效果**: 只显示紧急通知，减少干扰

## 安全提示和向后兼容性

⚠️ **向后兼容**:
- 系统支持旧版配置格式（平铺结构），会自动转换为新格式
- 无需立即升级配置，旧配置仍能使用

⚠️ **最佳实践**:
- 定期更新 `interests` 和 `dislikes`，保持配置准确
- 通知_preferences 可根据学期/时间段调整（如考试周）
- 不确定的关键词可先不填，随后根据分析结果补充



### 测试代理连接
```python
from src.config import get_config
import requests

config = get_config()
if config.proxy_enabled:
    proxies = config.proxy_config
    try:
        response = requests.get('https://www.google.com', proxies=proxies, timeout=5)
        print("✅ 代理连接成功")
    except requests.exceptions.RequestException as e:
        print(f"❌ 代理连接失败: {e}")
```

### 常见问题

**Q: 如何禁用代理？**
A: 在 `config.json` 中将 `proxy.enabled` 设置为 `false`，或直接删除 proxy 配置。

**Q: 代理地址应该如何填写？**
A: 
- 对于本地代理（Clash等），通常是 `127.0.0.1:7890`
- 对于远程代理，填写服务器地址和端口
- 如果需要认证，在 `username` 和 `password` 字段中填写

**Q: 使用了代理但仍然无法访问 Gemini API？**
A: 
1. 确认代理工具正在运行
2. 确认代理地址和端口正确
3. 尝试用浏览器测试代理是否可用
4. 查看日志输出是否有报错信息

**Q: 代理地址如何验证是否正确？**
A: 在代码中打印 `config.proxy_config` 来查看解析后的代理配置

## 安全提示

⚠️ **重要**: 
- **不要将 `config.json` 提交到版本控制系统**
- 在 `.gitignore` 中已添加 `config.json`，只需提交 `config.json.example.json`
- 如果你不小心暴露了 API Key，请立即重新生成一个新的 Key
- 代理认证信息（用户名密码）也应该保密
