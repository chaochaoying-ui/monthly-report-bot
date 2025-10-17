#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试任务数据
用于测试每日统计功能
"""

import os
import json
from datetime import datetime

# 文件路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_STATS_FILE = os.path.join(BASE_DIR, "task_stats.json")
CREATED_TASKS_FILE = os.path.join(BASE_DIR, "created_tasks.json")

def create_test_data():
    """创建测试任务数据"""
    current_month = datetime.now().strftime("%Y-%m")

    # 创建测试任务统计数据
    task_stats = {
        "current_month": current_month,
        "tasks": {
            "task_2025-10_1": {
                "title": "完成月度技术方案设计",
                "assignees": ["ou_17b6bee82dd946d92a322cc7dea40eb7"],
                "created_at": "2025-10-17T09:30:00-03:00",
                "completed": True,
                "completed_at": "2025-10-17T14:20:00-03:00"
            },
            "task_2025-10_2": {
                "title": "撰写项目进度报告",
                "assignees": ["ou_03491624846d90ea22fa64177860a8cf"],
                "created_at": "2025-10-17T09:30:00-03:00",
                "completed": True,
                "completed_at": "2025-10-17T15:10:00-03:00"
            },
            "task_2025-10_3": {
                "title": "代码审查与优化",
                "assignees": ["ou_7552fdb195c3ad2c0453258fb157c12a"],
                "created_at": "2025-10-17T09:30:00-03:00",
                "completed": False,
                "completed_at": None
            },
            "task_2025-10_4": {
                "title": "系统测试报告",
                "assignees": ["ou_145eca14d330bb8162c45536538d6764"],
                "created_at": "2025-10-17T09:30:00-03:00",
                "completed": True,
                "completed_at": "2025-10-17T16:05:00-03:00"
            },
            "task_2025-10_5": {
                "title": "用户培训文档",
                "assignees": ["ou_0bbab538833c35081e8f5c3ef213e17e"],
                "created_at": "2025-10-17T09:30:00-03:00",
                "completed": False,
                "completed_at": None
            },
            "task_2025-10_6": {
                "title": "性能优化方案",
                "assignees": ["ou_f5338c49049621c36310e2215204d0be"],
                "created_at": "2025-10-17T09:30:00-03:00",
                "completed": True,
                "completed_at": "2025-10-17T13:45:00-03:00"
            },
            "task_2025-10_7": {
                "title": "安全漏洞修复",
                "assignees": ["ou_2f93cb9407ca5a281a92d1f5a72fdf7b"],
                "created_at": "2025-10-17T09:30:00-03:00",
                "completed": False,
                "completed_at": None
            },
            "task_2025-10_8": {
                "title": "数据备份检查",
                "assignees": ["ou_07443a67428d8741eab5eac851b754b9"],
                "created_at": "2025-10-17T09:30:00-03:00",
                "completed": True,
                "completed_at": "2025-10-17T12:30:00-03:00"
            },
            "task_2025-10_9": {
                "title": "API文档更新",
                "assignees": ["ou_a9c22d7a23ff6dd0e3dc1a93b2763b5a"],
                "created_at": "2025-10-17T09:30:00-03:00",
                "completed": False,
                "completed_at": None
            },
            "task_2025-10_10": {
                "title": "客户需求分析",
                "assignees": ["ou_66ef2e056d0425ac560717a8b80395c3"],
                "created_at": "2025-10-17T09:30:00-03:00",
                "completed": True,
                "completed_at": "2025-10-17T11:15:00-03:00"
            }
        },
        "total_tasks": 10,
        "completed_tasks": 6,
        "completion_rate": 60.0,
        "last_update": datetime.now().isoformat()
    }

    # 保存任务统计数据
    with open(TASK_STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(task_stats, f, ensure_ascii=False, indent=2)

    print("[OK] Test task stats data created: " + TASK_STATS_FILE)
    print("   - Total tasks: " + str(task_stats['total_tasks']))
    print("   - Completed: " + str(task_stats['completed_tasks']))
    print("   - Completion rate: " + str(task_stats['completion_rate']) + "%")

    # 创建任务记录
    created_tasks = {
        current_month: True
    }

    with open(CREATED_TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(created_tasks, f, ensure_ascii=False, indent=2)

    print("[OK] Task record created: " + CREATED_TASKS_FILE)
    print("   - Current month: " + current_month)

if __name__ == "__main__":
    print("="*60)
    print("Create Test Task Data")
    print("="*60)
    print()

    create_test_data()

    print()
    print("="*60)
    print("Test data created successfully!")
    print("You can now run test_daily_stats.bat to test the feature")
    print("="*60)

