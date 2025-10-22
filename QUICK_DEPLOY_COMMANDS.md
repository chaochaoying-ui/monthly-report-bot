# 🚀 GCP 快速部署命令 - 已完成人员排行榜功能

## 📋 部署步骤（复制粘贴即可）

### 方法一：使用部署脚本（推荐）⭐

#### 步骤 1: SSH 连接到服务器
```bash
ssh hdi918072@<YOUR_GCP_IP>
```

#### 步骤 2: 进入项目目录并拉取最新代码
```bash
cd ~/monthly-report-bot/monthly_report_bot_link_pack
git fetch origin
git pull origin main
```

#### 步骤 3: 赋予部署脚本执行权限
```bash
chmod +x deploy_ranking_feature.sh
```

#### 步骤 4: 运行部署脚本
```bash
./deploy_ranking_feature.sh
```

脚本会自动完成以下操作：
- ✅ 检查项目目录
- ✅ 拉取最新代码
- ✅ 安装依赖库
- ✅ 验证必需文件
- ✅ 测试图表生成
- ✅ 重启服务（可选）

---

### 方法二：手动部署命令

如果脚本不可用，可以逐条执行以下命令：

#### 1. 连接服务器
```bash
ssh hdi918072@<YOUR_GCP_IP>
```

#### 2. 进入项目目录
```bash
cd ~/monthly-report-bot/monthly_report_bot_link_pack
```

#### 3. 拉取最新代码
```bash
git fetch origin
git pull origin main
```

#### 4. 查看最新提交
```bash
git log --oneline -5
```

应该能看到：
- `b8d52a3` - docs: 添加GCP部署脚本和详细部署指南
- `9e56517` - docs: 添加已完成人员排行榜功能实现总结文档
- `d654d68` - feat: 完善已完成人员排行榜功能并美化图表

#### 5. 安装依赖库（使用清华镜像源）
```bash
pip3 install matplotlib seaborn numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

或者（如果上面的命令失败）：
```bash
python3 -m pip install matplotlib seaborn numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 6. 验证依赖安装
```bash
python3 << 'EOF'
import matplotlib
import seaborn
import numpy
print("✅ matplotlib 版本:", matplotlib.__version__)
print("✅ seaborn 版本:", seaborn.__version__)
print("✅ numpy 版本:", numpy.__version__)
EOF
```

#### 7. 创建图表目录
```bash
mkdir -p charts
```

#### 8. 测试图表生成功能
```bash
python3 test_chart_generator.py
```

期望看到：
```
✅ 成功加载任务统计数据
📊 已完成人员统计:
   🥇 #1 刘野: 4个任务
   🥈 #2 高雅慧: 2个任务
   🥉 #3 袁阿虎: 2个任务
✅ 综合仪表板生成成功!
```

#### 9. 重启服务
```bash
sudo systemctl restart monthly-report-bot-interactive.service
```

#### 10. 检查服务状态
```bash
sudo systemctl status monthly-report-bot-interactive.service
```

#### 11. 查看服务日志
```bash
sudo journalctl -u monthly-report-bot-interactive.service -n 50
```

---

## 🧪 验证部署

### 1. 检查服务是否运行
```bash
sudo systemctl is-active monthly-report-bot-interactive.service
```

应该返回：`active`

### 2. 查看生成的图表
```bash
ls -lht charts/*.png | head -5
```

### 3. 在飞书群聊中测试

发送以下任一命令：
- `图表`
- `可视化`
- `饼图`

应该收到包含排行榜的美化统计图表。

---

## 🔧 常见问题快速修复

### 问题 1: pip3 安装失败
```bash
# 方法1: 使用 --break-system-packages
pip3 install matplotlib seaborn numpy --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple

# 方法2: 使用 python3 -m pip
python3 -m pip install matplotlib seaborn numpy -i https://pypi.tuna.tsinghua.edu.cn/simple

# 方法3: 使用 sudo
sudo pip3 install matplotlib seaborn numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题 2: 服务启动失败
```bash
# 查看详细日志
sudo journalctl -u monthly-report-bot-interactive.service -n 100 --no-pager

# 手动测试运行
cd ~/monthly-report-bot/monthly_report_bot_link_pack
python3 monthly_report_bot_final_interactive.py
```

### 问题 3: Git 拉取失败
```bash
# 检查远程仓库
git remote -v

# 强制拉取（谨慎使用）
git fetch origin
git reset --hard origin/main
```

### 问题 4: 图表生成失败
```bash
# 检查 matplotlib 是否安装
python3 -c "import matplotlib" && echo "已安装" || echo "未安装"

# 重新安装
pip3 install --upgrade matplotlib seaborn numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 📊 完整的一键复制命令

如果你想一次性执行所有命令（不包括服务重启），复制以下内容：

```bash
# 进入项目目录
cd ~/monthly-report-bot/monthly_report_bot_link_pack

# 拉取最新代码
git fetch origin && git pull origin main

# 显示最新提交
echo "========================================"
echo "📝 最新提交记录:"
git log --oneline -3
echo "========================================"

# 安装依赖（如果已安装会自动跳过）
pip3 install matplotlib seaborn numpy -i https://pypi.tuna.tsinghua.edu.cn/simple 2>/dev/null || \
python3 -m pip install matplotlib seaborn numpy -i https://pypi.tuna.tsinghua.edu.cn/simple

# 验证依赖
echo ""
echo "========================================"
echo "📦 验证依赖库安装:"
python3 << 'EOF'
try:
    import matplotlib
    import seaborn
    import numpy
    print("✅ matplotlib:", matplotlib.__version__)
    print("✅ seaborn:", seaborn.__version__)
    print("✅ numpy:", numpy.__version__)
except ImportError as e:
    print("❌ 依赖缺失:", e)
EOF
echo "========================================"

# 创建图表目录
mkdir -p charts

# 测试图表生成
echo ""
echo "========================================"
echo "🧪 测试图表生成功能:"
python3 test_chart_generator.py
echo "========================================"

# 提示用户重启服务
echo ""
echo "========================================"
echo "✅ 代码更新完成！"
echo ""
echo "下一步操作："
echo "1. 重启服务："
echo "   sudo systemctl restart monthly-report-bot-interactive.service"
echo ""
echo "2. 查看服务状态："
echo "   sudo systemctl status monthly-report-bot-interactive.service"
echo ""
echo "3. 查看实时日志："
echo "   sudo journalctl -u monthly-report-bot-interactive.service -f"
echo "========================================"
```

---

## 🎯 服务管理命令

### 启动服务
```bash
sudo systemctl start monthly-report-bot-interactive.service
```

### 停止服务
```bash
sudo systemctl stop monthly-report-bot-interactive.service
```

### 重启服务
```bash
sudo systemctl restart monthly-report-bot-interactive.service
```

### 查看服务状态
```bash
sudo systemctl status monthly-report-bot-interactive.service
```

### 查看实时日志
```bash
sudo journalctl -u monthly-report-bot-interactive.service -f
```

### 查看最近50行日志
```bash
sudo journalctl -u monthly-report-bot-interactive.service -n 50
```

---

## 📝 部署检查清单

部署完成后，请确认以下事项：

- [ ] Git 已拉取到最新版本（commit: b8d52a3 或更新）
- [ ] matplotlib、seaborn、numpy 已安装
- [ ] test_chart_generator.py 测试成功
- [ ] charts 目录已创建
- [ ] 服务已重启
- [ ] 服务状态为 active
- [ ] 无错误日志
- [ ] 飞书群聊中"图表"命令响应正常

---

## 🆘 紧急回滚

如果部署后出现严重问题，可以快速回滚：

```bash
cd ~/monthly-report-bot/monthly_report_bot_link_pack
git log --oneline -10  # 查找之前的稳定版本 commit hash
git reset --hard <之前的commit_hash>  # 例如: git reset --hard cae8bc2
sudo systemctl restart monthly-report-bot-interactive.service
```

---

**文档版本**：v1.0
**更新时间**：2025-10-22
**适用版本**：v1.3.1-interactive
