#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月报机器人最终版（交互增强） - 在 monthly_report_bot_final 基础上复制并增加消息交互（Echo Bot）
参考官方文档：
- https://open.feishu.cn/document/develop-an-echo-bot/introduction
- https://open.feishu.cn/document/develop-an-echo-bot/development-steps
- https://open.feishu.cn/document/develop-an-echo-bot/faq
- https://open.feishu.cn/document/develop-an-echo-bot/explanation-of-example-code
"""

from __future__ import annotations
import os, sys, time, json, math, datetime, logging, re
import tempfile
from typing import Dict, List, Tuple, Optional, Any
import re as _re_cached  # 局部预编译正则所用
import argparse
import yaml, pytz
import asyncio
from datetime import datetime, timedelta

# 导入飞书官方SDK
try:
    import lark_oapi as lark
    from lark_oapi.api.im.v1 import *
    from lark_oapi.api.task.v2 import *
    from lark_oapi.api.task.v2.model import *
except Exception as _import_error:
    lark = None  # 允许在未安装 SDK 时导入本模块以运行纯函数测试

# 引入WS包装器（内部用长轮询模拟以接入事件）
try:
    from app.ws_wrapper import create_ws_handler
except ModuleNotFoundError:
    import pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent / "app"))
    from ws_wrapper import create_ws_handler

# 引入图表生成器
try:
    from chart_generator import chart_generator
except ImportError:
    chart_generator = None

try:
    from ai_intent import classify_intent, intent_to_command
except ImportError:
    classify_intent = None
    intent_to_command = None

VERSION = "1.3.1-interactive"

# ---------------------- 基础配置 ----------------------

# 强制设置标准输出编码为 UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    except Exception:
        pass

print("="*60)
print("月报机器人 v1.3 交互增强版 - 核心功能 + Echo")
print("Python 版本:", sys.version)
print("当前工作目录:", os.getcwd())
print("="*60)

# 环境变量（与 monthly_report_bot_final 保持一致）
APP_ID     = os.environ.get("APP_ID", "").strip()
APP_SECRET = os.environ.get("APP_SECRET", "").strip()
CHAT_ID    = os.environ.get("CHAT_ID", "").strip()
FILE_URL   = os.environ.get("FILE_URL", "").strip()
TZ_NAME    = os.environ.get("TZ", "America/Argentina/Buenos_Aires").strip()
TZ         = pytz.timezone(TZ_NAME)
USE_OFFICIAL_WS = os.environ.get("USE_OFFICIAL_WS", "true").lower() == "true"
AI_INTENT_ENABLED = os.environ.get("AI_INTENT_ENABLED", "true").lower() == "true"

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
        logging.FileHandler("monthly_report_bot_final.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# 过滤飞书SDK推送但未注册处理器的 application.* 事件噪声（降级并丢弃原错误）
class _LarkProcessorNotFoundFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = str(record.getMessage())
        except Exception:
            msg = str(record.msg)
        if "processor not found" in msg and "application." in msg:
            # 降级为信息日志并丢弃原始错误日志
            logging.getLogger(__name__).info("忽略未注册的应用事件: %s", msg)
            return False
        return True

# 将过滤器挂到 root logger，作用于所有下游日志
logging.getLogger().addFilter(_LarkProcessorNotFoundFilter())

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

async def check_task_status_from_feishu(task_id: str) -> bool:
    """从飞书API检查任务实际完成状态"""
    try:
        if not lark_client:
            logger.warning("飞书客户端未初始化，无法检查任务状态")
            return False
        
        request = GetTaskRequest.builder() \
            .task_guid(task_id) \
            .build()
        
        response = await lark_client.task.v2.task.aget(request)
        
        if response.success():
            task = response.data.task
            is_completed = task.complete == 2
            logger.info("任务状态检查: %s -> %s", task_id, "已完成" if is_completed else "进行中")
            return is_completed
        else:
            logger.warning("查询任务状态失败: %s, code: %s", task_id, response.code)
            return False
            
    except Exception as e:
        logger.error("检查任务状态异常: %s, task_id: %s", e, task_id)
        return False

async def complete_task_on_feishu(task_id: str) -> bool:
    """调用飞书API将任务标记为完成（设置completed_at时间戳）"""
    try:
        if not lark_client:
            logger.warning("飞书客户端未初始化，无法完成任务")
            return False

        # 使用 PatchTaskRequest 更新任务，设置 completed_at 时间戳
        # completed_at 不为空表示任务已完成
        completed_timestamp = str(int(datetime.now(TZ).timestamp() * 1000))

        request = PatchTaskRequest.builder() \
            .task_guid(task_id) \
            .request_body(InputTask.builder()
                        .completed_at(completed_timestamp)
                        .build()) \
            .build()

        response = await lark_client.task.v2.task.apatch(request)

        if response.success():
            logger.info("✅ 飞书任务已标记完成: %s", task_id)
            return True
        else:
            logger.warning("❌ 飞书任务完成失败: %s, code: %s, msg: %s", task_id, response.code, response.msg)
            return False

    except Exception as e:
        logger.error("飞书任务完成异常: %s, task_id: %s", e, task_id)
        return False

def update_task_completion(task_id: str, task_title: str, assignees: List[str], completed: bool = True, task_type: str = "月报") -> None:
    """更新任务完成状态"""
    try:
        stats = load_task_stats()
        current_month = datetime.now(TZ).strftime("%Y-%m")

        if stats["current_month"] != current_month:
            stats = {
                "current_month": current_month,
                "tasks": {},
                "total_tasks": 0,
                "completed_tasks": 0,
                "completion_rate": 0.0,
                "last_update": datetime.now(TZ).isoformat()
            }

        if task_id not in stats["tasks"]:
            stats["tasks"][task_id] = {
                "title": task_title,
                "assignees": assignees,
                "task_type": task_type,
                "created_at": datetime.now(TZ).isoformat(),
                "completed": False,
                "completed_at": None
            }
            stats["total_tasks"] += 1
        
        if completed and not stats["tasks"][task_id]["completed"]:
            stats["tasks"][task_id]["completed"] = True
            stats["tasks"][task_id]["completed_at"] = datetime.now(TZ).isoformat()
            stats["completed_tasks"] += 1
        
        if stats["total_tasks"] > 0:
            stats["completion_rate"] = round(stats["completed_tasks"] / stats["total_tasks"] * 100, 2)
        
        save_task_stats(stats)
        logger.info("任务完成状态更新: %s -> %s", task_title, "已完成" if completed else "未完成")
        
    except Exception as e:
        logger.error("更新任务完成状态失败: %s", e)

async def sync_task_completion_status() -> None:
    """同步所有任务的完成状态（从飞书API获取真实状态）"""
    try:
        stats = load_task_stats()
        if not stats["tasks"]:
            logger.info("没有任务需要同步状态")
            return
        
        logger.info("开始同步任务完成状态...")
        updated_count = 0
        
        for task_id, task_info in stats["tasks"].items():
            try:
                is_completed = await check_task_status_from_feishu(task_id)
                if is_completed != task_info["completed"]:
                    if is_completed:
                        stats["tasks"][task_id]["completed"] = True
                        stats["tasks"][task_id]["completed_at"] = datetime.now(TZ).isoformat()
                        logger.info("任务标记为已完成: %s", task_info["title"])
                    else:
                        if task_info["completed"]:
                            logger.info("保留本地已完成状态，不因远端未完成/查询失败而降级: %s", task_info["title"])
                            continue
                        stats["tasks"][task_id]["completed"] = False
                        stats["tasks"][task_id]["completed_at"] = None
                        logger.info("任务保持未完成: %s", task_info["title"])
                    updated_count += 1
            except Exception as e:
                logger.error("同步任务状态失败: %s, task_id: %s", e, task_id)
        
        stats["total_tasks"] = len(stats["tasks"])
        stats["completed_tasks"] = sum(1 for task in stats["tasks"].values() if task.get("completed", False))
        if stats["total_tasks"] > 0:
            stats["completion_rate"] = round(stats["completed_tasks"] / stats["total_tasks"] * 100, 2)
        else:
            stats["completion_rate"] = 0.0
        
        if updated_count > 0:
            save_task_stats(stats)
            logger.info("任务状态同步完成，更新了 %d 个任务", updated_count)
        else:
            logger.info("任务状态同步完成，无需更新")
            
    except Exception as e:
        logger.error("同步任务完成状态失败: %s", e)

def get_task_completion_stats() -> Dict[str, Any]:
    """获取任务完成统计"""
    try:
        stats = load_task_stats()
        current_month = datetime.now(TZ).strftime("%Y-%m")
        
        if stats["current_month"] != current_month:
            return {
                "current_month": current_month,
                "total_tasks": 0,
                "completed_tasks": 0,
                "completion_rate": 0.0,
                "pending_tasks": 0,
                "pending_assignees": [],
                "tasks": {}
            }
        
        pending_tasks = stats["total_tasks"] - stats["completed_tasks"]
        
        pending_assignees = []
        for task_id, task_info in stats["tasks"].items():
            if not task_info["completed"]:
                pending_assignees.extend(task_info["assignees"])
        pending_assignees = list(set(pending_assignees))
        
        # 按任务类型分组统计
        type_stats: Dict[str, Any] = {}
        for task_info in stats["tasks"].values():
            ttype = task_info.get("task_type", "月报")
            if ttype not in type_stats:
                type_stats[ttype] = {"total": 0, "completed": 0, "pending_assignees": []}
            type_stats[ttype]["total"] += 1
            if task_info["completed"]:
                type_stats[ttype]["completed"] += 1
            else:
                type_stats[ttype]["pending_assignees"].extend(task_info["assignees"])
        for ttype, ts in type_stats.items():
            ts["pending"] = ts["total"] - ts["completed"]
            ts["completion_rate"] = round(ts["completed"] / ts["total"] * 100, 2) if ts["total"] > 0 else 0.0
            ts["pending_assignees"] = list(set(ts["pending_assignees"]))

        return {
            "current_month": stats["current_month"],
            "total_tasks": stats["total_tasks"],
            "completed_tasks": stats["completed_tasks"],
            "completion_rate": stats["completion_rate"],
            "pending_tasks": pending_tasks,
            "pending_assignees": pending_assignees,
            "type_stats": type_stats,
            "tasks": stats.get("tasks", {})
        }

    except Exception as e:
        logger.error("获取任务完成统计失败: %s", e)
        return {
            "current_month": datetime.now(TZ).strftime("%Y-%m"),
            "total_tasks": 0,
            "completed_tasks": 0,
            "completion_rate": 0.0,
            "pending_tasks": 0,
            "pending_assignees": [],
            "type_stats": {},
            "tasks": {}
        }

def get_pending_tasks_detail(task_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """获取未完成任务的详细信息，可按任务类型过滤"""
    try:
        stats = load_task_stats()
        pending_tasks = []

        for task_id, task_info in stats["tasks"].items():
            if not task_info["completed"]:
                if task_type is None or task_info.get("task_type", "月报") == task_type:
                    pending_tasks.append({
                        "task_id": task_id,
                        "title": task_info["title"],
                        "assignees": task_info["assignees"],
                        "task_type": task_info.get("task_type", "月报")
                    })

        return pending_tasks

    except Exception as e:
        logger.error("获取未完成任务详情失败: %s", e)
        return []

def get_completed_assignees_summary() -> Dict[str, int]:
    """获取已完成任务的人员统计（每个人完成了多少个任务）"""
    try:
        stats = load_task_stats()
        completed_counts = {}

        for task_id, task_info in stats["tasks"].items():
            if task_info["completed"]:
                for assignee in task_info["assignees"]:
                    completed_counts[assignee] = completed_counts.get(assignee, 0) + 1

        return completed_counts

    except Exception as e:
        logger.error("获取已完成人员统计失败: %s", e)
        return {}

# ---------------------- 用户信息映射 ----------------------

USER_ID_MAPPING = {
    "ou_0d2f73fe7a911e049d051f2de23f9289": "马富凡",
    "ou_03491624846d90ea22fa64177860a8cf": "刘智辉",
    "ou_7552fdb195c3ad2c0453258fb157c12a": "成自飞",
    "ou_145eca14d330bb8162c45536538d6764": "王继军",
    "ou_e1c26a62aed90bc5b879ba4d244adb75": "熊黄平",
    "ou_b792a42b4ebbae74be98e8e5f28659ca": "景晓东",
    "ou_2f93cb9407ca5a281a92d1f5a72fdf7b": "唐进",
    "ou_e8b3904bb4e9ebe4b8e039b88faa6db4": "范明杰",
    "ou_a9c22d7a23ff6dd0e3dc1a93b2763b5a": "张文康",
    "ou_12e764a007cd597d9f03922f8f7c8c2e": "蒲星宇",
    "ou_f22b36450dd631f8def2ccadc07235d7": "何寨",
    "ou_e8d10f3f8106f5c5ca9d864f90782f51": "袁阿虎",
    "ou_b843712f1d1622d5038a034df9d7f33a": "魏荣荣",
    "ou_5199fde738bcaedd5fcf4555b0adf7a0": "孙建敏",
    "ou_74c2c34207adb95db789b2f9fe4bc2bf": "齐书红",
    "ou_5b1673a24607bec4fbcbc74b8572e774": "杨强",
    "ou_ada0f1ebc2d334bec7685f3c1545fe5d": "刘野",  # 修正ID 2025-03
    "ou_5ad999af75b598dac3a05c773800d2bc": "孟洪武",
    "ou_1e008e4217c7283055ce817d3cdf9682": "王明毅",
    "ou_9be94cf6a100dbaf2030070c184050ca": "王紫阳",
    "ou_6436b107b7acc310c230bc19161679b5": "李洪蛟",
    "ou_49299becc523c8d3aa1120261f1e2bcd": "李炤",
    "ou_05bf998a0c033635dcabbde130ab2021": "何庆平",
    "ou_3a123c0b19f5fcde8e9832da17a79144": "张德勇",
    "ou_10f155c6f2b8717cb81de959908c0a43": "王涛",
    "ou_0bbd2f698a7cc385b5eb67c584ad497f": "李新明",
    "ou_a348100295a01cd7cfa597a16211c805": "李怡慧",
    "ou_9847326a1fea8db87079101775bd97a9": "王冠群",
    "ou_31b587d7ca13d371a0d5b798ebb475fe": "钟飞宏",
    "ou_b54c036f6aca80c566157e951b2aa7ea": "闵国政",
    "ou_d1eb2de82f6609f7e5e001508587f32b": "高雅慧",
    "ou_621143d2374d7bb3693a179a15a227b6": "袁龙",  # 新增用户 2025-11-18
    "ou_5ca06c62f2854b2bc0947e83fc85bf96": "屈超",  # 修正ID 2025-03
    "ou_e8face5de9cc109f67f385ec3fced158": "季宗军",  # 新增用户 2025-03
    "ou_b709bc9bad1bbaf2edbcc95f5138e3c3": "吴中甫",  # 新增用户 2025-03
    "ou_6c3e3989442de940036939a732f0e658": "张随",
    "ou_e32b70d3b2dcab3b77d043650f2ecbad": "田致维",
}

def get_user_display_name(user_id: str) -> str:
    """获取用户显示名称"""
    return USER_ID_MAPPING.get(user_id, f"用户({user_id[:8]}...)")

def format_assignees_display(assignees: List[str]) -> str:
    """格式化负责人显示"""
    if not assignees:
        return "**待分配**"
    
    display_names = []
    for assignee in assignees:
        display_name = get_user_display_name(assignee)
        display_names.append(f"<at user_id=\"{assignee}\">{display_name}</at>")
    
    return " ".join(display_names)

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

def build_task_creation_card() -> Dict:
    """构建任务创建卡片"""
    stats = get_task_completion_stats()
    
    all_tasks = []
    task_stats = load_task_stats()
    for task_id, task_info in task_stats["tasks"].items():
        all_tasks.append({
            "title": task_info["title"],
            "assignees": task_info["assignees"]
        })
    
    task_list_text = ""
    for i, task in enumerate(all_tasks, 1):
        assignee_mentions = ""
        if task["assignees"]:
            for assignee in task["assignees"]:
                display_name = get_user_display_name(assignee)  # 获取显示名称
                assignee_mentions += f"<at user_id=\"{assignee}\">{display_name}</at> "
        else:
            assignee_mentions = "**待分配**"

        task_list_text += f"{i:2d}. **{task['title']}**\n    👤 负责人: {assignee_mentions}\n\n"
    
    return {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "📋 月度报告任务已创建"
            },
            "template": "blue"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**本月报告任务已创建完成！**\n\n📊 **任务统计**:\n• 总任务数: {stats['total_tasks']}\n• 待完成: {stats['pending_tasks']}\n\n📝 **任务详情**:\n{task_list_text}\n请各位负责人及时完成分配的任务。"
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

def _build_type_summary(stats: Dict) -> str:
    """生成双主线分类统计文字，插入卡片正文"""
    ts = stats.get("type_stats", {})
    yb = ts.get("月报", {})
    zdxm = ts.get("重大项目月报", {})
    parts = []
    if yb:
        parts.append(f"  📌 月报: {yb.get('completed',0)}/{yb.get('total',0)} ({yb.get('completion_rate',0)}%)")
    if zdxm:
        parts.append(f"  📌 公司重大项目月报: {zdxm.get('completed',0)}/{zdxm.get('total',0)} ({zdxm.get('completion_rate',0)}%)")
    return ("\n" + "\n".join(parts)) if parts else ""


def build_daily_reminder_card() -> Dict:
    """构建每日提醒卡片"""
    stats = get_task_completion_stats()
    pending_tasks = get_pending_tasks_detail()
    
    mention_text = ""
    if stats['pending_assignees']:
        mention_text = "\n\n**未完成任务的负责人：**\n"
        for assignee in stats['pending_assignees']:
            display_name = get_user_display_name(assignee)
            mention_text += f"<at user_id=\"{assignee}\">{display_name}</at> "
    
    task_list = ""
    if pending_tasks:
        task_list = "\n\n**未完成任务详情：**\n"
        for i, task in enumerate(pending_tasks[:8], 1):
            assignee_mentions = format_assignees_display(task["assignees"])
            task_list += f"{i}. **{task['title']}**\n    👤 负责人: {assignee_mentions}\n\n"
        if len(pending_tasks) > 8:
            task_list += f"... 还有 {len(pending_tasks) - 8} 个任务未完成\n"
    
    return {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "📅 每日任务提醒"
            },
            "template": "orange"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**月度报告任务进度提醒**\n\n📊 **当前进度**:\n• 总任务数: {stats['total_tasks']}\n• 已完成: {stats['completed_tasks']}\n• 待完成: {stats['pending_tasks']}\n• 完成率: {stats['completion_rate']}%{_build_type_summary(stats)}{mention_text}{task_list}\n\n请未完成任务的负责人尽快处理！"
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

def build_final_reminder_card() -> Dict:
    """构建最终催办卡片"""
    stats = get_task_completion_stats()
    pending_tasks = get_pending_tasks_detail()
    
    mention_text = ""
    if stats['pending_assignees']:
        mention_text = "\n\n**⚠️ 紧急催办 - 未完成任务的负责人：**\n"
        for assignee in stats['pending_assignees']:
            display_name = get_user_display_name(assignee)
            mention_text += f"<at user_id=\"{assignee}\">{display_name}</at> "
    
    task_list = ""
    if pending_tasks:
        task_list = "\n\n**未完成任务详情：**\n"
        for i, task in enumerate(pending_tasks, 1):
            assignee_mentions = format_assignees_display(task["assignees"])
            task_list += f"{i}. **{task['title']}**\n    👤 负责人: {assignee_mentions}\n\n"
    
    return {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "🚨 最终催办"
            },
            "template": "red"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**月度报告截止日期临近！**\n\n📊 **当前进度**:\n• 总任务数: {stats['total_tasks']}\n• 已完成: {stats['completed_tasks']}\n• 待完成: {stats['pending_tasks']}\n• 完成率: {stats['completion_rate']}%{_build_type_summary(stats)}{mention_text}{task_list}\n\n🚨 **请立即完成剩余任务！**"
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

def build_daily_stats_card(stats: Dict) -> Dict:
    """构建每日统计卡片（18-23日 17:00）"""
    if not stats:
        stats = get_task_completion_stats()

    progress_width = min(int(stats['completion_rate'] / 10), 10)
    progress_bar = "█" * progress_width + "░" * (10 - progress_width)

    if stats['completion_rate'] >= 100:
        summary = "🎉 **今日所有任务已完成！**"
    elif stats['completion_rate'] >= 80:
        summary = "✅ **今日完成情况良好！**"
    elif stats['completion_rate'] >= 60:
        summary = "⚠️ **今日完成情况一般！**"
    else:
        summary = "❌ **今日完成情况需改进！**"

    return {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "📊 今日完成情况统计"
            },
            "template": "blue"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**{stats['current_month']} 月报任务进展**\n\n{summary}\n\n📈 **完成情况**:\n• 总任务数: {stats['total_tasks']}\n• 已完成: {stats['completed_tasks']}\n• 未完成: {stats['pending_tasks']}\n• 完成率: {stats['completion_rate']}%{_build_type_summary(stats)}\n\n📊 **进度条**:\n`{progress_bar}` {stats['completion_rate']}%\n\n⏰ 统计时间: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')}\n\n💡 **提示**: 图表将随后发送"
                }
            }
        ]
    }

def build_final_stats_card() -> Dict:
    """构建最终统计卡片"""
    stats = get_task_completion_stats()
    
    progress_width = min(int(stats['completion_rate'] / 10), 10)
    progress_bar = "█" * progress_width + "░" * (10 - progress_width)
    
    if stats['completion_rate'] >= 100:
        summary = "🎉 **恭喜！所有任务已完成！**"
    elif stats['completion_rate'] >= 80:
        summary = "✅ **任务完成情况良好！**"
    elif stats['completion_rate'] >= 60:
        summary = "⚠️ **任务完成情况一般，需要关注！**"
    else:
        summary = "❌ **任务完成情况较差，需要改进！**"
    
    # 尝试生成图表
    chart_info = ""
    if chart_generator and stats.get('total_tasks', 0) > 0:
        try:
            chart_path = chart_generator.generate_comprehensive_dashboard(stats)
            if chart_path and os.path.exists(chart_path):
                chart_info = f"\n\n📊 **可视化统计**: 已生成综合仪表板图表"
        except Exception as e:
            logger.error(f"生成统计卡片图表失败: {e}")
    
    return {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "📊 月度报告最终统计"
            },
            "template": "green"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**{stats['current_month']} 月度报告完成情况**\n\n{summary}\n\n📈 **完成情况**:\n• 总任务数: {stats['total_tasks']}\n• 已完成: {stats['completed_tasks']}\n• 未完成: {stats['pending_tasks']}\n• 完成率: {stats['completion_rate']}%{_build_type_summary(stats)}\n\n📊 **进度条**:\n`{progress_bar}` {stats['completion_rate']}%{chart_info}\n\n⏰ 统计时间: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')}"
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
                    },
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "📊 图表统计"
                        },
                        "type": "primary",
                        "url": "https://open.feishu.cn"
                    }
                ]
            }
        ]
    }

# ---------------------- 消息发送函数 ----------------------

async def send_card_to_chat(card: Dict) -> bool:
    """发送卡片到群聊"""
    try:
        request = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(CreateMessageRequestBody.builder()
                        .receive_id(CHAT_ID)
                        .msg_type("interactive")
                        .content(json.dumps(card, ensure_ascii=False))
                        .build()) \
            .build()
        
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

async def send_image_to_chat(image_path: str, title: str = "图片") -> bool:
    """发送图片到群聊（作为卡片形式）"""
    try:
        # 上传图片获取 image_key
        image_key = await upload_image(image_path)

        if not image_key:
            logger.error("图片上传失败，无法发送")
            return False

        # 构建包含图片的卡片
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "img",
                    "img_key": image_key,
                    "alt": {
                        "tag": "plain_text",
                        "content": title
                    }
                }
            ]
        }

        # 发送卡片
        return await send_card_to_chat(card)

    except Exception as e:
        logger.error("发送图片异常: %s", e)
        return False

# ---------------------- 交互增强：回帖与Echo ----------------------

async def reply_to_message(message_id: str, content: str, msg_type: str = "text") -> bool:
    """回复指定消息（官方SDK areply），默认文本回帖，按需支持卡片"""
    try:
        if not lark_client:
            logger.error("客户端未初始化，无法发送消息")
            return False

        if msg_type == "text":
            body = ReplyMessageRequestBody.builder() \
                .msg_type("text") \
                .content(json.dumps({"text": content}, ensure_ascii=False)) \
                .build()
        else:
            body = ReplyMessageRequestBody.builder() \
                .msg_type("interactive") \
                .content(json.dumps(content, ensure_ascii=False)) \
                .build()

        request = ReplyMessageRequest.builder() \
            .message_id(message_id) \
            .request_body(body) \
            .build()

        response = await lark_client.im.v1.message.areply(request)
        if response.code == 0 or getattr(response, "success", lambda: False)():
            logger.info("消息回复成功: %s", str(content)[:50])
            return True
        logger.error("消息回复失败: code=%s, msg=%s", getattr(response, "code", "?"), getattr(response, "msg", "?"))
        return False
    except Exception as e:
        logger.error("回复消息异常: %s", e)
        return False

async def upload_image(image_path: str) -> Optional[str]:
    """上传图片到飞书，返回image_key"""
    import io
    try:
        if not os.path.exists(image_path):
            logger.error("图片文件不存在: %s", image_path)
            return None

        # 读取图片文件为字节数据
        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        # 使用 BytesIO 包装字节数据，模拟文件对象
        image_file = io.BytesIO(image_bytes)
        image_file.name = os.path.basename(image_path)

        # 构建请求
        request = CreateImageRequest.builder() \
            .request_body(CreateImageRequestBody.builder()
                        .image_type("message")
                        .image(image_file)
                        .build()) \
            .build()

        # 上传图片
        response = await lark_client.im.v1.image.acreate(request)

        if response.success():
            image_key = response.data.image_key
            logger.info("图片上传成功, image_key: %s", image_key)
            return image_key
        else:
            logger.error("图片上传失败, code: %s, msg: %s", response.code, response.msg)
            return None

    except Exception as e:
        import traceback
        logger.error("上传图片异常: %s", e)
        logger.error("异常堆栈: %s", traceback.format_exc())
        return None

_RE_AT_RICH = _re_cached.compile(r"<at\b[^>]*?>.*?</at>", _re_cached.IGNORECASE)
_RE_AT_PLAIN = _re_cached.compile(r"(^|\s)@\S+")
_RE_SPACES = _re_cached.compile(r"\s+")

def _sanitize_command_text(text: str) -> str:
    """去除@提及与多余空白，标准化指令匹配文本（小写）。
    兼容两类@格式：
    1) 纯文本例如 "@_user_1 帮助"
    2) 富文本例如 "<at user_id=\"ou_xxx\">周超</at> 帮助"
    """
    if text is None:
        return ""
    s = str(text)
    # 去除富文本@标签
    s = _RE_AT_RICH.sub(" ", s)
    # 去除纯文本@标记（前导位置或多处，统一清理）
    s = _RE_AT_PLAIN.sub(" ", s)
    # 规范空白
    s = _RE_SPACES.sub(" ", s).strip()
    return s.lower()


_DIRECT_COMMAND_TEXTS = {
    "/help", "help", "?", "帮助", "命令", "功能", "说明",
    "状态", "进度", "统计", "完成率", "进展", "完成情况", "status", "progress", "summary",
    "未完成", "谁没交", "谁未交", "谁未提交", "未提交", "没交", "未上交", "还有谁",
    "任务列表", "列表", "pending", "todo",
    "我的任务", "我的待办", "我负责的任务", "my tasks", "my task", "mine",
    "文件", "链接", "地址", "月报", "月报链接", "报告", "文档", "表格", "模板", "模板地址",
    "file", "link",
    "截止", "截止时间", "时间", "时间安排", "提醒", "什么时候", "deadline", "schedule", "plan", "计划",
    "图表", "可视化", "饼图", "统计图", "图表统计", "chart", "visualization", "pie", "dashboard",
    "已完成", "完成了", "完成", "我完成", "done", "我完成了", "标记完成", "提交了", "完成啦",
}


def _resolve_command_text_with_ai(text: str, normalized: str) -> str:
    """Use AI only for free-form text; exact commands stay local and deterministic."""
    if normalized in _DIRECT_COMMAND_TEXTS:
        return normalized
    if not AI_INTENT_ENABLED or classify_intent is None or intent_to_command is None:
        return normalized

    try:
        intent_result = classify_intent(text)
        command = intent_to_command(intent_result)
        if command:
            logger.info(
                "AI intent matched: text=%r intent=%s confidence=%s command=%s",
                text,
                intent_result.get("intent"),
                intent_result.get("confidence"),
                command,
            )
            return _sanitize_command_text(command)
    except Exception as e:
        logger.warning("AI intent fallback to keyword matching: %s", e)
    return normalized


def generate_echo_reply(text: str) -> str:
    """根据输入文本生成回声/帮助回复（可单元测试）"""
    normalized = _sanitize_command_text(text)
    if normalized in {"/help", "help", "?", "帮助", "命令", "功能", "说明", "帮助一下", "怎么用"}:
        return (
            "📋 **月报机器人帮助**\n\n"
            "🔍 **查询功能：**\n"
            "• 状态/进度/统计 - 查看全部任务完成情况\n"
            "• 月报进度 - 查看月报主线（23条）完成情况\n"
            "• 公司重大项目进度 - 查看公司重大项目月报主线（37条）完成情况\n"
            "• 未完成/任务列表 - 查看待完成任务详情\n"
            "• 图表/可视化 - 生成美观的统计图表\n\n"
            "📎 **其他功能：**\n"
            "• 文件/链接 - 获取月报文件地址\n"
            "• 截止/时间 - 查看时间安排\n"
            "• 已完成/完成了 - 标记任务完成\n\n"
            "💡 **提示：** 直接发送问题，我会尽力帮助您！"
        )

    # 月报主线进度
    if normalized in {"月报进度", "月报状态", "月报统计", "月报完成情况"}:
        stats = get_task_completion_stats()
        ts = stats.get("type_stats", {}).get("月报", {})
        if not ts:
            return "📊 月报任务尚未创建"
        lines = [
            f"📊 月报进度（{stats['current_month']}）",
            f"- 总任务数: {ts['total']}",
            f"- 已完成: {ts['completed']}",
            f"- 待完成: {ts['pending']}",
            f"- 完成率: {ts['completion_rate']}%",
        ]
        return "\n".join(lines)

    # 公司重大项目月报主线进度
    if normalized in {"公司重大项目进度", "重大项目进度", "公司重大项目月报进度", "重大项目状态", "重大项目统计", "重大项目月报进度"}:
        stats = get_task_completion_stats()
        ts = stats.get("type_stats", {}).get("重大项目月报", {})
        if not ts:
            return "📊 公司重大项目月报任务尚未创建"
        lines = [
            f"📊 公司重大项目月报进度（{stats['current_month']}）",
            f"- 总任务数: {ts['total']}",
            f"- 已完成: {ts['completed']}",
            f"- 待完成: {ts['pending']}",
            f"- 完成率: {ts['completion_rate']}%",
        ]
        return "\n".join(lines)

    # 状态/统计（全部）
    if normalized in {"状态", "进度", "统计", "完成率", "进展", "完成情况", "总进度", "全部进度", "status", "progress", "summary"}:
        # 未创建任务（当月）→ 直接提示无任务
        try:
            created = load_created_tasks()
            current_month = datetime.now(TZ).strftime("%Y-%m")
            if not created.get(current_month, False):
                return "当前没有任务"
        except Exception:
            pass
        stats = get_task_completion_stats()
        lines = [
            f"📊 当前进度（{stats['current_month']}）",
            f"- 总任务数: {stats['total_tasks']}",
            f"- 已完成: {stats['completed_tasks']}",
            f"- 待完成: {stats['pending_tasks']}",
            f"- 完成率: {stats['completion_rate']}%",
        ]

        # 添加已完成人员统计
        completed_summary = get_completed_assignees_summary()
        if completed_summary:
            lines.append("\n✅ 已完成人员:")
            for assignee_id, count in sorted(completed_summary.items(), key=lambda x: x[1], reverse=True):
                display_name = get_user_display_name(assignee_id)
                lines.append(f"   • {display_name}: {count}个任务")

        lines.append("\n👉 查看未完成任务请发送『未完成』或『谁没交』")
        lines.append("📈 发送『图表』或『可视化』查看美观的统计图表")
        return "\n".join(lines)

    # 未完成任务列表
    if normalized in {"未完成", "谁没交", "谁未交", "谁未提交", "未提交", "没交", "未上交", "还有谁", "任务列表", "列表", "pending", "todo"}:
        # 未创建任务（当月）→ 直接提示无任务
        try:
            created = load_created_tasks()
            current_month = datetime.now(TZ).strftime("%Y-%m")
            if not created.get(current_month, False):
                return "当前没有任务"
        except Exception:
            pass
        tasks = get_pending_tasks_detail()
        if not tasks:
            stats0 = get_task_completion_stats()
            if stats0.get("total_tasks", 0) == 0:
                return "当前没有任务"
            return "👏 当前没有未完成任务！"
        limit = 8
        out = [f"📝 未完成任务（前{min(limit, len(tasks))}个）"]
        for i, task in enumerate(tasks[:limit], 1):
            assignees = task.get("assignees") or []
            names = [get_user_display_name(a) for a in assignees]
            name_text = "、".join(names) if names else "待分配"
            out.append(f"{i}. {task['title']} | 负责人: {name_text}")
        if len(tasks) > limit:
            out.append(f"... 还有 {len(tasks) - limit} 个任务未完成")
        return "\n".join(out)

    # 文件/链接
    if normalized in {"文件", "链接", "地址", "月报", "月报链接", "报告", "文档", "表格", "模板", "模板地址", "file", "link"}:
        return f"📎 月报文件链接：{FILE_URL}"

    # 时间安排/截止
    if normalized in {"截止", "截止时间", "时间", "时间安排", "提醒", "什么时候", "deadline", "schedule", "plan", "计划"}:
        return (
            "⏰ 时间安排\n\n"
            "- 17日 09:30：创建当月任务\n"
            "- 18-23日 09:30：发送每日提醒（@未完成负责人）\n"
            "- 18-23日 17:00：发送统计卡片+图表\n"
            "- 23日 17:00：发送最终催办和统计"
        )

    # 已完成/完成了（提示操作方式）
    if normalized in {"已完成", "完成了", "完成", "我完成", "done", "我完成了", "标记完成", "提交了", "完成啦"}:
        return "感谢您的辛勤工作，祝您工作愉快，后续将不再催办"

    # 默认回复：人性化的帮助提示
    friendly_responses = [
        f"👋 您好！我是月报收集助手。\n\n您刚才说的是「{text[:20]}{'...' if len(text) > 20 else ''}」，我暂时还不太理解呢。\n\n💡 试试以下命令吧：\n• 发送「帮助」查看所有功能\n• 发送「进度」查看任务完成情况\n• 发送「图表」查看可视化统计\n• 发送「任务列表」查看未完成任务",
        f"🤔 抱歉，我还不太明白「{text[:20]}{'...' if len(text) > 20 else ''}」是什么意思。\n\n您可以：\n• 输入「帮助」了解我能做什么\n• 输入「进度」查看当前完成情况\n• 输入「图表」查看美观的统计图表",
        f"😊 收到您的消息「{text[:20]}{'...' if len(text) > 20 else ''}」。\n\n我是月报机器人，专门帮助大家跟踪月报任务进度！\n\n🔍 常用命令：\n• 帮助 - 查看所有功能\n• 进度 - 查看完成情况\n• 图表 - 查看可视化数据"
    ]

    # 根据文本长度选择回复样式
    import hashlib
    text_hash = int(hashlib.md5(text.encode()).hexdigest(), 16)
    response_index = text_hash % len(friendly_responses)

    return friendly_responses[response_index]

def generate_chart_response() -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """生成图表响应，返回 (chart_path, stats) 元组"""
    try:
        # 检查是否有任务数据
        created = load_created_tasks()
        current_month = datetime.now(TZ).strftime("%Y-%m")
        if not created.get(current_month, False):
            return None, None

        stats = get_task_completion_stats()
        if stats.get('total_tasks', 0) == 0:
            return None, None

        # 检查图表生成器是否可用
        if chart_generator is None:
            return None, None

        # 生成图表
        chart_path = chart_generator.generate_comprehensive_dashboard(stats)

        if chart_path and os.path.exists(chart_path):
            return chart_path, stats
        else:
            return None, None

    except Exception as e:
        logger.error(f"生成图表响应失败: {e}")
        return None, None

async def mark_user_tasks_completed(user_id: str) -> Tuple[int, List[str]]:
    """
    标记某个用户的所有未完成任务为已完成（本地+飞书API）

    Args:
        user_id: 用户的 open_id

    Returns:
        (完成任务数, 任务标题列表)
    """
    try:
        logger.info("[DEBUG] mark_user_tasks_completed called for user_id=%s", user_id)
        stats = load_task_stats()
        if not stats or "tasks" not in stats:
            logger.info("[DEBUG] No stats or tasks found, returning 0")
            return 0, []

        current_month = datetime.now(TZ).strftime("%Y-%m")
        completed_count = 0
        completed_titles = []
        tasks_to_complete = []  # 收集需要完成的任务

        logger.info("[DEBUG] Processing %d tasks for user_id=%s", len(stats.get("tasks", {})), user_id)

        # 第一步：找出该用户所有未完成的任务
        for task_id, task_info in stats["tasks"].items():
            assignees = task_info.get("assignees", [])
            if user_id in assignees and not task_info.get("completed", False):
                tasks_to_complete.append((task_id, task_info))

        # 第二步：逐个完成任务（本地+飞书API）
        for task_id, task_info in tasks_to_complete:
            # 调用飞书API将任务标记为完成
            feishu_success = await complete_task_on_feishu(task_id)

            if feishu_success:
                # 飞书API成功后，更新本地状态
                task_info["completed"] = True
                task_info["completed_at"] = datetime.now(TZ).isoformat()
                completed_count += 1
                completed_titles.append(task_info.get("title", task_id))
                logger.info(f"✅ 任务已完成（本地+飞书）: {task_info.get('title')} (user: {user_id})")
            else:
                # 飞书API失败，仍然更新本地状态（保证用户体验）
                task_info["completed"] = True
                task_info["completed_at"] = datetime.now(TZ).isoformat()
                completed_count += 1
                completed_titles.append(task_info.get("title", task_id))
                logger.warning(f"⚠️ 任务本地已完成，但飞书API失败: {task_info.get('title')} (user: {user_id})")

        if completed_count > 0:
            # 更新统计数据
            total_completed = sum(1 for t in stats["tasks"].values() if t.get("completed", False))
            total_tasks = len(stats["tasks"])
            stats["completed_tasks"] = total_completed
            stats["completion_rate"] = round((total_completed / total_tasks) * 100, 2) if total_tasks > 0 else 0
            stats["last_update"] = datetime.now(TZ).isoformat()

            # 保存更新后的数据
            save_task_stats(stats)
            logger.info(f"已为用户 {user_id} 标记 {completed_count} 个任务为完成")

        return completed_count, completed_titles

    except Exception as e:
        logger.error(f"标记用户任务完成失败: {e}", exc_info=True)
        return 0, []

async def handle_message_event(event: Dict[str, Any]) -> bool:
    """处理消息事件（im.message.receive_v1）：支持"状态/未完成/谁没交"等意图与无任务判断"""
    try:
        message = event.get("message", {})
        sender = event.get("sender", {})
        sender_id_obj = sender.get("sender_id", {})
        user_open_id = sender_id_obj.get("open_id", "") or sender_id_obj.get("user_id", "")

        content_raw = message.get("content", "")
        content: Dict[str, Any] = {}
        if isinstance(content_raw, str):
            try:
                content = json.loads(content_raw)
            except Exception:
                content = {}
        elif isinstance(content_raw, dict):
            content = content_raw

        text = (content.get("text", "") or "").strip()
        message_id = message.get("message_id", "")
        if not text or not message_id:
            return True

        normalized = _sanitize_command_text(text)
        normalized = _resolve_command_text_with_ai(text, normalized)
        logger.info("[DEBUG] Message from user %s: text=%r, normalized=%r", user_open_id, text, normalized)

        # 我的任务 -> 只显示当前用户未完成任务
        if normalized in {"我的任务", "我的待办", "我负责的任务", "my tasks", "my task", "mine"}:
            if not user_open_id:
                await reply_to_message(message_id, "无法识别您的飞书用户身份，请联系管理员检查事件配置。")
                return True

            tasks = [
                task
                for task in get_pending_tasks_detail()
                if user_open_id in (task.get("assignees") or [])
            ]
            if not tasks:
                await reply_to_message(message_id, "您当前没有未完成任务。")
                return True

            out = [f"📝 我的未完成任务（{len(tasks)}个）"]
            for i, task in enumerate(tasks[:8], 1):
                out.append(f"{i}. {task['title']}")
            if len(tasks) > 8:
                out.append(f"... 还有 {len(tasks) - 8} 个任务未显示")
            await reply_to_message(message_id, "\n".join(out))
            return True

        # 未完成/谁没交 → 若当月未创建任务则直接回复“当前没有任务”
        if normalized in {"未完成", "谁没交", "还有谁", "任务列表", "列表", "pending", "todo"}:
            try:
                created = load_created_tasks()
                current_month = datetime.now(TZ).strftime("%Y-%m")
                if not created.get(current_month, False):
                    await reply_to_message(message_id, "当前没有任务")
                    return True
            except Exception:
                pass
            tasks = get_pending_tasks_detail()
            if not tasks:
                stats0 = get_task_completion_stats()
                if stats0.get("total_tasks", 0) == 0:
                    await reply_to_message(message_id, "当前没有任务")
                else:
                    await reply_to_message(message_id, "👏 当前没有未完成任务！")
                return True
            out = ["📝 未完成任务（前8个）"]
            for i, task in enumerate(tasks[:8], 1):
                names = [get_user_display_name(a) for a in (task.get("assignees") or [])]
                name_text = "、".join(names) if names else "待分配"
                out.append(f"{i}. {task['title']} | 负责人: {name_text}")
            if len(tasks) > 8:
                out.append(f"... 还有 {len(tasks) - 8} 个任务未完成")
            await reply_to_message(message_id, "\n".join(out))
            return True

        # 状态/进度/统计 → 若当月未创建任务则直接回复"当前没有任务"
        if normalized in {"状态", "进度", "统计", "完成率", "status", "progress", "summary"}:
            try:
                created = load_created_tasks()
                current_month = datetime.now(TZ).strftime("%Y-%m")
                if not created.get(current_month, False):
                    await reply_to_message(message_id, "当前没有任务")
                    return True
            except Exception:
                pass
            stats = get_task_completion_stats()
            lines = [
                f"📊 当前进度（{stats['current_month']}）",
                f"- 总任务数: {stats['total_tasks']}",
                f"- 已完成: {stats['completed_tasks']}",
                f"- 待完成: {stats['pending_tasks']}",
                f"- 完成率: {stats['completion_rate']}%",
            ]

            # 添加已完成人员统计
            completed_summary = get_completed_assignees_summary()
            if completed_summary:
                lines.append("\n✅ 已完成人员:")
                for assignee_id, count in sorted(completed_summary.items(), key=lambda x: x[1], reverse=True):
                    display_name = get_user_display_name(assignee_id)
                    lines.append(f"   • {display_name}: {count}个任务")

            await reply_to_message(message_id, "\n".join(lines))
            return True

        # 图表/可视化统计
        if normalized in {"图表", "可视化", "饼图", "统计图", "图表统计", "chart", "visualization", "pie", "dashboard"}:
            try:
                created = load_created_tasks()
                current_month = datetime.now(TZ).strftime("%Y-%m")
                if not created.get(current_month, False):
                    await reply_to_message(message_id, "当前没有任务，无法生成图表")
                    return True
            except Exception:
                pass

            chart_path, stats = generate_chart_response()

            if chart_path and stats:
                # 上传图表
                image_key = await upload_image(chart_path)

                if image_key:
                    # 构建包含图片的卡片消息
                    card_content = {
                        "config": {
                            "wide_screen_mode": True
                        },
                        "header": {
                            "title": {
                                "tag": "plain_text",
                                "content": "📊 任务统计图表"
                            },
                            "template": "blue"
                        },
                        "elements": [
                            {
                                "tag": "div",
                                "text": {
                                    "tag": "lark_md",
                                    "content": (
                                        f"**{stats['current_month']} 月度任务进度**\n\n"
                                        f"📈 **统计数据**:\n"
                                        f"• 总任务数: {stats['total_tasks']}\n"
                                        f"• 已完成: {stats['completed_tasks']}\n"
                                        f"• 待完成: {stats['pending_tasks']}\n"
                                        f"• 完成率: {stats['completion_rate']}%"
                                    )
                                }
                            },
                            {
                                "tag": "img",
                                "img_key": image_key,
                                "alt": {
                                    "tag": "plain_text",
                                    "content": "任务统计图表"
                                }
                            },
                            {
                                "tag": "div",
                                "text": {
                                    "tag": "lark_md",
                                    "content": "📊 **上图为综合统计仪表板**，包含任务完成情况、完成率、任务数量对比、已完成人员排行榜等多维度分析"
                                }
                            }
                        ]
                    }
                    await reply_to_message(message_id, card_content, msg_type="interactive")
                else:
                    # 图片上传失败，返回文本信息
                    await reply_to_message(
                        message_id,
                        f"📊 统计图表已生成，但上传失败\n\n"
                        f"📈 当前进度（{stats['current_month']}）:\n"
                        f"- 总任务数: {stats['total_tasks']}\n"
                        f"- 已完成: {stats['completed_tasks']}\n"
                        f"- 待完成: {stats['pending_tasks']}\n"
                        f"- 完成率: {stats['completion_rate']}%"
                    )
            else:
                # 图表生成失败
                error_msg = "图表功能暂不可用，请检查依赖库安装" if chart_generator is None else "图表生成失败，请稍后重试"
                await reply_to_message(message_id, error_msg)

            return True

        # 已完成/完成了 - 自动标记用户的任务为完成
        if normalized in {"已完成", "完成了", "完成", "我完成", "done", "我完成了", "标记完成", "提交了", "完成啦"}:
            logger.info("[DEBUG] '已完成' command matched! user_open_id=%s", user_open_id)
            if user_open_id:
                # 标记该用户的所有未完成任务为已完成（本地+飞书API）
                logger.info("[DEBUG] Calling mark_user_tasks_completed for user_open_id=%s", user_open_id)
                completed_count, completed_titles = await mark_user_tasks_completed(user_open_id)

                if completed_count > 0:
                    # 构建回复消息
                    user_name = get_user_display_name(user_open_id)
                    reply_lines = [
                        f"✅ 太棒了！已为您自动标记以下任务为完成：",
                        ""
                    ]
                    for i, title in enumerate(completed_titles, 1):
                        reply_lines.append(f"{i}. {title}")

                    # 获取最新统计
                    stats = get_task_completion_stats()
                    reply_lines.extend([
                        "",
                        f"📊 **最新进度**:",
                        f"• 已完成: {stats['completed_tasks']}/{stats['total_tasks']}",
                        f"• 完成率: {stats['completion_rate']}%",
                        "",
                        "🎉 感谢您的辛勤工作！后续将不再催办这些任务。"
                    ])

                    await reply_to_message(message_id, "\n".join(reply_lines))
                else:
                    await reply_to_message(message_id, "您当前没有未完成的任务，或者任务已经标记为完成了。")
            else:
                await reply_to_message(message_id, "感谢您的辛勤工作！请联系管理员手动标记任务完成。")

            return True

        # 其它：回声/帮助等
        reply_text = generate_echo_reply(text)
        await reply_to_message(message_id, reply_text, msg_type="text")
        return True
    except Exception as e:
        logger.error("处理消息事件异常: %s", e)
        return False

# ---------------------- 官方WS事件接入（可选） ----------------------

def _build_event_from_p2(data: Any) -> Dict[str, Any]:
    """将 lark_oapi 的 P2ImMessageReceiveV1 转为通用事件字典，供 handle_message_event 复用"""
    try:
        msg = getattr(getattr(data, "event", None), "message", None)
        sender = getattr(getattr(data, "event", None), "sender", None)
        content_raw = getattr(msg, "content", "")
        message_id = getattr(msg, "message_id", "")
        chat_id = getattr(msg, "chat_id", "")
        # sender_id 兼容 user_id/open_id
        user_id = ""
        if sender is not None:
            sender_id = getattr(sender, "sender_id", None)
            if sender_id is not None:
                user_id = getattr(sender_id, "user_id", "") or getattr(sender_id, "open_id", "")
        # 输出与 webhook 事件尽可能一致的结构
        event_dict = {
            "message": {
                "content": content_raw,
                "message_id": message_id,
                "chat_id": chat_id,
            },
            "sender": {
                "sender_id": {
                    "user_id": user_id,
                }
            }
        }
        return event_dict
    except Exception:
        return {"message": {"content": "", "message_id": "", "chat_id": ""}}

async def _run_official_ws(loop: asyncio.AbstractEventLoop) -> None:
    """在后台线程启动官方WS客户端，收到消息事件时转发到当前事件循环"""
    if not (lark and hasattr(lark, "ws")):
        logger.warning("官方WS不可用，跳过WS启动")
        return
    
    def _start_ws():
        try:
            # 构建事件分发器
            handler_builder = lark.EventDispatcherHandler.builder("", "")
            
            def _on_p2_message(data):
                try:
                    # 仅当事件循环仍在运行时才调度协程，避免在关闭后创建未等待的协程
                    if loop.is_closed() or not loop.is_running():
                        logger.warning("事件循环已关闭/未运行，丢弃P2消息事件")
                        return
                    ev = _build_event_from_p2(data)
                    coro = handle_message_event(ev)
                    fut = asyncio.run_coroutine_threadsafe(coro, loop)
                    # 捕获协程内部异常，避免静默失败
                    def _log_future_result(f):
                        try:
                            _ = f.result()
                        except Exception as ex2:
                            logger.error("P2消息事件处理异常: %s", ex2)
                    fut.add_done_callback(_log_future_result)
                except Exception as ex:
                    logger.error("转发P2消息事件失败: %s", ex)
            
            handler = handler_builder.register_p2_im_message_receive_v1(_on_p2_message).build()
            logger.info("已注册官方WS消息事件处理器")
            
            client = lark.ws.Client(APP_ID, APP_SECRET, event_handler=handler, log_level=lark.LogLevel.INFO)
            logger.info("开始建立官方WS长连接...")
            client.start()
        except Exception as e:
            logger.error("官方WS启动失败: %s", e)
    
    # 在后台线程运行阻塞的 WS 客户端
    await asyncio.to_thread(_start_ws)

# ---------------------- 定时任务 ----------------------

def should_create_tasks(now: Optional[datetime] = None) -> bool:
    """判断是否应该创建任务（17日09:30）"""
    if now is None:
        now = datetime.now(TZ)
    current_day = now.day
    current_time = now.strftime("%H:%M")

    return current_day == 17 and current_time == "09:30"

def should_send_daily_reminder(now: Optional[datetime] = None) -> bool:
    """判断是否应该发送每日提醒（18-23日09:30，@未完成负责人）"""
    if now is None:
        now = datetime.now(TZ)
    current_day = now.day
    current_time = now.strftime("%H:%M")

    return 18 <= current_day <= 23 and current_time == "09:30"

def should_send_daily_stats(now: Optional[datetime] = None) -> bool:
    """判断是否应该发送每日统计（18-23日17:00，统计完成情况+图表展示）"""
    if now is None:
        now = datetime.now(TZ)
    current_day = now.day
    current_time = now.strftime("%H:%M")

    return 18 <= current_day <= 23 and current_time == "17:00"

def should_send_final_reminder(now: Optional[datetime] = None) -> bool:
    """判断是否应该发送最终催办（23日17:00）"""
    if now is None:
        now = datetime.now(TZ)
    current_day = now.day
    current_time = now.strftime("%H:%M")

    return current_day == 23 and current_time == "17:00"

def should_send_final_stats(now: Optional[datetime] = None) -> bool:
    """判断是否应该发送最终统计（23日17:00）"""
    if now is None:
        now = datetime.now(TZ)
    current_day = now.day
    current_time = now.strftime("%H:%M")

    return current_day == 23 and current_time == "17:00"

# ---------------------- 主程序逻辑 ----------------------

async def main_loop():
    """主循环：保留原定时能力"""
    logger.info("启动月报机器人主循环（交互增强版）")
    
    while True:
        try:
            now = datetime.now(TZ)
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            logger.info("当前时间: %s", now_str)
            
            if should_create_tasks(now):
                logger.info("执行任务创建...")
                success = await create_tasks()
                if success:
                    card = build_task_creation_card()
                    await send_card_to_chat(card)
                else:
                    await send_text_to_chat("❌ 任务创建失败，请检查配置")
            
            elif should_send_daily_reminder(now):
                logger.info("发送每日提醒（09:30）...")
                await sync_task_completion_status()
                card = build_daily_reminder_card()
                await send_card_to_chat(card)

            elif should_send_daily_stats(now):
                logger.info("发送每日统计（17:00，完成情况+图表）...")
                await sync_task_completion_status()
                # 发送统计卡片
                stats = load_task_stats()
                card = build_daily_stats_card(stats)
                await send_card_to_chat(card)
                # 生成并发送图表
                try:
                    from chart_generator import chart_generator
                    chart_path = chart_generator.generate_comprehensive_dashboard(stats)
                    await send_image_to_chat(chart_path, "📊 今日完成情况统计图表")
                except Exception as e:
                    logger.error(f"生成图表失败: {e}")

            elif should_send_final_reminder(now):
                logger.info("发送最终催办...")
                await sync_task_completion_status()
                card = build_final_reminder_card()
                await send_card_to_chat(card)
            
            elif should_send_final_stats(now):
                logger.info("发送最终统计...")
                await sync_task_completion_status()
                card = build_final_stats_card()
                await send_card_to_chat(card)
            
            elif now.minute == 0:
                logger.info("执行定时任务状态同步...")
                await sync_task_completion_status()
            
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error("主循环异常: %s", e)
            await asyncio.sleep(60)

async def create_tasks() -> bool:
    """创建月度报告任务（真实调用飞书API）"""
    try:
        created_tasks = load_created_tasks()
        current_month = datetime.now(TZ).strftime("%Y-%m")

        if created_tasks.get(current_month, False):
            logger.info("本月任务已创建，跳过")
            return True

        if not os.path.exists(TASKS_FILE):
            logger.error("任务配置文件不存在: %s", TASKS_FILE)
            return False

        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            tasks_config = yaml.safe_load(f)

        if isinstance(tasks_config, dict) and 'tasks' in tasks_config:
            task_list = tasks_config['tasks']
        elif isinstance(tasks_config, list):
            task_list = tasks_config
        else:
            logger.error("任务配置文件格式错误: 需为列表或包含 tasks 键的字典")
            return False

        logger.info("开始创建月度报告任务（调用飞书API）...")
        success_count = 0

        for i, task_config in enumerate(task_list):
            try:
                # 构建任务标题
                task_title = f"{current_month} {task_config['title']}"

                # 获取负责人列表
                assignees = []
                if task_config.get('assignee_open_id'):
                    if isinstance(task_config['assignee_open_id'], list):
                        assignees = task_config['assignee_open_id']
                    else:
                        assignees = [task_config['assignee_open_id']]

                # 过滤空值
                assignees = [a for a in assignees if a and a.strip()]

                # 计算截止时间（23号 23:59:59）
                deadline = datetime.now(TZ).replace(day=23, hour=23, minute=59, second=59)
                # 飞书Task v2 API需要毫秒级时间戳（乘以1000）
                due_timestamp = int(deadline.timestamp() * 1000)

                # 准备任务成员（在创建时直接分配）
                members_list = []
                if assignees:
                    for assignee_id in assignees:
                        member = Member.builder() \
                            .id(assignee_id) \
                            .role("assignee") \
                            .build()
                        members_list.append(member)

                # 创建任务请求（使用正确的API类名）
                request = CreateTaskRequest.builder() \
                    .request_body(InputTask.builder()
                                .summary(task_title)
                                .description(f"月度报告任务: {task_config['title']}\n文档链接: {task_config.get('doc_url', '')}")
                                .due(Due.builder()
                                    .timestamp(str(due_timestamp))
                                    .is_all_day(False)
                                    .build())
                                .members(members_list)  # 直接在创建时分配成员
                                .build()) \
                    .build()

                response = await lark_client.task.v2.task.acreate(request)

                if response.success():
                    task_guid = response.data.task.guid
                    logger.info("✅ 任务创建成功: %s (GUID: %s)", task_title, task_guid)

                    if assignees:
                        logger.info("✅ 任务分配成功: %s -> %s", task_title, assignees)

                    # 更新统计（使用真实的 task_guid）
                    update_task_completion(task_guid, task_config['title'], assignees, False,
                                           task_type=task_config.get('task_type', '月报'))
                    success_count += 1

                else:
                    logger.error("❌ 任务创建失败: %s, code: %s, msg: %s",
                               task_title, response.code, response.msg)

            except Exception as e:
                logger.error("❌ 创建任务异常: %s, 任务: %s", e, task_config.get('title', 'Unknown'))

        if success_count > 0:
            created_tasks[current_month] = True
            save_created_tasks(created_tasks)
            logger.info("✅ 本月任务创建完成，成功创建 %d 个任务", success_count)
            return True
        else:
            logger.error("❌ 没有成功创建任何任务")
            return False

    except Exception as e:
        logger.error("❌ 创建任务异常: %s", e)
        return False

# ---------------------- 任务记录文件 ----------------------

def load_created_tasks() -> Dict[str, bool]:
    try:
        if os.path.exists(CREATED_TASKS_FILE):
            with open(CREATED_TASKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error("加载任务记录失败: %s", e)
        return {}

def save_created_tasks(tasks: Dict[str, bool]) -> None:
    try:
        with open(CREATED_TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("保存任务记录失败: %s", e)

# ---------------------- 启动入口 ----------------------

async def main():
    """主函数：初始化SDK + 并行运行交互与定时"""
    errors = validate_env_vars()
    if errors:
        logger.error("环境变量验证失败: %s", errors)
        return
    
    logger.info("环境变量验证通过")
    logger.info("APP_ID: %s", APP_ID)
    logger.info("CHAT_ID: %s", CHAT_ID)
    logger.info("WELCOME_CARD_ID: %s", WELCOME_CARD_ID)
    logger.info("SDK版本: lark-oapi")
    
    if not init_lark_client():
        logger.error("飞书SDK客户端初始化失败，程序退出")
        return
    
    # 发送启动通知
    await send_text_to_chat("🚀 月报机器人最终版（交互增强）已启动，支持 Echo 回声与定时任务...")
    
    tasks = []
    
    if USE_OFFICIAL_WS and (lark and hasattr(lark, "ws")):
        # 官方WS（可用则优先）
        logger.info("尝试启动官方WS长连接...")
        tasks.append(asyncio.create_task(_run_official_ws(asyncio.get_running_loop())))
    else:
        # 当官方WS不可用或显式关闭时，自动回退到包装器（长轮询）
        if USE_OFFICIAL_WS and not (lark and hasattr(lark, "ws")):
            logger.warning("官方WS不可用，自动回退到长轮询模式")
    handler = create_ws_handler()
    if hasattr(handler, "register_event_handler"):
        handler.register_event_handler("im.message.receive_v1", handle_message_event)
        logger.info("已注册消息事件处理器（Echo）")
        tasks.append(asyncio.create_task(handler.connect_to_feishu()))
    
    # 定时循环
    tasks.append(asyncio.create_task(main_loop()))
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error("程序异常退出: %s", e)


