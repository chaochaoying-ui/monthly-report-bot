#!/bin/bash
# -*- coding: utf-8 -*-
# =============================================================================
# GCP 部署脚本 - 已完成人员排行榜功能
# =============================================================================

set -e  # 遇到错误立即退出

echo "=========================================="
echo "🚀 开始部署已完成人员排行榜功能"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目目录
PROJECT_DIR="$HOME/monthly-report-bot/monthly_report_bot_link_pack"

# 步骤1：检查当前目录
echo ""
echo "📂 步骤1: 检查项目目录..."
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ 项目目录不存在: $PROJECT_DIR${NC}"
    exit 1
fi
cd "$PROJECT_DIR"
echo -e "${GREEN}✅ 当前目录: $(pwd)${NC}"

# 步骤2：拉取最新代码
echo ""
echo "📥 步骤2: 拉取最新代码..."
git fetch origin
git pull origin main
echo -e "${GREEN}✅ 代码更新完成${NC}"

# 步骤3：显示最新提交
echo ""
echo "📝 最新提交记录:"
git log --oneline -5

# 步骤4：检查matplotlib是否已安装
echo ""
echo "📦 步骤4: 检查依赖库..."
if python3 -c "import matplotlib" 2>/dev/null; then
    echo -e "${GREEN}✅ matplotlib 已安装${NC}"
else
    echo -e "${YELLOW}⚠️  matplotlib 未安装，开始安装...${NC}"
    pip3 install matplotlib seaborn numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo -e "${GREEN}✅ 依赖库安装完成${NC}"
fi

# 步骤5：验证必需文件
echo ""
echo "📄 步骤5: 验证必需文件..."
required_files=(
    "chart_generator.py"
    "task_stats.json"
    "monthly_report_bot_final_interactive.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ 缺失文件: $file${NC}"
        exit 1
    fi
done

# 步骤6：创建charts目录
echo ""
echo "📁 步骤6: 创建图表目录..."
mkdir -p charts
echo -e "${GREEN}✅ charts 目录已创建${NC}"

# 步骤7：测试图表生成功能
echo ""
echo "🧪 步骤7: 测试图表生成功能..."
if [ -f "test_chart_generator.py" ]; then
    echo "运行测试脚本..."
    python3 test_chart_generator.py

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 图表生成测试成功${NC}"
    else
        echo -e "${RED}❌ 图表生成测试失败${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  测试脚本不存在，跳过测试${NC}"
fi

# 步骤8：检查systemd服务状态
echo ""
echo "🔍 步骤8: 检查服务状态..."
SERVICE_NAME="monthly-report-bot-interactive.service"

if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${GREEN}✅ 服务正在运行${NC}"

    # 询问是否重启服务
    echo ""
    echo -e "${YELLOW}是否需要重启服务以应用更新？(y/n)${NC}"
    read -r answer

    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        echo "🔄 重启服务..."
        sudo systemctl restart "$SERVICE_NAME"
        sleep 3

        if systemctl is-active --quiet "$SERVICE_NAME"; then
            echo -e "${GREEN}✅ 服务重启成功${NC}"
        else
            echo -e "${RED}❌ 服务重启失败${NC}"
            echo "查看服务日志:"
            sudo journalctl -u "$SERVICE_NAME" -n 50
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠️  跳过服务重启（需要手动重启以应用更新）${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  服务未运行${NC}"
    echo "启动服务..."
    sudo systemctl start "$SERVICE_NAME"
    sleep 3

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ 服务启动成功${NC}"
    else
        echo -e "${RED}❌ 服务启动失败${NC}"
        exit 1
    fi
fi

# 步骤9：验证服务状态
echo ""
echo "✅ 步骤9: 验证服务状态..."
sudo systemctl status "$SERVICE_NAME" --no-pager -l

# 步骤10：显示最新生成的图表
echo ""
echo "📊 步骤10: 检查生成的图表..."
if [ -d "charts" ]; then
    echo "最近生成的图表文件:"
    ls -lht charts/*.png | head -5
else
    echo -e "${YELLOW}⚠️  charts 目录为空${NC}"
fi

# 完成
echo ""
echo "=========================================="
echo -e "${GREEN}✅ 部署完成！${NC}"
echo "=========================================="
echo ""
echo "📋 功能清单:"
echo "  ✅ 用户ID映射已完善（17个用户）"
echo "  ✅ 排行榜金银铜配色已启用"
echo "  ✅ 勋章系统已激活"
echo "  ✅ 排名标记已添加"
echo ""
echo "🎯 使用方式:"
echo "  在飞书群聊中发送以下命令查看美化的统计图表："
echo "  - '图表' / '可视化' / '饼图' / '统计图'"
echo ""
echo "📝 查看日志:"
echo "  sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "🔄 重启服务:"
echo "  sudo systemctl restart $SERVICE_NAME"
echo ""
echo "=========================================="
