#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 文章总结模块
使用 Google Gemini API 对爬取的文章进行 AI 总结、关键词提取等处理

⚠️ 注意：此模块为通用文章处理，建议使用 structured_ai_summarizer.py 进行
学校通知的相关性分析，它提供结构化输出和更好的个性化功能。
"""

import json
import os
import sys
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from google import genai

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from logger_config import get_logger

logger = get_logger(__name__)


class AISummarizer:
    """使用 Gemini API 进行文章处理的类"""
    
    def __init__(self, config=None):
        """
        初始化 AI 总结器
        
        Args:
            config: 配置对象，如果为 None 则使用默认配置
        """
        self.config = config or get_config()
        self._initialize_storage()
        self._initialize_genai()
    
    def _initialize_storage(self) -> None:
        """初始化持久化存储目录"""
        self.articles_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'articles'
        )
        self.summary_dir = os.path.join(self.articles_dir, 'summaries')
        
        os.makedirs(self.summary_dir, exist_ok=True)
        logger.info(f"✅ 摘要存储目录: {self.summary_dir}")
    
    def _initialize_genai(self) -> None:
        """初始化 Gemini API"""
        api_key = self.config.gemini_api_key
        
        if not api_key:
            raise ValueError(
                "❌ 未设置 Gemini API Key，请在 config.json 中配置 gemini.api_key"
            )
        
        # 新版本 API：在 Client 中传入 api_key
        self.api_key = api_key
        logger.info("✅ Gemini API 初始化成功")
        self.model_name = self.config.gemini_model
    
    def _calculate_config_md5(self) -> str:
        """计算 config.json 的 MD5 校验和"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'config.json'
        )
        
        if not os.path.exists(config_path):
            return ""
        
        try:
            with open(config_path, 'rb') as f:
                md5_hash = hashlib.md5()
                for chunk in iter(lambda: f.read(4096), b''):
                    md5_hash.update(chunk)
                return md5_hash.hexdigest()
        except Exception as e:
            logger.error(f"❌ 计算 config.json MD5 失败: {str(e)}")
            return ""
    
    def _get_model(self):
        """获取 Gemini 模型实例"""
        return genai.Client().models.get(self.model_name)
    
    def summarize_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        总结文章
        
        Args:
            article: 文章数据字典，包含 title, content 等字段
            
        Returns:
            包含总结结果的字典
        """
        try:
            content = article.get('content', '')
            title = article.get('title', '')
            
            if not content:
                logger.warning(f"⚠️ 文章内容为空: {title}")
                return {
                    'status': 'error',
                    'message': '文章内容为空',
                    'summary': None
                }
            
            # 获取总结提示词
            prompt_template = self.config.get_prompt(
                'summarize_article',
                "请用中文总结以下新闻文章，保留关键信息和要点。\n\n文章内容：\n{content}"
            )
            
            # 替换占位符
            prompt = prompt_template.format(content=content)
            
            logger.info(f"🔄 正在总结文章: {title[:50]}...")
            
            # 调用 Gemini API（新版本 API）
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            summary = response.text
            logger.info(f"✅ 文章总结成功: {title[:50]}...")
            
            return {
                'status': 'success',
                'title': title,
                'summary': summary
            }
        
        except Exception as e:
            logger.error(f"❌ 文章总结失败: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'summary': None
            }
    
    def extract_keywords(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        从文章中提取关键词
        
        Args:
            article: 文章数据字典
            
        Returns:
            包含关键词的字典
        """
        try:
            content = article.get('content', '')
            title = article.get('title', '')
            
            if not content:
                logger.warning(f"⚠️ 文章内容为空: {title}")
                return {
                    'status': 'error',
                    'message': '文章内容为空',
                    'keywords': []
                }
            
            # 获取关键词提示词
            prompt_template = self.config.get_prompt(
                'extract_keywords',
                "请从以下新闻文章中提取5-10个关键词，用中文表示，以逗号分隔。\n\n文章内容：\n{content}"
            )
            
            prompt = prompt_template.format(content=content)
            
            logger.info(f"🔄 正在提取关键词: {title[:50]}...")
            
            # 调用 Gemini API（新版本 API）
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            keywords_text = response.text
            # 将逗号分隔的关键词转换为列表
            keywords = [kw.strip() for kw in keywords_text.split(',')]
            
            logger.info(f"✅ 关键词提取成功: {title[:50]}...")
            
            return {
                'status': 'success',
                'title': title,
                'keywords': keywords
            }
        
        except Exception as e:
            logger.error(f"❌ 关键词提取失败: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'keywords': []
            }
    
    def generate_title(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        为文章生成标题
        
        Args:
            article: 文章数据字典
            
        Returns:
            包含生成标题的字典
        """
        try:
            content = article.get('content', '')
            original_title = article.get('title', '')
            
            if not content:
                logger.warning(f"⚠️ 文章内容为空")
                return {
                    'status': 'error',
                    'message': '文章内容为空',
                    'generated_title': None
                }
            
            # 获取标题生成提示词
            prompt_template = self.config.get_prompt(
                'generate_title',
                "请为以下新闻内容生成一个简洁有力的标题（中文）。\n\n新闻内容：\n{content}"
            )
            
            prompt = prompt_template.format(content=content)
            
            logger.info(f"🔄 正在生成标题...")
            
            response = genai.Client().models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            generated_title = response.text.strip()
            logger.info(f"✅ 标题生成成功")
            
            return {
                'status': 'success',
                'original_title': original_title,
                'generated_title': generated_title
            }
        
        except Exception as e:
            logger.error(f"❌ 标题生成失败: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'generated_title': None
            }
    
    def process_articles(
        self,
        articles: List[Dict[str, Any]],
        action: str = 'summarize'
    ) -> List[Dict[str, Any]]:
        """
        批量处理多篇文章
        
        Args:
            articles: 文章列表
            action: 处理类型 ('summarize', 'keywords', 'title')
            
        Returns:
            处理结果列表
        """
        results = []
        total = len(articles)
        
        logger.info(f"🚀 开始处理 {total} 篇文章，操作类型: {action}")
        
        for idx, article in enumerate(articles, 1):
            logger.info(f"[{idx}/{total}] 处理中...")
            
            if action == 'summarize':
                result = self.summarize_article(article)
            elif action == 'keywords':
                result = self.extract_keywords(article)
            elif action == 'title':
                result = self.generate_title(article)
            else:
                logger.error(f"❌ 未知的操作类型: {action}")
                continue
            
            results.append(result)
        
        logger.info(f"✅ 处理完成，共处理 {len(results)} 篇文章")
        
        return results


def main():
    """主函数 - 示例用法"""
    try:
        # 初始化总结器
        summarizer = AISummarizer()
        
        # 示例：加载并处理一篇文章
        articles_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'articles'
        )
        
        # 读取第一篇文章
        article_files = [f for f in os.listdir(articles_dir) 
                        if f.endswith('.json') and f != 'index.json']
        
        if not article_files:
            logger.warning("⚠️ 没有找到文章文件")
            return
        
        with open(os.path.join(articles_dir, article_files[0]), 'r', encoding='utf-8') as f:
            article = json.load(f)
        
        logger.info(f"📖 加载文章: {article.get('title', 'Unknown')}")
        
        # 测试总结功能
        print("\n" + "="*60)
        print("📋 文章总结")
        print("="*60)
        result = summarizer.summarize_article(article)
        if result['status'] == 'success':
            print(f"标题: {result['title']}\n")
            print(f"总结:\n{result['summary']}")
        else:
            print(f"错误: {result['message']}")
        
        # 测试关键词提取
        print("\n" + "="*60)
        print("🏷️ 关键词提取")
        print("="*60)
        result = summarizer.extract_keywords(article)
        if result['status'] == 'success':
            print(f"标题: {result['title']}\n")
            print(f"关键词: {', '.join(result['keywords'])}")
        else:
            print(f"错误: {result['message']}")
    
    except Exception as e:
        logger.error(f"❌ 程序执行失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
