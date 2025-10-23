# 服务器端修复指南 - GCP部署

## 📋 问题
- 已完成任务显示为 0
- 实际上很多人已完成任务
- 完成率显示 0.0%

## ✅ 快速修复（3个步骤）

### 步骤1: 上传文件到服务器

在您的本地Windows电脑上，打开PowerShell或命令提示符：

```powershell
# 进入项目目录
cd F:\monthly_report_bot_link_pack\monthly_report_bot_link_pack

# 上传修复文件到服务器
scp monthly_report_bot_ws_v1.1.py hdi918072@34.145.43.77:/home/hdi918072/monthly_report_bot/
scp sync_existing_tasks.py hdi918072@34.145.43.77:/home/hdi918072/monthly_report_bot/
scp fix_on_server.sh hdi918072@34.145.43.77:/home/hdi918072/monthly_report_bot/
```

### 步骤2: SSH登录服务器

```powershell
ssh hdi918072@34.145.43.77
```

### 步骤3: 在服务器上运行修复脚本

```bash
cd /home/hdi918072/monthly_report_bot
chmod +x fix_on_server.sh
./fix_on_server.sh
```

**预期输出**：
```
============================================================
月报机器人 - 任务同步修复（服务器端）
============================================================

步骤 1/4: 备份关键文件...
✅ 已备份主程序 -> monthly_report_bot_ws_v1.1.py.backup_20251023_143000
✅ 已备份任务数据 -> task_stats.json.backup_20251023_143000

步骤 2/4: 检查必要文件...
✅ 所有必要文件都存在

步骤 3/4: 同步任务GUID...
✅ 虚拟环境已激活

正在运行同步脚本...
----------------------------------------
============================================================
飞书任务同步工具
============================================================
📅 当前月份: 2025-10
📊 本地任务数: 23

📋 正在获取飞书任务列表...
✅ 成功获取 23 个任务

🔍 分析飞书任务...
  ✅ 月报-工程计划及执行情况...
  ✅ 月报-设计工作进展...
  ⏳ 月报-现场施工照片...
  ...

✅ 找到 23 个月报任务

🔄 更新 task_stats.json...
  ✅ 月报-工程计划及执行情况 (已完成)
  ✅ 月报-设计工作进展 (已完成)
  ...

✅ task_stats.json 已更新

============================================================
✅ 同步完成！
============================================================
📊 统计信息:
  • 总任务数: 23
  • 已完成: 9
  • 待完成: 14
  • 完成率: 39.13%
  • 更新任务: 23

🎉 现在任务状态已与飞书同步！
----------------------------------------
✅ 任务同步成功

步骤 4/4: 重启月报机器人服务...
✅ 服务重启命令已执行
✅ 服务运行正常

============================================================
✅ 修复完成！
============================================================
```

---

## 🧪 验证修复

在飞书群聊中发送：`状态`

**期望结果**：
```
📊 当前进度（2025-10）
- 总任务数: 23
- 已完成: 9        ← ✅ 不再是0！
- 待完成: 14
- 完成率: 39.13%   ← ✅ 正确！

👥 已完成人员:
刘野: 5个任务 🥇
范明杰: 1个任务
黄杰: 2个任务
王大伟: 1个任务
```

---

## 📝 详细步骤说明

### 为什么要上传这些文件？

1. **monthly_report_bot_ws_v1.1.py** - 修复后的主程序
   - 修复了 `create_tasks()` 函数
   - 使用真实飞书API创建任务
   - 保存真实的task_guid

2. **sync_existing_tasks.py** - 同步工具
   - 从飞书获取所有任务
   - 匹配本地任务
   - 更新为真实GUID
   - 同步完成状态

3. **fix_on_server.sh** - 自动化修复脚本
   - 自动备份
   - 运行同步
   - 重启服务
   - 验证结果

---

## 🔍 如果遇到问题

### 问题1: SCP上传失败

**错误**：
```
Permission denied (publickey)
```

**解决**：
```powershell
# 方案1: 使用密码登录（如果服务器允许）
scp -o PreferredAuthentications=password monthly_report_bot_ws_v1.1.py hdi918072@34.145.43.77:/home/hdi918072/monthly_report_bot/

# 方案2: 先SSH登录，然后在服务器上用其他方式获取文件
# 例如：从GitHub下载，或使用其他传输方式
```

### 问题2: 同步脚本找不到任务

**错误**：
```
未找到任何飞书任务
```

**原因**：
- 飞书应用权限不足
- .env 文件中的凭证不正确

**解决**：
```bash
# 检查 .env 文件
cat .env | grep FEISHU

# 确认应用权限
# 需要权限：task:task:readonly, task:task
```

### 问题3: 服务重启失败

**错误**：
```
❌ 服务启动失败
```

**解决**：
```bash
# 查看详细错误
sudo journalctl -u monthly-report-bot -n 50

# 检查语法错误
python3 -m py_compile monthly_report_bot_ws_v1.1.py

# 手动启动测试
cd /home/hdi918072/monthly_report_bot
source venv/bin/activate
python3 monthly_report_bot_ws_v1.1.py
```

---

## 🔄 回滚方案

如果修复后出现问题，可以回滚：

```bash
# SSH登录服务器
ssh hdi918072@34.145.43.77

# 进入项目目录
cd /home/hdi918072/monthly_report_bot

# 查看备份文件
ls -la *.backup_*

# 回滚（替换时间戳为实际备份文件的时间戳）
cp monthly_report_bot_ws_v1.1.py.backup_20251023_143000 monthly_report_bot_ws_v1.1.py
cp task_stats.json.backup_20251023_143000 task_stats.json

# 重启服务
sudo systemctl restart monthly-report-bot
```

---

## 📊 修复原理

### 问题根源

**旧代码**（模拟创建）：
```python
task_id = f"task_2025-10_1"  # ❌ 假ID
update_task_completion(task_id, ...)
```

**同步失败**：
```python
# 用假ID查询飞书API
is_completed = await check_task_status_from_feishu("task_2025-10_1")
# 飞书返回：任务不存在
# 结果：completed 永远是 False
```

### 修复方案

**新代码**（真实创建）：
```python
response = await lark_client.task.v2.task.acreate(request)
task_guid = response.data.task.guid  # ✅ 真实GUID
update_task_completion(task_guid, ...)
```

**同步工具**（修复已存在任务）：
```python
# 1. 从飞书获取所有任务
feishu_tasks = await list_all_tasks(client)

# 2. 匹配标题，获取真实GUID
for task in feishu_tasks:
    if task.summary == "2025-10 月报-工程计划及执行情况":
        real_guid = task.guid  # ✅ 真实GUID
        is_completed = task.complete == 2  # ✅ 真实状态

# 3. 更新本地数据
new_tasks[real_guid] = old_task_info
new_tasks[real_guid]["completed"] = is_completed
```

---

## ✅ 修复检查清单

执行完修复后，请确认：

- [ ] fix_on_server.sh 脚本成功运行
- [ ] 同步脚本显示找到 23 个任务
- [ ] 同步脚本显示正确的已完成数量（例如 9 个）
- [ ] 服务成功重启
- [ ] 发送`状态`显示正确的已完成数（不再是0）
- [ ] 发送`图表`能看到准确统计
- [ ] 已完成人员排行榜显示正确

**全部打✅** → 修复成功！🎉

---

## 📞 需要帮助

### 查看服务日志

```bash
# 实时查看
sudo journalctl -u monthly-report-bot -f

# 最新50行
sudo journalctl -u monthly-report-bot -n 50

# 查看错误
sudo journalctl -u monthly-report-bot -p err -n 20
```

### 手动测试同步

```bash
cd /home/hdi918072/monthly_report_bot
source venv/bin/activate
python3 sync_existing_tasks.py
```

### 检查服务状态

```bash
sudo systemctl status monthly-report-bot
```

---

## 🎯 总结

### 您需要做的（3步）

1. **本地上传文件**：
   ```powershell
   scp monthly_report_bot_ws_v1.1.py hdi918072@34.145.43.77:/home/hdi918072/monthly_report_bot/
   scp sync_existing_tasks.py hdi918072@34.145.43.77:/home/hdi918072/monthly_report_bot/
   scp fix_on_server.sh hdi918072@34.145.43.77:/home/hdi918072/monthly_report_bot/
   ```

2. **SSH登录服务器**：
   ```powershell
   ssh hdi918072@34.145.43.77
   ```

3. **运行修复脚本**：
   ```bash
   cd /home/hdi918072/monthly_report_bot
   chmod +x fix_on_server.sh
   ./fix_on_server.sh
   ```

### 预计耗时
- 上传文件: 30秒
- 运行修复: 1-2分钟
- **总计**: 约3分钟

### 修复效果
- ✅ 任务完成状态正确同步
- ✅ 完成率准确显示（39.13%而非0%）
- ✅ 每日提醒只@未完成人员
- ✅ 图表统计准确

---

**修复完成后，请在飞书群聊发送 `状态` 验证效果！**
