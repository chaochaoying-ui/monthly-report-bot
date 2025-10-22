#!/bin/bash

# ============================================================================
# 安装 v1.1 缺失的依赖
# ============================================================================

echo "========================================================================"
echo "安装 v1.1 缺失的依赖包"
echo "========================================================================"
echo ""

# 停止服务
echo "停止服务..."
sudo systemctl stop monthly-report-bot
echo "✅ 服务已停止"
echo ""

# 激活虚拟环境
echo "激活虚拟环境..."
cd ~/monthly-report-bot/monthly_report_bot_link_pack
source venv/bin/activate
echo "✅ 虚拟环境已激活"
echo ""

# 安装缺失的依赖
echo "安装缺失的依赖包..."
echo "这可能需要几分钟时间..."
echo ""

pip install websockets>=12.0 aiohttp>=3.9.0 matplotlib>=3.7.0 numpy>=1.24.0 jieba>=0.42.1 langdetect>=1.0.9 -i https://pypi.tuna.tsinghua.edu.cn/simple

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 依赖安装完成"
else
    echo ""
    echo "❌ 依赖安装失败"
    exit 1
fi

echo ""
echo "验证关键依赖..."

# 验证每个依赖
python3 << 'VERIFY_EOF'
import sys

packages = [
    ('websockets', 'WebSocket 支持'),
    ('aiohttp', 'HTTP 异步支持'),
    ('matplotlib', '图表生成'),
    ('numpy', '数值计算'),
    ('jieba', '中文分词'),
    ('langdetect', '语言检测'),
]

all_ok = True
for pkg, desc in packages:
    try:
        __import__(pkg)
        print(f"✅ {pkg:15} - {desc}")
    except ImportError:
        print(f"❌ {pkg:15} - {desc} (缺失)")
        all_ok = False

if all_ok:
    print("\n✅ 所有依赖已就绪")
    sys.exit(0)
else:
    print("\n❌ 部分依赖缺失")
    sys.exit(1)
VERIFY_EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 依赖验证失败，请检查错误信息"
    exit 1
fi

echo ""
echo "========================================================================"
echo "启动 v1.1 服务"
echo "========================================================================"
echo ""

sudo systemctl start monthly-report-bot
sleep 3

if sudo systemctl is-active --quiet monthly-report-bot; then
    echo "✅ 服务已成功启动"
    echo ""
    echo "服务状态:"
    sudo systemctl status monthly-report-bot --no-pager | head -15
    echo ""
    echo "最新日志:"
    sudo journalctl -u monthly-report-bot -n 30 --no-pager | tail -20
else
    echo "❌ 服务启动失败"
    echo ""
    echo "错误日志:"
    sudo journalctl -u monthly-report-bot -n 50 --no-pager
    exit 1
fi

echo ""
echo "========================================================================"
echo "✅✅✅ 依赖安装完成，v1.1 已成功启动！✅✅✅"
echo "========================================================================"
