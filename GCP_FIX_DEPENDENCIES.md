# 🔧 修复 v1.1 依赖问题

## 问题描述

v1.1 启动失败，错误信息：
```
ModuleNotFoundError: No module named 'matplotlib'
```

## 原因

v1.1 使用 matplotlib 生成进度图表，但 GCP 服务器的虚拟环境中没有安装这个依赖。

---

## 🚀 快速修复（复制整个命令执行）

在 GCP SSH 终端执行以下命令：

```bash
# ============================================================================
# 停止服务，安装依赖，重启服务
# ============================================================================

echo "停止服务..."
sudo systemctl stop monthly-report-bot

echo ""
echo "激活虚拟环境..."
cd ~/monthly-report-bot/monthly_report_bot_link_pack
source venv/bin/activate

echo ""
echo "安装 v1.1 依赖..."
pip install matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple

echo ""
echo "验证安装..."
python3 -c "import matplotlib; print('✅ matplotlib 已安装:', matplotlib.__version__)"

echo ""
echo "启动 v1.1 服务..."
sudo systemctl start monthly-report-bot

echo ""
echo "等待服务启动..."
sleep 5

echo ""
echo "检查服务状态..."
sudo systemctl status monthly-report-bot --no-pager | head -15

echo ""
echo "检查最新日志..."
sudo journalctl -u monthly-report-bot -n 20 --no-pager

echo ""
echo "========================================================================"
echo "✅ 修复完成！"
echo "========================================================================"
```

---

## 📋 分步说明

如果需要分步执行：

### 1. 停止服务
```bash
sudo systemctl stop monthly-report-bot
```

### 2. 安装 matplotlib
```bash
cd ~/monthly-report-bot/monthly_report_bot_link_pack
source venv/bin/activate
pip install matplotlib
```

### 3. 重启服务
```bash
sudo systemctl start monthly-report-bot
```

### 4. 检查状态
```bash
sudo systemctl status monthly-report-bot
sudo journalctl -u monthly-report-bot -n 50 --no-pager
```

---

## ✅ 验证成功标志

应该看到：
```
● monthly-report-bot.service - Monthly Report Bot v1.1 (WebSocket)
   Loaded: loaded
   Active: active (running)
```

日志应该显示：
```
✅ WebSocket 连接已建立
✅ 用户消息处理器已注册
```

---

## 🔍 为什么会出现这个问题？

v1.1 新增了进度图表功能（18-22日 17:00 发送），需要 matplotlib 生成图表。但部署脚本中没有包含安装新依赖的步骤。

---

## 📝 后续改进

我会更新部署脚本，在部署时自动安装 requirements_v1_1.txt 中的所有依赖。

---

**执行修复命令后，v1.1 就可以正常运行了！**
