# 🚀 GCP 服务器部署修复指令

## 📋 快速部署（推荐）

### 方法 1: 使用一键部署脚本

#### 步骤 1: 将脚本上传到 GCP 服务器

**在本地 Windows PowerShell 中执行**:

```powershell
# 使用 gcloud CLI 上传（如果已安装）
gcloud compute scp "f:\monthly_report_bot_link_pack\deploy_fix_to_gcp.sh" `
    hdi918072@monthly-report-bot:~/deploy_fix_to_gcp.sh `
    --zone=us-west1-b

# 或使用 SCP（如果配置了 SSH 密钥）
scp "f:\monthly_report_bot_link_pack\deploy_fix_to_gcp.sh" `
    hdi918072@monthly-report-bot:~/deploy_fix_to_gcp.sh
```

#### 步骤 2: 在 GCP 服务器上执行脚本

**在 GCP Web SSH 终端中执行**:

```bash
# 添加执行权限
chmod +x ~/deploy_fix_to_gcp.sh

# 执行部署脚本
~/deploy_fix_to_gcp.sh
```

**等待脚本完成**，预期输出：

```
========================================================================
GCP 服务器 - 每日提醒 @ 格式修复部署
========================================================================

[1/8] 检查环境...
✅ 项目目录: /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack
✅ 主文件存在

[2/8] 创建备份...
✅ 备份已创建: /home/hdi918072/monthly-report-bot/backups/...

[3/8] 应用 @ 格式修复...
✅ @ 格式修复已应用
✅ @ 格式修复完成

[4/8] 添加测试函数客户端初始化...
✅ 客户端初始化代码已添加
✅ 客户端初始化完成

[5/8] 验证修复...
✅ 找到 3 处 @ 格式修复
✅ 客户端初始化代码已添加
✅ Python 语法检查通过

[6/8] 重启 monthly-report-bot 服务...
✅ 服务已重启

[7/8] 检查服务状态...
✅ 服务运行正常

[8/8] 测试每日提醒功能...
正在发送测试提醒到飞书群...
✅ 每日提醒测试成功！

========================================================================
✅ 修复部署完成！
========================================================================
```

---

## 📝 方法 2: 手动部署（备用）

如果一键脚本失败，可以手动执行以下步骤：

### 步骤 1: SSH 连接到 GCP 服务器

在 GCP 控制台点击 VM 实例的 "SSH" 按钮，或使用命令：

```bash
gcloud compute ssh hdi918072@monthly-report-bot --zone=us-west1-b
```

### 步骤 2: 进入项目目录

```bash
cd ~/monthly-report-bot/monthly_report_bot_link_pack
```

### 步骤 3: 备份当前文件

```bash
# 创建备份目录
mkdir -p ~/monthly-report-bot/backups

# 备份主文件
cp monthly_report_bot_final_interactive.py \
   ~/monthly-report-bot/backups/monthly_report_bot_final_interactive.py.$(date +%Y%m%d_%H%M%S).backup
```

### 步骤 4: 创建修复脚本

```bash
cat > /tmp/apply_fix.py << 'PYTHON_EOF'
#!/usr/bin/env python3
import re

file_path = "monthly_report_bot_final_interactive.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修复 1: 负责人汇总 @ 格式
content = re.sub(
    r'(# 创建@负责人的文本\s+assignee_mentions = \[\]\s+for assignee in incomplete_assignees:\s+)assignee_mentions\.append\(f"<at id=\\"\\{assignee\\}\\"></at>"\)',
    r'\1display_name = get_user_display_name(assignee)\n            assignee_mentions.append(f"<at user_id=\\"{assignee}\\">{display_name}</at>")',
    content
)

# 修复 2: 任务详情 @ 格式
content = re.sub(
    r'(for assignee in task\.get\(\'assignees\', \[\]\):\s+)task_assignees\.append\(f"<at id=\\"\\{assignee\\}\\"></at>"\)',
    r'\1display_name = get_user_display_name(assignee)\n                task_assignees.append(f"<at user_id=\\"{assignee}\\">{display_name}</at>")',
    content
)

# 修复 3: 任务列表 @ 格式
content = re.sub(
    r'(for assignee in task\["assignees"\]:\s+)assignee_mentions \+= f"<at user_id=\\"\\{assignee\\}\\"></at> "',
    r'\1display_name = get_user_display_name(assignee)\n                assignee_mentions += f"<at user_id=\\"{assignee}\\">{display_name}</at> "',
    content
)

# 修复 4: 添加客户端初始化
if 'if not init_lark_client():' not in content:
    content = re.sub(
        r'(async def test_daily_reminder\(\):.*?logger\.info\("开始测试每日提醒功能\.\.\."\)\s+)(success = await send_daily_reminder\(\))',
        r'\1\n        # 初始化飞书客户端\n        if not init_lark_client():\n            logger.error("❌ 飞书客户端初始化失败")\n            return False\n\n        \2',
        content,
        flags=re.DOTALL
    )

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 所有修复已应用")
PYTHON_EOF

# 执行修复
python3 /tmp/apply_fix.py
```

### 步骤 5: 验证修复

```bash
# 检查 @ 格式修复
grep -n "display_name = get_user_display_name" monthly_report_bot_final_interactive.py

# 检查客户端初始化
grep -A5 "async def test_daily_reminder" monthly_report_bot_final_interactive.py
```

**预期输出**:
```
401:            display_name = get_user_display_name(assignee)
461:                display_name = get_user_display_name(assignee)
802:                display_name = get_user_display_name(assignee)
```

### 步骤 6: 重启服务

```bash
sudo systemctl restart monthly-report-bot
```

### 步骤 7: 检查服务状态

```bash
sudo systemctl status monthly-report-bot
```

### 步骤 8: 测试每日提醒

```bash
cd ~/monthly-report-bot/monthly_report_bot_link_pack
source venv/bin/activate
python3 -c "import asyncio; from monthly_report_bot_final_interactive import test_daily_reminder; asyncio.run(test_daily_reminder())"
```

---

## ✅ 验证清单

部署完成后，请检查以下项目：

### 1. 服务器端验证

- [ ] 服务运行正常: `sudo systemctl status monthly-report-bot`
- [ ] 没有错误日志: `sudo journalctl -u monthly-report-bot -n 50`
- [ ] 测试命令成功: 显示 "✅ 每日提醒测试成功"

### 2. 飞书群验证

- [ ] 收到每日提醒卡片消息
- [ ] 负责人姓名正确显示（如: `@周超`, `@张三`）
- [ ] 点击 @ 可以跳转到对应用户
- [ ] 负责人收到飞书通知

### 3. 功能验证

打开飞书群，检查每日提醒消息格式：

**预期效果**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
每日任务提醒
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 每日任务提醒 - 2025-10-21
────────────────────────────────
📊 月度报告任务进度提醒

📈 当前进度:
• 总任务数: 6
• 已完成: 1
• 待完成: 5
• 完成率: 16.7%

────────────────────────────────
👥 未完成任务的负责人:
@周超 @张三 @李四   ← 应该显示真实姓名

📋 未完成任务详情:

1. **完成月度数据分析报告**
   👤 负责人: @周超   ← 应该显示真实姓名

...

⏰ 提醒: @周超 @张三 @李四 请尽快完成任务！
```

---

## 🔍 故障排查

### 问题 1: 脚本执行失败

**症状**: 脚本报错或中途退出

**解决方案**:

```bash
# 查看详细错误
bash -x ~/deploy_fix_to_gcp.sh

# 手动执行步骤（见方法 2）
```

### 问题 2: 服务无法启动

**症状**: `sudo systemctl status monthly-report-bot` 显示 failed

**解决方案**:

```bash
# 查看详细错误
sudo journalctl -u monthly-report-bot -n 100 --no-pager

# 检查语法错误
cd ~/monthly-report-bot/monthly_report_bot_link_pack
source venv/bin/activate
python3 -m py_compile monthly_report_bot_final_interactive.py

# 手动测试运行
python3 monthly_report_bot_final_interactive.py
```

### 问题 3: @ 仍然显示为空

**症状**: 飞书群中负责人 @ 仍然是空白

**可能原因**:

1. **修复未正确应用**

   ```bash
   # 检查修复是否应用
   grep -c "display_name = get_user_display_name" monthly_report_bot_final_interactive.py
   # 应该输出: 3
   ```

2. **用户 ID 未在映射表中**

   ```bash
   # 检查 USER_ID_MAPPING
   grep -A10 "USER_ID_MAPPING" monthly_report_bot_final_interactive.py
   ```

   添加缺失的用户 ID:
   ```python
   USER_ID_MAPPING = {
       "ou_c245b0a7dff11b36369edb96471ed182": "周超",
       "ou_新用户ID": "新用户姓名",  # 添加这一行
   }
   ```

3. **服务未重启**

   ```bash
   sudo systemctl restart monthly-report-bot
   ```

### 问题 4: 测试提醒发送失败

**症状**: 运行测试命令时报错

**解决方案**:

```bash
# 检查环境变量
cd ~/monthly-report-bot/monthly_report_bot_link_pack
cat .env

# 确保包含:
# FEISHU_APP_ID=...
# FEISHU_APP_SECRET=...
# CHAT_ID=...

# 测试飞书连接
source venv/bin/activate
python3 << 'EOF'
import os
print("APP_ID:", os.getenv("FEISHU_APP_ID"))
print("APP_SECRET:", os.getenv("FEISHU_APP_SECRET")[:10] + "...")
print("CHAT_ID:", os.getenv("CHAT_ID"))
EOF
```

---

## 🔄 回滚步骤

如果修复后出现问题，可以快速回滚：

```bash
# 查看可用的备份
ls -lht ~/monthly-report-bot/backups/

# 恢复备份（替换时间戳）
cp ~/monthly-report-bot/backups/monthly_report_bot_final_interactive.py.YYYYMMDD_HHMMSS.backup \
   ~/monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot_final_interactive.py

# 重启服务
sudo systemctl restart monthly-report-bot

# 检查状态
sudo systemctl status monthly-report-bot
```

---

## 📊 部署后监控

### 实时日志监控

```bash
# 实时查看服务日志
sudo journalctl -u monthly-report-bot -f

# 查看最近 50 条日志
sudo journalctl -u monthly-report-bot -n 50 --no-pager

# 查看错误日志
sudo tail -f /var/log/monthly-report-bot-error.log
```

### 性能监控

```bash
# 检查进程状态
ps aux | grep monthly_report_bot

# 检查内存使用
free -h

# 检查磁盘使用
df -h
```

---

## 📞 获取支持

如果遇到无法解决的问题：

1. **收集信息**:
   ```bash
   # 收集诊断信息
   echo "=== 服务状态 ===" > ~/debug.log
   sudo systemctl status monthly-report-bot >> ~/debug.log
   echo "=== 最近日志 ===" >> ~/debug.log
   sudo journalctl -u monthly-report-bot -n 50 >> ~/debug.log
   echo "=== 错误日志 ===" >> ~/debug.log
   tail -50 /var/log/monthly-report-bot-error.log >> ~/debug.log

   # 查看诊断信息
   cat ~/debug.log
   ```

2. **检查文档**:
   - [README_FIX.md](README_FIX.md)
   - [DEPLOY_FIX_GUIDE.md](DEPLOY_FIX_GUIDE.md)
   - [FIX_AT_FORMAT_SUMMARY.md](FIX_AT_FORMAT_SUMMARY.md)

---

## 🎉 部署成功！

修复部署完成后：

1. ✅ 每日提醒中的 @ 功能正常
2. ✅ 负责人姓名正确显示
3. ✅ 可以正确通知到对应用户
4. ✅ 服务稳定运行

享受自动化的月报管理吧！🚀
