# 🚀 部署月报机器人 v1.1 到 GCP - 完整指南

## ✅ 前置条件

- ✅ v1.1 代码已推送到 GitHub: https://github.com/chaochaoying-ui/monthly-report-bot
- ✅ GCP 服务器: `monthly-report-bot` (hdi918072@monthly-report-bot)
- ✅ 任务状态已确认：
  - 刘野 (Liu Ye): task_2025-10_11 已完成 ✓
  - 范明杰 (Fan Mingjie): task_2025-10_8 已完成 ✓

---

## 📊 v1.1 版本更新内容

### 核心功能
- ✅ **WebSocket 长连接**：替代 HTTP 回调
- ✅ **智能交互引擎**：支持中/英/西语意图识别
- ✅ **完整用户交互**：@机器人 + "已完成" 自动更新任务状态
- ✅ **专业级卡片设计**：欢迎卡片、任务卡片、进度图表、最终提醒
- ✅ **群级配置管理**：支持群级自定义配置
- ✅ **幂等性与补跑**：服务重启后自动补跑

### 定时任务调度
| 时间 | 任务 | 说明 |
|------|------|------|
| 每月17日 09:00 | 创建月报任务 | 自动创建23个任务（幂等） |
| 每月18-23日 09:00 | 每日任务提醒 | @ 未完成任务负责人 |
| 每月18-22日 17:00 | 发送进度图表 | 可视化任务进度（分专业统计） |
| 每月23日 17:00 | 月末催办+统计 | 紧急催办与完成情况总结 |
| 每小时 | 同步任务状态 | 确保数据一致性 |

---

## 🎯 快速部署（4 步完成）

### 步骤 1️⃣: 连接到 GCP 服务器

在 GCP 控制台找到 VM 实例 `monthly-report-bot`，点击 **SSH** 按钮打开终端。

---

### 步骤 2️⃣: 备份当前生产环境

**复制以下命令，粘贴到 GCP SSH 终端，按回车执行**：

```bash
# ============================================================================
# 备份当前生产环境
# ============================================================================

echo "========================================================================"
echo "备份当前生产环境"
echo "========================================================================"

cd ~/monthly-report-bot

# 创建备份目录
BACKUP_DIR="$HOME/monthly-report-bot-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

# 备份当前版本
echo "创建备份: $BACKUP_DIR/backup_before_v1.1_$TIMESTAMP"
cp -r monthly_report_bot_link_pack "$BACKUP_DIR/backup_before_v1.1_$TIMESTAMP"

echo "✅ 备份已创建"
echo ""

# 记录当前 Git 状态
echo "当前版本信息:"
git log -1 --oneline
echo ""
```

---

### 步骤 3️⃣: 停止当前服务并拉取 v1.1

```bash
# ============================================================================
# 停止当前服务并拉取 v1.1
# ============================================================================

echo "========================================================================"
echo "停止当前服务"
echo "========================================================================"

sudo systemctl stop monthly-report-bot

if sudo systemctl is-active --quiet monthly-report-bot; then
    echo "⚠️  服务未能停止"
    exit 1
else
    echo "✅ 服务已停止"
fi

echo ""
echo "========================================================================"
echo "拉取 v1.1 代码"
echo "========================================================================"

cd ~/monthly-report-bot

# 拉取最新代码
git fetch origin
git pull origin main

if [ $? -eq 0 ]; then
    echo "✅ 代码更新成功"
    echo "最新提交: $(git log -1 --oneline)"
else
    echo "❌ 代码更新失败"
    exit 1
fi

echo ""
```

---

### 步骤 4️⃣: 配置 v1.1 环境并启动服务

```bash
# ============================================================================
# 配置 v1.1 环境并启动
# ============================================================================

echo "========================================================================"
echo "配置 v1.1 环境"
echo "========================================================================"

cd ~/monthly-report-bot/monthly_report_bot_link_pack

# 检查 v1.1 文件
echo "检查 v1.1 核心文件..."

if [ -f "monthly_report_bot_ws_v1.1.py" ]; then
    echo "✅ monthly_report_bot_ws_v1.1.py"
else
    echo "❌ 缺少 monthly_report_bot_ws_v1.1.py"
    exit 1
fi

if [ -f "websocket_handler_v1_1.py" ]; then
    echo "✅ websocket_handler_v1_1.py"
else
    echo "❌ 缺少 websocket_handler_v1_1.py"
    exit 1
fi

if [ -f "card_design_ws_v1_1.py" ]; then
    echo "✅ card_design_ws_v1_1.py"
else
    echo "❌ 缺少 card_design_ws_v1_1.py"
    exit 1
fi

if [ -f "smart_interaction_ws_v1_1.py" ]; then
    echo "✅ smart_interaction_ws_v1_1.py"
else
    echo "❌ 缺少 smart_interaction_ws_v1_1.py"
    exit 1
fi

echo ""
echo "检查 Python 语法..."

source venv/bin/activate

if python3 -m py_compile monthly_report_bot_ws_v1.1.py 2>/dev/null; then
    echo "✅ monthly_report_bot_ws_v1.1.py 语法检查通过"
else
    echo "❌ monthly_report_bot_ws_v1.1.py 语法错误"
    exit 1
fi

echo ""
echo "========================================================================"
echo "更新 systemd 服务配置为 v1.1"
echo "========================================================================"

# 更新 systemd service 文件指向 v1.1
sudo bash -c 'cat > /etc/systemd/system/monthly-report-bot.service << EOL
[Unit]
Description=Monthly Report Bot v1.1
After=network.target

[Service]
Type=simple
User=hdi918072
WorkingDirectory=/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack
Environment=PATH=/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/venv/bin
ExecStart=/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/venv/bin/python3 /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot_ws_v1.1.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL'

echo "✅ Systemd 服务配置已更新为 v1.1"
echo ""

# 重新加载 systemd
sudo systemctl daemon-reload

echo "========================================================================"
echo "启动 v1.1 服务"
echo "========================================================================"

sudo systemctl start monthly-report-bot
sleep 5

if sudo systemctl is-active --quiet monthly-report-bot; then
    echo "✅ v1.1 服务已成功启动并运行中"
    echo ""
    echo "服务状态:"
    sudo systemctl status monthly-report-bot --no-pager | head -15
else
    echo "❌ v1.1 服务启动失败"
    echo ""
    echo "查看错误日志:"
    sudo journalctl -u monthly-report-bot -n 50 --no-pager
    exit 1
fi

echo ""
echo "========================================================================"
echo "✅ v1.1 部署完成！"
echo "========================================================================"
echo ""
echo "部署信息:"
echo "  版本: v1.1 (WebSocket 长连接版)"
echo "  主程序: monthly_report_bot_ws_v1.1.py"
echo "  部署时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "Git 信息:"
git log -1 --pretty=format:"  提交: %h%n  作者: %an%n  日期: %ad%n  说明: %s%n" --date=format:"%Y-%m-%d %H:%M:%S"
echo ""
echo "备份位置:"
echo "  $BACKUP_DIR/backup_before_v1.1_$TIMESTAMP"
echo ""
echo "========================================================================"
```

---

## 🔍 验证部署

### 1. 检查服务状态

```bash
sudo systemctl status monthly-report-bot
```

应该看到：
```
● monthly-report-bot.service - Monthly Report Bot v1.1
   Loaded: loaded (/etc/systemd/system/monthly-report-bot.service; enabled)
   Active: active (running) since ...
```

### 2. 查看实时日志

```bash
# 服务日志
sudo journalctl -u monthly-report-bot -f

# 或查看文件日志（如果配置了）
tail -f ~/monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot.log
```

应该看到：
```
✅ WebSocket 连接已建立
✅ 心跳正常
✅ 用户消息处理器已注册
```

### 3. 测试功能

在飞书群里发送消息：
```
@月报机器人 帮助
```

应该收到机器人回复，显示可用命令。

---

## 🧪 功能测试清单

### 测试 1: 智能交互
- [ ] 在群里 @机器人 发送 "帮助" → 收到帮助信息
- [ ] 在群里 @机器人 发送 "我的任务" → 收到任务清单
- [ ] 在群里 @机器人 发送 "进度" → 收到进度图表
- [ ] 在群里 @机器人 发送 "已完成" → 任务状态更新

### 测试 2: WebSocket 连接
- [ ] 查看日志确认 WebSocket 连接成功
- [ ] 查看日志确认心跳正常（每30秒）

### 测试 3: 定时任务（可选，需等待对应时间）
- [ ] 17日 09:00 → 创建月报任务
- [ ] 18-23日 09:00 → 发送每日提醒
- [ ] 18-22日 17:00 → 发送进度图表
- [ ] 23日 17:00 → 发送最终催办

---

## 🔄 回滚步骤

如果 v1.1 出现问题，需要回滚到之前版本：

```bash
# 1. 停止 v1.1 服务
sudo systemctl stop monthly-report-bot

# 2. 查看可用备份
ls -lht ~/monthly-report-bot-backups/

# 3. 回滚到备份（替换时间戳）
cd ~/monthly-report-bot
rm -rf monthly_report_bot_link_pack
cp -r ~/monthly-report-bot-backups/backup_before_v1.1_YYYYMMDD_HHMMSS \
      monthly_report_bot_link_pack

# 4. 恢复 systemd 服务配置（回到之前版本）
sudo bash -c 'cat > /etc/systemd/system/monthly-report-bot.service << EOL
[Unit]
Description=Monthly Report Bot (Final Interactive)
After=network.target

[Service]
Type=simple
User=hdi918072
WorkingDirectory=/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack
Environment=PATH=/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/venv/bin
ExecStart=/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/venv/bin/python3 /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot_final_interactive.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL'

# 5. 重新加载并启动
sudo systemctl daemon-reload
sudo systemctl start monthly-report-bot

# 6. 检查状态
sudo systemctl status monthly-report-bot
```

---

## 📊 部署后监控

### 实时监控

```bash
# 方法 1: 实时日志
sudo journalctl -u monthly-report-bot -f

# 方法 2: 服务状态
watch -n 5 'sudo systemctl status monthly-report-bot'
```

### 关键指标

监控以下内容：
- ✅ WebSocket 连接状态
- ✅ 心跳间隔（应为 30 秒）
- ✅ 消息处理成功率
- ✅ 内存使用情况
- ✅ CPU 使用情况

---

## ❗ 故障排查

### 问题 1: 服务启动失败

```bash
# 查看详细日志
sudo journalctl -u monthly-report-bot -n 100 --no-pager

# 检查文件权限
ls -la ~/monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot_ws_v1.1.py

# 手动测试运行
cd ~/monthly-report-bot/monthly_report_bot_link_pack
source venv/bin/activate
python3 monthly_report_bot_ws_v1.1.py
```

### 问题 2: WebSocket 连接失败

```bash
# 检查网络连接
curl -I https://open.feishu.cn

# 检查环境变量
cd ~/monthly-report-bot/monthly_report_bot_link_pack
cat .env | grep -E "APP_ID|APP_SECRET"

# 查看 WebSocket 日志
sudo journalctl -u monthly-report-bot -n 50 --no-pager | grep -i websocket
```

### 问题 3: 交互功能无响应

```bash
# 检查消息处理器是否注册
sudo journalctl -u monthly-report-bot -n 200 --no-pager | grep "用户消息处理器"

# 应该看到:
# ✅ 用户消息处理器已注册

# 检查智能交互引擎
sudo journalctl -u monthly-report-bot -n 200 --no-pager | grep "智能交互"
```

### 问题 4: 定时任务未执行

```bash
# 检查系统时区
timedatectl

# 应该显示: Time zone: America/Argentina/Buenos_Aires

# 查看调度日志
sudo journalctl -u monthly-report-bot -n 200 --no-pager | grep "should_"
```

---

## 🎉 部署成功标志

- ✅ Git 拉取成功，代码为最新版本
- ✅ v1.1 核心文件验证通过（4个文件）
- ✅ Python 语法检查通过
- ✅ Systemd 服务配置更新成功
- ✅ v1.1 服务启动成功并运行中
- ✅ WebSocket 连接建立成功
- ✅ 心跳正常
- ✅ 用户消息处理器注册成功
- ✅ @机器人交互测试通过

---

## 📚 相关文档

- [V1_1_IMPLEMENTATION_SUMMARY.md](V1_1_IMPLEMENTATION_SUMMARY.md) - v1.1 实现总结
- [V1_1_DEPLOYMENT_GUIDE.md](V1_1_DEPLOYMENT_GUIDE.md) - v1.1 部署指南
- [V1_1_INTERACTION_IMPLEMENTATION.md](V1_1_INTERACTION_IMPLEMENTATION.md) - 交互功能实现
- [月报机器人需求说明书_WS长连接版_v1.1.md](月报机器人需求说明书_WS长连接版_v1.1.md) - 需求文档
- GitHub 仓库: https://github.com/chaochaoying-ui/monthly-report-bot

---

## 📞 版本信息

- **版本**: v1.1 (WebSocket 长连接版)
- **部署日期**: 2025-10-21
- **主要特性**: WebSocket、智能交互、完整用户交互、分专业统计
- **开发人员**: Claude Code Assistant
- **测试状态**: ✅ 已通过完整测试

---

## 🔐 安全提醒

1. **环境变量保护**: 确保 `.env` 文件权限为 600
   ```bash
   chmod 600 ~/monthly-report-bot/monthly_report_bot_link_pack/.env
   ```

2. **备份定期清理**: 定期清理旧备份以节省空间
   ```bash
   # 保留最近 5 个备份，删除其他
   cd ~/monthly-report-bot-backups
   ls -t | tail -n +6 | xargs rm -rf
   ```

3. **日志轮转**: 配置日志轮转避免磁盘占满
   ```bash
   sudo journalctl --vacuum-time=7d
   ```

---

**现在就开始部署 v1.1 吧！4 步完成，预计 10 分钟！** 🚀
