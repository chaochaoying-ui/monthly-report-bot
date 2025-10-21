# 从当前版本迁移到 v1.1 指南

> 详细的迁移步骤，确保平滑升级到 v1.1 版本

## 📋 迁移概览

### 为什么要升级到 v1.1？

1. **更准确的调度时间**
   - 任务创建：17日 09:00（原：17-19日）
   - 每日提醒：18-23日 09:00（原：18-22日 09:31）
   - 新增进度图表：18-22日 17:00
   - 最终提醒：23日 17:00（原：23日 09:32）

2. **新增功能**
   - ✅ 智能交互引擎（多语言支持）
   - ✅ 进度图表可视化
   - ✅ 群级配置管理
   - ✅ 完整的幂等性和补跑机制
   - ✅ WebSocket 长连接（移除 HTTP 回调）

3. **改进的架构**
   - 模块化设计
   - 更好的错误处理
   - 完整的日志记录
   - 性能优化

### 迁移风险评估

| 风险项 | 等级 | 缓解措施 |
|--------|------|---------|
| 数据丢失 | 低 | 完整备份，数据格式兼容 |
| 服务中断 | 中 | 计划维护窗口，快速回滚方案 |
| 功能不兼容 | 低 | 全面测试，保留旧版本 |
| 配置错误 | 中 | 配置验证，文档详细 |

**建议迁移时间**: 非工作时间（如周末或晚上）

---

## 🔍 迁移前检查

### 1. 确认当前版本

```bash
# 检查当前运行的版本
ps aux | grep monthly_report_bot

# 查看日志确认版本
head -n 20 monthly_report_bot.log | grep VERSION
```

### 2. 记录当前配置

```bash
# 导出当前环境变量
env | grep -E 'APP_ID|APP_SECRET|CHAT_ID|FILE_URL|TZ' > current_env.txt

# 备份配置文件
cat .env > .env.backup
```

### 3. 检查数据文件

```bash
# 列出所有数据文件
ls -lh task_stats.json created_tasks.json tasks.yaml

# 检查数据完整性
python3 << 'EOF'
import json
import yaml

# 检查 JSON 文件
with open('task_stats.json', 'r') as f:
    stats = json.load(f)
    print(f"任务统计: {stats.get('total_tasks', 0)} 个任务")

with open('created_tasks.json', 'r') as f:
    created = json.load(f)
    print(f"已创建任务记录: {len(created)} 条")

# 检查 YAML 文件
with open('tasks.yaml', 'r') as f:
    tasks = yaml.safe_load(f)
    print(f"任务模板: {len(tasks.get('tasks', []))} 个模板")
EOF
```

### 4. 测试环境准备

```bash
# 确保有足够的磁盘空间（至少 500MB）
df -h .

# 确保有足够的内存（至少 512MB 可用）
free -m

# 检查 Python 版本（需要 3.9+）
python3 --version
```

---

## 📦 步骤1: 备份现有系统

### 完整备份

```bash
# 创建备份目录
mkdir -p ~/monthly_report_bot_backup_$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=~/monthly_report_bot_backup_$(date +%Y%m%d_%H%M%S)

# 备份数据文件
cp task_stats.json $BACKUP_DIR/
cp created_tasks.json $BACKUP_DIR/
cp tasks.yaml $BACKUP_DIR/
cp .env $BACKUP_DIR/

# 备份日志文件
cp monthly_report_bot.log $BACKUP_DIR/

# 备份当前代码
cp monthly_report_bot_final_interactive.py $BACKUP_DIR/

# 创建备份清单
cat > $BACKUP_DIR/BACKUP_INFO.txt << EOF
备份时间: $(date)
备份目录: $BACKUP_DIR
原始路径: $(pwd)
Python版本: $(python3 --version)
系统信息: $(uname -a)
EOF

echo "✅ 备份完成: $BACKUP_DIR"
```

### 验证备份

```bash
# 检查备份文件
ls -lh $BACKUP_DIR

# 验证 JSON 文件可读
python3 -m json.tool $BACKUP_DIR/task_stats.json > /dev/null && echo "✅ task_stats.json 备份完整"
python3 -m json.tool $BACKUP_DIR/created_tasks.json > /dev/null && echo "✅ created_tasks.json 备份完整"
```

---

## 🛑 步骤2: 停止当前服务

### 方法1: 使用 systemd（推荐）

```bash
# 停止服务
sudo systemctl stop monthly-report-bot

# 确认服务已停止
sudo systemctl status monthly-report-bot

# 如果服务没有正确停止，强制停止
sudo systemctl kill monthly-report-bot
```

### 方法2: 手动停止进程

```bash
# 查找进程
ps aux | grep monthly_report_bot

# 停止进程（使用进程ID）
kill <PID>

# 如果无法停止，强制终止
kill -9 <PID>

# 验证进程已停止
ps aux | grep monthly_report_bot
```

### 确认停止成功

```bash
# 确保没有相关进程在运行
pgrep -f monthly_report_bot || echo "✅ 服务已完全停止"

# 检查端口占用（如果有HTTP服务）
sudo netstat -tlnp | grep python3 || echo "✅ 端口已释放"
```

---

## 📥 步骤3: 获取 v1.1 代码

### 从 GitHub 更新

```bash
# 进入项目目录
cd /opt/monthly-report-bot  # 或你的实际路径

# 保存本地修改（如果有）
git stash

# 拉取最新代码
git fetch origin
git pull origin main

# 如果有冲突，解决后再继续
git stash pop  # 恢复本地修改（可选）

# 验证 v1.1 文件存在
ls -l monthly_report_bot_link_pack/monthly_report_bot_link_pack/monthly_report_bot_ws_v1.1.py
ls -l monthly_report_bot_link_pack/monthly_report_bot_link_pack/smart_interaction_ws_v1_1.py
ls -l monthly_report_bot_link_pack/monthly_report_bot_link_pack/card_design_ws_v1_1.py
ls -l monthly_report_bot_link_pack/monthly_report_bot_link_pack/websocket_handler_v1_1.py
```

### 手动下载（备选方案）

```bash
# 下载 v1.1 文件
cd monthly_report_bot_link_pack/monthly_report_bot_link_pack

# 下载主文件
curl -O https://raw.githubusercontent.com/chaochaoying-ui/monthly-report-bot/main/monthly_report_bot_link_pack/monthly_report_bot_link_pack/monthly_report_bot_ws_v1.1.py

# 下载模块文件
curl -O https://raw.githubusercontent.com/chaochaoying-ui/monthly-report-bot/main/monthly_report_bot_link_pack/monthly_report_bot_link_pack/smart_interaction_ws_v1_1.py
curl -O https://raw.githubusercontent.com/chaochaoying-ui/monthly-report-bot/main/monthly_report_bot_link_pack/monthly_report_bot_link_pack/card_design_ws_v1_1.py
curl -O https://raw.githubusercontent.com/chaochaoying-ui/monthly-report-bot/main/monthly_report_bot_link_pack/monthly_report_bot_link_pack/websocket_handler_v1_1.py

# 下载测试文件
curl -O https://raw.githubusercontent.com/chaochaoying-ui/monthly-report-bot/main/monthly_report_bot_link_pack/monthly_report_bot_link_pack/test_bot_v1_1.py
```

---

## 🔧 步骤4: 安装/更新依赖

### 检查依赖差异

```bash
# 查看新依赖
cat requirements_v1_1.txt

# 如果文件不存在，创建它
cat > requirements_v1_1.txt << 'EOF'
lark-oapi>=1.2.0
python-dotenv>=0.19.0
pyyaml>=6.0
pytz>=2021.3
requests>=2.26.0
matplotlib>=3.5.0
websockets>=10.0
EOF
```

### 安装依赖

```bash
# 激活虚拟环境（如果使用）
source venv/bin/activate

# 更新 pip
pip install --upgrade pip

# 安装新依赖
pip install -r requirements_v1_1.txt

# 验证安装
pip list | grep -E 'lark-oapi|websockets|matplotlib'
```

---

## ⚙️ 步骤5: 更新配置

### 更新 .env 文件

```bash
# 备份现有 .env
cp .env .env.old

# 添加 v1.1 新配置项
cat >> .env << 'EOF'

# ===== v1.1 新增配置 =====

# 智能交互配置
ENABLE_NLU=true
INTENT_THRESHOLD=0.75
LANGS=["zh","en","es"]

# WebSocket配置
WS_ENDPOINT=wss://open.feishu.cn/ws/v2
WS_HEARTBEAT_INTERVAL=30
WS_RECONNECT_MAX_ATTEMPTS=5

# 日志级别
LOG_LEVEL=INFO
EOF

echo "✅ 配置已更新"
```

### 验证配置

```bash
# 检查必需的环境变量
python3 << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

required = ['APP_ID', 'APP_SECRET', 'CHAT_ID', 'FILE_URL', 'TZ']
optional = ['ENABLE_NLU', 'INTENT_THRESHOLD', 'WS_ENDPOINT']

print("=== 必需配置 ===")
for var in required:
    value = os.getenv(var)
    status = "✅" if value else "❌"
    print(f"{status} {var}: {'已设置' if value else '未设置'}")

print("\n=== 可选配置（v1.1新增） ===")
for var in optional:
    value = os.getenv(var)
    status = "✅" if value else "⚠️"
    print(f"{status} {var}: {value if value else '使用默认值'}")
EOF
```

### 创建新数据文件

```bash
# 创建群级配置文件（如果不存在）
if [ ! -f group_config.json ]; then
    cat > group_config.json << 'EOF'
{
  "push_time": "09:00",
  "file_url": "",
  "timezone": "America/Argentina/Buenos_Aires",
  "created_tasks": {}
}
EOF
    echo "✅ 创建 group_config.json"
fi

# 创建交互日志文件（如果不存在）
if [ ! -f interaction_log.json ]; then
    echo '{"interactions": []}' > interaction_log.json
    echo "✅ 创建 interaction_log.json"
fi
```

---

## 🧪 步骤6: 测试 v1.1 版本

### 运行测试脚本

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行全面测试
python test_bot_v1_1.py

# 预期输出：
# ✅ 环境变量测试通过
# ✅ 智能交互引擎测试通过
# ✅ 卡片设计测试通过
# ✅ WebSocket 连接测试通过
```

### 手动验证

```bash
# 1. 验证导入
python3 << 'EOF'
try:
    from smart_interaction_ws_v1_1 import SmartInteractionEngine
    from card_design_ws_v1_1 import build_welcome_card, build_progress_chart_card
    from websocket_handler_v1_1 import FeishuWebSocketHandler
    print("✅ 所有模块导入成功")
except Exception as e:
    print(f"❌ 导入失败: {e}")
EOF

# 2. 测试配置加载
python3 << 'EOF'
import json
import os

# 测试加载配置
with open('group_config.json', 'r') as f:
    config = json.load(f)
    print(f"✅ 群级配置加载成功: {config.get('timezone', 'N/A')}")

# 测试任务统计
with open('task_stats.json', 'r') as f:
    stats = json.load(f)
    print(f"✅ 任务统计加载成功: {stats.get('total_tasks', 0)} 个任务")
EOF
```

---

## 🚀 步骤7: 更新 systemd 服务

### 创建新服务文件

```bash
# 创建 v1.1 服务文件
sudo tee /etc/systemd/system/monthly-report-bot-v1.1.service > /dev/null << EOF
[Unit]
Description=Monthly Report Bot v1.1
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
EnvironmentFile=$(pwd)/.env
ExecStart=$(pwd)/venv/bin/python monthly_report_bot_ws_v1.1.py
Restart=always
RestartSec=10
StandardOutput=append:$(pwd)/monthly_report_bot.log
StandardError=append:$(pwd)/monthly_report_bot.log

[Install]
WantedBy=multi-user.target
EOF

echo "✅ 服务文件已创建"
```

### 重新加载 systemd

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 验证服务文件
sudo systemctl cat monthly-report-bot-v1.1
```

---

## ✅ 步骤8: 启动 v1.1 服务

### 启动服务

```bash
# 启动 v1.1 服务
sudo systemctl start monthly-report-bot-v1.1

# 等待几秒钟
sleep 5

# 检查服务状态
sudo systemctl status monthly-report-bot-v1.1
```

### 验证运行

```bash
# 1. 检查进程
ps aux | grep monthly_report_bot_ws_v1.1

# 2. 查看实时日志
tail -f monthly_report_bot.log

# 3. 检查 WebSocket 连接
tail -f monthly_report_bot.log | grep -E "WebSocket|连接成功"

# 4. 使用 systemd 日志
sudo journalctl -u monthly-report-bot-v1.1 -f
```

### 验证关键功能

```bash
# 等待1-2分钟后检查
echo "正在验证关键功能..."

# 1. 检查 WebSocket 连接
if grep -q "WebSocket.*成功" monthly_report_bot.log; then
    echo "✅ WebSocket 连接成功"
else
    echo "❌ WebSocket 连接失败"
fi

# 2. 检查事件处理
if grep -q "事件处理" monthly_report_bot.log; then
    echo "✅ 事件处理正常"
else
    echo "⚠️  暂无事件处理（等待事件触发）"
fi

# 3. 检查错误
if grep -q "ERROR\|Exception" monthly_report_bot.log | tail -20; then
    echo "⚠️  发现错误，请查看日志"
else
    echo "✅ 无错误"
fi
```

---

## 🎯 步骤9: 功能验证

### 验证定时任务调度

```bash
# 查看调度逻辑
python3 << 'EOF'
from datetime import datetime
import pytz

TZ = pytz.timezone("America/Argentina/Buenos_Aires")
now = datetime.now(TZ)

print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"当前日期: {now.day}日")
print(f"当前时刻: {now.strftime('%H:%M')}")

print("\n=== 定时任务状态 ===")
print(f"创建任务 (17日 09:00): {'✅ 会执行' if now.day == 17 and now.strftime('%H:%M') == '09:00' else '❌ 不会执行'}")
print(f"每日提醒 (18-23日 09:00): {'✅ 会执行' if 18 <= now.day <= 23 and now.strftime('%H:%M') == '09:00' else '❌ 不会执行'}")
print(f"进度图表 (18-22日 17:00): {'✅ 会执行' if 18 <= now.day <= 22 and now.strftime('%H:%M') == '17:00' else '❌ 不会执行'}")
print(f"最终提醒 (23日 17:00): {'✅ 会执行' if now.day == 23 and now.strftime('%H:%M') == '17:00' else '❌ 不会执行'}")
EOF
```

### 测试智能交互（可选）

在飞书群聊中测试：

1. **测试欢迎卡片**
   - 添加一个新成员
   - 验证：≤3秒收到欢迎卡片

2. **测试智能交互**
   - 发送："我的任务"
   - 验证：收到私聊消息

3. **测试帮助命令**
   - 发送："帮助"
   - 验证：收到帮助信息

---

## 🔄 步骤10: 设置开机自启

```bash
# 启用开机自启
sudo systemctl enable monthly-report-bot-v1.1

# 验证
sudo systemctl is-enabled monthly-report-bot-v1.1

# 禁用旧版本开机自启（如果存在）
sudo systemctl disable monthly-report-bot 2>/dev/null || true
```

---

## 🔙 回滚方案

如果迁移后出现问题，可以快速回滚：

### 快速回滚

```bash
# 1. 停止 v1.1 服务
sudo systemctl stop monthly-report-bot-v1.1
sudo systemctl disable monthly-report-bot-v1.1

# 2. 恢复备份数据（如果需要）
BACKUP_DIR=~/monthly_report_bot_backup_<时间戳>  # 使用实际备份目录
cp $BACKUP_DIR/task_stats.json ./
cp $BACKUP_DIR/created_tasks.json ./
cp $BACKUP_DIR/.env ./

# 3. 启动旧版本服务
sudo systemctl start monthly-report-bot
sudo systemctl enable monthly-report-bot

# 4. 验证
sudo systemctl status monthly-report-bot
tail -f monthly_report_bot.log
```

### 验证回滚

```bash
# 确认旧版本运行
ps aux | grep monthly_report_bot_final_interactive.py

# 检查日志
tail -20 monthly_report_bot.log
```

---

## 📊 迁移后检查清单

### 立即检查（迁移后1小时内）

- [ ] ✅ v1.1 服务正常运行
- [ ] ✅ WebSocket 连接成功
- [ ] ✅ 日志无严重错误
- [ ] ✅ 内存使用正常（<200MB）
- [ ] ✅ CPU 使用正常（<5%）

### 短期检查（迁移后24小时内）

- [ ] ✅ 欢迎卡片功能正常（添加新成员测试）
- [ ] ✅ 智能交互功能正常（发送测试消息）
- [ ] ✅ 无频繁重启
- [ ] ✅ 无内存泄漏

### 长期检查（迁移后1周内）

- [ ] ✅ 定时任务按时执行
  - [ ] 17日 09:00 任务创建
  - [ ] 18-23日 09:00 每日提醒
  - [ ] 18-22日 17:00 进度图表
  - [ ] 23日 17:00 最终提醒
- [ ] ✅ 所有功能正常
- [ ] ✅ 性能稳定
- [ ] ✅ 用户反馈良好

---

## 🐛 常见迁移问题

### 问题1: 依赖安装失败

**症状**: `pip install` 失败

**解决**:
```bash
# 升级 pip
pip install --upgrade pip

# 使用清华镜像
pip install -r requirements_v1_1.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 逐个安装
pip install lark-oapi
pip install websockets
pip install matplotlib
```

### 问题2: WebSocket 连接失败

**症状**: 日志显示连接错误

**解决**:
```bash
# 检查网络
ping open.feishu.cn

# 验证凭证
echo $APP_ID
echo $APP_SECRET

# 检查防火墙
sudo ufw status

# 重启服务
sudo systemctl restart monthly-report-bot-v1.1
```

### 问题3: 导入模块失败

**症状**: `ModuleNotFoundError`

**解决**:
```bash
# 确保在正确的目录
pwd

# 检查文件存在
ls -l *_v1_1.py

# 验证 Python 路径
python3 -c "import sys; print('\n'.join(sys.path))"

# 重新安装依赖
pip install -r requirements_v1_1.txt --force-reinstall
```

### 问题4: 数据文件错误

**症状**: JSON 解析错误

**解决**:
```bash
# 验证 JSON 文件
python3 -m json.tool task_stats.json
python3 -m json.tool created_tasks.json

# 如果损坏，恢复备份
BACKUP_DIR=~/monthly_report_bot_backup_<时间戳>
cp $BACKUP_DIR/task_stats.json ./
cp $BACKUP_DIR/created_tasks.json ./
```

---

## 📝 迁移记录模板

记录您的迁移过程：

```bash
cat > migration_record_$(date +%Y%m%d).txt << 'EOF'
===== 月报机器人 v1.1 迁移记录 =====

迁移日期: <填写>
操作人员: <填写>
迁移环境: <生产/测试>

=== 迁移前状态 ===
旧版本: <填写>
服务状态: <运行中/已停止>
数据完整性: <完整/部分丢失>

=== 迁移步骤 ===
[ ] 1. 备份完成
[ ] 2. 服务停止
[ ] 3. 代码更新
[ ] 4. 依赖安装
[ ] 5. 配置更新
[ ] 6. 测试通过
[ ] 7. 服务启动
[ ] 8. 功能验证
[ ] 9. 开机自启设置

=== 遇到的问题 ===
<记录问题和解决方案>

=== 迁移后状态 ===
v1.1 状态: <正常/异常>
功能验证: <通过/失败>
性能指标: <正常/异常>

=== 备注 ===
<其他需要记录的信息>

迁移完成时间: <填写>
验证人员: <填写>
EOF
```

---

## ✅ 迁移完成

恭喜！您已成功迁移到 v1.1 版本。

### 下一步

1. **监控运行**: 持续监控服务状态和日志
2. **收集反馈**: 收集用户反馈，及时优化
3. **文档更新**: 更新内部文档和操作手册
4. **培训用户**: 向用户介绍新功能（智能交互、多语言等）

### 相关文档

- [v1.1 实现总结](V1_1_IMPLEMENTATION_SUMMARY.md)
- [v1.1 部署指南](V1_1_DEPLOYMENT_GUIDE.md)
- [完整功能文档](月报机器人完整功能文档.md)

---

**迁移指南版本**: v1.0
**最后更新**: 2025-10-21
