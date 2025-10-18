#!/bin/bash
# GCP Compute Engine 自动部署脚本
# 用途：在GCP虚拟机上自动部署月报机器人

echo "=========================================="
echo "月报机器人 GCP 部署脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}请不要使用root用户运行此脚本${NC}"
   exit 1
fi

echo -e "${GREEN}步骤 1/8: 更新系统包列表...${NC}"
# 等待 apt 锁释放
while sudo fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 || sudo fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do
    echo "等待其他apt进程完成..."
    sleep 2
done
sudo apt update -y || {
    echo -e "${YELLOW}apt update失败，继续执行...${NC}"
}

echo -e "${GREEN}步骤 2/8: 安装Python 3.11和依赖...${NC}"
sudo apt install -y python3.11 python3.11-venv python3-pip git wget curl

echo -e "${GREEN}步骤 3/8: 克隆项目...${NC}"
cd ~
if [ -d "monthly-report-bot" ]; then
    echo "项目目录已存在，拉取最新代码..."
    cd monthly-report-bot
    git pull
else
    echo "克隆项目..."
    git clone https://github.com/chaochaoying-ui/monthly-report-bot.git
    cd monthly-report-bot
fi

echo -e "${GREEN}步骤 4/8: 设置Python虚拟环境...${NC}"
cd monthly_report_bot_link_pack
python3.11 -m venv venv
source venv/bin/activate

echo -e "${GREEN}步骤 5/8: 安装Python依赖...${NC}"
pip install --upgrade pip
# 安装核心依赖
pip install requests>=2.31.0 PyYAML>=6.0.1 pytz>=2023.3 cryptography>=41.0.0 websockets>=11.0 python-dotenv>=1.0.0 lark-oapi || {
    echo -e "${RED}依赖安装失败${NC}"
    exit 1
}

echo -e "${GREEN}步骤 6/8: 配置环境变量...${NC}"
# 总是重新创建 .env 文件以确保变量名正确
echo "创建/更新.env文件..."
cat > .env << 'EOF'
# 飞书应用配置（注意：变量名必须与代码中一致）
APP_ID=cli_a8fd44a9453cd00c
APP_SECRET=jsVoFWgaaw05en6418h7xbhV5oXxAwIm
CHAT_ID=oc_e4218b232326ea81a077b65c4cd16ce5
WELCOME_CARD_ID=AAqInYqWzIiu6
FILE_URL=https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd
VERIFICATION_TOKEN=v_01J6RE0Q4VEcCQ0hFg1RbdLT
TZ=America/Argentina/Buenos_Aires
PYTHONIOENCODING=utf-8
EOF
echo -e "${GREEN}.env文件已创建${NC}"

echo -e "${GREEN}步骤 7/8: 创建systemd服务...${NC}"
# 获取当前用户和工作目录
CURRENT_USER=$(whoami)
WORK_DIR=$(pwd)
VENV_PYTHON="$WORK_DIR/venv/bin/python"

sudo tee /etc/systemd/system/monthly-report-bot.service > /dev/null << EOF
[Unit]
Description=Monthly Report Bot for Feishu
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$WORK_DIR
Environment="PATH=$WORK_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=$WORK_DIR/.env
ExecStart=$VENV_PYTHON monthly_report_bot_final_interactive.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/monthly-report-bot.log
StandardError=append:/var/log/monthly-report-bot-error.log

[Install]
WantedBy=multi-user.target
EOF

# 创建日志文件
sudo touch /var/log/monthly-report-bot.log
sudo touch /var/log/monthly-report-bot-error.log
sudo chown $CURRENT_USER:$CURRENT_USER /var/log/monthly-report-bot.log
sudo chown $CURRENT_USER:$CURRENT_USER /var/log/monthly-report-bot-error.log

echo -e "${GREEN}步骤 8/8: 启动服务...${NC}"
# 重新加载systemd
sudo systemctl daemon-reload

# 停止旧服务（如果存在）
sudo systemctl stop monthly-report-bot 2>/dev/null || true

# 启动服务
sudo systemctl start monthly-report-bot

# 设置开机自启
sudo systemctl enable monthly-report-bot

# 等待几秒让服务启动
sleep 5

# 检查服务状态
if sudo systemctl is-active --quiet monthly-report-bot; then
    echo -e "${GREEN}=========================================="
    echo "✅ 部署成功！"
    echo "==========================================${NC}"
    echo ""
    echo "服务状态："
    sudo systemctl status monthly-report-bot --no-pager -l
    echo ""
    echo -e "${GREEN}查看实时日志：${NC}"
    echo "  sudo tail -f /var/log/monthly-report-bot.log"
    echo ""
    echo -e "${GREEN}查看错误日志：${NC}"
    echo "  sudo tail -f /var/log/monthly-report-bot-error.log"
    echo ""
    echo -e "${GREEN}其他命令：${NC}"
    echo "  查看状态: sudo systemctl status monthly-report-bot"
    echo "  查看systemd日志: sudo journalctl -u monthly-report-bot -f"
    echo "  重启服务: sudo systemctl restart monthly-report-bot"
    echo "  停止服务: sudo systemctl stop monthly-report-bot"
    echo ""
    echo -e "${GREEN}机器人已在后台运行，现在可以在飞书群聊中@机器人测试！${NC}"
    echo ""
    echo -e "${YELLOW}正在显示最近的日志（按Ctrl+C退出）...${NC}"
    sleep 2
    sudo tail -n 20 /var/log/monthly-report-bot.log
else
    echo -e "${RED}=========================================="
    echo "❌ 服务启动失败"
    echo "==========================================${NC}"
    echo ""
    echo -e "${YELLOW}systemd日志：${NC}"
    sudo journalctl -u monthly-report-bot -n 30 --no-pager
    echo ""
    echo -e "${YELLOW}错误日志文件：${NC}"
    sudo tail -n 20 /var/log/monthly-report-bot-error.log 2>/dev/null || echo "错误日志文件为空或不存在"
    echo ""
    echo -e "${YELLOW}请尝试手动运行以下命令排查问题：${NC}"
    echo "  cd ~/monthly-report-bot/monthly_report_bot_link_pack"
    echo "  source venv/bin/activate"
    echo "  python monthly_report_bot_final_interactive.py"
    exit 1
fi

