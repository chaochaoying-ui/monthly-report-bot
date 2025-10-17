# ⚡ GCP部署快速开始（5分钟）

## 🎯 前置条件
- ✅ Google账号
- ✅ 信用卡（验证用，不会扣费）
- ✅ GitHub代码已上传

## 📋 5步部署

### 第1步：创建GCP账号（2分钟）
1. 访问 https://cloud.google.com/
2. 点击"免费开始使用"
3. 登录Google账号
4. 填写信用卡信息
5. ✅ 获得$300免费额度

### 第2步：创建虚拟机（1分钟）

在GCP控制台：
1. 搜索"Compute Engine"
2. 点击"创建实例"
3. 快速配置：
   ```
   名称: monthly-report-bot
   区域: us-west1
   机器类型: e2-micro (免费)
   操作系统: Ubuntu 22.04 LTS
   磁盘: 30GB 标准磁盘
   防火墙: ✅ HTTP ✅ HTTPS
   ```
4. 点击"创建"

### 第3步：连接虚拟机（10秒）

点击VM实例右侧的 **"SSH"** 按钮

### 第4步：运行部署脚本（5分钟）

在SSH终端中粘贴：

```bash
wget https://raw.githubusercontent.com/chaochaoying-ui/monthly-report-bot/main/deploy_to_gcp.sh && chmod +x deploy_to_gcp.sh && ./deploy_to_gcp.sh
```

### 第5步：验证部署（30秒）

```bash
# 查看状态
sudo systemctl status monthly-report-bot

# 查看日志
sudo tail -f /var/log/monthly-report-bot.log
```

看到"WebSocket连接成功" = ✅ 完成！

---

## 🧪 测试

在飞书群聊中：
```
@月报收集系统 帮助
```

机器人应该会回复！

---

## 📊 部署架构

```
┌─────────────────────┐
│  GitHub Actions     │ ← 定时任务备份
│  (定时任务)         │
└─────────────────────┘

┌─────────────────────┐
│  GCP Compute Engine │ ← 主服务
│  (24小时实时交互)   │
│                     │
│  ┌───────────────┐  │
│  │ Ubuntu VM     │  │
│  │ Python Bot    │  │
│  │ systemd服务   │  │
│  └───────────────┘  │
└─────────────────────┘
         ↓
┌─────────────────────┐
│  飞书群聊           │
│  (实时响应@消息)    │
└─────────────────────┘
```

---

## 💰 成本

**完全免费！**

GCP e2-micro永久免费：
- ✅ 1 vCPU
- ✅ 1GB RAM
- ✅ 30GB存储
- ✅ 每月免费

机器人使用：
- CPU: < 10%
- 内存: < 300MB
- 存储: < 2GB

---

## 🔧 常用命令

```bash
# 查看状态
sudo systemctl status monthly-report-bot

# 重启服务
sudo systemctl restart monthly-report-bot

# 查看日志
sudo tail -f /var/log/monthly-report-bot.log

# 更新代码
cd ~/monthly-report-bot && git pull && sudo systemctl restart monthly-report-bot
```

---

## ❓ 遇到问题？

查看详细文档：
- `GCP_DEPLOYMENT_GUIDE.md` - 完整部署指南
- GitHub Issues - 提问交流

---

**🎉 5分钟，您的机器人已经24小时在线了！**

