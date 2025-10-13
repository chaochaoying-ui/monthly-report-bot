#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务统计管理工具
用于手动管理任务完成状态和查看统计信息
"""

import os
import sys
import json
import yaml
import pytz
from datetime import datetime
from typing import Dict, List, Any

# 设置环境变量
os.environ["TZ"] = "America/Argentina/Buenos_Aires"
TZ = pytz.timezone("America/Argentina/Buenos_Aires")

# 文件路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(BASE_DIR, "tasks.yaml")
TASK_STATS_FILE = os.path.join(BASE_DIR, "task_stats.json")

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
        print(f"加载任务统计失败: {e}")
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
        print("✅ 统计信息已保存")
    except Exception as e:
        print(f"❌ 保存任务统计失败: {e}")

def load_tasks() -> List[Dict[str, Any]]:
    """加载任务配置"""
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ 加载任务配置失败: {e}")
        return []

def show_stats() -> None:
    """显示统计信息"""
    print("="*60)
    print("📊 任务完成统计")
    print("="*60)
    
    stats = load_task_stats()
    tasks = load_tasks()
    
    print(f"📅 统计月份: {stats['current_month']}")
    print(f"📋 总任务数: {stats['total_tasks']}")
    print(f"✅ 已完成: {stats['completed_tasks']}")
    print(f"⏳ 待完成: {stats['total_tasks'] - stats['completed_tasks']}")
    print(f"📈 完成率: {stats['completion_rate']}%")
    print(f"🕒 最后更新: {stats['last_update']}")
    print()
    
    if stats['tasks']:
        print("📝 任务详情:")
        print("-" * 60)
        for task_id, task_info in stats['tasks'].items():
            status = "✅ 已完成" if task_info['completed'] else "⏳ 进行中"
            created_time = datetime.fromisoformat(task_info['created_at']).strftime("%m-%d %H:%M")
            completed_time = ""
            if task_info['completed'] and task_info['completed_at']:
                completed_time = f" (完成于: {datetime.fromisoformat(task_info['completed_at']).strftime('%m-%d %H:%M')})"
            
            print(f"• {task_id[:8]}... | {status} | 创建: {created_time}{completed_time}")
    else:
        print("📝 暂无任务记录")
    
    print("="*60)

def mark_task_completed(task_id: str) -> None:
    """标记任务为已完成"""
    print(f"🔧 标记任务完成: {task_id}")
    
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
    
    if not stats["tasks"][task_id]["completed"]:
        stats["tasks"][task_id]["completed"] = True
        stats["tasks"][task_id]["completed_at"] = datetime.now(TZ).isoformat()
        stats["completed_tasks"] += 1
        
        # 计算完成率
        if stats["total_tasks"] > 0:
            stats["completion_rate"] = round(stats["completed_tasks"] / stats["total_tasks"] * 100, 2)
        
        save_task_stats(stats)
        print(f"✅ 任务 {task_id} 已标记为完成")
    else:
        print(f"⚠️  任务 {task_id} 已经是完成状态")

def mark_task_incomplete(task_id: str) -> None:
    """标记任务为未完成"""
    print(f"🔧 标记任务未完成: {task_id}")
    
    stats = load_task_stats()
    
    if task_id in stats["tasks"] and stats["tasks"][task_id]["completed"]:
        stats["tasks"][task_id]["completed"] = False
        stats["tasks"][task_id]["completed_at"] = None
        stats["completed_tasks"] -= 1
        
        # 计算完成率
        if stats["total_tasks"] > 0:
            stats["completion_rate"] = round(stats["completed_tasks"] / stats["total_tasks"] * 100, 2)
        
        save_task_stats(stats)
        print(f"✅ 任务 {task_id} 已标记为未完成")
    else:
        print(f"⚠️  任务 {task_id} 本来就是未完成状态")

def reset_monthly_stats() -> None:
    """重置月度统计"""
    print("🔄 重置月度统计")
    
    current_month = datetime.now(TZ).strftime("%Y-%m")
    stats = {
        "current_month": current_month,
        "tasks": {},
        "total_tasks": 0,
        "completed_tasks": 0,
        "completion_rate": 0.0,
        "last_update": datetime.now(TZ).isoformat()
    }
    
    save_task_stats(stats)
    print(f"✅ {current_month} 月度统计已重置")

def show_help() -> None:
    """显示帮助信息"""
    print("="*60)
    print("🔧 任务统计管理工具")
    print("="*60)
    print("使用方法:")
    print("  python task_stats_manager.py [命令] [参数]")
    print()
    print("可用命令:")
    print("  stats                    - 显示统计信息")
    print("  complete <task_id>       - 标记任务为已完成")
    print("  incomplete <task_id>     - 标记任务为未完成")
    print("  reset                    - 重置月度统计")
    print("  help                     - 显示此帮助信息")
    print()
    print("示例:")
    print("  python task_stats_manager.py stats")
    print("  python task_stats_manager.py complete abc123")
    print("  python task_stats_manager.py reset")
    print("="*60)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "stats":
        show_stats()
    elif command == "complete":
        if len(sys.argv) < 3:
            print("❌ 请提供任务ID")
            return
        task_id = sys.argv[2]
        mark_task_completed(task_id)
    elif command == "incomplete":
        if len(sys.argv) < 3:
            print("❌ 请提供任务ID")
            return
        task_id = sys.argv[2]
        mark_task_incomplete(task_id)
    elif command == "reset":
        reset_monthly_stats()
    elif command == "help":
        show_help()
    else:
        print(f"❌ 未知命令: {command}")
        show_help()

if __name__ == "__main__":
    main()
