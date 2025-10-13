#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试定时任务功能
手动触发F2、F3、F4三个任务
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
os.environ["APP_ID"] = "cli_a8fd44a9453cd00c"
os.environ["APP_SECRET"] = "jsVoFWgaaw05en6418h7xbhV5oXxAwIm"
os.environ["CHAT_ID"] = "oc_07f2d3d314f00fc29baf323a3a589972"
os.environ["FILE_URL"] = "https://be9bhmcgo2.feishu.cn/file/Wn5AbQAmVo32OExC5zIcIiAXnKc?office_edit=1"
os.environ["TZ"] = "America/Argentina/Buenos_Aires"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# 初始化飞书客户端
def init_lark_client():
    """初始化飞书SDK客户端"""
    try:
        client = lark.Client.builder() \
            .app_id(os.environ["APP_ID"]) \
            .app_secret(os.environ["APP_SECRET"]) \
            .build()
        return client
    except Exception as e:
        logger.error("初始化飞书客户端失败: %s", e)
        return None

def build_monthly_task_card() -> Dict:
    """构建月报任务卡片（F3）"""
    return {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "📋 月度报告任务"
            },
            "template": "blue"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "**本月报告任务已创建！**\n\n请及时完成您的月度报告。"
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "查看任务"
                        },
                        "type": "primary",
                        "url": os.environ["FILE_URL"]
                    }
                ]
            }
        ]
    }

def build_final_reminder_card() -> Dict:
    """构建最终提醒卡片（F4）"""
    return {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "⚠️ 最终提醒"
            },
            "template": "red"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "**月度报告截止日期临近！**\n\n请尽快完成您的报告。"
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "立即处理"
                        },
                        "type": "danger",
                        "url": os.environ["FILE_URL"]
                    }
                ]
            }
        ]
    }

async def send_card_to_chat(client, card: Dict, task_name: str) -> bool:
    """发送卡片到群聊"""
    try:
        logger.info("正在发送 %s...", task_name)
        
        # 按照官方文档构造请求对象
        request = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(CreateMessageRequestBody.builder()
                        .receive_id(os.environ["CHAT_ID"])
                        .msg_type("interactive")
                        .content(json.dumps(card, ensure_ascii=False))
                        .build()) \
            .build()
        
        # 发起请求
        response = await client.im.v1.message.acreate(request)
        
        if response.success():
            logger.info("✅ %s 发送成功", task_name)
            return True
        else:
            logger.error("❌ %s 发送失败, code: %s, msg: %s", 
                        task_name, response.code, response.msg)
            return False
            
    except Exception as e:
        logger.error("❌ %s 发送异常: %s", task_name, e)
        return False

async def test_f2_task_creation():
    """测试F2任务创建功能"""
    logger.info("="*60)
    logger.info("🧪 测试 F2. 任务创建（17–19日09:30）")
    logger.info("="*60)
    
    # 模拟任务创建逻辑
    now = datetime.now()
    logger.info("当前时间: %s", now.strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("✅ F2任务创建功能测试完成")
    logger.info("📝 在实际运行中，这里会创建具体的任务")
    logger.info("")

async def test_f3_task_card():
    """测试F3月报任务卡片功能"""
    logger.info("="*60)
    logger.info("🧪 测试 F3. 月报任务卡片（18–22日09:31）")
    logger.info("="*60)
    
    client = init_lark_client()
    if not client:
        logger.error("❌ 飞书客户端初始化失败")
        return
    
    # 构建并发送月报任务卡片
    card = build_monthly_task_card()
    success = await send_card_to_chat(client, card, "F3月报任务卡片")
    
    if success:
        logger.info("✅ F3月报任务卡片测试完成")
    else:
        logger.error("❌ F3月报任务卡片测试失败")
    logger.info("")

async def test_f4_final_reminder():
    """测试F4最终提醒功能"""
    logger.info("="*60)
    logger.info("🧪 测试 F4. 最终提醒（23日09:32）")
    logger.info("="*60)
    
    client = init_lark_client()
    if not client:
        logger.error("❌ 飞书客户端初始化失败")
        return
    
    # 构建并发送最终提醒卡片
    card = build_final_reminder_card()
    success = await send_card_to_chat(client, card, "F4最终提醒")
    
    if success:
        logger.info("✅ F4最终提醒测试完成")
    else:
        logger.error("❌ F4最终提醒测试失败")
    logger.info("")

async def main():
    """主函数"""
    logger.info("🚀 开始测试定时任务功能")
    logger.info("")
    
    # 测试F2任务创建
    await test_f2_task_creation()
    
    # 等待2秒
    await asyncio.sleep(2)
    
    # 测试F3月报任务卡片
    await test_f3_task_card()
    
    # 等待2秒
    await asyncio.sleep(2)
    
    # 测试F4最终提醒
    await test_f4_final_reminder()
    
    logger.info("="*60)
    logger.info("🎉 所有定时任务测试完成！")
    logger.info("请检查飞书群聊中的消息")
    logger.info("="*60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
    except Exception as e:
        logger.error("测试异常: %s", e)
