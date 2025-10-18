#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动触发任务创建的测试脚本
用于在 GCP 上测试任务创建功能
"""

import sys
import os
import asyncio

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monthly_report_bot_link_pack'))

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv('monthly_report_bot_link_pack/.env')
except:
    pass

# 导入主程序
from monthly_report_bot_link_pack import monthly_report_bot_final_interactive as bot

async def main():
    print("=" * 60)
    print("手动触发任务创建测试")
    print("=" * 60)

    # 初始化客户端
    if not bot.init_lark_client():
        print("❌ 飞书客户端初始化失败")
        return

    print("✅ 飞书客户端初始化成功")
    print(f"📅 当前月份: {bot.datetime.now(bot.TZ).strftime('%Y-%m')}")
    print(f"⏰ 当前时间: {bot.datetime.now(bot.TZ).strftime('%Y-%m-%d %H:%M:%S')}")

    # 检查当前任务状态
    stats = bot.get_task_completion_stats()
    print(f"\n当前任务统计:")
    print(f"  总任务数: {stats['total_tasks']}")
    print(f"  已完成: {stats['completed_tasks']}")
    print(f"  完成率: {stats['completion_rate']}%")

    # 手动创建任务
    print("\n开始创建任务...")
    success = await bot.create_monthly_tasks()

    if success:
        print("✅ 任务创建成功！")

        # 重新检查任务状态
        stats = bot.get_task_completion_stats()
        print(f"\n创建后的任务统计:")
        print(f"  总任务数: {stats['total_tasks']}")
        print(f"  已完成: {stats['completed_tasks']}")
        print(f"  完成率: {stats['completion_rate']}%")
    else:
        print("❌ 任务创建失败")

if __name__ == "__main__":
    asyncio.run(main())

