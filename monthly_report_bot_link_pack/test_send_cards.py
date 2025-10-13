#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试发送各种卡片到群里
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入最终版的功能
from monthly_report_bot_final import (
    init_lark_client,
    send_card_to_chat,
    send_text_to_chat,
    build_task_creation_card,
    build_daily_reminder_card,
    build_final_reminder_card,
    build_final_stats_card
)

async def test_send_cards():
    """测试发送各种卡片"""
    print("="*60)
    print("🧪 测试发送任务卡片到群里")
    print("="*60)
    
    # 初始化飞书客户端
    print("1. 初始化飞书客户端...")
    if not init_lark_client():
        print("❌ 飞书客户端初始化失败")
        return
    
    print("✅ 飞书客户端初始化成功")
    
    # 发送测试通知
    print("\n2. 发送测试通知...")
    await send_text_to_chat("🧪 开始测试任务卡片发送...")
    
    # 发送任务创建卡片
    print("\n3. 发送任务创建卡片...")
    task_creation_card = build_task_creation_card()
    success = await send_card_to_chat(task_creation_card)
    if success:
        print("✅ 任务创建卡片发送成功")
    else:
        print("❌ 任务创建卡片发送失败")
    
    await asyncio.sleep(2)  # 等待2秒
    
    # 发送每日提醒卡片
    print("\n4. 发送每日提醒卡片...")
    daily_reminder_card = build_daily_reminder_card()
    success = await send_card_to_chat(daily_reminder_card)
    if success:
        print("✅ 每日提醒卡片发送成功")
    else:
        print("❌ 每日提醒卡片发送失败")
    
    await asyncio.sleep(2)  # 等待2秒
    
    # 发送最终催办卡片
    print("\n5. 发送最终催办卡片...")
    final_reminder_card = build_final_reminder_card()
    success = await send_card_to_chat(final_reminder_card)
    if success:
        print("✅ 最终催办卡片发送成功")
    else:
        print("❌ 最终催办卡片发送失败")
    
    await asyncio.sleep(2)  # 等待2秒
    
    # 发送最终统计卡片
    print("\n6. 发送最终统计卡片...")
    final_stats_card = build_final_stats_card()
    success = await send_card_to_chat(final_stats_card)
    if success:
        print("✅ 最终统计卡片发送成功")
    else:
        print("❌ 最终统计卡片发送失败")
    
    # 发送完成通知
    print("\n7. 发送测试完成通知...")
    await send_text_to_chat("✅ 任务卡片测试完成！请查看上面的4种卡片效果。")
    
    print("\n" + "="*60)
    print("🧪 测试完成")
    print("="*60)
    print("📱 请到群里查看卡片效果：")
    print("   • 任务创建卡片（蓝色）")
    print("   • 每日提醒卡片（橙色）")
    print("   • 最终催办卡片（红色）")
    print("   • 最终统计卡片（绿色）")

if __name__ == "__main__":
    asyncio.run(test_send_cards())
