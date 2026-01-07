#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
存储管理层
提供统一的文章和数据存储接口
"""

from .manager import (
    StorageBackend,
    FileStorageBackend,
    IndexStorage,
    StorageManager,
    get_storage_manager
)

__all__ = [
    'StorageBackend',
    'FileStorageBackend',
    'IndexStorage',
    'StorageManager',
    'get_storage_manager'
]
