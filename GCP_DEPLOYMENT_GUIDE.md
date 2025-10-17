# 🚀 Google Cloud Platform 部署指南

## 📋 目录
- [准备工作](#准备工作)
- [快速部署](#快速部署)
- [详细步骤](#详细步骤)
- [服务管理](#服务管理)
- [故障排除](#故障排除)
- [成本优化](#成本优化)

---

## 🎯 准备工作

### 1. 注册GCP账号
1. 访问 https://cloud.google.com/
2. 点击"免费开始使用"
3. 使用Google账号登录
4. 填写信用卡信息（不会扣费，仅用于验证）
5. 获得 $300 新用户额度（90天有效）

### 2. 创建项目
1. 登录GCP控制台
2. 点击顶部"选择项目" → "新建项目"
3. 项目名称：`monthly-report-bot`
4. 点击"创建"

### 3. 启用Compute Engine API
1. 在控制台搜索"Compute Engine"
2. 点击"启用API"
3. 等待启用完成

---

## ⚡ 快速部署（5分钟）

### 方法1：使用自动部署脚本（推荐）

#### 步骤1：创建虚拟机

在GCP控制台创建VM实例：

**配置参数**：
- **名称**：`monthly-report-bot`
- **区域**：`us-west1` （俄勒冈）
- **可用区**：`us-west1-b`
- **机器类型**：
  - 系列：E2
  - 机器类型：`e2-micro` （免费）
- **启动磁盘**：
  - 操作系统：Ubuntu
  - 版本：Ubuntu 22.04 LTS
  - 磁盘大小：30 GB（标准永久性磁盘）
- **防火墙**：
  - ✅ 允许HTTP流量
  - ✅ 允许HTTPS流量

#### 步骤2：连接到虚拟机

点击VM实例右侧的"SSH"按钮，打开Web SSH终端

#### 步骤3：运行部署脚本

在SSH终端中执行：

```bash
# 下载部署脚本
wget https://raw.githubusercontent.com/chaochaoying-ui/monthly-report-bot/main/deploy_to_gcp.sh

# 添加执行权限
chmod +x deploy_to_gcp.sh

# 运行脚本
./deploy_to_gcp.sh
```

**等待5-10分钟，脚本会自动完成所有配置！**

#### 步骤4：验证部署

```bash
# 查看服务状态
sudo systemctl status monthly-report-bot

# 查看运行日志
sudo tail -f /var/log/monthly-report-bot.log
```

看到 "WebSocket连接成功" 即表示部署完成！

---

## 📝 详细步骤（手动部署）

### 步骤1：连接虚拟机

```bash
# 通过gcloud CLI连接（可选）
gcloud compute ssh monthly-report-bot --zone=us-west1-b

# 或使用Web SSH（推荐）
# 在GCP控制台点击VM实例的"SSH"按钮
```

### 步骤2：更新系统

```bash
sudo apt update && sudo apt upgrade -y
```

### 步骤3：安装Python 3.11

```bash
sudo apt install -y python3.11 python3.11-venv python3-pip git
```

### 步骤4：克隆项目

```bash
cd ~
git clone https://github.com/chaochaoying-ui/monthly-report-bot.git
cd monthly-report-bot/monthly_report_bot_link_pack
```

### 步骤5：创建虚拟环境

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 步骤6：安装依赖

```bash
pip install --upgrade pip
pip install -r requirements_v1_1.txt
```

### 步骤7：配置环境变量

```bash
nano .env
```

添加以下内容：

```env
FEISHU_APP_ID=cli_a8fd44a9453cd00c
FEISHU_APP_SECRET=jsVoFWgaaw05en6418h7xbhV5oXxAwIm
CHAT_ID=oc_e4218b232326ea81a077b65c4cd16ce5
WELCOME_CARD_ID=AAqInYqWzIiu6
FILE_URL=https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd
VERIFICATION_TOKEN=v_01J6RE0Q4VEcCQ0hFg1RbdLT
TZ=America/Argentina/Buenos_Aires
PYTHONIOENCODING=utf-8
```

保存并退出（`Ctrl+X` → `Y` → `Enter`）

### 步骤8：测试运行

```bash
# 激活虚拟环境
source venv/bin/activate

# 测试运行
python monthly_report_bot_final_interactive.py
```

如果看到连接成功的日志，按 `Ctrl+C` 停止，继续配置服务。

### 步骤9：创建systemd服务

```bash
sudo nano /etc/systemd/system/monthly-report-bot.service
```

添加以下内容（**替换YOUR_USERNAME为实际用户名**）：

```ini
[Unit]
Description=Monthly Report Bot for Feishu
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/monthly-report-bot/monthly_report_bot_link_pack
Environment="PATH=/home/YOUR_USERNAME/monthly-report-bot/monthly_report_bot_link_pack/venv/bin"
EnvironmentFile=/home/YOUR_USERNAME/monthly-report-bot/monthly_report_bot_link_pack/.env
ExecStart=/home/YOUR_USERNAME/monthly-report-bot/monthly_report_bot_link_pack/venv/bin/python monthly_report_bot_final_interactive.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/monthly-report-bot.log
StandardError=append:/var/log/monthly-report-bot-error.log

[Install]
WantedBy=multi-user.target
```

保存并退出。

### 步骤10：创建日志文件

```bash
sudo touch /var/log/monthly-report-bot.log
sudo touch /var/log/monthly-report-bot-error.log
sudo chown $USER:$USER /var/log/monthly-report-bot.log
sudo chown $USER:$USER /var/log/monthly-report-bot-error.log
```

### 步骤11：启动服务

```bash
# 重新加载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start monthly-report-bot

# 设置开机自启
sudo systemctl enable monthly-report-bot

# 查看状态
sudo systemctl status monthly-report-bot
```

---

## 🔧 服务管理

### 常用命令

```bash
# 查看服务状态
sudo systemctl status monthly-report-bot

# 启动服务
sudo systemctl start monthly-report-bot

# 停止服务
sudo systemctl stop monthly-report-bot

# 重启服务
sudo systemctl restart monthly-report-bot

# 查看实时日志
sudo tail -f /var/log/monthly-report-bot.log

# 查看错误日志
sudo tail -f /var/log/monthly-report-bot-error.log

# 查看最近50条系统日志
sudo journalctl -u monthly-report-bot -n 50

# 查看实时系统日志
sudo journalctl -u monthly-report-bot -f
```

### 更新代码

```bash
# 进入项目目录
cd ~/monthly-report-bot

# 拉取最新代码
git pull

# 重启服务
sudo systemctl restart monthly-report-bot

# 查看状态
sudo systemctl status monthly-report-bot
```

---

## 🔍 故障排除

### 问题1：服务无法启动

```bash
# 查看详细错误信息
sudo journalctl -u monthly-report-bot -n 100

# 检查配置文件
cat /etc/systemd/system/monthly-report-bot.service

# 手动测试运行
cd ~/monthly-report-bot/monthly_report_bot_link_pack
source venv/bin/activate
python monthly_report_bot_final_interactive.py
```

### 问题2：WebSocket连接失败

```bash
# 检查网络连接
ping open.feishu.cn

# 检查环境变量
cat ~/monthly-report-bot/monthly_report_bot_link_pack/.env

# 查看错误日志
sudo tail -f /var/log/monthly-report-bot-error.log
```

### 问题3：依赖安装失败

```bash
# 重新安装依赖
cd ~/monthly-report-bot/monthly_report_bot_link_pack
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements_v1_1.txt --force-reinstall
```

### 问题4：权限问题

```bash
# 检查文件所有者
ls -la ~/monthly-report-bot

# 修复权限
sudo chown -R $USER:$USER ~/monthly-report-bot
```

---

## 💰 成本优化

### 永久免费额度

GCP e2-micro实例永久免费，包括：
- ✅ 1个虚拟CPU
- ✅ 1GB内存
- ✅ 30GB标准存储
- ✅ 每月1GB出站流量（北美）

**月报机器人的资源使用**：
- CPU：< 10%
- 内存：< 300MB
- 存储：< 2GB
- 流量：< 100MB/月

✅ **完全在免费额度内！**

### 注意事项

1. **选择免费区域**：
   - us-west1
   - us-central1
   - us-east1

2. **使用标准磁盘**：
   - 选择"标准永久性磁盘"
   - 不要选择SSD

3. **监控使用量**：
   - 在GCP控制台查看"结算"
   - 设置预算提醒

---

## ✅ 部署验证清单

- [ ] VM实例创建成功
- [ ] SSH连接正常
- [ ] Python 3.11安装完成
- [ ] 项目克隆成功
- [ ] 依赖安装完成
- [ ] 环境变量配置正确
- [ ] systemd服务创建成功
- [ ] 服务启动成功
- [ ] 日志显示连接成功
- [ ] 飞书群聊测试@机器人有响应

---

## 🎯 下一步

部署完成后：

1. **测试实时交互**：
   - 在飞书群聊@机器人
   - 发送"帮助"查看命令
   - 测试"我的任务"等功能

2. **监控运行状态**：
   - 定期查看日志
   - 设置GCP监控告警

3. **保持更新**：
   - 定期拉取GitHub最新代码
   - 更新后重启服务

---

## 📞 获取帮助

如遇问题：
1. 查看本文档的"故障排除"部分
2. 检查GitHub仓库的Issues
3. 查看GCP官方文档

---

**🎉 恭喜！您的月报机器人现在24小时在线运行了！**

