#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理 task_stats.json 中的模拟任务ID，准备接收真实GUID

这个脚本会：
1. 备份现有的 task_stats.json
2. 清空 tasks 字典（保留已完成统计）
3. 重置任务计数器
4. 等待下次任务创建时使用真实GUID

注意：这会清除所有任务记录，但保留总体统计数据
运行后需要重新创建任务（使用修复后的代码）
"""

import json
import os
from datetime import datetime
import shutil

# 文件路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_STATS_FILE = os.path.join(BASE_DIR, "task_stats.json")
BACKUP_SUFFIX = datetime.now().strftime("%Y%m%d_%H%M%S")

def main():
    print("=" * 60)
    print("清理 task_stats.json 中的模拟任务ID")
    print("=" * 60)

    # 检查文件是否存在
    if not os.path.exists(TASK_STATS_FILE):
        print(f"❌ 错误: 文件不存在: {TASK_STATS_FILE}")
        return

    # 读取当前数据
    with open(TASK_STATS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"\n📊 当前状态:")
    print(f"  - 当前月份: {data.get('current_month', 'N/A')}")
    print(f"  - 任务总数: {data.get('total_tasks', 0)}")
    print(f"  - 已完成: {data.get('completed_tasks', 0)}")
    print(f"  - 完成率: {data.get('completion_rate', 0)}%")

    # 检查任务ID格式
    fake_ids = []
    real_guids = []

    for task_id in data.get('tasks', {}).keys():
        if task_id.startswith('task_'):
            fake_ids.append(task_id)
        else:
            real_guids.append(task_id)

    print(f"\n🔍 任务ID分析:")
    print(f"  - 假ID数量: {len(fake_ids)} (如 task_2025-10_1)")
    print(f"  - 真实GUID数量: {len(real_guids)} (如 d65bbb59-2b71-...)")

    if len(fake_ids) == 0:
        print("\n✅ 太好了！没有发现假ID，task_stats.json 已经使用真实GUID")
        return

    # 确认操作
    print(f"\n⚠️  警告:")
    print(f"  - 将删除 {len(fake_ids)} 个假ID任务记录")
    print(f"  - 将保留 {len(real_guids)} 个真实GUID任务记录")
    print(f"  - 将保留总体统计数据（已完成数量等）")
    print(f"  - 会自动备份到: {TASK_STATS_FILE}.backup_{BACKUP_SUFFIX}")

    confirm = input("\n继续执行清理操作？(yes/no): ")
    if confirm.lower() not in ['yes', 'y']:
        print("❌ 操作已取消")
        return

    # 备份原文件
    backup_file = f"{TASK_STATS_FILE}.backup_{BACKUP_SUFFIX}"
    shutil.copy2(TASK_STATS_FILE, backup_file)
    print(f"\n✅ 已备份到: {backup_file}")

    # 清理假ID，保留真实GUID
    new_tasks = {}
    for task_id, task_info in data.get('tasks', {}).items():
        if not task_id.startswith('task_'):
            new_tasks[task_id] = task_info

    # 更新数据
    data['tasks'] = new_tasks
    data['last_update'] = datetime.now().isoformat()

    # 如果所有任务都是假ID，重置统计
    if len(new_tasks) == 0:
        print("\n⚠️  所有任务都是假ID，将重置统计数据")
        data['total_tasks'] = 0
        data['completed_tasks'] = 0
        data['completion_rate'] = 0.0
    else:
        # 重新计算统计（基于剩余的真实GUID）
        completed_count = sum(1 for t in new_tasks.values() if t.get('completed', False))
        total_count = len(new_tasks)
        data['total_tasks'] = total_count
        data['completed_tasks'] = completed_count
        data['completion_rate'] = round((completed_count / total_count * 100), 2) if total_count > 0 else 0.0

    # 保存更新后的数据
    with open(TASK_STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 清理完成!")
    print(f"\n📊 新状态:")
    print(f"  - 当前月份: {data['current_month']}")
    print(f"  - 任务总数: {data['total_tasks']}")
    print(f"  - 已完成: {data['completed_tasks']}")
    print(f"  - 完成率: {data['completion_rate']}%")

    print(f"\n📝 下一步:")
    if data['total_tasks'] == 0:
        print("  1. 确保 monthly_report_bot_ws_v1.1.py 已经修复（使用 InputTask, Due, Member API）")
        print("  2. 删除 created_tasks.json（让系统重新创建任务）：")
        print("     rm created_tasks.json")
        print("  3. 重启服务，等待下次任务创建时间（每月17-19日 09:30）")
        print("  4. 或者手动运行任务创建：")
        print("     python3 -c 'import monthly_report_bot_ws_v1 as bot; import asyncio; asyncio.run(bot.create_tasks())'")
    else:
        print(f"  已保留 {data['total_tasks']} 个真实GUID任务，无需重新创建")

    print(f"\n🔄 如需回滚，运行:")
    print(f"  cp {backup_file} {TASK_STATS_FILE}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
