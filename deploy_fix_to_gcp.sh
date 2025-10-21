#!/bin/bash
################################################################################
# GCP 服务器 - 每日提醒 @ 格式修复部署脚本
# 用途: 在 GCP 服务器上应用所有修复
# 使用方法:
#   1. 将此脚本上传到 GCP 服务器
#   2. chmod +x deploy_fix_to_gcp.sh
#   3. ./deploy_fix_to_gcp.sh
################################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目信息
PROJECT_DIR="$HOME/monthly-report-bot/monthly_report_bot_link_pack"
BACKUP_DIR="$HOME/monthly-report-bot/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MAIN_FILE="monthly_report_bot_final_interactive.py"

echo -e "${BLUE}========================================================================"
echo "GCP 服务器 - 每日提醒 @ 格式修复部署"
echo "========================================================================${NC}"

################################################################################
# 步骤 1: 环境检查
################################################################################
echo -e "\n${YELLOW}[1/8] 检查环境...${NC}"

if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ 项目目录不存在: $PROJECT_DIR${NC}"
    echo "请先克隆项目到服务器"
    exit 1
fi

cd "$PROJECT_DIR"
echo -e "${GREEN}✅ 项目目录: $PROJECT_DIR${NC}"

if [ ! -f "$MAIN_FILE" ]; then
    echo -e "${RED}❌ 主文件不存在: $MAIN_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 主文件存在${NC}"

################################################################################
# 步骤 2: 创建备份
################################################################################
echo -e "\n${YELLOW}[2/8] 创建备份...${NC}"

mkdir -p "$BACKUP_DIR"
cp "$MAIN_FILE" "$BACKUP_DIR/${MAIN_FILE}.$TIMESTAMP.backup"
echo -e "${GREEN}✅ 备份已创建:${NC}"
echo "   $BACKUP_DIR/${MAIN_FILE}.$TIMESTAMP.backup"

################################################################################
# 步骤 3: 应用 @ 格式修复
################################################################################
echo -e "\n${YELLOW}[3/8] 应用 @ 格式修复...${NC}"

# 创建 Python 修复脚本
cat > /tmp/apply_at_format_fix.py << 'PYTHON_EOF'
#!/usr/bin/env python3
"""应用 @ 格式修复"""

import re
import sys

def apply_fix(file_path):
    """应用所有 @ 格式修复"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 修复 1: send_daily_reminder() - 负责人汇总 (行 398-402)
    pattern1 = r'(# 创建@负责人的文本\s+assignee_mentions = \[\]\s+for assignee in incomplete_assignees:\s+)assignee_mentions\.append\(f"<at id=\\"\\{assignee\\}\\"></at>"\)'
    replacement1 = r'\1display_name = get_user_display_name(assignee)\n            assignee_mentions.append(f"<at user_id=\\"{assignee}\\">{display_name}</at>")'
    content = re.sub(pattern1, replacement1, content)

    # 修复 2: send_daily_reminder() - 任务详情列表 (行 457-462)
    pattern2 = r'(# 添加未完成任务列表（最多显示前10个）\s+for i, task in enumerate\(incomplete_tasks\[:10\], 1\):\s+task_assignees = \[\]\s+for assignee in task\.get\(\'assignees\', \[\]\):\s+)task_assignees\.append\(f"<at id=\\"\\{assignee\\}\\"></at>"\)'
    replacement2 = r'\1display_name = get_user_display_name(assignee)\n                task_assignees.append(f"<at user_id=\\"{assignee}\\">{display_name}</at>")'
    content = re.sub(pattern2, replacement2, content)

    # 修复 3: 任务列表显示函数 (行 797-805)
    pattern3 = r'(task_list_text = ""\s+for i, task in enumerate\(all_tasks, 1\):\s+assignee_mentions = ""\s+if task\["assignees"\]:\s+for assignee in task\["assignees"\]:\s+)assignee_mentions \+= f"<at user_id=\\"\\{assignee\\}\\"></at> "'
    replacement3 = r'\1display_name = get_user_display_name(assignee)\n                assignee_mentions += f"<at user_id=\\"{assignee}\\">{display_name}</at> "'
    content = re.sub(pattern3, replacement3, content)

    # 检查是否有修改
    if content == original_content:
        print("⚠️  未检测到需要修复的 @ 格式（可能已经修复过）")
        return False

    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "monthly_report_bot_final_interactive.py"

    if apply_fix(file_path):
        print("✅ @ 格式修复已应用")
    else:
        print("ℹ️  @ 格式已经是最新版本")
PYTHON_EOF

# 执行修复
python3 /tmp/apply_at_format_fix.py "$MAIN_FILE"
echo -e "${GREEN}✅ @ 格式修复完成${NC}"

################################################################################
# 步骤 4: 添加客户端初始化
################################################################################
echo -e "\n${YELLOW}[4/8] 添加测试函数客户端初始化...${NC}"

# 创建 Python 脚本添加初始化代码
cat > /tmp/add_client_init.py << 'PYTHON_EOF'
#!/usr/bin/env python3
"""添加飞书客户端初始化"""

import re
import sys

def add_client_init(file_path):
    """在 test_daily_reminder 函数中添加客户端初始化"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已经添加了初始化代码
    if 'if not init_lark_client():' in content:
        print("✅ 客户端初始化代码已存在，跳过")
        return False

    # 在 test_daily_reminder 函数中添加初始化
    pattern = r'(async def test_daily_reminder\(\):.*?logger\.info\("开始测试每日提醒功能\.\.\."\)\s+)(success = await send_daily_reminder\(\))'
    replacement = r'\1\n        # 初始化飞书客户端\n        if not init_lark_client():\n            logger.error("❌ 飞书客户端初始化失败")\n            return False\n\n        \2'

    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "monthly_report_bot_final_interactive.py"

    if add_client_init(file_path):
        print("✅ 客户端初始化代码已添加")
PYTHON_EOF

python3 /tmp/add_client_init.py "$MAIN_FILE"
echo -e "${GREEN}✅ 客户端初始化完成${NC}"

################################################################################
# 步骤 5: 验证修复
################################################################################
echo -e "\n${YELLOW}[5/8] 验证修复...${NC}"

# 验证 @ 格式修复
AT_FORMAT_COUNT=$(grep -c "display_name = get_user_display_name" "$MAIN_FILE" || true)
if [ "$AT_FORMAT_COUNT" -ge 3 ]; then
    echo -e "${GREEN}✅ 找到 $AT_FORMAT_COUNT 处 @ 格式修复${NC}"
else
    echo -e "${YELLOW}⚠️  只找到 $AT_FORMAT_COUNT 处 @ 格式修复（预期至少 3 处）${NC}"
fi

# 验证客户端初始化
if grep -q "if not init_lark_client():" "$MAIN_FILE"; then
    echo -e "${GREEN}✅ 客户端初始化代码已添加${NC}"
else
    echo -e "${YELLOW}⚠️  客户端初始化代码未找到${NC}"
fi

# 检查语法错误
echo -e "\n${YELLOW}检查 Python 语法...${NC}"
if python3 -m py_compile "$MAIN_FILE" 2>/dev/null; then
    echo -e "${GREEN}✅ Python 语法检查通过${NC}"
else
    echo -e "${RED}❌ Python 语法错误！${NC}"
    echo "请检查文件: $MAIN_FILE"
    exit 1
fi

################################################################################
# 步骤 6: 重启服务
################################################################################
echo -e "\n${YELLOW}[6/8] 重启 monthly-report-bot 服务...${NC}"

if sudo systemctl restart monthly-report-bot; then
    echo -e "${GREEN}✅ 服务已重启${NC}"
else
    echo -e "${RED}❌ 服务重启失败${NC}"
    echo "请检查服务状态: sudo systemctl status monthly-report-bot"
    exit 1
fi

sleep 3

################################################################################
# 步骤 7: 检查服务状态
################################################################################
echo -e "\n${YELLOW}[7/8] 检查服务状态...${NC}"

if sudo systemctl is-active --quiet monthly-report-bot; then
    echo -e "${GREEN}✅ 服务运行正常${NC}"

    # 显示最近日志
    echo -e "\n${BLUE}最近日志:${NC}"
    sudo journalctl -u monthly-report-bot -n 10 --no-pager | tail -5
else
    echo -e "${RED}❌ 服务未运行${NC}"
    echo ""
    echo "最近日志:"
    sudo journalctl -u monthly-report-bot -n 20 --no-pager
    exit 1
fi

################################################################################
# 步骤 8: 测试每日提醒功能
################################################################################
echo -e "\n${YELLOW}[8/8] 测试每日提醒功能...${NC}"
echo -e "${BLUE}正在发送测试提醒到飞书群...${NC}"

cd "$PROJECT_DIR"
source venv/bin/activate

# 运行测试
if python3 -c "import asyncio; from monthly_report_bot_final_interactive import test_daily_reminder; asyncio.run(test_daily_reminder())" 2>&1 | grep -q "每日提醒测试成功"; then
    echo -e "${GREEN}✅ 每日提醒测试成功！${NC}"
else
    echo -e "${YELLOW}⚠️  测试未完全成功，请查看上面的输出${NC}"
fi

################################################################################
# 完成
################################################################################
echo ""
echo -e "${BLUE}========================================================================"
echo "✅ 修复部署完成！"
echo "========================================================================${NC}"
echo ""
echo -e "${GREEN}修复内容:${NC}"
echo "  • @ 格式修复 (3 处)"
echo "  • 测试函数客户端初始化"
echo ""
echo -e "${GREEN}下一步:${NC}"
echo "  1. 查看飞书群消息，确认每日提醒显示正确"
echo "  2. 检查负责人 @ 是否正确显示（如: @周超, @张三）"
echo "  3. 点击 @ 确认可以跳转到对应用户"
echo ""
echo -e "${YELLOW}查看日志:${NC}"
echo "  sudo journalctl -u monthly-report-bot -f"
echo ""
echo -e "${YELLOW}如需回滚:${NC}"
echo "  cp $BACKUP_DIR/${MAIN_FILE}.$TIMESTAMP.backup \\"
echo "     $PROJECT_DIR/$MAIN_FILE"
echo "  sudo systemctl restart monthly-report-bot"
echo ""
echo -e "${BLUE}========================================================================${NC}"
