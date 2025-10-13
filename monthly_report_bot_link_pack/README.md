# 月报机器人 v1.1 - WS长连接版

基于需求说明书实现的专业级月报管理助手，采用WebSocket长连接技术和智能交互引擎。

## ✨ 核心特性

### 🔗 WebSocket长连接回调
- 仅使用WebSocket回调，更稳定可靠
- 自动重连机制，支持断线重连
- 心跳保活，确保连接稳定
- 事件去重，避免重复处理

### 🧠 智能交互引擎
- 多语言支持（中文、英文、西班牙语）
- 智能意图识别和实体提取
- 卡片式交互回调
- 权限控制和用户画像

### 👥 新成员欢迎功能
- 🆕 **自动欢迎新成员**：新成员进群时自动发送欢迎卡片
- 📋 **预定义卡片**：使用卡片ID `AAqInYqWzIiu6` 发送欢迎内容
- ⚡ **实时响应**：通过WebSocket长连接实时监听成员变更事件

### 📋 群级配置管理
- 支持不同群组的个性化配置
- 时区、推送时间、文件链接独立设置
- 动态配置加载和更新

### 🎨 专业级卡片设计
- 标准化交互卡片模板
- 多语言本地化支持
- 响应式设计适配各种客户端

### ⚙️ 幂等性与补跑机制
- 任务创建幂等性保证
- 服务恢复后自动补跑遗漏任务
- 状态持久化和恢复

## 📁 项目结构

```
monthly_report_bot_link_pack/
├── monthly_report_bot_ws_v1.1.py      # 主程序
├── websocket_handler_v1_1.py          # WebSocket处理器
├── smart_interaction_ws_v1_1.py       # 智能交互引擎
├── card_design_ws_v1_1.py             # 卡片设计模块
├── start_bot_v1_1.bat                 # Windows启动脚本
├── test_bot_v1_1.py                   # 测试套件
├── requirements_v1_1.txt              # 依赖文件
├── tasks.yaml                         # 任务配置
├── DEPLOYMENT_GUIDE_V1_1.md           # 部署指南
├── ADJUSTMENT_SUMMARY_V1_1.md         # 调整总结
└── 月报机器人需求说明书_WS长连接版_v1.1.md  # 需求文档
```

## 🚀 快速启动

### 1. 安装依赖
```bash
pip install -r requirements_v1_1.txt
```

### 2. 配置环境变量
```bash
# Windows (PowerShell)
$env:APP_ID = "cli_your_app_id"
$env:APP_SECRET = "your_app_secret"
$env:CHAT_ID = "oc_your_chat_id"
$env:FILE_URL = "https://your_file_url"
$env:WELCOME_CARD_ID = "AAqInYqWzIiu6"

# Linux/macOS
export APP_ID="cli_your_app_id"
export APP_SECRET="your_app_secret"
export CHAT_ID="oc_your_chat_id"
export FILE_URL="https://your_file_url"
export WELCOME_CARD_ID="AAqInYqWzIiu6"
```

### 3. 启动机器人
```bash
# Windows
start_bot_v1_1.bat

# Linux/macOS
python monthly_report_bot_ws_v1.1.py
```

## 🔧 环境变量说明

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `APP_ID` | 飞书应用ID | `YOUR_APP_ID` |
| `APP_SECRET` | 飞书应用密钥 | `jsVoFWgaaw05en6418h7xbhV5oXxAwIm` |
| `CHAT_ID` | 群聊ID | `oc_07f2d3d314f00fc29baf323a3a589972` |
| `FILE_URL` | 月报文件链接 | `https://be9bhmcgo2.feishu.cn/file/...` |
| `WELCOME_CARD_ID` | 欢迎卡片ID | `AAqInYqWzIiu6` |
| `TZ` | 时区 | `America/Argentina/Buenos_Aires` |
| `WS_ENDPOINT` | WebSocket端点 | `wss://open.feishu.cn/ws/v2` |
| `ENABLE_NLU` | 启用智能交互 | `true` |

## 📅 定时任务

- **17-19日 09:30**: 创建当月任务
- **18-22日 09:31**: 发送月报任务卡片
- **23日 09:32**: 发送最终提醒卡片

## 👥 新成员欢迎流程

1. **监听事件**: WebSocket长连接监听 `im.chat.member.user.added_v1` 事件
2. **获取用户**: 提取新加入的用户列表
3. **发送欢迎**: 向每个新用户发送预定义的欢迎卡片 (`AAqInYqWzIiu6`)
4. **记录日志**: 记录发送成功/失败状态

## 🧪 测试验证

运行测试套件验证功能：
```bash
python test_bot_v1_1.py
```

测试覆盖：
- ✅ 环境变量配置
- ✅ 智能交互引擎
- ✅ 卡片设计模块
- ✅ WebSocket处理器
- ✅ **新成员欢迎功能**
- ✅ 配置文件检查
- ✅ API连接测试

## 🎯 运行模式

启动脚本提供4种运行模式：

1. **完整模式**: 主程序 + WebSocket服务（推荐）
2. **仅主程序**: 定时任务功能
3. **仅WebSocket服务**: 事件处理功能
4. **测试模式**: 验证配置和连接

## 📖 更多文档

- [部署指南](DEPLOYMENT_GUIDE_V1_1.md)
- [调整总结](ADJUSTMENT_SUMMARY_V1_1.md)
- [需求说明书](月报机器人需求说明书_WS长连接版_v1.1.md)

## 🆕 新功能亮点

### 新成员欢迎卡片
当有新成员加入群聊时，机器人会：
1. 实时检测到成员变更事件
2. 自动向新成员发送个性化欢迎卡片
3. 提供月报流程介绍和使用指南
4. 记录欢迎卡片发送状态

这个功能通过WebSocket长连接实现，确保新成员能够及时了解月报流程，提升团队协作效率。

---

**月报机器人 v1.1** - 让月报管理更智能、更高效！ 🚀