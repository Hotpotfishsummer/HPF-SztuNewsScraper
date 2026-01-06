#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 分析模块初始化
提供与 Dify 工作流的集成接口
"""

from .dify_workflow import DifyWorkflowHandler
from .dify_client import DifyClient

__all__ = ['DifyWorkflowHandler', 'DifyClient']
__version__ = '1.0.0'
