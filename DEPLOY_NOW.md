# 🚀 立即部署 - 图表上传功能

## 🎯 最新更新（2025-10-22）

✅ **新增功能：图表图片自动上传和展示**
- 发送"图表"后直接显示美化的图表图片
- 不再只显示文件名，而是在消息中直接展示
- 包含金银铜排行榜的综合统计仪表板

## ⚠️ 注意：部署脚本位置

部署脚本 `deploy_ranking_feature.sh` 在**项目根目录**，不在 `monthly_report_bot_link_pack` 子目录中。

---

## 🚀 快速部署（推荐）

**在 GCP 服务器上执行以下命令：**

```bash
# 1. 进入项目目录
cd ~/monthly-report-bot/monthly_report_bot_link_pack

# 2. 拉取最新代码
git pull origin main

# 3. 重启服务
sudo systemctl restart monthly-report-bot.service

# 4. 检查服务状态
sudo systemctl status monthly-report-bot.service

# 5. 测试：在飞书群聊中发送"图表"
```

✅ **验证成功**：在飞书中发送"图表"，应该看到包含图表图片的卡片消息

---

## ✅ 正确的部署命令

### 方法一：使用部署脚本（推荐）

```bash
# 当前你在：~/monthly-report-bot/monthly_report_bot_link_pack
# 需要返回上级目录

cd ~/monthly-report-bot
chmod +x deploy_ranking_feature.sh
./deploy_ranking_feature.sh
```

---

### 方法二：直接手动部署（更快）

由于你已经在 `~/monthly-report-bot/monthly_report_bot_link_pack` 目录，直接执行以下命令：

```bash
# 1. 安装依赖
pip3 install matplotlib seaborn numpy -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 验证依赖
python3 << 'EOF'
import matplotlib, seaborn, numpy
print("✅ matplotlib:", matplotlib.__version__)
print("✅ seaborn:", seaborn.__version__)
print("✅ numpy:", numpy.__version__)
EOF

# 3. 创建图表目录
mkdir -p charts

# 4. 测试图表生成
python3 test_chart_generator.py

# 5. 重启服务
sudo systemctl restart monthly-report-bot-interactive.service

# 6. 检查状态
sudo systemctl status monthly-report-bot-interactive.service
```

---

## 🎯 推荐执行方式（一键命令）

复制以下整段命令，一次性执行：

```bash
echo "=========================================="
echo "🚀 开始部署排行榜功能"
echo "=========================================="

# 安装依赖
echo ""
echo "📦 安装依赖库..."
pip3 install matplotlib seaborn numpy -i https://pypi.tuna.tsinghua.edu.cn/simple 2>/dev/null || \
python3 -m pip install matplotlib seaborn numpy -i https://pypi.tuna.tsinghua.edu.cn/simple

# 验证依赖
echo ""
echo "✅ 验证依赖安装..."
python3 << 'EOF'
try:
    import matplotlib, seaborn, numpy
    print("✅ matplotlib:", matplotlib.__version__)
    print("✅ seaborn:", seaborn.__version__)
    print("✅ numpy:", numpy.__version__)
except ImportError as e:
    print("❌ 依赖缺失:", e)
    exit(1)
EOF

# 创建图表目录
echo ""
echo "📁 创建图表目录..."
mkdir -p charts
echo "✅ charts 目录已创建"

# 测试图表生成
echo ""
echo "🧪 测试图表生成..."
python3 test_chart_generator.py

# 提示重启服务
echo ""
echo "=========================================="
echo "✅ 部署准备完成！"
echo "=========================================="
echo ""
echo "🔄 现在需要重启服务以应用更新："
echo ""
echo "sudo systemctl restart monthly-report-bot-interactive.service"
echo ""
echo "然后检查服务状态："
echo "sudo systemctl status monthly-report-bot-interactive.service"
echo ""
echo "=========================================="
```

---

## 🔍 如果安装依赖失败

尝试以下任一方法：

### 方法 1: 使用 --break-system-packages
```bash
pip3 install matplotlib seaborn numpy --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 方法 2: 使用 sudo
```bash
sudo pip3 install matplotlib seaborn numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 方法 3: 使用 python3 -m pip
```bash
python3 -m pip install --user matplotlib seaborn numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## ✅ 部署后验证

### 1. 检查服务状态
```bash
sudo systemctl is-active monthly-report-bot-interactive.service
```
应该返回：`active`

### 2. 查看生成的图表
```bash
ls -lht charts/*.png | head -3
```

### 3. 在飞书群聊中测试
发送：`图表`

应该看到包含金银铜排行榜的美化图表。

---

## 📝 当前目录结构

```
~/monthly-report-bot/
├── deploy_ranking_feature.sh          ← 部署脚本在这里
├── GCP_DEPLOY_RANKING_GUIDE.md
├── QUICK_DEPLOY_COMMANDS.md
├── RANKING_FEATURE_COMPLETE.md
└── monthly_report_bot_link_pack/      ← 你现在在这里
    ├── chart_generator.py             ← 已更新
    ├── test_chart_generator.py        ← 新增
    ├── monthly_report_bot_final_interactive.py
    ├── task_stats.json
    └── charts/                        ← 图表输出目录
```

---

**快速开始**：复制"一键命令"部分，直接执行！
