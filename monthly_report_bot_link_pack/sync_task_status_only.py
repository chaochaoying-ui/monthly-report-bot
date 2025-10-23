#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版任务同步工具 - 只同步已有任务的完成状态
不需要列出所有任务，直接使用task_stats.json中的task_id查询状态
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any
import pytz

try:
    import lark_oapi as lark
    from lark_oapi.api.task.v2 import *
except ImportError:
    print("错误：需要安装 lark_oapi")
    print("运行: pip install lark-oapi")
    exit(1)

# 阿根廷时区
TZ = pytz.timezone('America/Argentina/Buenos_Aires')

# 配置文件
TASK_STATS_FILE = os.path.join(os.path.dirname(__file__), "task_stats.json")

def load_task_stats() -> Dict[str, Any]:
    """加载任务统计"""
    try:
        if os.path.exists(TASK_STATS_FILE):
            with open(TASK_STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"加载task_stats.json失败: {e}")
        return {}

def save_task_stats(stats: Dict[str, Any]) -> None:
    """保存任务统计"""
    try:
        stats["last_update"] = datetime.now(TZ).isoformat()
        with open(TASK_STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print("✅ task_stats.json 已更新")
    except Exception as e:
        print(f"保存task_stats.json失败: {e}")

async def check_task_status(client, task_guid: str) -> int:
    """
    检查单个任务状态
    返回: 2=已完成, 1=进行中, 0=查询失败
    """
    try:
        request = GetTaskRequest.builder() \
            .task_guid(task_guid) \
            .build()

        response = await client.task.v2.task.aget(request)

        if response.success():
            task = response.data.task
            return task.complete  # 2=已完成, 1=进行中
        else:
            print(f"  ⚠️ 查询失败: {task_guid[:20]}... (code={response.code})")
            return 0

    except Exception as e:
        print(f"  ❌ 异常: {task_guid[:20]}... ({e})")
        return 0

async def main():
    print("=" * 60)
    print("任务状态同步工具（简化版）")
    print("=" * 60)

    # 从环境变量读取凭证
    APP_ID = os.environ.get('APP_ID', '').strip()
    APP_SECRET = os.environ.get('APP_SECRET', '').strip()

    if not APP_ID or not APP_SECRET:
        print("错误：未找到飞书应用凭证")
        print("请确保环境变量中有 APP_ID 和 APP_SECRET")
        print("或运行: set -a && source .env && set +a")
        return

    print(f"APP_ID: {APP_ID[:15]}...")
    print(f"APP_SECRET: {APP_SECRET[:15]}...")

    # 初始化飞书客户端
    client = lark.Client.builder() \
        .app_id(APP_ID) \
        .app_secret(APP_SECRET) \
        .build()

    # 加载当前task_stats
    stats = load_task_stats()
    if not stats or "tasks" not in stats:
        print("❌ task_stats.json 为空或格式不正确")
        return

    current_month = datetime.now(TZ).strftime("%Y-%m")
    print(f"\n📅 当前月份: {current_month}")
    print(f"📊 本地任务数: {len(stats['tasks'])}")

    # 同步所有任务状态
    print(f"\n🔄 开始同步任务状态...")
    updated_count = 0
    unchanged_count = 0

    for task_guid, task_info in stats["tasks"].items():
        title = task_info.get("title", "")[:40]
        old_completed = task_info.get("completed", False)

        # 查询任务状态
        complete_status = await check_task_status(client, task_guid)

        if complete_status == 0:
            # 查询失败，跳过
            continue

        new_completed = (complete_status == 2)

        if new_completed != old_completed:
            # 状态变化
            stats["tasks"][task_guid]["completed"] = new_completed
            if new_completed:
                stats["tasks"][task_guid]["completed_at"] = datetime.now(TZ).isoformat()
                print(f"  ✅ {title}... (已完成)")
            else:
                stats["tasks"][task_guid]["completed_at"] = None
                print(f"  ⏳ {title}... (未完成)")
            updated_count += 1
        else:
            # 状态未变化
            status_icon = "✅" if new_completed else "⏳"
            unchanged_count += 1
            # print(f"  {status_icon} {title}... (无变化)")

    # 重新计算统计
    total_tasks = len(stats["tasks"])
    completed_tasks = sum(1 for t in stats["tasks"].values() if t.get("completed", False))
    completion_rate = round((completed_tasks / total_tasks) * 100, 2) if total_tasks > 0 else 0.0

    # 更新stats
    stats["total_tasks"] = total_tasks
    stats["completed_tasks"] = completed_tasks
    stats["completion_rate"] = completion_rate
    stats["current_month"] = current_month

    # 保存
    save_task_stats(stats)

    print(f"\n" + "=" * 60)
    print(f"✅ 同步完成！")
    print(f"=" * 60)
    print(f"📊 统计信息:")
    print(f"  • 总任务数: {total_tasks}")
    print(f"  • 已完成: {completed_tasks}")
    print(f"  • 待完成: {total_tasks - completed_tasks}")
    print(f"  • 完成率: {completion_rate}%")
    print(f"  • 状态变化: {updated_count} 个")
    print(f"  • 状态不变: {unchanged_count} 个")
    print(f"\n🎉 任务状态已同步！")

if __name__ == "__main__":
    asyncio.run(main())
