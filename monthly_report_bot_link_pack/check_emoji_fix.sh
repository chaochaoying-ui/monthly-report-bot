#!/bin/bash
# 检查emoji字体修复是否已部署到服务器

echo "=========================================="
echo "检查emoji字体修复部署状态"
echo "=========================================="
echo ""

# 1. 检查服务器上是否安装了emoji字体
echo "【1】检查系统emoji字体..."
echo "--------------------"
echo "Symbola 字体:"
fc-list | grep -i symbola | head -3
if [ $? -eq 0 ]; then
    echo "✅ Symbola 字体已安装"
else
    echo "❌ Symbola 字体未安装"
    echo "   安装命令: sudo apt install fonts-symbola"
fi

echo ""
echo "Noto Color Emoji 字体:"
fc-list | grep -i emoji | head -3
if [ $? -eq 0 ]; then
    echo "✅ Noto Color Emoji 字体已安装"
else
    echo "❌ Noto Color Emoji 字体未安装"
    echo "   安装命令: sudo apt install fonts-noto-color-emoji"
fi

echo ""
echo "【2】检查 chart_generator.py 中的修复..."
echo "--------------------"

# 检查是否有emoji字体配置
if grep -q "Symbola" chart_generator.py; then
    echo "✅ 代码中包含 Symbola 字体配置"
else
    echo "❌ 代码中缺少 Symbola 字体配置"
fi

# 检查是否在样式后重新应用字体
if grep -A 3 "plt.style.use" chart_generator.py | grep -q "setup_chinese_fonts"; then
    echo "✅ 在 plt.style.use 后重新调用了 setup_chinese_fonts"
else
    echo "❌ 未在 plt.style.use 后重新调用 setup_chinese_fonts"
fi

echo ""
echo "【3】检查Git提交历史..."
echo "--------------------"
git log --oneline --grep="emoji" --all | head -5
git log --oneline --since="2025-10-24" | head -10

echo ""
echo "【4】检查最后一次git pull时间..."
echo "--------------------"
echo "chart_generator.py 最后修改时间:"
ls -lh chart_generator.py | awk '{print $6, $7, $8}'

echo ""
echo "Git 状态:"
git status | head -10

echo ""
echo "【5】检查matplotlib字体缓存..."
echo "--------------------"
if [ -d ~/.cache/matplotlib ]; then
    echo "matplotlib 缓存目录存在:"
    ls -lh ~/.cache/matplotlib/ | head -5
    echo ""
    echo "⚠️  建议清除缓存: rm -rf ~/.cache/matplotlib"
else
    echo "✅ matplotlib 缓存目录不存在（已清除或首次运行）"
fi

if [ -d ~/.matplotlib ]; then
    echo ""
    echo "旧版matplotlib配置目录存在:"
    ls -lh ~/.matplotlib/ | head -5
    echo ""
    echo "⚠️  建议清除: rm -rf ~/.matplotlib"
else
    echo "✅ 旧版matplotlib配置目录不存在"
fi

echo ""
echo "【6】推荐的修复步骤（如果emoji仍然乱码）..."
echo "--------------------"
echo "1. 确保已安装emoji字体:"
echo "   sudo apt update"
echo "   sudo apt install fonts-symbola fonts-noto-color-emoji"
echo ""
echo "2. 拉取最新代码:"
echo "   git pull origin main"
echo ""
echo "3. 清除matplotlib缓存:"
echo "   rm -rf ~/.cache/matplotlib"
echo "   rm -rf ~/.matplotlib"
echo ""
echo "4. 重启服务:"
echo "   sudo systemctl restart monthly-report-bot"
echo ""
echo "5. 查看日志确认字体加载:"
echo "   sudo journalctl -u monthly-report-bot -n 100 | grep -i '字体\\|font\\|emoji'"
echo ""
echo "6. 在飞书测试:"
echo "   @月报收集系统 图表"
echo ""
echo "=========================================="
