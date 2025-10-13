#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查WebSocket配置
验证事件订阅和权限配置
"""

import os
import sys
import asyncio
import json
import logging
from datetime import datetime

# 导入飞书官方SDK
import lark_oapi as lark
from lark_oapi.api.auth.v3 import *
from lark_oapi.api.event.v1 import *

# 设置环境变量
os.environ["APP_ID"] = "cli_a8fd44a9453cd00c"
os.environ["APP_SECRET"] = "jsVoFWgaaw05en6418h7xbhV5oXxAwIm"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

async def check_app_credentials():
    """检查应用凭证"""
    logger.info("="*60)
    logger.info("🔍 检查应用凭证")
    logger.info("="*60)
    
    try:
        client = lark.Client.builder() \
            .app_id(os.environ["APP_ID"]) \
            .app_secret(os.environ["APP_SECRET"]) \
            .build()
        
        # 获取租户访问令牌
        request = CreateTenantAccessTokenRequest.builder() \
            .request_body(CreateTenantAccessTokenRequestBody.builder()
                        .app_id(os.environ["APP_ID"])
                        .app_secret(os.environ["APP_SECRET"])
                        .build()) \
            .build()
        
        response = await client.auth.v3.tenant_access_token.acreate(request)
        
        if response.success():
            logger.info("✅ 应用凭证验证成功")
            logger.info(f"租户访问令牌: {response.data.tenant_access_token[:20]}...")
            return True
        else:
            logger.error(f"❌ 应用凭证验证失败: {response.code} - {response.msg}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 应用凭证检查异常: {e}")
        return False

async def check_event_subscription():
    """检查事件订阅配置"""
    logger.info("="*60)
    logger.info("🔍 检查事件订阅配置")
    logger.info("="*60)
    
    try:
        client = lark.Client.builder() \
            .app_id(os.environ["APP_ID"]) \
            .app_secret(os.environ["APP_SECRET"]) \
            .build()
        
        # 获取事件订阅配置
        request = GetEventSubscriptionRequest.builder().build()
        response = await client.event.v1.event_subscription.aget(request)
        
        if response.success():
            logger.info("✅ 事件订阅配置获取成功")
            logger.info(f"事件订阅URL: {response.data.endpoint}")
            logger.info(f"事件类型: {response.data.event_types}")
            return True
        else:
            logger.error(f"❌ 事件订阅配置获取失败: {response.code} - {response.msg}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 事件订阅检查异常: {e}")
        return False

async def check_app_permissions():
    """检查应用权限"""
    logger.info("="*60)
    logger.info("🔍 检查应用权限")
    logger.info("="*60)
    
    try:
        client = lark.Client.builder() \
            .app_id(os.environ["APP_ID"]) \
            .app_secret(os.environ["APP_SECRET"]) \
            .build()
        
        # 获取应用信息
        request = GetAppRequest.builder().build()
        response = await client.application.v1.app.aget(request)
        
        if response.success():
            logger.info("✅ 应用权限检查成功")
            logger.info(f"应用名称: {response.data.app.name}")
            logger.info(f"应用描述: {response.data.app.description}")
            return True
        else:
            logger.error(f"❌ 应用权限检查失败: {response.code} - {response.msg}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 应用权限检查异常: {e}")
        return False

async def test_websocket_connection():
    """测试WebSocket连接"""
    logger.info("="*60)
    logger.info("🔍 测试WebSocket连接")
    logger.info("="*60)
    
    try:
        client = lark.Client.builder() \
            .app_id(os.environ["APP_ID"]) \
            .app_secret(os.environ["APP_SECRET"]) \
            .build()
        
        # 获取WebSocket URL
        request = GetWebSocketUrlRequest.builder().build()
        response = await client.event.v1.web_socket_url.aget(request)
        
        if response.success():
            logger.info("✅ WebSocket URL获取成功")
            logger.info(f"WebSocket URL: {response.data.url}")
            return True
        else:
            logger.error(f"❌ WebSocket URL获取失败: {response.code} - {response.msg}")
            return False
            
    except Exception as e:
        logger.error(f"❌ WebSocket连接测试异常: {e}")
        return False

async def main():
    """主函数"""
    logger.info("🚀 开始检查WebSocket配置")
    logger.info("")
    
    # 检查各项配置
    checks = [
        ("应用凭证", check_app_credentials()),
        ("事件订阅", check_event_subscription()),
        ("应用权限", check_app_permissions()),
        ("WebSocket连接", test_websocket_connection())
    ]
    
    results = []
    for check_name, check_coro in checks:
        logger.info(f"正在检查: {check_name}")
        result = await check_coro
        results.append((check_name, result))
        logger.info("")
    
    # 总结
    logger.info("="*60)
    logger.info("📊 检查结果总结")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{check_name}: {status}")
    
    logger.info("")
    if passed == total:
        logger.info("🎉 所有检查通过！WebSocket配置正确")
    else:
        logger.info("⚠️  部分检查失败，请检查相关配置")
        logger.info("")
        logger.info("🔧 建议解决方案:")
        logger.info("1. 检查飞书开放平台的应用配置")
        logger.info("2. 确认事件订阅已正确配置")
        logger.info("3. 验证应用权限设置")
        logger.info("4. 检查网络连接")
    
    logger.info("="*60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("检查被用户中断")
    except Exception as e:
        logger.error("检查异常: %s", e)
