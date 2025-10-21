#!/usr/bin/env python3
"""测试每日提醒功能修复"""

import asyncio
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from monthly_report_bot_link_pack.monthly_report_bot_final_interactive import (
    test_daily_reminder,
    get_user_display_name,
    get_task_completion_stats
)

async def test_fix():
    """测试修复后的功能"""
    print("=" * 60)
    print("测试每日提醒功能修复")
    print("=" * 60)

    # 1. 测试 get_user_display_name 函数
    print("\n1. 测试 get_user_display_name 函数:")
    test_user_id = "ou_c245b0a7dff11b36369edb96471ed182"
    display_name = get_user_display_name(test_user_id)
    print(f"   用户 ID: {test_user_id}")
    print(f"   显示名称: {display_name}")

    # 2. 测试任务统计
    print("\n2. 测试任务统计:")
    stats = get_task_completion_stats()
    print(f"   总任务数: {stats['total_tasks']}")
    print(f"   已完成: {stats['completed_tasks']}")
    print(f"   待完成: {stats['total_tasks'] - stats['completed_tasks']}")
    print(f"   完成率: {stats['completion_rate']:.1f}%")

    # 3. 测试@格式生成
    print("\n3. 测试@格式生成:")
    for task_id, task_info in stats['tasks'].items():
        if not task_info.get('completed', False):
            assignees = task_info.get('assignees', [])
            print(f"\n   任务: {task_info['title']}")
            print(f"   负责人数: {len(assignees)}")
            for assignee in assignees:
                display_name = get_user_display_name(assignee)
                at_format = f"<at user_id=\"{assignee}\">{display_name}</at>"
                print(f"   - {at_format}")

    # 4. 发送测试提醒
    print("\n4. 发送测试每日提醒:")
    success = await test_daily_reminder()

    if success:
        print("\n✅ 每日提醒测试成功！")
    else:
        print("\n❌ 每日提醒测试失败！")

    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_fix())
