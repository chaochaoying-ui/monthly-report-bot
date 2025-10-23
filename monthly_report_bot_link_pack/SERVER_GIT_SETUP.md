# 服务器Git配置指南

## 🚨 当前问题

在服务器上执行 `git commit` 时遇到错误：
```
Author identity unknown
*** Please tell me who you are.
fatal: empty ident name not allowed
```

在执行 `git push` 时需要输入GitHub用户名和密码。

---

## ✅ 解决方案

### 步骤1: 配置Git用户信息

在服务器上执行以下命令：

```bash
# 配置全局用户名和邮箱
git config --global user.email "your_email@example.com"
git config --global user.name "Your Name"

# 验证配置
git config --global user.email
git config --global user.name
```

**示例**：
```bash
git config --global user.email "hdi918072@gmail.com"
git config --global user.name "HDI918072"
```

---

### 步骤2: 配置GitHub认证（推荐使用Personal Access Token）

GitHub已经**不再支持密码认证**，需要使用Personal Access Token (PAT)。

#### 2.1 创建Personal Access Token

1. 登录GitHub: https://github.com
2. 点击右上角头像 → Settings
3. 左侧菜单最底部 → Developer settings
4. Personal access tokens → Tokens (classic)
5. Generate new token (classic)
6. 设置：
   - Note: `monthly-report-bot-server`
   - Expiration: `No expiration` 或 `90 days`
   - 勾选权限: `repo` (完整仓库访问权限)
7. 点击 **Generate token**
8. **立即复制token** (只显示一次！格式如: `ghp_xxxxxxxxxxxxxxxxxxxx`)

#### 2.2 在服务器上配置Token

**方法A: 使用Git Credential Helper (推荐)**

```bash
# 配置Git存储凭据
git config --global credential.helper store

# 第一次push时会要求输入用户名和密码
# Username: 你的GitHub用户名
# Password: 粘贴刚才创建的Personal Access Token (不是密码！)

# 凭据会保存在 ~/.git-credentials 中，下次自动使用
```

**方法B: 修改远程仓库URL (包含token)**

```bash
# 查看当前远程仓库URL
git remote -v

# 修改为包含token的URL
git remote set-url origin https://ghp_YOUR_TOKEN@github.com/USERNAME/REPO.git

# 示例（替换成你的实际值）
git remote set-url origin https://ghp_xxxxxxxxxxxxxxxxxxxx@github.com/yourusername/monthly-report-bot.git
```

⚠️ **注意**: 方法B会将token明文存储在 `.git/config` 中，相对不太安全。

---

### 步骤3: 验证配置

```bash
# 测试配置是否成功
git config --global --list

# 尝试拉取代码
git pull

# 如果成功，说明配置正确
```

---

## 🔄 完整的服务器操作流程

### 场景1: 从本地推送代码到GitHub，然后在服务器上拉取

**在本地电脑**:
```bash
cd f:/monthly_report_bot_link_pack/monthly_report_bot_link_pack
git add .
git commit -m "fix: 修复任务同步问题"
git push origin main
```

**在服务器上**:
```bash
# SSH登录
ssh hdi918072@34.145.43.77

# 进入项目目录
cd /home/hdi918072/monthly-report-bot

# 拉取最新代码（不需要commit）
git pull origin main

# 运行同步脚本
source venv/bin/activate
python3 sync_existing_tasks.py

# 重启服务
sudo systemctl restart monthly-report-bot
```

---

### 场景2: 在服务器上直接修改代码并提交（不推荐）

如果必须在服务器上修改：

```bash
# 1. 配置Git用户（一次性）
git config --global user.email "your_email@example.com"
git config --global user.name "Your Name"

# 2. 配置凭据存储（一次性）
git config --global credential.helper store

# 3. 修改代码后提交
git add .
git commit -m "fix: 服务器上的紧急修复"

# 4. 第一次推送时输入凭据
git push origin main
# Username: 你的GitHub用户名
# Password: Personal Access Token (ghp_xxxxxxxxxxxxxxxxxxxx)

# 5. 后续推送会自动使用保存的凭据
git push origin main
```

---

## 📝 推荐工作流程

**最佳实践** (避免在服务器上修改代码):

```
本地开发 → Git提交 → 推送到GitHub → 服务器拉取 → 重启服务
```

**步骤**:

1. **本地开发**:
   ```bash
   # 在本地修改代码
   code monthly_report_bot_ws_v1.1.py
   ```

2. **本地提交**:
   ```bash
   git add .
   git commit -m "fix: 描述修改内容"
   git push origin main
   ```

3. **服务器拉取**:
   ```bash
   ssh hdi918072@34.145.43.77
   cd /home/hdi918072/monthly-report-bot
   git pull origin main
   ```

4. **重启服务**:
   ```bash
   sudo systemctl restart monthly-report-bot
   sudo systemctl status monthly-report-bot
   ```

---

## 🆘 常见问题

### Q1: 忘记Personal Access Token怎么办？

Token只在创建时显示一次。如果忘记：
1. 去GitHub删除旧token
2. 创建新token
3. 重新配置服务器

### Q2: git pull时提示"Authentication failed"

原因: Token过期或错误

解决:
```bash
# 删除保存的凭据
rm ~/.git-credentials

# 重新配置
git config --global credential.helper store

# 下次pull时重新输入token
git pull origin main
```

### Q3: 如何查看保存的凭据？

```bash
# 查看凭据文件
cat ~/.git-credentials

# 格式: https://username:token@github.com
```

### Q4: 多人使用服务器，如何避免冲突？

- 每个人使用自己的GitHub账号和token
- 或者创建一个专用的部署账号，共享token（不推荐）

---

## 🔒 安全建议

1. ✅ **使用Personal Access Token**，不要使用密码
2. ✅ **设置Token过期时间**（建议90天或180天）
3. ✅ **最小权限原则**：只授予必要的权限（repo）
4. ✅ **定期轮换Token**
5. ❌ **不要**将token提交到代码仓库
6. ❌ **不要**在公开场合分享token

---

## 📋 快速参考

### 一次性配置（在服务器上执行一次）

```bash
# 1. 配置Git用户信息
git config --global user.email "your_email@example.com"
git config --global user.name "Your Name"

# 2. 配置凭据存储
git config --global credential.helper store

# 3. 验证配置
git config --global --list

# 4. 第一次操作时会要求输入token
git pull origin main
# Username: <你的GitHub用户名>
# Password: <你的Personal Access Token>

# 5. 后续操作会自动使用保存的凭据
```

### 日常操作

```bash
# SSH登录
ssh hdi918072@34.145.43.77

# 进入目录
cd /home/hdi918072/monthly-report-bot

# 拉取最新代码
git pull origin main

# 重启服务
sudo systemctl restart monthly-report-bot
```

---

## ✅ 检查清单

配置完成后，确认以下项目：

- [ ] Git用户名和邮箱已配置
- [ ] Personal Access Token已创建
- [ ] 凭据存储已启用
- [ ] 能够成功执行 `git pull`
- [ ] 能够成功执行 `git push`（如果需要）

---

**创建时间**: 2025-10-23
**适用于**: GCP Ubuntu服务器
**服务器**: hdi918072@34.145.43.77
