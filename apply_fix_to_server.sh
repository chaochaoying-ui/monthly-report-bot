#!/bin/bash
################################################################################
# 一键修复脚本 - 每日提醒 @ 格式问题
# 用途: 在 GCP 服务器上应用所有修复
# 使用: bash apply_fix_to_server.sh
################################################################################

set -e  # 遇到错误立即退出

echo "========================================================================"
echo "每日提醒 @ 格式修复 - 一键部署脚本"
echo "========================================================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_DIR="$HOME/monthly-report-bot/monthly_report_bot_link_pack"
BACKUP_DIR="$HOME/monthly-report-bot/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${YELLOW}步骤 1/7: 检查项目目录${NC}"
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ 项目目录不存在: $PROJECT_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 项目目录存在${NC}"

echo -e "\n${YELLOW}步骤 2/7: 创建备份${NC}"
mkdir -p "$BACKUP_DIR"
cp "$PROJECT_DIR/monthly_report_bot_final_interactive.py" \
   "$BACKUP_DIR/monthly_report_bot_final_interactive.py.$TIMESTAMP.backup"
echo -e "${GREEN}✅ 备份已创建: $BACKUP_DIR/monthly_report_bot_final_interactive.py.$TIMESTAMP.backup${NC}"

echo -e "\n${YELLOW}步骤 3/7: 应用 @ 格式修复${NC}"
cd "$PROJECT_DIR"

# 修复 1: 第 398-402 行 - 每日提醒负责人汇总
sed -i 's|assignee_mentions\.append(f"<at id=\\"{assignee}\\"></at>")|display_name = get_user_display_name(assignee)\n            assignee_mentions.append(f"<at user_id=\\"{assignee}\\">{display_name}</at>")|g' \
    monthly_report_bot_final_interactive.py

# 修复 2: 第 457-462 行 - 每日提醒任务详情列表
sed -i 's|task_assignees\.append(f"<at id=\\"{assignee}\\"></at>")|display_name = get_user_display_name(assignee)\n                task_assignees.append(f"<at user_id=\\"{assignee}\\">{display_name}</at>")|g' \
    monthly_report_bot_final_interactive.py

echo -e "${GREEN}✅ @ 格式修复已应用${NC}"

echo -e "\n${YELLOW}步骤 4/7: 添加客户端初始化${NC}"
# 在 test_daily_reminder 函数中添加客户端初始化
# 这个需要用 Python 脚本来做，因为 sed 处理多行替换比较困难

python3 << 'PYTHON_EOF'
import re

file_path = 'monthly_report_bot_final_interactive.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已经添加了初始化代码
if 'if not init_lark_client():' not in content:
    # 在 test_daily_reminder 函数中添加初始化
    pattern = r'(async def test_daily_reminder\(\):.*?logger\.info\("开始测试每日提醒功能\.\.\."\))\s+(success = await send_daily_reminder\(\))'
    replacement = r'\1\n\n        # 初始化飞书客户端\n        if not init_lark_client():\n            logger.error("❌ 飞书客户端初始化失败")\n            return False\n\n        \2'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ 客户端初始化代码已添加")
else:
    print("✅ 客户端初始化代码已存在，跳过")
PYTHON_EOF

echo -e "${GREEN}✅ 客户端初始化已添加${NC}"

echo -e "\n${YELLOW}步骤 5/7: 验证修复${NC}"
if grep -q "display_name = get_user_display_name" monthly_report_bot_final_interactive.py; then
    COUNT=$(grep -c "display_name = get_user_display_name" monthly_report_bot_final_interactive.py)
    echo -e "${GREEN}✅ 找到 $COUNT 处 @ 格式修复${NC}"
else
    echo -e "${RED}❌ @ 格式修复未应用${NC}"
    exit 1
fi

if grep -q "if not init_lark_client():" monthly_report_bot_final_interactive.py; then
    echo -e "${GREEN}✅ 客户端初始化代码已添加${NC}"
else
    echo -e "${YELLOW}⚠️  客户端初始化代码可能未正确添加${NC}"
fi

echo -e "\n${YELLOW}步骤 6/7: 重启服务${NC}"
sudo systemctl restart monthly-report-bot
sleep 3
echo -e "${GREEN}✅ 服务已重启${NC}"

echo -e "\n${YELLOW}步骤 7/7: 检查服务状态${NC}"
if sudo systemctl is-active --quiet monthly-report-bot; then
    echo -e "${GREEN}✅ 服务运行正常${NC}"
else
    echo -e "${RED}❌ 服务未运行${NC}"
    echo "查看日志:"
    sudo journalctl -u monthly-report-bot -n 20 --no-pager
    exit 1
fi

echo ""
echo "========================================================================"
echo -e "${GREEN}✅ 修复部署完成！${NC}"
echo "========================================================================"
echo ""
echo "下一步:"
echo "1. 测试每日提醒功能:"
echo "   cd $PROJECT_DIR"
echo "   source venv/bin/activate"
echo "   python3 -c \"import asyncio; from monthly_report_bot_final_interactive import test_daily_reminder; asyncio.run(test_daily_reminder())\""
echo ""
echo "2. 检查飞书群消息，确认负责人正确显示"
echo ""
echo "3. 如果需要回滚:"
echo "   cp $BACKUP_DIR/monthly_report_bot_final_interactive.py.$TIMESTAMP.backup \\"
echo "      $PROJECT_DIR/monthly_report_bot_final_interactive.py"
echo "   sudo systemctl restart monthly-report-bot"
echo ""
echo "========================================================================"
