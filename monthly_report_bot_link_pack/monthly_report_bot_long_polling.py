#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月报机器人 v1.1 - 长轮询版本
基于需求说明书实现，使用长轮询替代WebSocket
"""

from __future__ import annotations
import os, sys, time, json, math, datetime, logging
import tempfile
from typing import Dict, List, Tuple, Optional, Any
import argparse
import requests, yaml, pytz
import asyncio
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager

# 导入自定义模块
from long_polling_handler import FeishuLongPollingHandler

VERSION = "1.1.0"

# ---------------------- 基础配置 ----------------------

# 强制设置标准输出编码为 UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    except Exception:
        pass

print("="*60)
print("月报机器人 v1.1 - 长轮询版本")
print("Python 版本:", sys.version)
print("当前工作目录:", os.getcwd())
print("="*60)

# 环境变量（按照需求文档8.1配置）
FEISHU = "https://open.feishu.cn/open-apis"
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

# 常量
REQUEST_TIMEOUT = 30

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
lp_handler = None

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

# ---------------------- 飞书API工具函数 ----------------------

def tenant_token() -> Optional[str]:
    """获取租户访问令牌"""
    try:
        url = f"{FEISHU}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": APP_ID,
            "app_secret": APP_SECRET
        }
        
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        if data.get("code", 0) == 0:
            return data.get("tenant_access_token", "")
        else:
            logger.error("获取租户令牌失败: %s", data.get("msg", "未知错误"))
            return None
            
    except Exception as e:
        logger.error("获取租户令牌异常: %s", e)
        return None

def send_card_to_chat(token: str, chat_id: str, card: Dict) -> bool:
    """发送卡片到群聊"""
    try:
        url = f"{FEISHU}/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "receive_id": chat_id,
            "msg_type": "interactive",
            "content": json.dumps(card, ensure_ascii=False)
        }
        
        response = requests.post(
            url, 
            json=payload, 
            headers=headers, 
            timeout=REQUEST_TIMEOUT,
            params={"receive_id_type": "chat_id"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code", 0) == 0:
                logger.info("卡片发送成功")
                return True
            else:
                logger.error("卡片发送失败: %s", data.get("msg"))
                return False
        else:
            logger.error("卡片发送HTTP错误: %d", response.status_code)
            return False
            
    except Exception as e:
        logger.error("发送卡片异常: %s", e)
        return False

def send_text_to_chat(token: str, chat_id: str, text: str) -> bool:
    """发送文本消息到群聊"""
    try:
        url = f"{FEISHU}/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "receive_id": chat_id,
            "msg_type": "text",
            "content": json.dumps({"text": text}, ensure_ascii=False)
        }
        
        response = requests.post(
            url, 
            json=payload, 
            headers=headers, 
            timeout=REQUEST_TIMEOUT,
            params={"receive_id_type": "chat_id"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code", 0) == 0:
                logger.info("文本消息发送成功")
                return True
            else:
                logger.error("文本消息发送失败: %s", data.get("msg"))
                return False
        else:
            logger.error("文本消息发送HTTP错误: %d", response.status_code)
            return False
            
    except Exception as e:
        logger.error("发送文本消息异常: %s", e)
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
        token = tenant_token()
        if not token:
            return False
        
        url = f"{FEISHU}/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 使用模板卡片格式
        payload = {
            "receive_id": user_id,
            "msg_type": "interactive",
            "content": json.dumps({
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
            }, ensure_ascii=False)
        }
        
        response = requests.post(
            url, 
            json=payload, 
            headers=headers, 
            timeout=REQUEST_TIMEOUT,
            params={"receive_id_type": "user_id"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code", 0) == 0:
                logger.info("欢迎卡片发送成功，用户ID: %s", user_id)
                return True
            else:
                logger.error("欢迎卡片发送失败: %s", data.get("msg"))
                return False
        else:
            logger.error("欢迎卡片发送HTTP错误: %d", response.status_code)
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
                token = tenant_token()
                if token:
                    card = build_monthly_task_card()
                    send_card_to_chat(token, CHAT_ID, card)
            
            elif should_send_final_reminder():
                logger.info("发送最终提醒...")
                token = tenant_token()
                if token:
                    card = build_final_reminder_card()
                    send_card_to_chat(token, CHAT_ID, card)
            
            # 等待1分钟
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error("主循环异常: %s", e)
            await asyncio.sleep(60)

async def start_long_polling():
    """启动长轮询事件处理"""
    global lp_handler
    
    logger.info("启动长轮询事件处理...")
    
    # 创建长轮询处理器
    lp_handler = FeishuLongPollingHandler()
    
    # 设置欢迎卡片处理器
    lp_handler.set_welcome_handler(handle_new_member_welcome)
    
    # 启动长轮询
    await lp_handler.start_polling()

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
    
    # 启动主循环和长轮询
    await asyncio.gather(
        main_loop(),
        start_long_polling()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error("程序异常退出: %s", e)

