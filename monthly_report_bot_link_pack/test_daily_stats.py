#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试每日统计功能（17:30定时任务）
手动触发每日统计卡片发送
"""

import os
import sys
import asyncio
import json
import logging
from datetime import datetime
import pytz

# 导入飞书官方SDK
import lark_oapi as lark
from lark_oapi.api.im.v1 import *

# 设置环境变量
APP_ID = os.environ.get("APP_ID", "cli_a8fd44a9453cd00c")
APP_SECRET = os.environ.get("APP_SECRET", "jsVoFWgaaw05en6418h7xbhV5oXxAwIm")
CHAT_ID = os.environ.get("CHAT_ID", "oc_07f2d3d314f00fc29baf323a3a589972")
FILE_URL = os.environ.get("FILE_URL", "https://be9bhmcgo2.feishu.cn/file/Wn5AbQAmVo32OExC5zIcIiAXnKc?office_edit=1")
TZ_NAME = os.environ.get("TZ", "America/Argentina/Buenos_Aires")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# 导入主程序模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from monthly_report_bot_final_interactive import (
        init_lark_client,
        build_daily_stats_card_with_chart,
        send_card_to_chat,
        lark_client
    )
    # 设置全局lark_client
    import monthly_report_bot_final_interactive as main_module
except ImportError as e:
    logger.error("导入主程序模块失败: %s", e)
    sys.exit(1)

async def test_daily_stats():
    """测试每日统计功能"""
    logger.info("="*60)
    logger.info("🧪 测试每日统计功能（17:30定时任务）")
    logger.info("="*60)

    # 初始化飞书客户端
    logger.info("初始化飞书客户端...")
    if not init_lark_client():
        logger.error("❌ 飞书客户端初始化失败")
        return

    logger.info("✅ 飞书客户端初始化成功")
    logger.info("")

    # 构建每日统计卡片（带图表）
    logger.info("📊 开始生成每日统计卡片...")
    try:
        card = await build_daily_stats_card_with_chart()
        logger.info("✅ 统计卡片生成成功")
        logger.info("")

        # 发送卡片
        logger.info("📤 发送统计卡片到群聊...")
        success = await send_card_to_chat(card)

        if success:
            logger.info("✅ 每日统计卡片发送成功！")
            logger.info("请检查飞书群聊中的消息")
        else:
            logger.error("❌ 每日统计卡片发送失败")

    except Exception as e:
        logger.error("❌ 测试失败: %s", e)
        import traceback
        traceback.print_exc()

    logger.info("")
    logger.info("="*60)
    logger.info("🎉 测试完成！")
    logger.info("="*60)

async def test_timing_function():
    """测试定时任务判断函数"""
    logger.info("")
    logger.info("="*60)
    logger.info("🧪 测试定时任务判断函数")
    logger.info("="*60)

    from monthly_report_bot_final_interactive import should_send_daily_stats

    # 测试不同时间点
    test_times = [
        datetime(2025, 10, 17, 17, 30),  # 17:30 - 应该触发
        datetime(2025, 10, 17, 17, 29),  # 17:29 - 不应该触发
        datetime(2025, 10, 17, 17, 31),  # 17:31 - 不应该触发
        datetime(2025, 10, 17, 10, 0),   # 10:00 - 不应该触发
    ]

    for test_time in test_times:
        tz = pytz.timezone(TZ_NAME)
        test_time_tz = tz.localize(test_time)
        result = should_send_daily_stats(test_time_tz)
        logger.info("时间: %s -> 触发: %s",
                   test_time.strftime("%H:%M"),
                   "✅ 是" if result else "❌ 否")

    logger.info("="*60)

async def main():
    """主函数"""
    logger.info("🚀 开始测试每日统计功能")
    logger.info("")

    # 测试定时判断函数
    await test_timing_function()

    # 等待2秒
    await asyncio.sleep(2)

    # 测试统计卡片生成和发送
    await test_daily_stats()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
    except Exception as e:
        logger.error("测试异常: %s", e)
        import traceback
        traceback.print_exc()

