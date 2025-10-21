#!/usr/bin/env python3
"""验证 @ 格式修复 - 无需导入主模块"""

import re

def verify_at_format():
    """验证文件中的 @ 格式"""

    print("=" * 80)
    print("验证每日提醒 @ 格式修复")
    print("=" * 80)

    # 读取修复后的文件
    file_path = "monthly_report_bot_link_pack/monthly_report_bot_final_interactive.py"

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')

    # 查找所有包含 <at 的行
    at_tags = []
    for i, line in enumerate(lines, 1):
        if '<at' in line and 'user_id=' in line:
            at_tags.append((i, line.strip()))

    print(f"\n找到 {len(at_tags)} 处使用 @ 标签的位置")
    print("\n检查结果:")
    print("-" * 80)

    # 检查格式
    correct_format_count = 0
    old_format_count = 0

    for line_num, line in at_tags:
        # 检查是否有显示名称（正确格式）
        if re.search(r'<at user_id="[^"]+">.*?</at>', line):
            status = "✅ 正确"
            correct_format_count += 1
        # 检查是否是旧格式（只有 user_id，没有显示名称）
        elif re.search(r'<at user_id="[^"]+"></at>', line):
            status = "⚠️  缺少显示名称"
            old_format_count += 1
        # 检查是否使用了错误的 id 属性
        elif '<at id=' in line:
            status = "❌ 使用了错误的 'id' 属性"
            old_format_count += 1
        else:
            status = "❓ 未知格式"
            old_format_count += 1

        # 只显示前10个和有问题的
        if len(at_tags) <= 10 or status != "✅ 正确":
            print(f"\n第 {line_num:4d} 行: {status}")
            print(f"  {line[:100]}...")

    print("\n" + "=" * 80)
    print("统计结果:")
    print(f"  ✅ 正确格式: {correct_format_count} 处")
    print(f"  ❌ 需要修复: {old_format_count} 处")
    print("=" * 80)

    if old_format_count == 0:
        print("\n🎉 所有 @ 格式都已正确修复！")
        print("\n正确格式示例:")
        print('  <at user_id="ou_xxx">周超</at>')
        print('  <at user_id="ou_yyy">张三</at>')
        return True
    else:
        print(f"\n⚠️  还有 {old_format_count} 处需要修复")
        print("\n需要修复的格式:")
        print('  ❌ <at id="ou_xxx"></at>')
        print('  ❌ <at user_id="ou_xxx"></at>')
        print("\n应该改为:")
        print('  ✅ <at user_id="ou_xxx">显示名称</at>')
        return False

if __name__ == "__main__":
    success = verify_at_format()
    exit(0 if success else 1)
