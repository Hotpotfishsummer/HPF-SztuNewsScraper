#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dify 工作流对接模块 - 新闻相关性分析
对接 Dify 工作流，接收用户资料和新闻文件，返回结构化的相关性分析结果
"""

import json
import sys
import os
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

# 添加 src 目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import get_config
from logger_config import get_logger
from ai.dify_client import DifyClient

logger = get_logger(__name__)


class DifyWorkflowHandler:
    """处理 Dify 工作流的输入输出"""
    
    def __init__(self):
        """初始化工作流处理器"""
        self.config = get_config()
        self.logger = logger
        self.dify_client = DifyClient()
    
    def validate_inputs(self, user_profile_str: str, news_file_path: str) -> Dict[str, Any]:
        """
        验证输入参数
        
        Args:
            user_profile_str: 用户资料的 JSON 字符串
            news_file_path: 新闻文件路径
            
        Returns:
            包含验证结果和解析数据的字典
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'user_profile': None,
            'news_data': None
        }
        
        # 验证用户资料 JSON 字符串
        try:
            user_profile = json.loads(user_profile_str)
            validation_result['user_profile'] = user_profile
            self.logger.info("✅ 用户资料 JSON 解析成功")
        except json.JSONDecodeError as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"用户资料 JSON 解析失败: {str(e)}")
            self.logger.error(f"❌ 用户资料格式错误: {str(e)}")
        
        # 验证新闻文件
        if not os.path.exists(news_file_path):
            validation_result['valid'] = False
            validation_result['errors'].append(f"新闻文件不存在: {news_file_path}")
            self.logger.error(f"❌ 新闻文件不存在: {news_file_path}")
        else:
            try:
                with open(news_file_path, 'r', encoding='utf-8') as f:
                    news_data = json.load(f)
                validation_result['news_data'] = news_data
                self.logger.info("✅ 新闻文件解析成功")
            except json.JSONDecodeError as e:
                validation_result['valid'] = False
                validation_result['errors'].append(f"新闻文件 JSON 解析失败: {str(e)}")
                self.logger.error(f"❌ 新闻文件格式错误: {str(e)}")
            except Exception as e:
                validation_result['valid'] = False
                validation_result['errors'].append(f"读取新闻文件失败: {str(e)}")
                self.logger.error(f"❌ 读取新闻文件失败: {str(e)}")
        
        return validation_result
    
    def process_workflow(self, user_profile_str: str, news_file_path: str) -> str:
        """
        处理 Dify 工作流
        
        Args:
            user_profile_str: 用户资料的 JSON 字符串
            news_file_path: 新闻文件路径
            
        Returns:
            JSON 格式的分析结果字符串
        """
        # 验证输入
        validation = self.validate_inputs(user_profile_str, news_file_path)
        
        if not validation['valid']:
            error_response = {
                'status': 'error',
                'message': '输入验证失败',
                'errors': validation['errors']
            }
            self.logger.error(f"❌ 工作流处理失败: {validation['errors']}")
            return json.dumps(error_response, ensure_ascii=False)
        
        try:
            user_profile = validation['user_profile']
            news_data = validation['news_data']
            
            # 提取必需的新闻字段
            title = news_data.get('title', '')
            content = news_data.get('content', '')
            
            if not title or not content:
                error_response = {
                    'status': 'error',
                    'message': '新闻文件缺少必需字段 (title, content)',
                    'received_keys': list(news_data.keys())
                }
                self.logger.error("❌ 新闻数据缺少必需字段")
                return json.dumps(error_response, ensure_ascii=False)
            
            # 检查 Dify 是否启用
            if self.config.dify_enabled:
                # 传递文件路径给 Dify API
                return self._call_dify_api(user_profile, news_data, news_file_path)
            else:
                # 如果 Dify 未启用，返回准备好的数据
                return self._prepare_workflow_result(user_profile, title, content, news_file_path)
        
        except Exception as e:
            error_response = {
                'status': 'error',
                'message': f'工作流处理异常: {str(e)}'
            }
            self.logger.error(f"❌ 工作流处理异常: {str(e)}")
            return json.dumps(error_response, ensure_ascii=False)
    
    def _call_dify_api(self, user_profile: Dict[str, Any], news_data: Dict[str, Any], news_file_path: str) -> str:
        """
        调用 Dify API 进行工作流处理
        
        Args:
            user_profile: 用户资料字典
            news_data: 新闻数据字典（备用，如果文件不可用）
            news_file_path: 新闻文件路径（JSON 文件）
            
        Returns:
            JSON 格式的分析结果字符串
        """
        try:
            # 检查 Dify 是否配置
            if not self.dify_client.is_configured():
                error_response = {
                    'status': 'error',
                    'message': 'Dify API Key 未配置'
                }
                self.logger.error("❌ Dify API Key 未配置")
                return json.dumps(error_response, ensure_ascii=False)
            
            # 验证新闻文件是否存在
            if not os.path.exists(news_file_path):
                error_response = {
                    'status': 'error',
                    'message': f'新闻文件不存在: {news_file_path}'
                }
                self.logger.error(f"❌ {error_response['message']}")
                return json.dumps(error_response, ensure_ascii=False)
            
            # 步骤 1: 上传文件到 Dify 获取文件 ID
            self.logger.info(f"📤 正在上传文件到 Dify: {news_file_path}")
            upload_result = self.dify_client.upload_file(news_file_path)
            
            if not upload_result:
                error_response = {
                    'status': 'error',
                    'message': '文件上传到 Dify 失败'
                }
                self.logger.error("❌ 文件上传失败")
                return json.dumps(error_response, ensure_ascii=False)
            
            file_id, detected_type = upload_result
            
            # 步骤 2: 使用文件 ID 调用工作流
            self.logger.info(f"🔄 使用文件 ID 调用 Dify 工作流")
            
            user_profile_json = json.dumps(user_profile, ensure_ascii=False)
            dify_response = self.dify_client.call_workflow(user_profile_json, file_id, detected_type)
            
            # 解析 Dify 响应
            response_data = json.loads(dify_response)
            
            if response_data.get('status') == 'success':
                # 提取并验证输出
                analysis_result = self.dify_client.extract_outputs(dify_response)
                validation_result = self.dify_client.validate_response(analysis_result)
                
                return json.dumps({
                    'status': 'success',
                    'data': analysis_result,
                    'dify_response_id': response_data.get('dify_response_id', ''),
                    'validation_warnings': validation_result.get('warnings', [])
                }, ensure_ascii=False)
            else:
                # Dify API 错误
                return dify_response
        
        except Exception as e:
            error_response = {
                'status': 'error',
                'message': f'Dify API 调用异常: {str(e)}'
            }
            self.logger.error(f"❌ Dify API 调用异常: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return json.dumps(error_response, ensure_ascii=False)
    
    def _prepare_workflow_result(self, user_profile: Dict[str, Any], 
                                 title: str, content: str, 
                                 news_file_path: str) -> str:
        """
        准备工作流结果（Dify 未启用时）
        
        Args:
            user_profile: 用户资料
            title: 新闻标题
            content: 新闻内容
            news_file_path: 文件路径
            
        Returns:
            JSON 格式的结果字符串
        """
        result = {
            'status': 'pending_analysis',
            'message': '等待 Dify 工作流处理',
            'input_metadata': {
                'user_profile_provided': bool(user_profile),
                'news_title': title[:100],
                'news_content_length': len(content),
                'news_file_path': news_file_path,
                'processed_at': self._get_iso_timestamp()
            },
            'workflow_inputs': {
                'user_profile': user_profile,
                'news': {
                    'title': title,
                    'content': content,
                    'file_path': news_file_path
                }
            },
            'expected_output_schema': {
                'title': 'string (文章的标题)',
                'summary': 'string (文章内容的简明总结)',
                'relevance_score': 'number (0-10，10表示最相关)',
                'relevance_reason': 'string (评分原因说明)'
            }
        }
        return json.dumps(result, ensure_ascii=False)
    
    def _prepare_analysis_data(self, user_profile: Dict[str, Any], 
                              title: str, content: str, 
                              news_file_path: str) -> Dict[str, Any]:
        """
        准备分析数据供 Dify 工作流使用
        
        Args:
            user_profile: 用户资料字典
            title: 新闻标题
            content: 新闻内容
            news_file_path: 新闻文件路径
            
        Returns:
            准备好的分析数据
        """
        return {
            'status': 'pending_analysis',
            'message': '等待 Dify 工作流处理',
            'input_metadata': {
                'user_profile_provided': bool(user_profile),
                'news_title': title[:100],
                'news_content_length': len(content),
                'news_file_path': news_file_path,
                'processed_at': self._get_iso_timestamp()
            },
            'workflow_inputs': {
                'user_profile': user_profile,
                'news': {
                    'title': title,
                    'content': content,
                    'file_path': news_file_path
                }
            },
            'expected_output_schema': {
                'title': 'string (文章的标题)',
                'summary': 'string (文章内容的简明总结)',
                'relevance_score': 'number (0-10，10表示最相关)',
                'relevance_reason': 'string (评分原因说明)'
            }
        }
    
    def parse_workflow_output(self, workflow_output_str: str) -> Dict[str, Any]:
        """
        解析 Dify 工作流的输出
        
        Args:
            workflow_output_str: 工作流返回的 JSON 字符串
            
        Returns:
            解析后的输出字典
        """
        try:
            output_data = json.loads(workflow_output_str)
            
            # 验证输出包含必需字段
            required_fields = ['title', 'summary', 'relevance_score', 'relevance_reason']
            missing_fields = [f for f in required_fields if f not in output_data]
            
            if missing_fields:
                self.logger.warning(f"⚠️ 工作流输出缺少字段: {missing_fields}")
            
            # 验证 relevance_score 的有效性
            if 'relevance_score' in output_data:
                try:
                    score = float(output_data['relevance_score'])
                    if not (0 <= score <= 10):
                        self.logger.warning(f"⚠️ 相关性评分超出范围: {score}")
                except (ValueError, TypeError):
                    self.logger.warning(f"⚠️ 相关性评分格式错误: {output_data['relevance_score']}")
            
            return {
                'status': 'success',
                'data': output_data,
                'validation_warnings': missing_fields
            }
        
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ 工作流输出 JSON 解析失败: {str(e)}")
            return {
                'status': 'error',
                'message': f'输出 JSON 解析失败: {str(e)}',
                'raw_output': workflow_output_str
            }
    
    def _get_iso_timestamp(self) -> str:
        """获取 ISO 格式的时间戳"""
        return datetime.now().isoformat()
