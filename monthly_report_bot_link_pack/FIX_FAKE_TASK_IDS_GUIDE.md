# 修复"已完成任务数显示为0"问题 - 完整部署指南

## 🎯 问题描述

**症状**：
- 图表和状态显示"已完成: 0"
- 完成率显示 0.0%
- task_stats.json 中使用的是假ID (task_2025-10_1) 而非真实GUID

**根本原因**：
1. 代码使用了错误的API类名 (`CreateTaskRequestBody`, `CreateTaskRequestBodyDue`)
2. task_stats.json 中存储的是模拟ID而非真实飞书任务GUID
3. 参考：[PITFALLS_AND_SOLUTIONS.md](PITFALLS_AND_SOLUTIONS.md) 坑 #1.1 和 坑 #1.3

---

## ✅ 修复内容

### 1. 代码修复 (已完成)
- ✅ 修正API类名：`InputTask`, `Due`, `Member`
- ✅ 在创建时直接分配成员
- ✅ 移除错误的 `Origin` 字段
- ✅ 确保使用真实GUID保存到 task_stats.json

### 2. 数据清理脚本 (已创建)
- ✅ `clear_fake_task_ids.py` - 清理假ID，保留真实GUID

---

## 🚀 部署步骤

### 方法A: 完整部署（推荐 - 重新创建所有任务）

如果你想重新创建所有任务，使用此方法：

#### 步骤1: SSH登录服务器
```bash
ssh hdi918072@34.145.43.77
```

#### 步骤2: 进入项目目录
```bash
cd /home/hdi918072/monthly-report-bot
```

#### 步骤3: 备份当前数据
```bash
# 备份任务统计文件
cp task_stats.json task_stats.json.backup_$(date +%Y%m%d_%H%M%S)

# 备份任务创建记录
cp created_tasks.json created_tasks.json.backup_$(date +%Y%m%d_%H%M%S)
```

#### 步骤4: 拉取最新代码
```bash
# 如果有本地修改，先stash
git stash

# 拉取最新代码
git pull origin main

# 确认代码已更新
git log --oneline -3
# 应该看到最新的提交:
# dd4eda4 docs: 更新错题本，记录坑#1.3 API类名错误问题
# c5701b5 fix: 修复任务创建API类名错误和task_stats.json假ID问题
```

#### 步骤5: 验证修复代码
```bash
# 检查修复是否存在
grep -n "InputTask.builder()" monthly_report_bot_ws_v1.1.py
# 应该能看到第1434行包含 InputTask

grep -n "Due.builder()" monthly_report_bot_ws_v1.1.py
# 应该能看到第1437行包含 Due.builder()

grep -n "Member.builder()" monthly_report_bot_ws_v1.1.py
# 应该能看到第1426行包含 Member.builder()
```

#### 步骤6: 清理旧数据
```bash
# 激活虚拟环境
source venv/bin/activate

# 运行清理脚本
python3 clear_fake_task_ids.py
# 按提示输入 yes 确认清理

# 删除任务创建记录（让系统重新创建）
rm created_tasks.json
```

#### 步骤7: 重启服务
```bash
# 清除Python缓存
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# 重新加载systemd配置
sudo systemctl daemon-reload

# 重启服务
sudo systemctl restart monthly-report-bot

# 检查服务状态
sudo systemctl status monthly-report-bot
```

#### 步骤8: 查看日志确认
```bash
# 查看实时日志
sudo journalctl -u monthly-report-bot -f

# 在另一个终端查看最近的日志
sudo journalctl -u monthly-report-bot -n 100
```

#### 步骤9: 手动触发任务创建（可选）
```bash
# 如果不想等到自动创建时间（每月17-19日 09:30）
# 可以手动触发创建
cd /home/hdi918072/monthly-report-bot

# 方法1: 使用Python交互式调用
python3 << 'EOF'
import asyncio
import sys
sys.path.insert(0, '.')
from monthly_report_bot_ws_v1 import create_tasks

async def main():
    result = await create_tasks()
    print(f"任务创建结果: {result}")

asyncio.run(main())
EOF
```

#### 步骤10: 验证修复
```bash
# 检查 task_stats.json 中的ID格式
cat task_stats.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
tasks = data.get('tasks', {})
fake_ids = sum(1 for k in tasks if k.startswith('task_'))
real_guids = sum(1 for k in tasks if not k.startswith('task_'))
print(f'假ID数量: {fake_ids}')
print(f'真实GUID数量: {real_guids}')
print(f'总任务数: {data.get(\"total_tasks\", 0)}')
print(f'已完成: {data.get(\"completed_tasks\", 0)}')
print(f'完成率: {data.get(\"completion_rate\", 0)}%')
"

# 应该输出：
# 假ID数量: 0
# 真实GUID数量: 24
# 总任务数: 24
# 已完成: 9
# 完成率: 39.13%
```

#### 步骤11: 在飞书中测试
在飞书群聊中发送：
```
@月报收集系统 图表
```

**预期结果**：
- ✅ 图表显示"已完成: 9"（或实际完成数量）
- ✅ 完成率显示 39.13%（或实际比例）
- ✅ 已完成人员排行榜显示正确

---

### 方法B: 保留数据部署（适用于已有真实GUID任务）

如果 task_stats.json 中已经有部分真实GUID任务，想保留它们：

#### 步骤1-4: 与方法A相同

#### 步骤5: 运行清理脚本（保留真实GUID）
```bash
source venv/bin/activate
python3 clear_fake_task_ids.py
# 这会删除假ID，保留真实GUID
```

#### 步骤6: 不删除 created_tasks.json
```bash
# 如果本月已创建过真实任务，保留创建记录
# 不执行 rm created_tasks.json
```

#### 步骤7-11: 与方法A相同

---

## 🧪 验证清单

部署完成后，请逐项检查：

### 服务状态
- [ ] `systemctl status monthly-report-bot` 显示 `active (running)`
- [ ] 日志中没有 `AttributeError` 或 `CreateTaskRequestBody` 错误
- [ ] 日志中包含 "✅ 任务创建成功" 和真实GUID

### 数据文件
- [ ] `task_stats.json` 中的任务ID是GUID格式（包含连字符）
- [ ] 假ID数量为 0
- [ ] 总任务数正确（23或24个）
- [ ] 已完成任务数大于 0

### 飞书功能
- [ ] 发送 `@月报收集系统 状态` 显示正确的已完成数量
- [ ] 发送 `@月报收集系统 图表` 显示正确的统计图表
- [ ] 图表中显示已完成人员排行榜
- [ ] 完成率不是 0.0%

---

## ❌ 常见问题排查

### Q1: git pull 失败，提示文件冲突
**解决**：
```bash
git stash
git pull origin main
git stash pop
# 手动解决冲突后
git add .
git commit -m "merge: resolve conflicts"
```

### Q2: 清理脚本运行后，所有任务都被删除了
**回滚**：
```bash
# 查找备份文件
ls -lt task_stats.json.backup_*

# 恢复最新的备份
cp task_stats.json.backup_YYYYMMDD_HHMMSS task_stats.json

# 重启服务
sudo systemctl restart monthly-report-bot
```

### Q3: 服务启动失败，日志显示 ImportError
**解决**：
```bash
cd /home/hdi918072/monthly-report-bot
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt

# 重启服务
sudo systemctl restart monthly-report-bot
```

### Q4: task_stats.json 仍然是假ID
**原因**：可能是 `created_tasks.json` 中记录本月已创建，导致不再创建新任务

**解决**：
```bash
# 删除创建记录
rm created_tasks.json

# 重启服务
sudo systemctl restart monthly-report-bot

# 手动触发任务创建（参考步骤9）
```

### Q5: 手动触发任务创建时报错
**检查点**：
1. 确认虚拟环境已激活：`which python3` 应该指向 venv
2. 确认 .env 文件存在且包含正确的 APP_ID 和 APP_SECRET
3. 查看详细错误日志：`sudo journalctl -u monthly-report-bot -n 200`

---

## 🔄 回滚方案

如果部署失败，需要回滚：

### 快速回滚
```bash
cd /home/hdi918072/monthly-report-bot

# 1. 回滚代码
git reset --hard HEAD~2  # 回退2个提交
git pull origin main    # 重新拉取旧版本

# 2. 恢复数据文件
cp task_stats.json.backup_* task_stats.json
cp created_tasks.json.backup_* created_tasks.json

# 3. 重启服务
sudo systemctl restart monthly-report-bot

# 4. 验证服务
sudo systemctl status monthly-report-bot
```

---

## 📊 预期结果

### 部署前
```
📊 2025-10 月度任务进度

统计数据:
• 总任务数: 24
• 已完成: 0        ← ❌ 错误
• 待完成: 24
• 完成率: 0.0%     ← ❌ 错误
```

### 部署后
```
📊 2025-10 月度任务进度

统计数据:
• 总任务数: 24
• 已完成: 9        ← ✅ 正确
• 待完成: 15
• 完成率: 37.5%    ← ✅ 正确

👥 已完成人员:
刘野: 5个任务 🥇
范明杰: 1个任务
黄杰: 2个任务
王大伟: 1个任务
```

---

## 📝 相关文档

- [PITFALLS_AND_SOLUTIONS.md](PITFALLS_AND_SOLUTIONS.md) - 错题本（必读！）
  - 坑 #1.1: 使用模拟任务ID而非真实GUID
  - 坑 #1.3: API类名错误导致代码未真正生效
- [SESSION_SUMMARY_2025-10-23.md](../SESSION_SUMMARY_2025-10-23.md) - 正确的API用法
- [clear_fake_task_ids.py](clear_fake_task_ids.py) - 数据清理脚本

---

## 🎯 部署后任务

- [ ] 监控服务日志24小时，确认无异常
- [ ] 验证下一次每日提醒显示正确数据
- [ ] 更新部署记录文档
- [ ] 通知团队成员修复已完成

---

**创建时间**: 2025-10-27
**版本**: v1.0
**适用于**: monthly_report_bot v1.3.1+

**⚠️ 重要提醒**: 部署前请先阅读 [PITFALLS_AND_SOLUTIONS.md](PITFALLS_AND_SOLUTIONS.md)，避免重复犯错！
