# 群组切换指南

## 📋 概述

为了避免在正式群中测试功能时打扰群成员，我们提供了测试群和正式群的快速切换功能。

---

## 🎯 群组信息

| 群组类型 | 群组ID | 用途 |
|---------|--------|------|
| **测试群** | `oc_07f2d3d314f00fc29baf323a3a589972` | 功能测试、调试 |
| **正式群** | `oc_e4218b232326ea81a077b65c4cd16ce5` | 生产环境 |

---

## 🔄 切换到测试群

### 方法1: 使用脚本（推荐）

```bash
# SSH 登录服务器
ssh hdi918072@34.145.43.77

# 进入项目目录
cd /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack

# 执行切换脚本
bash switch_to_test_group.sh
```

### 方法2: 手动修改

```bash
# 1. 备份 .env 文件
cp .env .env.backup_$(date +%Y%m%d_%H%M%S)

# 2. 修改 CHAT_ID
# 如果已有 CHAT_ID 行，修改它
sed -i 's/^CHAT_ID=.*/CHAT_ID=oc_07f2d3d314f00fc29baf323a3a589972/' .env

# 或者手动编辑
nano .env
# 找到 CHAT_ID= 那一行，改为:
# CHAT_ID=oc_07f2d3d314f00fc29baf323a3a589972

# 3. 重启服务
sudo systemctl restart monthly-report-bot

# 4. 验证
sudo systemctl status monthly-report-bot
```

---

## 🏢 切换回正式群

⚠️ **重要**: 仅在完成所有测试后切换！

### 方法1: 使用脚本（推荐）

```bash
cd /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack
bash switch_to_prod_group.sh
# 会提示确认，输入 yes
```

### 方法2: 手动修改

```bash
# 1. 备份 .env 文件
cp .env .env.backup_$(date +%Y%m%d_%H%M%S)

# 2. 修改 CHAT_ID 为正式群
sed -i 's/^CHAT_ID=.*/CHAT_ID=oc_e4218b232326ea81a077b65c4cd16ce5/' .env

# 3. 重启服务
sudo systemctl restart monthly-report-bot

# 4. 验证
sudo systemctl status monthly-report-bot
```

---

## ✅ 验证切换结果

### 1. 检查环境变量

```bash
cd /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack

# 查看 .env 中的 CHAT_ID
grep "^CHAT_ID=" .env

# 应该显示:
# 测试群: CHAT_ID=oc_07f2d3d314f00fc29baf323a3a589972
# 正式群: CHAT_ID=oc_e4218b232326ea81a077b65c4cd16ce5
```

### 2. 查看服务日志

```bash
# 查看启动日志
sudo journalctl -u monthly-report-bot -n 50 | grep -i "chat"

# 或者查看完整日志
sudo journalctl -u monthly-report-bot -f
```

### 3. 在飞书群中测试

在**对应的群**中发送消息测试：

```
状态
```

机器人应该在正确的群中响应。

---

## 📝 当前环境检查

### 快速检查当前配置

```bash
cd /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack

echo "当前 CHAT_ID:"
grep "^CHAT_ID=" .env

echo ""
echo "服务状态:"
sudo systemctl is-active monthly-report-bot

echo ""
echo "最近日志:"
sudo journalctl -u monthly-report-bot -n 10 --no-pager
```

---

## 🔧 脚本说明

### switch_to_test_group.sh

**功能**:
- ✅ 自动备份 .env 文件
- ✅ 更新 CHAT_ID 为测试群
- ✅ 重启服务
- ✅ 显示服务状态和日志

**使用场景**:
- 开发新功能时
- 调试问题时
- 测试任务创建/同步时
- 避免打扰正式群成员

### switch_to_prod_group.sh

**功能**:
- ✅ 确认提示（防止误操作）
- ✅ 自动备份 .env 文件
- ✅ 更新 CHAT_ID 为正式群
- ✅ 重启服务
- ✅ 显示服务状态和日志

**使用场景**:
- 所有功能测试完成
- 准备部署到生产环境
- 开始正式使用

---

## 🚨 注意事项

### 测试群使用注意

1. ✅ **频繁测试**: 可以随意发送消息测试
2. ✅ **任务创建**: 可以删除 task_stats.json 重新创建
3. ✅ **调试日志**: 可以查看详细日志
4. ⚠️ **不要遗忘**: 测试完记得切换回正式群

### 正式群使用注意

1. ⚠️ **谨慎操作**: 避免频繁重启服务
2. ⚠️ **少发消息**: 不要发送过多测试消息
3. ⚠️ **任务数据**: 不要随意删除 task_stats.json
4. ⚠️ **验证充分**: 切换前确保在测试群中验证通过

---

## 📋 典型工作流程

### 开发/测试流程

```
1. 切换到测试群
   bash switch_to_test_group.sh

2. 在本地修改代码
   code monthly_report_bot_ws_v1.1.py

3. 提交并推送
   git add .
   git commit -m "feat: 新功能"
   git push origin main

4. 在服务器上更新
   cd /home/hdi918072/monthly-report-bot
   git pull origin main

5. 重启服务
   cd monthly_report_bot_link_pack
   sudo systemctl restart monthly-report-bot

6. 在测试群中验证
   发送: 状态
   发送: 图表
   等等...

7. 确认功能正常后，切换回正式群
   bash switch_to_prod_group.sh
```

### 紧急修复流程

```
1. 如果在正式群发现问题
   bash switch_to_test_group.sh

2. 在测试群中重现问题

3. 修复代码

4. 在测试群中验证修复

5. 确认无误后切换回正式群
   bash switch_to_prod_group.sh
```

---

## 🔍 故障排查

### 问题1: 切换后机器人不响应

**检查步骤**:

```bash
# 1. 确认服务运行
sudo systemctl status monthly-report-bot

# 2. 查看 CHAT_ID 是否正确
grep "^CHAT_ID=" .env

# 3. 查看日志
sudo journalctl -u monthly-report-bot -n 50

# 4. 重启服务
sudo systemctl restart monthly-report-bot
```

### 问题2: 在错误的群中响应

**原因**: CHAT_ID 配置错误或未生效

**解决**:

```bash
# 1. 检查 .env
cat .env | grep CHAT_ID

# 2. 重新运行切换脚本
bash switch_to_test_group.sh

# 3. 或手动修改并重启
nano .env  # 修改 CHAT_ID
sudo systemctl restart monthly-report-bot
```

### 问题3: 脚本执行失败

**可能原因**:
- 权限不足
- .env 文件不存在
- sed 命令语法问题

**解决**:

```bash
# 添加执行权限
chmod +x switch_to_test_group.sh
chmod +x switch_to_prod_group.sh

# 检查 .env 文件
ls -la .env

# 手动执行命令
sed -i 's/^CHAT_ID=.*/CHAT_ID=oc_07f2d3d314f00fc29baf323a3a589972/' .env
```

---

## 📚 相关文档

- [部署前检查清单](PRE_DEPLOY_CHECKLIST.md)
- [错题本](PITFALLS_AND_SOLUTIONS.md)
- [服务器Git配置](SERVER_GIT_SETUP.md)

---

## 🎯 快速参考

### 命令速查表

| 操作 | 命令 |
|-----|------|
| 切换到测试群 | `bash switch_to_test_group.sh` |
| 切换到正式群 | `bash switch_to_prod_group.sh` |
| 查看当前配置 | `grep "^CHAT_ID=" .env` |
| 查看服务状态 | `sudo systemctl status monthly-report-bot` |
| 重启服务 | `sudo systemctl restart monthly-report-bot` |
| 查看日志 | `sudo journalctl -u monthly-report-bot -f` |

---

**最后更新**: 2025-10-23
**维护者**: 项目团队
