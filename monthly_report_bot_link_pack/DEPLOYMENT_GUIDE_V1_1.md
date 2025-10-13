# 月报机器人 v1.1 部署指南

> 基于需求说明书 v1.1 实现，支持 WebSocket 长连接、智能交互、群级配置等功能

## 📋 目录

- [1. 系统要求](#1-系统要求)
- [2. 环境准备](#2-环境准备)
- [3. 安装部署](#3-安装部署)
- [4. 配置说明](#4-配置说明)
- [5. 启动运行](#5-启动运行)
- [6. 监控告警](#6-监控告警)
- [7. 故障排查](#7-故障排查)
- [8. 升级回退](#8-升级回退)

---

## 1. 系统要求

### 1.1 硬件要求
- **CPU**: 2核心以上
- **内存**: 4GB以上
- **存储**: 10GB可用空间
- **网络**: 稳定的互联网连接

### 1.2 软件要求
- **操作系统**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+
- **Python**: 3.8+
- **数据库**: 无需（使用文件存储）
- **Web服务器**: 无需（内置WebSocket服务）

### 1.3 网络要求
- **出站连接**: 飞书API (open.feishu.cn)
- **入站连接**: WebSocket端口 (8080)
- **防火墙**: 开放8080端口

---

## 2. 环境准备

### 2.1 安装Python环境

```bash
# Windows
# 下载并安装Python 3.8+ from https://www.python.org/

# Linux (Ubuntu)
sudo apt update
sudo apt install python3 python3-pip python3-venv

# macOS
brew install python3
```

### 2.2 创建虚拟环境

```bash
# 创建项目目录
mkdir monthly_report_bot_v1_1
cd monthly_report_bot_v1_1

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 2.3 安装依赖

```bash
# 安装依赖包
pip install -r requirements_v1_1.txt

# 验证安装
python -c "import requests, yaml, pytz, websockets; print('依赖安装成功')"
```

---

## 3. 安装部署

### 3.1 下载代码

```bash
# 克隆或下载项目文件
# 确保包含以下文件：
# - monthly_report_bot_ws_v1.1.py
# - smart_interaction_ws_v1_1.py
# - card_design_ws_v1_1.py
# - websocket_handler_v1_1.py
# - tasks.yaml
# - requirements_v1_1.txt
# - start_bot_v1_1.bat (Windows)
# - start_bot_v1_1.sh (Linux/macOS)
```

### 3.2 文件结构

```
monthly_report_bot_v1_1/
├── monthly_report_bot_ws_v1.1.py      # 主程序
├── smart_interaction_ws_v1_1.py       # 智能交互引擎
├── card_design_ws_v1_1.py             # 卡片设计模块
├── websocket_handler_v1_1.py          # WebSocket处理器
├── test_bot_v1_1.py                   # 测试脚本
├── tasks.yaml                          # 任务配置
├── requirements_v1_1.txt               # 依赖文件
├── start_bot_v1_1.bat                 # Windows启动脚本
├── start_bot_v1_1.sh                  # Linux/macOS启动脚本
├── config/                             # 配置目录
│   ├── group_config.json              # 群级配置
│   ├── created_tasks.json             # 已创建任务记录
│   └── interaction_log.json           # 交互日志
└── logs/                               # 日志目录
    └── monthly_report_bot.log         # 运行日志
```

---

## 4. 配置说明

### 4.1 环境变量配置

创建 `.env` 文件或设置系统环境变量：

```bash
# 飞书应用配置
APP_ID=cli_a8fd44a9453cd00c
APP_SECRET=jsVoFWgaaw05en6418h7xbhV5oXxAwIm
CHAT_ID=oc_07f2d3d314f00fc29baf323a3a589972
FILE_URL=https://be9bhmcgo2.feishu.cn/file/Wn5AbQAmVo32OExC5zIcIiAXnKc?office_edit=1
TZ=America/Argentina/Buenos_Aires
VERIFICATION_TOKEN=your_verification_token_here

# WebSocket配置
WS_ENDPOINT=wss://open.feishu.cn/ws/v2
WS_HEARTBEAT_INTERVAL=30
WS_RECONNECT_MAX_ATTEMPTS=5

# 智能交互配置
ENABLE_NLU=true
INTENT_THRESHOLD=0.75
LANGS=["zh","en","es"]

# 日志与监控
LOG_LEVEL=INFO
METRICS_ENDPOINT=http://localhost:9090/metrics
```

### 4.2 任务配置 (tasks.yaml)

```yaml
- title: 月报-工程计划及执行情况
  assignee_open_id: ou_b96c7ed4a604dc049569102d01c6c26d
  desc: 工程计划及执行情况描述
  due: "23 17:00"
  collaborators: []

- title: 月报-设计工作进展
  assignee_open_id: ou_07443a67428d8741eab5eac851b754b9
  desc: 设计工作进展描述
  due: "23 17:00"
  collaborators: []
```

### 4.3 群级配置 (group_config.json)

```json
{
  "push_time": "09:30",
  "file_url": "https://be9bhmcgo2.feishu.cn/file/Wn5AbQAmVo32OExC5zIcIiAXnKc?office_edit=1",
  "timezone": "America/Argentina/Buenos_Aires",
  "created_tasks": {}
}
```

---

## 5. 启动运行

### 5.1 Windows 启动

```bash
# 使用批处理脚本
start_bot_v1_1.bat

# 或直接运行
python monthly_report_bot_ws_v1.1.py
```

### 5.2 Linux/macOS 启动

```bash
# 使用Shell脚本
chmod +x start_bot_v1_1.sh
./start_bot_v1_1.sh

# 或直接运行
python3 monthly_report_bot_ws_v1.1.py
```

### 5.3 运行模式选择

启动脚本提供4种运行模式：

1. **完整模式**: 主程序 + WebSocket服务 + 智能交互
2. **仅主程序**: 定时任务创建、卡片推送、最终提醒
3. **仅WebSocket服务**: 事件处理、智能交互、卡片回调
4. **测试模式**: 验证配置、测试连接、模拟事件

### 5.4 后台运行

```bash
# Linux/macOS 后台运行
nohup python3 monthly_report_bot_ws_v1.1.py > bot.log 2>&1 &

# Windows 后台运行
start /B python monthly_report_bot_ws_v1.1.py > bot.log 2>&1
```

---

## 6. 监控告警

### 6.1 日志监控

```bash
# 查看实时日志
tail -f logs/monthly_report_bot.log

# 查看错误日志
grep "ERROR" logs/monthly_report_bot.log

# 查看WebSocket连接状态
grep "WebSocket" logs/monthly_report_bot.log
```

### 6.2 健康检查

```bash
# 运行健康检查
python test_bot_v1_1.py

# 检查关键指标
- WebSocket连接状态
- API调用成功率
- 任务创建成功率
- 卡片发送成功率
```

### 6.3 告警配置

根据需求文档7.4，配置以下告警：

```bash
# WS连续断开>3次告警
# 5xx连续>3次告警
# 任务创建失败告警
# 卡片发送失败告警
```

---

## 7. 故障排查

### 7.1 常见问题

#### 问题1: WebSocket连接失败
```bash
# 检查网络连接
ping open.feishu.cn

# 检查防火墙
netstat -an | grep 8080

# 检查应用配置
echo $APP_ID
echo $APP_SECRET
```

#### 问题2: 任务创建失败
```bash
# 检查tasks.yaml格式
python -c "import yaml; yaml.safe_load(open('tasks.yaml'))"

# 检查API权限
# 确认应用有任务管理权限
```

#### 问题3: 智能交互不工作
```bash
# 检查NLU配置
echo $ENABLE_NLU
echo $INTENT_THRESHOLD

# 测试意图识别
python -c "from smart_interaction_ws_v1_1 import SmartInteractionEngine; engine = SmartInteractionEngine(); print(engine.analyze_intent('我的任务', 'test_user'))"
```

### 7.2 日志分析

```bash
# 分析错误模式
grep "ERROR" logs/monthly_report_bot.log | awk '{print $4}' | sort | uniq -c

# 分析性能问题
grep "耗时" logs/monthly_report_bot.log

# 分析用户交互
grep "用户意图" logs/monthly_report_bot.log
```

### 7.3 性能优化

```bash
# 检查内存使用
ps aux | grep python

# 检查CPU使用
top -p $(pgrep -f monthly_report_bot)

# 优化建议
- 调整心跳间隔
- 优化日志级别
- 清理历史数据
```

---

## 8. 升级回退

### 8.1 升级流程

```bash
# 1. 备份当前版本
cp -r monthly_report_bot_v1_1 monthly_report_bot_v1_1_backup

# 2. 停止服务
pkill -f monthly_report_bot_ws_v1_1.py

# 3. 更新代码
# 下载新版本文件

# 4. 更新依赖
pip install -r requirements_v1_1.txt

# 5. 测试新版本
python test_bot_v1_1.py

# 6. 启动新版本
python monthly_report_bot_ws_v1_1.py
```

### 8.2 回退流程

```bash
# 1. 停止新版本
pkill -f monthly_report_bot_ws_v1_1.py

# 2. 恢复备份
rm -rf monthly_report_bot_v1_1
mv monthly_report_bot_v1_1_backup monthly_report_bot_v1_1

# 3. 启动旧版本
cd monthly_report_bot_v1_1
python monthly_report_bot_ws_v1_1.py
```

### 8.3 数据迁移

```bash
# 备份配置文件
cp config/group_config.json config/group_config.json.backup
cp config/created_tasks.json config/created_tasks.json.backup

# 迁移数据（如需要）
# 根据新版本的数据格式要求进行迁移
```

---

## 📞 技术支持

### 联系方式
- **文档**: 月报机器人需求说明书_WS长连接版_v1.1.md
- **测试**: python test_bot_v1_1.py
- **日志**: logs/monthly_report_bot.log

### 关键指标
- **WS可用性**: ≥ 99.9%
- **意图识别准确率**: ≥ 90%
- **按钮响应延迟**: ≤ 2s
- **服务恢复时间**: ≤ 5min

---

**版本**: v1.1  
**更新日期**: 2024年12月  
**维护者**: 开发团队

