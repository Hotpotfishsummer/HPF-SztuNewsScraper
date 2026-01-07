#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI 应用主程序
提供 RESTful API 接口
"""

import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..core.logger import get_logger
from ..core.config import get_config

logger = get_logger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="SZTU 新闻爬虫 API",
    description="深圳技术大学新闻爬虫 API 服务",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "ok",
        "message": "SZTU 新闻爬虫 API 服务运行中"
    }


@app.get("/api/v1/articles")
async def list_articles(skip: int = 0, limit: int = 10):
    """列出所有文章"""
    try:
        from core.scraper import get_all_articles_from_index
        
        articles = get_all_articles_from_index()
        
        # 分页处理
        total = len(articles)
        paginated = articles[skip:skip + limit]
        
        return {
            "status": "success",
            "total": total,
            "skip": skip,
            "limit": limit,
            "articles": paginated
        }
    
    except Exception as e:
        logger.error(f"获取文章列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/articles/{article_id}")
async def get_article(article_id: str):
    """获取指定文章详情"""
    try:
        from core.scraper import load_articles_index
        
        index = load_articles_index()
        
        # 查找文章
        for url, article_info in index.items():
            if article_info.get('filename') and article_info['filename'].replace('.json', '') == article_id:
                return {
                    "status": "success",
                    "article": article_info
                }
        
        raise HTTPException(status_code=404, detail="文章不存在")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文章详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/scrape")
async def scrape_articles(pages: int = 1):
    """爬取新闻文章"""
    try:
        if pages < 1 or pages > 10:
            raise HTTPException(status_code=400, detail="pages 必须在 1-10 之间")
        
        from core.scraper import fetch_articles_with_details
        
        logger.info(f"开始爬取 {pages} 页新闻...")
        fetch_articles_with_details(pages)
        
        return {
            "status": "success",
            "message": f"成功爬取 {pages} 页新闻"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"爬取新闻失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/config")
async def get_api_config():
    """获取系统配置信息"""
    try:
        config = get_config()
        
        return {
            "status": "success",
            "config": {
                "dify_enabled": config.dify_enabled,
                "log_level": config.log_level,
                "environment": config.environment
            }
        }
    
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    config = get_config()
    host = config.api_host
    port = config.api_port
    
    logger.info(f"启动 FastAPI 应用: http://{host}:{port}")
    logger.info(f"API 文档: http://{host}:{port}/docs")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=config.log_level.lower()
    )
