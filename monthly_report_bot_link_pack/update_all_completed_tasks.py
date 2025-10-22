#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新所有已完成人员的任务状态
包括：刘野、范明杰、袁阿虎、高雅慧
"""

import json
import os
from datetime import datetime
import pytz

# 阿根廷时区
TZ = pytz.timezone("America/Argentina/Buenos_Aires")

# 文件路径
TASK_STATS_FILE = "task_stats.json"

def update_all_completed_tasks():
    """更新所有已完成人员的任务状态"""

    # 读取当前任务统计
    with open(TASK_STATS_FILE, 'r', encoding='utf-8') as f:
        stats = json.load(f)

    # 完成时间（使用阿根廷时区）
    completion_time = datetime.now(TZ).isoformat()

    # 已完成人员的任务ID
    completed_task_ids = {
        # 刘野的5个任务
        "task_2025-10_1": "2025-10-21T10:00:00-03:00",
        "task_2025-10_3": "2025-10-21T10:00:00-03:00",
        "task_2025-10_4": "2025-10-21T10:00:00-03:00",
        "task_2025-10_5": "2025-10-21T10:00:00-03:00",

        # 范明杰的1个任务
        "task_2025-10_2": "2025-10-21T10:00:00-03:00",

        # 袁阿虎的2个任务
        "task_2025-10_17": "2025-10-22T09:26:00-03:00",
        "task_2025-10_18": "2025-10-22T09:26:00-03:00",

        # 高雅慧的2个任务
        "task_2025-10_10": "2025-10-22T09:26:00-03:00",
        "task_2025-10_11": "2025-10-22T09:26:00-03:00",
    }

    updated_count = 0

    # 更新所有已完成任务
    for task_id, completed_at in completed_task_ids.items():
        if task_id in stats["tasks"]:
            if not stats["tasks"][task_id]["completed"]:
                stats["tasks"][task_id]["completed"] = True
                stats["tasks"][task_id]["completed_at"] = completed_at
                stats["completed_tasks"] += 1
                updated_count += 1
                print(f"✅ 标记完成: {stats['tasks'][task_id]['title']}")
            else:
                print(f"⏭️  已完成: {stats['tasks'][task_id]['title']}")

    # 重新计算完成率
    if stats["total_tasks"] > 0:
        stats["completion_rate"] = round(stats["completed_tasks"] / stats["total_tasks"] * 100, 2)

    # 更新时间
    stats["last_update"] = completion_time

    # 保存更新后的数据
    with open(TASK_STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    # 打印摘要
    print("\n" + "="*60)
    print("📊 任务完成状态更新摘要")
    print("="*60)
    print(f"\n👤 已完成人员统计:")
    print(f"   - 刘野: 5个任务 ✅")
    print(f"   - 范明杰: 1个任务 ✅")
    print(f"   - 袁阿虎: 2个任务 ✅")
    print(f"   - 高雅慧: 2个任务 ✅")
    print(f"\n📈 总体统计:")
    print(f"   - 总任务数: {stats['total_tasks']}")
    print(f"   - 已完成: {stats['completed_tasks']}")
    print(f"   - 待完成: {stats['total_tasks'] - stats['completed_tasks']}")
    print(f"   - 完成率: {stats['completion_rate']}%")
    print(f"\n⏰ 更新时间: {completion_time}")
    print(f"📝 本次更新: {updated_count} 个任务")
    print("="*60)

if __name__ == "__main__":
    try:
        update_all_completed_tasks()
        print("\n✅ 任务完成状态更新成功！")
    except Exception as e:
        print(f"\n❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
