#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试长轮询功能
"""

import asyncio
import logging
from long_polling_handler import FeishuLongPollingHandler

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

async def test_welcome_handler(event_data):
    """测试欢迎处理器"""
    logger.info("测试欢迎处理器被调用")
    logger.info("事件数据: %s", event_data)
    return True

async def test_long_polling():
    """测试长轮询功能"""
    logger.info("开始测试长轮询功能...")
    
    # 创建长轮询处理器
    handler = FeishuLongPollingHandler()
    
    # 设置欢迎处理器
    handler.set_welcome_handler(test_welcome_handler)
    
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
    asyncio.run(test_long_polling())

