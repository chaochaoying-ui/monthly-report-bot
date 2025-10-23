#!/bin/bash
# 切换到测试群组

echo "============================================================"
echo "切换月报机器人到测试群"
echo "============================================================"
echo ""

# 测试群ID
TEST_GROUP_ID="oc_07f2d3d314f00fc29baf323a3a589972"

# 正式群ID（如果已知，记录下来以便后续切换回来）
PROD_GROUP_ID="oc_e4218b232326ea81a077b65c4cd16ce5"  # 从之前的文件中找到的

echo "📋 当前配置:"
echo "  测试群ID: $TEST_GROUP_ID"
echo "  正式群ID: $PROD_GROUP_ID"
echo ""

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "❌ 错误: .env 文件不存在"
    exit 1
fi

echo "📝 备份当前 .env 文件..."
cp .env .env.backup_$(date +%Y%m%d_%H%M%S)

echo "🔄 更新 CHAT_ID 为测试群..."

# 检查是否已有 CHAT_ID 配置
if grep -q "^CHAT_ID=" .env; then
    # 替换现有的 CHAT_ID
    sed -i "s/^CHAT_ID=.*/CHAT_ID=$TEST_GROUP_ID/" .env
    echo "✅ 已更新 CHAT_ID"
else
    # 添加新的 CHAT_ID
    echo "" >> .env
    echo "# 群组ID (测试群)" >> .env
    echo "CHAT_ID=$TEST_GROUP_ID" >> .env
    echo "✅ 已添加 CHAT_ID"
fi

echo ""
echo "📋 当前 .env 文件中的 CHAT_ID:"
grep "^CHAT_ID=" .env

echo ""
echo "🔄 重启服务..."
sudo systemctl restart monthly-report-bot

echo ""
echo "⏳ 等待服务启动..."
sleep 5

echo ""
echo "📊 检查服务状态..."
sudo systemctl status monthly-report-bot --no-pager | head -15

echo ""
echo "📋 查看最近日志..."
sudo journalctl -u monthly-report-bot -n 20 --no-pager | tail -10

echo ""
echo "============================================================"
echo "✅ 切换完成！"
echo "============================================================"
echo ""
echo "现在机器人将在测试群中运行: $TEST_GROUP_ID"
echo ""
echo "测试完成后，如需切换回正式群，运行:"
echo "  bash switch_to_prod_group.sh"
echo ""
echo "或手动修改 .env 中的 CHAT_ID 并重启服务:"
echo "  sed -i 's/^CHAT_ID=.*/CHAT_ID=$PROD_GROUP_ID/' .env"
echo "  sudo systemctl restart monthly-report-bot"
echo ""
