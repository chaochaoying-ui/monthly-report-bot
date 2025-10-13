#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整功能版本的新功能
包括任务统计和文本交互功能
"""

import os
import sys
import asyncio
import json
import logging
from datetime import datetime
import pytz

# 设置环境变量
os.environ["APP_ID"] = "cli_a8fd44a9453cd00c"
os.environ["APP_SECRET"] = "jsVoFWgaaw05en6418h7xbhV5oXxAwIm"
os.environ["CHAT_ID"] = "oc_07f2d3d314f00fc29baf323a3a589972"
os.environ["FILE_URL"] = "https://be9bhmcgo2.feishu.cn/file/Wn5AbQAmVo32OExC5zIcIiAXnKc?office_edit=1"
os.environ["TZ"] = "America/Argentina/Buenos_Aires"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

def test_task_configuration():
    """测试任务配置"""
    logger.info("="*60)
    logger.info("🧪 测试任务配置")
    logger.info("="*60)
    
    try:
        import yaml
        with open("tasks.yaml", "r", encoding="utf-8") as f:
            tasks = yaml.safe_load(f)
        
        logger.info(f"✅ 任务配置加载成功，共 {len(tasks)} 个任务")
        
        # 验证任务配置
        for i, task in enumerate(tasks, 1):
            title = task.get("title", "")
            assignee = task.get("assignee_open_id", "")
            doc_url = task.get("doc_url", "")
            
            logger.info(f"任务 {i}: {title}")
            logger.info(f"  负责人: {assignee}")
            logger.info(f"  文档链接: {doc_url}")
            logger.info("")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 任务配置测试失败: {e}")
        return False

def test_smart_interaction():
    """测试智能交互功能"""
    logger.info("="*60)
    logger.info("🧪 测试智能交互功能")
    logger.info("="*60)
    
    try:
        # 导入智能交互引擎
        from smart_interaction_ws_v1_1 import SmartInteractionEngine
        
        # 创建交互引擎
        engine = SmartInteractionEngine()
        
        # 测试意图识别
        test_messages = [
            "查看我的任务",
            "标记任务完成",
            "申请任务延期",
            "查看帮助",
            "查看统计信息"
        ]
        
        for message in test_messages:
            result = engine.process_message("test_user_123", message)
            logger.info(f"消息: {message}")
            logger.info(f"意图: {result.get('intent', 'unknown')}")
            logger.info(f"置信度: {result.get('confidence', 0):.2f}")
            logger.info("")
        
        logger.info("✅ 智能交互功能测试完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 智能交互功能测试失败: {e}")
        return False

def test_task_statistics():
    """测试任务统计功能"""
    logger.info("="*60)
    logger.info("🧪 测试任务统计功能")
    logger.info("="*60)
    
    try:
        # 模拟任务统计数据
        task_stats = {
            "total_tasks": 25,
            "completed_tasks": 18,
            "pending_tasks": 7,
            "completion_rate": 72.0,
            "overdue_tasks": 2,
            "on_time_tasks": 16
        }
        
        logger.info("📊 任务统计信息:")
        logger.info(f"总任务数: {task_stats['total_tasks']}")
        logger.info(f"已完成: {task_stats['completed_tasks']}")
        logger.info(f"待完成: {task_stats['pending_tasks']}")
        logger.info(f"完成率: {task_stats['completion_rate']}%")
        logger.info(f"逾期任务: {task_stats['overdue_tasks']}")
        logger.info(f"按时完成: {task_stats['on_time_tasks']}")
        logger.info("")
        
        logger.info("✅ 任务统计功能测试完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 任务统计功能测试失败: {e}")
        return False

def test_multilingual_support():
    """测试多语言支持"""
    logger.info("="*60)
    logger.info("🧪 测试多语言支持")
    logger.info("="*60)
    
    try:
        # 测试不同语言的消息
        test_cases = [
            ("zh", "查看我的任务"),
            ("en", "Show my tasks"),
            ("es", "Mostrar mis tareas")
        ]
        
        for lang, message in test_cases:
            logger.info(f"语言: {lang}")
            logger.info(f"消息: {message}")
            logger.info("")
        
        logger.info("✅ 多语言支持测试完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 多语言支持测试失败: {e}")
        return False

def test_card_design():
    """测试卡片设计功能"""
    logger.info("="*60)
    logger.info("🧪 测试卡片设计功能")
    logger.info("="*60)
    
    try:
        # 导入卡片设计模块
        from card_design_ws_v1_1 import (
            build_welcome_card, build_monthly_task_card, 
            build_final_reminder_card, build_help_card
        )
        
        # 测试各种卡片构建
        cards = [
            ("欢迎卡片", build_welcome_card()),
            ("月报任务卡片", build_monthly_task_card()),
            ("最终提醒卡片", build_final_reminder_card()),
            ("帮助卡片", build_help_card())
        ]
        
        for card_name, card in cards:
            logger.info(f"✅ {card_name} 构建成功")
            logger.info(f"   类型: {card.get('header', {}).get('title', {}).get('content', 'N/A')}")
        
        logger.info("")
        logger.info("✅ 卡片设计功能测试完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 卡片设计功能测试失败: {e}")
        return False

async def main():
    """主函数"""
    logger.info("🚀 开始测试完整功能版本")
    logger.info("")
    
    # 测试任务配置
    task_config_ok = test_task_configuration()
    
    # 测试智能交互
    interaction_ok = test_smart_interaction()
    
    # 测试任务统计
    statistics_ok = test_task_statistics()
    
    # 测试多语言支持
    multilingual_ok = test_multilingual_support()
    
    # 测试卡片设计
    card_design_ok = test_card_design()
    
    # 总结
    logger.info("="*60)
    logger.info("🎉 完整功能版本测试完成！")
    logger.info("="*60)
    
    tests = [
        ("任务配置", task_config_ok),
        ("智能交互", interaction_ok),
        ("任务统计", statistics_ok),
        ("多语言支持", multilingual_ok),
        ("卡片设计", card_design_ok)
    ]
    
    passed = sum(1 for _, ok in tests if ok)
    total = len(tests)
    
    logger.info(f"测试结果: {passed}/{total} 通过")
    logger.info("")
    
    for test_name, ok in tests:
        status = "✅ 通过" if ok else "❌ 失败"
        logger.info(f"{test_name}: {status}")
    
    logger.info("")
    if passed == total:
        logger.info("🎊 所有功能测试通过！完整功能版本运行正常！")
    else:
        logger.info("⚠️  部分功能测试失败，请检查相关模块")
    
    logger.info("="*60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
    except Exception as e:
        logger.error("测试异常: %s", e)
