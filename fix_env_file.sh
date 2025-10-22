#!/bin/bash

# ============================================================================
# 修复 .env 文件配置
# ============================================================================

echo "========================================================================"
echo "检查和修复 .env 文件配置"
echo "========================================================================"
echo ""

cd ~/monthly-report-bot/monthly_report_bot_link_pack

echo "步骤 1: 查找所有 .env 文件"
echo "------------------------------------------------------------------------"

# 查找所有可能的 .env 文件位置
echo "搜索 .env 文件..."
echo ""

find ~/monthly-report-bot -name ".env" -type f 2>/dev/null | while read envfile; do
    echo "找到: $envfile"
    echo "内容预览（前 10 行）:"
    head -10 "$envfile" | sed 's/SECRET=.*/SECRET=***hidden***/g'
    echo ""
done

echo ""
echo "步骤 2: 检查当前目录的 .env 文件"
echo "------------------------------------------------------------------------"

if [ -f .env ]; then
    echo "✅ 当前目录存在 .env 文件"
    echo ""
    echo "文件内容（已脱敏）:"
    echo "----------------------------------------"
    cat .env | sed 's/\(SECRET=\).*/\1***hidden***/g' | sed 's/\(APP_ID=cli_\).*/\1***hidden***/g'
    echo "----------------------------------------"
    echo ""

    # 检查是否包含必需的字段
    echo "检查必需字段:"

    if grep -q "FEISHU_APP_ID" .env; then
        APP_ID=$(grep "FEISHU_APP_ID" .env | cut -d'=' -f2 | tr -d ' ' | tr -d '"' | tr -d "'")
        if [ -n "$APP_ID" ]; then
            echo "✅ FEISHU_APP_ID: 已设置"
        else
            echo "❌ FEISHU_APP_ID: 字段存在但值为空"
        fi
    else
        echo "❌ FEISHU_APP_ID: 缺失"
    fi

    if grep -q "FEISHU_APP_SECRET" .env; then
        APP_SECRET=$(grep "FEISHU_APP_SECRET" .env | cut -d'=' -f2 | tr -d ' ' | tr -d '"' | tr -d "'")
        if [ -n "$APP_SECRET" ]; then
            echo "✅ FEISHU_APP_SECRET: 已设置"
        else
            echo "❌ FEISHU_APP_SECRET: 字段存在但值为空"
        fi
    else
        echo "❌ FEISHU_APP_SECRET: 缺失"
    fi

    if grep -q "CHAT_ID" .env; then
        CHAT_ID=$(grep "CHAT_ID" .env | cut -d'=' -f2 | tr -d ' ' | tr -d '"' | tr -d "'")
        if [ -n "$CHAT_ID" ]; then
            echo "✅ CHAT_ID: 已设置"
        else
            echo "❌ CHAT_ID: 字段存在但值为空"
        fi
    else
        echo "❌ CHAT_ID: 缺失"
    fi
else
    echo "❌ 当前目录不存在 .env 文件"
fi

echo ""
echo "步骤 3: 检查旧版本的配置"
echo "------------------------------------------------------------------------"

# 检查是否有旧版本的环境变量文件
if [ -f ~/monthly-report-bot/monthly_report_bot_link_pack/.env.example ]; then
    echo "找到 .env.example 模板文件"
fi

if [ -f ~/monthly-report-bot/monthly_report_bot_link_pack/.env.bak ]; then
    echo "找到 .env.bak 备份文件"
fi

# 检查旧版本机器人是否有配置
if [ -f ~/monthly-report-bot/monthly_report_bot_link_pack/.env ]; then
    echo ""
    echo "检查 .env 文件中的变量名..."
    echo ""

    # 列出所有环境变量名
    grep "=" .env | grep -v "^#" | cut -d'=' -f1 | while read varname; do
        echo "  - $varname"
    done
fi

echo ""
echo "========================================================================"
echo "诊断结果"
echo "========================================================================"
echo ""

if [ -f .env ]; then
    HAS_APP_ID=$(grep -c "FEISHU_APP_ID=" .env)
    HAS_APP_SECRET=$(grep -c "FEISHU_APP_SECRET=" .env)

    if [ "$HAS_APP_ID" -eq 0 ] || [ "$HAS_APP_SECRET" -eq 0 ]; then
        echo "❌ .env 文件缺少必需的配置项"
        echo ""
        echo "需要添加以下内容："
        echo ""
        echo "FEISHU_APP_ID=cli_xxxxxxxxxxxxx"
        echo "FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxx"
        echo ""
        echo "编辑 .env 文件："
        echo "  nano ~/monthly-report-bot/monthly_report_bot_link_pack/.env"
        echo ""
        echo "或者从飞书开放平台获取正确的 APP_ID 和 APP_SECRET"
        echo "  https://open.feishu.cn/app"
    else
        echo "✅ .env 文件包含所有必需字段"
        echo ""
        echo "但值可能为空或格式不正确，请检查："
        echo "  nano ~/monthly-report-bot/monthly_report_bot_link_pack/.env"
    fi
else
    echo "❌ .env 文件不存在"
    echo ""
    echo "创建 .env 文件："
    echo "  nano ~/monthly-report-bot/monthly_report_bot_link_pack/.env"
    echo ""
    echo "添加以下内容："
    echo ""
    echo "FEISHU_APP_ID=cli_xxxxxxxxxxxxx"
    echo "FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxx"
    echo "CHAT_ID=oc_xxxxxxxxxxxxx"
    echo "FILE_URL=https://your-file-url"
fi

echo ""
echo "========================================================================"
