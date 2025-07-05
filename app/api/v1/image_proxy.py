"""
图片代理API

提供图片代理服务，解决跨域访问问题
"""

import base64
import asyncio
from typing import Optional
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, HTTPException, Query, Response
from loguru import logger

router = APIRouter()


@router.get("/image")
async def proxy_image(
    url: str = Query(..., description="Base64编码的图片URL"),
    platform: Optional[str] = Query(None, description="平台名称"),
    timeout: int = Query(30, description="超时时间（秒）")
):
    """
    代理图片请求
    
    Args:
        url: Base64编码的原始图片URL
        platform: 平台名称（bilibili, xianyu等）
        timeout: 请求超时时间
        
    Returns:
        图片二进制数据
    """
    try:
        # 解码URL
        try:
            decoded_url = base64.urlsafe_b64decode(url.encode()).decode()
        except Exception as e:
            logger.error(f"URL解码失败: {e}")
            raise HTTPException(status_code=400, detail="无效的URL编码")
        
        # 验证URL格式
        parsed = urlparse(decoded_url)
        if not parsed.scheme or not parsed.netloc:
            raise HTTPException(status_code=400, detail="无效的URL格式")
        
        logger.info(f"代理图片请求: {decoded_url} (platform: {platform})")
        
        # 设置请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        
        # 根据平台设置特定的请求头
        if platform == "bilibili":
            headers.update({
                "Referer": "https://www.bilibili.com/",
                "Origin": "https://www.bilibili.com"
            })
        elif platform == "xianyu":
            headers.update({
                "Referer": "https://www.taobao.com/",
                "Origin": "https://www.taobao.com"
            })
        
        # 发起HTTP请求
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(decoded_url, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"图片请求失败: {response.status_code} - {decoded_url}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"图片请求失败: {response.status_code}"
                )
            
            # 获取内容类型
            content_type = response.headers.get("content-type", "image/jpeg")
            
            # 验证是否为图片
            if not content_type.startswith("image/"):
                logger.error(f"响应不是图片格式: {content_type}")
                raise HTTPException(status_code=400, detail="响应不是图片格式")
            
            # 获取图片大小
            content_length = len(response.content)
            logger.info(f"图片代理成功: {decoded_url}, 大小: {content_length} bytes")
            
            # 返回图片数据
            return Response(
                content=response.content,
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=86400",  # 缓存1天
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET",
                    "Access-Control-Allow-Headers": "*"
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"图片代理失败: {e}, url: {url}")
        raise HTTPException(status_code=500, detail=f"图片代理失败: {str(e)}")


@router.get("/info")
async def get_image_info(
    url: str = Query(..., description="Base64编码的图片URL")
):
    """
    获取图片信息
    
    Args:
        url: Base64编码的原始图片URL
        
    Returns:
        图片信息
    """
    try:
        # 解码URL
        try:
            decoded_url = base64.urlsafe_b64decode(url.encode()).decode()
        except Exception as e:
            logger.error(f"URL解码失败: {e}")
            raise HTTPException(status_code=400, detail="无效的URL编码")
        
        # 验证URL格式
        parsed = urlparse(decoded_url)
        if not parsed.scheme or not parsed.netloc:
            raise HTTPException(status_code=400, detail="无效的URL格式")
        
        # 发起HEAD请求获取图片信息
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.head(decoded_url, headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"无法获取图片信息: {response.status_code}"
                )
            
            return {
                "url": decoded_url,
                "content_type": response.headers.get("content-type", "unknown"),
                "content_length": response.headers.get("content-length", "unknown"),
                "last_modified": response.headers.get("last-modified", "unknown"),
                "status_code": response.status_code
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取图片信息失败: {e}, url: {url}")
        raise HTTPException(status_code=500, detail=f"获取图片信息失败: {str(e)}") 