# HTTP回调服务器配置指南

## 🎯 概述

我们已经成功实现了HTTP回调服务器来处理新成员欢迎功能。现在需要配置飞书后台来使用这个服务器。

## ✅ 当前状态

- ✅ HTTP回调服务器已启动（端口8080）
- ✅ 模板卡片发送功能正常（使用template格式）
- ✅ 支持用户和机器人加入事件
- ✅ 签名验证已配置（测试模式）
- ✅ 所有功能测试通过

## 📋 飞书后台配置步骤

### 1. 获取公网IP地址

首先需要获取您的公网IP地址，让飞书能够访问您的服务器：

```bash
# Windows
curl ifconfig.me

# 或者访问网站
# https://whatismyipaddress.com/
```

### 2. 配置端口转发

如果您的服务器在内网，需要配置端口转发：
- 外部端口：8080
- 内部IP：您的服务器IP
- 内部端口：8080

### 3. 飞书后台配置

1. **登录飞书开放平台**
   - 访问：https://open.feishu.cn/
   - 选择您的应用：`cli_a8fd44a9453cd00c`

2. **配置事件订阅**
   - 进入：应用功能 → 事件订阅
   - 选择：**HTTP回调**（不是长连接）

3. **设置回调URL**
   ```
   http://您的公网IP:8080/webhook
   ```
   例如：
   ```
   http://190.210.214.21:8080/webhook
   ```

4. **订阅事件**
   勾选以下事件：
   - ✅ `im.chat.member.user.added_v1`（用户加入群聊）
   - ✅ `im.chat.member.bot.added_v1`（机器人加入群聊）

5. **设置验证令牌**
   - 在验证令牌字段中输入：`test_token`
   - 这个值需要与服务器中的`VERIFICATION_TOKEN`环境变量一致

6. **保存配置**
   - 点击"保存"按钮
   - 系统会自动进行URL验证

## 🧪 测试步骤

### 1. 启动服务器

```bash
# 方法1：使用批处理文件
.\start_http_callback.bat

# 方法2：直接运行
$env:APP_ID="cli_a8fd44a9453cd00c"
$env:APP_SECRET="jsVoFWgaaw05en6418h7xbhV5oXxAwIm"
$env:WELCOME_CARD_ID="AAqInYqWzIiu6"
$env:VERIFICATION_TOKEN="test_token"
python simple_http_callback.py
```

### 2. 测试服务器

```bash
# 测试健康检查
curl http://localhost:8080/health

# 测试webhook
python test_http_callback.py
```

### 3. 测试新成员加入

1. **邀请用户进群**
   - 在飞书群聊中邀请一个新用户
   - 观察是否收到欢迎卡片

2. **邀请机器人进群**
   - 在飞书群聊中邀请另一个机器人
   - 观察服务器日志

## 📊 监控和日志

### 查看服务器日志

服务器运行时会显示详细的日志信息：
- 事件接收日志
- 欢迎卡片发送状态
- 错误信息

### 健康检查

```bash
curl http://localhost:8080/health
```

响应示例：
```json
{
  "status": "ok",
  "timestamp": 1755894774.208
}
```

## 🔧 故障排除

### 常见问题

1. **401错误**
   - 检查`VERIFICATION_TOKEN`是否一致
   - 确认签名验证配置

2. **连接超时**
   - 检查防火墙设置
   - 确认端口转发配置
   - 验证公网IP地址

3. **欢迎卡片发送失败**
   - 检查`APP_ID`和`APP_SECRET`
   - 确认应用权限配置
   - 查看飞书API错误信息

### 调试命令

```bash
# 检查端口是否开放
netstat -an | findstr :8080

# 测试网络连接
telnet 您的公网IP 8080

# 查看服务器进程
tasklist | findstr python
```

## 📝 环境变量配置

确保以下环境变量正确设置：

```bash
APP_ID=cli_a8fd44a9453cd00c
APP_SECRET=jsVoFWgaaw05en6418h7xbhV5oXxAwIm
WELCOME_CARD_ID=AAqInYqWzIiu6
VERIFICATION_TOKEN=test_token
```

## 🎉 成功标志

当配置成功后，您应该看到：

1. ✅ 飞书后台URL验证成功
2. ✅ 服务器日志显示事件接收
3. ✅ 新成员加入时自动发送欢迎卡片
4. ✅ 健康检查返回正常状态

## 📞 技术支持

如果遇到问题，请检查：
1. 服务器日志输出
2. 飞书后台错误信息
3. 网络连接状态
4. 环境变量配置

---

**注意**：此配置完成后，每当有新成员（用户或机器人）加入群聊时，系统会自动发送欢迎卡片！
