#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新袁阿虎和高雅慧的任务完成状态
"""

import json
import os
from datetime import datetime
import pytz

# 阿根廷时区
TZ = pytz.timezone("America/Argentina/Buenos_Aires")

# 文件路径
TASK_STATS_FILE = "task_stats.json"

def update_task_completion():
    """更新袁阿虎和高雅慧的任务完成状态"""

    # 读取当前任务统计
    with open(TASK_STATS_FILE, 'r', encoding='utf-8') as f:
        stats = json.load(f)

    # 完成时间（使用阿根廷时区）
    completion_time = datetime.now(TZ).isoformat()

    # 袁阿虎的任务
    yuan_tasks = ["task_2025-10_17", "task_2025-10_18"]
    # 高雅慧的任务
    gao_tasks = ["task_2025-10_10", "task_2025-10_11"]

    updated_tasks = []

    # 更新袁阿虎的任务
    for task_id in yuan_tasks:
        if task_id in stats["tasks"] and not stats["tasks"][task_id]["completed"]:
            stats["tasks"][task_id]["completed"] = True
            stats["tasks"][task_id]["completed_at"] = completion_time
            stats["completed_tasks"] += 1
            updated_tasks.append(f"✅ {task_id}: {stats['tasks'][task_id]['title']}")
            print(f"✅ 标记完成: {stats['tasks'][task_id]['title']} (袁阿虎)")

    # 更新高雅慧的任务
    for task_id in gao_tasks:
        if task_id in stats["tasks"] and not stats["tasks"][task_id]["completed"]:
            stats["tasks"][task_id]["completed"] = True
            stats["tasks"][task_id]["completed_at"] = completion_time
            stats["completed_tasks"] += 1
            updated_tasks.append(f"✅ {task_id}: {stats['tasks'][task_id]['title']}")
            print(f"✅ 标记完成: {stats['tasks'][task_id]['title']} (高雅慧)")

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
    print(f"\n👤 袁阿虎: 完成 {len([t for t in yuan_tasks if t in stats['tasks'] and stats['tasks'][t]['completed']])} 个任务")
    print(f"👤 高雅慧: 完成 {len([t for t in gao_tasks if t in stats['tasks'] and stats['tasks'][t]['completed']])} 个任务")
    print(f"\n📈 总体统计:")
    print(f"   - 总任务数: {stats['total_tasks']}")
    print(f"   - 已完成: {stats['completed_tasks']}")
    print(f"   - 待完成: {stats['total_tasks'] - stats['completed_tasks']}")
    print(f"   - 完成率: {stats['completion_rate']}%")
    print(f"\n⏰ 更新时间: {completion_time}")
    print("="*60)

if __name__ == "__main__":
    try:
        update_task_completion()
        print("\n✅ 任务完成状态更新成功！")
    except Exception as e:
        print(f"\n❌ 更新失败: {e}")
