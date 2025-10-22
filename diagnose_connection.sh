#!/bin/bash

# ============================================================================
# 诊断 v1.1 WebSocket 连接问题
# ============================================================================

echo "========================================================================"
echo "诊断 v1.1 WebSocket 连接问题"
echo "========================================================================"
echo ""

cd ~/monthly-report-bot/monthly_report_bot_link_pack

echo "步骤 1: 检查环境变量配置"
echo "------------------------------------------------------------------------"

if [ -f .env ]; then
    echo "✅ .env 文件存在"
    echo ""
    echo "环境变量内容（已脱敏）："
    echo ""

    # 读取并显示环境变量（脱敏）
    if grep -q "FEISHU_APP_ID" .env; then
        APP_ID=$(grep "FEISHU_APP_ID" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'" | tr -d ' ')
        echo "FEISHU_APP_ID = ${APP_ID:0:8}... (长度: ${#APP_ID})"
    else
        echo "❌ 缺少 FEISHU_APP_ID"
    fi

    if grep -q "FEISHU_APP_SECRET" .env; then
        APP_SECRET=$(grep "FEISHU_APP_SECRET" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'" | tr -d ' ')
        echo "FEISHU_APP_SECRET = ${APP_SECRET:0:8}... (长度: ${#APP_SECRET})"
    else
        echo "❌ 缺少 FEISHU_APP_SECRET"
    fi

    if grep -q "CHAT_ID" .env; then
        CHAT_ID=$(grep "CHAT_ID" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'" | tr -d ' ')
        echo "CHAT_ID = ${CHAT_ID:0:8}... (长度: ${#CHAT_ID})"
    else
        echo "❌ 缺少 CHAT_ID"
    fi

    if grep -q "FILE_URL" .env; then
        echo "FILE_URL = ✅ 已配置"
    else
        echo "FILE_URL = ⚠️  未配置（可选）"
    fi
else
    echo "❌ .env 文件不存在"
    echo ""
    echo "需要创建 .env 文件，包含以下内容："
    echo ""
    echo "FEISHU_APP_ID=your_app_id"
    echo "FEISHU_APP_SECRET=your_app_secret"
    echo "CHAT_ID=your_chat_id"
    echo "FILE_URL=your_file_url"
fi

echo ""
echo "步骤 2: 检查 APP_ID 和 APP_SECRET 格式"
echo "------------------------------------------------------------------------"

source venv/bin/activate

python3 << 'CHECK_EOF'
import os
import sys
from pathlib import Path

# 加载 .env
env_file = Path(".env")
if not env_file.exists():
    print("❌ .env 文件不存在")
    sys.exit(1)

env_vars = {}
with open(env_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip().strip('"').strip("'")

app_id = env_vars.get('FEISHU_APP_ID', '')
app_secret = env_vars.get('FEISHU_APP_SECRET', '')
chat_id = env_vars.get('CHAT_ID', '')

print("验证结果:")
print("")

# 验证 APP_ID
if app_id:
    if app_id.startswith('cli_'):
        print(f"✅ APP_ID 格式正确: cli_xxxxxxxx (长度: {len(app_id)})")
    else:
        print(f"⚠️  APP_ID 格式异常: 应该以 'cli_' 开头")
        print(f"   当前值: {app_id[:10]}...")
else:
    print("❌ APP_ID 为空")

# 验证 APP_SECRET
if app_secret:
    if len(app_secret) > 20:
        print(f"✅ APP_SECRET 格式正确 (长度: {len(app_secret)})")
    else:
        print(f"⚠️  APP_SECRET 长度异常: {len(app_secret)} (应该 > 20)")
else:
    print("❌ APP_SECRET 为空")

# 验证 CHAT_ID
if chat_id:
    if chat_id.startswith('oc_'):
        print(f"✅ CHAT_ID 格式正确: oc_xxxxxxxx (长度: {len(chat_id)})")
    else:
        print(f"⚠️  CHAT_ID 格式异常: 应该以 'oc_' 开头")
        print(f"   当前值: {chat_id[:10]}...")
else:
    print("❌ CHAT_ID 为空")

print("")

# 检查是否有空格或特殊字符
issues = []
if ' ' in app_id:
    issues.append("APP_ID 包含空格")
if ' ' in app_secret:
    issues.append("APP_SECRET 包含空格")
if ' ' in chat_id:
    issues.append("CHAT_ID 包含空格")

if issues:
    print("❌ 发现问题:")
    for issue in issues:
        print(f"   - {issue}")
    sys.exit(1)
else:
    print("✅ 环境变量格式检查通过")
CHECK_EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 环境变量验证失败"
    echo ""
    echo "请检查 .env 文件内容，确保："
    echo "1. APP_ID 以 'cli_' 开头"
    echo "2. APP_SECRET 长度大于 20"
    echo "3. CHAT_ID 以 'oc_' 开头"
    echo "4. 没有多余的空格或引号"
    exit 1
fi

echo ""
echo "步骤 3: 测试飞书 API 连接"
echo "------------------------------------------------------------------------"

python3 << 'TEST_EOF'
import os
import requests
from pathlib import Path

# 加载环境变量
env_file = Path(".env")
env_vars = {}
with open(env_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip().strip('"').strip("'")

app_id = env_vars.get('FEISHU_APP_ID', '')
app_secret = env_vars.get('FEISHU_APP_SECRET', '')

print("测试获取租户令牌...")
print("")

url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
payload = {
    "app_id": app_id,
    "app_secret": app_secret
}

try:
    response = requests.post(url, json=payload, timeout=10)
    data = response.json()

    print(f"HTTP 状态码: {response.status_code}")
    print(f"响应内容: {data}")
    print("")

    if data.get("code") == 0:
        print("✅ 租户令牌获取成功")
        token = data.get("tenant_access_token", "")
        print(f"   令牌: {token[:20]}...")
    else:
        print(f"❌ 租户令牌获取失败")
        print(f"   错误码: {data.get('code')}")
        print(f"   错误信息: {data.get('msg')}")

        # 常见错误提示
        if data.get('msg') == 'invalid param':
            print("")
            print("💡 可能的原因:")
            print("   1. APP_ID 或 APP_SECRET 错误")
            print("   2. APP_ID/APP_SECRET 包含多余的空格或引号")
            print("   3. .env 文件格式不正确")

except Exception as e:
    print(f"❌ 请求失败: {e}")
TEST_EOF

echo ""
echo "步骤 4: 查看最新服务日志"
echo "------------------------------------------------------------------------"

sudo journalctl -u monthly-report-bot -n 50 --no-pager | grep -E "ERROR|token|WebSocket|连接"

echo ""
echo "========================================================================"
echo "诊断完成"
echo "========================================================================"
echo ""
echo "如果发现 APP_ID 或 APP_SECRET 有问题，请编辑 .env 文件："
echo "   nano ~/.env"
echo ""
echo "修改后重启服务："
echo "   sudo systemctl restart monthly-report-bot"
