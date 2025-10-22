#!/bin/bash

# ============================================================================
# 更新 systemd 服务配置以加载 .env 文件
# ============================================================================

echo "========================================================================"
echo "更新 systemd 服务配置"
echo "========================================================================"
echo ""

echo "当前服务配置:"
echo "------------------------------------------------------------------------"
sudo cat /etc/systemd/system/monthly-report-bot.service
echo ""

echo "========================================================================"
echo "创建新的服务配置"
echo "========================================================================"
echo ""

# 创建新的服务配置
sudo bash -c 'cat > /etc/systemd/system/monthly-report-bot.service << EOL
[Unit]
Description=Monthly Report Bot v1.1 (WebSocket)
After=network.target

[Service]
Type=simple
User=hdi918072
WorkingDirectory=/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack
EnvironmentFile=/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/.env
ExecStart=/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/venv/bin/python3 /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot_ws_v1.1.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL'

echo "✅ 服务配置已更新"
echo ""

echo "新的服务配置:"
echo "------------------------------------------------------------------------"
sudo cat /etc/systemd/system/monthly-report-bot.service
echo ""

echo "========================================================================"
echo "重新加载 systemd 配置"
echo "========================================================================"
echo ""

sudo systemctl daemon-reload
echo "✅ systemd 配置已重新加载"
echo ""

echo "========================================================================"
echo "重启服务"
echo "========================================================================"
echo ""

sudo systemctl restart monthly-report-bot
sleep 3

if sudo systemctl is-active --quiet monthly-report-bot; then
    echo "✅ 服务已成功启动"
    echo ""
    echo "服务状态:"
    sudo systemctl status monthly-report-bot --no-pager | head -20
    echo ""
    echo "最新日志:"
    sudo journalctl -u monthly-report-bot -n 30 --no-pager | tail -20
else
    echo "❌ 服务启动失败"
    echo ""
    echo "错误日志:"
    sudo journalctl -u monthly-report-bot -n 50 --no-pager
    exit 1
fi

echo ""
echo "========================================================================"
echo "验证环境变量"
echo "========================================================================"
echo ""

echo "检查服务是否正确读取 .env 文件..."
sleep 2

# 检查日志中是否有错误
if sudo journalctl -u monthly-report-bot -n 50 --no-pager | grep -q "invalid param"; then
    echo "⚠️  仍然存在 'invalid param' 错误"
    echo ""
    echo "可能的原因:"
    echo "1. .env 文件路径不正确"
    echo "2. .env 文件权限问题"
    echo "3. .env 文件格式问题"
    echo ""
    echo "检查 .env 文件:"
    echo "  ls -la ~/monthly-report-bot/monthly_report_bot_link_pack/.env"
    echo "  cat ~/monthly-report-bot/monthly_report_bot_link_pack/.env"
elif sudo journalctl -u monthly-report-bot -n 50 --no-pager | grep -q "WebSocket 连接已建立"; then
    echo "✅✅✅ WebSocket 连接成功！v1.1 正常运行！✅✅✅"
else
    echo "⏳ 等待 WebSocket 连接..."
    echo ""
    echo "查看实时日志:"
    echo "  sudo journalctl -u monthly-report-bot -f"
fi

echo ""
echo "========================================================================"
echo "完成"
echo "========================================================================"
