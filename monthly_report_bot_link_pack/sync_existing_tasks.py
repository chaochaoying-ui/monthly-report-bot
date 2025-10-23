#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步已存在的飞书任务

问题：之前使用模拟task_id（task_2025-10_1），与飞书真实任务GUID不匹配
解决：通过飞书API列出所有任务，根据任务标题匹配，更新task_stats.json
"""

import os
import sys
import json
import asyncio
import re
from datetime import datetime
from typing import Dict, List, Any
import pytz

# 强制UTF-8输出
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    import lark_oapi as lark
    from lark_oapi.api.task.v2 import *
except ImportError:
    print("错误：需要安装 lark_oapi")
    print("运行: pip install lark-oapi")
    exit(1)

# 阿根廷时区
TZ = pytz.timezone('America/Argentina/Buenos_Aires')

# 配置文件
TASK_STATS_FILE = os.path.join(os.path.dirname(__file__), "task_stats.json")
ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")

def load_env():
    """加载环境变量"""
    env_vars = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def load_task_stats() -> Dict[str, Any]:
    """加载任务统计"""
    try:
        if os.path.exists(TASK_STATS_FILE):
            with open(TASK_STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"❌ 加载task_stats.json失败: {e}")
        return {}

def save_task_stats(stats: Dict[str, Any]) -> None:
    """保存任务统计"""
    try:
        stats["last_update"] = datetime.now(TZ).isoformat()
        with open(TASK_STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print("✅ task_stats.json 已更新")
    except Exception as e:
        print(f"❌ 保存task_stats.json失败: {e}")

async def list_all_tasks(client):
    """列出所有飞书任务"""
    try:
        print("\n📋 正在获取飞书任务列表...")

        # 构建请求
        request = ListTaskRequest.builder() \
            .page_size(100) \
            .build()

        response = await client.task.v2.task.alist(request)

        if response.success():
            tasks = response.data.items or []
            print(f"✅ 成功获取 {len(tasks)} 个任务")
            return tasks
        else:
            print(f"❌ 获取任务列表失败: code={response.code}, msg={response.msg}")
            return []

    except Exception as e:
        print(f"❌ 列出任务异常: {e}")
        return []

async def get_task_detail(client, task_guid: str):
    """获取任务详情（包括完成状态）"""
    try:
        request = GetTaskRequest.builder() \
            .task_guid(task_guid) \
            .build()

        response = await client.task.v2.task.aget(request)

        if response.success():
            return response.data.task
        else:
            print(f"⚠️ 获取任务详情失败: {task_guid}")
            return None

    except Exception as e:
        print(f"❌ 获取任务详情异常: {e}")
        return None

def normalize_title(title: str) -> str:
    """
    规范化任务标题，去除月份前缀
    例: "2025-10 月报-工程计划及执行情况" -> "月报-工程计划及执行情况"
    """
    # 去除 YYYY-MM 前缀
    title = re.sub(r'^\d{4}-\d{2}\s+', '', title)
    return title.strip()

async def main():
    print("=" * 60)
    print("飞书任务同步工具")
    print("=" * 60)

    # 加载环境变量
    env_vars = load_env()
    app_id = env_vars.get('APP_ID') or env_vars.get('FEISHU_APP_ID')
    app_secret = env_vars.get('APP_SECRET') or env_vars.get('FEISHU_APP_SECRET')

    if not app_id or not app_secret:
        print("错误：未找到飞书应用凭证")
        print("请检查 .env 文件中的 APP_ID 和 APP_SECRET")
        print("当前 .env 内容（前5个键）:", list(env_vars.keys())[:5])
        return

    # 初始化飞书客户端
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .build()

    # 加载当前task_stats
    stats = load_task_stats()
    if not stats or "tasks" not in stats:
        print("❌ task_stats.json 为空或格式不正确")
        return

    current_month = datetime.now(TZ).strftime("%Y-%m")
    print(f"\n📅 当前月份: {current_month}")
    print(f"📊 本地任务数: {len(stats['tasks'])}")

    # 获取飞书任务列表
    feishu_tasks = await list_all_tasks(client)

    if not feishu_tasks:
        print("\n⚠️ 未找到任何飞书任务")
        return

    # 创建标题到GUID的映射
    title_to_guid = {}
    title_to_status = {}

    print(f"\n🔍 分析飞书任务...")
    for task in feishu_tasks:
        task_guid = task.guid
        task_summary = task.summary or ""

        # 规范化标题
        normalized_title = normalize_title(task_summary)

        # 跳过不是月报任务的
        if not normalized_title.startswith("月报-"):
            continue

        # 获取完成状态
        task_detail = await get_task_detail(client, task_guid)
        if task_detail:
            is_completed = task_detail.complete == 2
            title_to_guid[normalized_title] = task_guid
            title_to_status[normalized_title] = is_completed

            status_icon = "✅" if is_completed else "⏳"
            print(f"  {status_icon} {normalized_title[:50]}...")

    print(f"\n✅ 找到 {len(title_to_guid)} 个月报任务")

    # 更新task_stats.json
    print(f"\n🔄 更新 task_stats.json...")
    updated_count = 0
    new_tasks = {}

    for old_task_id, task_info in stats["tasks"].items():
        title = task_info.get("title", "")

        # 检查是否能匹配到飞书任务
        if title in title_to_guid:
            new_guid = title_to_guid[title]
            new_completed = title_to_status[title]

            # 使用新的GUID作为key
            new_tasks[new_guid] = task_info.copy()

            # 更新完成状态
            old_completed = task_info.get("completed", False)
            new_tasks[new_guid]["completed"] = new_completed

            if new_completed and not old_completed:
                new_tasks[new_guid]["completed_at"] = datetime.now(TZ).isoformat()
                print(f"  ✅ {title[:40]}... (已完成)")
            elif not new_completed and old_completed:
                new_tasks[new_guid]["completed_at"] = None
                print(f"  ⏳ {title[:40]}... (未完成)")
            else:
                status = "已完成" if new_completed else "未完成"
                print(f"  ↔️ {title[:40]}... ({status})")

            updated_count += 1
        else:
            # 保留原有任务（未匹配到飞书任务）
            new_tasks[old_task_id] = task_info
            print(f"  ⚠️ {title[:40]}... (未匹配到飞书任务)")

    # 重新计算统计
    total_tasks = len(new_tasks)
    completed_tasks = sum(1 for t in new_tasks.values() if t.get("completed", False))
    completion_rate = round((completed_tasks / total_tasks) * 100, 2) if total_tasks > 0 else 0.0

    # 更新stats
    stats["tasks"] = new_tasks
    stats["total_tasks"] = total_tasks
    stats["completed_tasks"] = completed_tasks
    stats["completion_rate"] = completion_rate
    stats["current_month"] = current_month

    # 保存
    save_task_stats(stats)

    print(f"\n" + "=" * 60)
    print(f"✅ 同步完成！")
    print(f"=" * 60)
    print(f"📊 统计信息:")
    print(f"  • 总任务数: {total_tasks}")
    print(f"  • 已完成: {completed_tasks}")
    print(f"  • 待完成: {total_tasks - completed_tasks}")
    print(f"  • 完成率: {completion_rate}%")
    print(f"  • 更新任务: {updated_count}")
    print(f"\n🎉 现在任务状态已与飞书同步！")

if __name__ == "__main__":
    asyncio.run(main())
