# 🚀 月报机器人环境安装指南

## 📋 快速安装（3步完成）

### 方法1：自动安装（推荐）⭐

1. **右键点击** `download_python.ps1`
2. 选择 **"使用PowerShell运行"**
3. 等待Python自动下载和安装
4. 重启终端后运行 `install_environment.bat`

---

### 方法2：手动安装

#### 步骤1：安装Python 3.11

1. **下载Python**
   ```
   https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
   ```

2. **安装配置**
   - ✅ 勾选 **"Add python.exe to PATH"** （重要！）
   - ✅ 选择 **"Install for all users"**
   - ✅ 点击 **"Install Now"**

3. **验证安装**
   打开新的PowerShell窗口：
   ```powershell
   python --version
   # 应显示：Python 3.11.9
   ```

#### 步骤2：安装项目依赖

```powershell
cd F:\monthly_report_bot_link_pack\monthly_report_bot_link_pack
python -m pip install -r requirements_v1_1.txt
```

#### 步骤3：启动机器人

```powershell
start_bot.bat
```

---

## 📦 依赖包清单

### 核心依赖（必需）
- `lark-oapi>=1.4.22` - 飞书官方SDK
- `pytz` - 时区处理
- `pyyaml` - YAML配置
- `requests` - HTTP请求

### 可选依赖
- `matplotlib` - 图表生成
- `pandas` - 数据处理
- `numpy` - 数值计算

---

## 🔧 环境变量配置

已预配置在 `start_bot.bat` 中：
- ✅ `APP_ID`: cli_a8fd44a9453cd00c
- ✅ `APP_SECRET`: jsVoFWgaaw05en6418h7xbhV5oXxAwIm
- ✅ `CHAT_ID`: oc_e4218b232326ea81a077b65c4cd16ce5
- ✅ `FILE_URL`: 飞书文档链接
- ✅ `TZ`: Asia/Shanghai

无需手动配置！

---

## 🎯 启动方式

### 方式1：批处理文件（推荐）
```bash
双击 start_bot.bat
```

### 方式2：命令行
```bash
cd F:\monthly_report_bot_link_pack\monthly_report_bot_link_pack
python monthly_report_bot_final_interactive.py
```

---

## ✅ 安装验证

运行以下命令检查环境：

```powershell
# 检查Python
python --version

# 检查依赖包
python -c "import lark_oapi; import pytz; import yaml; print('环境正常')"
```

---

## ❓ 常见问题

### Q1: 提示"python不是内部或外部命令"
**A:** Python未添加到PATH，需要：
1. 重新安装Python，勾选 "Add Python to PATH"
2. 或重启电脑后重试

### Q2: pip安装失败
**A:** 尝试使用国内镜像：
```bash
pip install -r requirements_v1_1.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 依赖包版本冲突
**A:** 使用虚拟环境：
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements_v1_1.txt
```

### Q4: PowerShell脚本无法运行
**A:** 设置执行策略：
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

---

## 📞 获取帮助

如果遇到问题，请检查：
1. Python版本 >= 3.11
2. 网络连接正常
3. 防火墙/杀毒软件未阻止
4. 环境变量配置正确

---

**安装完成后，运行 `start_bot.bat` 即可启动机器人！** 🎉



