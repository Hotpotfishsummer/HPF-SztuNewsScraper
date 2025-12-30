#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SZTU 新闻爬虫 - 网页爬取模块
"""

import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import hashlib
import os
from pathlib import Path
from datetime import datetime
from logger_config import get_logger

logger = get_logger(__name__)


ARTICLES_DIR = "articles"
ARTICLES_INDEX_FILE = os.path.join(ARTICLES_DIR, "index.json")


def ensure_articles_dir():
    """确保articles目录存在"""
    Path(ARTICLES_DIR).mkdir(exist_ok=True)


def load_articles_index() -> dict:
    """
    加载文章索引
    
    Returns:
        dict: 文章索引，格式为 {url: {filename, title, category, ...}}
    """
    ensure_articles_dir()
    
    if os.path.exists(ARTICLES_INDEX_FILE):
        try:
            with open(ARTICLES_INDEX_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    return {}


def save_articles_index(index: dict):
    """
    保存文章索引
    
    Args:
        index: 文章索引字典
    """
    ensure_articles_dir()
    
    try:
        with open(ARTICLES_INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    except IOError as e:
        pass


def add_to_articles_index(url: str, filename: str, article_info: dict):
    """
    添加文章到索引
    
    Args:
        url: 文章链接
        filename: 文章文件名
        article_info: 文章信息字典
    """
    index = load_articles_index()
    
    # 添加或更新索引项
    index[url] = {
        'filename': filename,
        'title': article_info.get('title', ''),
        'category': article_info.get('category', ''),
        'department': article_info.get('department', ''),
        'author': article_info.get('author', ''),
        'publish_date': article_info.get('publish_date', ''),
        'publish_time': article_info.get('publish_time', ''),
        'has_attachment': article_info.get('has_attachment', False),
        'fetch_time': article_info.get('fetch_time', '')
    }
    
    save_articles_index(index)


def get_article_by_url(url: str) -> dict:
    """
    根据 URL 获取文章信息
    
    Args:
        url: 文章链接
        
    Returns:
        dict: 文章索引项或空字典
    """
    index = load_articles_index()
    return index.get(url, {})


def is_article_cached(url: str) -> bool:
    """
    检查URL对应的文章是否已缓存
    
    通过检查索引文件和对应的文章文件是否存在来判断
    
    Args:
        url: 文章链接
        
    Returns:
        bool: 如果文章已缓存返回True，否则返回False
    """
    index = load_articles_index()
    
    # 检查索引中是否存在该URL
    if url not in index:
        return False
    
    # 获取缓存的文件名
    article_info = index[url]
    filename = article_info.get('filename', '')
    
    if not filename:
        return False
    
    # 检查对应的文件是否存在
    filepath = os.path.join(ARTICLES_DIR, filename)
    return os.path.exists(filepath)


def generate_filename(title: str, url: str) -> str:
    """
    生成唯一的英文文件名
    
    Args:
        title: 文章标题
        url: 文章URL
        
    Returns:
        str: 不包含中文的唯一文件名
    """
    # 使用URL的MD5哈希值作为基础，确保唯一性
    hash_str = hashlib.md5((url or title).encode()).hexdigest()
    return f"{hash_str}.json"


def load_articles() -> list:
    """加载所有已爬取的文章"""
    articles = []
    ensure_articles_dir()
    
    for filename in os.listdir(ARTICLES_DIR):
        if filename.endswith('.json') and filename != 'index.json':
            try:
                with open(os.path.join(ARTICLES_DIR, filename), 'r', encoding='utf-8') as f:
                    article = json.load(f)
                    articles.append(article)
            except (json.JSONDecodeError, IOError):
                continue
    
    return sorted(articles, key=lambda x: x.get('publish_time', ''), reverse=True)


def get_all_articles_from_index() -> list:
    """
    从索引文件加载所有文章信息（不需要加载完整的文章文件）
    
    Returns:
        list: 文章索引列表
    """
    index = load_articles_index()
    
    # 将索引转换为列表格式，并按发布时间排序
    articles = list(index.values())
    articles.sort(
        key=lambda x: x.get('publish_time', ''),
        reverse=True
    )
    
    return articles


def extract_article_details(html_content: str, url: str) -> dict:
    """
    从文章 HTML 中提取完整的文章详情
    
    Args:
        html_content: 文章页面的 HTML 内容
        url: 文章链接
        
    Returns:
        dict: 包含标题、内容、作者、时间等信息
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    article_data = {
        'url': url,
        'title': '',
        'author': '',
        'publish_time': '',
        'content': '',
        'fetch_time': datetime.now().isoformat()
    }
    
    try:
        # 提取标题
        title_elem = soup.select_one('h1.article-title')
        if title_elem:
            article_data['title'] = title_elem.get_text(strip=True)
        
        # 提取作者和发布时间
        article_sm = soup.select_one('div.article-sm')
        if article_sm:
            text = article_sm.get_text(separator=' | ', strip=True)
            # 解析格式: "作者：xxx | 发布时间：yyyy年mm月dd日 HH:MM | 点击数：xxx"
            parts = text.split(' | ')
            for part in parts:
                if '作者：' in part:
                    article_data['author'] = part.replace('作者：', '').strip()
                elif '发布时间：' in part:
                    article_data['publish_time'] = part.replace('发布时间：', '').strip()
        
        # 提取文章内容
        content_elem = soup.select_one('div#vsb_content')
        if content_elem:
            # 移除script和style标签
            for tag in content_elem(['script', 'style']):
                tag.decompose()
            
            # 获取文本内容
            text = content_elem.get_text(separator='\n', strip=True)
            article_data['content'] = text
        
    except Exception as e:
        pass
    
    return article_data


def fetch_article_content(url: str, session: requests.Session, headers: dict) -> str:
    """
    爬取文章详情内容
    
    Args:
        url: 文章URL
        session: requests会话
        headers: 请求头
        
    Returns:
        str: 文章内容文本
    """
    if not url:
        return ""
    
    try:
        response = session.get(url, headers=headers, timeout=10, verify=False)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            return ""
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尝试多种选择器查找文章内容
        content = None
        for selector in [
            'div#vsb_content',
            'div.article-content',
            'div.news-content',
            'div.content',
            'article',
            'div[class*="content"]',
            'div[id*="content"]'
        ]:
            content = soup.select_one(selector)
            if content:
                break
        
        if content:
            # 移除script和style标签
            for tag in content(['script', 'style']):
                tag.decompose()
            
            # 获取文本
            text = content.get_text(separator='\n', strip=True)
            return text[:5000]  # 限制内容长度
        
        return ""
        
    except Exception as e:
        return ""


def save_article(article: dict):
    """
    保存单篇文章到JSON文件
    
    Args:
        article: 文章字典
    """
    ensure_articles_dir()
    
    filename = generate_filename(article['title'], article.get('url', ''))
    filepath = os.path.join(ARTICLES_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=2)
    except IOError as e:
        logger.error(f"保存文件失败: {str(e)}")


def save_article_detailed(article: dict) -> bool:
    """
    保存详细的文章信息到 JSON 文件，并更新索引
    
    Args:
        article: 包含完整信息的文章字典
        
    Returns:
        bool: 保存成功返回 True
    """
    ensure_articles_dir()
    
    if not article.get('title'):
        return False
    
    url = article.get('url', '')
    filename = generate_filename(article['title'], url)
    filepath = os.path.join(ARTICLES_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=2)
        
        # 更新索引
        add_to_articles_index(url, filename, article)
        
        return True
    except IOError as e:
        return False


def fetch_news_pages(pages: int) -> bool:
    """
    爬取指定页数的新闻
    
    Args:
        pages: 要爬取的页数 (1-10)
        
    Returns:
        bool: 爬取成功返回True，失败返回False
    """
    logger.info(f"正在爬取 {pages} 页新闻，请耐心等待...")
    
    # 创建请求会话，禁用代理
    session = requests.Session()
    session.trust_env = False
    
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    base_url = "https://nbw.sztu.edu.cn/list.jsp?urltype=tree.TreeTempUrl&wbtreeid=1029"
    articles_saved = 0
    
    try:
        for page_num in range(1, pages + 1):
            # 构造分页URL
            if page_num == 1:
                url = base_url
            else:
                url = f"{base_url}&page={page_num}"
            
            logger.info(f"正在爬取第 {page_num} 页...")
            
            try:
                response = session.get(url, headers=headers, timeout=10, verify=False)
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    logger.warning(f"HTTP {response.status_code}")
                    continue
                
                # 解析HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找文章列表容器
                articles_found = 0
                
                # 尝试多种可能的选择器来查找文章
                article_elements = soup.select('a[href*="news"]') or soup.select('div.news-item') or soup.select('li')
                
                for element in article_elements:
                    try:
                        # 提取标题
                        title = element.get_text(strip=True)
                        if not title or len(title) < 5:
                            continue
                        
                        # 提取链接
                        href = element.get('href', '')
                        if href:
                            href = urljoin(base_url, href)
                        
                        # 检查是否已缓存（索引存在且文件存在）
                        if href and is_article_cached(href):
                            continue
                        
                        # 爬取文章详情内容
                        content = ""
                        if href:
                            logger.info("获取详情...")
                            content = fetch_article_content(href, session, headers)
                        
                        article = {
                            'title': title,
                            'url': href,
                            'content': content,
                            'author': 'SZTU',
                            'publish_time': time.strftime('%Y-%m-%d'),
                            'fetch_time': time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        # 保存文章
                        save_article(article)
                        articles_found += 1
                        articles_saved += 1
                    except Exception as e:
                        continue
                
                logger.info(f"保存 {articles_found} 篇")
                time.sleep(1)  # 礼貌延迟
                
            except requests.exceptions.RequestException as e:
                logger.error(f"网络错误: {str(e)}")
                continue
        
        if articles_saved > 0:
            logger.info(f"爬取完成！共保存 {articles_saved} 篇新文章到 {ARTICLES_DIR}/ 目录")
            return True
        else:
            logger.warning("未获取到任何新文章")
            return False
            
    except Exception as e:
        logger.error(f"爬取失败: {str(e)}")
        return False
    finally:
        session.close()


def extract_news_links_from_html(html_content: str, base_url: str = "https://nbw.sztu.edu.cn/") -> list:
    """
    从 HTML 内容中提取新闻标题和链接
    
    Args:
        html_content: HTML 页面内容
        base_url: 基础 URL，用于转换相对链接
        
    Returns:
        list: 包含新闻信息的字典列表
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    articles = []
    
    # 查找所有新闻列表项
    # 根据 HTML 结构，每条新闻在 <li class="clearfix"> 中
    news_items = soup.find_all('li', class_='clearfix')
    
    for item in news_items:
        try:
            # 提取序号
            serial = item.find('div', class_='width01')
            serial_text = serial.get_text(strip=True) if serial else ''
            
            # 提取类别
            category_div = item.find('div', class_='width02')
            category_link = category_div.find('a') if category_div else None
            category = category_link.get_text(strip=True) if category_link else ''
            
            # 提取发文单位
            department_div = item.find('div', class_='width03')
            department_link = department_div.find('a') if department_div else None
            department = department_link.get_text(strip=True) if department_link else ''
            
            # 提取标题和链接
            title_div = item.find('div', class_='width04')
            if not title_div:
                continue
            
            title_link = title_div.find('a')
            if not title_link:
                continue
            
            # 从 title 属性或 span 文本获取标题
            title = title_link.get('title', '') or title_link.find('span').get_text(strip=True) if title_link.find('span') else ''
            href = title_link.get('href', '')
            
            # 转换相对链接为绝对链接
            full_url = urljoin(base_url, href)
            
            # 提取是否有附件
            attachment_div = item.find('div', class_='width05')
            has_attachment = bool(attachment_div.find('img')) if attachment_div else False
            
            # 提取发文日期
            date_div = item.find('div', class_='width06')
            publish_date = date_div.get_text(strip=True) if date_div else ''
            
            article = {
                'serial': serial_text,
                'category': category,
                'department': department,
                'title': title,
                'url': full_url,
                'has_attachment': has_attachment,
                'publish_date': publish_date,
                'fetch_time': datetime.now().isoformat()
            }
            
            articles.append(article)
            
        except Exception as e:
            continue
    
    return articles





def fetch_news_pages_with_json(pages: int) -> bool:
    """
    爬取指定页数的新闻，并将新闻链接和标题保存到 JSON 文件
    
    Args:
        pages: 要爬取的页数 (1-10)
        
    Returns:
        bool: 爬取成功返回True，失败返回False
    """
    logger.info(f"正在爬取 {pages} 页新闻并保存为 JSON...")
    
    # 创建请求会话，禁用代理
    session = requests.Session()
    session.trust_env = False
    
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    base_url = "https://nbw.sztu.edu.cn/list.jsp?urltype=tree.TreeTempUrl&wbtreeid=1029"
    pages_saved = 0
    total_articles = 0
    
    try:
        for page_num in range(1, pages + 1):
            # 构造分页URL
            if page_num == 1:
                url = base_url
            else:
                url = f"{base_url}&PAGENUM={page_num}"
            
            logger.info(f"正在爬取第 {page_num} 页...")
            
            try:
                response = session.get(url, headers=headers, timeout=10, verify=False)
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    logger.warning(f"HTTP {response.status_code}")
                    continue
                
                # 从 HTML 中提取新闻信息
                articles = extract_news_links_from_html(response.text, base_url)
                
                if articles:
                    # 显示提取到的新闻信息
                    logger.info(f"提取 {len(articles)} 条新闻")
                    total_articles += len(articles)
                else:
                    logger.warning("未找到新闻")
                
                time.sleep(1)  # 礼貌延迟
                
            except requests.exceptions.RequestException as e:
                logger.error(f"网络错误: {str(e)}")
                continue
        
        if total_articles > 0:
            logger.info(f"爬取完成！共提取 {total_articles} 条新闻")
            return True
        else:
            logger.warning("未获取到任何新闻")
            return False
            
    except Exception as e:
        logger.error(f"爬取失败: {str(e)}")
        return False
    finally:
        session.close()


def fetch_articles_with_details(pages: int) -> bool:
    """
    爬取指定页数的新闻，并保存每篇文章的完整详情（标题、内容、作者、时间等）
    
    Args:
        pages: 要爬取的页数 (1-10)
        
    Returns:
        bool: 爬取成功返回True，失败返回False
    """
    logger.info(f"正在爬取 {pages} 页新闻，保存完整详情...")
    
    # 创建请求会话，禁用代理
    session = requests.Session()
    session.trust_env = False
    
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    base_url = "https://nbw.sztu.edu.cn/list.jsp?urltype=tree.TreeTempUrl&wbtreeid=1029"
    articles_saved = 0
    
    try:
        for page_num in range(1, pages + 1):
            # 构造分页URL
            if page_num == 1:
                url = base_url
            else:
                url = f"{base_url}&PAGENUM={page_num}"
            
            logger.info(f"正在爬取第 {page_num} 页...")
            
            try:
                response = session.get(url, headers=headers, timeout=10, verify=False)
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    logger.warning(f"HTTP {response.status_code}")
                    continue
                
                # 从列表页面提取新闻链接
                articles_list = extract_news_links_from_html(response.text, base_url)
                
                if not articles_list:
                    logger.warning("未找到新闻")
                    continue
                
                # 对每篇新闻，访问详情页面获取完整信息
                articles_found = 0
                for article_info in articles_list:
                    article_url = article_info.get('url', '')
                    
                    if not article_url:
                        continue
                    
                    # 检查是否已缓存（索引存在且文件存在）
                    if is_article_cached(article_url):
                        logger.info(f"⏭️  跳过已缓存文章: {article_info.get('title', '')}")
                        continue
                    
                    try:
                        # 获取详情页面
                        detail_response = session.get(article_url, headers=headers, timeout=10, verify=False)
                        detail_response.encoding = 'utf-8'
                        
                        if detail_response.status_code == 200:
                            # 提取详细信息
                            article_detail = extract_article_details(detail_response.text, article_url)
                            
                            # 补充列表页面获取的信息
                            article_detail['category'] = article_info.get('category', '')
                            article_detail['department'] = article_info.get('department', '')
                            article_detail['serial'] = article_info.get('serial', '')
                            article_detail['has_attachment'] = article_info.get('has_attachment', False)
                            
                            # 保存文章
                            if save_article_detailed(article_detail):
                                articles_found += 1
                                articles_saved += 1
                        
                        time.sleep(0.5)  # 礼貌延迟
                        
                    except Exception as e:
                        continue
                
                logger.info(f"保存 {articles_found} 篇")
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"网络错误: {str(e)}")
                continue
        
        if articles_saved > 0:
            logger.info(f"爬取完成！共保存 {articles_saved} 篇文章到 {ARTICLES_DIR}/ 目录")
            return True
        else:
            logger.warning("未获取到任何新文章")
            return False
            
    except Exception as e:
        logger.error(f"爬取失败: {str(e)}")
        return False
    finally:
        session.close()
