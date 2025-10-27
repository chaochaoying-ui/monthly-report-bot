#!/bin/bash

# 部署 emoji 显示修复 (坑 #6.5)
# 修复日期: 2025-10-27
# 相关提交: f409649

set -e  # 遇到错误立即退出

echo "=========================================="
echo "部署 Emoji 显示修复"
echo "=========================================="
echo ""

# 1. 进入项目目录
echo "📁 [1/7] 进入项目目录..."
cd /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack

# 2. 备份当前代码
echo "💾 [2/7] 备份当前代码..."
cp chart_generator.py chart_generator.py.backup_$(date +%Y%m%d_%H%M%S)

# 3. 拉取最新代码
echo "⬇️  [3/7] 拉取最新代码..."
git pull origin main

# 4. 验证关键修复已应用
echo "✅ [4/7] 验证修复代码..."
if grep -q "# 确保字体配置在每次生成图表前都被应用" chart_generator.py; then
    echo "   ✅ 找到字体配置修复代码"
    count=$(grep -c "# 确保字体配置在每次生成图表前都被应用" chart_generator.py)
    echo "   ✅ 4个图表方法中有 $count 个已添加字体配置"
    if [ "$count" -ne 4 ]; then
        echo "   ⚠️  警告：预期4个方法都应该有字体配置，实际只有 $count 个"
    fi
else
    echo "   ❌ 错误：未找到字体配置修复代码！"
    exit 1
fi

# 5. 清除 matplotlib 字体缓存
echo "🗑️  [5/7] 清除 matplotlib 字体缓存..."
rm -rf ~/.cache/matplotlib
rm -rf ~/.matplotlib
echo "   ✅ 缓存已清除"

# 6. 重启服务
echo "🔄 [6/7] 重启服务..."
sudo systemctl restart monthly-report-bot

# 等待服务启动
sleep 3

# 7. 检查服务状态
echo "🔍 [7/7] 检查服务状态..."
if systemctl is-active --quiet monthly-report-bot; then
    echo "   ✅ 服务运行正常"
else
    echo "   ❌ 服务启动失败！"
    sudo systemctl status monthly-report-bot
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "📝 下一步："
echo "1. 查看日志验证字体配置："
echo "   sudo journalctl -u monthly-report-bot -f | grep '开始配置中文和 emoji 字体'"
echo ""
echo "2. 在飞书生成新图表测试："
echo "   发送: @月报收集系统 图表"
echo ""
echo "3. 检查是否还有字体警告："
echo "   sudo journalctl -u monthly-report-bot -n 100 | grep 'missing from font'"
echo ""
echo "🎯 预期结果："
echo "   - 看到 '开始配置中文和 emoji 字体' 日志"
echo "   - 看到 '✅ 成功加载 Symbola emoji 字体' 日志"
echo "   - 图表中 🥇🥈🥉 emoji 正常显示"
echo "   - 没有 'Glyph ... missing from font(s)' 警告"
echo ""
