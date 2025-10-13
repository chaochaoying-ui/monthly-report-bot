#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复WebSocket配置
解决"获取租户令牌失败: invalid param"问题
"""

import os
import sys
import asyncio
import json
import logging

# 导入飞书官方SDK
import lark_oapi as lark
from lark_oapi.api.auth.v3 import *

# 设置环境变量
os.environ["APP_ID"] = "cli_a8fd44a9453cd00c"
os.environ["APP_SECRET"] = "jsVoFWgaaw05en6418h7xbhV5oXxAwIm"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

async def test_basic_auth():
    """测试基础认证"""
    logger.info("="*60)
    logger.info("🔍 测试基础认证")
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
            logger.info("✅ 基础认证成功")
            logger.info(f"租户访问令牌: {response.data.tenant_access_token[:20]}...")
            logger.info(f"过期时间: {response.data.expire}")
            return True
        else:
            logger.error(f"❌ 基础认证失败: {response.code} - {response.msg}")
            logger.error("可能的原因:")
            logger.error("1. APP_ID 或 APP_SECRET 错误")
            logger.error("2. 应用未正确配置")
            logger.error("3. 应用权限不足")
            return False
            
    except Exception as e:
        logger.error(f"❌ 基础认证异常: {e}")
        return False

async def main():
    """主函数"""
    logger.info("🚀 开始修复WebSocket配置")
    logger.info("")
    
    # 显示当前配置
    logger.info("当前配置:")
    logger.info(f"APP_ID: {os.environ['APP_ID']}")
    logger.info(f"APP_SECRET: {os.environ['APP_SECRET'][:10]}...")
    logger.info("")
    
    # 测试基础认证
    auth_success = await test_basic_auth()
    
    logger.info("="*60)
    if auth_success:
        logger.info("🎉 基础认证成功！")
        logger.info("")
        logger.info("🔧 下一步建议:")
        logger.info("1. 检查飞书开放平台的事件订阅配置")
        logger.info("2. 确认应用已获得必要权限")
        logger.info("3. 验证网络连接正常")
        logger.info("")
        logger.info("现在可以尝试运行完整功能版本:")
        logger.info("python monthly_report_bot_official.py")
    else:
        logger.info("❌ 基础认证失败")
        logger.info("")
        logger.info("🔧 解决方案:")
        logger.info("1. 检查飞书开放平台的应用配置")
        logger.info("2. 确认 APP_ID 和 APP_SECRET 正确")
        logger.info("3. 验证应用状态为已发布")
        logger.info("4. 检查应用权限设置")
        logger.info("")
        logger.info("建议使用简化版本:")
        logger.info("python monthly_report_bot_simple.py")
    
    logger.info("="*60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("修复被用户中断")
    except Exception as e:
        logger.error("修复异常: %s", e)
