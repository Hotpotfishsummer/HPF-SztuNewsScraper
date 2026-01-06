#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dify API 客户端 - 封装通用的 API 操作
提供文件上传、工作流调用等基础功能
"""

import json
import os
import time
import requests
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import get_config
from logger_config import get_logger

logger = get_logger(__name__)


class DifyClient:
    """Dify API 客户端 - 处理所有 Dify API 交互"""
    
    def __init__(self):
        """初始化 Dify 客户端"""
        self.config = get_config()
        self.logger = logger
        self.api_endpoint = self.config.dify_api_endpoint
        self.api_key = self.config.dify_api_key
        self.timeout = self.config.dify_timeout
        self.retry_times = self.config.dify_retry_times
        self.retry_delay = self.config.dify_retry_delay
    
    def is_configured(self) -> bool:
        """检查 Dify 是否配置完整"""
        return self.config.dify_enabled and bool(self.api_key)
    
    def upload_file(self, file_path: str) -> Optional[Tuple[str, str]]:
        """
        上传文件到 Dify，获取文件 ID
        
        Args:
            file_path: 本地文件路径
            
        Returns:
            (文件 ID, 检测文件类型) 元组，如果上传失败返回 None
        """
        if not self.api_key:
            self.logger.error("❌ Dify API Key 未配置")
            return None
        
        try:
            # 文件上传端点
            url = f"{self.api_endpoint}/files/upload"
            
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            # 确定文件的 MIME 类型
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension == '.json':
                mime_type = 'application/json'
            else:
                mime_type = 'application/octet-stream'
            
            # 打开文件并上传
            with open(file_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(file_path), f, mime_type)
                }
                
                self.logger.info(f"📤 上传文件: {os.path.basename(file_path)} (MIME: {mime_type})")
                
                response = requests.post(
                    url,
                    files=files,
                    headers=headers,
                    timeout=self.timeout
                )
            
            if response.status_code in (200, 201):
                result = response.json()
                file_id = result.get('id') or result.get('file_id')
                
                self.logger.info(f"📋 上传响应: {json.dumps(result, ensure_ascii=False)}")
                
                if file_id:
                    # 尝试从响应中获取文件类型信息
                    detected_mime = result.get('mime_type') or result.get('type') or 'application/json'
                    
                    # 将 MIME 类型转换为 Dify 期望的类型
                    if 'json' in detected_mime.lower():
                        detected_type = 'custom'
                    elif 'text' in detected_mime.lower():
                        detected_type = 'document'
                    else:
                        detected_type = 'document'
                    
                    self.logger.info(f"✅ 文件上传成功，ID: {file_id}, MIME: {detected_mime}, 映射类型: {detected_type}")
                    return (file_id, detected_type)
                else:
                    self.logger.error(f"❌ 上传响应中无文件 ID: {result}")
                    return None
            else:
                self.logger.error(f"❌ 文件上传失败: HTTP {response.status_code}: {response.text}")
                return None
        
        except Exception as e:
            self.logger.error(f"❌ 文件上传异常: {str(e)}")
            return None
    
    def call_workflow(self, user_input: str, file_id: str, file_type: str) -> str:
        """
        调用 Dify 工作流
        
        Args:
            user_input: 用户输入（用户资料 JSON 字符串）
            file_id: 上传的文件 ID
            file_type: 文件类型
            
        Returns:
            JSON 格式的工作流结果字符串
        """
        if not self.api_key:
            error_response = {
                'status': 'error',
                'message': 'Dify API Key 未配置'
            }
            self.logger.error("❌ Dify API Key 未配置")
            return json.dumps(error_response, ensure_ascii=False)
        
        try:
            url = f"{self.api_endpoint}/workflows/run"
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # 重试逻辑
            last_error = None
            file_type_variants = ['custom', 'json', 'document']
            variant_index = 0
            
            self.logger.info(f"🔄 正在调用 Dify 工作流: {url}")
            self.logger.info(f"📋 文件类型尝试顺序: {file_type_variants}")
            
            for attempt in range(1, self.retry_times + 1):
                try:
                    current_type = file_type_variants[variant_index % len(file_type_variants)]
                    
                    request_data = {
                        'user': 'student_analyzer',
                        'inputs': {
                            'userinput_prompt': user_input,
                            'userinput_doc': {
                                'transfer_method': 'local_file',
                                'upload_file_id': file_id,
                                'type': current_type
                            }
                        },
                        'response_mode': 'blocking'
                    }
                    
                    self.logger.info(f"📤 尝试使用文件类型: {current_type}")
                    
                    response = requests.post(
                        url,
                        json=request_data,
                        headers=headers,
                        timeout=self.timeout
                    )
                    
                    # 如果 400 错误且是文件类型问题，尝试其他类型
                    if response.status_code == 400 and 'type' in response.text.lower():
                        variant_index += 1
                        next_type = file_type_variants[variant_index % len(file_type_variants)]
                        self.logger.info(f"⚠️ 文件类型 '{current_type}' 不匹配，尝试 '{next_type}'...")
                        continue
                    
                    if response.status_code == 200:
                        result = response.json()
                        self.logger.info(f"📋 Dify 工作流返回内容: {json.dumps(result, ensure_ascii=False)}")
                        
                        if 'data' in result and 'outputs' in result['data']:
                            self.logger.info("✅ Dify API 调用成功")
                            
                            return json.dumps({
                                'status': 'success',
                                'data': result['data']['outputs'],
                                'dify_response_id': result['data'].get('workflow_run_id', '')
                            }, ensure_ascii=False)
                        else:
                            self.logger.warning(f"⚠️ Dify 返回结构不符: {result}")
                    
                    elif response.status_code == 401:
                        error_response = {
                            'status': 'error',
                            'message': 'Dify API Key 无效或已过期'
                        }
                        self.logger.error("❌ Dify 认证失败")
                        return json.dumps(error_response, ensure_ascii=False)
                    
                    elif response.status_code == 404:
                        error_response = {
                            'status': 'error',
                            'message': '该 Dify API Key 对应的工作流不存在或不可访问'
                        }
                        self.logger.error("❌ Dify 工作流不存在")
                        return json.dumps(error_response, ensure_ascii=False)
                    
                    else:
                        last_error = f"HTTP {response.status_code}: {response.text}"
                        self.logger.warning(f"⚠️ Dify API 返回错误 [{attempt}/{self.retry_times}]: {last_error}")
                
                except requests.Timeout:
                    last_error = "请求超时"
                    self.logger.warning(f"⚠️ Dify API 请求超时 [{attempt}/{self.retry_times}]")
                
                except requests.RequestException as e:
                    last_error = str(e)
                    self.logger.warning(f"⚠️ Dify API 请求异常 [{attempt}/{self.retry_times}]: {str(e)}")
                
                # 如果不是最后一次尝试，等待后重试
                if attempt < self.retry_times:
                    self.logger.info(f"⏳ {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
            
            # 所有重试都失败
            error_response = {
                'status': 'error',
                'message': f'Dify API 调用失败: {last_error}',
                'retry_times': self.retry_times
            }
            self.logger.error(f"❌ Dify API 调用失败（重试 {self.retry_times} 次后）: {last_error}")
            return json.dumps(error_response, ensure_ascii=False)
        
        except Exception as e:
            error_response = {
                'status': 'error',
                'message': f'Dify API 调用异常: {str(e)}'
            }
            self.logger.error(f"❌ Dify API 调用异常: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return json.dumps(error_response, ensure_ascii=False)
    
    def extract_outputs(self, dify_response: str) -> Dict[str, Any]:
        """
        从 Dify 工作流返回的响应中提取输出
        
        Args:
            dify_response: Dify 返回的 JSON 字符串
            
        Returns:
            提取的输出字典
        """
        try:
            response_data = json.loads(dify_response)
            
            if response_data.get('status') == 'success':
                outputs = response_data.get('data', {})
                
                # 处理 Dify 返回的文本格式输出
                if isinstance(outputs, dict) and 'text' in outputs:
                    text_content = outputs['text']
                    try:
                        outputs = json.loads(text_content)
                        self.logger.info(f"✅ 从 outputs.text 解析 JSON 成功")
                    except json.JSONDecodeError:
                        self.logger.warning(f"⚠️ 无法解析 outputs.text 中的 JSON")
                        return self._format_output(text_content)
                
                return self._format_output(outputs)
            else:
                self.logger.error(f"❌ Dify 返回错误状态: {response_data.get('message')}")
                return {
                    'status': 'error',
                    'message': response_data.get('message', '未知错误')
                }
        
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ 响应 JSON 解析失败: {str(e)}")
            return {
                'status': 'error',
                'message': f'响应解析失败: {str(e)}'
            }
    
    def _format_output(self, outputs: Any) -> Dict[str, Any]:
        """
        格式化 Dify 输出为标准结构
        
        Args:
            outputs: Dify 输出（可能是字典或字符串）
            
        Returns:
            格式化后的输出
        """
        # 如果是字符串，尝试解析为 JSON
        if isinstance(outputs, str):
            try:
                outputs = json.loads(outputs)
            except json.JSONDecodeError:
                # 无法解析则作为摘要返回
                return {
                    'title': '分析结果',
                    'summary': outputs[:500],
                    'relevance_score': 0,
                    'relevance_reason': '来自 Dify 工作流的原始输出'
                }
        
        # 如果是字典，提取需要的字段
        if isinstance(outputs, dict):
            result = {
                'title': outputs.get('title', ''),
                'summary': outputs.get('summary', ''),
                'relevance_score': outputs.get('relevance_score', 0),
                'relevance_reason': outputs.get('relevance_reason', '')
            }
            self.logger.info(f"✅ 成功提取分析结果: 相关性评分 {result['relevance_score']}")
            return result
        
        # 其他情况
        return {
            'title': '分析结果',
            'summary': str(outputs)[:500],
            'relevance_score': 0,
            'relevance_reason': 'Dify 工作流返回了非标准格式的结果'
        }
    
    def validate_response(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证工作流输出的有效性
        
        Args:
            output_data: 输出数据
            
        Returns:
            包含验证结果的字典
        """
        result = {
            'status': 'valid',
            'warnings': [],
            'data': output_data
        }
        
        # 检查必需字段
        required_fields = ['title', 'summary', 'relevance_score', 'relevance_reason']
        missing_fields = [f for f in required_fields if f not in output_data]
        
        if missing_fields:
            result['warnings'].append(f"缺少字段: {missing_fields}")
            self.logger.warning(f"⚠️ 输出缺少字段: {missing_fields}")
        
        # 验证相关性评分
        if 'relevance_score' in output_data:
            try:
                score = float(output_data['relevance_score'])
                if not (0 <= score <= 10):
                    result['warnings'].append(f"相关性评分超出范围: {score}")
                    self.logger.warning(f"⚠️ 相关性评分超出范围: {score}")
            except (ValueError, TypeError):
                result['warnings'].append(f"相关性评分格式错误: {output_data['relevance_score']}")
                self.logger.warning(f"⚠️ 相关性评分格式错误")
        
        return result
