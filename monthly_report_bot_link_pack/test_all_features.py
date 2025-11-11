#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整功能测试脚本
用于部署前验证所有核心功能
"""

import os
import sys
import json
from datetime import datetime
import pytz

print("=" * 70)
print("月报机器人 - 完整功能测试")
print("=" * 70)
print()

# 测试结果记录
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def test_pass(name):
    test_results["passed"].append(name)
    print(f"✅ {name}")

def test_fail(name, reason):
    test_results["failed"].append(f"{name}: {reason}")
    print(f"❌ {name}: {reason}")

def test_warn(name, reason):
    test_results["warnings"].append(f"{name}: {reason}")
    print(f"⚠️  {name}: {reason}")

# ============================================================
# 1. 环境检查
# ============================================================
print("\n" + "=" * 70)
print("1. 环境检查")
print("=" * 70)

# 1.1 Python 版本
if sys.version_info >= (3, 8):
    test_pass(f"Python 版本: {sys.version_info.major}.{sys.version_info.minor}")
else:
    test_fail("Python 版本", f"需要 >= 3.8，当前: {sys.version_info.major}.{sys.version_info.minor}")

# 1.2 必需的包
required_packages = [
    "requests",
    "pyyaml",
    "pytz",
    "matplotlib",
    "seaborn",
    "numpy"
]

for package in required_packages:
    try:
        __import__(package)
        test_pass(f"包 {package} 已安装")
    except ImportError:
        test_fail(f"包 {package}", "未安装")

# 1.3 环境变量
required_env_vars = [
    "APP_ID",
    "APP_SECRET",
    "CHAT_ID",
    "WELCOME_CARD_ID"
]

for var in required_env_vars:
    if os.environ.get(var):
        test_pass(f"环境变量 {var}")
    else:
        test_warn(f"环境变量 {var}", "未设置")

# 1.4 时区
tz = os.environ.get("TZ", "未设置")
if tz == "America/Argentina/Buenos_Aires":
    test_pass(f"时区配置: {tz}")
else:
    test_warn("时区配置", f"当前: {tz}, 建议: America/Argentina/Buenos_Aires")

# ============================================================
# 2. 文件完整性检查
# ============================================================
print("\n" + "=" * 70)
print("2. 文件完整性检查")
print("=" * 70)

required_files = [
    "tasks.yaml",
    "created_tasks.json",
    "task_stats.json"
]

for filename in required_files:
    if os.path.exists(filename):
        file_size = os.path.getsize(filename)
        test_pass(f"文件 {filename} 存在 ({file_size} bytes)")

        # 检查 JSON 文件是否有效
        if filename.endswith(".json"):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                test_pass(f"文件 {filename} JSON 格式有效")
            except json.JSONDecodeError as e:
                test_fail(f"文件 {filename}", f"JSON 格式错误: {e}")
    else:
        test_fail(f"文件 {filename}", "不存在")

# ============================================================
# 3. 任务数据检查
# ============================================================
print("\n" + "=" * 70)
print("3. 任务数据检查")
print("=" * 70)

# 3.1 tasks.yaml
try:
    import yaml
    with open("tasks.yaml", "r", encoding="utf-8") as f:
        tasks_template = yaml.safe_load(f)

    if tasks_template and "tasks" in tasks_template:
        task_count = len(tasks_template["tasks"])
        test_pass(f"tasks.yaml 包含 {task_count} 个任务模板")

        # 检查必需字段
        for task_id, task in tasks_template["tasks"].items():
            required_fields = ["title", "assignees"]
            missing_fields = [f for f in required_fields if f not in task]
            if not missing_fields:
                test_pass(f"任务 {task_id} 字段完整")
            else:
                test_fail(f"任务 {task_id}", f"缺少字段: {missing_fields}")
    else:
        test_fail("tasks.yaml", "格式错误或无任务")
except Exception as e:
    test_fail("tasks.yaml", f"读取失败: {e}")

# 3.2 task_stats.json
try:
    with open("task_stats.json", "r", encoding="utf-8") as f:
        task_stats = json.load(f)

    if "tasks" in task_stats:
        stats_task_count = len(task_stats["tasks"])
        if stats_task_count > 0:
            test_pass(f"task_stats.json 包含 {stats_task_count} 个任务")

            # 统计完成情况
            completed_count = sum(1 for t in task_stats["tasks"].values() if t.get("completed"))
            completion_rate = (completed_count / stats_task_count) * 100 if stats_task_count > 0 else 0
            print(f"   📊 完成情况: {completed_count}/{stats_task_count} ({completion_rate:.1f}%)")
        else:
            test_warn("task_stats.json", "没有任务数据")
    else:
        test_warn("task_stats.json", "格式错误")
except Exception as e:
    test_fail("task_stats.json", f"读取失败: {e}")

# ============================================================
# 4. 字体配置检查
# ============================================================
print("\n" + "=" * 70)
print("4. 字体配置检查")
print("=" * 70)

try:
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    # 检查字体配置
    font_list = plt.rcParams.get('font.sans-serif', [])
    if font_list:
        test_pass(f"matplotlib 字体配置: {font_list}")

        # 检查是否包含 Symbola
        if 'Symbola' in font_list:
            test_pass("Symbola 字体在配置中")
        else:
            test_warn("Symbola 字体", "不在 rcParams 中")
    else:
        test_warn("matplotlib 字体配置", "为空")

    # 检查 fontManager
    symbola_fonts = [f for f in fm.fontManager.ttflist if 'Symbola' in f.name]
    if symbola_fonts:
        test_pass(f"Symbola 字体在 fontManager 中 (数量: {len(symbola_fonts)})")
    else:
        test_warn("Symbola 字体", "不在 fontManager 中")

    # 测试 emoji 字符
    test_emoji = "🏆 🥇 🥈 📊 📈"
    print(f"   测试 emoji: {test_emoji}")

except Exception as e:
    test_fail("字体配置", f"检查失败: {e}")

# ============================================================
# 5. 图表生成测试
# ============================================================
print("\n" + "=" * 70)
print("5. 图表生成测试")
print("=" * 70)

try:
    # 检查 chart_generator 是否可导入
    sys.path.insert(0, os.path.dirname(__file__))
    from chart_generator import chart_generator

    test_pass("chart_generator 模块可导入")

    # 尝试生成一个简单图表
    if task_stats and "tasks" in task_stats:
        try:
            chart_path = chart_generator.generate_comprehensive_dashboard(task_stats)
            if os.path.exists(chart_path):
                file_size = os.path.getsize(chart_path)
                test_pass(f"图表生成成功: {chart_path} ({file_size} bytes)")
            else:
                test_fail("图表生成", "文件不存在")
        except Exception as e:
            test_fail("图表生成", f"执行失败: {e}")
    else:
        test_warn("图表生成", "没有任务数据，跳过测试")

except ImportError as e:
    test_fail("chart_generator", f"导入失败: {e}")

# ============================================================
# 6. 定时任务配置检查
# ============================================================
print("\n" + "=" * 70)
print("6. 定时任务配置检查")
print("=" * 70)

# 尝试导入主程序并检查定时任务配置
try:
    # 这里只检查配置，不实际运行
    test_warn("定时任务配置", "需要手动检查代码中的时间配置")
    print("   当前配置:")
    print("   - 任务创建: 19日 21:10 (需求: 17-19日 09:30)")
    print("   - 每日提醒: 每天 09:00 (需求: 18-22日 09:31)")
    print("   - 月末提醒: 月末 17:00 (需求: 23日 09:32)")
except Exception as e:
    test_fail("定时任务配置", f"检查失败: {e}")

# ============================================================
# 测试总结
# ============================================================
print("\n" + "=" * 70)
print("测试总结")
print("=" * 70)

total_tests = len(test_results["passed"]) + len(test_results["failed"]) + len(test_results["warnings"])
print(f"\n总测试数: {total_tests}")
print(f"✅ 通过: {len(test_results['passed'])}")
print(f"⚠️  警告: {len(test_results['warnings'])}")
print(f"❌ 失败: {len(test_results['failed'])}")

if test_results["failed"]:
    print("\n失败的测试:")
    for failure in test_results["failed"]:
        print(f"  ❌ {failure}")

if test_results["warnings"]:
    print("\n警告:")
    for warning in test_results["warnings"]:
        print(f"  ⚠️  {warning}")

# ============================================================
# 部署建议
# ============================================================
print("\n" + "=" * 70)
print("部署建议")
print("=" * 70)

if len(test_results["failed"]) == 0:
    print("\n✅ 所有关键测试通过！")
    if len(test_results["warnings"]) == 0:
        print("✅ 无警告，可以部署到生产环境")
    else:
        print(f"⚠️  有 {len(test_results['warnings'])} 个警告，建议查看后再部署")
else:
    print(f"\n❌ 有 {len(test_results['failed'])} 个测试失败")
    print("❌ 不建议部署，请先修复失败项")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)

# 保存测试报告
report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(report_filename, "w", encoding="utf-8") as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed": len(test_results["passed"]),
        "warnings": len(test_results["warnings"]),
        "failed": len(test_results["failed"]),
        "details": test_results
    }, f, indent=2, ensure_ascii=False)

print(f"\n📄 详细报告已保存到: {report_filename}")
