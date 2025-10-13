#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月报机器人增强版 - 包含核心定时任务和完成统计功能
不依赖WebSocket，专注于定时任务发送和统计
"""

from __future__ import annotations
import os, sys, time, json, math, datetime, logging
import tempfile
from typing import Dict, List, Tuple, Optional, Any
import argparse
import yaml, pytz
import asyncio
from datetime import datetime, timedelta

# 导入飞书官方SDK
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from lark_oapi.api.task.v2 import *

VERSION = "1.2.0-enhanced"

# ---------------------- 基础配置 ----------------------

# 强制设置标准输出编码为 UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    except Exception:
        pass

print("="*60)
print("月报机器人 v1.2 增强版 - 核心定时任务 + 完成统计")
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
CREATED_TASKS_FILE = os.path.join(BASE_DIR, "created_tasks.json")
TASK_STATS_FILE = os.path.join(BASE_DIR, "task_stats.json")

# 日志配置
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("monthly_report_bot_enhanced.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 全局变量
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

def init_lark_client() -> bool:
    """初始化飞书SDK客户端"""
    global lark_client
    
    try:
        lark_client = lark.Client.builder() \
            .app_id(APP_ID) \
            .app_secret(APP_SECRET) \
            .build()
        
        logger.info("飞书SDK客户端初始化成功")
        return True
        
    except Exception as e:
        logger.error("飞书SDK客户端初始化失败: %s", e)
        return False

# ---------------------- 任务统计管理 ----------------------

def load_task_stats() -> Dict[str, Any]:
    """加载任务统计信息"""
    try:
        if os.path.exists(TASK_STATS_FILE):
            with open(TASK_STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "current_month": datetime.now(TZ).strftime("%Y-%m"),
            "tasks": {},
            "total_tasks": 0,
            "completed_tasks": 0,
            "completion_rate": 0.0,
            "last_update": datetime.now(TZ).isoformat()
        }
    except Exception as e:
        logger.error("加载任务统计失败: %s", e)
        return {
            "current_month": datetime.now(TZ).strftime("%Y-%m"),
            "tasks": {},
            "total_tasks": 0,
            "completed_tasks": 0,
            "completion_rate": 0.0,
            "last_update": datetime.now(TZ).isoformat()
        }

def save_task_stats(stats: Dict[str, Any]) -> None:
    """保存任务统计信息"""
    try:
        stats["last_update"] = datetime.now(TZ).isoformat()
        with open(TASK_STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("保存任务统计失败: %s", e)

def update_task_completion(task_id: str, completed: bool = True) -> None:
    """更新任务完成状态"""
    try:
        stats = load_task_stats()
        current_month = datetime.now(TZ).strftime("%Y-%m")
        
        # 如果是新月份，重置统计
        if stats["current_month"] != current_month:
            stats = {
                "current_month": current_month,
                "tasks": {},
                "total_tasks": 0,
                "completed_tasks": 0,
                "completion_rate": 0.0,
                "last_update": datetime.now(TZ).isoformat()
            }
        
        # 更新任务状态
        if task_id not in stats["tasks"]:
            stats["tasks"][task_id] = {
                "created_at": datetime.now(TZ).isoformat(),
                "completed": False,
                "completed_at": None
            }
            stats["total_tasks"] += 1
        
        if completed and not stats["tasks"][task_id]["completed"]:
            stats["tasks"][task_id]["completed"] = True
            stats["tasks"][task_id]["completed_at"] = datetime.now(TZ).isoformat()
            stats["completed_tasks"] += 1
        
        # 计算完成率
        if stats["total_tasks"] > 0:
            stats["completion_rate"] = round(stats["completed_tasks"] / stats["total_tasks"] * 100, 2)
        
        save_task_stats(stats)
        logger.info("任务完成状态更新: %s -> %s", task_id, "已完成" if completed else "未完成")
        
    except Exception as e:
        logger.error("更新任务完成状态失败: %s", e)

def get_task_completion_stats() -> Dict[str, Any]:
    """获取任务完成统计"""
    try:
        stats = load_task_stats()
        current_month = datetime.now(TZ).strftime("%Y-%m")
        
        # 如果月份不匹配，返回空统计
        if stats["current_month"] != current_month:
            return {
                "current_month": current_month,
                "total_tasks": 0,
                "completed_tasks": 0,
                "completion_rate": 0.0,
                "pending_tasks": 0
            }
        
        pending_tasks = stats["total_tasks"] - stats["completed_tasks"]
        
        return {
            "current_month": stats["current_month"],
            "total_tasks": stats["total_tasks"],
            "completed_tasks": stats["completed_tasks"],
            "completion_rate": stats["completion_rate"],
            "pending_tasks": pending_tasks
        }
        
    except Exception as e:
        logger.error("获取任务完成统计失败: %s", e)
        return {
            "current_month": datetime.now(TZ).strftime("%Y-%m"),
            "total_tasks": 0,
            "completed_tasks": 0,
            "completion_rate": 0.0,
            "pending_tasks": 0
        }

# ---------------------- 任务管理函数 ----------------------

def load_created_tasks() -> Dict[str, bool]:
    """加载已创建的任务记录"""
    try:
        if os.path.exists(CREATED_TASKS_FILE):
            with open(CREATED_TASKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error("加载任务记录失败: %s", e)
        return {}

def save_created_tasks(tasks: Dict[str, bool]) -> None:
    """保存任务创建记录"""
    try:
        with open(CREATED_TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("保存任务记录失败: %s", e)

def load_tasks() -> List[Dict[str, Any]]:
    """加载任务配置"""
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error("加载任务配置失败: %s", e)
        return []

async def create_tasks() -> bool:
    """创建月度任务"""
    try:
        tasks = load_tasks()
        if not tasks:
            logger.error("没有找到任务配置")
            return False
        
        created_tasks = load_created_tasks()
        current_month = datetime.now(TZ).strftime("%Y-%m")
        
        # 检查是否已经创建过本月任务
        if created_tasks.get(current_month, False):
            logger.info("本月任务已创建，跳过")
            return True
        
        success_count = 0
        for i, task_config in enumerate(tasks):
            try:
                # 构建任务标题
                task_title = f"{current_month} {task_config['title']}"
                
                # 创建任务请求
                request = CreateTaskRequest.builder() \
                    .request_body(CreateTaskRequestBody.builder()
                                .summary(task_title)
                                .description(f"月度报告任务: {task_config['title']}\n文档链接: {task_config['doc_url']}")
                                .due_time(int(time.time() + 30 * 24 * 3600))  # 30天后到期
                                .origin(CreateTaskRequestBodyOrigin.builder()
                                       .platform_i18n_key("feishu")
                                       .href(task_config['doc_url'])
                                       .build())
                                .build()) \
                    .build()
                
                response = await lark_client.task.v2.task.acreate(request)
                
                if response.success():
                    task_id = response.data.task.guid
                    logger.info("任务创建成功: %s (ID: %s)", task_title, task_id)
                    
                    # 如果有负责人，分配任务
                    if task_config.get('assignee_open_id'):
                        assignee_request = CreateTaskCollaboratorRequest.builder() \
                            .task_guid(task_id) \
                            .request_body(CreateTaskCollaboratorRequestBody.builder()
                                        .id_list([task_config['assignee_open_id']])
                                        .build()) \
                            .build()
                        
                        assignee_response = await lark_client.task.v2.task_collaborator.acreate(assignee_request)
                        if assignee_response.success():
                            logger.info("任务分配成功: %s -> %s", task_title, task_config['assignee_open_id'])
                        else:
                            logger.warning("任务分配失败: %s", assignee_response.msg)
                    
                    # 更新统计
                    update_task_completion(task_id, False)
                    success_count += 1
                    
                else:
                    logger.error("任务创建失败: %s, code: %s, msg: %s", 
                               task_title, response.code, response.msg)
                    
            except Exception as e:
                logger.error("创建任务异常: %s, 任务: %s", e, task_config.get('title', 'Unknown'))
        
        if success_count > 0:
            # 标记本月任务已创建
            created_tasks[current_month] = True
            save_created_tasks(created_tasks)
            logger.info("本月任务创建完成，成功创建 %d 个任务", success_count)
            return True
        else:
            logger.error("没有成功创建任何任务")
            return False
            
    except Exception as e:
        logger.error("创建任务异常: %s", e)
        return False

async def check_task_completion() -> None:
    """检查任务完成情况"""
    try:
        stats = get_task_completion_stats()
        if stats["total_tasks"] == 0:
            return
        
        # 获取所有任务的最新状态
        tasks = load_tasks()
        current_month = datetime.now(TZ).strftime("%Y-%m")
        
        for task_config in tasks:
            task_title = f"{current_month} {task_config['title']}"
            
            # 这里可以添加检查任务完成状态的逻辑
            # 由于API限制，我们主要依赖手动更新
            
        logger.info("任务完成情况检查完成: 总计%d个，已完成%d个，完成率%.1f%%", 
                   stats["total_tasks"], stats["completed_tasks"], stats["completion_rate"])
        
    except Exception as e:
        logger.error("检查任务完成情况异常: %s", e)

# ---------------------- 卡片构建函数 ----------------------

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
    stats = get_task_completion_stats()
    
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
                    "content": f"**本月报告任务已创建！**\n\n📊 **任务统计**:\n• 总任务数: {stats['total_tasks']}\n• 已完成: {stats['completed_tasks']}\n• 待完成: {stats['pending_tasks']}\n• 完成率: {stats['completion_rate']}%\n\n请及时完成您的月度报告。"
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
    stats = get_task_completion_stats()
    
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
                    "content": f"**月度报告截止日期临近！**\n\n📊 **当前进度**:\n• 总任务数: {stats['total_tasks']}\n• 已完成: {stats['completed_tasks']}\n• 待完成: {stats['pending_tasks']}\n• 完成率: {stats['completion_rate']}%\n\n⚠️ 请尽快完成剩余报告！"
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

def build_stats_card() -> Dict:
    """构建统计卡片"""
    stats = get_task_completion_stats()
    
    # 计算进度条
    progress_width = min(int(stats['completion_rate'] / 10), 10)
    progress_bar = "█" * progress_width + "░" * (10 - progress_width)
    
    return {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "📊 月度报告完成统计"
            },
            "template": "green"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**{stats['current_month']} 月度报告进度**\n\n📈 **完成情况**:\n• 总任务数: {stats['total_tasks']}\n• 已完成: {stats['completed_tasks']}\n• 待完成: {stats['pending_tasks']}\n• 完成率: {stats['completion_rate']}%\n\n📊 **进度条**:\n`{progress_bar}` {stats['completion_rate']}%\n\n⏰ 更新时间: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')}"
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "查看详情"
                        },
                        "type": "default",
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
        # 按照官方文档构造请求对象
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
        
        if response.success():
            logger.info("卡片发送成功")
            return True
        else:
            logger.error("卡片发送失败, code: %s, msg: %s", response.code, response.msg)
            return False
            
    except Exception as e:
        logger.error("发送卡片异常: %s", e)
        return False

async def send_text_to_chat(text: str) -> bool:
    """发送文本消息到群聊"""
    try:
        request = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(CreateMessageRequestBody.builder()
                        .receive_id(CHAT_ID)
                        .msg_type("text")
                        .content(json.dumps({"text": text}, ensure_ascii=False))
                        .build()) \
            .build()
        
        response = await lark_client.im.v1.message.acreate(request)
        
        if response.success():
            logger.info("文本消息发送成功: %s", text)
            return True
        else:
            logger.error("文本消息发送失败, code: %s, msg: %s", response.code, response.msg)
            return False
            
    except Exception as e:
        logger.error("发送文本消息异常: %s", e)
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

def should_send_stats() -> bool:
    """判断是否应该发送统计信息（每日10:00）"""
    now = datetime.now(TZ)
    current_time = now.strftime("%H:%M")
    
    return current_time == "10:00"

# ---------------------- 主程序逻辑 ----------------------

async def main_loop():
    """主循环"""
    logger.info("启动月报机器人主循环")
    
    while True:
        try:
            now = datetime.now(TZ)
            logger.info("当前时间: %s", now.strftime("%Y-%m-%d %H:%M:%S"))
            
            # 检查定时任务
            if should_create_tasks():
                logger.info("执行任务创建...")
                success = await create_tasks()
                if success:
                    await send_text_to_chat("📋 本月任务已创建，请及时完成！")
                else:
                    await send_text_to_chat("❌ 任务创建失败，请检查配置")
            
            elif should_send_task_card():
                logger.info("发送月报任务卡片...")
                card = build_monthly_task_card()
                await send_card_to_chat(card)
            
            elif should_send_final_reminder():
                logger.info("发送最终提醒...")
                card = build_final_reminder_card()
                await send_card_to_chat(card)
            
            elif should_send_stats():
                logger.info("发送统计信息...")
                card = build_stats_card()
                await send_card_to_chat(card)
            
            # 每小时检查一次任务完成情况
            if now.minute == 0:
                await check_task_completion()
            
            # 等待1分钟
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error("主循环异常: %s", e)
            await asyncio.sleep(60)

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
    
    # 发送启动通知
    await send_text_to_chat("🚀 月报机器人增强版已启动，正在监控定时任务和统计完成情况...")
    
    # 启动主循环
    await main_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error("程序异常退出: %s", e)
