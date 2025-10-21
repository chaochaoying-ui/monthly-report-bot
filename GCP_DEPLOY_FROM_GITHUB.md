# 🚀 从 GitHub 部署修复到 GCP - 简单3步

## ✅ 前置条件

- ✅ 修复已推送到 GitHub: https://github.com/chaochaoying-ui/monthly-report-bot
- ✅ 提交 ID: `b9fc048`
- ✅ GCP 服务器: `monthly-report-bot` (hdi918072@monthly-report-bot)

---

## 🎯 快速部署（3 步完成）

### 步骤 1️⃣: 连接到 GCP 服务器

在 GCP 控制台找到 VM 实例 `monthly-report-bot`，点击 **SSH** 按钮打开终端。

---

### 步骤 2️⃣: 拉取最新代码并部署

**复制以下命令，粘贴到 GCP SSH 终端，按回车执行**：

```bash
# ============================================================================
# 从 GitHub 拉取并部署修复
# ============================================================================

echo "========================================================================"
echo "从 GitHub 部署每日提醒 @ 格式修复"
echo "========================================================================"

# 1. 进入项目目录
cd ~/monthly-report-bot
echo "✅ 当前目录: $(pwd)"

# 2. 备份当前文件
echo ""
echo "创建备份..."
BACKUP_DIR="$HOME/monthly-report-bot-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"
cp -r monthly_report_bot_link_pack "$BACKUP_DIR/monthly_report_bot_link_pack.$TIMESTAMP"
echo "✅ 备份已创建: $BACKUP_DIR/monthly_report_bot_link_pack.$TIMESTAMP"

# 3. 拉取最新代码
echo ""
echo "从 GitHub 拉取最新代码..."
git fetch origin
git pull origin main

if [ $? -eq 0 ]; then
    echo "✅ 代码更新成功"
    echo "最新提交: $(git log -1 --oneline)"
else
    echo "❌ 代码更新失败"
    exit 1
fi

# 4. 验证修复
echo ""
echo "========================================================================"
echo "验证修复"
echo "========================================================================"

cd monthly_report_bot_link_pack

AT_COUNT=$(grep -c "display_name = get_user_display_name" monthly_report_bot_final_interactive.py)
echo "找到 $AT_COUNT 处 @ 格式修复（预期: 至少 3 处）"

if [ "$AT_COUNT" -ge 3 ]; then
    echo "✅ @ 格式修复验证通过"
else
    echo "⚠️  @ 格式修复未找到，可能拉取失败"
    exit 1
fi

if grep -q "if not init_lark_client():" monthly_report_bot_final_interactive.py; then
    echo "✅ 客户端初始化验证通过"
else
    echo "⚠️  客户端初始化未找到"
fi

# 5. 检查语法
echo ""
echo "检查 Python 语法..."
if python3 -m py_compile monthly_report_bot_final_interactive.py 2>/dev/null; then
    echo "✅ Python 语法检查通过"
else
    echo "❌ Python 语法错误！"
    exit 1
fi

# 6. 重启服务
echo ""
echo "========================================================================"
echo "重启服务"
echo "========================================================================"

sudo systemctl restart monthly-report-bot
sleep 3

if sudo systemctl is-active --quiet monthly-report-bot; then
    echo "✅ 服务已成功重启并运行中"

    # 显示服务状态
    echo ""
    echo "服务状态:"
    sudo systemctl status monthly-report-bot --no-pager | head -10
else
    echo "❌ 服务重启失败"
    echo ""
    echo "查看错误日志:"
    sudo journalctl -u monthly-report-bot -n 30 --no-pager
    exit 1
fi

# 7. 测试每日提醒
echo ""
echo "========================================================================"
echo "测试每日提醒功能"
echo "========================================================================"

source venv/bin/activate

python3 << 'TEST_EOF'
import asyncio
from monthly_report_bot_final_interactive import test_daily_reminder

async def main():
    print("📤 发送测试每日提醒到飞书群...")
    print("")
    success = await test_daily_reminder()
    print("")
    if success:
        print("✅✅✅ 每日提醒测试成功！✅✅✅")
        print("")
        print("请检查飞书群消息:")
        print("  1. 负责人 @ 是否正确显示（如: @周超, @张三）")
        print("  2. 点击 @ 是否可以跳转")
        print("  3. 负责人是否收到通知")
    else:
        print("⚠️  测试未完全成功，请查看上面的日志")

asyncio.run(main())
TEST_EOF

# 完成
echo ""
echo "========================================================================"
echo "✅ 部署完成！"
echo "========================================================================"
echo ""
echo "Git 信息:"
git log -1 --pretty=format:"  提交: %h%n  作者: %an%n  日期: %ad%n  说明: %s%n" --date=format:"%Y-%m-%d %H:%M:%S"
echo ""
echo "备份位置:"
echo "  $BACKUP_DIR/monthly_report_bot_link_pack.$TIMESTAMP"
echo ""
echo "如需回滚:"
echo "  cd ~/monthly-report-bot"
echo "  rm -rf monthly_report_bot_link_pack"
echo "  cp -r $BACKUP_DIR/monthly_report_bot_link_pack.$TIMESTAMP monthly_report_bot_link_pack"
echo "  sudo systemctl restart monthly-report-bot"
echo ""
echo "========================================================================"
```

---

### 步骤 3️⃣: 验证部署结果

#### 1. 查看脚本输出

确认看到：
```
✅✅✅ 每日提醒测试成功！✅✅✅
```

#### 2. 检查飞书群消息

打开飞书群，应该收到一条**每日任务提醒**消息，检查：

- ✅ 负责人姓名正确显示（如: `@周超`, `@张三`）
- ✅ 点击 @ 可以跳转到用户
- ✅ 负责人收到飞书通知

#### 3. 对比修复效果

**修复前**:
```
👥 未完成任务的负责人:
@  @  @           ← 显示为空
```

**修复后**:
```
👥 未完成任务的负责人:
@周超 @张三 @李四   ← 正确显示姓名
```

---

## 🔍 故障排查

### 问题 1: git pull 失败

```bash
cd ~/monthly-report-bot
git status

# 如果有本地修改冲突
git stash
git pull origin main
git stash pop
```

### 问题 2: 服务重启失败

```bash
# 查看详细日志
sudo journalctl -u monthly-report-bot -n 50 --no-pager

# 手动测试运行
cd ~/monthly-report-bot/monthly_report_bot_link_pack
source venv/bin/activate
python3 monthly_report_bot_final_interactive.py
```

### 问题 3: @ 仍然显示为空

```bash
# 检查修复是否应用
cd ~/monthly-report-bot/monthly_report_bot_link_pack
grep -n "display_name = get_user_display_name" monthly_report_bot_final_interactive.py

# 应该看到至少 3 行输出
```

### 问题 4: 测试提醒发送失败

```bash
# 检查环境变量
cd ~/monthly-report-bot/monthly_report_bot_link_pack
cat .env | grep -E "FEISHU_APP_ID|FEISHU_APP_SECRET|CHAT_ID"
```

---

## 🔄 回滚步骤

如果部署后出现问题：

```bash
# 查看可用备份
ls -lht ~/monthly-report-bot-backups/

# 回滚到备份（替换时间戳）
cd ~/monthly-report-bot
rm -rf monthly_report_bot_link_pack
cp -r ~/monthly-report-bot-backups/monthly_report_bot_link_pack.YYYYMMDD_HHMMSS \
      monthly_report_bot_link_pack

# 重启服务
sudo systemctl restart monthly-report-bot

# 检查状态
sudo systemctl status monthly-report-bot
```

或者，使用 Git 回滚：

```bash
cd ~/monthly-report-bot
git log --oneline -5  # 查看最近的提交

# 回滚到上一个提交
git reset --hard HEAD~1

# 重启服务
cd monthly_report_bot_link_pack
sudo systemctl restart monthly-report-bot
```

---

## 📊 部署后监控

### 查看实时日志

```bash
# 服务日志
sudo journalctl -u monthly-report-bot -f

# 或查看文件日志
sudo tail -f /var/log/monthly-report-bot.log
```

### 检查服务状态

```bash
sudo systemctl status monthly-report-bot
```

### 手动触发测试

```bash
cd ~/monthly-report-bot/monthly_report_bot_link_pack
source venv/bin/activate
python3 -c "import asyncio; from monthly_report_bot_final_interactive import test_daily_reminder; asyncio.run(test_daily_reminder())"
```

---

## 🎉 部署成功标志

- ✅ Git 拉取成功，显示最新提交
- ✅ 验证找到 3 处 @ 格式修复
- ✅ 服务重启成功并运行中
- ✅ 测试提醒发送成功
- ✅ 飞书群收到消息，@ 显示正确

---

## 📚 相关文档

- [README_FIX.md](README_FIX.md) - 修复总览
- [DEPLOY_FIX_GUIDE.md](DEPLOY_FIX_GUIDE.md) - 详细部署指南
- [FIX_AT_FORMAT_SUMMARY.md](FIX_AT_FORMAT_SUMMARY.md) - 技术细节
- GitHub 仓库: https://github.com/chaochaoying-ui/monthly-report-bot

---

## 📞 获取支持

修复日期: 2025-10-21
提交 ID: b9fc048
修复人员: Claude Code Assistant

---

**现在就开始部署吧！只需 3 步，5 分钟完成！** 🚀
