# GCP 部署前检查清单

## 📋 部署前必读

在运行 `deploy_to_gcp.sh` 脚本之前，请确认以下事项：

### 1. GCP 虚拟机要求 ✅

- **操作系统**: Ubuntu 22.04 LTS（推荐）
- **CPU**: 最低 1 核心（e2-micro 免费层）
- **内存**: 最低 1 GB
- **磁盘**: 最低 10 GB
- **网络**: 需要访问外网（访问 GitHub 和飞书 API）

### 2. 必需的飞书配置 ✅

在运行脚本前，请确认您已经有以下信息（脚本中已包含）：

```bash
FEISHU_APP_ID=cli_a8fd44a9453cd00c
FEISHU_APP_SECRET=jsVoFWgaaw05en6418h7xbhV5oXxAwIm
CHAT_ID=oc_e4218b232326ea81a077b65c4cd16ce5
WELCOME_CARD_ID=AAqInYqWzIiu6
FILE_URL=https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd
VERIFICATION_TOKEN=v_01J6RE0Q4VEcCQ0hFg1RbdLT
```

### 3. 飞书应用权限配置 ✅

确保您的飞书应用已配置以下权限：

- ✅ 获取与发送单聊、群组消息
- ✅ 接收群聊消息
- ✅ 获取群组信息
- ✅ 发送卡片消息
- ✅ WebSocket 连接权限

### 4. 部署脚本改进清单 ✅

**已修复的问题：**

- ✅ **apt 锁文件冲突**: 添加了等待机制，避免与系统自动更新冲突
- ✅ **移除系统升级**: 不再执行 `apt upgrade`，避免长时间等待
- ✅ **优化依赖安装**: 只安装核心依赖，包括 `websockets`
- ✅ **增强错误处理**: 服务失败时显示详细的调试信息
- ✅ **日志权限修复**: 自动设置日志文件权限
- ✅ **停止旧服务**: 在启动前先停止旧服务

## 🚀 部署步骤

### 方法一：一键部署（推荐）

```bash
# SSH 连接到 GCP 虚拟机后执行
wget https://raw.githubusercontent.com/chaochaoying-ui/monthly-report-bot/main/deploy_to_gcp.sh
chmod +x deploy_to_gcp.sh
./deploy_to_gcp.sh
```

### 方法二：分步部署（调试用）

如果一键部署失败，可以按以下步骤手动执行：

```bash
# 1. 更新系统
sudo apt update

# 2. 安装 Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip git wget curl

# 3. 克隆项目
cd ~
git clone https://github.com/chaochaoying-ui/monthly-report-bot.git
cd monthly-report-bot/monthly_report_bot_link_pack

# 4. 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 5. 安装依赖
pip install --upgrade pip
pip install requests>=2.31.0 PyYAML>=6.0.1 pytz>=2023.3 cryptography>=41.0.0 websockets>=11.0

# 6. 创建 .env 文件
cat > .env << 'EOF'
FEISHU_APP_ID=cli_a8fd44a9453cd00c
FEISHU_APP_SECRET=jsVoFWgaaw05en6418h7xbhV5oXxAwIm
CHAT_ID=oc_e4218b232326ea81a077b65c4cd16ce5
WELCOME_CARD_ID=AAqInYqWzIiu6
FILE_URL=https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd
VERIFICATION_TOKEN=v_01J6RE0Q4VEcCQ0hFg1RbdLT
TZ=America/Argentina/Buenos_Aires
PYTHONIOENCODING=utf-8
EOF

# 7. 测试运行（可选，Ctrl+C 退出）
python monthly_report_bot_final_interactive.py
```

## 🔧 故障排查

### 如果部署失败

**1. 下载诊断脚本**

```bash
wget https://raw.githubusercontent.com/chaochaoying-ui/monthly-report-bot/main/diagnose_service.sh
chmod +x diagnose_service.sh
./diagnose_service.sh
```

**2. 下载修复脚本**

```bash
wget https://raw.githubusercontent.com/chaochaoying-ui/monthly-report-bot/main/fix_gcp_service.sh
chmod +x fix_gcp_service.sh
./fix_gcp_service.sh
```

### 常见错误

#### 错误 1: `ModuleNotFoundError: No module named 'websockets'`

**原因**: 依赖未安装或安装失败

**解决方案**:
```bash
cd ~/monthly-report-bot/monthly_report_bot_link_pack
source venv/bin/activate
pip install websockets>=11.0
sudo systemctl restart monthly-report-bot
```

#### 错误 2: `Could not get lock /var/lib/apt/lists/lock`

**原因**: 系统正在自动更新

**解决方案**: 等待 2-3 分钟后重新运行，或手动终止：
```bash
sudo killall apt apt-get
sudo rm /var/lib/apt/lists/lock
sudo rm /var/lib/dpkg/lock*
sudo dpkg --configure -a
```

#### 错误 3: 服务启动但无法连接飞书

**原因**: 网络配置或防火墙问题

**解决方案**:
```bash
# 检查网络连接
curl -I https://open.feishu.cn

# 检查机器人日志
sudo tail -f /var/log/monthly-report-bot.log
sudo tail -f /var/log/monthly-report-bot-error.log
```

#### 错误 4: `.env` 文件不存在

**原因**: 脚本未正确创建环境变量文件

**解决方案**: 手动创建（见"方法二：分步部署"第 6 步）

## 📊 验证部署

### 1. 检查服务状态

```bash
sudo systemctl status monthly-report-bot
```

**期望输出**: `Active: active (running)`

### 2. 查看实时日志

```bash
sudo tail -f /var/log/monthly-report-bot.log
```

**期望输出**: 连接成功的日志信息

### 3. 在飞书群聊中测试

- 在配置的群聊中 `@机器人` 发送消息
- 查看机器人是否有回应

## 🔄 日常维护命令

```bash
# 查看服务状态
sudo systemctl status monthly-report-bot

# 重启服务
sudo systemctl restart monthly-report-bot

# 停止服务
sudo systemctl stop monthly-report-bot

# 启动服务
sudo systemctl start monthly-report-bot

# 查看实时日志
sudo tail -f /var/log/monthly-report-bot.log

# 查看错误日志
sudo tail -f /var/log/monthly-report-bot-error.log

# 查看 systemd 日志
sudo journalctl -u monthly-report-bot -f

# 查看最近 100 条日志
sudo journalctl -u monthly-report-bot -n 100
```

## 📝 更新代码

```bash
cd ~/monthly-report-bot
git pull
sudo systemctl restart monthly-report-bot
```

## 🛑 卸载服务

```bash
# 停止并禁用服务
sudo systemctl stop monthly-report-bot
sudo systemctl disable monthly-report-bot

# 删除服务文件
sudo rm /etc/systemd/system/monthly-report-bot.service
sudo systemctl daemon-reload

# 删除日志文件
sudo rm /var/log/monthly-report-bot.log
sudo rm /var/log/monthly-report-bot-error.log

# 删除项目（可选）
rm -rf ~/monthly-report-bot
```

## 💡 最佳实践

1. **定期更新**: 每周或每月拉取最新代码
2. **监控日志**: 定期检查错误日志，及时发现问题
3. **备份配置**: 保存 `.env` 文件备份
4. **测试环境**: 重要更新前先在测试环境验证
5. **资源监控**: 使用 `htop` 或 GCP 控制台监控资源使用

## 🆘 获取帮助

如果遇到无法解决的问题，请提供以下信息：

1. 执行 `diagnose_service.sh` 的完整输出
2. `/var/log/monthly-report-bot-error.log` 的最后 50 行
3. `sudo journalctl -u monthly-report-bot -n 50` 的输出
4. GCP 虚拟机配置（CPU、内存、磁盘）

---

**部署脚本版本**: v2.0 (2025-10-18)  
**最后更新**: 2025-10-18

