# GitHub Actions 部署指南

## 🚀 部署概述

本指南将帮助您在GitHub上部署月报机器人，实现每月自动执行任务。

## 📋 部署步骤

### 1. 配置GitHub Secrets

在GitHub仓库中设置以下密钥：

1. 进入仓库页面
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret** 添加以下密钥：

```
FEISHU_APP_ID=你的飞书应用ID
FEISHU_APP_SECRET=你的飞书应用密钥
FEISHU_VERIFICATION_TOKEN=你的飞书验证令牌
FEISHU_ENCRYPT_KEY=你的飞书加密密钥（可选）
CHAT_ID=目标群聊ID
WELCOME_CARD_ID=欢迎卡片ID（默认：AAqInYqWzIiu6）
```

### 2. 验证工作流

1. 进入 **Actions** 页面
2. 找到 "月报机器人定时任务" 工作流
3. 点击 **Run workflow** 进行手动测试

### 3. 定时任务说明

机器人将按照以下时间表自动执行：

| 日期 | 时间 | 任务 | 描述 |
|------|------|------|------|
| 17-19日 | 09:30 | 创建任务 | 创建24个月报任务并@负责人 |
| 18-22日 | 09:31 | 每日统计 | 发送任务完成情况统计 |
| 23日 | 09:32 | 最终提醒 | 发送截止日期提醒 |
| 23日 | 18:00 | 最终统计 | 发送月度统计报告 |

### 4. 时区配置

默认时区：`America/Argentina/Buenos_Aires` (UTC-3)

如需修改时区，编辑 `.github/workflows/monthly-bot-scheduler.yml` 中的cron表达式。

## 🔧 高级配置

### 自定义执行时间

修改 `.github/workflows/monthly-bot-scheduler.yml` 中的cron表达式：

```yaml
schedule:
  - cron: '30 12 17-19 * *'  # 分钟 小时 日期 月份 星期
```

### 手动触发

工作流支持手动触发，可以指定任务类型：

- `create_tasks`: 创建任务
- `daily_stats`: 每日统计
- `final_reminder`: 最终提醒
- `final_stats`: 最终统计

## 📊 监控和日志

### 查看执行日志

1. 进入 **Actions** 页面
2. 点击对应的工作流运行记录
3. 查看详细日志

### 执行状态通知

工作流执行完成后会显示：
- 执行时间
- GitHub Actions URL
- 成功/失败状态

## 🛠️ 故障排除

### 常见问题

1. **令牌过期**
   - 检查飞书应用配置
   - 确认App ID和App Secret正确

2. **群聊ID错误**
   - 确认CHAT_ID是群聊的open_chat_id
   - 检查机器人是否已加入群聊

3. **定时任务未执行**
   - 检查GitHub Actions是否启用
   - 确认cron表达式正确
   - 查看仓库是否设置为公开（私有仓库有限制）

### 调试模式

启用详细日志：

```yaml
- name: 执行任务创建
  env:
    LOG_LEVEL: DEBUG
  run: |
    # 任务执行代码
```

## 📈 扩展功能

### 添加新任务

1. 修改 `tasks.yaml` 文件
2. 提交到main分支
3. 工作流将自动使用新配置

### 自定义消息模板

修改 `github_actions_bot.py` 中的消息模板函数。

### 集成其他服务

可以在工作流中添加：
- 邮件通知
- Slack通知
- 数据库记录
- 其他API调用

## 🔒 安全注意事项

1. **密钥管理**
   - 不要在代码中硬编码密钥
   - 定期轮换飞书应用密钥
   - 使用最小权限原则

2. **访问控制**
   - 限制仓库访问权限
   - 审查工作流权限
   - 监控异常活动

3. **数据保护**
   - 敏感数据加密存储
   - 定期清理日志
   - 遵循数据保护法规

## 📞 技术支持

如遇问题，请：

1. 查看GitHub Actions执行日志
2. 检查飞书开发者控制台
3. 参考项目文档
4. 提交Issue到仓库

---

**部署完成后，您的月报机器人将在GitHub云端自动运行，无需本地维护！**
