# SZTU 新闻爬虫

一个基于Python的新闻爬取系统，专门用于爬取深圳技术大学公文通网站新闻内容。

## 功能特性

- 📰 自动爬取新闻列表和完整内容
- 🔍 智能索引管理，避免重复爬取
- 💾 本地缓存管理，支持离线浏览
- 🌐 Streamlit Web界面，美观易用
- 🔐 安全的文件管理和权限控制

## 安装指南

### 1. 克隆项目
```bash
git clone https://github.com/Hotpotfishsummer/HPF-SztuNewsScraper.git
cd HPF-SztuNewsScraper
```

### 2. 使用Conda创建环境（推荐）
```bash
conda env create -f environment.yml
conda activate hpf-sztu-scraper
```

或使用pip安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 方式一：交互式菜单
```bash
python run.py
```

菜单选项：
1. **爬取新闻标题和链接** - 提取列表页面的新闻摘要信息
2. **爬取完整文章** - 获取每篇文章的完整详情内容
3. **查看已爬取的新闻** - 列出所有已保存的文章
4. **根据 URL 查询文章** - 通过URL搜索特定文章
5. **根据标题搜索文章** - 通过关键词搜索文章
6. **启动 Web 浏览界面** - 使用Streamlit浏览器查看文章
7. **退出**

Web界面功能：
- 📋 左侧文章列表，支持搜索和分类/部门过滤
- 📖 右侧文章详细内容展示
- 🔍 实时搜索功能
- 📁 按分类和部门过滤
- 📱 响应式设计，适配不同屏幕

## 项目结构

```
HPF-SztuNewsScraper/
├── run.py                 # 主程序入口
├── requirements.txt       # pip依赖配置
├── environment.yml        # conda环境配置
├── README.md             # 项目说明
├── .gitignore            # git忽略配置
└── src/
    ├── main.py           # 交互式菜单主程序
    ├── scraper.py        # 爬取核心模块
    ├── logger_config.py   # 日志配置
    ├── extract_news.py    # 新闻提取工具
    └── streamlit_app.py   # Web界面应用
└── articles/             # 爬取的文章存储目录
    └── index.json        # 文章索引文件
```

## 核心功能说明

### 爬取流程

1. **列表页爬取** - 从学校公文通获取新闻列表
2. **详情页爬取** - 逐一访问每篇文章获取完整内容
3. **索引管理** - 自动生成index.json索引文件，记录所有文章元数据
4. **缓存检查** - 再次爬取时自动检查索引，避免重复下载已存在的文章
5. **本地存储** - 文章以JSON格式保存在articles目录

### 智能缓存机制

- **索引文件查询** - 爬取前检查index.json中的URL记录
- **文件存在验证** - 确认对应的文章文件是否存在
- **自动跳过** - 若文章已缓存，自动跳过网络请求
- **增量更新** - 只爬取和保存新增的文章

### 文章文件 (articles/*.json)

完整的文章数据包含：
- 基本信息（标题、分类、部门等）
- 完整内容
- 元数据和时间戳

## 注意事项

- 爬取时请注意网站的访问频率限制，建议在空闲时间进行
