#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试任务状态同步功能
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入最终版的功能
from monthly_report_bot_final import (
    init_lark_client, 
    sync_task_completion_status, 
    get_task_completion_stats,
    get_pending_tasks_detail,
    load_task_stats
)

async def test_task_sync():
    """测试任务状态同步功能"""
    print("="*60)
    print("🧪 测试任务状态同步功能")
    print("="*60)
    
    # 初始化飞书客户端
    print("1. 初始化飞书客户端...")
    if not init_lark_client():
        print("❌ 飞书客户端初始化失败")
        return
    
    print("✅ 飞书客户端初始化成功")
    
    # 显示当前统计
    print("\n2. 显示当前任务统计...")
    stats = get_task_completion_stats()
    print(f"📊 当前统计:")
    print(f"   • 总任务数: {stats['total_tasks']}")
    print(f"   • 已完成: {stats['completed_tasks']}")
    print(f"   • 待完成: {stats['pending_tasks']}")
    print(f"   • 完成率: {stats['completion_rate']}%")
    print(f"   • 未完成负责人数: {len(stats['pending_assignees'])}")
    
    # 显示未完成任务详情
    pending_tasks = get_pending_tasks_detail()
    if pending_tasks:
        print(f"\n📝 未完成任务详情:")
        for i, task in enumerate(pending_tasks[:5], 1):  # 只显示前5个
            print(f"   {i}. {task['title']}")
            print(f"      负责人: {', '.join(task['assignees'])}")
        if len(pending_tasks) > 5:
            print(f"      ... 还有 {len(pending_tasks) - 5} 个任务")
    else:
        print("\n📝 暂无未完成任务")
    
    # 执行任务状态同步
    print("\n3. 执行任务状态同步...")
    await sync_task_completion_status()
    
    # 显示同步后的统计
    print("\n4. 显示同步后的统计...")
    stats_after = get_task_completion_stats()
    print(f"📊 同步后统计:")
    print(f"   • 总任务数: {stats_after['total_tasks']}")
    print(f"   • 已完成: {stats_after['completed_tasks']}")
    print(f"   • 待完成: {stats_after['pending_tasks']}")
    print(f"   • 完成率: {stats_after['completion_rate']}%")
    print(f"   • 未完成负责人数: {len(stats_after['pending_assignees'])}")
    
    # 比较变化
    if stats_after['completed_tasks'] != stats['completed_tasks']:
        print(f"\n🔄 发现变化:")
        print(f"   • 已完成任务数变化: {stats['completed_tasks']} -> {stats_after['completed_tasks']}")
        print(f"   • 完成率变化: {stats['completion_rate']}% -> {stats_after['completion_rate']}%")
    else:
        print(f"\n✅ 统计无变化，任务状态已是最新")
    
    print("\n" + "="*60)
    print("🧪 测试完成")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_task_sync())
