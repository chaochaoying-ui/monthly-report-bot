#!/bin/bash

# GCP Monthly Report Bot Service Fix Script
# 修复 systemd 服务配置问题

# --- 配置 ---
PROJECT_DIR="$HOME/monthly-report-bot"
BOT_APP_DIR="monthly_report_bot_link_pack"
VENV_DIR="venv"
SERVICE_NAME="monthly-report-bot"
MAIN_SCRIPT="monthly_report_bot_final_interactive.py"

# --- 颜色输出 ---
log_info() {
    echo -e "\e[32m[INFO]\e[0m $1"
}

log_error() {
    echo -e "\e[31m[ERROR]\e[0m $1"
}

log_warning() {
    echo -e "\e[33m[WARNING]\e[0m $1"
}

# --- 主要修复步骤 ---

log_info "=========================================="
log_info "月报机器人服务修复脚本"
log_info "=========================================="

# 1. 检查项目目录
log_info "步骤 1/6: 检查项目目录..."
if [ ! -d "$PROJECT_DIR/$BOT_APP_DIR" ]; then
    log_error "项目目录不存在: $PROJECT_DIR/$BOT_APP_DIR"
    exit 1
fi
log_info "项目目录存在: $PROJECT_DIR/$BOT_APP_DIR"

# 2. 检查主程序文件
log_info "步骤 2/6: 检查主程序文件..."
FULL_SCRIPT_PATH="$PROJECT_DIR/$BOT_APP_DIR/$MAIN_SCRIPT"
if [ ! -f "$FULL_SCRIPT_PATH" ]; then
    log_error "主程序文件不存在: $FULL_SCRIPT_PATH"
    log_info "可用的 Python 文件："
    ls -la "$PROJECT_DIR/$BOT_APP_DIR"/*.py 2>/dev/null || log_warning "没有找到 Python 文件"
    exit 1
fi
log_info "主程序文件存在: $FULL_SCRIPT_PATH"

# 3. 检查并修复虚拟环境
log_info "步骤 3/6: 检查虚拟环境..."
VENV_PATH="$PROJECT_DIR/$BOT_APP_DIR/$VENV_DIR"
PYTHON_BIN="$VENV_PATH/bin/python3"

if [ ! -d "$VENV_PATH" ]; then
    log_warning "虚拟环境不存在，正在创建..."
    cd "$PROJECT_DIR/$BOT_APP_DIR" || exit 1
    python3.11 -m venv "$VENV_DIR" || {
        log_error "创建虚拟环境失败"
        exit 1
    }
fi

if [ ! -f "$PYTHON_BIN" ]; then
    log_error "Python 解释器不存在: $PYTHON_BIN"
    exit 1
fi

log_info "虚拟环境存在: $VENV_PATH"
log_info "Python 版本: $($PYTHON_BIN --version)"

# 检查并安装依赖
log_info "检查 Python 依赖..."
cd "$PROJECT_DIR/$BOT_APP_DIR" || exit 1
source "$VENV_PATH/bin/activate"

# 检查关键依赖
MISSING_DEPS=()
$PYTHON_BIN -c "import websockets" 2>/dev/null || MISSING_DEPS+=("websockets")
$PYTHON_BIN -c "import requests" 2>/dev/null || MISSING_DEPS+=("requests")
$PYTHON_BIN -c "import yaml" 2>/dev/null || MISSING_DEPS+=("PyYAML")

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    log_warning "缺少依赖: ${MISSING_DEPS[*]}"
    log_info "正在安装依赖..."
    pip install --upgrade pip
    pip install requests>=2.31.0 PyYAML>=6.0.1 pytz>=2023.3 cryptography>=41.0.0 websockets>=11.0 || {
        log_error "依赖安装失败"
        exit 1
    }
    log_info "依赖安装完成"
else
    log_info "所有依赖已安装"
fi

# 4. 检查 .env 文件
log_info "步骤 4/6: 检查 .env 文件..."
ENV_FILE="$PROJECT_DIR/$BOT_APP_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    log_error ".env 文件不存在: $ENV_FILE"
    exit 1
fi
log_info ".env 文件存在"

# 5. 重新创建 systemd 服务文件（修复版本）
log_info "步骤 5/6: 重新创建 systemd 服务文件..."
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
WORKING_DIR="$PROJECT_DIR/$BOT_APP_DIR"

sudo bash -c "cat << 'EOF' > $SERVICE_FILE
[Unit]
Description=Monthly Report Bot Service
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORKING_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$PYTHON_BIN $FULL_SCRIPT_PATH
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=monthly-report-bot

[Install]
WantedBy=multi-user.target
EOF
" || {
    log_error "创建服务文件失败"
    exit 1
}

log_info "服务文件已创建: $SERVICE_FILE"
log_info "服务配置内容："
sudo cat "$SERVICE_FILE"

# 6. 重新加载并启动服务
log_info "步骤 6/6: 重新加载并启动服务..."
sudo systemctl daemon-reload || {
    log_error "重新加载 systemd 失败"
    exit 1
}

sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true
sudo systemctl start "$SERVICE_NAME" || {
    log_error "服务启动失败"
    log_error "请查看错误日志："
    sudo journalctl -u "$SERVICE_NAME" -n 50 --no-pager
    exit 1
}

sudo systemctl enable "$SERVICE_NAME" || {
    log_warning "设置开机自启动失败"
}

# 检查服务状态
log_info "=========================================="
log_info "检查服务状态..."
log_info "=========================================="
sudo systemctl status "$SERVICE_NAME" --no-pager -l

log_info ""
log_info "=========================================="
log_info "✅ 修复完成！"
log_info "=========================================="
log_info "常用命令："
log_info "  查看服务状态:   sudo systemctl status $SERVICE_NAME"
log_info "  查看实时日志:   sudo journalctl -u $SERVICE_NAME -f"
log_info "  查看最近日志:   sudo journalctl -u $SERVICE_NAME -n 100"
log_info "  重启服务:       sudo systemctl restart $SERVICE_NAME"
log_info "  停止服务:       sudo systemctl stop $SERVICE_NAME"
log_info "=========================================="

