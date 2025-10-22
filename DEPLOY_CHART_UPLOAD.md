# 🚀 部署图表上传功能

## 📋 更新内容

✅ **已修复的问题**：
- 图表生成成功但只显示文件名，无法直接查看
- 用户收到"图表文件: dashboard_20251022_153640.png"但不知道在哪里打开

✅ **新增功能**：
- 自动上传图表图片到飞书
- 在消息中直接展示美化的图表
- 包含金银铜排行榜的综合统计仪表板
- 完整的错误处理和降级方案

---

## 🔧 部署步骤

### 1️⃣ 登录 GCP 服务器

```bash
ssh hdi918072@<your-gcp-ip>
```

### 2️⃣ 进入项目目录并拉取最新代码

```bash
cd ~/monthly-report-bot/monthly_report_bot_link_pack
git pull origin main
```

### 3️⃣ 验证更新内容

```bash
# 查看最新提交
git log -1 --oneline

# 应该显示: feat: 添加图表图片上传和展示功能
```

### 4️⃣ 检查依赖（已安装可跳过）

```bash
# 激活虚拟环境
source venv/bin/activate

# 检查依赖
python3 << 'EOF'
import matplotlib, seaborn, numpy
print("✅ matplotlib:", matplotlib.__version__)
print("✅ seaborn:", seaborn.__version__)
print("✅ numpy:", numpy.__version__)
EOF
```

如果依赖缺失，运行：
```bash
pip install matplotlib seaborn numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 5️⃣ 重启服务

```bash
# 重启服务
sudo systemctl restart monthly-report-bot.service

# 检查服务状态
sudo systemctl status monthly-report-bot.service
```

预期输出：
```
● monthly-report-bot.service - Monthly Report Bot
   Loaded: loaded
   Active: active (running) since ...
```

### 6️⃣ 查看日志确认启动成功

```bash
# 查看最新日志
tail -f ~/monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot_final.log
```

预期看到：
```
月报机器人 v1.3 交互增强版 - 核心功能 + Echo
...
INFO 客户端初始化完成
```

---

## ✅ 验证部署

### 方法一：在飞书群聊中测试

1. 在飞书群聊中发送：`图表`
2. 预期效果：
   - 收到一张交互式卡片
   - 卡片标题：📊 任务统计图表
   - 卡片内容：统计数据 + 美化的图表图片
   - 图表包含：饼状图、进度条、金银铜排行榜

### 方法二：检查生成的图表文件

```bash
cd ~/monthly-report-bot/monthly_report_bot_link_pack
ls -lht charts/*.png | head -3
```

---

## 🎯 功能说明

### 触发关键词
在飞书群聊中发送以下任一关键词即可生成图表：
- `图表`
- `可视化`
- `饼图`
- `统计图`
- `图表统计`
- `chart`
- `visualization`
- `pie`
- `dashboard`

### 返回内容

**成功时**：返回包含以下内容的交互式卡片
- 📊 标题：任务统计图表
- 📈 统计数据：总任务数、已完成、待完成、完成率
- 🖼️ 图表图片：综合统计仪表板
- 💡 说明文字：图表包含多维度分析

**失败时**：返回友好的错误提示
- 依赖缺失：提示检查依赖库安装
- 图片上传失败：返回文本形式的统计数据
- 无任务数据：提示当前没有任务

---

## 🔍 故障排查

### 问题 1：服务无法启动

**检查日志**：
```bash
sudo journalctl -u monthly-report-bot.service -n 50
```

**常见原因**：
- Python 依赖缺失
- 虚拟环境路径错误
- 环境变量未设置

### 问题 2：图表不显示

**检查**：
1. 依赖是否安装在虚拟环境中
   ```bash
   source venv/bin/activate
   pip list | grep -E "matplotlib|seaborn|numpy"
   ```

2. 图表文件是否生成
   ```bash
   ls -la charts/
   ```

3. 查看服务日志
   ```bash
   tail -100 monthly_report_bot_final.log | grep -i "图表\|chart\|image"
   ```

### 问题 3：图片上传失败

**可能原因**：
- 网络连接问题
- 飞书 API 权限不足
- 图片文件过大（>10MB）

**解决方案**：
- 检查服务器网络连接
- 确认飞书应用权限包含 `im:message` 和 `im:image`
- 查看日志中的详细错误信息

---

## 📝 技术细节

### 新增代码位置

**文件**：`monthly_report_bot_ws_v1.1.py`

**新增函数**：
- `upload_image(image_path: str) -> Optional[str]`
  - 功能：上传图片到飞书，返回 image_key
  - 位置：第 773-807 行

**修改函数**：
- `generate_chart_response() -> Tuple[Optional[str], Optional[Dict[str, Any]]]`
  - 改动：返回 (chart_path, stats) 元组而非文本
  - 位置：第 923-950 行

- `handle_message_event(event: Dict[str, Any]) -> bool`
  - 改动：新增图表请求处理逻辑（上传图片并发送卡片）
  - 位置：第 1035-1114 行

### 使用的飞书 API

- **CreateImageRequest**：上传图片
  - API: `lark_client.im.v1.image.acreate()`
  - 参数：image_type="message", image=二进制数据
  - 返回：image_key

- **ReplyMessageRequest**：回复消息
  - API: `lark_client.im.v1.message.areply()`
  - 支持类型：text（文本）、interactive（卡片）

### 卡片结构

```json
{
  "config": {"wide_screen_mode": true},
  "header": {
    "title": {"tag": "plain_text", "content": "📊 任务统计图表"},
    "template": "blue"
  },
  "elements": [
    {
      "tag": "div",
      "text": {"tag": "lark_md", "content": "统计数据..."}
    },
    {
      "tag": "img",
      "img_key": "<image_key>",
      "alt": {"tag": "plain_text", "content": "任务统计图表"}
    },
    {
      "tag": "div",
      "text": {"tag": "lark_md", "content": "说明文字..."}
    }
  ]
}
```

---

## 🎉 完成！

部署完成后，在飞书群聊中发送"图表"即可看到美化的统计图表！

如有问题，请查看日志：
```bash
tail -100 ~/monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot_final.log
```
