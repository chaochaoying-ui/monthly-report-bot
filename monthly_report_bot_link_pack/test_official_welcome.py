#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试基于飞书官方文档标准版本的新成员欢迎功能
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
os.environ["VERIFICATION_TOKEN"] = "test_token"

# 导入飞书官方SDK
import lark_oapi as lark
from lark_oapi.api.im.v1 import *

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

async def test_send_welcome_card_to_chat():
    """测试向群聊发送欢迎卡片"""
    try:
        # 创建飞书客户端
        client = lark.Client.builder() \
            .app_id(os.environ["APP_ID"]) \
            .app_secret(os.environ["APP_SECRET"]) \
            .log_level(lark.LogLevel.INFO) \
            .build()
        
        # 构建欢迎卡片
        welcome_card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "🎉 欢迎新成员"
                },
                "template": "green"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "**欢迎加入我们的团队！**\n\n我们很高兴您加入我们的群聊。"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "**当前配置信息：**\n- 时区：America/Argentina/Buenos_Aires\n- 文件链接：已配置\n- 推送时间：09:30-09:32"
                    }
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "查看帮助"
                            },
                            "type": "default",
                            "value": {
                                "action": "view_help"
                            }
                        },
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "设置配置"
                            },
                            "type": "primary",
                            "value": {
                                "action": "setup_config"
                            }
                        }
                    ]
                }
            ]
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

async def test_send_template_card():
    """测试发送模板卡片"""
    try:
        # 创建飞书客户端
        client = lark.Client.builder() \
            .app_id(os.environ["APP_ID"]) \
            .app_secret(os.environ["APP_SECRET"]) \
            .log_level(lark.LogLevel.INFO) \
            .build()
        
        # 构建模板卡片
        template_card = {
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
                        .content(json.dumps(template_card, ensure_ascii=False))
                        .build()) \
            .build()
        
        # 发起请求
        response = await client.im.v1.message.acreate(request)
        
        # 处理失败返回
        if not response.success():
            logger.error(f"发送模板卡片失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return False
        
        # 处理业务结果
        logger.info("模板卡片发送成功: %s", lark.JSON.marshal(response.data, indent=4))
        return True
        
    except Exception as e:
        logger.error("发送模板卡片异常: %s", e)
        return False

async def test_send_text_message():
    """测试发送文本消息"""
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
                        .content(json.dumps({"text": "🎉 欢迎新成员加入！这是基于飞书官方文档标准版本的测试消息。"}, ensure_ascii=False))
                        .build()) \
            .build()
        
        # 发起请求
        response = await client.im.v1.message.acreate(request)
        
        # 处理失败返回
        if not response.success():
            logger.error(f"发送文本消息失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return False
        
        # 处理业务结果
        logger.info("文本消息发送成功: %s", lark.JSON.marshal(response.data, indent=4))
        return True
        
    except Exception as e:
        logger.error("发送文本消息异常: %s", e)
        return False

async def main():
    """主测试函数"""
    print("="*60)
    print("测试基于飞书官方文档标准版本的新成员欢迎功能")
    print("="*60)
    
    # 测试1：发送欢迎卡片到群聊
    print("\n1. 测试发送欢迎卡片到群聊...")
    result1 = await test_send_welcome_card_to_chat()
    print(f"结果: {'成功' if result1 else '失败'}")
    
    # 等待2秒
    await asyncio.sleep(2)
    
    # 测试2：发送模板卡片
    print("\n2. 测试发送模板卡片...")
    result2 = await test_send_template_card()
    print(f"结果: {'成功' if result2 else '失败'}")
    
    # 等待2秒
    await asyncio.sleep(2)
    
    # 测试3：发送文本消息
    print("\n3. 测试发送文本消息...")
    result3 = await test_send_text_message()
    print(f"结果: {'成功' if result3 else '失败'}")
    
    # 总结
    print("\n" + "="*60)
    print("测试总结:")
    print(f"- 欢迎卡片发送: {'✅ 成功' if result1 else '❌ 失败'}")
    print(f"- 模板卡片发送: {'✅ 成功' if result2 else '❌ 失败'}")
    print(f"- 文本消息发送: {'✅ 成功' if result3 else '❌ 失败'}")
    print("="*60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试异常: {e}")
