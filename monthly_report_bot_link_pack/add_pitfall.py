#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错题本更新工具 - 快速添加新的坑和解决方案
"""

import sys
from datetime import datetime

def get_severity_emoji(severity: str) -> str:
    """获取严重程度对应的emoji"""
    severity_map = {
        "高": "🔴",
        "中": "🟡",
        "低": "🟢"
    }
    return severity_map.get(severity, "🟡")

def generate_pitfall_entry():
    """交互式生成错题本条目"""
    print("=" * 60)
    print("错题本更新工具 - 添加新的坑")
    print("=" * 60)
    print()

    # 1. 选择类别
    print("选择类别:")
    categories = {
        "1": ("1", "核心架构问题"),
        "2": ("2", "部署相关问题"),
        "3": ("3", "环境变量问题"),
        "4": ("4", "飞书API调用问题"),
        "5": ("5", "数据同步问题"),
        "6": ("6", "字体和图表问题"),
        "7": ("7", "服务器运维问题"),
    }

    for key, (num, name) in categories.items():
        print(f"  {key}. {name}")

    category = input("\n请输入类别编号 (1-7): ").strip()
    if category not in categories:
        print("❌ 无效的类别编号")
        sys.exit(1)

    category_num, category_name = categories[category]

    # 2. 输入问题简述
    print()
    title = input("问题简述 (简短描述，如: 使用模拟任务ID而非真实GUID): ").strip()
    if not title:
        print("❌ 问题简述不能为空")
        sys.exit(1)

    # 3. 输入问题描述
    print()
    print("问题详细描述 (可以多行，输入空行结束):")
    description_lines = []
    while True:
        line = input()
        if not line:
            break
        description_lines.append(line)

    description = "\n".join(description_lines)
    if not description:
        print("❌ 问题描述不能为空")
        sys.exit(1)

    # 4. 输入影响
    print()
    print("影响 (一行一个，输入空行结束):")
    impacts = []
    while True:
        line = input("- ").strip()
        if not line:
            break
        impacts.append(f"- ❌ {line}")

    # 5. 输入根本原因
    print()
    root_cause = input("根本原因: ").strip()

    # 6. 输入错误尝试 (可选)
    print()
    has_wrong_attempts = input("是否有错误尝试? (y/n): ").strip().lower()
    wrong_attempts = ""
    if has_wrong_attempts == 'y':
        print("错误尝试 (可以多行，输入空行结束):")
        wrong_lines = []
        while True:
            line = input()
            if not line:
                break
            wrong_lines.append(line)
        wrong_attempts = "\n".join(wrong_lines)

    # 7. 输入正确做法
    print()
    print("正确做法 (可以多行，输入空行结束):")
    solution_lines = []
    while True:
        line = input()
        if not line:
            break
        solution_lines.append(line)

    solution = "\n".join(solution_lines)
    if not solution:
        print("❌ 正确做法不能为空")
        sys.exit(1)

    # 8. 输入关键点
    print()
    print("关键点 (一行一个，输入空行结束):")
    key_points = []
    while True:
        line = input("- ").strip()
        if not line:
            break
        # 判断是要点还是要避免的做法
        if line.startswith("不要") or line.startswith("避免") or line.startswith("❌"):
            key_points.append(f"{line}")
        else:
            key_points.append(f"✅ {line}")

    # 9. 选择严重程度
    print()
    print("严重程度:")
    print("  1. 高 (🔴) - 导致核心功能失效")
    print("  2. 中 (🟡) - 影响部分功能或体验")
    print("  3. 低 (🟢) - 小问题，容易修复")
    severity_choice = input("请选择 (1-3): ").strip()
    severity_map = {"1": "高", "2": "中", "3": "低"}
    severity = severity_map.get(severity_choice, "中")
    severity_emoji = get_severity_emoji(severity)

    # 10. 生成Markdown条目
    today = datetime.now().strftime("%Y-%m-%d")

    # 获取下一个子编号（需要手动确认）
    sub_num = input(f"\n在类别 #{category_num} 下的子编号 (如 1, 2, 3...): ").strip()

    entry = f"""
### ❌ 坑 #{category_num}.{sub_num}: {title}

**问题描述**:
{description}

**影响**:
{chr(10).join(impacts)}

**根本原因**:
{root_cause}
"""

    if wrong_attempts:
        entry += f"""
**❌ 错误尝试**:
{wrong_attempts}
"""

    entry += f"""
**✅ 正确做法**:
{solution}

**关键点**:
{chr(10).join(key_points)}

**修复时间**: {today}
**严重程度**: {severity_emoji} {severity}

---
"""

    # 11. 预览并确认
    print()
    print("=" * 60)
    print("生成的错题本条目预览:")
    print("=" * 60)
    print(entry)
    print("=" * 60)

    confirm = input("\n将此条目添加到 PITFALLS_AND_SOLUTIONS.md? (y/n): ").strip().lower()

    if confirm == 'y':
        # 读取现有文件
        with open('PITFALLS_AND_SOLUTIONS.md', 'r', encoding='utf-8') as f:
            content = f.read()

        # 在 "新增错误记录区" 下方添加
        marker = "_(每次遇到新问题后，在这里添加记录，然后移动到对应的章节)_"

        if marker in content:
            parts = content.split(marker)
            new_content = parts[0] + marker + "\n" + entry + "\n" + parts[1]
        else:
            # 如果找不到标记，添加到文件末尾
            new_content = content + "\n" + entry

        # 写回文件
        with open('PITFALLS_AND_SOLUTIONS.md', 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("\n✅ 已添加到 PITFALLS_AND_SOLUTIONS.md")
        print(f"📝 请手动将条目移动到 '## {category_num}. {category_name}' 章节下")
        print("📝 并更新相应的子编号")
    else:
        print("\n❌ 取消添加")

        # 保存到临时文件
        temp_file = f"pitfall_draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(entry)
        print(f"📝 条目已保存到 {temp_file}")

if __name__ == "__main__":
    try:
        generate_pitfall_entry()
    except KeyboardInterrupt:
        print("\n\n❌ 操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        sys.exit(1)
