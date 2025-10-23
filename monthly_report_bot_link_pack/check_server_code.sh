#!/bin/bash
# 检查服务器上的代码是否已修复

echo "============================================================"
echo "检查服务器代码版本"
echo "============================================================"
echo ""

echo "1. 检查 create_tasks() 函数中的关键行..."
echo ""

# 检查第1438行是否使用真实API
echo "第1438行（应该是: response = await lark_client.task.v2.task.acreate(request)）:"
sed -n '1438p' monthly_report_bot_ws_v1.1.py
echo ""

# 检查第1441行是否获取真实GUID
echo "第1441行（应该是: task_guid = response.data.task.guid）:"
sed -n '1441p' monthly_report_bot_ws_v1.1.py
echo ""

# 检查第1460行是否使用真实GUID
echo "第1460行（应该是: update_task_completion(task_guid, ...)）:"
sed -n '1460p' monthly_report_bot_ws_v1.1.py
echo ""

echo "============================================================"
echo "2. 检查是否还有\"模拟创建任务\"的代码..."
echo ""

if grep -n "模拟创建任务" monthly_report_bot_ws_v1.1.py; then
    echo "❌ 发现旧代码！仍然在使用模拟任务创建"
else
    echo "✅ 未发现\"模拟创建任务\"，代码已更新"
fi

echo ""
echo "============================================================"
echo "3. 检查当前 task_stats.json 中的任务ID格式..."
echo ""

if [ -f "task_stats.json" ]; then
    echo "任务ID示例（前3个）:"
    python3 -c "import json; data=json.load(open('task_stats.json')); [print(f'  {task_id}') for task_id in list(data.get('tasks', {}).keys())[:3]]"
    echo ""

    # 检查是否是假ID
    if python3 -c "import json; data=json.load(open('task_stats.json')); exit(0 if any('task_2025' in k for k in data.get('tasks', {}).keys()) else 1)"; then
        echo "❌ 发现假任务ID (task_2025-10_X 格式)"
        echo "   需要删除 task_stats.json 并重新创建任务"
    else
        echo "✅ 任务ID格式正确（GUID格式）"
    fi
else
    echo "⚠️ task_stats.json 不存在"
fi

echo ""
echo "============================================================"
echo "4. 检查最近一次 Git 提交..."
echo ""
git log --oneline -1
echo ""

echo "============================================================"
echo "总结"
echo "============================================================"
echo ""
echo "如果看到以下情况，说明需要更新服务器代码："
echo "  - ❌ 第1438行不是使用 acreate(request)"
echo "  - ❌ 发现\"模拟创建任务\"的代码"
echo "  - ❌ 任务ID是 task_2025-10_X 格式"
echo ""
echo "如果代码已更新但任务ID仍是假的，需要："
echo "  1. 备份: cp task_stats.json task_stats.json.backup"
echo "  2. 删除: rm task_stats.json"
echo "  3. 重启: sudo systemctl restart monthly-report-bot"
echo ""
