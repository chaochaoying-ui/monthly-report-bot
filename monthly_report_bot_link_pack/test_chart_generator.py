#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图表生成功能
"""

import json
import os
import sys
import io

# 强制设置标准输出编码为 UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chart_generator import chart_generator

def load_task_stats():
    """加载任务统计数据"""
    stats_file = os.path.join(os.path.dirname(__file__), "task_stats.json")

    if not os.path.exists(stats_file):
        print(f"❌ 任务统计文件不存在: {stats_file}")
        return None

    try:
        with open(stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
        print(f"✅ 成功加载任务统计数据")
        print(f"   - 当前月份: {stats.get('current_month', 'N/A')}")
        print(f"   - 总任务数: {stats.get('total_tasks', 0)}")
        print(f"   - 已完成: {stats.get('completed_tasks', 0)}")
        print(f"   - 完成率: {stats.get('completion_rate', 0)}%")
        return stats
    except Exception as e:
        print(f"❌ 加载任务统计数据失败: {e}")
        return None

def test_comprehensive_dashboard():
    """测试综合仪表板生成"""
    print("\n" + "="*60)
    print("测试：生成美化版综合仪表板（包含已完成人员排行榜）")
    print("="*60)

    # 加载真实数据
    stats = load_task_stats()
    if not stats:
        return False

    # 统计已完成人员信息
    completed_users = {}
    tasks = stats.get('tasks', {})

    user_mapping = {
        "ou_b96c7ed4a604dc049569102d01c6c26d": "刘野",
        "ou_07443a67428d8741eab5eac851b754b9": "范明杰",
        "ou_3b14801caa065a0074c7d6db8603f288": "袁阿虎",
        "ou_33d81ce8839d93132e4417530f60c4a9": "高雅慧",
    }

    for task_id, task_info in tasks.items():
        if task_info.get('completed', False):
            for assignee in task_info.get('assignees', []):
                user_name = user_mapping.get(assignee, f"用户{assignee[:8]}")
                completed_users[user_name] = completed_users.get(user_name, 0) + 1

    print(f"\n📊 已完成人员统计:")
    sorted_users = sorted(completed_users.items(), key=lambda x: x[1], reverse=True)
    for i, (name, count) in enumerate(sorted_users, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"   {medal} #{i} {name}: {count}个任务")

    try:
        print(f"\n🎨 开始生成综合仪表板...")
        chart_path = chart_generator.generate_comprehensive_dashboard(stats)

        if chart_path and os.path.exists(chart_path):
            print(f"✅ 综合仪表板生成成功!")
            print(f"   📁 文件路径: {chart_path}")
            print(f"   📏 文件大小: {os.path.getsize(chart_path) / 1024:.2f} KB")

            # 获取绝对路径
            abs_path = os.path.abspath(chart_path)
            print(f"   🔗 绝对路径: {abs_path}")

            return True
        else:
            print(f"❌ 综合仪表板生成失败")
            return False

    except Exception as e:
        print(f"❌ 生成过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("="*60)
    print("🧪 图表生成器测试")
    print("="*60)

    success = test_comprehensive_dashboard()

    print("\n" + "="*60)
    if success:
        print("✅ 测试完成 - 所有功能正常")
    else:
        print("❌ 测试失败 - 请检查错误信息")
    print("="*60)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
