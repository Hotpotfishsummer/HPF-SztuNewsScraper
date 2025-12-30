#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 HTML 页面提取新闻标题和链接，保存到 JSON 文件
"""

import json
import os
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from logger_config import get_logger

logger = get_logger(__name__)


def extract_news_from_html(html_content: str, base_url: str = "https://nbw.sztu.edu.cn/") -> list:
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
            logger.warning(f"提取单条新闻时出错: {str(e)}")
            continue
    
    return articles


def save_articles_to_json(articles: list, output_file: str = "news_articles.json"):
    """
    保存提取的新闻到 JSON 文件
    
    Args:
        articles: 新闻列表
        output_file: 输出文件名
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        logger.info(f"成功保存 {len(articles)} 条新闻到 {output_file}")
    except IOError as e:
        logger.error(f"保存文件失败: {str(e)}")


def extract_from_file(html_file: str, output_file: str = "news_articles.json"):
    """
    从 HTML 文件中提取新闻并保存
    
    Args:
        html_file: HTML 文件路径
        output_file: 输出 JSON 文件名
    """
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        articles = extract_news_from_html(html_content)
        
        if not articles:
            logger.warning("未找到任何新闻")
            return
        
        logger.info(f"提取到 {len(articles)} 条新闻:")
        for i, article in enumerate(articles, 1):
            logger.info(f"{i}. 【{article['category']}】{article['title']}")
            logger.info(f"   发布部门: {article['department']}")
            logger.info(f"   发布日期: {article['publish_date']}")
            logger.info(f"   链接: {article['url']}")
            logger.info(f"   附件: {'有' if article['has_attachment'] else '无'}")
        
        save_articles_to_json(articles, output_file)
        
    except FileNotFoundError:
        logger.error(f"文件不存在: {html_file}")
    except Exception as e:
        logger.error(f"处理失败: {str(e)}")


if __name__ == "__main__":
    # 示例：从 tmp/main.res 提取新闻
    extract_from_file("tmp/main.res", "tmp/news_articles.json")
