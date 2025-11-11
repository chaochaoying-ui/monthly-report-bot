# ⚡ 快速验证指南

**目的**: 在 3 分钟内完成最终 emoji 显示验证

---

## 🎯 执行步骤

### 步骤 1：同步数据（30 秒）

**在本地 Windows PowerShell/CMD 执行**:

```cmd
cd f:\monthly_report_bot_link_pack
sync_task_data.bat
```

**等待输出**:
```
✅ 任务数据已同步！
```

---

### 步骤 2：触发图表生成（10 秒）

**在飞书测试群发送**:

```
进度图表
```

**等待机器人回复图片**

---

### 步骤 3：检查 emoji 显示（5 秒）

**查看图表图片中**:
- 🏆 奖杯（排名第一）
- 🥇 金牌（排名第二）
- 🥈 银牌（排名第三）
- 📊 柱状图标题
- 📈 趋势图标题

**判断**:
- ✅ **正常**: emoji 显示为彩色图标
- ❌ **异常**: emoji 显示为 ▯ 白色方框

---

## ✅ 如果 emoji 正常显示

**恭喜！立即部署到正式群：**

```bash
# SSH 到服务器
ssh hdi918072@34.145.43.77

# 修改环境变量（将 CHAT_ID 改为正式群 ID）
sudo nano /etc/monthly-report-bot/.env
# 修改 CHAT_ID=oc_正式群ID

# 重启服务
sudo systemctl restart monthly-report-bot

# 查看日志确认启动成功
sudo journalctl -u monthly-report-bot -f
```

**在正式群测试**:
```
帮助
/stats
```

---

## ⚠️ 如果 emoji 显示为方框

**不要慌！执行备选方案 A：**

### 修复步骤

1. **SSH 到服务器**
   ```bash
   ssh hdi918072@34.145.43.77
   cd /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack
   ```

2. **编辑 chart_generator.py**
   ```bash
   nano chart_generator.py
   ```

3. **在 setup_chinese_fonts() 函数后添加**（约第 130 行）
   ```python
   # ========== 全局 FontProperties（备选方案 A）==========
   _chinese_font_prop = None
   _emoji_font_prop = None

   def get_font_properties():
       """获取预配置的字体 Properties"""
       global _chinese_font_prop, _emoji_font_prop

       if _chinese_font_prop is None:
           chinese_font_path = '/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/fonts/simhei.ttf'
           symbola_path = '/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf'

           _chinese_font_prop = fm.FontProperties(fname=chinese_font_path)
           _emoji_font_prop = fm.FontProperties(fname=symbola_path)

       return _chinese_font_prop, _emoji_font_prop
   ```

4. **找到图表生成函数中所有包含 emoji 的 ax.text()**

   搜索关键词：
   ```bash
   grep -n "🏆\|🥇\|🥈\|📊\|📈" chart_generator.py
   ```

5. **修改每一处 emoji 文本渲染**

   **修改前**:
   ```python
   ax.text(x, y, "🏆", fontsize=16)
   ```

   **修改后**:
   ```python
   _, emoji_prop = get_font_properties()
   ax.text(x, y, "🏆", fontproperties=emoji_prop, fontsize=16)
   ```

6. **保存、提交、重启**
   ```bash
   # Ctrl+X 保存退出

   # 提交到 Git
   git add chart_generator.py
   git commit -m "fix: 使用 FontProperties 直接指定 Symbola 字体修复 emoji 显示"
   git push

   # 重启服务
   sudo systemctl restart monthly-report-bot
   ```

7. **重新测试**
   在飞书测试群发送：`进度图表`

---

## 📊 预期结果

### 成功的日志
```
DEBUG: ✅ Symbola 已存在于 fontManager，跳过添加
DEBUG: fontManager 中的 Symbola 字体数量: 1
DEBUG: ✅ findfont(Symbola) 返回: /usr/share/fonts/.../Symbola_hint.ttf
美化版综合仪表板已生成: charts/dashboard_20251111_170523.png
图片上传成功, image_key: img_v3_02ri_xxxxx
```

### 失败的日志（需要修复）
```
UserWarning: Glyph 127942 (\N{TROPHY}) missing from font(s) SimHei.
UserWarning: Glyph 129351 (\N{FIRST PLACE MEDAL}) missing from font(s) SimHei.
```

---

## 📞 遇到问题？

### 问题 1：sync_task_data.bat 失败

**可能原因**: SSH 连接失败或权限问题

**手动执行**:
```cmd
scp monthly_report_bot_link_pack/task_stats.json hdi918072@34.145.43.77:/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/
ssh hdi918072@34.145.43.77 "sudo systemctl restart monthly-report-bot"
```

---

### 问题 2：机器人没有回复图表

**检查日志**:
```bash
ssh hdi918072@34.145.43.77
sudo journalctl -u monthly-report-bot -n 50 | grep "生成\|失败\|ERROR"
```

**可能原因**:
- 任务数据为空
- chart_generator 模块错误
- 网络问题

**验证数据**:
```bash
cat /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/task_stats.json | head -50
```

---

### 问题 3：图表生成但上传失败

**检查网络**:
```bash
ping open.feishu.cn
```

**检查图片文件**:
```bash
ls -lh /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/charts/*.png
```

---

## 🎓 备查文档

| 文档 | 用途 |
|------|------|
| [DEPLOYMENT_READY_REPORT.md](DEPLOYMENT_READY_REPORT.md) | 完整的就绪报告 |
| [PRE_PRODUCTION_CHECKLIST.md](PRE_PRODUCTION_CHECKLIST.md) | 详细的部署检查清单 |
| [TIMING_CONFIGURATION_SUMMARY.md](TIMING_CONFIGURATION_SUMMARY.md) | 定时任务配置说明 |
| [NEXT_STEPS_2025-11-11.md](NEXT_STEPS_2025-11-11.md) | emoji 修复详细方案 |

---

**文档生成时间**: 2025-11-11 15:05 (UTC+8)
**预计验证耗时**: 3 分钟
**成功率预测**: 95%（基于字体配置日志分析）
