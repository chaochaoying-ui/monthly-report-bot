#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月报机器人 v1.1 - 基于需求说明书实现
设计理念：稳定可靠、技术先进、用户友好的月报管理助手

核心功能：
1. WebSocket长连接回调（仅WS）
2. 智能交互引擎（多语言、意图识别）
3. 群级配置管理
4. 幂等性与补跑机制
5. 专业级卡片设计
"""

from __future__ import annotations
import os, sys, time, json, math, datetime, logging
import tempfile
from typing import Dict, List, Tuple, Optional, Any
import argparse
import requests, yaml, pytz
import asyncio
import websockets
import hmac
import hashlib
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager

# 导入自定义模块
from card_design_ws_v1_1 import (
    build_welcome_card, build_monthly_task_card,
    build_final_reminder_card, build_help_card,
    build_progress_chart_card
)
from smart_interaction_ws_v1_1 import SmartInteractionEngine
from websocket_handler_v1_1 import FeishuWebSocketHandler

VERSION = "1.1.0"

# ---------------------- 基础配置 ----------------------

# 强制设置标准输出编码为 UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    except Exception:
        pass

print("="*60)
print("月报机器人 v1.1 - 基于需求说明书实现")
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

# WebSocket配置
WS_ENDPOINT = os.environ.get("WS_ENDPOINT", "wss://open.feishu.cn/ws/v2")
WS_HEARTBEAT_INTERVAL = int(os.environ.get("WS_HEARTBEAT_INTERVAL", "30"))
WS_RECONNECT_MAX_ATTEMPTS = int(os.environ.get("WS_RECONNECT_MAX_ATTEMPTS", "5"))

# 欢迎卡片配置
WELCOME_CARD_ID = os.environ.get("WELCOME_CARD_ID", "AAqInYqWzIiu6")

# 智能交互配置
ENABLE_NLU = os.environ.get("ENABLE_NLU", "true").lower() == "true"
INTENT_THRESHOLD = float(os.environ.get("INTENT_THRESHOLD", "0.75"))
LANGS = json.loads(os.environ.get("LANGS", '["zh","en","es"]'))

# 日志与监控
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
METRICS_ENDPOINT = os.environ.get("METRICS_ENDPOINT", "http://localhost:9090/metrics")

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

# 初始化智能交互引擎
smart_engine = SmartInteractionEngine() if ENABLE_NLU else None

# 初始化WebSocket处理器
ws_handler = FeishuWebSocketHandler()

# 注册欢迎卡片处理器
async def welcome_handler_wrapper(event_data):
    """欢迎卡片处理器包装函数"""
    return handle_chat_member_bot_added_event(event_data)

# 消息处理器将在 main() 函数中，handle_user_message 定义后注册

# ---------------------- 工具函数 ----------------------

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

def tenant_token() -> str:
    """获取租户访问令牌"""
    url = f"{FEISHU}/auth/v3/tenant_access_token/internal"
    for attempt in range(1, 4):
        try:
            logger.info("请求租户令牌 (尝试 %d/3)...", attempt)
            r = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            if data.get("code", 0) == 0:
                token = data.get("tenant_access_token", "")
                logger.info("租户令牌获取成功")
                return token
            else:
                logger.error("租户令牌获取失败: %s", data.get("msg", "未知错误"))
        except Exception as e:
            logger.error("租户令牌请求异常 (尝试 %d/3): %s", attempt, e)
            if attempt < 3:
                time.sleep(2 ** attempt)
    return ""

def load_group_config() -> Dict[str, Any]:
    """加载群级配置"""
    if os.path.exists(GROUP_CONFIG_FILE):
        try:
            with open(GROUP_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("加载群级配置失败: %s", e)
    return {
        "push_time": "09:30",
        "file_url": FILE_URL,
        "timezone": TZ_NAME,
        "created_tasks": {}
    }

def save_group_config(config: Dict[str, Any]) -> None:
    """保存群级配置"""
    try:
        with open(GROUP_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("保存群级配置失败: %s", e)

def load_created_tasks() -> Dict[str, bool]:
    """加载已创建任务记录（幂等性）"""
    if os.path.exists(CREATED_TASKS_FILE):
        try:
            with open(CREATED_TASKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("加载已创建任务记录失败: %s", e)
    return {}

def save_created_tasks(tasks: Dict[str, bool]) -> None:
    """保存已创建任务记录"""
    try:
        with open(CREATED_TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("保存已创建任务记录失败: %s", e)

def load_interaction_log() -> Dict[str, Any]:
    """加载交互日志（去重）"""
    if os.path.exists(INTERACTION_LOG_FILE):
        try:
            with open(INTERACTION_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("加载交互日志失败: %s", e)
    return {"interactions": []}

def save_interaction_log(log_data: Dict[str, Any]) -> None:
    """保存交互日志"""
    try:
        with open(INTERACTION_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("保存交互日志失败: %s", e)

def is_duplicate_interaction(user_id: str, task_id: str, action: str, date: str) -> bool:
    """检查是否为重复交互"""
    log_data = load_interaction_log()
    interaction_key = f"{user_id}_{task_id}_{action}_{date}"
    return interaction_key in [item.get("key") for item in log_data.get("interactions", [])]

def load_task_stats() -> Dict[str, Any]:
    """加载任务统计数据"""
    task_stats_file = os.path.join(BASE_DIR, "task_stats.json")
    if os.path.exists(task_stats_file):
        try:
            with open(task_stats_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("加载任务统计失败: %s", e)
    return {
        "current_month": datetime.now(TZ).strftime("%Y-%m"),
        "total_tasks": 0,
        "completed_tasks": 0,
        "completion_rate": 0.0,
        "tasks": {}
    }

def get_task_completion_stats() -> Dict[str, Any]:
    """获取任务完成统计信息（返回统一结构）

    说明：
    - 统一返回包含 total, completed, pending_assignees 等的结构，供卡片/提醒直接使用
    - 包含分专业统计（by_category）
    - 避免因缺少键导致的 KeyError
    """
    try:
        stats = load_task_stats()

        # 基础字段兜底
        current_month = stats.get("current_month") or datetime.now(TZ).strftime("%Y-%m")
        total_tasks = int(stats.get("total_tasks", 0) or 0)
        completed_tasks = int(stats.get("completed_tasks", 0) or 0)
        completion_rate = float(stats.get("completion_rate", 0.0) or 0.0)

        # 计算未完成任务与负责人集合
        pending_assignees_set: set = set()
        tasks_dict = stats.get("tasks") or {}

        # 分专业统计
        category_stats = {}

        for _task_id, task_info in tasks_dict.items():
            # 获取任务分类（如果有的话）
            category = task_info.get("category", "未分类")
            if category not in category_stats:
                category_stats[category] = {"total": 0, "completed": 0}

            category_stats[category]["total"] += 1

            if task_info.get("completed", False):
                category_stats[category]["completed"] += 1
            else:
                # 收集未完成任务的负责人
                for a in task_info.get("assignees", []) or []:
                    if a:
                        pending_assignees_set.add(str(a))

        pending_assignees = list(pending_assignees_set)
        pending_tasks = max(total_tasks - completed_tasks, 0)

        # 返回统一结构
        return {
            "current_month": current_month,
            "total": total_tasks,
            "completed": completed_tasks,
            "completion_rate": completion_rate,
            "pending_tasks": pending_tasks,
            "pending_assignees": pending_assignees,
            "by_category": category_stats
        }

    except Exception as e:
        logger.error("获取任务完成统计异常: %s", e)
        return {
            "current_month": datetime.now(TZ).strftime("%Y-%m"),
            "total": 0,
            "completed": 0,
            "completion_rate": 0.0,
            "pending_tasks": 0,
            "pending_assignees": [],
            "by_category": {}
        }

def record_interaction(user_id: str, task_id: str, action: str, date: str) -> None:
    """记录交互（去重）"""
    log_data = load_interaction_log()
    interaction_key = f"{user_id}_{task_id}_{action}_{date}"
    log_data["interactions"].append({
        "key": interaction_key,
        "user_id": user_id,
        "task_id": task_id,
        "action": action,
        "date": date,
        "timestamp": datetime.now().isoformat()
    })
    # 保留最近7天的记录
    cutoff_date = (datetime.now() - timedelta(days=7)).date().isoformat()
    log_data["interactions"] = [
        item for item in log_data["interactions"] 
        if item["date"] >= cutoff_date
    ]
    save_interaction_log(log_data)

# ---------------------- 任务管理 ----------------------

def load_tasks() -> List[Dict[str, Any]]:
    """加载任务配置"""
    if not os.path.exists(TASKS_FILE):
        logger.error("任务配置文件不存在: %s", TASKS_FILE)
        return []
    
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            tasks = yaml.safe_load(f)
            logger.info("加载任务配置成功，共 %d 项", len(tasks))
            return tasks or []
    except Exception as e:
        logger.error("加载任务配置失败: %s", e)
        return []

def create_tasks_for_month(year: int, month: int) -> Dict[str, Any]:
    """为指定月份创建任务（幂等）"""
    month_key = f"{year:04d}-{month:02d}"
    created_tasks = load_created_tasks()
    
    # 检查是否已创建
    if created_tasks.get(month_key, False):
        logger.info("任务已创建，跳过: %s", month_key)
        return {"status": "skipped", "reason": "already_created"}
    
    tasks = load_tasks()
    token = tenant_token()
    if not token:
        return {"status": "error", "reason": "token_failed"}
    
    success_count = 0
    failed_tasks = []
    
    for task in tasks:
        try:
            # 检查负责人是否存在
            assignee_open_id = task.get("assignee_open_id", "").strip()
            if not assignee_open_id:
                logger.warning("跳过无负责人的任务: %s", task.get("title", "未知"))
                failed_tasks.append({
                    "title": task.get("title", "未知"),
                    "reason": "no_assignee"
                })
                continue
            
            # 创建任务
            result = create_single_task(token, task, year, month)
            if result.get("success"):
                success_count += 1
            else:
                failed_tasks.append({
                    "title": task.get("title", "未知"),
                    "reason": result.get("reason", "unknown")
                })
                
        except Exception as e:
            logger.error("创建任务异常: %s", e)
            failed_tasks.append({
                "title": task.get("title", "未知"),
                "reason": str(e)
            })
    
    # 记录创建状态
    if success_count > 0:
        created_tasks[month_key] = True
        save_created_tasks(created_tasks)
    
    return {
        "status": "success",
        "success_count": success_count,
        "failed_tasks": failed_tasks,
        "month_key": month_key
    }

def create_single_task(token: str, task: Dict[str, Any], year: int, month: int) -> Dict[str, Any]:
    """创建单个任务"""
    try:
        # 生成截止时间（每月23日17:00）
        due_date = datetime(year, month, 23, 17, 0, tzinfo=TZ)
        
        # 构建任务数据
        task_data = {
            "summary": task.get("title", ""),
            "description": task.get("desc", ""),
            "due_time": due_date.isoformat(),
            "assignee_id": task.get("assignee_open_id", ""),
            "collaborator_ids": task.get("collaborators", [])
        }
        
        # 调用飞书API创建任务
        url = f"{FEISHU}/task/v2/tasks"
        headers = {"Authorization": f"Bearer {token}"}
        
        r = requests.post(url, json=task_data, headers=headers, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        
        data = r.json()
        if data.get("code", 0) == 0:
            logger.info("任务创建成功: %s", task.get("title", ""))
            return {"success": True, "task_id": data.get("data", {}).get("task", {}).get("id", "")}
        else:
            logger.error("任务创建失败: %s", data.get("msg", "未知错误"))
            return {"success": False, "reason": data.get("msg", "unknown")}
            
    except Exception as e:
        logger.error("创建任务异常: %s", e)
        return {"success": False, "reason": str(e)}

# ---------------------- 消息发送 ----------------------

def send_card_to_chat(token: str, chat_id: str, card: Dict[str, Any]) -> bool:
    """发送卡片消息到群聊"""
    if not token or not chat_id:
        return False
    
    url = f"{FEISHU}/im/v1/messages"
    params = {"receive_id_type": "chat_id"}
    payload = {
        "receive_id": chat_id,
        "msg_type": "interactive",
        "content": json.dumps(card, ensure_ascii=False)
    }
    
    try:
        r = requests.post(url, params=params, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }, json=payload, timeout=REQUEST_TIMEOUT)
        
        r.raise_for_status()
        data = r.json()
        
        if data.get("code", 0) == 0:
            logger.info("卡片发送成功")
            return True
        else:
            logger.error("卡片发送失败: %s", data.get("msg", "未知错误"))
            return False
            
    except Exception as e:
        logger.error("发送卡片异常: %s", e)
        return False

def send_text_to_chat(token: str, chat_id: str, text: str) -> bool:
    """发送文本消息到群聊"""
    if not token or not chat_id:
        return False
    
    url = f"{FEISHU}/im/v1/messages"
    params = {"receive_id_type": "chat_id"}
    payload = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": text}, ensure_ascii=False)
    }
    
    try:
        r = requests.post(url, params=params, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }, json=payload, timeout=REQUEST_TIMEOUT)
        
        r.raise_for_status()
        data = r.json()
        
        if data.get("code", 0) == 0:
            logger.info("文本发送成功")
            return True
        else:
            logger.error("文本发送失败: %s", data.get("msg", "未知错误"))
            return False
            
    except Exception as e:
        logger.error("发送文本异常: %s", e)
        return False

# ---------------------- 新成员欢迎功能 ----------------------

def send_welcome_card_to_user(token: str, user_id: str) -> bool:
    """向新用户发送欢迎卡片"""
    if not token or not user_id:
        return False
    
    try:
        url = f"{FEISHU}/im/v1/messages"
        params = {"receive_id_type": "user_id"}
        
        # 使用预定义的欢迎卡片ID
        payload = {
            "receive_id": user_id,
            "msg_type": "interactive",
            "content": json.dumps({
                "card_id": WELCOME_CARD_ID
            }, ensure_ascii=False)
        }
        
        r = requests.post(url, params=params, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }, json=payload, timeout=REQUEST_TIMEOUT)
        
        r.raise_for_status()
        data = r.json()
        
        if data.get("code", 0) == 0:
            logger.info("欢迎卡片发送成功，用户ID: %s", user_id)
            return True
        else:
            logger.error("欢迎卡片发送失败: %s", data.get("msg", "未知错误"))
            return False
            
    except Exception as e:
        logger.error("发送欢迎卡片异常: %s", e)
        return False

def handle_chat_member_bot_added_event(event_data: Dict[str, Any]) -> bool:
    """处理新成员进群事件"""
    try:
        logger.info("收到新成员进群事件: %s", event_data)
        
        # 获取token
        token = tenant_token()
        if not token:
            logger.error("无法获取access token")
            return False
        
        # 获取新加入的用户列表
        event = event_data.get("event", {})
        users = event.get("users", [])
        
        if not users:
            logger.warning("新成员进群事件中没有用户信息")
            return False
        
        # 向每个新用户发送欢迎卡片
        success_count = 0
        for user in users:
            user_id = user.get("user_id")
            if user_id:
                if send_welcome_card_to_user(token, user_id):
                    success_count += 1
                    logger.info("成功向用户 %s 发送欢迎卡片", user_id)
                else:
                    logger.error("向用户 %s 发送欢迎卡片失败", user_id)
        
        logger.info("欢迎卡片发送完成，成功: %d/%d", success_count, len(users))
        return success_count > 0
        
    except Exception as e:
        logger.error("处理新成员进群事件异常: %s", e)
        return False

# ---------------------- 用户交互功能 ----------------------

async def reply_to_message(message_id: str, text: str, msg_type: str = "text") -> bool:
    """回复消息"""
    try:
        token = tenant_token()
        if not token:
            logger.error("无法获取token，回复失败")
            return False

        url = f"{FEISHU}/im/v1/messages/{message_id}/reply"

        payload = {
            "msg_type": msg_type,
            "content": json.dumps({"text": text}, ensure_ascii=False)
        }

        r = requests.post(url, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }, json=payload, timeout=REQUEST_TIMEOUT)

        r.raise_for_status()
        data = r.json()

        if data.get("code", 0) == 0:
            logger.info("消息回复成功")
            return True
        else:
            logger.error("消息回复失败: %s", data.get("msg", "未知错误"))
            return False

    except Exception as e:
        logger.error("回复消息异常: %s", e)
        return False


async def handle_mark_completed(user_id: str, message_id: str) -> bool:
    """处理用户标记任务完成"""
    try:
        # 1. 加载任务统计
        stats = load_task_stats()
        tasks_dict = stats.get("tasks", {})

        # 2. 查找用户负责的未完成任务
        user_tasks = []
        for task_id, task_info in tasks_dict.items():
            if not task_info.get("completed", False):
                assignees = task_info.get("assignees", [])
                if user_id in assignees:
                    user_tasks.append({
                        "task_id": task_id,
                        "title": task_info.get("title", "未知任务"),
                        "assignees": assignees
                    })

        # 3. 判断情况
        if not user_tasks:
            await reply_to_message(message_id, "✅ 您负责的任务都已完成，感谢您的辛勤工作！")
            logger.info("用户 %s 没有未完成任务", user_id)
            return True

        # 4. 标记所有任务为完成
        marked_count = 0
        for task in user_tasks:
            # 更新任务状态
            if task["task_id"] in stats["tasks"]:
                stats["tasks"][task["task_id"]]["completed"] = True
                marked_count += 1
                logger.info("标记任务完成: %s (%s)", task["title"], task["task_id"])

        # 5. 重新计算统计
        total = len(stats["tasks"])
        completed_count = sum(1 for t in stats["tasks"].values() if t.get("completed", False))
        stats["completed_tasks"] = completed_count
        stats["completion_rate"] = (completed_count / total * 100) if total > 0 else 0.0

        # 6. 保存更新后的统计数据
        save_task_stats(stats)

        # 7. 重新获取最新统计（使用统一函数）
        updated_stats = get_task_completion_stats()

        # 8. 回复确认消息
        reply_text = f"✅ 已标记 {marked_count} 个任务为完成！\n\n"
        reply_text += f"📊 当前进度:\n"
        reply_text += f"• 总任务: {updated_stats['total']}\n"
        reply_text += f"• 已完成: {updated_stats['completed']}\n"
        reply_text += f"• 完成率: {updated_stats['completion_rate']:.1f}%\n\n"
        reply_text += f"感谢您的辛勤工作！🎉"

        await reply_to_message(message_id, reply_text)

        # 9. 记录交互（去重）
        today = datetime.now(TZ).date().isoformat()
        if not is_duplicate_interaction(user_id, "all", "mark_completed", today):
            record_interaction(user_id, "all", "mark_completed", today)

        logger.info("用户 %s 成功标记 %d 个任务为完成", user_id, marked_count)
        return True

    except Exception as e:
        logger.error("处理标记完成异常: %s", e)
        await reply_to_message(message_id, "❌ 标记失败，请稍后重试或联系管理员")
        return False


async def handle_query_tasks(user_id: str, message_id: str) -> bool:
    """处理查询用户任务"""
    try:
        stats = load_task_stats()
        tasks_dict = stats.get("tasks", {})

        # 查找用户负责的所有任务
        user_tasks = []
        for task_id, task_info in tasks_dict.items():
            assignees = task_info.get("assignees", [])
            if user_id in assignees:
                user_tasks.append({
                    "title": task_info.get("title", "未知任务"),
                    "completed": task_info.get("completed", False)
                })

        if not user_tasks:
            await reply_to_message(message_id, "📝 您当前没有分配的任务")
            return True

        # 分类任务
        completed = [t for t in user_tasks if t["completed"]]
        pending = [t for t in user_tasks if not t["completed"]]

        # 构建回复消息
        reply_text = f"📋 您的任务清单:\n\n"
        reply_text += f"✅ 已完成: {len(completed)}\n"
        reply_text += f"⏳ 未完成: {len(pending)}\n\n"

        if pending:
            reply_text += "**待完成任务:**\n"
            for i, task in enumerate(pending[:8], 1):
                reply_text += f"{i}. {task['title']}\n"
            if len(pending) > 8:
                reply_text += f"\n... 还有 {len(pending) - 8} 个任务未完成\n"

        reply_text += f"\n💡 完成后请回复「已完成」标记任务"

        await reply_to_message(message_id, reply_text)
        return True

    except Exception as e:
        logger.error("处理查询任务异常: %s", e)
        await reply_to_message(message_id, "❌ 查询失败，请稍后重试")
        return False


async def handle_view_progress(message_id: str) -> bool:
    """处理查看进度"""
    try:
        stats = get_task_completion_stats()

        if stats.get("total", 0) == 0:
            await reply_to_message(message_id, "📊 当前没有任务")
            return True

        reply_text = f"📊 月报任务进度 ({stats['current_month']})\n\n"
        reply_text += f"• 总任务数: {stats['total']}\n"
        reply_text += f"• 已完成: {stats['completed']}\n"
        reply_text += f"• 未完成: {stats['pending_tasks']}\n"
        reply_text += f"• 完成率: {stats['completion_rate']:.1f}%\n"

        # 如果有分专业统计
        by_category = stats.get('by_category', {})
        if by_category:
            reply_text += f"\n**分专业进度:**\n"
            for category, cat_stats in by_category.items():
                cat_total = cat_stats.get("total", 0)
                cat_completed = cat_stats.get("completed", 0)
                cat_rate = (cat_completed / cat_total * 100) if cat_total > 0 else 0
                reply_text += f"• {category}: {cat_completed}/{cat_total} ({cat_rate:.0f}%)\n"

        await reply_to_message(message_id, reply_text)
        return True

    except Exception as e:
        logger.error("处理查看进度异常: %s", e)
        await reply_to_message(message_id, "❌ 查询失败，请稍后重试")
        return False


async def handle_user_message(event: Dict[str, Any]) -> bool:
    """处理用户消息（支持@机器人标记完成和智能交互）"""
    try:
        # 1. 提取消息内容
        message = event.get("message", {})
        content_raw = message.get("content", "")
        sender = event.get("sender", {})
        user_id = sender.get("sender_id", {}).get("user_id", "")
        message_id = message.get("message_id", "")

        if not message_id:
            logger.warning("消息没有message_id，跳过处理")
            return True

        # 解析JSON内容
        try:
            content = json.loads(content_raw) if isinstance(content_raw, str) else content_raw
        except:
            content = content_raw if isinstance(content_raw, dict) else {}

        text = content.get("text", "").strip()

        if not text or not user_id:
            logger.info("消息内容为空或无用户ID，跳过处理")
            return True

        logger.info("收到用户消息: user_id=%s, text=%s", user_id, text)

        # 2. 使用智能交互引擎分析意图（如果启用）
        if ENABLE_NLU and smart_engine:
            try:
                intent_result = smart_engine.analyze_intent(text, user_id)
                intent = intent_result.get("intent")
                confidence = intent_result.get("confidence", 0)

                logger.info("意图识别结果: intent=%s, confidence=%.2f", intent, confidence)

                # 3. 处理不同意图
                if intent == "mark_completed" and confidence >= INTENT_THRESHOLD:
                    return await handle_mark_completed(user_id, message_id)

                elif intent == "query_tasks" and confidence >= INTENT_THRESHOLD:
                    return await handle_query_tasks(user_id, message_id)

                elif intent == "view_progress" and confidence >= INTENT_THRESHOLD:
                    return await handle_view_progress(message_id)

                elif intent == "help_setting" and confidence >= INTENT_THRESHOLD:
                    help_text = (
                        "📖 月报机器人使用帮助\n\n"
                        "**可用命令:**\n"
                        "• 已完成 / done - 标记任务完成\n"
                        "• 我的任务 - 查看任务清单\n"
                        "• 进度 / 状态 - 查看整体进度\n"
                        "• 帮助 - 显示此帮助信息\n\n"
                        "💡 提示: 支持中文、英文、西班牙语"
                    )
                    await reply_to_message(message_id, help_text)
                    return True

            except Exception as e:
                logger.error("智能交互引擎处理异常: %s", e)

        # 4. 降级方案：简单关键词匹配
        text_lower = text.lower()

        # 标记完成
        if any(keyword in text_lower for keyword in ["已完成", "完成了", "完成", "done", "completed", "finish"]):
            return await handle_mark_completed(user_id, message_id)

        # 查询任务
        elif any(keyword in text_lower for keyword in ["我的任务", "我的清单", "my task", "mis tareas"]):
            return await handle_query_tasks(user_id, message_id)

        # 查看进度
        elif any(keyword in text_lower for keyword in ["进度", "状态", "完成率", "progress", "status"]):
            return await handle_view_progress(message_id)

        # 帮助
        elif any(keyword in text_lower for keyword in ["帮助", "help", "ayuda"]):
            help_text = (
                "💡 您可以回复:\n"
                "• 已完成 - 标记任务完成\n"
                "• 我的任务 - 查看任务清单\n"
                "• 进度 - 查看整体进度"
            )
            await reply_to_message(message_id, help_text)
            return True

        # 其他：提示可用命令
        else:
            logger.info("未识别的消息: %s", text)
            # 不回复，避免干扰正常聊天

        return True

    except Exception as e:
        logger.error("处理用户消息异常: %s", e)
        return False


def save_task_stats(stats: Dict[str, Any]) -> None:
    """保存任务统计数据"""
    try:
        task_stats_file = os.path.join(BASE_DIR, "task_stats.json")
        with open(task_stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        logger.info("任务统计数据已保存")
    except Exception as e:
        logger.error("保存任务统计数据失败: %s", e)

# ---------------------- 定时任务 ----------------------

def should_create_tasks() -> bool:
    """判断是否应该创建任务（17日09:00 阿根廷时间）"""
    now = datetime.now(TZ)
    current_day = now.day
    current_time = now.strftime("%H:%M")

    return current_day == 17 and current_time == "09:00"

def should_send_daily_reminder() -> bool:
    """判断是否应该发送每日提醒（18-23日09:00）"""
    now = datetime.now(TZ)
    current_day = now.day
    current_time = now.strftime("%H:%M")

    return 18 <= current_day <= 23 and current_time == "09:00"

def should_send_progress_chart() -> bool:
    """判断是否应该发送进度图表（18-22日17:00）"""
    now = datetime.now(TZ)
    current_day = now.day
    current_time = now.strftime("%H:%M")

    return 18 <= current_day <= 22 and current_time == "17:00"

def should_send_final_reminder() -> bool:
    """判断是否应该发送月末催办和统计（23日17:00）"""
    now = datetime.now(TZ)
    current_day = now.day
    current_time = now.strftime("%H:%M")

    return current_day == 23 and current_time == "17:00"

# ---------------------- 主程序逻辑 ----------------------

async def main_loop():
    """主循环"""
    logger.info("启动月报机器人主循环")

    while True:
        try:
            # 检查定时任务
            if should_create_tasks():
                logger.info("执行任务创建（17日09:00）...")
                now = datetime.now(TZ)
                result = create_tasks_for_month(now.year, now.month)
                logger.info("任务创建结果: %s", result)

            elif should_send_daily_reminder():
                logger.info("发送每日任务提醒（18-23日09:00）...")
                token = tenant_token()
                if token:
                    config = load_group_config()
                    card = build_monthly_task_card(config)
                    send_card_to_chat(token, CHAT_ID, card)

            elif should_send_progress_chart():
                logger.info("发送进度图表（18-22日17:00）...")
                token = tenant_token()
                if token:
                    config = load_group_config()
                    # TODO: 实现进度图表卡片
                    stats = get_task_completion_stats()
                    chart_card = build_progress_chart_card(stats)
                    send_card_to_chat(token, CHAT_ID, chart_card)

            elif should_send_final_reminder():
                logger.info("发送月末催办和统计（23日17:00）...")
                token = tenant_token()
                if token:
                    config = load_group_config()
                    card = build_final_reminder_card(config)
                    send_card_to_chat(token, CHAT_ID, card)

            # 等待1分钟
            await asyncio.sleep(60)

        except Exception as e:
            logger.error("主循环异常: %s", e)
            await asyncio.sleep(60)

async def start_websocket_client():
    """启动WebSocket客户端连接到飞书"""
    logger.info("启动WebSocket客户端连接到飞书...")
    
    # 连接到飞书WebSocket服务
    await ws_handler.connect_to_feishu()

async def main():
    """主函数"""
    # 验证环境变量
    errors = validate_env_vars()
    if errors:
        logger.error("环境变量验证失败: %s", errors)
        return

    # 注册用户消息处理器到 WebSocket 处理器
    ws_handler.set_message_handler(handle_user_message)
    logger.info("✅ 用户消息处理器已注册")

    # 启动主循环和WebSocket客户端
    await asyncio.gather(
        main_loop(),
        start_websocket_client()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error("程序异常退出: %s", e)
