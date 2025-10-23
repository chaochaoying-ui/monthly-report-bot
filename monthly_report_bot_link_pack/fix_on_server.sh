#!/bin/bash
# 服务器端任务同步修复脚本 - 直接在GCP服务器上运行

set -e

echo "============================================================"
echo "月报机器人 - 任务同步修复（服务器端）"
echo "============================================================"
echo ""

# 检查是否在正确目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "📁 当前目录: $SCRIPT_DIR"
echo ""

# 步骤1: 备份关键文件
echo "步骤 1/4: 备份关键文件..."
BACKUP_TIME=$(date +%Y%m%d_%H%M%S)

if [ -f "monthly_report_bot_ws_v1.1.py" ]; then
    cp monthly_report_bot_ws_v1.1.py "monthly_report_bot_ws_v1.1.py.backup_${BACKUP_TIME}"
    echo "✅ 已备份主程序 -> monthly_report_bot_ws_v1.1.py.backup_${BACKUP_TIME}"
fi

if [ -f "task_stats.json" ]; then
    cp task_stats.json "task_stats.json.backup_${BACKUP_TIME}"
    echo "✅ 已备份任务数据 -> task_stats.json.backup_${BACKUP_TIME}"
fi

echo ""

# 步骤2: 检查必要文件
echo "步骤 2/4: 检查必要文件..."

if [ ! -f "sync_existing_tasks.py" ]; then
    echo "❌ 错误: 找不到 sync_existing_tasks.py"
    echo "请先上传该文件到服务器"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "❌ 错误: 找不到 .env 文件"
    exit 1
fi

echo "✅ 所有必要文件都存在"
echo ""

# 步骤3: 激活虚拟环境并运行同步脚本
echo "步骤 3/4: 同步任务GUID..."

if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "⚠️ 未找到虚拟环境，使用系统Python"
fi

echo ""
echo "正在运行同步脚本..."
echo "----------------------------------------"

python3 sync_existing_tasks.py

if [ $? -eq 0 ]; then
    echo "----------------------------------------"
    echo "✅ 任务同步成功"
else
    echo "----------------------------------------"
    echo "❌ 任务同步失败"
    echo ""
    echo "可能的原因："
    echo "1. 飞书API凭证不正确（检查 .env 文件）"
    echo "2. 网络连接问题"
    echo "3. 飞书应用权限不足"
    echo ""
    echo "请检查上面的错误信息"
    exit 1
fi

echo ""

# 步骤4: 重启服务
echo "步骤 4/4: 重启月报机器人服务..."

sudo systemctl restart monthly-report-bot

if [ $? -eq 0 ]; then
    echo "✅ 服务重启命令已执行"
    sleep 3

    if sudo systemctl is-active --quiet monthly-report-bot; then
        echo "✅ 服务运行正常"
    else
        echo "❌ 服务启动失败"
        echo ""
        echo "查看服务状态:"
        sudo systemctl status monthly-report-bot --no-pager
        exit 1
    fi
else
    echo "❌ 服务重启失败"
    exit 1
fi

echo ""
echo "============================================================"
echo "✅ 修复完成！"
echo "============================================================"
echo ""
echo "📊 验证步骤:"
echo "  1. 在飞书群聊中发送: 状态"
echo "  2. 检查是否显示正确的已完成任务数"
echo "  3. 检查完成率是否准确（应该不再是0%）"
echo ""
echo "📁 备份文件:"
echo "  - monthly_report_bot_ws_v1.1.py.backup_${BACKUP_TIME}"
echo "  - task_stats.json.backup_${BACKUP_TIME}"
echo ""
echo "🔧 如需回滚:"
echo "  cp monthly_report_bot_ws_v1.1.py.backup_${BACKUP_TIME} monthly_report_bot_ws_v1.1.py"
echo "  cp task_stats.json.backup_${BACKUP_TIME} task_stats.json"
echo "  sudo systemctl restart monthly-report-bot"
echo ""
echo "📋 查看服务日志:"
echo "  sudo journalctl -u monthly-report-bot -n 50"
echo ""
