#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 分析结果存储和记录管理
记录所有通过 Dify 工作流处理的新闻分析结果
集成了结构化索引、配置监控、缓存管理等功能
"""

import json
import os
import hashlib
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys

# 添加 src 目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from logger_config import get_logger

logger = get_logger(__name__)


class AnalysisRecorder:
    """记录和管理分析结果"""
    
    def __init__(self):
        """初始化记录管理器"""
        self.ai_dir = Path(__file__).parent
        # 修改日志目录到 articles 下
        self.logs_dir = Path(__file__).parent.parent.parent / 'articles' / 'analysis_records'
        self.cache_dir = self.ai_dir / 'cache'
        
        # 获取根目录的 config.json 路径
        self.config_path = Path(__file__).parent.parent.parent / 'config.json'
        
        # 创建必要目录
        self.logs_dir.mkdir(exist_ok=True, parents=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # 分析记录索引文件
        self.index_file = self.logs_dir / 'analysis_index.json'
        self._initialize_index()
        
        logger.info(f"✅ 分析记录管理器初始化完成")
        logger.info(f"   日志目录: {self.logs_dir}")
        logger.info(f"   缓存目录: {self.cache_dir}")
        logger.info(f"   配置文件: {self.config_path}")
    
    def _initialize_index(self) -> None:
        """初始化分析索引文件"""
        if not self.index_file.exists():
            index_data = {
                'version': '1.0.0',
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'total_analyses': 0,
                'config_md5': self._calculate_config_md5(),
                'analyses': {}  # 改为字典，key为源文件名，值为分析记录
            }
            self._save_json(self.index_file, index_data)
            logger.info(f"✅ 创建分析索引文件: {self.index_file}")
    
    def _calculate_config_md5(self) -> str:
        """
        计算 config.json 的 MD5 校验和
        用于检测配置变化，识别需要重新分析的结果
        
        Returns:
            MD5 哈希值字符串，如果文件不存在返回空字符串
        """
        if not self.config_path.exists():
            logger.warning(f"⚠️ config.json 文件不存在: {self.config_path}")
            return ""
        
        try:
            with open(self.config_path, 'rb') as f:
                md5_hash = hashlib.md5()
                for chunk in iter(lambda: f.read(4096), b''):
                    md5_hash.update(chunk)
                return md5_hash.hexdigest()
        except Exception as e:
            logger.error(f"❌ 计算 config.json MD5 失败: {str(e)}")
            return ""
    
    def _is_config_changed(self, stored_md5: str) -> bool:
        """
        检查配置是否已变化
        
        Args:
            stored_md5: 存储的 MD5 值
            
        Returns:
            True 如果配置已变化，False 表示未变化
        """
        current_md5 = self._calculate_config_md5()
        changed = stored_md5 != current_md5
        
        if changed and stored_md5:
            logger.warning(
                f"⚠️ 检测到配置变化:\n"
                f"  旧 MD5: {stored_md5[:8]}...\n"
                f"  新 MD5: {current_md5[:8]}..."
            )
        
        return changed
    
    def record_analysis(self, 
                       user_profile: Dict[str, Any],
                       news_data: Dict[str, Any],
                       analysis_result: Dict[str, Any],
                       news_file_path: str = None) -> str:
        """
        记录一次分析结果
        按源文件名称保存分析记录，避免重复分析相同文件
        
        Args:
            user_profile: 用户资料
            news_data: 新闻数据
            analysis_result: 分析结果
            news_file_path: 原始新闻文件路径
            
        Returns:
            记录文件的路径
        """
        try:
            # 从源文件路径生成记录文件名（与源文件名称相同）
            if news_file_path:
                # 提取文件名（不含路径）
                source_filename = os.path.basename(news_file_path)
                # 如果不是 .json 扩展名，则添加
                if not source_filename.endswith('.json'):
                    filename = os.path.splitext(source_filename)[0] + '.json'
                else:
                    filename = source_filename
            else:
                # 如果没有源文件路径，使用标题生成文件名
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                news_title = news_data.get('title', 'untitled')
                safe_title = ''.join(c if c.isalnum() or c in '-_' else '_' 
                                    for c in news_title[:30])
                filename = f"{timestamp}_{safe_title}.json"
            
            record_path = self.logs_dir / filename
            
            # 计算当前配置的 MD5
            config_md5 = self._calculate_config_md5()
            
            # 构建完整记录（包含配置校验信息）
            record = {
                'timestamp': datetime.now().isoformat(),
                'status': 'recorded',
                'config_md5': config_md5,  # 记录配置的 MD5 哈希值
                'user_profile': user_profile,
                'news_input': {
                    'title': news_data.get('title'),
                    'content_length': len(news_data.get('content', '')),
                    'source': news_data.get('source'),
                    'publish_date': news_data.get('publish_date'),
                    'file_path': news_file_path
                },
                'analysis_output': analysis_result
            }
            
            # 保存记录
            self._save_json(record_path, record)
            
            # 更新索引
            self._update_index(record, filename)
            
            logger.info(f"✅ 分析结果已记录: {record_path}")
            return str(record_path)
        
        except Exception as e:
            logger.error(f"❌ 记录分析结果失败: {str(e)}")
            raise
    
    def _update_index(self, record: Dict[str, Any], filename: str) -> None:
        """更新分析索引"""
        try:
            index = self._load_json(self.index_file)
            
            # 使用文件名作为 key，存储分析记录信息
            index['analyses'][filename] = {
                'filename': filename,
                'timestamp': record['timestamp'],
                'news_title': record['news_input'].get('title', 'untitled'),
                'relevance_score': record['analysis_output'].get('relevance_score'),
                'config_md5': record['config_md5']  # 记录配置 MD5 用于检测过期
            }
            
            index['total_analyses'] = len(index['analyses'])
            index['last_updated'] = datetime.now().isoformat()
            
            self._save_json(self.index_file, index)
            logger.info(f"✅ 分析索引已更新: 总数 {index['total_analyses']}")
        
        except Exception as e:
            logger.warning(f"⚠️ 更新索引失败: {str(e)}")
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取分析历史记录
        
        Args:
            limit: 返回的最大记录数
            
        Returns:
            分析历史列表
        """
        try:
            index = self._load_json(self.index_file)
            
            # 将字典转换为列表，按时间戳排序
            analyses = index.get('analyses', {})
            if isinstance(analyses, dict):
                # 转换字典为列表
                analyses_list = list(analyses.values())
            else:
                # 如果是列表（向后兼容），直接使用
                analyses_list = analyses
            
            # 按时间戳排序，返回最新的 limit 条记录
            sorted_analyses = sorted(analyses_list, key=lambda x: x.get('timestamp', ''), reverse=True)
            return sorted_analyses[:limit]
        
        except Exception as e:
            logger.error(f"❌ 获取分析历史失败: {str(e)}")
            return []
    
    def has_analysis(self, filename: str) -> bool:
        """
        检查文件是否已完整分析过
        必须同时满足：索引中有记录 AND 对应的物理文件存在
        如果任一缺失，则认为需要重新分析
        
        Args:
            filename: 源文件名
            
        Returns:
            True 表示已完整分析（索引+文件都存在），False 表示需要分析
        """
        try:
            # 确保文件名格式一致
            if not filename.endswith('.json'):
                filename = os.path.splitext(filename)[0] + '.json'
            
            # 1. 检查索引中是否有记录
            index = self._load_json(self.index_file)
            analyses = index.get('analyses', {})
            
            has_index = False
            if isinstance(analyses, dict):
                has_index = filename in analyses
            else:
                has_index = any(a.get('filename') == filename for a in analyses)
            
            logger.debug(f"📋 索引检查: {filename} - {'✅ 有记录' if has_index else '❌ 无记录'}")
            
            # 2. 检查物理文件是否存在
            record_file_path = self.logs_dir / filename
            file_exists = record_file_path.exists()
            
            logger.debug(f"📁 文件检查: {filename} - {'✅ 文件存在' if file_exists else '❌ 文件不存在'}")
            logger.debug(f"   路径: {record_file_path}")
            
            # 3. 只有索引和文件都存在时才认为已分析
            both_exist = has_index and file_exists
            
            if has_index and not file_exists:
                logger.warning(f"⚠️ 索引记录存在但文件缺失: {filename}")
                logger.info(f"🔄 需要重新分析（文件已删除）")
            elif file_exists and not has_index:
                logger.warning(f"⚠️ 物理文件存在但索引记录缺失: {filename}")
                logger.info(f"🔄 需要重新分析（索引不同步）")
            elif both_exist:
                logger.info(f"✅ 文件完整分析过: {filename}")
            else:
                logger.debug(f"❌ 文件未分析: {filename}")
            
            return both_exist
        
        except Exception as e:
            logger.error(f"❌ 检查分析状态失败: {str(e)}")
            return False
    
    def get_analysis_record(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        获取文件的分析记录
        
        Args:
            filename: 源文件名
            
        Returns:
            分析记录字典，不存在返回 None
        """
        try:
            # 先检查索引
            index = self._load_json(self.index_file)
            analyses = index.get('analyses', {})
            
            if isinstance(analyses, dict):
                if filename in analyses:
                    # 返回索引中的记录信息
                    return analyses[filename]
            else:
                # 列表结构支持（向后兼容）
                for a in analyses:
                    if a.get('filename') == filename:
                        return a
            
            logger.warning(f"⚠️ 未在索引中找到: {filename}")
            return None
        
        except Exception as e:
            logger.error(f"❌ 获取分析记录失败: {str(e)}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取分析统计信息
        
        Returns:
            统计信息字典
        """
        try:
            index = self._load_json(self.index_file)
            analyses = index.get('analyses', {})
            
            # 转换为列表（如果是字典）
            if isinstance(analyses, dict):
                analyses_list = list(analyses.values())
            else:
                analyses_list = analyses
            
            # 计算统计信息
            stats = {
                'total_analyses': index.get('total_analyses', 0),
                'average_relevance_score': 0,
                'score_distribution': {
                    'high': 0,      # 8-10
                    'medium': 0,    # 5-7
                    'low': 0        # 0-4
                }
            }
            
            scores = []
            for analysis in analyses_list:
                score = analysis.get('relevance_score')
                if score is not None:
                    scores.append(score)
                    
                    if score >= 8:
                        stats['score_distribution']['high'] += 1
                    elif score >= 5:
                        stats['score_distribution']['medium'] += 1
                    else:
                        stats['score_distribution']['low'] += 1
            
            if scores:
                stats['average_relevance_score'] = sum(scores) / len(scores)
            
            return stats
        
        except Exception as e:
            logger.error(f"❌ 获取统计信息失败: {str(e)}")
            return {}
    
    def load_analysis(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        加载已保存的分析记录
        检测配置是否已变化，避免使用过期的分析结果
        
        Args:
            filename: 记录文件名
            
        Returns:
            分析记录字典，不存在或配置已变化返回 None
        """
        try:
            record_path = self.logs_dir / filename
            
            if not record_path.exists():
                logger.warning(f"⚠️ 分析记录不存在: {filename}")
                return None
            
            record = self._load_json(record_path)
            
            # 检查配置是否已变化
            stored_md5 = record.get('config_md5', '')
            if self._is_config_changed(stored_md5):
                logger.warning(
                    f"⚠️ 分析记录可能已过期（配置已变）: {filename}\n"
                    f"   建议重新分析"
                )
                return None
            
            logger.info(f"✅ 已加载分析记录: {filename}")
            return record
        
        except Exception as e:
            logger.error(f"❌ 加载分析记录失败: {str(e)}")
            return None
    
    def check_analysis_validity(self, filename: str) -> Dict[str, Any]:
        """
        检查分析结果的有效性
        验证文件存在性和配置一致性
        
        Args:
            filename: 记录文件名
            
        Returns:
            包含有效性检查结果的字典
        """
        result = {
            'filename': filename,
            'exists': False,
            'config_valid': False,
            'needs_reanalysis': False,
            'details': ''
        }
        
        try:
            record_path = self.logs_dir / filename
            
            # 检查文件存在性
            if not record_path.exists():
                result['details'] = '分析记录文件不存在'
                result['needs_reanalysis'] = True
                return result
            
            result['exists'] = True
            
            # 检查配置一致性
            record = self._load_json(record_path)
            stored_md5 = record.get('config_md5', '')
            
            if not self._is_config_changed(stored_md5):
                result['config_valid'] = True
                result['details'] = '分析结果有效'
            else:
                result['config_valid'] = False
                result['needs_reanalysis'] = True
                result['details'] = f'配置已变化 (旧MD5: {stored_md5[:8]}...)'
            
            return result
        
        except Exception as e:
            result['details'] = f'检查异常: {str(e)}'
            result['needs_reanalysis'] = True
            logger.error(f"❌ 检查分析有效性失败: {str(e)}")
            return result
    
    def cache_analysis(self, cache_key: str, data: Dict[str, Any]) -> None:
        """
        缓存分析结果以避免重复处理
        
        Args:
            cache_key: 缓存键（通常为新闻标题的哈希值）
            data: 要缓存的数据
        """
        try:
            cache_path = self.cache_dir / f"{cache_key}.json"
            
            cache_entry = {
                'cache_key': cache_key,
                'cached_at': datetime.now().isoformat(),
                'config_md5': self._calculate_config_md5(),
                'data': data
            }
            
            self._save_json(cache_path, cache_entry)
            logger.info(f"✅ 分析结果已缓存: {cache_key}")
        
        except Exception as e:
            logger.warning(f"⚠️ 缓存分析结果失败: {str(e)}")
    
    def get_cached_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存的分析结果
        验证配置一致性，确保缓存结果仍然有效
        
        Args:
            cache_key: 缓存键
            
        Returns:
            缓存的数据，不存在或配置已变化返回 None
        """
        try:
            cache_path = self.cache_dir / f"{cache_key}.json"
            
            if not cache_path.exists():
                return None
            
            cache_entry = self._load_json(cache_path)
            
            # 检查配置一致性
            stored_md5 = cache_entry.get('config_md5', '')
            if self._is_config_changed(stored_md5):
                logger.warning(f"⚠️ 缓存已过期（配置已变）: {cache_key}")
                return None
            
            return cache_entry.get('data')
        
        except Exception as e:
            logger.warning(f"⚠️ 获取缓存失败: {str(e)}")
            return None
    
    def find_outdated_analyses(self) -> List[Dict[str, Any]]:
        """
        查找所有配置已变化的分析结果（需要重新分析）
        
        Returns:
            需要重新分析的分析记录列表
        """
        try:
            index = self._load_json(self.index_file)
            current_md5 = self._calculate_config_md5()
            analyses = index.get('analyses', {})
            
            # 转换为列表（如果是字典）
            if isinstance(analyses, dict):
                analyses_list = list(analyses.values())
            else:
                analyses_list = analyses
            
            outdated = []
            
            for analysis in analyses_list:
                filename = analysis.get('filename')
                stored_md5 = analysis.get('config_md5', '')
                
                if stored_md5 and stored_md5 != current_md5:
                    outdated.append({
                        'filename': filename,
                        'needs_reanalysis': True,
                        'reason': f'配置已变化 (旧MD5: {stored_md5[:8]}...)'
                    })
            
            if outdated:
                logger.warning(f"⚠️ 发现 {len(outdated)} 个需要重新分析的记录")
            
            return outdated
        
        except Exception as e:
            logger.error(f"❌ 查找过期记录失败: {str(e)}")
            return []
    
    def export_to_csv(self, output_path: str = None) -> str:
        """
        将分析结果导出为 CSV 格式
        
        Args:
            output_path: 输出文件路径（可选）
            
        Returns:
            输出文件的路径
        """
        try:
            if not output_path:
                output_path = str(self.logs_dir / f"analysis_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            
            import csv
            
            index = self._load_json(self.index_file)
            analyses = index.get('analyses', {})
            
            # 转换为列表（如果是字典）
            if isinstance(analyses, dict):
                analyses_list = list(analyses.values())
            else:
                analyses_list = analyses
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['timestamp', 'news_title', 'relevance_score', 'filename'])
                writer.writeheader()
                
                for analysis in analyses_list:
                    writer.writerow({
                        'timestamp': analysis.get('timestamp'),
                        'news_title': analysis.get('news_title'),
                        'relevance_score': analysis.get('relevance_score'),
                        'filename': analysis.get('filename')
                    })
            
            logger.info(f"✅ 分析结果已导出: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"❌ 导出分析结果失败: {str(e)}")
            raise
    
    def _save_json(self, filepath: Path, data: Dict[str, Any]) -> None:
        """保存 JSON 文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_json(self, filepath: Path) -> Dict[str, Any]:
        """加载 JSON 文件"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
