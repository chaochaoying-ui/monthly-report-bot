# 月报机器人开发错题本 (Pitfalls & Solutions)

> **使用说明**: 每次开发、部署、修复问题前，**必须先阅读本文档**！
> 这里记录了所有踩过的坑和正确的解决方案。避免重复犯错。

**最后更新**: 2025-10-23
**版本**: v1.0

---

## 📌 目录

1. [核心架构问题](#1-核心架构问题)
2. [部署相关问题](#2-部署相关问题)
3. [环境变量问题](#3-环境变量问题)
4. [飞书API调用问题](#4-飞书api调用问题)
5. [数据同步问题](#5-数据同步问题)
6. [字体和图表问题](#6-字体和图表问题)
7. [服务器运维问题](#7-服务器运维问题)

---

## 1. 核心架构问题

### ❌ 坑 #1.1: 使用模拟任务ID而非真实GUID

**问题描述**:
```python
# 错误代码 (monthly_report_bot_ws_v1.1.py:1413)
task_id = f"task_{current_month}_{success_count + 1}"  # ❌ 假ID
logger.info("模拟创建任务: %s (ID: %s)", task_title, task_id)
update_task_completion(task_id, task_config['title'], assignees, False)
```

**影响**:
- ❌ 任务状态无法与飞书同步
- ❌ 每日提醒显示"已完成: 0"
- ❌ 图表统计永远是0%
- ❌ 智能@提醒失效

**根本原因**:
- 本地使用字符串拼接生成假ID: `task_2025-10_1`
- 飞书真实任务GUID格式: `b1c2d3e4-5f6a-7b8c-9d0e-1f2a3b4c5d6e`
- 用假ID查询飞书API时返回"任务不存在"

**✅ 正确做法**:
```python
# 正确代码 (monthly_report_bot_ws_v1.1.py:1422-1461)
request = CreateTaskRequest.builder() \
    .request_body(CreateTaskRequestBody.builder()
                .summary(task_title)
                .description(f"月度报告任务: {task_config['title']}\n文档链接: {task_config.get('doc_url', '')}")
                .due(CreateTaskRequestBodyDue.builder()
                    .timestamp(str(due_timestamp))
                    .is_all_day(False)
                    .build())
                .build()) \
    .build()

# ✅ 真正调用飞书API
response = await lark_client.task.v2.task.acreate(request)

if response.success():
    task_guid = response.data.task.guid  # ✅ 使用飞书返回的真实GUID
    logger.info("✅ 任务创建成功: %s (GUID: %s)", task_title, task_guid)

    # ✅ 使用真实GUID保存
    update_task_completion(task_guid, task_config['title'], assignees, False)
else:
    logger.error(f"❌ 任务创建失败: {response.msg}")
```

**关键点**:
1. ✅ 必须调用 `lark_client.task.v2.task.acreate(request)`
2. ✅ 必须从响应中提取 `response.data.task.guid`
3. ✅ 必须使用真实GUID保存到 `task_stats.json`
4. ✅ 未来所有任务操作都使用这个GUID

**验证方法**:
```bash
# 检查 task_stats.json 中的任务ID格式
cat task_stats.json | grep "task_2025"  # 不应该有输出
cat task_stats.json | grep -E "[a-f0-9]{8}-[a-f0-9]{4}"  # 应该能看到GUID
```

**修复时间**: 2025-10-23
**严重程度**: 🔴 极高 - 导致核心功能失效

---

### ❌ 坑 #1.2: 同步任务时用错误的API

**问题描述**:
尝试使用 `ListTaskRequest` API列出所有任务，但一直失败：
```python
request = ListTaskRequest.builder() \
    .page_size(100) \
    .build()
response = await client.task.v2.task.alist(request)
# ❌ 错误: code=99991668, msg=Invalid access token for authorization
```

**影响**:
- ❌ 无法获取飞书中的真实任务列表
- ❌ 无法同步已存在任务的状态

**根本原因**:
- `ListTaskRequest` API 需要特殊的权限或认证方式
- 即使 APP_ID 和 APP_SECRET 正确，也可能因权限不足而失败

**❌ 错误尝试**:
```python
# 尝试1: 添加 log_level (无效)
lark_client = lark.Client.builder() \
    .app_id(APP_ID) \
    .app_secret(APP_SECRET) \
    .log_level(lark.LogLevel.ERROR) \  # ❌ 无效，参考代码中没有这个参数
    .build()

# 尝试2: 在bash中加载环境变量 (无效)
set -a && source .env && set +a && python3 sync_existing_tasks.py
```

**✅ 正确做法**:
使用 `GetTaskRequest` 查询单个任务，而不是列出所有任务：

```python
# sync_task_status_only.py
async def check_task_status(client, task_guid: str) -> int:
    """查询单个任务状态"""
    request = GetTaskRequest.builder() \
        .task_guid(task_guid) \
        .build()

    response = await client.task.v2.task.aget(request)

    if response.success():
        task = response.data.task
        return task.complete  # 2=completed, 1=in progress
    else:
        logger.error(f"查询失败: {task_guid[:20]}... (code={response.code})")
        return 0
```

**更好的方案**:
如果需要获取所有任务的GUID，应该：
1. 在任务创建时就保存正确的GUID（修复 #1.1 已解决）
2. 或者让有权限的用户手动从飞书web界面获取任务链接，从中提取GUID

**关键点**:
1. ❌ 不要依赖 `ListTaskRequest` - 权限问题很难解决
2. ✅ 使用 `GetTaskRequest` 查询已知GUID的任务
3. ✅ 在创建任务时就保存GUID，避免后续需要列出所有任务

**教训**:
- 遇到API权限问题时，不要盲目尝试各种配置
- 应该先参考已经验证过的正确代码（如 `monthly_report_bot_final_interactive.py`）
- 考虑更换API端点，而不是一直尝试修复同一个失败的API

**修复时间**: 2025-10-23
**严重程度**: 🟡 中等 - 有替代方案

---

## 2. 部署相关问题

### ❌ 坑 #2.1: SCP上传权限被拒绝

**问题描述**:
```bash
$ scp monthly_report_bot_ws_v1.1.py hdi918072@34.145.43.77:/home/hdi918072/monthly_report_bot/
hdi918072@34.145.43.77: Permission denied (publickey).
```

**影响**:
- ❌ 无法直接上传文件到服务器

**根本原因**:
- 服务器配置了SSH密钥认证
- 本地机器没有配置正确的SSH私钥

**❌ 错误做法**:
尝试配置SSH密钥（复杂且容易出错）

**✅ 正确做法**:
使用 GitHub 作为中转：

```bash
# 1. 推送到 GitHub
cd f:/monthly_report_bot_link_pack/monthly_report_bot_link_pack
git add monthly_report_bot_ws_v1.1.py sync_existing_tasks.py
git commit -m "fix: 修复任务同步问题"
git push origin main

# 2. SSH 登录服务器
ssh hdi918072@34.145.43.77

# 3. 在服务器上拉取
cd /home/hdi918072/monthly-report-bot  # ⚠️ 注意是 monthly-report-bot (带连字符)
git pull origin main
```

**关键点**:
1. ✅ Git push/pull 工作流更可靠
2. ✅ 代码有版本控制，更安全
3. ✅ 不需要配置SSH密钥
4. ⚠️ 注意不要把敏感信息（.env文件）提交到Git

**用户原话**:
> "之前是推送到github,然后再google cloud上下载。"

**修复时间**: 2025-10-23
**严重程度**: 🟢 低 - 有成熟的替代方案

---

### ❌ 坑 #2.2: 服务器目录路径错误

**问题描述**:
```bash
$ cd /home/hdi918072/monthly_report_bot
-bash: cd: /home/hdi918072/monthly_report_bot: No such file or directory
```

**影响**:
- ❌ 找不到项目目录
- ❌ 无法运行脚本

**根本原因**:
- 实际目录名是 `monthly-report-bot` (带连字符 `-`)
- 不是 `monthly_report_bot` (下划线 `_`)

**✅ 正确路径**:
```bash
# ✅ 正确
cd /home/hdi918072/monthly-report-bot

# ❌ 错误
cd /home/hdi918072/monthly_report_bot
```

**关键点**:
1. ✅ 登录服务器后先用 `ls -la` 确认目录名
2. ✅ 使用 tab 键自动补全，避免拼写错误
3. ✅ 在脚本中使用正确的路径常量

**验证方法**:
```bash
# 确认目录是否存在
ls -ld /home/hdi918072/monthly-report-bot
# 应该输出: drwxr-xr-x ... /home/hdi918072/monthly-report-bot
```

**修复时间**: 2025-10-23
**严重程度**: 🟢 低 - 容易修复

---

### ❌ 坑 #2.3: 部署脚本变量配置错误

**问题描述**:
一键部署脚本中的服务器配置可能过时或错误。

**影响**:
- ❌ 自动化部署失败

**✅ 正确配置**:
在 `deploy_task_sync_fix.bat` 或 `.sh` 中确认：

```bash
# 服务器配置
SERVER_USER=hdi918072
SERVER_IP=34.145.43.77
REMOTE_DIR=/home/hdi918072/monthly-report-bot  # ⚠️ 注意连字符
SERVICE_NAME=monthly-report-bot  # ⚠️ 服务名也是连字符
```

**验证方法**:
```bash
# 在服务器上检查服务名
sudo systemctl list-units | grep monthly
# 应该看到: monthly-report-bot.service
```

**关键点**:
1. ✅ 服务名和目录名一致
2. ✅ 使用连字符 `-` 而不是下划线 `_`
3. ✅ 部署前先手动验证一次配置

**修复时间**: 2025-10-23
**严重程度**: 🟡 中等 - 影响自动化部署

---

## 3. 环境变量问题

### ❌ 坑 #3.1: 环境变量命名格式错误

**问题描述**:
脚本中使用了错误的环境变量名：
```python
# ❌ 错误格式
app_id = os.environ.get('FEISHU_APP_ID')
app_secret = os.environ.get('FEISHU_APP_SECRET')
```

但 `.env` 文件中的实际格式是：
```bash
# ✅ 正确格式
APP_ID=cli_a67920ceb9fad013
APP_SECRET=xxxxxxxxxxxxxxx
```

**影响**:
- ❌ 脚本无法读取到 APP_ID 和 APP_SECRET
- ❌ 飞书API调用失败

**根本原因**:
- 不同项目可能使用不同的命名约定
- 有的用 `FEISHU_APP_ID`，有的用 `APP_ID`

**用户反馈**:
> "FEISHU_APP_ID=cli_xxxxxxxxxxxxx FEISHU_APP_SECRET=xxxxxxxxxxxxx，这个格式是错的。请查询上下文中的记录，这个问题之前遇到已经解决了一次"

**✅ 正确做法**:
```python
# 兼容两种格式
app_id = os.environ.get('APP_ID') or os.environ.get('FEISHU_APP_ID')
app_secret = os.environ.get('APP_SECRET') or os.environ.get('FEISHU_APP_SECRET')

if not app_id or not app_secret:
    print("❌ 错误: 未找到 APP_ID 和 APP_SECRET")
    print("请检查 .env 文件中是否包含:")
    print("  APP_ID=cli_...")
    print("  APP_SECRET=...")
    sys.exit(1)
```

**关键点**:
1. ✅ 优先使用项目约定的格式（`APP_ID`）
2. ✅ 兼容其他可能的命名（`FEISHU_APP_ID`）
3. ✅ 启动时验证环境变量是否存在
4. ✅ 参考已验证的代码（`monthly_report_bot_final_interactive.py`）

**参考代码** (monthly_report_bot_final_interactive.py:138-141):
```python
lark_client = lark.Client.builder() \
    .app_id(APP_ID) \
    .app_secret(APP_SECRET) \
    .build()
# ⚠️ 注意：没有 .log_level() 参数！
```

**修复时间**: 2025-10-23
**严重程度**: 🔴 高 - 导致API调用失败

---

### ❌ 坑 #3.2: 环境变量未正确加载

**问题描述**:
即使 `.env` 文件存在，脚本也可能无法读取到环境变量。

**影响**:
- ❌ 脚本运行失败
- ❌ 提示找不到 APP_ID

**❌ 错误尝试**:
```bash
# 尝试在 bash 命令行中设置
set -a && source .env && set +a && python3 sync_existing_tasks.py
# 结果：仍然失败
```

**根本原因**:
- Python脚本没有正确加载 `.env` 文件
- 或者路径不对

**✅ 正确做法**:
```python
from dotenv import load_dotenv
import os

# 确保从正确的路径加载 .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# 或者明确指定 .env 路径
load_dotenv('/home/hdi918072/monthly-report-bot/.env')

# 读取环境变量
APP_ID = os.environ.get('APP_ID')
APP_SECRET = os.environ.get('APP_SECRET')

# 验证
if not APP_ID:
    print(f"❌ 错误: .env 文件路径: {env_path}")
    print(f"❌ 错误: 文件是否存在: {os.path.exists(env_path)}")
    sys.exit(1)
```

**关键点**:
1. ✅ 使用 `python-dotenv` 库加载 `.env`
2. ✅ 明确指定 `.env` 文件路径
3. ✅ 添加调试日志确认文件是否加载成功
4. ✅ 在脚本开头就加载并验证环境变量

**修复时间**: 2025-10-23
**严重程度**: 🟡 中等 - 影响脚本运行

---

## 4. 飞书API调用问题

### ❌ 坑 #4.1: 错误添加不存在的客户端参数

**问题描述**:
尝试添加 `.log_level()` 参数来解决API调用问题：
```python
# ❌ 错误代码
lark_client = lark.Client.builder() \
    .app_id(APP_ID) \
    .app_secret(APP_SECRET) \
    .log_level(lark.LogLevel.ERROR) \  # ❌ 这个参数不存在！
    .build()
```

**影响**:
- ❌ 代码无法运行
- ❌ 浪费时间调试

**根本原因**:
- 盲目尝试各种参数，没有参考已验证的代码
- `lark_oapi` SDK 的 Client.builder() 不支持 `log_level()` 参数

**用户反馈**:
> "请参考...代码。这是之前已经验证过的正确方案，不要总是不停地试"

**✅ 正确做法**:
参考已验证的代码（`monthly_report_bot_final_interactive.py:138-141`）：
```python
# ✅ 正确代码（简洁且有效）
lark_client = lark.Client.builder() \
    .app_id(APP_ID) \
    .app_secret(APP_SECRET) \
    .build()
```

**关键点**:
1. ✅ 遇到问题时，先参考项目中已验证的代码
2. ❌ 不要盲目尝试各种参数组合
3. ✅ 如果需要调试，使用 Python logging 而不是修改 SDK 配置
4. ✅ 阅读官方文档确认API参数

**教训**:
- **不要瞎试！** 先看已有的正确代码
- 用户明确指出这是重复犯错，应该避免

**修复时间**: 2025-10-23
**严重程度**: 🟡 中等 - 浪费时间

---

### ❌ 坑 #4.2: 飞书API错误码处理不当

**问题描述**:
遇到飞书API错误码时，没有正确处理：
```python
# 错误码示例
# 99991668 - Invalid access token for authorization
# 1470400 - Task not found
```

**影响**:
- ❌ 不知道问题的真正原因
- ❌ 尝试错误的修复方案

**根本原因**:
- 没有理解错误码的真正含义
- 没有检查日志中的详细错误信息

**✅ 正确做法**:

1. **错误码 99991668 (Invalid access token)**:
   - 不一定是认证问题
   - 可能是API端点不支持或权限不足
   - 应该尝试换一个API端点（如从 `ListTaskRequest` 改为 `GetTaskRequest`）

2. **错误码 1470400 (Task not found)**:
   - 明确表示任务不存在
   - 说明使用的任务ID是错误的（假ID）
   - 应该检查任务ID的来源和格式

```python
# ✅ 正确的错误处理
response = await client.task.v2.task.aget(request)

if not response.success():
    error_code = response.code
    error_msg = response.msg

    if error_code == 1470400:
        # 任务不存在 - 说明任务ID错误
        logger.warning(f"任务不存在: {task_guid}, 可能是使用了模拟ID")
    elif error_code == 99991668:
        # 权限问题 - 考虑换API或检查应用权限
        logger.error(f"API权限不足: {error_msg}, 考虑使用其他API端点")
    else:
        logger.error(f"未知错误: code={error_code}, msg={error_msg}")

    return None
```

**关键点**:
1. ✅ 记录详细的错误码和消息
2. ✅ 根据错误码采取正确的应对措施
3. ✅ 不要盲目尝试修改认证配置
4. ✅ 考虑问题的根本原因（如任务ID格式错误）

**修复时间**: 2025-10-23
**严重程度**: 🟡 中等 - 影响问题诊断

---

## 5. 数据同步问题

### ❌ 坑 #5.1: task_stats.json 中的假ID无法同步

**问题描述**:
`task_stats.json` 中存储了23个假任务ID：
```json
{
  "tasks": {
    "task_2025-10_1": {...},  // ❌ 假ID
    "task_2025-10_2": {...},  // ❌ 假ID
    ...
  }
}
```

**影响**:
- ❌ 查询飞书API时全部返回"任务不存在"
- ❌ 无法同步任务完成状态
- ❌ 已完成的任务无法统计

**根本原因**:
- 创建任务时使用了模拟ID（见坑 #1.1）
- 导致本地数据与飞书数据不一致

**✅ 解决方案**:

**方案A: 如果飞书中存在真实任务**
1. 使用同步脚本从飞书获取任务列表
2. 根据任务标题匹配
3. 用真实GUID替换假ID

```python
# sync_existing_tasks.py
# 获取飞书任务 -> 匹配标题 -> 更新 task_stats.json
```

**方案B: 如果飞书中不存在任务**
1. 使用修复后的代码重新创建任务
2. 之前的完成记录可能需要手动恢复

**关键点**:
1. ✅ 先确认飞书中是否存在对应的任务
2. ✅ 如果存在，必须获取真实GUID
3. ✅ 更新 `task_stats.json` 时保留完成状态和时间戳
4. ✅ 备份原文件以防数据丢失

**验证方法**:
```bash
# 检查更新后的 task_stats.json
cat task_stats.json | python3 -m json.tool | grep -A 5 "tasks"

# 应该看到 GUID 格式而不是 task_2025-10_1
```

**修复时间**: 2025-10-23
**严重程度**: 🔴 极高 - 影响核心数据一致性

---

### ❌ 坑 #5.2: 同步时覆盖了已完成状态

**问题描述**:
同步任务时可能会错误地覆盖本地的完成状态。

**影响**:
- ❌ 本地记录的已完成任务变成未完成
- ❌ 统计数据回退

**根本原因**:
- 同步逻辑没有正确处理已完成状态的保留

**✅ 正确做法**:
```python
# 同步时应该合并状态，而不是覆盖
def sync_task_status(local_task, feishu_task):
    """
    合并本地和飞书的任务状态
    规则：以飞书状态为准，但保留本地的完成时间戳
    """
    feishu_completed = (feishu_task.complete == 2)  # 2 表示已完成
    local_completed = local_task.get('completed', False)

    if feishu_completed:
        # 飞书显示已完成，更新本地状态
        local_task['completed'] = True
        if not local_task.get('completed_at'):
            # 如果本地没有完成时间，使用当前时间
            local_task['completed_at'] = datetime.now().isoformat()
    elif not feishu_completed and local_completed:
        # 飞书显示未完成，但本地显示已完成
        # 可能是任务被重新打开，更新为未完成
        logger.warning(f"任务 {local_task['title']} 在飞书中被重新打开")
        local_task['completed'] = False
        local_task['completed_at'] = None

    return local_task
```

**关键点**:
1. ✅ 以飞书状态为权威来源
2. ✅ 保留本地的完成时间戳
3. ✅ 记录状态变化的日志
4. ✅ 同步前备份 `task_stats.json`

**修复时间**: 2025-10-23
**严重程度**: 🔴 高 - 可能导致数据丢失

---

## 6. 字体和图表问题

### ❌ 坑 #6.1: Ubuntu服务器中文乱码

**问题描述**:
生成的图表中，中文显示为方框乱码。

**影响**:
- ❌ 图表中文不可读
- ❌ 用户体验差

**根本原因**:
- Ubuntu服务器默认没有安装中文字体
- matplotlib 找不到合适的中文字体

**✅ 解决方案**:

**方法1: 安装系统字体**
```bash
# 安装 Noto CJK 字体
sudo apt-get update
sudo apt-get install fonts-noto-cjk

# 清除 matplotlib 字体缓存
rm -rf ~/.cache/matplotlib
```

**方法2: 使用自定义字体文件**
```python
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 加载自定义字体
font_path = "/path/to/NotoSansCJK-Regular.ttc"
font_prop = FontProperties(fname=font_path)

# 设置字体
plt.rcParams['font.sans-serif'] = [font_prop.get_name()]
plt.rcParams['axes.unicode_minus'] = False
```

**方法3: 直接从字体文件加载 (推荐)**
```python
from matplotlib.font_manager import fontManager

# 添加字体文件
font_path = "./fonts/NotoSansCJK-Regular.ttc"
fontManager.addfont(font_path)

# 使用字体
plt.rcParams['font.family'] = 'Noto Sans CJK SC'
```

**关键点**:
1. ✅ 优先使用系统字体（简单可靠）
2. ✅ 如果系统字体不可用，提供字体文件
3. ✅ 测试时检查图片的中文显示
4. ✅ 添加异常处理和日志

**相关提交**:
- `fdc728a` - fix: 修复 Ubuntu 服务器上的中文字体显示问题
- `b981458` - fix: 强化字体加载逻辑 - 直接从文件加载 Noto CJK
- `c71f9b8` - feat: 支持自定义字体文件上传

**修复时间**: 2025-10-21 (之前已修复)
**严重程度**: 🟡 中等 - 影响用户体验

---

### ❌ 坑 #6.2: 图片上传飞书失败

**问题描述**:
生成图表后上传到飞书时失败。

**影响**:
- ❌ 用户无法看到统计图表

**可能原因**:
1. 图片二进制数据处理不当
2. Content-Type 设置错误
3. 图片文件损坏

**✅ 解决方案**:
```python
from io import BytesIO

# 生成图表
fig, ax = plt.subplots()
# ... 绘图逻辑 ...

# 保存到内存
img_buffer = BytesIO()
plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
img_buffer.seek(0)  # ⚠️ 重要：重置指针到开头

# 上传到飞书
try:
    # 读取二进制数据
    img_data = img_buffer.read()

    # 上传
    request = CreateImageRequest.builder() \
        .request_body(CreateImageRequestBody.builder()
                     .image_type("message")
                     .image(img_data)  # 传入二进制数据
                     .build()) \
        .build()

    response = await lark_client.im.v1.image.create(request)

    if response.success():
        image_key = response.data.image_key
        logger.info(f"✅ 图片上传成功: {image_key}")
    else:
        logger.error(f"❌ 图片上传失败: {response.msg}")

except Exception as e:
    logger.error(f"❌ 图片上传异常: {str(e)}", exc_info=True)
finally:
    img_buffer.close()
    plt.close(fig)  # ⚠️ 释放图表资源
```

**关键点**:
1. ✅ 使用 `BytesIO` 而不是临时文件
2. ✅ 上传前调用 `seek(0)` 重置指针
3. ✅ 添加详细的异常日志
4. ✅ 上传后关闭 buffer 和图表对象

**相关提交**:
- `a894b10` - fix: 使用 BytesIO 包装图片数据并添加详细异常日志

**修复时间**: 2025-10-21 (之前已修复)
**严重程度**: 🟡 中等 - 影响功能可用性

---

## 7. 服务器运维问题

### ❌ 坑 #7.1: 服务重启后配置未生效

**问题描述**:
修改代码后重启服务，但修改未生效。

**影响**:
- ❌ 旧代码继续运行
- ❌ 修复无效

**可能原因**:
1. 文件上传到错误的目录
2. systemd 缓存了旧的服务配置
3. Python 字节码缓存 (`.pyc`) 未更新

**✅ 解决方案**:

**步骤1: 验证文件是否正确上传**
```bash
# 检查文件修改时间
ls -lh /home/hdi918072/monthly-report-bot/monthly_report_bot_ws_v1.1.py

# 检查文件内容（查看最近修改的行）
tail -n 50 /home/hdi918072/monthly-report-bot/monthly_report_bot_ws_v1.1.py
```

**步骤2: 清除 Python 字节码缓存**
```bash
find /home/hdi918072/monthly-report-bot -name "*.pyc" -delete
find /home/hdi918072/monthly-report-bot -name "__pycache__" -type d -exec rm -rf {} +
```

**步骤3: 重新加载 systemd 并重启**
```bash
sudo systemctl daemon-reload
sudo systemctl restart monthly-report-bot
sudo systemctl status monthly-report-bot
```

**步骤4: 查看实时日志确认**
```bash
sudo journalctl -u monthly-report-bot -f
# 应该看到最新的日志输出
```

**关键点**:
1. ✅ 验证文件确实已更新
2. ✅ 清除 Python 缓存
3. ✅ daemon-reload 后再 restart
4. ✅ 查看日志确认新代码运行

**修复时间**: 2025-10-23
**严重程度**: 🟡 中等 - 影响部署验证

---

### ❌ 坑 #7.2: 虚拟环境路径错误

**问题描述**:
在服务器上运行Python脚本时，找不到依赖包。

**影响**:
- ❌ 脚本无法运行
- ❌ ImportError

**根本原因**:
- 没有激活虚拟环境
- 或者激活了错误的虚拟环境

**✅ 正确做法**:
```bash
# 1. 进入项目目录
cd /home/hdi918072/monthly-report-bot

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 确认 Python 路径
which python3
# 应该输出: /home/hdi918072/monthly-report-bot/venv/bin/python3

# 4. 确认依赖包
pip list | grep lark-oapi

# 5. 运行脚本
python3 sync_existing_tasks.py
```

**关键点**:
1. ✅ 每次运行脚本前先激活虚拟环境
2. ✅ 使用 `which python3` 确认路径
3. ✅ 如果依赖缺失，重新安装: `pip install -r requirements.txt`

**修复时间**: 2025-10-23
**严重程度**: 🟢 低 - 容易修复

---

### ❌ 坑 #7.3: 服务日志文件过大

**问题描述**:
长期运行后，systemd 日志文件变得非常大。

**影响**:
- ❌ 磁盘空间占用
- ❌ 查看日志变慢

**✅ 解决方案**:

**查看日志大小**:
```bash
sudo journalctl --disk-usage
```

**清理旧日志**:
```bash
# 只保留最近7天的日志
sudo journalctl --vacuum-time=7d

# 或者限制日志大小为 100M
sudo journalctl --vacuum-size=100M
```

**配置日志轮转**:
编辑 `/etc/systemd/journald.conf`:
```ini
[Journal]
SystemMaxUse=100M
SystemMaxFileSize=10M
```

然后重启 journald:
```bash
sudo systemctl restart systemd-journald
```

**关键点**:
1. ✅ 定期清理旧日志
2. ✅ 配置日志大小限制
3. ✅ 在应用层面控制日志输出量

**修复时间**: 未遇到（预防性建议）
**严重程度**: 🟢 低 - 运维优化

---

## 📝 错误记录模板

每次遇到新的坑，按照以下模板记录：

```markdown
### ❌ 坑 #X.Y: [简短描述]

**问题描述**:
[详细描述问题现象，包括错误信息]

**影响**:
- ❌ [影响1]
- ❌ [影响2]

**根本原因**:
[分析问题的根本原因]

**❌ 错误尝试** (如果有):
[记录尝试过但失败的方案]

**✅ 正确做法**:
[正确的解决方案，包括代码示例]

**关键点**:
1. ✅ [要点1]
2. ✅ [要点2]
3. ❌ [要避免的做法]

**用户反馈** (如果有):
> [用户的原话]

**验证方法**:
[如何验证修复是否成功]

**相关文件**:
- [文件路径:行号]

**修复时间**: YYYY-MM-DD
**严重程度**: 🔴 极高 / 🟡 中等 / 🟢 低
```

---

## 🎯 部署前检查清单

每次部署新代码前，**必须**检查以下项目：

### 1. 代码检查
- [ ] 所有环境变量使用正确的命名（`APP_ID` 而非 `FEISHU_APP_ID`）
- [ ] 飞书客户端初始化不包含多余参数（不要加 `.log_level()`）
- [ ] 任务创建使用真实API调用（不是模拟）
- [ ] 使用真实GUID保存任务（不是拼接的假ID）
- [ ] 错误处理完整（记录详细日志）

### 2. 环境检查
- [ ] `.env` 文件存在且包含正确的 APP_ID 和 APP_SECRET
- [ ] 虚拟环境已激活
- [ ] 所有依赖包已安装（`pip list | grep lark-oapi`）
- [ ] Python版本正确（`python3 --version`）

### 3. 服务器检查
- [ ] 目录路径正确（`/home/hdi918072/monthly-report-bot`）
- [ ] 服务名正确（`monthly-report-bot`）
- [ ] 有备份旧文件（`cp xxx xxx.backup`）
- [ ] Git 仓库状态干净（`git status`）

### 4. 部署步骤
- [ ] 推送到 GitHub: `git push origin main`
- [ ] SSH 登录服务器
- [ ] 拉取最新代码: `git pull origin main`
- [ ] 运行同步脚本（如果需要）: `python3 sync_existing_tasks.py`
- [ ] 重启服务: `sudo systemctl restart monthly-report-bot`
- [ ] 查看服务状态: `sudo systemctl status monthly-report-bot`
- [ ] 查看实时日志: `sudo journalctl -u monthly-report-bot -f`

### 5. 验证测试
- [ ] 在飞书群聊发送 `状态` 命令
- [ ] 检查已完成任务数是否正确（不是0）
- [ ] 发送 `图表` 命令
- [ ] 检查图表是否显示正确（中文无乱码）
- [ ] 等待下一次每日提醒，验证数据准确性

---

## 🧠 关键教训

### 1. 不要盲目尝试 (Don't Try Random Solutions)

**错误示范**:
- 尝试添加 `.log_level()` 参数
- 尝试各种环境变量命名
- 不断修改认证配置

**正确做法**:
- ✅ 先参考项目中已验证的代码
- ✅ 阅读错误日志，理解真正的原因
- ✅ 一次只改一个地方，验证后再继续

**用户原话**:
> "不要总是不停地试"

---

### 2. 参考已验证的代码 (Reference Proven Code)

**关键文件**:
- `monthly_report_bot_final_interactive.py` - 已验证的正确实现

**用户原话**:
> "请参考...代码。这是之前已经验证过的正确方案"
> "这个问题直接也解决过，请阅读上下文"

**要点**:
- ✅ 项目中可能已经有正确的实现
- ✅ 先搜索类似的代码
- ✅ 复用而不是重新发明

---

### 3. 理解根本原因 (Understand Root Cause)

**错误示范**:
- 看到认证错误就修改认证配置
- 看到API失败就换各种参数

**正确做法**:
- ✅ 错误码 99991668 可能是权限问题，考虑换API
- ✅ 错误码 1470400 说明ID错误，检查ID来源
- ✅ 深入分析问题的根源，而不是表面症状

---

### 4. 使用成熟的工作流 (Use Proven Workflows)

**部署工作流**:
1. 本地开发和测试
2. 推送到 GitHub
3. 服务器上 git pull
4. 备份旧文件
5. 重启服务
6. 验证日志

**不要**:
- ❌ 直接在服务器上修改代码
- ❌ 没有备份就覆盖文件
- ❌ 没有版本控制

---

### 5. 阅读错题本 (Read This Document First)

**每次开发前**:
- ✅ 先阅读本文档
- ✅ 检查是否有类似的问题已经解决过
- ✅ 使用部署前检查清单

**每次遇到问题后**:
- ✅ 记录到本文档
- ✅ 包含详细的原因和解决方案
- ✅ 标注严重程度和修复时间

---

## 📚 参考资料

### 项目文档
- [TASK_SYNC_FIX.md](TASK_SYNC_FIX.md) - 任务同步问题修复详细说明
- [QUICK_FIX_GUIDE.md](QUICK_FIX_GUIDE.md) - 快速修复指南
- [SYNC_FIX_SUMMARY.md](SYNC_FIX_SUMMARY.md) - 修复总结
- [COMPLETE_FEATURES_AND_SUMMARY.md](COMPLETE_FEATURES_AND_SUMMARY.md) - 功能完成总结

### 已验证的代码
- `monthly_report_bot_final_interactive.py` - 参考实现
- `monthly_report_bot_ws_v1.1.py` - 当前版本（已修复）

### 工具脚本
- `sync_existing_tasks.py` - 任务同步工具
- `deploy_task_sync_fix.bat` - Windows 部署脚本
- `deploy_task_sync_fix.sh` - Linux/Mac 部署脚本

### 飞书开放平台
- [飞书开放平台文档](https://open.feishu.cn/document/)
- [任务API v2 文档](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/overview)
- [lark-oapi SDK](https://github.com/larksuite/oapi-sdk-python)

---

## 🆕 新增错误记录区

_(每次遇到新问题后，在这里添加记录，然后移动到对应的章节)_

<!--
模板：

### ❌ 坑 #X.Y: [问题简述]

**发现时间**: YYYY-MM-DD
**问题描述**: ...
**解决方案**: ...
**关键要点**: ...

-->

---

**提醒**:
- 🚨 每次开发前先阅读本文档
- 🚨 遇到问题时先搜索本文档
- 🚨 解决新问题后及时更新本文档

**文档维护**:
- 定期审查和归类新增的错误记录
- 更新严重程度和修复状态
- 添加更多验证方法和测试用例
