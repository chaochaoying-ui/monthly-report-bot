#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试飞书官方SDK功能
"""

import asyncio
import logging
import os
from lark_sdk_handler import LarkSDKHandler

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

async def test_welcome_handler(event_data):
    """测试欢迎处理器"""
    logger.info("测试欢迎处理器被调用")
    logger.info("事件数据: %s", event_data)
    return True

async def test_lark_sdk():
    """测试飞书官方SDK功能"""
    logger.info("开始测试飞书官方SDK功能...")
    
    # 创建SDK处理器
    handler = LarkSDKHandler()
    
    # 设置欢迎处理器
    handler.set_welcome_handler(test_welcome_handler)
    
    # 测试发送模板卡片
    logger.info("测试发送模板卡片...")
    template_variables = {
        "title": "测试卡片",
        "content": "这是一个测试卡片",
        "username": "测试用户",
        "welcome_message": "🎉 测试消息！"
    }
    
    # 注意：这里使用一个测试用户ID，实际使用时需要替换为真实的用户ID
    test_user_id = "mock_user_123"
    card_result = await handler.send_template_card(test_user_id, "AAqInYqWzIiu6", template_variables)
    logger.info("模板卡片发送结果: %s", card_result)
    
    # 测试发送文本消息
    logger.info("测试发送文本消息...")
    text_result = await handler.send_text_message(test_user_id, "🧪 测试消息：飞书官方SDK功能测试完成！")
    logger.info("文本消息发送结果: %s", text_result)
    
    # 运行一段时间进行测试
    logger.info("启动长轮询测试，运行30秒...")
    
    try:
        # 运行30秒
        await asyncio.wait_for(handler.start_polling(), timeout=30)
    except asyncio.TimeoutError:
        logger.info("测试完成")
    
    # 获取统计信息
    stats = handler.get_stats()
    logger.info("统计信息: %s", stats)

if __name__ == "__main__":
    asyncio.run(test_lark_sdk())

