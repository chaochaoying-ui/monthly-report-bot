# 🚀 生产环境部署前检查清单

**版本**: v1.3.1
**检查日期**: 2025-11-11
**检查人**: [待填写]
**目标环境**: 正式群

---

## 📋 快速总览

| 类别 | 状态 | 完成度 | 备注 |
|------|------|--------|------|
| **核心功能** | ⚠️ 部分完成 | 85% | 基本可用，部分功能缺失 |
| **定时任务** | ⚠️ 时间不符 | 70% | 功能正常，时间需调整 |
| **交互功能** | ⚠️ 简化版 | 60% | 命令可用，缺少按钮交互 |
| **数据持久化** | ✅ 完成 | 100% | 运行稳定 |
| **稳定性** | ✅ 优秀 | 95% | WS 连接稳定 |
| **图表显示** | 🔄 调试中 | 90% | 中文正常，emoji 待验证 |

---

## ✅ 必须检查项（Critical）

### 1. 核心功能测试

#### 1.1 任务创建
- [ ] 从 tasks.yaml 读取任务模板
- [ ] 正确创建飞书任务
- [ ] 任务包含标题、描述、负责人、截止时间
- [ ] 幂等性验证（不重复创建）
- [ ] 检查 created_tasks.json 记录

**测试命令**:
```bash
# 在测试群中手动触发（修改代码临时触发）
# 或等到定时时间
```

**验证方法**:
1. 检查飞书任务列表是否有新任务
2. 检查 created_tasks.json 是否有当月记录
3. 重启服务，确认不会重复创建

---

#### 1.2 任务完成标记
- [ ] 用户在飞书完成任务后，机器人能感知
- [ ] task_stats.json 正确更新完成状态
- [ ] 完成时间戳正确记录

**测试方法**:
1. 在飞书中标记一个任务为"已完成"
2. 发送 `/stats` 命令查看统计
3. 检查 task_stats.json 中对应任务的 `completed: true`

---

#### 1.3 任务统计查询
- [ ] `/stats` 命令返回正确统计
- [ ] `/my` 命令显示当前用户的任务
- [ ] `/pending` 命令显示未完成任务
- [ ] @ 功能正确（格式：`<at user_id="xxx"></at>`）

**测试命令**:
```
/stats
/my
/pending
帮助
```

---

#### 1.4 图表生成
- [ ] `/chart` 或 "进度图表" 触发图表生成
- [ ] 中文正常显示
- [ ] **Emoji 正常显示（🏆🥇🥈📊📈）** ← **关键测试**
- [ ] 图表上传到飞书成功
- [ ] 图片清晰可读

**测试步骤**:
1. 确保有任务数据（已同步 task_stats.json）
2. 在飞书发送：`进度图表`
3. 检查返回的图表图片：
   - 中文标题、标签清晰
   - **Emoji 不是方框，而是正常的表情符号**
   - 统计数据正确

**预期输出（日志）**:
```
DEBUG: ✅ Symbola 已存在于 fontManager，跳过添加
DEBUG: fontManager 中的 Symbola 字体数量: 1
DEBUG: ✅ findfont(Symbola) 返回: /usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf
美化版综合仪表板已生成: charts/dashboard_XXXXXX.png
```

**如果 Emoji 仍显示为方框**:
→ 查看 [NEXT_STEPS_2025-11-11.md](NEXT_STEPS_2025-11-11.md) 中的"备选方案 A"

---

### 2. 定时任务

#### 2.1 任务创建时间
**当前配置**: 每月 19 日 21:10
**需求要求**: 每月 17-19 日 09:30

- [ ] 确认是否需要调整为需求时间
- [ ] 如需调整，修改 `should_create_tasks()` 函数
- [ ] 测试调整后的逻辑

**代码位置**: `monthly_report_bot_ws_v1.1.py` 或相应的主文件

---

#### 2.2 每日提醒时间
**当前配置**: 每天 09:00
**需求要求**: 18-22 日 09:31

- [ ] 确认是否需要调整为需求时间
- [ ] 如需调整，修改 `should_send_daily_reminder()` 函数
- [ ] 注意：当前是每天都发送，需求是 18-22 日

---

#### 2.3 月末提醒时间
**当前配置**: 月末 17:00
**需求要求**: 23 日 09:32

- [ ] 确认是否需要调整
- [ ] 检查最终提醒内容是否包含 FILE_URL
- [ ] 检查是否正确列出逾期任务

---

### 3. 数据持久化

#### 3.1 文件完整性
- [ ] `created_tasks.json` 存在且可读写
- [ ] `task_stats.json` 存在且可读写
- [ ] `tasks.yaml` 正确配置（包含所有任务模板）

**检查命令**:
```bash
cd /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack
ls -la *.json *.yaml
cat created_tasks.json
cat task_stats.json | head -50
```

---

#### 3.2 数据备份
- [ ] 设置定期备份（建议每日）
- [ ] 备份到不同位置（避免单点故障）
- [ ] 测试恢复流程

**建议备份脚本**:
```bash
#!/bin/bash
# backup_data.sh
BACKUP_DIR="/home/hdi918072/backup/monthly-report-bot"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cd /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack

cp created_tasks.json $BACKUP_DIR/created_tasks_$DATE.json
cp task_stats.json $BACKUP_DIR/task_stats_$DATE.json
cp tasks.yaml $BACKUP_DIR/tasks_$DATE.yaml

# 只保留最近7天的备份
find $BACKUP_DIR -name "*.json" -mtime +7 -delete
```

---

### 4. 环境配置

#### 4.1 环境变量
- [ ] `APP_ID` 已设置（正式环境的 APP_ID）
- [ ] `APP_SECRET` 已设置
- [ ] `CHAT_ID` 已设置（正式群的 CHAT_ID）
- [ ] `WELCOME_CARD_ID` 已设置
- [ ] `TZ` 时区设置为 `America/Argentina/Buenos_Aires`
- [ ] `FILE_URL` 已设置（月报文件链接）

**检查命令**:
```bash
sudo systemctl status monthly-report-bot
sudo journalctl -u monthly-report-bot -n 50 | grep "环境变量\|APP_ID\|CHAT_ID"
```

**预期输出**:
```
环境变量验证通过
APP_ID: cli_xxxxx (正式环境的ID)
CHAT_ID: oc_xxxxx (正式群的ID)
```

---

#### 4.2 服务配置
- [ ] systemd 服务文件正确配置
- [ ] 服务设置为开机自启
- [ ] 日志输出正常
- [ ] 重启后自动恢复

**检查命令**:
```bash
sudo systemctl is-enabled monthly-report-bot  # 应返回 "enabled"
sudo systemctl restart monthly-report-bot
sudo systemctl status monthly-report-bot
```

---

### 5. 稳定性测试

#### 5.1 WebSocket 连接
- [ ] WS 连接建立成功
- [ ] 心跳保持正常
- [ ] 断线能自动重连（模拟网络中断）
- [ ] 重连后功能正常

**监控日志**:
```bash
sudo journalctl -u monthly-report-bot -f | grep "connected\|disconnected\|reconnect"
```

---

#### 5.2 服务重启测试
- [ ] 正常重启：`sudo systemctl restart monthly-report-bot`
- [ ] 服务器重启后自动启动
- [ ] 重启后数据不丢失
- [ ] 重启后 WS 连接正常建立

---

#### 5.3 异常处理
- [ ] 飞书 API 返回错误时有日志记录
- [ ] 文件读写失败有 fallback 机制
- [ ] 无任务数据时有友好提示
- [ ] 用户输入非法命令时有帮助信息

---

## ⚠️ 建议检查项（Recommended）

### 6. 用户体验

#### 6.1 交互响应
- [ ] 命令响应时间 < 2 秒
- [ ] 图表生成时间 < 5 秒
- [ ] 错误提示清晰友好

---

#### 6.2 消息格式
- [ ] @ 用户格式正确
- [ ] 卡片排版美观
- [ ] 文本换行合理
- [ ] Emoji 使用得当

---

### 7. 安全性

#### 7.1 权限控制
- [ ] 服务以非 root 用户运行
- [ ] 文件权限合理（600 或 644）
- [ ] 环境变量通过 systemd EnvironmentFile 注入（不在代码中硬编码）

---

#### 7.2 密钥管理
- [ ] APP_SECRET 不出现在日志中
- [ ] 敏感信息不提交到 Git
- [ ] `.env` 文件在 `.gitignore` 中

---

### 8. 监控和告警

#### 8.1 日志监控
- [ ] 设置日志告警（错误日志过多时通知）
- [ ] 定期检查日志（每周）
- [ ] 关键操作有审计日志

**建议监控命令**:
```bash
# 查看错误日志
sudo journalctl -u monthly-report-bot --since "1 hour ago" | grep "ERROR\|CRITICAL"

# 查看重启次数
sudo systemctl status monthly-report-bot | grep "Active"
```

---

#### 8.2 性能监控
- [ ] 监控 CPU 使用率
- [ ] 监控内存使用
- [ ] 监控磁盘空间

---

## 📊 已知问题和限制

### 当前版本限制

1. **❌ 缺少卡片按钮交互**
   - 无法通过按钮直接标记任务完成
   - 无法通过按钮申请延期
   - 需要使用命令或在飞书任务列表中操作

2. **❌ 缺少新成员欢迎功能**
   - 新成员加入群不会收到欢迎消息
   - 需要手动告知使用方法

3. **❌ 没有群级配置**
   - 所有配置是全局的
   - 无法为不同群设置不同参数

4. **⚠️ 定时时间与需求不完全一致**
   - 任务创建: 19日 21:10（需求: 17-19日 09:30）
   - 每日提醒: 每天 09:00（需求: 18-22日 09:31）
   - 月末提醒: 月末 17:00（需求: 23日 09:32）

5. **⚠️ 简化的交互系统**
   - 仅支持命令，不支持自然语言
   - 需要输入精确命令（如 `/stats`）

6. **🔄 Emoji 字体显示（调试中）**
   - 已配置 Symbola 字体
   - findfont() 能找到字体
   - 需要实际测试验证显示效果

---

## 🎯 部署决策

### 情况 A：可以部署（推荐）

**条件**：
- ✅ 核心功能测试通过
- ✅ 图表显示正常（包括 emoji）
- ✅ 稳定性测试通过
- ✅ 数据持久化正常

**虽然有以下限制，但不影响核心使用**：
- 定时时间可后续调整
- 卡片按钮可后续添加
- 简化交互可满足基本需求

**部署步骤**：
1. 将测试群的成功配置迁移到正式群
2. 更新环境变量（APP_ID, CHAT_ID）
3. 同步 tasks.yaml 和任务数据
4. 重启服务
5. 在正式群测试基本功能

---

### 情况 B：需要修复后部署

**条件**：
- ❌ Emoji 显示仍然为方框（图表不美观）
- ❌ 核心功能测试失败
- ❌ 数据持久化有问题

**修复方案**：
1. **Emoji 问题** → 实施 [NEXT_STEPS_2025-11-11.md](NEXT_STEPS_2025-11-11.md) 中的备选方案 A
2. **功能问题** → 根据测试结果修复具体问题
3. **数据问题** → 检查文件权限和读写逻辑

---

### 情况 C：分阶段部署（谨慎）

**第一阶段：只读模式**
- 部署到正式群，但禁用任务创建
- 仅测试查询、统计、图表功能
- 收集用户反馈

**第二阶段：完整功能**
- 确认第一阶段稳定后
- 启用任务创建和提醒功能
- 持续监控

---

## ✅ 部署前最终确认

**由部署负责人签字确认**：

- [ ] 我已阅读并理解所有已知问题和限制
- [ ] 我已完成所有"必须检查项"
- [ ] 我已设置好监控和告警
- [ ] 我知道如何快速回滚（关闭服务或切换 CHAT_ID）
- [ ] 我已通知正式群成员机器人上线和使用方法

**签字**：________________
**日期**：2025-11-11

---

## 📞 应急联系

**出现问题时的快速操作**：

### 紧急停止服务
```bash
ssh hdi918072@34.145.43.77
sudo systemctl stop monthly-report-bot
```

### 查看实时日志
```bash
sudo journalctl -u monthly-report-bot -f
```

### 回滚到测试群
```bash
# 修改 .env 文件中的 CHAT_ID 回到测试群
sudo systemctl restart monthly-report-bot
```

---

## 📚 相关文档

- [需求实现对照表](需求实现对照表.md) - 详细的功能对照
- [NEXT_STEPS_2025-11-11.md](NEXT_STEPS_2025-11-11.md) - Emoji 字体修复步骤
- [PITFALLS_EMOJI_FONT_DEBUG.md](PITFALLS_EMOJI_FONT_DEBUG.md) - 调试错题本
- [月报机器人需求说明书_WS长连接版_v1.1.md](monthly_report_bot_link_pack/月报机器人需求说明书_WS长连接版_v1.1.md) - 原始需求

---

**文档版本**: v1.0
**最后更新**: 2025-11-11
**维护者**: Claude Code Assistant
