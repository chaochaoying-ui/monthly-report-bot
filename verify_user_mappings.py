#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 tasks.yaml 中的所有用户ID是否都在 USER_ID_MAPPING 中
"""

import yaml
import re

# 读取 tasks.yaml
with open('monthly_report_bot_link_pack/tasks.yaml', 'r', encoding='utf-8') as f:
    tasks = yaml.safe_load(f)

# 读取 monthly_report_bot_ws_v1.1.py 获取 USER_ID_MAPPING
with open('monthly_report_bot_link_pack/monthly_report_bot_ws_v1.1.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取 USER_ID_MAPPING
mapping_match = re.search(r'USER_ID_MAPPING\s*=\s*\{([^}]+)\}', content, re.DOTALL)
if mapping_match:
    mapping_text = mapping_match.group(1)
    # 提取所有映射的用户ID
    mapped_ids = set(re.findall(r'"(ou_[a-f0-9]+)"', mapping_text))
else:
    print("❌ 无法找到 USER_ID_MAPPING")
    exit(1)

print("=" * 60)
print("验证用户ID映射")
print("=" * 60)
print(f"\n📋 USER_ID_MAPPING 中有 {len(mapped_ids)} 个用户\n")

# 收集 tasks.yaml 中的所有用户ID
task_user_ids = {}
for task in tasks:
    assignee_id = task.get('assignee_open_id', '')
    if assignee_id:
        # 处理可能的多个负责人（用分号分隔）
        if ';' in str(assignee_id):
            ids = [id.strip() for id in str(assignee_id).split(';')]
        else:
            ids = [str(assignee_id).strip()]

        for uid in ids:
            if uid:
                if uid not in task_user_ids:
                    task_user_ids[uid] = []
                task_user_ids[uid].append(task['title'])

print(f"📋 tasks.yaml 中使用了 {len(task_user_ids)} 个不同的用户ID\n")

# 检查是否有未映射的ID
missing_ids = set(task_user_ids.keys()) - mapped_ids
extra_ids = mapped_ids - set(task_user_ids.keys())

if missing_ids:
    print("❌ 以下用户ID在 tasks.yaml 中使用但未在 USER_ID_MAPPING 中定义：")
    print("")
    for uid in sorted(missing_ids):
        print(f"  • {uid}")
        print(f"    任务数: {len(task_user_ids[uid])}")
        for task_title in task_user_ids[uid][:3]:  # 只显示前3个任务
            print(f"      - {task_title}")
        if len(task_user_ids[uid]) > 3:
            print(f"      ... 还有 {len(task_user_ids[uid]) - 3} 个任务")
        print("")
else:
    print("✅ 所有用户ID都已正确映射！")
    print("")

if extra_ids:
    print(f"ℹ️  以下 {len(extra_ids)} 个用户ID在映射表中但未在任务中使用：")
    for uid in sorted(extra_ids):
        print(f"  • {uid}")
    print("")

# 显示所有映射关系
print("=" * 60)
print("当前任务分配统计")
print("=" * 60)
print("")

# 重新读取 USER_ID_MAPPING 来获取用户名
user_names = {}
for line in mapping_text.split('\n'):
    match = re.search(r'"(ou_[a-f0-9]+)":\s*"([^"]+)"', line)
    if match:
        user_names[match.group(1)] = match.group(2)

for uid in sorted(task_user_ids.keys()):
    user_name = user_names.get(uid, "未知用户")
    task_count = len(task_user_ids[uid])
    print(f"👤 {user_name} ({uid[:12]}...)")
    print(f"   任务数: {task_count}")
    print("")

print("=" * 60)
print("验证完成！")
print("=" * 60)
