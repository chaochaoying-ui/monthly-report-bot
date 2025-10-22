#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试美化后的图表生成功能
"""

import sys
import os
import json

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from chart_generator import chart_generator

def test_beautified_dashboard():
    """测试美化版仪表板"""
    print("=" * 60)
    print("测试美化版综合仪表板生成")
    print("=" * 60)

    # 加载实际的task_stats.json数据
    try:
        with open('task_stats.json', 'r', encoding='utf-8') as f:
            stats = json.load(f)

        print(f"\n📊 加载的统计数据:")
        print(f"  - 总任务数: {stats.get('total_tasks', 0)}")
        print(f"  - 已完成: {stats.get('completed_tasks', 0)}")
        print(f"  - 完成率: {stats.get('completion_rate', 0)}%")
        print(f"  - 当前月份: {stats.get('current_month', 'N/A')}")

        # 生成美化版仪表板
        print("\n🎨 正在生成美化版综合仪表板...")
        chart_path = chart_generator.generate_comprehensive_dashboard(stats)

        if chart_path and os.path.exists(chart_path):
            print(f"✅ 图表生成成功!")
            print(f"📁 文件路径: {chart_path}")
            print(f"📏 文件大小: {os.path.getsize(chart_path) / 1024:.2f} KB")
            return True
        else:
            print("❌ 图表生成失败")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_beautified_dashboard()
    sys.exit(0 if success else 1)
