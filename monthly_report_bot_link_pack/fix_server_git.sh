#!/bin/bash
# 服务器Git配置快速修复脚本

echo "============================================================"
echo "服务器Git配置修复脚本"
echo "============================================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 步骤1: 配置Git用户信息
echo -e "${YELLOW}步骤1: 配置Git用户信息${NC}"
echo ""

read -p "请输入您的GitHub用户名: " git_username
read -p "请输入您的邮箱地址: " git_email

git config --global user.name "$git_username"
git config --global user.email "$git_email"

echo -e "${GREEN}✅ Git用户信息配置完成${NC}"
echo "   用户名: $(git config --global user.name)"
echo "   邮箱: $(git config --global user.email)"
echo ""

# 步骤2: 配置凭据存储
echo -e "${YELLOW}步骤2: 配置凭据存储${NC}"
git config --global credential.helper store
echo -e "${GREEN}✅ 凭据存储已启用${NC}"
echo ""

# 步骤3: 提示创建Personal Access Token
echo -e "${YELLOW}步骤3: 配置GitHub Personal Access Token${NC}"
echo ""
echo -e "${RED}⚠️ 重要：GitHub已不再支持密码认证${NC}"
echo ""
echo "请按照以下步骤创建Personal Access Token:"
echo ""
echo "1. 打开浏览器访问: https://github.com/settings/tokens"
echo "2. 点击 'Generate new token (classic)'"
echo "3. Note设置为: monthly-report-bot-server"
echo "4. Expiration选择: No expiration 或 90 days"
echo "5. 勾选权限: repo (完整仓库访问)"
echo "6. 点击 'Generate token'"
echo "7. 复制生成的token (格式: ghp_xxxxxxxxxxxxxxxxxxxx)"
echo ""

read -p "已创建token? (按回车继续)" dummy

echo ""
echo -e "${YELLOW}现在测试Git连接...${NC}"
echo ""

# 步骤4: 测试git pull
echo "尝试拉取代码 (git pull origin main)..."
echo "如果提示输入用户名和密码:"
echo "  - Username: 输入你的GitHub用户名"
echo "  - Password: 粘贴刚才创建的Personal Access Token"
echo ""

git pull origin main

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}============================================================${NC}"
    echo -e "${GREEN}✅ Git配置成功！${NC}"
    echo -e "${GREEN}============================================================${NC}"
    echo ""
    echo "凭据已保存到 ~/.git-credentials"
    echo "后续git操作将自动使用保存的凭据"
    echo ""
    echo "现在可以执行:"
    echo "  git pull origin main    # 拉取最新代码"
    echo "  git push origin main    # 推送代码"
else
    echo ""
    echo -e "${RED}============================================================${NC}"
    echo -e "${RED}❌ Git配置失败${NC}"
    echo -e "${RED}============================================================${NC}"
    echo ""
    echo "可能的原因:"
    echo "  1. Personal Access Token错误"
    echo "  2. Token权限不足"
    echo "  3. 网络连接问题"
    echo ""
    echo "请检查并重新运行此脚本"
fi

echo ""
echo "当前Git配置:"
git config --global --list | grep -E "(user.name|user.email|credential.helper)"
