#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 结构化输出模块 - 学校通知相关性分析
使用 Gemini API 的结构化输出功能分析文章与用户的相关程度
"""

import json
import os
import sys
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from google import genai
from pydantic import BaseModel, Field

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from logger_config import get_logger

logger = get_logger(__name__)


# 定义结构化输出的数据模型
class ArticleRelevanceResponse(BaseModel):
    """文章相关性分析的结构化响应模型"""
    
    title: str = Field(description="文章的标题")
    summary: str = Field(description="文章内容的简明总结，提取核心信息")
    relevance_score: float = Field(
        description="与用户相关程度评分，范围从 0 到 10，10 表示与用户最相关",
        ge=0,
        le=10
    )
    relevance_reason: str = Field(
        description="评分原因说明，简述为什么这条新闻与用户相关或不相关"
    )


class StructuredAISummarizer:
    """使用结构化输出的 AI 相关性分析器"""
    
    def __init__(self, config=None):
        """
        初始化结构化 AI 分析器
        
        Args:
            config: 配置对象，如果为 None 则使用默认配置
        """
        self.config = config or get_config()
        self._validate_config()
        self._initialize_storage()
        self._initialize_genai()
    
    def _initialize_storage(self) -> None:
        """初始化持久化存储目录"""
        self.articles_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'articles'
        )
        self.analysis_dir = os.path.join(self.articles_dir, 'analysis_results')
        
        # 创建分析结果目录
        os.makedirs(self.analysis_dir, exist_ok=True)
        logger.info(f"✅ 分析结果存储目录: {self.analysis_dir}")
    
    def _validate_config(self) -> None:
        """验证必需的配置项是否存在"""
        try:
            # 验证必需的提示词配置
            self.config.get_prompt('analyze_relevance')
            logger.info("✅ 配置验证通过：所有必需的提示词都已配置")
        except KeyError as e:
            logger.error(f"❌ 配置验证失败: {str(e)}")
            raise
    
    def _initialize_genai(self) -> None:
        """初始化 Gemini API"""
        api_key = self.config.gemini_api_key
        
        if not api_key:
            raise ValueError(
                "❌ 未设置 Gemini API Key，请在 config.json 中配置 gemini.api_key"
            )
        
        # 存储 API Key，在创建 client 时使用
        self.api_key = api_key
        
        # 如果启用了代理，通过环境变量配置代理
        # Gemini SDK 会自动读取这些环境变量
        if self.config.proxy_enabled:
            proxy_url = self.config.get_proxy_url()
            if proxy_url:
                import os
                logger.info(f"🔐 代理已启用: {self.config.get('proxy.host')}:{self.config.get('proxy.port')}")
                # 设置环境变量，Gemini SDK 会自动使用
                os.environ['http_proxy'] = proxy_url
                os.environ['https_proxy'] = proxy_url
                # 对于 requests 库也设置这些
                os.environ['HTTP_PROXY'] = proxy_url
                os.environ['HTTPS_PROXY'] = proxy_url
                logger.info("✅ 环境变量代理配置成功")
        
        logger.info("✅ Gemini API 初始化成功")
        self.model_name = self.config.gemini_model
    
    def _load_response_schema(self) -> Dict[str, Any]:
        """
        加载响应 Schema
        
        Returns:
            Schema 字典
        """
        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'response_schema.json'
        )
        
        if not os.path.exists(schema_path):
            logger.warning(f"⚠️ 响应 Schema 文件不存在: {schema_path}")
            return self._get_default_schema()
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Schema 文件格式错误: {str(e)}")
            return self._get_default_schema()
    
    def _get_default_schema(self) -> Dict[str, Any]:
        """获取默认的响应 Schema"""
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "文章的标题"
                },
                "summary": {
                    "type": "string",
                    "description": "文章内容的简明总结，提取核心信息"
                },
                "relevance_score": {
                    "type": "number",
                    "description": "与用户相关程度评分，范围从 0 到 10，10 表示与用户最相关",
                    "minimum": 0,
                    "maximum": 10
                },
                "relevance_reason": {
                    "type": "string",
                    "description": "评分原因说明，简述为什么这条新闻与用户相关或不相关"
                }
            },
            "required": ["title", "summary", "relevance_score", "relevance_reason"]
        }
    
    def analyze_article(self, article: Dict[str, Any], source_filename: str = None) -> Dict[str, Any]:
        """
        使用结构化输出分析文章与用户的相关性
        
        Args:
            article: 文章数据字典
            source_filename: 源文件名（用于保存分析结果，如果为 None 则自动生成）
            
        Returns:
            包含分析结果的字典
        """
        try:
            content = article.get('content', '')
            original_title = article.get('title', '')
            
            if not content:
                logger.warning(f"⚠️ 文章内容为空: {original_title}")
                return {
                    'status': 'error',
                    'message': '文章内容为空',
                    'data': None,
                    'source_filename': source_filename,
                    'original_title': original_title
                }
            
            # 获取用户信息和提示词模板
            user_profile = self.config.get('user_profile', {})
            
            # 从配置文件获取提示词模板（必须存在）
            try:
                prompt_template = self.config.get_prompt('analyze_relevance')
            except KeyError as e:
                logger.error(f"❌ 配置错误: {str(e)}")
                raise
            
            # 提取嵌套的用户信息
            basic_info = user_profile.get('basic_info', {})
            education = user_profile.get('education', {})
            interests = user_profile.get('interests', {})
            dislikes = user_profile.get('dislikes', {})
            
            # 处理兴趣和不感兴趣的内容（支持新旧配置格式）
            interests_topics = ', '.join(interests.get('topics', user_profile.get('interests', [])))
            interests_keywords = ', '.join(interests.get('keywords', user_profile.get('relevant_keywords', [])))
            dislike_topics = ', '.join(dislikes.get('topics', []))
            dislike_keywords = ', '.join(dislikes.get('keywords', []))
            
            # 格式化提示词
            prompt = prompt_template.format(
                user_name=basic_info.get('name', user_profile.get('name', '')),
                student_id=basic_info.get('student_id', user_profile.get('student_id', '')),
                department=education.get('department', user_profile.get('department', '')),
                major=education.get('major', user_profile.get('major', '')),
                grade=education.get('grade', ''),
                **{'class': education.get('class', '')},  # 使用 ** 解包避免 class 关键字
                interests=interests_topics,
                relevant_keywords=interests_keywords,
                uninterested_topics=dislike_topics,
                uninterested_keywords=dislike_keywords,
                title=original_title,
                content=content
            )
            
            logger.info(f"🔄 正在分析文章与用户的相关性: {original_title[:50]}...")
            
            # 调用 Gemini API 使用结构化输出
            # 新版本 google-genai 使用简化的 Schema 定义
            client = genai.Client(api_key=self.api_key)
            
            # 定义响应 schema - 新版本使用简化的字典格式
            response_schema = {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "文章的标题"
                    },
                    "summary": {
                        "type": "string",
                        "description": "文章内容的简明总结"
                    },
                    "relevance_score": {
                        "type": "number",
                        "description": "与用户相关程度评分（0-10）,10分表示最相关"
                    },
                    "relevance_reason": {
                        "type": "string",
                        "description": "评分原因说明，简述为什么这条新闻与用户相关或不相关"
                    }
                },
                "required": ["title", "summary", "relevance_score", "relevance_reason"]
            }
            
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema
                )
            )
            
            # 解析响应
            if response.text:
                result_data = json.loads(response.text)
                logger.info(f"✅ 文章分析成功: {original_title[:50]}...")
                
                return {
                    'status': 'success',
                    'original_title': original_title,
                    'source_filename': source_filename,
                    'data': result_data
                }
            else:
                logger.error("❌ API 返回空响应")
                return {
                    'status': 'error',
                    'message': 'API 返回空响应',
                    'data': None,
                    'source_filename': source_filename,
                    'original_title': original_title
                }
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ 响应 JSON 解析失败: {str(e)}")
            return {
                'status': 'error',
                'message': f'JSON 解析失败: {str(e)}',
                'data': None,
                'source_filename': source_filename,
                'original_title': original_title
            }
        
        except Exception as e:
            logger.error(f"❌ 文章分析失败: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'data': None,
                'source_filename': source_filename,
                'original_title': original_title
            }
    
    def analyze_articles(self, articles: List[Dict[str, Any]], source_filenames: List[str] = None) -> List[Dict[str, Any]]:
        """
        批量分析多篇文章
        
        Args:
            articles: 文章列表
            source_filenames: 对应的源文件名列表（可选）
            
        Returns:
            分析结果列表
        """
        results = []
        total = len(articles)
        
        # 如果没有提供文件名，则为每篇文章生成一个
        if not source_filenames:
            source_filenames = [None] * total
        
        logger.info(f"🚀 开始分析 {total} 篇文章")
        
        for idx, (article, filename) in enumerate(zip(articles, source_filenames), 1):
            logger.info(f"[{idx}/{total}] 处理中...")
            result = self.analyze_article(article, source_filename=filename)
            results.append(result)
            
            # 如果分析成功，保存单个文章结果
            if result['status'] == 'success' and 'original_title' in result:
                self._save_single_article_result(result)
        
        logger.info(f"✅ 分析完成，共处理 {len(results)} 篇文章")
        
        return results
    
    def _calculate_config_md5(self) -> str:
        """
        计算 config.json 的 MD5 校验和
        
        Returns:
            MD5 哈希值
        """
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'config.json'
        )
        
        if not os.path.exists(config_path):
            logger.warning(f"⚠️ config.json 文件不存在: {config_path}")
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
    
    def _save_single_article_result(self, result: Dict[str, Any]) -> None:
        """
        保存单个文章的分析结果到文件
        
        Args:
            result: 分析结果字典
        """
        try:
            if 'original_title' not in result or result['status'] != 'success':
                return
            
            # 从原始标题生成文件名（使用 MD5 确保唯一性）
            # 假设文章已经有了源文件名，从 data 中提取
            article_data = result.get('data', {})
            source_filename = result.get('source_filename', None)
            
            if not source_filename:
                # 如果没有源文件名，生成一个
                title_hash = hashlib.md5(result['original_title'].encode()).hexdigest()
                source_filename = f"{title_hash}.json"
            
            # 构建完整的输出路径
            output_path = os.path.join(self.analysis_dir, source_filename)
            
            # 构建包含元数据的结果
            persistence_data = {
                'source_file': source_filename,
                'generated_at': datetime.now().isoformat(),
                'config_md5': self._calculate_config_md5(),
                'analysis_result': article_data
            }
            
            # 保存到文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(persistence_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 分析结果已保存: {output_path}")
        
        except Exception as e:
            logger.error(f"❌ 保存分析结果失败: {str(e)}")
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str = None) -> None:
        """
        批量保存分析结果到文件（可选）
        
        注意：单个文章的结果已在 analyze_article() 时自动保存到 articles/analysis_results/ 目录
        
        Args:
            results: 分析结果列表
            output_file: 输出文件路径（可选，用于生成汇总报告）
        """
        if not output_file:
            logger.info("💾 单个文章结果已自动保存到 articles/analysis_results/ 目录")
            return
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 汇总结果已保存到: {output_file}")
        except Exception as e:
            logger.error(f"❌ 保存汇总结果失败: {str(e)}")
    
    def load_saved_result(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        加载已保存的分析结果
        
        Args:
            filename: 文件名（相对于 analysis_results 目录）
            
        Returns:
            分析结果字典，如果文件不存在或 config 已变化则返回 None
        """
        result_path = os.path.join(self.analysis_dir, filename)
        
        if not os.path.exists(result_path):
            logger.warning(f"⚠️ 分析结果文件不存在: {result_path}")
            return None
        
        try:
            with open(result_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 验证 config.json 是否已变化
            stored_md5 = data.get('config_md5', '')
            current_md5 = self._calculate_config_md5()
            
            if stored_md5 != current_md5:
                logger.warning(
                    f"⚠️ 配置已变化，缓存结果可能已过期: {filename}\n"
                    f"  旧 MD5: {stored_md5}\n"
                    f"  新 MD5: {current_md5}"
                )
                return None
            
            logger.info(f"✅ 已加载缓存结果: {filename}")
            return data
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ 结果文件格式错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ 加载结果失败: {str(e)}")
            return None
    
    def result_exists(self, filename: str) -> bool:
        """
        检查分析结果是否已存在且有效
        
        Args:
            filename: 文件名
            
        Returns:
            True 如果结果存在且 config 未变化，否则 False
        """
        return self.load_saved_result(filename) is not None
    
    def analyze_articles_from_dir(self, skip_existing: bool = True) -> List[Dict[str, Any]]:
        """
        从 articles 目录读取所有文章并进行分析
        
        Args:
            skip_existing: 是否跳过已存在的分析结果（config 未变化时）
            
        Returns:
            分析结果列表
        """
        # 读取 articles 目录中的所有 JSON 文件
        article_files = []
        for filename in os.listdir(self.articles_dir):
            if filename.endswith('.json') and filename != 'index.json':
                article_files.append(filename)
        
        if not article_files:
            logger.warning("⚠️ 在 articles 目录中未找到任何文章")
            return []
        
        articles = []
        filenames = []
        
        for filename in article_files:
            filepath = os.path.join(self.articles_dir, filename)
            
            # 检查是否跳过已存在的结果
            if skip_existing and self.result_exists(filename):
                logger.info(f"⏭️ 跳过已分析的文章（配置未变）: {filename}")
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                articles.append(article)
                filenames.append(filename)
            except json.JSONDecodeError as e:
                logger.error(f"❌ 文章文件格式错误: {filename} - {str(e)}")
            except Exception as e:
                logger.error(f"❌ 读取文章失败: {filename} - {str(e)}")
        
        if articles:
            logger.info(f"📚 加载了 {len(articles)} 篇文章进行分析")
            return self.analyze_articles(articles, source_filenames=filenames)
        else:
            logger.info("✅ 所有文章都已分析过，无需重新分析")
            return []
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """
        获取分析统计信息
        
        Returns:
            包含统计信息的字典
        """
        if not os.path.exists(self.analysis_dir):
            return {
                'total_analyzed': 0,
                'analysis_results_dir': self.analysis_dir
            }
        
        result_files = [f for f in os.listdir(self.analysis_dir) if f.endswith('.json')]
        
        stats = {
            'total_analyzed': len(result_files),
            'analysis_results_dir': self.analysis_dir,
            'files': []
        }
        
        for filename in result_files:
            filepath = os.path.join(self.analysis_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    stats['files'].append({
                        'filename': filename,
                        'generated_at': data.get('generated_at'),
                        'relevance_score': data.get('analysis_result', {}).get('relevance_score')
                    })
            except Exception as e:
                logger.warning(f"⚠️ 无法读取统计信息: {filename} - {str(e)}")
        
        return stats


def main():
    """主函数 - 演示完整的分析工作流"""
    try:
        print("\n" + "="*70)
        print("🚀 学校通知相关性分析系统")
        print("="*70)
        
        # 初始化分析器
        analyzer = StructuredAISummarizer()
        
        # 方式 1: 从 articles 目录自动读取并分析所有文章
        print("\n📚 从 articles 目录读取并分析所有文章...")
        results = analyzer.analyze_articles_from_dir(skip_existing=True)
        
        if results:
            # 显示分析结果摘要
            successful = sum(1 for r in results if r['status'] == 'success')
            print(f"\n✅ 分析完成: {successful}/{len(results)} 篇文章成功分析")
            
            # 显示部分结果
            for result in results[:3]:
                if result['status'] == 'success':
                    data = result['data']
                    print(f"\n  📄 {data['title'][:30]}...")
                    print(f"     相关性评分: {data['relevance_score']}/10")
        
        # 显示统计信息
        print("\n📊 分析统计信息:")
        stats = analyzer.get_analysis_stats()
        print(f"   总分析文章数: {stats['total_analyzed']}")
        print(f"   存储目录: {stats['analysis_results_dir']}")
        
        if stats['files']:
            print(f"\n   📈 相关性评分分布:")
            scores = [f['relevance_score'] for f in stats['files'] if f['relevance_score'] is not None]
            if scores:
                avg_score = sum(scores) / len(scores)
                max_score = max(scores)
                min_score = min(scores)
                print(f"      平均: {avg_score:.1f}/10 | 最高: {max_score}/10 | 最低: {min_score}/10")
        
        # 演示加载缓存结果
        if stats['files']:
            first_file = stats['files'][0]['filename']
            print(f"\n💾 演示加载缓存结果: {first_file}")
            cached = analyzer.load_saved_result(first_file)
            if cached:
                result = cached['analysis_result']
                print(f"   标题: {result['title']}")
                print(f"   摘要: {result['summary'][:50]}...")
                print(f"   相关性: {result['relevance_score']}/10")
        
        print("\n" + "="*70)
        print("✨ 分析完成！结果已保存到 articles/analysis_results/ 目录")
        print("="*70 + "\n")
    
    except Exception as e:
        logger.error(f"❌ 程序执行失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
