#!/usr/bin/env python3
"""
初始化真实的月报任务数据
用途: 在部署时创建包含23个真实月报任务的 task_stats.json
"""

import json
import os
from datetime import datetime
import pytz

# 阿根廷时区
TZ = pytz.timezone("America/Argentina/Buenos_Aires")

def init_real_tasks():
    """从 tasks.yaml 创建真实的月报任务数据"""

    # 真实任务数据（来自 tasks.yaml）
    real_tasks = [
        {"title": "月报-工程计划及执行情况", "assignee": "ou_b96c7ed4a604dc049569102d01c6c26d", "category": "工程管理", "completed": True},
        {"title": "月报-设计工作进展", "assignee": "ou_07443a67428d8741eab5eac851b754b9", "category": "设计", "completed": True},
        {"title": "月报-本月其他工作进展-技术管理", "assignee": "ou_b96c7ed4a604dc049569102d01c6c26d", "category": "技术管理", "completed": True},
        {"title": "月报-存在的问题及措施-土建设计、总进度滞后方面、各分部工程进度、开工累计产值计划偏差方面", "assignee": "ou_b96c7ed4a604dc049569102d01c6c26d", "category": "工程管理", "completed": True},
        {"title": "月报-下月工作计划及安排-进度及产值方面", "assignee": "ou_b96c7ed4a604dc049569102d01c6c26d", "category": "工程管理", "completed": True},
        {"title": "月报-现场施工照片", "assignee": "ou_a9c22d7a23ff6dd0e3dc1a93b2763b5a", "category": "施工", "completed": False},
        {"title": "月报-设计工作进展情况-机电工程", "assignee": "ou_49299becc523c8d3aa1120261f1e2bcd", "category": "设计", "completed": False},
        {"title": "月报-采购工作进展情况-永久机电材料和成套设备采", "assignee": "ou_49299becc523c8d3aa1120261f1e2bcd", "category": "采购", "completed": False},
        {"title": "月报-存在的问题及措施-现场施工方面", "assignee": "ou_5199fde738bcaedd5fcf4555b0adf7a0", "category": "施工", "completed": False},
        {"title": "月报-本月其他工作进展-安质环管理", "assignee": "ou_33d81ce8839d93132e4417530f60c4a9", "category": "安全质量", "completed": False},
        {"title": "月报-下月工作计划及安排-安全、质量及环保方面", "assignee": "ou_33d81ce8839d93132e4417530f60c4a9", "category": "安全质量", "completed": False},
        {"title": "月报-项目主材当月出入库及库存情况", "assignee": "ou_f5338c49049621c36310e2215204d0be", "category": "物资管理", "completed": False},
        {"title": "月报-本月其他工作进展（设备管理）", "assignee": "ou_50c492f1d2b2ee2107c4e28ab4416732", "category": "设备管理", "completed": False},
        {"title": "月报-项目人员信息统计表", "assignee": "ou_2f93cb9407ca5a281a92d1f5a72fdf7b", "category": "人力资源", "completed": False},
        {"title": "月报-本月其他工作进展-项目部制度建设、劳务管理、公共关系建立及维护", "assignee": "ou_d85dd7bb7625ab3e3f8b129e54934aea", "category": "行政管理", "completed": False},
        {"title": "月报-总部监管意见的响应落实情况-工会补充协议", "assignee": "ou_c9d7859417eb0344b310fcff095fa639", "category": "合规管理", "completed": False},
        {"title": '月报-"两金"情况-现金流情况、营业收入完成情况', "assignee": "ou_3b14801caa065a0074c7d6db8603f288", "category": "财务", "completed": False},
        {"title": '月报-"本月其他工作进展-税务管理', "assignee": "ou_3b14801caa065a0074c7d6db8603f288", "category": "财务", "completed": False},
        {"title": "月报-主合同备忘录MOU工作进展", "assignee": "ou_0bbab538833c35081e8f5c3ef213e17e", "category": "合同管理", "completed": False},
        {"title": "月报-总部监管意见的响应落实情况-谅解备忘录相关事项", "assignee": "ou_0bbab538833c35081e8f5c3ef213e17e", "category": "合同管理", "completed": False},
        {"title": "月报-结算支付情况", "assignee": "ou_17b6bee82dd946d92a322cc7dea40eb7", "category": "财务", "completed": False},
        {"title": "月报-采购执行情况部分", "assignee": "ou_9847326a1fea8db87079101775bd97a9", "category": "采购", "completed": False},
        {"title": "月报-分包合同结算支付情况", "assignee": "ou_9847326a1fea8db87079101775bd97a9", "category": "合同管理", "completed": False},
    ]

    # 文档 URL（所有任务共享同一个文件夹）
    doc_url = "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"

    # 创建时间
    now = datetime.now(TZ)
    current_month = now.strftime("%Y-%m")
    created_at = f"{current_month}-17T09:00:00-03:00"
    completed_at = f"{current_month}-21T10:00:00-03:00"

    # 构建任务字典
    tasks = {}
    completed_count = 0

    for idx, task_data in enumerate(real_tasks, start=1):
        task_id = f"task_{current_month}_{idx}"

        task_info = {
            "title": task_data["title"],
            "assignees": [task_data["assignee"]],
            "category": task_data["category"],
            "created_at": created_at,
            "completed": task_data["completed"],
            "completed_at": completed_at if task_data["completed"] else None,
            "doc_url": doc_url
        }

        tasks[task_id] = task_info

        if task_data["completed"]:
            completed_count += 1

    # 构建完整的统计数据
    total_tasks = len(real_tasks)
    completion_rate = (completed_count / total_tasks * 100) if total_tasks > 0 else 0.0

    task_stats = {
        "current_month": current_month,
        "tasks": tasks,
        "total_tasks": total_tasks,
        "completed_tasks": completed_count,
        "completion_rate": round(completion_rate, 1),
        "last_update": now.isoformat()
    }

    # 保存到文件
    task_stats_file = os.path.join(os.path.dirname(__file__), "task_stats.json")

    with open(task_stats_file, "w", encoding="utf-8") as f:
        json.dump(task_stats, f, ensure_ascii=False, indent=2)

    print(f"✅ 已创建真实任务数据: {task_stats_file}")
    print(f"📊 任务统计:")
    print(f"   总任务数: {total_tasks}")
    print(f"   已完成: {completed_count}")
    print(f"   完成率: {completion_rate:.1f}%")
    print(f"   刘野 (ou_b96c7ed4a604dc049569102d01c6c26d): 5个任务已完成")
    print(f"   范明杰 (ou_07443a67428d8741eab5eac851b754b9): 1个任务已完成")

    return task_stats_file

if __name__ == "__main__":
    init_real_tasks()
