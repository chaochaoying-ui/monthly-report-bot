#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月报机器人 v1.1 - 基于飞书官方SDK版本
使用lark-oapi SDK实现更稳定的功能
"""

from __future__ import annotations
import os, sys, time, json, math, datetime, logging
import tempfile
from typing import Dict, List, Tuple, Optional, Any
import argparse
import yaml, pytz
import asyncio
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager

# 导入飞书官方SDK
import lark_oapi as lark
from lark_oapi.api.im.v1 import *

# 导入自定义模块
from lark_sdk_handler import LarkSDKHandler

VERSION = "1.1.0"

# ---------------------- 基础配置 ----------------------

# 强制设置标准输出编码为 UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    except Exception:
        pass

print("="*60)
print("月报机器人 v1.1 - 基于飞书官方SDK版本")
print("Python 版本:", sys.version)
print("当前工作目录:", os.getcwd())
print("="*60)

# 环境变量（按照需求文档8.1配置）
APP_ID     = os.environ.get("APP_ID", "cli_a8fd44a9453cd00c").strip()
APP_SECRET = os.environ.get("APP_SECRET", "jsVoFWgaaw05en6418h7xbhV5oXxAwIm").strip()
CHAT_ID    = os.environ.get("CHAT_ID", "oc_07f2d3d314f00fc29baf323a3a589972").strip()
FILE_URL   = os.environ.get("FILE_URL", "https://be9bhmcgo2.feishu.cn/file/Wn5AbQAmVo32OExC5zIcIiAXnKc?office_edit=1").strip()
TZ_NAME    = os.environ.get("TZ", "America/Argentina/Buenos_Aires")
TZ         = pytz.timezone(TZ_NAME)

# 欢迎卡片配置
WELCOME_CARD_ID = os.environ.get("WELCOME_CARD_ID", "AAqInYqWzIiu6")

# 日志与监控
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# 文件路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(BASE_DIR, "tasks.yaml")
GROUP_CONFIG_FILE = os.path.join(BASE_DIR, "group_config.json")
CREATED_TASKS_FILE = os.path.join(BASE_DIR, "created_tasks.json")
INTERACTION_LOG_FILE = os.path.join(BASE_DIR, "interaction_log.json")

# 日志配置
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("monthly_report_bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 全局变量
lark_handler = None
lark_client = None

# ---------------------- 环境变量验证 ----------------------

def validate_env_vars() -> List[str]:
    """验证环境变量"""
    errors = []
    
    if not APP_ID:
        errors.append("APP_ID 未设置")
    if not APP_SECRET:
        errors.append("APP_SECRET 未设置")
    if not CHAT_ID:
        errors.append("CHAT_ID 未设置")
    if not FILE_URL:
        errors.append("FILE_URL 未设置")
    
    return errors

# ---------------------- 飞书SDK客户端初始化 ----------------------

def init_lark_client():
    """初始化飞书SDK客户端"""
    global lark_client
    
    try:
        lark_client = lark.Client.builder() \
            .app_id(APP_ID) \
            .app_secret(APP_SECRET) \
            .log_level(lark.LogLevel.INFO) \
            .build()
        
        logger.info("飞书SDK客户端初始化成功")
        return True
    except Exception as e:
        logger.error("飞书SDK客户端初始化失败: %s", e)
        return False

# ---------------------- 卡片设计 ----------------------

def build_welcome_card() -> Dict:
    """构建欢迎卡片"""
    return {
        "type": "template",
        "data": {
            "template_id": WELCOME_CARD_ID,
            "template_variable": {
                "title": "欢迎新成员",
                "content": "我们很高兴您加入我们的团队！",
                "username": "系统管理员",
                "welcome_message": "🎉 欢迎加入我们的群聊！"
            }
        }
    }

def build_monthly_task_card() -> Dict:
    """构建月报任务卡片"""
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
                        "url": FILE_URL
                    }
                ]
            }
        ]
    }

def build_final_reminder_card() -> Dict:
    """构建最终提醒卡片"""
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
                        "url": FILE_URL
                    }
                ]
            }
        ]
    }

# ---------------------- 消息发送函数 ----------------------

async def send_card_to_chat(card: Dict) -> bool:
    """发送卡片到群聊"""
    try:
        # 构造请求对象
        request = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(CreateMessageRequestBody.builder()
                        .receive_id(CHAT_ID)
                        .msg_type("interactive")
                        .content(json.dumps(card, ensure_ascii=False))
                        .build()) \
            .build()
        
        # 发起请求
        response = await lark_client.im.v1.message.acreate(request)
        
        # 处理失败返回
        if not response.success():
            logger.error(f"发送卡片失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
            return False
        
        # 处理业务结果
        logger.info("卡片发送成功: %s", lark.JSON.marshal(response.data, indent=4))
        return True
        
    except Exception as e:
        logger.error("发送卡片异常: %s", e)
        return False

async def send_text_to_chat(text: str) -> bool:
    """发送文本消息到群聊"""
    try:
        # 构造请求对象
        request = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(CreateMessageRequestBody.builder()
                        .receive_id(CHAT_ID)
                        .msg_type("text")
                        .content(json.dumps({"text": text}, ensure_ascii=False))
                        .build()) \
            .build()
        
        # 发起请求
        response = await lark_client.im.v1.message.acreate(request)
        
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

# ---------------------- 新成员欢迎处理 ----------------------

async def handle_new_member_welcome(event_data: Dict) -> bool:
    """处理新成员欢迎"""
    try:
        event = event_data.get("event", {})
        event_type = event.get("type")
        
        if event_type == "im.chat.member.user.added_v1":
            users = event.get("users", [])
            success_count = 0
            
            for user in users:
                user_id = user.get("user_id")
                if user_id:
                    if await send_welcome_card_to_user(user_id):
                        success_count += 1
                        logger.info("成功向用户 %s 发送欢迎卡片", user_id)
                    else:
                        logger.error("向用户 %s 发送欢迎卡片失败", user_id)
            
            logger.info("欢迎卡片发送完成，成功: %d/%d", success_count, len(users))
            return success_count > 0
            
        elif event_type == "im.chat.member.bot.added_v1":
            bots = event.get("bots", [])
            logger.info("机器人加入群聊: %s", bots)
            return True
        
        return False
        
    except Exception as e:
        logger.error("处理新成员进群事件异常: %s", e)
        return False

async def send_welcome_card_to_user(user_id: str) -> bool:
    """向用户发送欢迎卡片"""
    try:
        # 使用SDK处理器发送模板卡片
        if lark_handler:
            template_variables = {
                "title": "欢迎新成员",
                "content": "我们很高兴您加入我们的团队！",
                "username": "系统管理员",
                "welcome_message": "🎉 欢迎加入我们的群聊！"
            }
            return await lark_handler.send_template_card(user_id, WELCOME_CARD_ID, template_variables)
        else:
            logger.error("SDK处理器未初始化")
            return False
            
    except Exception as e:
        logger.error("发送欢迎卡片异常: %s", e)
        return False

# ---------------------- 定时任务 ----------------------

def should_create_tasks() -> bool:
    """判断是否应该创建任务（17-19日09:30）"""
    now = datetime.now(TZ)
    current_day = now.day
    current_time = now.strftime("%H:%M")
    
    return 17 <= current_day <= 19 and current_time == "09:30"

def should_send_task_card() -> bool:
    """判断是否应该发送任务卡片（18-22日09:31）"""
    now = datetime.now(TZ)
    current_day = now.day
    current_time = now.strftime("%H:%M")
    
    return 18 <= current_day <= 22 and current_time == "09:31"

def should_send_final_reminder() -> bool:
    """判断是否应该发送最终提醒（23日09:32）"""
    now = datetime.now(TZ)
    current_day = now.day
    current_time = now.strftime("%H:%M")
    
    return current_day == 23 and current_time == "09:32"

# ---------------------- 主程序逻辑 ----------------------

async def main_loop():
    """主循环"""
    logger.info("启动月报机器人主循环")
    
    while True:
        try:
            # 检查定时任务
            if should_create_tasks():
                logger.info("执行任务创建...")
                now = datetime.now(TZ)
                logger.info("任务创建时间: %s", now.strftime("%Y-%m-%d %H:%M:%S"))
            
            elif should_send_task_card():
                logger.info("发送月报任务卡片...")
                card = build_monthly_task_card()
                await send_card_to_chat(card)
            
            elif should_send_final_reminder():
                logger.info("发送最终提醒...")
                card = build_final_reminder_card()
                await send_card_to_chat(card)
            
            # 等待1分钟
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error("主循环异常: %s", e)
            await asyncio.sleep(60)

async def start_lark_sdk_handler():
    """启动基于SDK的事件处理"""
    global lark_handler
    
    logger.info("启动基于飞书官方SDK的事件处理...")
    
    # 创建SDK处理器
    lark_handler = LarkSDKHandler()
    
    # 设置欢迎卡片处理器
    lark_handler.set_welcome_handler(handle_new_member_welcome)
    
    # 启动长轮询
    await lark_handler.start_polling()

async def main():
    """主函数"""
    # 验证环境变量
    errors = validate_env_vars()
    if errors:
        logger.error("环境变量验证失败: %s", errors)
        return
    
    logger.info("环境变量验证通过")
    logger.info("APP_ID: %s", APP_ID)
    logger.info("CHAT_ID: %s", CHAT_ID)
    logger.info("WELCOME_CARD_ID: %s", WELCOME_CARD_ID)
    logger.info("SDK版本: lark-oapi")
    
    # 初始化飞书SDK客户端
    if not init_lark_client():
        logger.error("飞书SDK客户端初始化失败，程序退出")
        return
    
    # 启动主循环和SDK事件处理
    await asyncio.gather(
        main_loop(),
        start_lark_sdk_handler()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error("程序异常退出: %s", e)
