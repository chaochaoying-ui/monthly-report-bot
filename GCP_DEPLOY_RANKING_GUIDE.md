# GCP 部署指南 - 已完成人员排行榜功能

## 📋 部署概述

本指南将帮助你在 GCP Ubuntu 服务器上部署最新的**已完成人员排行榜功能**。

## 🎯 部署内容

### 新增功能
1. ✅ **完整的用户ID映射**（17个用户）
2. ✅ **美化的排行榜设计**（金银铜配色 + 勋章系统）
3. ✅ **排名标记系统**（#1、#2、#3...）
4. ✅ **测试工具**（test_chart_generator.py）

### 更新的文件
- `chart_generator.py` - 图表生成器（添加用户映射和美化排行榜）
- `test_chart_generator.py` - 新增测试脚本
- `monthly_report_bot_final_interactive.py` - 微调（仅空白行）

## 🚀 方法一：一键部署（推荐）

### 1. 上传部署脚本

将 `deploy_ranking_feature.sh` 上传到服务器：

```bash
# 在本地执行（Windows PowerShell 或 Git Bash）
scp deploy_ranking_feature.sh hdi918072@<YOUR_GCP_IP>:~/
```

### 2. 连接到服务器

```bash
ssh hdi918072@<YOUR_GCP_IP>
```

### 3. 运行部署脚本

```bash
# 赋予执行权限
chmod +x ~/deploy_ranking_feature.sh

# 运行部署脚本
cd ~/monthly-report-bot/monthly_report_bot_link_pack
~/deploy_ranking_feature.sh
```

脚本会自动完成以下操作：
- ✅ 拉取最新代码
- ✅ 安装依赖库（matplotlib、seaborn、numpy）
- ✅ 验证必需文件
- ✅ 创建图表目录
- ✅ 测试图表生成功能
- ✅ 重启服务（可选）

## 🛠️ 方法二：手动部署

### 步骤 1: 连接到 GCP 服务器

```bash
ssh hdi918072@<YOUR_GCP_IP>
```

### 步骤 2: 进入项目目录

```bash
cd ~/monthly-report-bot/monthly_report_bot_link_pack
```

### 步骤 3: 拉取最新代码

```bash
git fetch origin
git pull origin main
```

查看最新提交：
```bash
git log --oneline -5
```

应该能看到：
- `9e56517` - docs: 添加已完成人员排行榜功能实现总结文档
- `d654d68` - feat: 完善已完成人员排行榜功能并美化图表

### 步骤 4: 安装依赖库

检查是否已安装：
```bash
python3 -c "import matplotlib, seaborn, numpy" && echo "依赖已安装" || echo "需要安装依赖"
```

如果需要安装：
```bash
pip3 install matplotlib seaborn numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤 5: 验证文件

```bash
# 检查关键文件是否存在
ls -lh chart_generator.py
ls -lh test_chart_generator.py
ls -lh task_stats.json
ls -lh monthly_report_bot_final_interactive.py
```

### 步骤 6: 创建图表目录

```bash
mkdir -p charts
```

### 步骤 7: 测试图表生成功能

```bash
python3 test_chart_generator.py
```

期望输出：
```
============================================================
🧪 图表生成器测试
============================================================

✅ 成功加载任务统计数据
   - 当前月份: 2025-10
   - 总任务数: 23
   - 已完成: 9
   - 完成率: 39.13%

📊 已完成人员统计:
   🥇 #1 刘野: 4个任务
   🥈 #2 高雅慧: 2个任务
   🥉 #3 袁阿虎: 2个任务
      #4 范明杰: 1个任务

✅ 综合仪表板生成成功!
============================================================
```

### 步骤 8: 重启服务

```bash
# 查看服务状态
sudo systemctl status monthly-report-bot-interactive.service

# 重启服务
sudo systemctl restart monthly-report-bot-interactive.service

# 等待几秒后检查状态
sleep 3
sudo systemctl status monthly-report-bot-interactive.service
```

### 步骤 9: 查看服务日志

```bash
# 实时查看日志
sudo journalctl -u monthly-report-bot-interactive.service -f

# 或查看最近50行
sudo journalctl -u monthly-report-bot-interactive.service -n 50
```

## 🧪 验证部署

### 1. 检查服务运行状态

```bash
sudo systemctl is-active monthly-report-bot-interactive.service
```

应返回：`active`

### 2. 测试图表生成

在飞书群聊中发送以下命令：
- "图表"
- "可视化"
- "饼图"
- "统计图"

机器人应该回复：
```
📊 统计图表已生成

📈 当前进度（2025-10）:
- 总任务数: 23
- 已完成: 9
- 待完成: 14
- 完成率: 39.13%

📁 图表文件: dashboard_20251022_xxxxxx.png
💡 提示: 图表包含饼状图、进度条、用户参与度等多维度统计
```

### 3. 查看生成的图表文件

```bash
ls -lht charts/*.png | head -5
```

## 📦 依赖库信息

### 必需的 Python 包

| 包名 | 版本要求 | 用途 |
|------|---------|------|
| matplotlib | >=3.7.0 | 图表绘制 |
| seaborn | >=0.13.0 | 样式美化 |
| numpy | >=1.24.0 | 数值计算 |

### 安装命令

```bash
# 使用清华镜像源（国内）
pip3 install matplotlib seaborn numpy -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用官方源
pip3 install matplotlib seaborn numpy
```

### 验证安装

```bash
python3 << EOF
import matplotlib
import seaborn
import numpy
print("matplotlib 版本:", matplotlib.__version__)
print("seaborn 版本:", seaborn.__version__)
print("numpy 版本:", numpy.__version__)
print("✅ 所有依赖已正确安装")
EOF
```

## 🔧 故障排查

### 问题 1: 依赖库安装失败

**错误**：`error: externally-managed-environment`

**解决方案**：
```bash
# 方法1: 使用 --break-system-packages（不推荐）
pip3 install matplotlib seaborn numpy --break-system-packages

# 方法2: 使用虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate
pip install matplotlib seaborn numpy
```

### 问题 2: 服务无法启动

**检查日志**：
```bash
sudo journalctl -u monthly-report-bot-interactive.service -n 100
```

**常见原因**：
- 端口被占用
- 环境变量缺失
- Python 依赖缺失

**解决方案**：
```bash
# 检查端口占用
sudo netstat -tlnp | grep 8000

# 检查环境变量
sudo systemctl show monthly-report-bot-interactive.service --property=Environment

# 手动运行程序测试
cd ~/monthly-report-bot/monthly_report_bot_link_pack
python3 monthly_report_bot_final_interactive.py
```

### 问题 3: 图表生成失败

**错误**：`ModuleNotFoundError: No module named 'matplotlib'`

**解决方案**：
```bash
# 检查 Python 路径
which python3

# 安装依赖到正确的 Python 环境
/usr/bin/python3 -m pip install matplotlib seaborn numpy
```

### 问题 4: 中文显示乱码

**解决方案**：
```bash
# 安装中文字体
sudo apt-get update
sudo apt-get install -y fonts-wqy-zenhei fonts-wqy-microhei

# 清除 matplotlib 字体缓存
rm -rf ~/.cache/matplotlib
```

### 问题 5: Git 拉取失败

**错误**：`Authentication failed`

**解决方案**：
```bash
# 检查远程仓库地址
git remote -v

# 如果使用 HTTPS，可能需要配置 token
git remote set-url origin https://<TOKEN>@github.com/chaochaoying-ui/monthly-report-bot.git

# 或使用 SSH（推荐）
git remote set-url origin git@github.com:chaochaoying-ui/monthly-report-bot.git
```

## 📊 功能测试清单

部署完成后，请按照以下清单测试功能：

- [ ] 服务正常运行（`systemctl is-active`）
- [ ] 无错误日志（`journalctl -n 50`）
- [ ] 图表生成测试成功（`test_chart_generator.py`）
- [ ] charts 目录已创建并有图表文件
- [ ] 飞书群聊中"图表"命令响应正常
- [ ] 排行榜显示金银铜配色
- [ ] 勋章系统正常显示（🥇🥈🥉）
- [ ] 排名标记正常显示（#1、#2、#3...）
- [ ] 所有17个用户的中文名正确映射

## 🎯 使用指南

### 用户命令

在飞书群聊中发送以下任一命令查看美化的统计图表：

| 命令 | 说明 |
|------|------|
| `图表` | 生成综合仪表板 |
| `可视化` | 同上 |
| `饼图` | 同上 |
| `统计图` | 同上 |
| `chart` | 同上（英文） |
| `visualization` | 同上（英文） |

### 管理命令

```bash
# 查看服务状态
sudo systemctl status monthly-report-bot-interactive.service

# 启动服务
sudo systemctl start monthly-report-bot-interactive.service

# 停止服务
sudo systemctl stop monthly-report-bot-interactive.service

# 重启服务
sudo systemctl restart monthly-report-bot-interactive.service

# 查看实时日志
sudo journalctl -u monthly-report-bot-interactive.service -f

# 查看最近日志
sudo journalctl -u monthly-report-bot-interactive.service -n 100
```

## 📝 配置文件位置

| 文件 | 路径 |
|------|------|
| 主程序 | `~/monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot_final_interactive.py` |
| 图表生成器 | `~/monthly-report-bot/monthly_report_bot_link_pack/chart_generator.py` |
| 任务统计 | `~/monthly-report-bot/monthly_report_bot_link_pack/task_stats.json` |
| systemd 配置 | `/etc/systemd/system/monthly-report-bot-interactive.service` |
| 环境变量 | `~/monthly-report-bot/monthly_report_bot_link_pack/.env` |
| 图表输出 | `~/monthly-report-bot/monthly_report_bot_link_pack/charts/` |

## 🔄 回滚操作

如果部署后出现问题，可以回滚到之前的版本：

```bash
cd ~/monthly-report-bot/monthly_report_bot_link_pack

# 查看提交历史
git log --oneline -10

# 回滚到之前的提交
git reset --hard <commit_hash>

# 重启服务
sudo systemctl restart monthly-report-bot-interactive.service
```

## 📞 技术支持

如果遇到问题，请提供以下信息：

1. **系统信息**：
   ```bash
   uname -a
   python3 --version
   pip3 list | grep -E "matplotlib|seaborn|numpy"
   ```

2. **服务状态**：
   ```bash
   sudo systemctl status monthly-report-bot-interactive.service
   ```

3. **最近日志**：
   ```bash
   sudo journalctl -u monthly-report-bot-interactive.service -n 100
   ```

4. **Git 状态**：
   ```bash
   git log --oneline -5
   git status
   ```

---

**文档版本**：v1.0
**更新时间**：2025-10-22
**适用版本**：v1.3.1-interactive
