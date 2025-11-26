# NewsSpider - 智能新闻爬取与问答系统

一个基于Python的智能新闻爬取系统，专门用于爬取深圳技术大学公文通网站新闻内容，并提供智能问答功能。

## 功能特性

- 📰 自动爬取新闻内容
- 📄 生成PDF文档
- 🤖 基于AI的智能问答
- 🌐 友好的Web界面
- 🔒 安全的配置管理

## 安装指南

### 1. 克隆项目
```bash
git clone <repository-url>
cd NewsSpider
```

### 2. 创建虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境
```bash
# 复制配置文件模板
cp config.py.template config.py

# 编辑 config.py 文件，填写您的配置信息
```


## 配置说明

在 `config.py` 中配置以下参数：

这里使用的是google的GEMINI-2.5-pro和text-embedding-004。

```python
# 网络代理端口(根据实际软件端口配置)
os.environ["http_proxy"] = "http://127.0.0.1:xxxx"
os.environ["https_proxy"] = "http://127.0.0.1:xxxx"
os.environ["all_proxy"] = "socks5://127.0.0.1:xxxx" 

# GEMINI API 密钥（必需）
GOOGLE_API_KEY = "your_api_key_here"

# 目标网站配置 （必需）
TARGET_BASE_URL = "复制学校内部网网址"
TARGET_PAGE_URL = "复制学校公文通页面的网址"

# 其他可选配置保持默认即可
# 但我建议还是仔细看看需要的配置文件，默认可能会报错
```

### 获取 GEMINI API 密钥

1. 访问 [GEMINI官网](https://gemini.google.com/app?hl=zh-cn)
2. 注册账号并获取API密钥
3. 在配置文件中设置 `GOOGLE_API_KEY`

## 若更换其他厂商的API

### 第一步-修改`config.py`文件

你需要注释掉原有的 Google 配置，并根据新厂商的要求添加 API Key、Base URL（接口地址）以及模型名称。

目前市面上绝大多数模型（DeepSeek、Kimi、阿里的通义千问等）都支持 OpenAI 格式的调用。

```python
import os

# --- 代理配置 (保持不变) ---
os.environ["http_proxy"] = "http://127.0.0.1:xxxx"
os.environ["https_proxy"] = "http://127.0.0.1:xxxx"
os.environ["all_proxy"] = "socks5://127.0.0.1:xxxx" 

# --- 原 Google 配置 (建议注释掉) ---
# GOOGLE_API_KEY = "your_google_api_key"
# GEMINI_MODEL = "gemini-2.5-pro"
# EMBEDDING_MODEL = "text-embedding-004"

# --- 新厂商配置 (以 OpenAI/DeepSeek 为例) ---

# 1. API 密钥
# 如果是 OpenAI，填 sk-xxxx
# 如果是 DeepSeek，填 deepseek-chat 的 key
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx" 

# 2. Base URL (接口地址)
# OpenAI 官方默认: "https://api.openai.com/v1"
# DeepSeek 官方: "https://api.deepseek.com"
# 其他中转商: 根据服务商文档填写
OPENAI_BASE_URL = "https://api.deepseek.com" 

# 3. 模型名称配置
# 对话模型名称 (例如: gpt-4o, deepseek-chat, moonshot-v1-8k)
LLM_MODEL_NAME = "deepseek-chat"

# 嵌入模型名称 (例如: text-embedding-3-small)
# 注意：如果厂商不提供 Embedding 服务，需使用第三方或本地模型(如OLLAMA平台)
EMBEDDING_MODEL_NAME = "text-embedding-3-small"

# --- 目标网站配置 (保持不变) ---
TARGET_BASE_URL = "..."
TARGET_PAGE_URL = "..."
```

### 第二步-修改`pdf_qa.py`文件中的api配置

根据实际调用的API，修改模块
```python
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings #修改为其他API的库
...
...
def get_response(memory, question):
    file_path = Config.PDF_FILE_PATH
  
   #下方应修改
    model = ChatGoogleGenerativeAI( 
        model=Config.GEMINI_MODEL, 
        api_key=Config.GOOGLE_API_KEY,
        temperature=0
    )
    
    embeddings_zh = GoogleGenerativeAIEmbeddings( 
        model=Config.EMBEDDING_MODEL,
        google_api_key=Config.GOOGLE_API_KEY
    )
...
```

例如：
```python
# 引入 OpenAI 的库（适用于 DeepSeek, Kimi 等）
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# ...

def get_response(memory, question):
    # ...
    
    # 修改 LLM 初始化
    model = ChatOpenAI(
        model=Config.LLM_MODEL_NAME,
        openai_api_key=Config.OPENAI_API_KEY,
        openai_api_base=Config.OPENAI_BASE_URL, # 关键：指定 Base URL
        temperature=0
    )
    
    # 修改 Embedding 初始化
    embeddings_zh = OpenAIEmbeddings(
        model=Config.EMBEDDING_MODEL_NAME,
        openai_api_key=Config.OPENAI_API_KEY,
        openai_api_base=Config.OPENAI_BASE_URL
    )
```



## 使用方法

### 启动系统
```bash
source .venv/bin/activate  # Linux/macOS
或 .venv\Scripts\activate  # Windows
streamlit run main.py
```

### 操作流程

1. **更新新闻**：
   - 输入要爬取的页数（建议1-2页）
   - 点击"更新文件"按钮
   - 等待爬取完成

2. **智能问答**：
   - 在问题输入框中输入查询内容
   - 点击"开始提问"按钮
   - 系统基于PDF内容提供回答
