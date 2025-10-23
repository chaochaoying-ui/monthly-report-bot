# 部署前检查清单 (Pre-Deployment Checklist)

> **使用说明**: 每次部署新代码到生产环境前，**必须完成本清单的所有检查项**！
> 打印或在屏幕上逐项核对，全部通过后才能部署。

**项目**: 月报机器人
**服务器**: hdi918072@34.145.43.77
**目录**: /home/hdi918072/monthly-report-bot
**服务名**: monthly-report-bot

---

## 📋 检查清单

### 阶段1: 部署前准备 (Pre-Deployment)

#### 1.1 错题本阅读
- [ ] 已阅读 [PITFALLS_AND_SOLUTIONS.md](PITFALLS_AND_SOLUTIONS.md)
- [ ] 确认本次修改不会重复之前的错误
- [ ] 了解相关模块的常见问题

#### 1.2 代码检查
- [ ] 代码已在本地测试通过
- [ ] 所有修改的文件已保存
- [ ] Python 语法检查通过: `python3 -m py_compile *.py`
- [ ] 没有遗留的 TODO 或 FIXME（除非有计划）

#### 1.3 环境变量检查
- [ ] 使用正确的环境变量命名:
  - `APP_ID`（不是 `FEISHU_APP_ID`）
  - `APP_SECRET`（不是 `FEISHU_APP_SECRET`）
- [ ] 代码中兼容两种格式: `os.environ.get('APP_ID') or os.environ.get('FEISHU_APP_ID')`
- [ ] 启动时验证环境变量存在

#### 1.4 飞书API调用检查
- [ ] 客户端初始化代码正确:
  ```python
  lark_client = lark.Client.builder() \
      .app_id(APP_ID) \
      .app_secret(APP_SECRET) \
      .build()
  ```
- [ ] **没有**添加 `.log_level()` 参数
- [ ] 参考了已验证的代码 (`monthly_report_bot_final_interactive.py`)

#### 1.5 任务管理检查（如果涉及任务相关修改）
- [ ] 任务创建使用真实API调用（不是模拟）
- [ ] 使用真实GUID保存任务（不是拼接的假ID如 `task_2025-10_1`）
- [ ] 任务ID格式验证: `^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$`

#### 1.6 错误处理检查
- [ ] 所有API调用都有错误处理
- [ ] 记录详细的错误日志（包括错误码和消息）
- [ ] 根据错误码采取正确的应对措施

#### 1.7 日志输出检查
- [ ] 关键操作有日志记录（INFO级别）
- [ ] 错误有详细日志（ERROR级别，包含 exc_info）
- [ ] 没有敏感信息（密码、token）输出到日志

---

### 阶段2: Git 版本控制 (Version Control)

#### 2.1 Git 状态检查
- [ ] 运行 `git status` 确认修改的文件
- [ ] 运行 `git diff` 检查修改内容
- [ ] 确认没有意外修改不相关的文件

#### 2.2 敏感信息检查
- [ ] `.env` 文件**未**添加到 git（在 .gitignore 中）
- [ ] 没有硬编码的密码、token、密钥
- [ ] 没有提交临时文件、日志文件

#### 2.3 提交信息
- [ ] Commit message 清晰描述了修改内容
- [ ] 使用规范的前缀:
  - `feat:` - 新功能
  - `fix:` - 修复bug
  - `refactor:` - 重构
  - `docs:` - 文档更新
  - `chore:` - 杂项（依赖更新等）

#### 2.4 推送到 GitHub
- [ ] 运行 `git add <files>` 添加文件
- [ ] 运行 `git commit -m "..."`
- [ ] 运行 `git push origin main`
- [ ] 确认 GitHub 上已看到最新提交

---

### 阶段3: 服务器部署 (Deployment)

#### 3.1 SSH 连接
- [ ] 成功连接到服务器: `ssh hdi918072@34.145.43.77`
- [ ] 确认当前用户: `whoami` → `hdi918072`

#### 3.2 目录检查
- [ ] 进入正确的目录: `cd /home/hdi918072/monthly-report-bot` （⚠️ 连字符 `-`）
- [ ] 确认目录内容: `ls -la`

#### 3.3 备份旧文件
- [ ] 备份主程序:
  ```bash
  cp monthly_report_bot_ws_v1.1.py monthly_report_bot_ws_v1.1.py.backup_$(date +%Y%m%d_%H%M%S)
  ```
- [ ] 备份数据文件:
  ```bash
  cp task_stats.json task_stats.json.backup_$(date +%Y%m%d_%H%M%S)
  ```
- [ ] 确认备份文件存在: `ls -lh *.backup_*`

#### 3.4 拉取新代码
- [ ] 检查当前分支: `git branch`
- [ ] 拉取最新代码: `git pull origin main`
- [ ] 确认拉取成功（没有冲突）
- [ ] 验证文件已更新: `ls -lh <modified_files>`

#### 3.5 虚拟环境检查
- [ ] 激活虚拟环境: `source venv/bin/activate`
- [ ] 确认 Python 路径: `which python3` → `/home/hdi918072/monthly-report-bot/venv/bin/python3`
- [ ] 检查依赖包: `pip list | grep lark-oapi`

#### 3.6 环境变量检查
- [ ] `.env` 文件存在: `ls -lh .env`
- [ ] `.env` 文件包含正确内容:
  ```bash
  cat .env | grep -E "^(APP_ID|APP_SECRET)="
  ```
- [ ] 格式正确（`APP_ID=...` 而不是 `FEISHU_APP_ID=...`）

#### 3.7 清除缓存
- [ ] 清除 Python 字节码缓存:
  ```bash
  find . -name "*.pyc" -delete
  find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
  ```

---

### 阶段4: 服务重启 (Service Restart)

#### 4.1 重新加载配置
- [ ] 重新加载 systemd: `sudo systemctl daemon-reload`

#### 4.2 重启服务
- [ ] 停止服务: `sudo systemctl stop monthly-report-bot`
- [ ] 等待3秒
- [ ] 启动服务: `sudo systemctl start monthly-report-bot`
- [ ] 或者直接重启: `sudo systemctl restart monthly-report-bot`

#### 4.3 检查服务状态
- [ ] 查看服务状态: `sudo systemctl status monthly-report-bot`
- [ ] 确认状态为 `active (running)`
- [ ] 没有红色的错误信息

#### 4.4 查看日志
- [ ] 查看最近日志: `sudo journalctl -u monthly-report-bot -n 50`
- [ ] 查看实时日志: `sudo journalctl -u monthly-report-bot -f`
- [ ] 确认没有启动错误
- [ ] 确认看到预期的启动日志（如 "✅ 连接成功" 等）

---

### 阶段5: 功能验证 (Functional Testing)

#### 5.1 基础功能测试
- [ ] 在飞书群聊发送: `状态`
- [ ] 机器人有响应
- [ ] 响应内容格式正确

#### 5.2 任务统计验证（如果涉及任务相关修改）
- [ ] 发送 `状态` 后，检查统计数据:
  - 总任务数是否正确
  - 已完成任务数**不是0**（如果确实有完成的任务）
  - 完成率计算正确
  - 已完成人员列表正确

#### 5.3 图表功能验证（如果涉及图表相关修改）
- [ ] 发送 `图表`
- [ ] 机器人发送了图片
- [ ] 图片中的中文**没有乱码**
- [ ] 饼图、进度条显示正确
- [ ] 统计数据与 `状态` 命令一致

#### 5.4 其他功能验证（根据修改内容）
- [ ] 测试修改相关的功能
- [ ] 测试可能受影响的关联功能
- [ ] 验证边界情况（如空列表、特殊字符等）

#### 5.5 监控观察
- [ ] 观察实时日志10分钟，确认没有异常错误
- [ ] 如果有定时任务，等待下一次执行并验证

---

### 阶段6: 回滚准备 (Rollback Plan)

#### 6.1 回滚脚本准备
如果部署失败，使用以下命令回滚：

```bash
# 恢复旧版本代码
cp monthly_report_bot_ws_v1.1.py.backup_<timestamp> monthly_report_bot_ws_v1.1.py
cp task_stats.json.backup_<timestamp> task_stats.json

# 重启服务
sudo systemctl restart monthly-report-bot

# 查看状态
sudo systemctl status monthly-report-bot
```

#### 6.2 回滚决策标准
以下情况需要立即回滚：
- [ ] 服务无法启动（状态为 failed）
- [ ] 启动后持续报错（日志中有大量 ERROR）
- [ ] 核心功能失效（如无法响应消息）
- [ ] 数据损坏或丢失

---

## 📝 部署记录

### 本次部署信息

**部署日期**: ___________
**部署时间**: ___________
**部署人员**: ___________
**修改内容**:
```
(填写本次修改的主要内容)
```

**相关文件**:
- [ ] `monthly_report_bot_ws_v1.1.py`
- [ ] `sync_existing_tasks.py`
- [ ] `task_stats.json`
- [ ] 其他: ___________

**部署结果**: [ ] 成功 / [ ] 失败 / [ ] 已回滚

**验证结果**: [ ] 通过 / [ ] 部分通过 / [ ] 失败

**备注**:
```
(记录部署过程中的特殊情况、问题、解决方案等)
```

---

## 🆘 常见问题快速参考

### Q1: 服务启动失败
```bash
# 检查详细错误
sudo journalctl -u monthly-report-bot -n 100 --no-pager

# 检查 Python 语法错误
python3 -m py_compile monthly_report_bot_ws_v1.1.py

# 检查环境变量
source venv/bin/activate
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.environ.get('APP_ID'))"
```

### Q2: 任务统计显示 0
```bash
# 检查 task_stats.json 中的任务ID格式
cat task_stats.json | grep -E '"task_2025-10_[0-9]+"'  # 不应该有输出（假ID）
cat task_stats.json | grep -E '[a-f0-9]{8}-[a-f0-9]{4}'  # 应该有输出（真实GUID）

# 运行同步脚本
python3 sync_existing_tasks.py
```

### Q3: 图表中文乱码
```bash
# 检查字体文件
ls -lh fonts/

# 检查系统字体
fc-list :lang=zh

# 如果没有中文字体，安装
sudo apt-get update && sudo apt-get install fonts-noto-cjk

# 清除 matplotlib 缓存
rm -rf ~/.cache/matplotlib
```

### Q4: 回滚到上一个版本
```bash
# 查看备份文件
ls -lh *.backup_* | tail -n 5

# 恢复最新备份
LATEST_BACKUP=$(ls -t monthly_report_bot_ws_v1.1.py.backup_* | head -n 1)
cp $LATEST_BACKUP monthly_report_bot_ws_v1.1.py

# 重启服务
sudo systemctl restart monthly-report-bot
```

---

## 📚 相关文档

- [PITFALLS_AND_SOLUTIONS.md](PITFALLS_AND_SOLUTIONS.md) - 错题本
- [TASK_SYNC_FIX.md](TASK_SYNC_FIX.md) - 任务同步问题详细说明
- [QUICK_FIX_GUIDE.md](QUICK_FIX_GUIDE.md) - 快速修复指南

---

## ✅ 最终确认

**部署前最后确认**:

- [ ] 我已完成上述所有检查项
- [ ] 我已阅读错题本，了解常见问题
- [ ] 我已准备好回滚方案
- [ ] 我已备份了所有关键文件
- [ ] 我可以监控部署后的服务运行情况

**签名**: ___________ **日期**: ___________

---

**提醒**:
- 🚨 本检查清单是**强制性**的，不可跳过
- 🚨 如果任何检查项不通过，必须先修复
- 🚨 不要在高峰时段（工作时间）部署重大更新
- 🚨 保持冷静，按清单逐项执行，不要跳步骤

**祝部署顺利！** 🎉
