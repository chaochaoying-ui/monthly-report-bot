#!/bin/bash

# ============================================================================
# 月报机器人 v1.1 一键部署脚本
# 用途: 在 GCP 服务器上一键部署 v1.1 版本
# 使用方法: 复制整个脚本，粘贴到 GCP SSH 终端，按回车执行
# ============================================================================

set -e  # 遇到错误立即停止

echo "========================================================================"
echo "🚀 月报机器人 v1.1 自动部署脚本"
echo "========================================================================"
echo ""

# ============================================================================
# 第 1 步: 备份当前生产环境
# ============================================================================

echo "步骤 1/4: 备份当前生产环境..."
echo "------------------------------------------------------------------------"

cd ~/monthly-report-bot

BACKUP_DIR="$HOME/monthly-report-bot-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

echo "创建备份: $BACKUP_DIR/backup_before_v1.1_$TIMESTAMP"
cp -r monthly_report_bot_link_pack "$BACKUP_DIR/backup_before_v1.1_$TIMESTAMP"

echo "✅ 备份已创建"
echo ""

# ============================================================================
# 第 2 步: 停止当前服务
# ============================================================================

echo "步骤 2/4: 停止当前服务..."
echo "------------------------------------------------------------------------"

sudo systemctl stop monthly-report-bot

if sudo systemctl is-active --quiet monthly-report-bot; then
    echo "❌ 服务未能停止"
    exit 1
else
    echo "✅ 服务已停止"
fi

echo ""

# ============================================================================
# 第 3 步: 拉取 v1.1 代码
# ============================================================================

echo "步骤 3/4: 拉取 v1.1 代码..."
echo "------------------------------------------------------------------------"

cd ~/monthly-report-bot

git fetch origin
git pull origin main

if [ $? -eq 0 ]; then
    echo "✅ 代码更新成功"
    echo "最新提交: $(git log -1 --oneline)"
else
    echo "❌ 代码更新失败"
    exit 1
fi

echo ""

# ============================================================================
# 第 4 步: 配置并启动 v1.1
# ============================================================================

echo "步骤 4/4: 配置并启动 v1.1..."
echo "------------------------------------------------------------------------"

cd ~/monthly-report-bot/monthly_report_bot_link_pack

# 检查 v1.1 核心文件
echo "检查 v1.1 核心文件..."

V1_1_FILES=(
    "monthly_report_bot_ws_v1.1.py"
    "websocket_handler_v1_1.py"
    "card_design_ws_v1_1.py"
    "smart_interaction_ws_v1_1.py"
)

for file in "${V1_1_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ 缺少 $file"
        exit 1
    fi
done

echo ""
echo "检查 Python 语法..."

source venv/bin/activate

if python3 -m py_compile monthly_report_bot_ws_v1.1.py 2>/dev/null; then
    echo "✅ Python 语法检查通过"
else
    echo "❌ Python 语法错误"
    exit 1
fi

echo ""
echo "更新 systemd 服务配置为 v1.1..."

# 更新 systemd service 文件
sudo bash -c 'cat > /etc/systemd/system/monthly-report-bot.service << EOL
[Unit]
Description=Monthly Report Bot v1.1 (WebSocket)
After=network.target

[Service]
Type=simple
User=hdi918072
WorkingDirectory=/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack
Environment=PATH=/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/venv/bin
ExecStart=/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/venv/bin/python3 /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot_ws_v1.1.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL'

echo "✅ Systemd 服务配置已更新"
echo ""

# 重新加载 systemd
sudo systemctl daemon-reload

echo "启动 v1.1 服务..."

sudo systemctl start monthly-report-bot
sleep 5

if sudo systemctl is-active --quiet monthly-report-bot; then
    echo "✅ v1.1 服务已成功启动"
else
    echo "❌ v1.1 服务启动失败"
    echo ""
    echo "错误日志:"
    sudo journalctl -u monthly-report-bot -n 50 --no-pager
    exit 1
fi

echo ""

# ============================================================================
# 验证部署
# ============================================================================

echo "========================================================================"
echo "验证部署..."
echo "========================================================================"
echo ""

echo "服务状态:"
sudo systemctl status monthly-report-bot --no-pager | head -15

echo ""
echo "检查 WebSocket 连接..."
sleep 3
sudo journalctl -u monthly-report-bot -n 50 --no-pager | grep -i "websocket\|连接\|心跳" | tail -10

echo ""

# ============================================================================
# 部署完成
# ============================================================================

echo "========================================================================"
echo "✅✅✅ v1.1 部署成功！✅✅✅"
echo "========================================================================"
echo ""
echo "📋 部署信息:"
echo "  版本: v1.1 (WebSocket 长连接版)"
echo "  主程序: monthly_report_bot_ws_v1.1.py"
echo "  部署时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "📦 Git 信息:"
git log -1 --pretty=format:"  提交: %h%n  作者: %an%n  日期: %ad%n  说明: %s%n" --date=format:"%Y-%m-%d %H:%M:%S"
echo ""
echo "💾 备份位置:"
echo "  $BACKUP_DIR/backup_before_v1.1_$TIMESTAMP"
echo ""
echo "========================================================================"
echo "🧪 测试建议"
echo "========================================================================"
echo ""
echo "1. 查看实时日志:"
echo "   sudo journalctl -u monthly-report-bot -f"
echo ""
echo "2. 测试交互功能（在飞书群里发送）:"
echo "   @月报机器人 帮助"
echo "   @月报机器人 我的任务"
echo "   @月报机器人 进度"
echo ""
echo "3. 如需回滚:"
echo "   sudo systemctl stop monthly-report-bot"
echo "   cd ~/monthly-report-bot"
echo "   rm -rf monthly_report_bot_link_pack"
echo "   cp -r $BACKUP_DIR/backup_before_v1.1_$TIMESTAMP monthly_report_bot_link_pack"
echo "   sudo systemctl start monthly-report-bot"
echo ""
echo "========================================================================"
echo "📚 完整文档: 参见 DEPLOY_V1_1_TO_GCP.md"
echo "========================================================================"
