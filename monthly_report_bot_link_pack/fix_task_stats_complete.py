#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 task_stats.json - 使用完整的23个任务数据
"""

import json
import os
import sys
from datetime import datetime

def load_complete_task_stats():
    """从本地完整文件加载数据"""
    # 完整的23个任务数据
    return {
        "current_month": "2025-10",
        "tasks": {
            "task_2025-10_1": {
                "title": "月报-工程计划及执行情况",
                "assignees": ["ou_b96c7ed4a604dc049569102d01c6c26d"],
                "category": "工程管理",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": True,
                "completed_at": "2025-10-21T10:00:00-03:00",
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_2": {
                "title": "月报-设计工作进展",
                "assignees": ["ou_07443a67428d8741eab5eac851b754b9"],
                "category": "设计",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": True,
                "completed_at": "2025-10-21T10:00:00-03:00",
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_3": {
                "title": "月报-本月其他工作进展-技术管理",
                "assignees": ["ou_b96c7ed4a604dc049569102d01c6c26d"],
                "category": "技术管理",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": True,
                "completed_at": "2025-10-21T10:00:00-03:00",
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_4": {
                "title": "月报-存在的问题及措施-土建设计、总进度滞后方面、各分部工程进度、开工累计产值计划偏差方面",
                "assignees": ["ou_b96c7ed4a604dc049569102d01c6c26d"],
                "category": "工程管理",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": True,
                "completed_at": "2025-10-21T10:00:00-03:00",
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_5": {
                "title": "月报-下月工作计划及安排-进度及产值方面",
                "assignees": ["ou_b96c7ed4a604dc049569102d01c6c26d"],
                "category": "工程管理",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": True,
                "completed_at": "2025-10-21T10:00:00-03:00",
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_6": {
                "title": "月报-现场施工照片",
                "assignees": ["ou_a9c22d7a23ff6dd0e3dc1a93b2763b5a"],
                "category": "施工",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": False,
                "completed_at": None,
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_7": {
                "title": "月报-设计工作进展情况-机电工程",
                "assignees": ["ou_66ef2e056d0425ac560717a8b80395c3"],
                "category": "设计",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": False,
                "completed_at": None,
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_8": {
                "title": "月报-采购工作进展情况-永久机电材料和成套设备采",
                "assignees": ["ou_49299becc523c8d3aa1120261f1e2bcd"],
                "category": "采购",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": False,
                "completed_at": None,
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_9": {
                "title": "月报-存在的问题及措施-现场施工方面",
                "assignees": ["ou_5199fde738bcaedd5fcf4555b0adf7a0"],
                "category": "施工",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": False,
                "completed_at": None,
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_10": {
                "title": "月报-本月其他工作进展-安质环管理",
                "assignees": ["ou_33d81ce8839d93132e4417530f60c4a9"],
                "category": "安全质量",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": True,
                "completed_at": "2025-10-22T09:26:00-03:00",
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_11": {
                "title": "月报-下月工作计划及安排-安全、质量及环保方面",
                "assignees": ["ou_33d81ce8839d93132e4417530f60c4a9"],
                "category": "安全质量",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": True,
                "completed_at": "2025-10-22T09:26:00-03:00",
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_12": {
                "title": "月报-项目主材当月出入库及库存情况",
                "assignees": ["ou_f5338c49049621c36310e2215204d0be"],
                "category": "物资管理",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": False,
                "completed_at": None,
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_13": {
                "title": "月报-本月其他工作进展（设备管理）",
                "assignees": ["ou_50c492f1d2b2ee2107c4e28ab4416732"],
                "category": "设备管理",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": False,
                "completed_at": None,
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_14": {
                "title": "月报-项目人员信息统计表",
                "assignees": ["ou_2f93cb9407ca5a281a92d1f5a72fdf7b"],
                "category": "人力资源",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": False,
                "completed_at": None,
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_15": {
                "title": "月报-本月其他工作进展-项目部制度建设、劳务管理、公共关系建立及维护",
                "assignees": ["ou_d85dd7bb7625ab3e3f8b129e54934aea"],
                "category": "行政管理",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": False,
                "completed_at": None,
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_16": {
                "title": "月报-总部监管意见的响应落实情况-工会补充协议",
                "assignees": ["ou_c9d7859417eb0344b310fcff095fa639"],
                "category": "合规管理",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": False,
                "completed_at": None,
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_17": {
                "title": "月报-\"两金\"情况-现金流情况、营业收入完成情况",
                "assignees": ["ou_3b14801caa065a0074c7d6db8603f288"],
                "category": "财务",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": True,
                "completed_at": "2025-10-22T09:26:00-03:00",
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_18": {
                "title": "月报-\"本月其他工作进展-税务管理",
                "assignees": ["ou_3b14801caa065a0074c7d6db8603f288"],
                "category": "财务",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": True,
                "completed_at": "2025-10-22T09:26:00-03:00",
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_19": {
                "title": "月报-主合同备忘录MOU工作进展",
                "assignees": ["ou_0bbab538833c35081e8f5c3ef213e17e"],
                "category": "合同管理",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": False,
                "completed_at": None,
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_20": {
                "title": "月报-总部监管意见的响应落实情况-谅解备忘录相关事项",
                "assignees": ["ou_0bbab538833c35081e8f5c3ef213e17e"],
                "category": "合同管理",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": False,
                "completed_at": None,
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_21": {
                "title": "月报-结算支付情况",
                "assignees": ["ou_17b6bee82dd946d92a322cc7dea40eb7"],
                "category": "财务",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": False,
                "completed_at": None,
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_22": {
                "title": "月报-采购执行情况部分",
                "assignees": ["ou_9847326a1fea8db87079101775bd97a9"],
                "category": "采购",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": False,
                "completed_at": None,
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            },
            "task_2025-10_23": {
                "title": "月报-分包合同结算支付情况",
                "assignees": ["ou_9847326a1fea8db87079101775bd97a9"],
                "category": "合同管理",
                "created_at": "2025-10-17T09:00:00-03:00",
                "completed": False,
                "completed_at": None,
                "doc_url": "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
            }
        },
        "total_tasks": 23,
        "completed_tasks": 9,
        "completion_rate": 39.13,
        "last_update": datetime.now().isoformat()
    }

def backup_current_file():
    """备份当前的 task_stats.json"""
    if os.path.exists("task_stats.json"):
        backup_name = f"task_stats.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            os.rename("task_stats.json", backup_name)
            print(f"✅ 已备份旧文件: {backup_name}")
            return True
        except Exception as e:
            print(f"⚠️  备份失败: {e}")
            return False
    else:
        print("⚠️  task_stats.json 文件不存在，将创建新文件")
        return False

def write_complete_stats():
    """写入完整的23个任务统计数据"""
    try:
        stats = load_complete_task_stats()
        with open("task_stats.json", "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print("✅ 已写入完整的23个任务统计数据")
        return True
    except Exception as e:
        print(f"❌ 写入失败: {e}")
        return False

def verify_stats():
    """验证写入的数据"""
    try:
        with open("task_stats.json", "r", encoding="utf-8") as f:
            stats = json.load(f)

        print("\n" + "="*60)
        print("📊 任务统计验证")
        print("="*60)
        print(f"当前月份: {stats.get('current_month')}")
        print(f"总任务数: {stats.get('total_tasks')}")
        print(f"已完成: {stats.get('completed_tasks')}")
        print(f"完成率: {stats.get('completion_rate')}%")

        # 统计已完成人员
        completed_users = {}
        user_mapping = {
            "ou_b96c7ed4a604dc049569102d01c6c26d": "刘野",
            "ou_07443a67428d8741eab5eac851b754b9": "范明杰",
            "ou_3b14801caa065a0074c7d6db8603f288": "袁阿虎",
            "ou_33d81ce8839d93132e4417530f60c4a9": "高雅慧",
        }

        for task_id, task_info in stats['tasks'].items():
            if task_info.get('completed', False):
                for assignee in task_info.get('assignees', []):
                    user_name = user_mapping.get(assignee, f"用户{assignee[:8]}")
                    completed_users[user_name] = completed_users.get(user_name, 0) + 1

        print("\n📋 已完成人员排行:")
        sorted_users = sorted(completed_users.items(), key=lambda x: x[1], reverse=True)
        for i, (name, count) in enumerate(sorted_users, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"   {medal} #{i} {name}: {count}个任务")

        print("="*60)
        return True

    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def main():
    print("="*60)
    print("🔧 修复 task_stats.json - 完整的23个任务")
    print("="*60)
    print()

    # 备份当前文件
    backup_current_file()

    # 写入完整数据
    if write_complete_stats():
        # 验证数据
        verify_stats()
        print()
        print("="*60)
        print("✅ 修复完成！")
        print("="*60)
        print()
        print("📊 数据概览:")
        print("  - 总任务数: 23个")
        print("  - 已完成: 9个")
        print("  - 待完成: 14个")
        print("  - 完成率: 39.13%")
        print()
        print("下一步:")
        print("1. 运行测试: python3 test_chart_generator.py")
        print("2. 重启服务: sudo systemctl restart monthly-report-bot-interactive.service")
        return 0
    else:
        print()
        print("="*60)
        print("❌ 修复失败！")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
