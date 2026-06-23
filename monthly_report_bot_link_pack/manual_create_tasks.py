#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动创建任务脚本
用于在任何时间手动触发任务创建
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
import pytz

# 加载环境变量
load_dotenv()

# 导入 lark SDK
try:
    import lark_oapi as lark
    from lark_oapi.api.task.v2 import *
    from lark_oapi.api.task.v2.model import *
except ImportError:
    print("❌ 错误: 未安装 lark-oapi")
    print("请运行: pip install lark-oapi")
    sys.exit(1)

# 环境变量
APP_ID = os.environ.get("APP_ID", "").strip()
APP_SECRET = os.environ.get("APP_SECRET", "").strip()
TZ_NAME = os.environ.get("TZ", "America/Argentina/Buenos_Aires").strip()
TZ = pytz.timezone(TZ_NAME)

# 验证环境变量
if not APP_ID or not APP_SECRET:
    print("❌ 错误: 缺少 APP_ID 或 APP_SECRET")
    print("请检查 .env 文件")
    sys.exit(1)

# 初始化飞书客户端
lark_client = lark.Client.builder() \
    .app_id(APP_ID) \
    .app_secret(APP_SECRET) \
    .build()

print("✅ 飞书客户端初始化成功")

# 任务配置文件
TASKS_YAML_FILE = "tasks.yaml"
TASK_STATS_FILE = "task_stats.json"
CREATED_TASKS_FILE = "created_tasks.json"

def load_tasks_config():
    """加载任务配置"""
    import yaml
    try:
        with open(TASKS_YAML_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            # tasks.yaml 直接是一个列表，不是字典
            if isinstance(config, list):
                return config
            elif isinstance(config, dict):
                return config.get('tasks', [])
            else:
                return []
    except Exception as e:
        print(f"❌ 加载任务配置失败: {e}")
        return []


def load_created_tasks():
    """加载已创建任务记录"""
    try:
        if os.path.exists(CREATED_TASKS_FILE):
            with open(CREATED_TASKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"❌ 加载created_tasks失败: {e}")
        return {}

def save_created_tasks(created_tasks):
    """保存已创建任务记录"""
    try:
        with open(CREATED_TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(created_tasks, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ 保存created_tasks失败: {e}")
def update_task_completion(task_id: str, title: str, assignees: list, completed: bool, task_type: str = "月报"):
    """更新任务完成状态"""
    try:
        # 读取现有数据
        if os.path.exists(TASK_STATS_FILE):
            with open(TASK_STATS_FILE, 'r', encoding='utf-8') as f:
                stats = json.load(f)
        else:
            current_month = datetime.now(TZ).strftime("%Y-%m")
            stats = {
                "current_month": current_month,
                "tasks": {},
                "total_tasks": 0,
                "completed_tasks": 0,
                "completion_rate": 0.0
            }

        # 更新任务信息
        stats["tasks"][task_id] = {
            "title": title,
            "assignees": assignees,
            "task_type": task_type,
            "completed": completed,
            "completed_at": datetime.now(TZ).isoformat() if completed else None
        }

        # 重新计算统计
        total = len(stats["tasks"])
        completed_count = sum(1 for t in stats["tasks"].values() if t.get("completed", False))
        completion_rate = (completed_count / total * 100) if total > 0 else 0.0

        stats["total_tasks"] = total
        stats["completed_tasks"] = completed_count
        stats["completion_rate"] = round(completion_rate, 2)

        # 保存
        with open(TASK_STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        print(f"  ✅ 已保存: {title} (GUID: {task_id[:20]}...)")

    except Exception as e:
        print(f"  ❌ 保存失败: {e}")

async def create_tasks():
    """创建任务"""
    print("=" * 60)
    print("开始创建月报任务")
    print("=" * 60)
    print()

    # 加载任务配置
    task_list = load_tasks_config()
    if not task_list:
        print("❌ 错误: 未找到任务配置")
        return False

    print(f"📋 找到 {len(task_list)} 个任务配置")
    print()

    # 获取当前月份
    current_month = datetime.now(TZ).strftime("%Y-%m")
    print(f"📅 当前月份: {current_month}")
    print()

    # 计算截止时间（23号 23:59:59）
    deadline = datetime.now(TZ).replace(day=23, hour=23, minute=59, second=59)
    # 飞书API需要毫秒级时间戳（乘以1000）
    due_timestamp = int(deadline.timestamp() * 1000)
    print(f"⏰ 截止时间: {deadline.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ 时间戳（毫秒）: {due_timestamp}")
    print()

    success_count = 0

    for i, task_config in enumerate(task_list, 1):
        try:
            # 构建任务标题
            task_title = f"{current_month} {task_config['title']}"

            # 获取负责人列表
            assignees = []
            if task_config.get('assignee_open_id'):
                if isinstance(task_config['assignee_open_id'], list):
                    assignees = task_config['assignee_open_id']
                else:
                    assignees = [task_config['assignee_open_id']]

            # 过滤空值
            assignees = [a for a in assignees if a and a.strip()]

            print(f"[{i}/{len(task_list)}] 创建任务: {task_title}")
            if assignees:
                print(f"     负责人: {len(assignees)} 人")

            # 创建任务请求 - 使用正确的 API (InputTask, Due, Member)
            # 准备成员列表
            members_list = []
            if assignees:
                for assignee_id in assignees:
                    member = Member.builder() \
                        .id(assignee_id) \
                        .role("assignee") \
                        .build()
                    members_list.append(member)

            task_builder = InputTask.builder() \
                            .summary(task_title) \
                            .description(f"月度报告任务: {task_config['title']}\n文档链接: {task_config.get('doc_url', '')}")

            # 添加截止时间
            task_builder = task_builder.due(Due.builder()
                                .timestamp(str(due_timestamp))
                                .is_all_day(False)
                                .build())

            # 如果有负责人，添加成员
            if members_list:
                task_builder = task_builder.members(members_list)

            request = CreateTaskRequest.builder() \
                .request_body(task_builder.build()) \
                .build()

            response = await lark_client.task.v2.task.acreate(request)

            if response.success():
                task_guid = response.data.task.guid
                print(f"     ✅ 任务创建成功（含负责人分配）")
                print(f"     GUID: {task_guid}")

                # 更新统计（使用真实的 task_guid）
                update_task_completion(task_guid, task_config['title'], assignees, False,
                                       task_type=task_config.get('task_type', '月报'))
                success_count += 1

            else:
                print(f"     ❌ 任务创建失败: code={response.code}, msg={response.msg}")

            print()

        except Exception as e:
            print(f"     ❌ 创建任务异常: {e}")
            print()

    print("=" * 60)
    if success_count > 0:
        print(f"✅ 任务创建完成，成功创建 {success_count}/{len(task_list)} 个任务")
        print()

        # 读取并显示统计
        if os.path.exists(TASK_STATS_FILE):
            with open(TASK_STATS_FILE, 'r', encoding='utf-8') as f:
                stats = json.load(f)

            print("📊 任务统计:")
            print(f"  - 总任务数: {stats['total_tasks']}")
            print(f"  - 已完成: {stats['completed_tasks']}")
            print(f"  - 待完成: {stats['total_tasks'] - stats['completed_tasks']}")
            print(f"  - 完成率: {stats['completion_rate']}%")


        # Mark tasks as created
        created_tasks = load_created_tasks()
        created_tasks[current_month] = True
        save_created_tasks(created_tasks)
        print("Tasks marked as created")


        return True
    else:
        print("❌ 没有成功创建任何任务")
        return False

async def main():
    """主函数"""
    print()
    print("🚀 手动创建任务脚本")
    print()

    # 检查是否已有任务
    if os.path.exists(TASK_STATS_FILE):
        with open(TASK_STATS_FILE, 'r', encoding='utf-8') as f:
            stats = json.load(f)

        if stats.get('total_tasks', 0) > 0:
            print(f"⚠️ 警告: 已存在 {stats['total_tasks']} 个任务")
            print()
            response = input("是否要删除现有任务并重新创建? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ 操作已取消")
                return

            # 备份并清空旧数据，确保重建从零开始
            import shutil
            backup_file = f"{TASK_STATS_FILE}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy(TASK_STATS_FILE, backup_file)
            print(f"✅ 已备份到: {backup_file}")
            os.remove(TASK_STATS_FILE)
            print(f"✅ 已清空旧任务数据，重新创建")
            print()

    # 创建任务
    success = await create_tasks()

    if success:
        print()
        print("=" * 60)
        print("✅ 全部完成！")
        print()
        print("下一步:")
        print("  1. 查看 task_stats.json 确认任务ID格式")
        print("  2. 在飞书群聊中发送 '状态' 验证")
        print("  3. 如果正常，重启服务:")
        print("     sudo systemctl restart monthly-report-bot")
        print("=" * 60)
    else:
        print()
        print("❌ 任务创建失败，请检查错误信息")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ 操作已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
