#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试创建任务 - 按照tasks.yaml配置创建24个任务
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入最终版的功能
from monthly_report_bot_final import (
    init_lark_client,
    send_card_to_chat,
    send_text_to_chat,
    build_task_creation_card,
    load_tasks,
    update_task_completion,
    get_task_completion_stats
)

async def test_create_tasks():
    """测试创建任务"""
    print("="*60)
    print("🧪 测试创建任务 - 按照tasks.yaml配置")
    print("="*60)
    
    # 初始化飞书客户端
    print("1. 初始化飞书客户端...")
    if not init_lark_client():
        print("❌ 飞书客户端初始化失败")
        return
    
    print("✅ 飞书客户端初始化成功")
    
    # 加载任务配置
    print("\n2. 加载任务配置...")
    tasks = load_tasks()
    if not tasks:
        print("❌ 没有找到任务配置")
        return
    
    print(f"✅ 成功加载 {len(tasks)} 个任务配置")
    
    # 显示任务配置
    print("\n3. 任务配置详情:")
    for i, task in enumerate(tasks, 1):
        assignees = task.get('assignee_open_id', [])
        if isinstance(assignees, str):
            assignees = [assignees]
        assignee_count = len([a for a in assignees if a and a.strip()])
        print(f"   {i:2d}. {task['title']}")
        print(f"       负责人: {assignee_count} 人")
        print(f"       文档: {task['doc_url']}")
    
    # 发送测试通知
    print("\n4. 发送测试通知...")
    await send_text_to_chat("🧪 开始测试任务创建功能...")
    
    # 模拟创建任务（不实际创建，只更新统计）
    print("\n5. 模拟创建任务...")
    current_month = "2025-01"  # 模拟1月份
    success_count = 0
    
    for i, task_config in enumerate(tasks):
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
            
            # 模拟任务ID
            task_id = f"test_task_{i+1:03d}"
            
            # 更新统计（模拟任务创建）
            update_task_completion(task_id, task_config['title'], assignees, False)
            success_count += 1
            
            print(f"   ✅ 任务 {i+1:2d}: {task_config['title']}")
            print(f"       负责人: {len(assignees)} 人")
            
        except Exception as e:
            print(f"   ❌ 任务 {i+1}: {task_config.get('title', 'Unknown')} - {e}")
    
    print(f"\n✅ 成功模拟创建 {success_count} 个任务")
    
    # 获取统计信息
    print("\n6. 获取任务统计...")
    stats = get_task_completion_stats()
    print(f"📊 任务统计:")
    print(f"   • 总任务数: {stats['total_tasks']}")
    print(f"   • 已完成: {stats['completed_tasks']}")
    print(f"   • 待完成: {stats['pending_tasks']}")
    print(f"   • 完成率: {stats['completion_rate']}%")
    print(f"   • 未完成负责人数: {len(stats['pending_assignees'])}")
    
    # 发送任务创建卡片
    print("\n7. 发送任务创建卡片...")
    task_creation_card = build_task_creation_card()
    success = await send_card_to_chat(task_creation_card)
    if success:
        print("✅ 任务创建卡片发送成功")
    else:
        print("❌ 任务创建卡片发送失败")
    
    # 发送完成通知
    print("\n8. 发送测试完成通知...")
    await send_text_to_chat(f"✅ 任务创建测试完成！\n📊 统计: 总任务 {stats['total_tasks']} 个，待完成 {stats['pending_tasks']} 个")
    
    print("\n" + "="*60)
    print("🧪 测试完成")
    print("="*60)
    print("📱 请到群里查看任务创建卡片效果")
    print("📊 任务统计已更新，可以测试其他功能")

if __name__ == "__main__":
    asyncio.run(test_create_tasks())
