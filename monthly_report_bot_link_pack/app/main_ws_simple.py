#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月报机器人 v1.1 - WS长连接版简化主程序（用于测试）
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

import pytz


# 确保以脚本直接运行时也能找到项目根目录的模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ws_wrapper import create_ws_handler
from card_design_ws_v1_1 import build_welcome_card

logger = logging.getLogger(__name__)

# 配置
APP_ID = (os.environ.get("APP_ID") or "").strip()
APP_SECRET = (os.environ.get("APP_SECRET") or "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()
FILE_URL = os.environ.get("FILE_URL", "").strip()
TZ_NAME = os.environ.get("TZ", "America/Argentina/Buenos_Aires")
TZ = pytz.timezone(TZ_NAME)

async def handle_bot_added_event(event_wrapper: Dict[str, Any]) -> bool:
    """欢迎卡片处理器"""
    try:
        logger.info("收到机器人加入事件")
        event = (event_wrapper or {}).get("event", {})
        chat_id = (event.get("chat_id") or CHAT_ID).strip()
        
        if not chat_id:
            logger.error("欢迎卡片缺少chat_id")
            return False
        
        # 构建欢迎卡片
        config = {
            "push_time": "09:30",
            "timezone": TZ_NAME,
            "file_url": FILE_URL
        }
        card = build_welcome_card(config)
        
        logger.info("欢迎卡片构建成功，准备发送到: %s", chat_id)
        logger.info("卡片内容: %s", json.dumps(card, ensure_ascii=False, indent=2))
        
        return True
        
    except Exception as e:
        logger.error("处理欢迎事件异常: %s", e)
        return False

async def handle_card_action_event(event: Dict[str, Any]) -> bool:
    """卡片交互处理器"""
    try:
        logger.info("收到卡片交互事件: %s", event)
        return True
    except Exception as e:
        logger.error("处理卡片交互异常: %s", e)
        return False

async def handle_message_event(event: Dict[str, Any]) -> bool:
    """消息处理器"""
    try:
        message = event.get("message", {})
        content = message.get("content", {})
        text = content.get("text", "").strip()
        
        if text:
            logger.info("收到消息: %s", text)
            
            # 简单的关键词匹配
            if "我的任务" in text or "my tasks" in text.lower():
                logger.info("识别到查询任务意图")
            elif "已完成" in text or "done" in text.lower():
                logger.info("识别到标记完成意图")
            elif "帮助" in text or "help" in text.lower():
                logger.info("识别到帮助意图")
        
        return True
        
    except Exception as e:
        logger.error("处理消息事件异常: %s", e)
        return False

async def schedule_loop():
    """简化的调度循环"""
    logger.info("启动调度循环（时区：%s）", TZ_NAME)
    
    while True:
        try:
            now = datetime.now(TZ)
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            
            # 每分钟记录一次时间
            if now.second == 0:
                logger.info("当前时间: %s", current_time)
                
                # 检查是否在任务创建时间窗口（17-19日09:30）
                if (17 <= now.day <= 19) and now.hour == 9 and now.minute == 30:
                    logger.info("到点：应该创建任务")
                
                # 检查是否在任务卡片时间窗口（18-22日09:31）
                elif (18 <= now.day <= 22) and now.hour == 9 and now.minute == 31:
                    logger.info("到点：应该发送月报任务卡片")
                
                # 检查是否在最终提醒时间窗口（23日09:32）
                elif now.day == 23 and now.hour == 9 and now.minute == 32:
                    logger.info("到点：应该发送最终提醒")
            
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error("调度循环异常: %s", e)
            await asyncio.sleep(5)

async def main():
    """主程序入口"""
    logger.info("启动月报机器人WS长连接版（测试模式）")
    logger.info("配置信息:")
    logger.info("  APP_ID: %s", APP_ID)
    logger.info("  CHAT_ID: %s", CHAT_ID)
    logger.info("  TZ: %s", TZ_NAME)
    logger.info("  FILE_URL: %s", FILE_URL)
    
    # 创建WS处理器
    handler = create_ws_handler()
    
    # 绑定事件处理器
    if hasattr(handler, "set_welcome_handler"):
        handler.set_welcome_handler(handle_bot_added_event)
        logger.info("已绑定欢迎卡片处理器")
    
    if hasattr(handler, "register_event_handler"):
        handler.register_event_handler("card.action.trigger", handle_card_action_event)
        handler.register_event_handler("im.message.receive_v1", handle_message_event)
        logger.info("已注册事件处理器")
    
    # 并行运行WS连接和调度循环
    logger.info("开始运行WS连接和调度循环...")
    await asyncio.gather(
        handler.connect_to_feishu(),
        schedule_loop()
    )

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler("monthly_report_bot_ws_test.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error("程序异常退出: %s", e)










