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

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    # 尝试从当前目录和脚本目录加载 .env 文件
    load_dotenv()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_file = os.path.join(script_dir, '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
except ImportError:
    # 如果没有安装 python-dotenv，跳过（适用于通过 systemd 环境变量传递的情况）
    pass

# 导入飞书官方SDK
try:
    import lark_oapi as lark
    from lark_oapi.api.im.v1 import *
    from lark_oapi.api.task.v2 import *
    from lark_oapi.api.task.v2.model import *
    # lark-oapi SDK 导入成功，可用于消息发送等功能
    # 注意：不使用飞书 Task API，而是通过卡片消息实现任务管理
except Exception as _import_error:
    import logging as _log
    _log.error(f"导入飞书SDK失败: {_import_error}")
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

# ---------------------- 消息发送辅助函数 ----------------------

async def send_text_to_chat(text: str) -> bool:
    """发送文本消息到群聊"""
    try:
        if not lark_client:
            logger.error("飞书客户端未初始化")
            return False
        
        request = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(CreateMessageRequestBody.builder()
                         .receive_id(CHAT_ID)
                         .msg_type("text")
                         .content(json.dumps({"text": text}, ensure_ascii=False))
                         .build()) \
            .build()
        
        response = lark_client.im.v1.message.create(request)
        
        if response.success():
            logger.info("文本消息发送成功: %s", text[:50])
            return True
        else:
            logger.error("文本消息发送失败: %s", response.msg)
            return False
            
    except Exception as e:
        logger.error("发送文本消息异常: %s", e)
        return False

async def send_card_to_chat(card_content: Dict) -> bool:
    """发送卡片消息到群聊"""
    try:
        if not lark_client:
            logger.error("飞书客户端未初始化")
            return False
        
        request = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(CreateMessageRequestBody.builder()
                         .receive_id(CHAT_ID)
                         .msg_type("interactive")
                         .content(json.dumps(card_content, ensure_ascii=False))
                         .build()) \
            .build()
        
        response = lark_client.im.v1.message.create(request)
        
        if response.success():
            logger.info("卡片消息发送成功")
            return True
        else:
            logger.error("卡片消息发送失败: %s", response.msg)
            return False
            
    except Exception as e:
        logger.error("发送卡片消息异常: %s", e)
        return False

# ---------------------- 任务创建与管理 ----------------------

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

async def create_monthly_tasks() -> bool:
    """创建当月任务（发送卡片消息到群聊）"""
    try:
        current_month = datetime.now(TZ).strftime("%Y-%m")
        created_tasks = load_created_tasks()
        
        # 检查是否已创建
        if created_tasks.get(current_month, False):
            logger.info("本月任务已创建，跳过: %s", current_month)
            return True
        
        # 加载任务配置
        tasks = load_tasks()
        if not tasks:
            logger.warning("没有任务配置，跳过创建")
            return False
        
        logger.info("开始创建任务，共 %d 项", len(tasks))
        
        success_count = 0
        failed_tasks = []
        
        # 发送开始消息
        await send_text_to_chat(f"🚀 开始创建 {current_month} 月报任务...")
        
        for i, task_config in enumerate(tasks, 1):
            try:
                # 获取任务信息
                title = task_config.get("title", "")
                desc = task_config.get("desc", "")
                doc_url = task_config.get("doc_url", FILE_URL)
                assignee_open_id = task_config.get("assignee_open_id", "").strip()
                
                if not assignee_open_id:
                    logger.warning("跳过无负责人的任务: %s", title)
                    failed_tasks.append(title)
                    continue
                
                # 创建任务卡片
                card_content = {
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "content": f"📋 **{title}**",
                                "tag": "lark_md"
                            }
                        },
                        {
                            "tag": "div",
                            "text": {
                                "content": f"👤 负责人: <at id=\"{assignee_open_id}\"></at>",
                                "tag": "lark_md"
                            }
                        },
                        {
                            "tag": "div",
                            "text": {
                                "content": f"📄 [查看文档]({doc_url})",
                                "tag": "lark_md"
                            }
                        },
                        {
                            "tag": "div",
                            "text": {
                                "content": "💡 完成后请在群聊中回复「已完成」来标记任务完成",
                                "tag": "lark_md"
                            }
                        }
                    ],
                    "header": {
                        "title": {
                            "content": f"{current_month} 月报任务",
                            "tag": "plain_text"
                        }
                    }
                }
                
                # 发送任务卡片到群聊
                if await send_card_to_chat(card_content):
                    success_count += 1
                    logger.info("任务创建成功 [%d/%d]: %s", i, len(tasks), title)
                    
                    # 更新任务统计（使用标题作为任务ID）
                    task_id = f"{current_month}_{title}"
                    update_task_completion(
                        task_id=task_id,
                        task_title=title,
                        assignees=[assignee_open_id],
                        completed=False
                    )
                else:
                    logger.error("任务创建失败 [%d/%d]: %s", i, len(tasks), title)
                    failed_tasks.append(title)
                
                # 避免发送过快
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error("创建任务异常 [%d/%d]: %s - %s", i, len(tasks), title, str(e))
                failed_tasks.append(title)
        
        # 记录创建状态
        if success_count > 0:
            created_tasks[current_month] = True
            save_created_tasks(created_tasks)
            logger.info("任务创建完成: %s, 成功 %d/%d", current_month, success_count, len(tasks))
        
        # 发送结果消息
        result_msg = f"✅ {current_month} 月报任务创建完成\n"
        result_msg += f"- 成功: {success_count}/{len(tasks)}\n"
        if failed_tasks:
            result_msg += f"- 失败: {len(failed_tasks)}\n"
            result_msg += "\n失败的任务:\n"
            for task in failed_tasks[:5]:  # 只显示前5个
                result_msg += f"  • {task}\n"
        
        await send_text_to_chat(result_msg)
        
        return success_count > 0
        
    except Exception as e:
        logger.error("创建月度任务异常: %s", e)
        await send_text_to_chat(f"❌ 任务创建失败: {str(e)}")
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

def update_task_completion(task_id: str, task_title: str, assignees: List[str], completed: bool = True) -> None:
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
                        stats["completed_tasks"] += 1
                        logger.info("任务标记为已完成: %s", task_info["title"])
                    else:
                        if task_info["completed"]:
                            stats["completed_tasks"] -= 1
                        stats["tasks"][task_id]["completed"] = False
                        stats["tasks"][task_id]["completed_at"] = None
                        logger.info("任务标记为未完成: %s", task_info["title"])
                    updated_count += 1
            except Exception as e:
                logger.error("同步任务状态失败: %s, task_id: %s", e, task_id)

        if stats["total_tasks"] > 0:
            stats["completion_rate"] = round(stats["completed_tasks"] / stats["total_tasks"] * 100, 2)

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
                "pending_assignees": []
            }

        pending_tasks = stats["total_tasks"] - stats["completed_tasks"]

        pending_assignees = []
        for task_id, task_info in stats["tasks"].items():
            if not task_info["completed"]:
                pending_assignees.extend(task_info["assignees"])
        pending_assignees = list(set(pending_assignees))

        return {
            "current_month": stats["current_month"],
            "total_tasks": stats["total_tasks"],
            "completed_tasks": stats["completed_tasks"],
            "completion_rate": stats["completion_rate"],
            "pending_tasks": pending_tasks,
            "pending_assignees": pending_assignees
        }

    except Exception as e:
        logger.error("获取任务完成统计失败: %s", e)
        return {
            "current_month": datetime.now(TZ).strftime("%Y-%m"),
            "total_tasks": 0,
            "completed_tasks": 0,
            "completion_rate": 0.0,
            "pending_tasks": 0,
            "pending_assignees": []
        }

def get_pending_tasks_detail() -> List[Dict[str, Any]]:
    """获取未完成任务的详细信息"""
    try:
        stats = load_task_stats()
        pending_tasks = []

        for task_id, task_info in stats["tasks"].items():
            if not task_info["completed"]:
                pending_tasks.append({
                    "task_id": task_id,
                    "title": task_info["title"],
                    "assignees": task_info["assignees"]
                })

        return pending_tasks

    except Exception as e:
        logger.error("获取未完成任务详情失败: %s", e)
        return []

# ---------------------- 用户信息映射 ----------------------

USER_ID_MAPPING = {
    "ou_17b6bee82dd946d92a322cc7dea40eb7": "马富凡",
    "ou_03491624846d90ea22fa64177860a8cf": "刘智辉",
    "ou_7552fdb195c3ad2c0453258fb157c12a": "成自飞",
    "ou_145eca14d330bb8162c45536538d6764": "王继军",
    "ou_0bbab538833c35081e8f5c3ef213e17e": "熊黄平",
    "ou_f5338c49049621c36310e2215204d0be": "景晓东",
    "ou_2f93cb9407ca5a281a92d1f5a72fdf7b": "唐进",
    "ou_07443a67428d8741eab5eac851b754b9": "范明杰",
    "ou_a9c22d7a23ff6dd0e3dc1a93b2763b5a": "张文康",
    "ou_66ef2e056d0425ac560717a8b80395c3": "蒲星宇",
    "ou_d85dd7bb7625ab3e3f8b129e54934aea": "何寨",
    "ou_3b14801caa065a0074c7d6db8603f288": "袁阿虎",
    "ou_b843712f1d1622d5038a034df9d7f33a": "魏荣荣",
    "ou_5199fde738bcaedd5fcf4555b0adf7a0": "孙建敏",
    "ou_22703f0c3bdb25b39de2b34d9605b8a9": "齐书红",
    "ou_5b1673a24607bec4fbcbc74b8572e774": "杨强",
    "ou_b96c7ed4a604dc049569102d01c6c26d": "刘野",
    "ou_5ad999af75b598dac3a05c773800d2bc": "孟洪武",
    "ou_1e008e4217c7283055ce817d3cdf9682": "王明毅",
    "ou_9be94cf6a100dbaf2030070c184050ca": "王紫阳",
    "ou_c9d7859417eb0344b310fcff095fa639": "李洪蛟",
    "ou_49299becc523c8d3aa1120261f1e2bcd": "李炤",
    "ou_05bf998a0c033635dcabbde130ab2021": "何庆平",
    "ou_3a123c0b19f5fcde8e9832da17a79144": "张德勇",
    "ou_10f155c6f2b8717cb81de959908c0a43": "王涛",
    "ou_0bbd2f698a7cc385b5eb67c584ad497f": "李新明",
    "ou_a348100295a01cd7cfa597a16211c805": "李怡慧",
    "ou_9847326a1fea8db87079101775bd97a9": "王冠群",
    "ou_31b587d7ca13d371a0d5b798ebb475fe": "钟飞宏",
    "ou_50c492f1d2b2ee2107c4e28ab4416732": "闵国政",
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
                assignee_mentions += f"<at user_id=\"{assignee}\"></at> "
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
                    "content": f"**月度报告任务进度提醒**\n\n📊 **当前进度**:\n• 总任务数: {stats['total_tasks']}\n• 已完成: {stats['completed_tasks']}\n• 待完成: {stats['pending_tasks']}\n• 完成率: {stats['completion_rate']}%{mention_text}{task_list}\n\n请未完成任务的负责人尽快处理！"
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
                    "content": f"**月度报告截止日期临近！**\n\n📊 **当前进度**:\n• 总任务数: {stats['total_tasks']}\n• 已完成: {stats['completed_tasks']}\n• 待完成: {stats['pending_tasks']}\n• 完成率: {stats['completion_rate']}%{mention_text}{task_list}\n\n🚨 **请立即完成剩余任务！**"
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
                    "content": f"**{stats['current_month']} 月度报告完成情况**\n\n{summary}\n\n📈 **完成情况**:\n• 总任务数: {stats['total_tasks']}\n• 已完成: {stats['completed_tasks']}\n• 未完成: {stats['pending_tasks']}\n• 完成率: {stats['completion_rate']}%\n\n📊 **进度条**:\n`{progress_bar}` {stats['completion_rate']}%{chart_info}\n\n⏰ 统计时间: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')}"
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

async def build_daily_stats_card_with_chart() -> Dict:
    """构建带图表的每日统计卡片"""
    try:
        # 同步任务状态
        await sync_task_completion_status()

        # 获取统计数据
        stats = get_task_completion_stats()
        task_stats_full = load_task_stats()

        # 生成图表
        chart_path = None
        image_key = None
        if chart_generator and stats.get('total_tasks', 0) > 0:
            try:
                chart_path = chart_generator.generate_comprehensive_dashboard(task_stats_full)
                if chart_path and os.path.exists(chart_path):
                    # 上传图表到飞书
                    image_key = await upload_image(chart_path)
                    logger.info("图表已生成并上传: %s", chart_path)
            except Exception as e:
                logger.error("生成或上传图表失败: %s", e)

        # 构建进度条
        progress_width = min(int(stats['completion_rate'] / 10), 10)
        progress_bar = "█" * progress_width + "░" * (10 - progress_width)

        # 评估完成情况
        if stats['completion_rate'] >= 100:
            summary = "🎉 **恭喜！所有任务已完成！**"
            template_color = "green"
        elif stats['completion_rate'] >= 80:
            summary = "✅ **任务完成情况良好！**"
            template_color = "blue"
        elif stats['completion_rate'] >= 60:
            summary = "⚠️ **任务完成情况一般，需要关注！**"
            template_color = "orange"
        else:
            summary = "❌ **任务完成情况较差，需要改进！**"
            template_color = "red"

        # 构建卡片元素
        elements = []

        # 添加统计文本
        content_text = (
            f"**{stats['current_month']} 月度报告进度统计**\n\n"
            f"{summary}\n\n"
            f"📈 **完成情况**:\n"
            f"• 总任务数: {stats['total_tasks']}\n"
            f"• 已完成: {stats['completed_tasks']}\n"
            f"• 待完成: {stats['pending_tasks']}\n"
            f"• 完成率: {stats['completion_rate']}%\n\n"
            f"📊 **进度条**:\n"
            f"`{progress_bar}` {stats['completion_rate']}%\n\n"
            f"⏰ 统计时间: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')}"
        )

        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": content_text
            }
        })

        # 添加图表图片（如果成功上传）
        if image_key:
            elements.append({
                "tag": "img",
                "img_key": image_key,
                "alt": {
                    "tag": "plain_text",
                    "content": "任务统计图表"
                }
            })
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "📊 **上图为综合统计仪表板**，包含任务完成情况、完成率、任务数量对比等多维度分析"
                }
            })

        # 添加按钮
        elements.append({
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "查看详情"
                    },
                    "type": "primary",
                    "url": FILE_URL
                }
            ]
        })

        # 构建完整卡片
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "📊 每日任务统计报告"
                },
                "template": template_color
            },
            "elements": elements
        }

        return card

    except Exception as e:
        logger.error("构建每日统计卡片失败: %s", e)
        # 返回简化版卡片
        return {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "📊 每日任务统计报告"
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "统计卡片生成失败，请稍后重试"
                    }
                }
            ]
        }

# ---------------------- 图片上传函数 ----------------------

async def upload_image(image_path: str) -> Optional[str]:
    """上传图片到飞书，返回image_key"""
    try:
        from lark_oapi.api.im.v1 import CreateImageRequest

        if not os.path.exists(image_path):
            logger.error("图片文件不存在: %s", image_path)
            return None

        # 读取图片文件
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # 构建请求
        request = CreateImageRequest.builder() \
            .request_body(CreateImageRequestBody.builder()
                        .image_type("message")
                        .image(image_data)
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
        logger.error("上传图片异常: %s", e)
        return None

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


def generate_echo_reply(text: str) -> str:
    """根据输入文本生成回声/帮助回复（可单元测试）"""
    normalized = _sanitize_command_text(text)
    if normalized in {"/help", "help", "?", "帮助", "命令", "功能", "说明", "帮助一下", "怎么用"}:
        return (
            "📋 月报机器人帮助\n\n"
            "- 发送『状态/进度/统计/完成率』查看任务进度\n"
            "- 发送『未完成/谁没交/任务列表』查看未完成任务\n"
            "- 发送『图表/可视化/饼图』查看美观的统计图表\n"
            "- 发送『文件/链接/模板/地址』获取月报文件链接\n"
            "- 发送『截止/时间/提醒/什么时候』查看时间安排\n"
            "- 发送『已完成/完成了/done』查看如何标记完成说明\n"
            "- 其它文本将按原文回声返回（echo）"
        )

    # 状态/统计
    if normalized in {"状态", "进度", "统计", "完成率", "进展", "完成情况", "status", "progress", "summary"}:
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
            "- 17-19日 09:30：创建当月任务\n"
            "- 18-22日 10:00：发送每日提醒\n"
            "- 23日 09:00：发送最终催办\n"
            "- 23日 18:00：发送最终统计"
        )

    # 已完成/完成了（提示操作方式）
    if normalized in {"已完成", "完成了", "完成", "我完成", "done", "我完成了", "标记完成", "提交了", "完成啦"}:
        return "感谢您的辛勤工作，祝您工作愉快，后续将不再催办"

    # 图表/可视化统计
    if normalized in {"图表", "可视化", "饼图", "统计图", "图表统计", "chart", "visualization", "pie", "dashboard"}:
        return generate_chart_response()

    return f"Echo: {text}"

def generate_chart_response() -> str:
    """生成图表响应"""
    try:
        # 检查是否有任务数据
        created = load_created_tasks()
        current_month = datetime.now(TZ).strftime("%Y-%m")
        if not created.get(current_month, False):
            return "当前没有任务，无法生成图表"

        stats = get_task_completion_stats()
        if stats.get('total_tasks', 0) == 0:
            return "当前没有任务，无法生成图表"

        # 检查图表生成器是否可用
        if chart_generator is None:
            return "图表功能暂不可用，请检查依赖库安装"

        # 生成图表
        chart_path = chart_generator.generate_comprehensive_dashboard(stats)

        if chart_path and os.path.exists(chart_path):
            # 返回图表信息
            return (
                f"📊 统计图表已生成\n\n"
                f"📈 当前进度（{stats['current_month']}）:\n"
                f"- 总任务数: {stats['total_tasks']}\n"
                f"- 已完成: {stats['completed_tasks']}\n"
                f"- 待完成: {stats['pending_tasks']}\n"
                f"- 完成率: {stats['completion_rate']}%\n\n"
                f"📁 图表文件: {os.path.basename(chart_path)}\n"
                f"💡 提示: 图表包含饼状图、进度条、用户参与度等多维度统计"
            )
        else:
            return "图表生成失败，请稍后重试"

    except Exception as e:
        logger.error(f"生成图表响应失败: {e}")
        return "图表生成失败，请稍后重试"

async def handle_message_event(event: Dict[str, Any]) -> bool:
    """处理消息事件（im.message.receive_v1）：支持“状态/未完成/谁没交”等意图与无任务判断"""
    try:
        message = event.get("message", {})
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

        # 状态/进度/统计 → 若当月未创建任务则直接回复“当前没有任务”
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
            await reply_to_message(message_id, "\n".join(lines))
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
    """判断是否应该创建任务（17-19日09:30）"""
    if now is None:
        now = datetime.now(TZ)
    current_day = now.day
    current_time = now.strftime("%H:%M")

    return 17 <= current_day <= 19 and current_time == "09:30"

def should_send_daily_reminder(now: Optional[datetime] = None) -> bool:
    """判断是否应该发送每日提醒（18-22日10:00）"""
    if now is None:
        now = datetime.now(TZ)
    current_day = now.day
    current_time = now.strftime("%H:%M")

    return 18 <= current_day <= 22 and current_time == "10:00"

def should_send_final_reminder(now: Optional[datetime] = None) -> bool:
    """判断是否应该发送最终催办（23日09:00）"""
    if now is None:
        now = datetime.now(TZ)
    current_day = now.day
    current_time = now.strftime("%H:%M")

    return current_day == 23 and current_time == "09:00"

def should_send_final_stats(now: Optional[datetime] = None) -> bool:
    """判断是否应该发送最终统计（23日18:00）"""
    if now is None:
        now = datetime.now(TZ)
    current_day = now.day
    current_time = now.strftime("%H:%M")

    return current_day == 23 and current_time == "18:00"

def should_send_daily_stats(now: Optional[datetime] = None) -> bool:
    """判断是否应该发送每日统计（每天17:30）"""
    if now is None:
        now = datetime.now(TZ)
    current_time = now.strftime("%H:%M")

    return current_time == "17:30"

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
                success = await create_monthly_tasks()
                if not success:
                    await send_text_to_chat("❌ 任务创建失败，请检查配置")

            elif should_send_daily_reminder(now):
                logger.info("发送每日提醒...")
                await sync_task_completion_status()
                card = build_daily_reminder_card()
                await send_card_to_chat(card)

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

            elif should_send_daily_stats(now):
                logger.info("发送每日统计（17:30）...")
                card = await build_daily_stats_card_with_chart()
                success = await send_card_to_chat(card)
                if success:
                    logger.info("✅ 每日统计卡片发送成功")
                else:
                    logger.error("❌ 每日统计卡片发送失败")

            elif now.minute == 0:
                logger.info("执行定时任务状态同步...")
                await sync_task_completion_status()

            await asyncio.sleep(60)

        except Exception as e:
            logger.error("主循环异常: %s", e)
            await asyncio.sleep(60)

# 注：create_monthly_tasks 函数已在上方定义（使用 lark_oapi SDK 真实创建任务）

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


