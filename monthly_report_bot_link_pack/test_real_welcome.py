#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试真实的新成员欢迎功能
向群聊发送欢迎卡片，模拟新成员加入的效果
"""

import os
import sys
import asyncio
import json
import logging
from datetime import datetime

# 设置环境变量
os.environ["APP_ID"] = "cli_a8fd44a9453cd00c"
os.environ["APP_SECRET"] = "jsVoFWgaaw05en6418h7xbhV5oXxAwIm"
os.environ["CHAT_ID"] = "oc_07f2d3d314f00fc29baf323a3a589972"
os.environ["WELCOME_CARD_ID"] = "AAqInYqWzIiu6"

# 导入飞书官方SDK
import lark_oapi as lark
from lark_oapi.api.im.v1 import *

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

async def send_welcome_card_to_chat():
    """向群聊发送欢迎卡片"""
    try:
        # 创建飞书客户端
        client = lark.Client.builder() \
            .app_id(os.environ["APP_ID"]) \
            .app_secret(os.environ["APP_SECRET"]) \
            .log_level(lark.LogLevel.INFO) \
            .build()
        
        # 构建欢迎卡片（使用模板格式）
        welcome_card = {
            "type": "template",
            "data": {
                "template_id": os.environ["WELCOME_CARD_ID"],
                "template_variable": {
                    "title": "欢迎新成员",
                    "content": "我们很高兴您加入我们的团队！",
                    "username": "系统管理员",
                    "welcome_message": "🎉 欢迎加入我们的群聊！"
                }
            }
        }
        
        # 构造请求对象
        request = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(CreateMessageRequestBody.builder()
                        .receive_id(os.environ["CHAT_ID"])
                        .msg_type("interactive")
                        .content(json.dumps(welcome_card, ensure_ascii=False))
                        .build()) \
            .build()
        
        # 发起请求
        response = await client.im.v1.message.acreate(request)
        
        # 处理失败返回
        if not response.success():
            logger.error(f"发送欢迎卡片失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return False
        
        # 处理业务结果
        logger.info("欢迎卡片发送成功: %s", lark.JSON.marshal(response.data, indent=4))
        return True
        
    except Exception as e:
        logger.error("发送欢迎卡片异常: %s", e)
        return False

async def send_test_message():
    """发送测试消息"""
    try:
        # 创建飞书客户端
        client = lark.Client.builder() \
            .app_id(os.environ["APP_ID"]) \
            .app_secret(os.environ["APP_SECRET"]) \
            .log_level(lark.LogLevel.INFO) \
            .build()
        
        # 构造请求对象
        request = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(CreateMessageRequestBody.builder()
                        .receive_id(os.environ["CHAT_ID"])
                        .msg_type("text")
                        .content(json.dumps({"text": "🤖 月报机器人已启动！\n\n基于飞书官方文档标准版本正在运行中...\n\n功能包括：\n✅ 新成员欢迎卡片\n✅ 定时任务管理\n✅ 月报进度跟踪\n✅ 最终提醒通知\n\n现在可以邀请新成员进群测试欢迎功能！"}, ensure_ascii=False))
                        .build()) \
            .build()
        
        # 发起请求
        response = await client.im.v1.message.acreate(request)
        
        # 处理失败返回
        if not response.success():
            logger.error(f"发送测试消息失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return False
        
        # 处理业务结果
        logger.info("测试消息发送成功: %s", lark.JSON.marshal(response.data, indent=4))
        return True
        
    except Exception as e:
        logger.error("发送测试消息异常: %s", e)
        return False

async def main():
    """主测试函数"""
    print("="*60)
    print("测试真实的新成员欢迎功能")
    print("="*60)
    
    # 测试1：发送测试消息
    print("\n1. 发送机器人启动通知...")
    result1 = await send_test_message()
    print(f"结果: {'✅ 成功' if result1 else '❌ 失败'}")
    
    # 等待3秒
    await asyncio.sleep(3)
    
    # 测试2：发送欢迎卡片
    print("\n2. 发送新成员欢迎卡片...")
    result2 = await send_welcome_card_to_chat()
    print(f"结果: {'✅ 成功' if result2 else '❌ 失败'}")
    
    # 总结
    print("\n" + "="*60)
    print("测试总结:")
    print(f"- 启动通知: {'✅ 成功' if result1 else '❌ 失败'}")
    print(f"- 欢迎卡片: {'✅ 成功' if result2 else '❌ 失败'}")
    print("\n💡 提示:")
    print("- 现在可以邀请新成员进群")
    print("- 程序会自动检测并发送欢迎卡片")
    print("- 查看群聊中的消息确认功能正常")
    print("="*60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试异常: {e}")
