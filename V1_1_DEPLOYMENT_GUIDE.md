# 月报机器人 v1.1 部署指南

> 完整的 v1.1 版本部署、测试和上线指南

## 📋 目录

- [环境要求](#环境要求)
- [部署前准备](#部署前准备)
- [部署方法](#部署方法)
  - [方法1: GCP云服务器部署](#方法1-gcp云服务器部署)
  - [方法2: 本地服务器部署](#方法2-本地服务器部署)
- [配置说明](#配置说明)
- [测试验证](#测试验证)
- [服务管理](#服务管理)
- [故障排查](#故障排查)
- [从旧版本迁移](#从旧版本迁移)

---

## 环境要求

### 系统要求
- **操作系统**: Ubuntu 20.04+ / Debian 10+ / CentOS 7+
- **Python 版本**: Python 3.9+
- **内存**: 至少 512MB RAM
- **磁盘**: 至少 1GB 可用空间
- **网络**: 稳定的互联网连接，可访问飞书 API

### 必需软件
- Python 3.9+
- pip (Python 包管理器)
- git (用于代码更新)
- systemd (用于服务管理，Linux系统自带)

---

## 部署前准备

### 1. 获取飞书应用凭证

登录 [飞书开放平台](https://open.feishu.cn/)：

1. 创建企业自建应用
2. 获取以下信息：
   - `APP_ID`: 应用ID
   - `APP_SECRET`: 应用密钥
3. 配置应用权限：
   - `im:message` - 发送消息
   - `im:message.group_at_msg` - 接收群聊@消息
   - `im:chat` - 获取群信息
4. 获取目标群聊ID (`CHAT_ID`)
5. 准备文件链接 (`FILE_URL`)

### 2. 检查网络连接

```bash
# 测试飞书 API 连通性
curl -I https://open.feishu.cn

# 测试 WebSocket 连通性
telnet open.feishu.cn 443
```

---

## 部署方法

### 方法1: GCP云服务器部署

#### 步骤1: 连接到GCP服务器

```bash
# SSH 连接到 GCP 实例
gcloud compute ssh your-instance-name --zone=your-zone

# 或使用标准 SSH
ssh username@your-gcp-ip
```

#### 步骤2: 克隆代码仓库

```bash
# 克隆仓库
cd /opt
sudo git clone https://github.com/chaochaoying-ui/monthly-report-bot.git
cd monthly-report-bot

# 切换到月报机器人目录
cd monthly_report_bot_link_pack/monthly_report_bot_link_pack
```

#### 步骤3: 安装依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements_v1_1.txt
```

#### 步骤4: 配置环境变量

```bash
# 创建 .env 文件
cat > .env << 'EOF'
APP_ID=cli_a8fd44a9453cd00c
APP_SECRET=jsVoFWgaaw05en6418h7xbhV5oXxAwIm
CHAT_ID=oc_07f2d3d314f00fc29baf323a3a589972
FILE_URL=https://be9bhmcgo2.feishu.cn/file/Wn5AbQAmVo32OExC5zIcIiAXnKc?office_edit=1
TZ=America/Argentina/Buenos_Aires
ENABLE_NLU=true
INTENT_THRESHOLD=0.75
LANGS=["zh","en","es"]
WS_ENDPOINT=wss://open.feishu.cn/ws/v2
WS_HEARTBEAT_INTERVAL=30
WS_RECONNECT_MAX_ATTEMPTS=5
LOG_LEVEL=INFO
EOF
```

#### 步骤5: 创建 systemd 服务

```bash
# 创建服务文件
sudo tee /etc/systemd/system/monthly-report-bot-v1.1.service > /dev/null << 'EOF'
[Unit]
Description=Monthly Report Bot v1.1
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot_link_pack
Environment="PATH=/opt/monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot_link_pack/venv/bin"
EnvironmentFile=/opt/monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot_link_pack/.env
ExecStart=/opt/monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot_link_pack/venv/bin/python monthly_report_bot_ws_v1.1.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start monthly-report-bot-v1.1

# 设置开机自启
sudo systemctl enable monthly-report-bot-v1.1
```

#### 步骤6: 验证部署

```bash
# 检查服务状态
sudo systemctl status monthly-report-bot-v1.1

# 查看日志
tail -f /opt/monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot_link_pack/monthly_report_bot.log

# 或使用 journalctl
sudo journalctl -u monthly-report-bot-v1.1 -f
```

---

### 方法2: 本地服务器部署

#### Windows 部署

```powershell
# 克隆代码
git clone https://github.com/chaochaoying-ui/monthly-report-bot.git
cd monthly-report-bot\monthly_report_bot_link_pack\monthly_report_bot_link_pack

# 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements_v1_1.txt

# 配置环境变量（创建 .env 文件）
# 参考上面的 .env 内容

# 运行程序
python monthly_report_bot_ws_v1.1.py
```

#### Linux/Mac 部署

```bash
# 克隆代码
git clone https://github.com/chaochaoying-ui/monthly-report-bot.git
cd monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot_link_pack

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements_v1_1.txt

# 配置环境变量
# 创建 .env 文件，参考上面的内容

# 运行程序
python monthly_report_bot_ws_v1.1.py
```

---

## 配置说明

### 环境变量详解

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| APP_ID | ✅ | - | 飞书应用ID |
| APP_SECRET | ✅ | - | 飞书应用密钥 |
| CHAT_ID | ✅ | - | 目标群聊ID |
| FILE_URL | ✅ | - | 月报文件链接 |
| TZ | ✅ | America/Argentina/Buenos_Aires | 时区设置 |
| ENABLE_NLU | ❌ | true | 是否启用智能交互 |
| INTENT_THRESHOLD | ❌ | 0.75 | 意图识别阈值 |
| LANGS | ❌ | ["zh","en","es"] | 支持的语言 |
| WS_ENDPOINT | ❌ | wss://open.feishu.cn/ws/v2 | WebSocket端点 |
| WS_HEARTBEAT_INTERVAL | ❌ | 30 | 心跳间隔（秒） |
| WS_RECONNECT_MAX_ATTEMPTS | ❌ | 5 | 最大重连次数 |
| LOG_LEVEL | ❌ | INFO | 日志级别 |

### 群级配置文件

`group_config.json`:

```json
{
  "push_time": "09:00",
  "file_url": "https://be9bhmcgo2.feishu.cn/file/xxx",
  "timezone": "America/Argentina/Buenos_Aires",
  "created_tasks": {}
}
```

---

## 测试验证

### 1. 运行测试脚本

```bash
# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 运行测试
python test_bot_v1_1.py
```

### 2. 测试项目

测试脚本会验证以下内容：

- ✅ 环境变量配置
- ✅ 智能交互引擎
- ✅ 卡片设计模块
- ✅ WebSocket 连接
- ✅ 多语言支持
- ✅ 意图识别准确率

### 3. 手动测试

#### 测试 WebSocket 连接

```bash
# 查看日志，确认 WebSocket 连接成功
tail -f monthly_report_bot.log | grep "WebSocket"
```

#### 测试卡片发送

在群聊中：
1. 添加新成员 → 应该收到欢迎卡片（≤3秒）
2. 等待定时任务触发
3. 查看日志确认任务执行

#### 测试智能交互

在群聊中发送：
- "我的任务" → 应该收到私聊消息
- "查看进度" → 应该收到进度卡片
- "帮助" → 应该收到帮助信息

---

## 服务管理

### 启动服务

```bash
sudo systemctl start monthly-report-bot-v1.1
```

### 停止服务

```bash
sudo systemctl stop monthly-report-bot-v1.1
```

### 重启服务

```bash
sudo systemctl restart monthly-report-bot-v1.1
```

### 查看状态

```bash
sudo systemctl status monthly-report-bot-v1.1
```

### 查看日志

```bash
# 实时日志
sudo journalctl -u monthly-report-bot-v1.1 -f

# 最近100行
sudo journalctl -u monthly-report-bot-v1.1 -n 100

# 应用日志文件
tail -f monthly_report_bot.log
```

### 开机自启

```bash
# 启用开机自启
sudo systemctl enable monthly-report-bot-v1.1

# 禁用开机自启
sudo systemctl disable monthly-report-bot-v1.1
```

---

## 故障排查

### 问题1: WebSocket 连接失败

**症状**: 日志显示 "WebSocket 连接失败"

**解决方法**:
```bash
# 1. 检查网络连接
ping open.feishu.cn

# 2. 验证应用凭证
echo $APP_ID
echo $APP_SECRET

# 3. 检查防火墙
sudo ufw status

# 4. 重启服务
sudo systemctl restart monthly-report-bot-v1.1
```

### 问题2: 卡片发送失败

**症状**: "卡片发送失败: 权限不足"

**解决方法**:
1. 登录飞书开放平台
2. 检查应用权限设置
3. 确认应用已添加到群聊
4. 验证 CHAT_ID 是否正确

### 问题3: 定时任务未执行

**症状**: 到了指定时间但任务没有执行

**解决方法**:
```bash
# 1. 检查系统时区
timedatectl

# 2. 检查服务时区配置
echo $TZ

# 3. 查看日志
tail -f monthly_report_bot.log | grep "should_"

# 4. 手动触发测试
# 修改时间判断条件进行测试
```

### 问题4: 内存不足

**症状**: 服务频繁重启，日志显示内存错误

**解决方法**:
```bash
# 1. 检查内存使用
free -m

# 2. 增加swap空间（GCP）
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 3. 优化配置，减少日志输出
# 在 .env 中设置
LOG_LEVEL=WARNING
```

### 问题5: 智能交互识别率低

**症状**: 用户输入无法正确识别意图

**解决方法**:
1. 检查 INTENT_THRESHOLD 设置（降低阈值）
2. 查看 smart_interaction_ws_v1_1.py 中的意图规则
3. 添加更多同义词
4. 启用降级机制（卡片按钮）

---

## 从旧版本迁移

### 迁移步骤

#### 1. 备份现有数据

```bash
# 备份数据文件
cp task_stats.json task_stats.json.backup
cp created_tasks.json created_tasks.json.backup
cp tasks.yaml tasks.yaml.backup

# 备份日志
cp monthly_report_bot.log monthly_report_bot.log.backup
```

#### 2. 停止旧版本服务

```bash
# 如果使用 systemd
sudo systemctl stop monthly-report-bot

# 或直接 kill 进程
pkill -f monthly_report_bot_final_interactive.py
```

#### 3. 更新代码

```bash
# 拉取最新代码
cd /opt/monthly-report-bot
git pull origin main

# 切换到新目录
cd monthly_report_bot_link_pack/monthly_report_bot_link_pack
```

#### 4. 安装新依赖

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装/更新依赖
pip install -r requirements_v1_1.txt
```

#### 5. 更新配置

```bash
# 添加 v1.1 新配置项到 .env
cat >> .env << 'EOF'
ENABLE_NLU=true
INTENT_THRESHOLD=0.75
LANGS=["zh","en","es"]
WS_ENDPOINT=wss://open.feishu.cn/ws/v2
WS_HEARTBEAT_INTERVAL=30
WS_RECONNECT_MAX_ATTEMPTS=5
EOF
```

#### 6. 创建新服务文件

```bash
# 使用上面的 systemd 服务配置
# 确保 ExecStart 指向 monthly_report_bot_ws_v1.1.py
```

#### 7. 启动新版本

```bash
sudo systemctl daemon-reload
sudo systemctl start monthly-report-bot-v1.1
sudo systemctl enable monthly-report-bot-v1.1
```

#### 8. 验证迁移

```bash
# 检查服务状态
sudo systemctl status monthly-report-bot-v1.1

# 查看日志
tail -f monthly_report_bot.log

# 运行测试
python test_bot_v1_1.py
```

### 数据兼容性

v1.1 版本完全兼容旧版本的数据文件：
- ✅ `task_stats.json` - 直接使用
- ✅ `created_tasks.json` - 直接使用
- ✅ `tasks.yaml` - 直接使用

新增数据文件：
- `group_config.json` - 自动创建
- `interaction_log.json` - 自动创建

### 回滚方案

如果需要回滚到旧版本：

```bash
# 1. 停止 v1.1 服务
sudo systemctl stop monthly-report-bot-v1.1

# 2. 恢复数据备份（如有修改）
cp task_stats.json.backup task_stats.json

# 3. 启动旧版本服务
sudo systemctl start monthly-report-bot

# 4. 验证
sudo systemctl status monthly-report-bot
```

---

## 🔐 安全建议

### 1. 环境变量保护

```bash
# 设置 .env 文件权限
chmod 600 .env

# 不要提交 .env 到 git
echo ".env" >> .gitignore
```

### 2. 定期更新

```bash
# 定期更新代码
git pull origin main

# 更新依赖
pip install -r requirements_v1_1.txt --upgrade
```

### 3. 日志管理

```bash
# 配置日志轮转
sudo tee /etc/logrotate.d/monthly-report-bot > /dev/null << 'EOF'
/opt/monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot_link_pack/monthly_report_bot.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
EOF
```

---

## 📞 技术支持

### 问题反馈

- GitHub Issues: https://github.com/chaochaoying-ui/monthly-report-bot/issues
- 邮件: support@example.com

### 相关文档

- [月报机器人完整功能文档](月报机器人完整功能文档.md)
- [v1.1 实现总结](V1_1_IMPLEMENTATION_SUMMARY.md)
- [需求说明书 v1.1](月报机器人需求说明书_WS长连接版_v1.1.md)

---

**部署指南版本**: v1.1
**最后更新**: 2025-10-21
