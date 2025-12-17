#!/bin/bash
# 修复刘野用户ID的部署脚本
# 将 ou_b96c7ed4a604dc049569102d01c6c26d 改为 ou_b96c7cd4a604dc049569102d01c6c26d

set -e

SERVER_IP="34.125.160.193"
SERVER_USER="zhangmingbo123"
BOT_DIR="~/monthly-report-bot/monthly_report_bot_link_pack"

echo "=============================="
echo "修复刘野用户ID映射"
echo "=============================="
echo ""
echo "问题描述："
echo "  刘野的用户ID在配置中错误地写成了 ou_b96c7ed (应为 ou_b96c7cd)"
echo "  导致飞书卡片显示 '用户(ou_b96c7...)' 而不是 '刘野'"
echo ""
echo "修复内容："
echo "  1. tasks.yaml - 4处刘野的任务分配"
echo "  2. monthly_report_bot_ws_v1.1.py - USER_ID_MAPPING"
echo ""
echo "目标服务器: $SERVER_IP"
echo ""

# 1. 备份服务器上的文件
echo "步骤 1/4: 备份服务器文件..."
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd ~/monthly-report-bot/monthly_report_bot_link_pack
cp tasks.yaml tasks.yaml.backup_fix_liuye_$(date +%Y%m%d_%H%M%S)
cp monthly_report_bot_ws_v1.1.py monthly_report_bot_ws_v1.1.py.backup_fix_liuye_$(date +%Y%m%d_%H%M%S)
echo "✅ 备份完成"
ENDSSH

# 2. 上传修复后的文件
echo ""
echo "步骤 2/4: 上传修复后的文件..."
scp monthly_report_bot_link_pack/tasks.yaml ${SERVER_USER}@${SERVER_IP}:${BOT_DIR}/
scp monthly_report_bot_link_pack/monthly_report_bot_ws_v1.1.py ${SERVER_USER}@${SERVER_IP}:${BOT_DIR}/
echo "✅ 文件上传完成"

# 3. 验证修复
echo ""
echo "步骤 3/4: 验证修复..."
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd ~/monthly-report-bot/monthly_report_bot_link_pack

echo "检查 tasks.yaml 中刘野的用户ID..."
count=$(grep -c "ou_b96c7cd4a604dc049569102d01c6c26d" tasks.yaml || true)
if [ "$count" -eq 4 ]; then
    echo "✅ tasks.yaml 已正确更新（4处）"
else
    echo "❌ tasks.yaml 更新有误（应该4处，实际${count}处）"
    exit 1
fi

echo ""
echo "检查 monthly_report_bot_ws_v1.1.py 中的映射..."
if grep -q '"ou_b96c7cd4a604dc049569102d01c6c26d": "刘野"' monthly_report_bot_ws_v1.1.py; then
    echo "✅ USER_ID_MAPPING 已正确更新"
else
    echo "❌ USER_ID_MAPPING 更新有误"
    exit 1
fi

echo ""
echo "检查是否还有旧ID残留..."
old_count=$(grep -c "ou_b96c7ed4a604dc049569102d01c6c26d" tasks.yaml monthly_report_bot_ws_v1.1.py 2>/dev/null || true)
if [ "$old_count" -eq 0 ]; then
    echo "✅ 没有旧ID残留"
else
    echo "⚠️  警告：发现 ${old_count} 处旧ID残留"
fi
ENDSSH

# 4. 重启机器人
echo ""
echo "步骤 4/4: 重启月报机器人..."
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd ~/monthly-report-bot

# 查找并停止现有进程
echo "停止现有机器人进程..."
pkill -f "monthly_report_bot_ws_v1.1.py" || true
sleep 2

# 启动新进程
echo "启动月报机器人..."
cd monthly_report_bot_link_pack
nohup python3 monthly_report_bot_ws_v1.1.py > ../bot.log 2>&1 &
sleep 3

# 检查进程
if pgrep -f "monthly_report_bot_ws_v1.1.py" > /dev/null; then
    echo "✅ 机器人已成功启动"
    echo ""
    echo "查看最新日志："
    tail -20 ../bot.log
else
    echo "❌ 机器人启动失败"
    echo ""
    echo "错误日志："
    tail -50 ../bot.log
    exit 1
fi
ENDSSH

echo ""
echo "=============================="
echo "✅ 修复部署完成！"
echo "=============================="
echo ""
echo "现在刘野的4个任务应该正确显示姓名了："
echo "  1. 月报-工程计划及执行情况"
echo "  2. 月报-本月其他工作进展-技术管理"
echo "  3. 月报-存在的问题及措施-总进度滞后方面..."
echo "  4. 月报-下月工作计划及安排-进度及产值方面"
echo ""
echo "验证方法："
echo "  在飞书群中发送：@月报收集系统 状态"
echo "  检查刘野的任务是否正确显示姓名"
echo ""
