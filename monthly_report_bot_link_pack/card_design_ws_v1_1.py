#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月报机器人 v1.1 - 卡片设计模块
设计理念：专业美观、信息清晰、交互友好

功能：
1. 欢迎卡片（新成员入群）
2. 月报任务卡片（18-22日）
3. 最终提醒卡片（23日）
4. 帮助卡片
"""

from __future__ import annotations
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def build_welcome_card(config: Dict[str, Any]) -> Dict[str, Any]:
    """构建欢迎卡片（按照需求文档9.1）"""
    return {
        "header": {
            "title": "欢迎加入月报协作群！",
            "template": "blue"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "content": f"""当前配置：
• 推送时刻：{config.get('push_time', '09:30')}
• 时区：{config.get('timezone', 'America/Argentina/Buenos_Aires')}
• 文件链接：{'已配置' if config.get('file_url') else '未配置'}""",
                    "tag": "lark_md"
                }
            },
            {
                "tag": "action_group",
                "actions": [
                    {
                        "tag": "button",
                        "text": "设置推送时刻",
                        "type": "primary",
                        "value": {"action": "set_push_time"}
                    },
                    {
                        "tag": "button", 
                        "text": "绑定文件链接",
                        "type": "default",
                        "value": {"action": "bind_file_url"}
                    },
                    {
                        "tag": "button",
                        "text": "查看帮助",
                        "type": "default", 
                        "value": {"action": "show_help"}
                    }
                ]
            }
        ]
    }

def build_monthly_task_card(config: Dict[str, Any], date: str = None, 
                           completed_count: int = 0, total_count: int = 0) -> Dict[str, Any]:
    """构建月报任务卡片（按照需求文档9.2）"""
    if date is None:
        date = datetime.now().strftime("%Y年%m月%d日")
    
    completion_rate = int((completed_count / total_count * 100) if total_count > 0 else 0)
    
    return {
        "header": {
            "title": f"📊 月报任务进度 - {date}",
            "template": "green"
        },
        "elements": [
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": True, 
                        "text": {
                            "content": f"**已完成**\n{completed_count}/{total_count}", 
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": True, 
                        "text": {
                            "content": f"**完成率**\n{completion_rate}%", 
                            "tag": "lark_md"
                        }
                    }
                ]
            },
            {
                "tag": "action_group",
                "actions": [
                    {
                        "tag": "button",
                        "text": "我已完成",
                        "type": "primary",
                        "value": {"action": "mark_completed"}
                    },
                    {
                        "tag": "button",
                        "text": "申请延期", 
                        "type": "default",
                        "value": {"action": "request_extension"}
                    },
                    {
                        "tag": "button",
                        "text": "查看我的清单",
                        "type": "default",
                        "value": {"action": "view_my_tasks"}
                    }
                ]
            }
        ]
    }

def build_final_reminder_card(config: Dict[str, Any], overdue_tasks: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """构建最终提醒卡片（按照需求文档F4）"""
    file_url = config.get('file_url', '')
    
    # 构建逾期清单文本
    overdue_text = ""
    if overdue_tasks:
        overdue_text = "\n\n**逾期清单：**\n"
        for task in overdue_tasks:
            overdue_text += f"• {task.get('assignee', '未知')} - {task.get('title', '未知任务')} (截止: {task.get('due_date', '未知')})\n"
    
    return {
        "header": {
            "title": "📣 月报最终提醒",
            "template": "red"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "content": f"""请在今天 17:00 前完成提交。

文件链接：{file_url}{overdue_text}""",
                    "tag": "lark_md"
                }
            },
            {
                "tag": "action_group",
                "actions": [
                    {
                        "tag": "button",
                        "text": "查看文件",
                        "type": "primary",
                        "value": {"action": "open_file", "url": file_url}
                    },
                    {
                        "tag": "button",
                        "text": "查看我的任务",
                        "type": "default",
                        "value": {"action": "view_my_tasks"}
                    }
                ]
            }
        ]
    }

def build_help_card(language: str = "zh") -> Dict[str, Any]:
    """构建帮助卡片"""
    help_content = {
        "zh": {
            "title": "月报机器人使用帮助",
            "content": """**基本功能：**
• 自动创建月报任务（每月17-19日）
• 每日任务进度提醒（18-22日）
• 最终提交提醒（23日）

**交互方式：**
• 文本对话：直接输入"我的任务"、"已完成"等
• 卡片按钮：点击卡片上的按钮进行操作

**常用命令：**
• "我的清单" - 查看个人任务
• "已完成" - 标记任务完成
• "延期到明天17:00" - 申请延期
• "查看进度" - 查看整体进度""",
            "button_text": "返回"
        },
        "en": {
            "title": "Monthly Report Bot Help",
            "content": """**Basic Features:**
• Auto-create monthly report tasks (17-19th monthly)
• Daily task progress reminders (18-22nd)
• Final submission reminder (23rd)

**Interaction Methods:**
• Text chat: Direct input like "my tasks", "done", etc.
• Card buttons: Click buttons on cards

**Common Commands:**
• "my tasks" - View personal tasks
• "done" - Mark task as completed
• "extend to tomorrow 17:00" - Request extension
• "show progress" - View overall progress""",
            "button_text": "Back"
        },
        "es": {
            "title": "Ayuda del Bot de Reporte Mensual",
            "content": """**Funciones Básicas:**
• Crear automáticamente tareas de reporte mensual (17-19 de cada mes)
• Recordatorios diarios de progreso (18-22)
• Recordatorio final de envío (23)

**Métodos de Interacción:**
• Chat de texto: Entrada directa como "mis tareas", "hecho", etc.
• Botones de tarjeta: Hacer clic en botones de tarjetas

**Comandos Comunes:**
• "mis tareas" - Ver tareas personales
• "hecho" - Marcar tarea como completada
• "extender a mañana 17:00" - Solicitar extensión
• "mostrar progreso" - Ver progreso general""",
            "button_text": "Volver"
        }
    }
    
    content = help_content.get(language, help_content["zh"])
    
    return {
        "header": {
            "title": content["title"],
            "template": "blue"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "content": content["content"],
                    "tag": "lark_md"
                }
            },
            {
                "tag": "action_group",
                "actions": [
                    {
                        "tag": "button",
                        "text": content["button_text"],
                        "type": "default",
                        "value": {"action": "back_to_main"}
                    }
                ]
            }
        ]
    }

def build_task_list_card(tasks: List[Dict[str, Any]], user_open_id: str, language: str = "zh") -> Dict[str, Any]:
    """构建任务清单卡片（私聊使用）"""
    if not tasks:
        return build_empty_task_card(language)
    
    # 构建任务列表
    task_list = ""
    for i, task in enumerate(tasks[:10], 1):  # 最多显示10个任务
        status_emoji = "✅" if task.get("status") == "completed" else "⏳"
        task_list += f"{i}. {status_emoji} {task.get('title', '未知任务')}\n"
    
    if len(tasks) > 10:
        task_list += f"\n... 还有 {len(tasks) - 10} 个任务"
    
    return {
        "header": {
            "title": get_task_list_title(language),
            "template": "green"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "content": task_list,
                    "tag": "lark_md"
                }
            },
            {
                "tag": "action_group",
                "actions": [
                    {
                        "tag": "button",
                        "text": get_mark_completed_text(language),
                        "type": "primary",
                        "value": {"action": "mark_completed", "user_id": user_open_id}
                    },
                    {
                        "tag": "button",
                        "text": get_request_extension_text(language),
                        "type": "default",
                        "value": {"action": "request_extension", "user_id": user_open_id}
                    }
                ]
            }
        ]
    }

def build_empty_task_card(language: str = "zh") -> Dict[str, Any]:
    """构建空任务卡片"""
    content_map = {
        "zh": {
            "title": "任务清单",
            "content": "🎉 恭喜！您当前没有待完成的任务。",
            "button_text": "返回"
        },
        "en": {
            "title": "Task List",
            "content": "🎉 Congratulations! You have no pending tasks.",
            "button_text": "Back"
        },
        "es": {
            "title": "Lista de Tareas",
            "content": "🎉 ¡Felicitaciones! No tienes tareas pendientes.",
            "button_text": "Volver"
        }
    }
    
    content = content_map.get(language, content_map["zh"])
    
    return {
        "header": {
            "title": content["title"],
            "template": "green"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "content": content["content"],
                    "tag": "lark_md"
                }
            },
            {
                "tag": "action_group",
                "actions": [
                    {
                        "tag": "button",
                        "text": content["button_text"],
                        "type": "default",
                        "value": {"action": "back_to_main"}
                    }
                ]
            }
        ]
    }

def build_extension_request_card(language: str = "zh") -> Dict[str, Any]:
    """构建延期申请卡片"""
    content_map = {
        "zh": {
            "title": "申请延期",
            "content": "请选择要延期的任务和新的截止时间：",
            "button_text": "提交申请"
        },
        "en": {
            "title": "Request Extension",
            "content": "Please select the task to extend and new deadline:",
            "button_text": "Submit Request"
        },
        "es": {
            "title": "Solicitar Extensión",
            "content": "Por favor selecciona la tarea para extender y nueva fecha límite:",
            "button_text": "Enviar Solicitud"
        }
    }
    
    content = content_map.get(language, content_map["zh"])
    
    return {
        "header": {
            "title": content["title"],
            "template": "orange"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "content": content["content"],
                    "tag": "lark_md"
                }
            },
            {
                "tag": "action_group",
                "actions": [
                    {
                        "tag": "button",
                        "text": content["button_text"],
                        "type": "primary",
                        "value": {"action": "submit_extension"}
                    },
                    {
                        "tag": "button",
                        "text": "取消",
                        "type": "default",
                        "value": {"action": "cancel_extension"}
                    }
                ]
            }
        ]
    }

def build_config_card(config: Dict[str, Any], language: str = "zh") -> Dict[str, Any]:
    """构建配置卡片"""
    content_map = {
        "zh": {
            "title": "群组配置",
            "content": f"""**当前配置：**
• 推送时刻：{config.get('push_time', '09:30')}
• 时区：{config.get('timezone', 'America/Argentina/Buenos_Aires')}
• 文件链接：{config.get('file_url', '未配置')}""",
            "button_text": "修改配置"
        },
        "en": {
            "title": "Group Configuration",
            "content": f"""**Current Configuration:**
• Push Time: {config.get('push_time', '09:30')}
• Timezone: {config.get('timezone', 'America/Argentina/Buenos_Aires')}
• File URL: {config.get('file_url', 'Not configured')}""",
            "button_text": "Modify Configuration"
        },
        "es": {
            "title": "Configuración del Grupo",
            "content": f"""**Configuración Actual:**
• Hora de Envío: {config.get('push_time', '09:30')}
• Zona Horaria: {config.get('timezone', 'America/Argentina/Buenos_Aires')}
• URL del Archivo: {config.get('file_url', 'No configurado')}""",
            "button_text": "Modificar Configuración"
        }
    }
    
    content = content_map.get(language, content_map["zh"])
    
    return {
        "header": {
            "title": content["title"],
            "template": "blue"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "content": content["content"],
                    "tag": "lark_md"
                }
            },
            {
                "tag": "action_group",
                "actions": [
                    {
                        "tag": "button",
                        "text": content["button_text"],
                        "type": "primary",
                        "value": {"action": "modify_config"}
                    },
                    {
                        "tag": "button",
                        "text": "返回",
                        "type": "default",
                        "value": {"action": "back_to_main"}
                    }
                ]
            }
        ]
    }

# 辅助函数
def get_task_list_title(language: str) -> str:
    """获取任务清单标题"""
    titles = {
        "zh": "您的任务清单",
        "en": "Your Task List",
        "es": "Tu Lista de Tareas"
    }
    return titles.get(language, titles["zh"])

def get_mark_completed_text(language: str) -> str:
    """获取标记完成按钮文本"""
    texts = {
        "zh": "标记完成",
        "en": "Mark Completed",
        "es": "Marcar Completado"
    }
    return texts.get(language, texts["zh"])

def get_request_extension_text(language: str) -> str:
    """获取申请延期按钮文本"""
    texts = {
        "zh": "申请延期",
        "en": "Request Extension",
        "es": "Solicitar Extensión"
    }
    return texts.get(language, texts["zh"])

def build_progress_chart_card(stats: Dict[str, Any], language: str = "zh") -> Dict[str, Any]:
    """
    构建进度图表卡片（18-22日17:00发送）

    Args:
        stats: 任务完成统计数据
        language: 语言（zh/en/es）

    Returns:
        卡片JSON对象
    """
    from datetime import datetime
    import pytz

    TZ = pytz.timezone("America/Argentina/Buenos_Aires")
    now = datetime.now(TZ)
    date_str = now.strftime("%Y年%m月%d日")

    # 标题文本
    title_texts = {
        "zh": f"📊 月报任务进度 - {date_str}",
        "en": f"📊 Monthly Report Progress - {now.strftime('%Y-%m-%d')}",
        "es": f"📊 Progreso del Reporte Mensual - {now.strftime('%Y-%m-%d')}"
    }

    # 计算完成率
    total = stats.get("total", 0)
    completed = stats.get("completed", 0)
    completion_rate = (completed / total * 100) if total > 0 else 0

    # 构建统计信息文本
    stats_text = f"**总任务**: {total}\\n**已完成**: {completed}\\n**未完成**: {total - completed}\\n**完成率**: {completion_rate:.1f}%"

    # 分专业统计
    by_category = stats.get("by_category", {})
    if by_category:
        stats_text += "\\n\\n**分专业进度:**\\n"
        for category, cat_stats in by_category.items():
            cat_total = cat_stats.get("total", 0)
            cat_completed = cat_stats.get("completed", 0)
            cat_rate = (cat_completed / cat_total * 100) if cat_total > 0 else 0
            stats_text += f"• {category}: {cat_completed}/{cat_total} ({cat_rate:.0f}%)\\n"

    card = {
        "header": {
            "title": {
                "tag": "plain_text",
                "content": title_texts.get(language, title_texts["zh"])
            },
            "template": "green"
        },
        "elements": [
            {
                "tag": "markdown",
                "content": stats_text
            },
            {
                "tag": "hr"
            },
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": "可视化任务进度" if language == "zh" else "Task Progress Visualization"
                    }
                ]
            }
        ]
    }

    return card

