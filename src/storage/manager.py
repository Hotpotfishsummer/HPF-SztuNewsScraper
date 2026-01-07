#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
存储管理层
提供统一的文章和索引存储接口
"""

import json
import os
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..core.logger import get_logger

logger = get_logger(__name__)


class StorageBackend(ABC):
    """存储后端抽象基类"""
    
    @abstractmethod
    def save_article(self, filename: str, data: Dict) -> bool:
        """保存文章"""
        pass
    
    @abstractmethod
    def load_article(self, filename: str) -> Optional[Dict]:
        """加载文章"""
        pass
    
    @abstractmethod
    def article_exists(self, filename: str) -> bool:
        """检查文章是否存在"""
        pass
    
    @abstractmethod
    def list_articles(self) -> List[str]:
        """列出所有文章文件名"""
        pass
    
    @abstractmethod
    def delete_article(self, filename: str) -> bool:
        """删除文章"""
        pass


class FileStorageBackend(StorageBackend):
    """基于本地文件系统的存储后端"""
    
    def __init__(self, base_dir: str = "articles"):
        """初始化文件存储后端
        
        Args:
            base_dir: 存储目录
        """
        self.base_dir = base_dir
        Path(self.base_dir).mkdir(exist_ok=True)
    
    def save_article(self, filename: str, data: Dict) -> bool:
        """保存文章到 JSON 文件"""
        try:
            filepath = os.path.join(self.base_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存文章失败: {filename}, 错误: {e}")
            return False
    
    def load_article(self, filename: str) -> Optional[Dict]:
        """从 JSON 文件加载文章"""
        try:
            filepath = os.path.join(self.base_dir, filename)
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载文章失败: {filename}, 错误: {e}")
            return None
    
    def article_exists(self, filename: str) -> bool:
        """检查文章是否存在"""
        filepath = os.path.join(self.base_dir, filename)
        return os.path.exists(filepath)
    
    def list_articles(self) -> List[str]:
        """列出所有文章文件名"""
        try:
            if not os.path.exists(self.base_dir):
                return []
            return [f for f in os.listdir(self.base_dir) if f.endswith('.json') and f != 'index.json']
        except Exception as e:
            logger.error(f"列出文章失败: {e}")
            return []
    
    def delete_article(self, filename: str) -> bool:
        """删除文章（移到 .trash）"""
        try:
            filepath = os.path.join(self.base_dir, filename)
            if not os.path.exists(filepath):
                return False
            
            # 创建 .trash 目录
            trash_dir = os.path.join(os.path.dirname(self.base_dir), '.trash')
            Path(trash_dir).mkdir(exist_ok=True)
            
            # 移动到 .trash
            trash_path = os.path.join(trash_dir, filename)
            import shutil
            shutil.move(filepath, trash_path)
            
            logger.info(f"已软删除: {filename} → {trash_path}")
            return True
        except Exception as e:
            logger.error(f"删除文章失败: {filename}, 错误: {e}")
            return False


class IndexStorage:
    """文章索引存储"""
    
    def __init__(self, index_file: str = "articles/index.json"):
        """初始化索引存储
        
        Args:
            index_file: 索引文件路径
        """
        self.index_file = index_file
        self._ensure_index_dir()
    
    def _ensure_index_dir(self):
        """确保索引目录存在"""
        index_dir = os.path.dirname(self.index_file)
        if index_dir:
            Path(index_dir).mkdir(parents=True, exist_ok=True)
    
    def load(self) -> Dict[str, Any]:
        """加载索引"""
        if not os.path.exists(self.index_file):
            return {}
        
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"加载索引失败: {e}")
            return {}
    
    def save(self, index: Dict[str, Any]) -> bool:
        """保存索引"""
        try:
            self._ensure_index_dir()
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存索引失败: {e}")
            return False
    
    def add_entry(self, url: str, article_info: Dict) -> bool:
        """添加索引项"""
        index = self.load()
        index[url] = article_info
        return self.save(index)
    
    def remove_entry(self, url: str) -> bool:
        """移除索引项"""
        index = self.load()
        if url in index:
            del index[url]
            return self.save(index)
        return False
    
    def get_entry(self, url: str) -> Optional[Dict]:
        """获取索引项"""
        index = self.load()
        return index.get(url)
    
    def entry_exists(self, url: str) -> bool:
        """检查索引项是否存在"""
        index = self.load()
        return url in index


class StorageManager:
    """统一的存储管理器"""
    
    def __init__(self, articles_dir: str = "articles", index_file: str = "articles/index.json"):
        """初始化存储管理器
        
        Args:
            articles_dir: 文章存储目录
            index_file: 索引文件路径
        """
        self.backend = FileStorageBackend(articles_dir)
        self.index = IndexStorage(index_file)
    
    def save_article(self, filename: str, data: Dict, url: Optional[str] = None) -> bool:
        """保存文章并更新索引"""
        # 保存文件
        if not self.backend.save_article(filename, data):
            return False
        
        # 更新索引
        if url:
            article_info = {
                'filename': filename,
                'title': data.get('title', ''),
                'category': data.get('category', ''),
                'department': data.get('department', ''),
                'publish_time': data.get('publish_time', ''),
                'fetch_time': datetime.now().isoformat(),
                'url': url,
                'has_attachment': data.get('has_attachment', False)
            }
            self.index.add_entry(url, article_info)
        
        return True
    
    def load_article(self, filename: str) -> Optional[Dict]:
        """加载文章"""
        return self.backend.load_article(filename)
    
    def article_exists(self, filename: str) -> bool:
        """检查文章是否存在"""
        return self.backend.article_exists(filename)
    
    def get_all_articles(self) -> List[Dict]:
        """获取所有文章的索引信息"""
        index = self.index.load()
        return list(index.values())
    
    def delete_article(self, filename: str, url: Optional[str] = None) -> bool:
        """删除文章"""
        if not self.backend.delete_article(filename):
            return False
        
        if url:
            self.index.remove_entry(url)
        
        return True


# 全局存储管理器实例
_storage_manager: Optional[StorageManager] = None


def get_storage_manager() -> StorageManager:
    """获取全局存储管理器实例"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageManager()
    return _storage_manager
