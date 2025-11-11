# 下一步操作指南 - 2025-11-11

## 📋 当前状态

### ✅ 已完成
1. 修复了 ParseException 错误（findfont 测试使用文件路径而不是 family 名称）
2. 防止 Symbola 字体重复注册（添加存在性检查）
3. 代码已推送到 GitHub (commit: 6dfb11d)

### 🔍 发现的问题
1. **ParseException**: `findfont(FontProperties(family='sans-serif'))` 在某些 matplotlib 版本会报错
2. **重复注册**: Symbola 被添加多次到 fontManager
3. **无任务数据**: 服务器上的 task_stats.json 可能为空或损坏

---

## 🚀 立即执行的步骤

### 第一步：部署代码修复

```bash
# 连接服务器
ssh hdi918072@34.145.43.77

# 更新代码
cd /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack
git pull

# 重启服务
sudo systemctl restart monthly-report-bot

# 查看日志
sudo journalctl -u monthly-report-bot -f
```

**预期输出：**
- `DEBUG: ✅ Symbola 已添加到 fontManager` (第一次)
- `DEBUG: ✅ Symbola 已存在于 fontManager，跳过添加` (后续)
- `DEBUG: fontManager 中的 Symbola 字体数量: 1` (不再是 2, 4, 6...)
- `DEBUG: ✅ findfont(SimHei) 返回: /path/to/simhei.ttf`
- `DEBUG: ✅ findfont(Symbola) 返回: /path/to/Symbola_hint.ttf`
- **不再有 ParseException 错误！**

---

### 第二步：同步任务数据

**在本地 Windows 机器上执行：**

```cmd
cd f:\monthly_report_bot_link_pack

# 方法 A: 使用准备好的脚本
sync_task_data.bat

# 或 方法 B: 手动执行
scp monthly_report_bot_link_pack/task_stats.json hdi918072@34.145.43.77:/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/
ssh hdi918072@34.145.43.77 "sudo systemctl restart monthly-report-bot"
```

---

### 第三步：触发图表生成

**在飞书群中发送：**
```
进度图表
```
或
```
综合图表
```

---

### 第四步：查看结果

**在日志中查找：**

1. **字体配置信息：**
   ```
   DEBUG: ✅ 字体列表: ['SimHei', 'Symbola', 'DejaVu Sans']
   DEBUG: ✅ findfont(Symbola) 返回: /usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf
   ```

2. **图表生成日志：**
   ```
   2025-11-11 XX:XX:XX,XXX INFO ===== 开始配置中文和 emoji 字体 =====
   2025-11-11 XX:XX:XX,XXX INFO 美化版综合仪表板已生成: charts/dashboard_XXXXXX.png
   ```

3. **检查是否还有 Glyph warnings：**
   ```
   # 如果没有这些警告，说明 emoji 字体工作了！
   UserWarning: Glyph 127942 (\N{TROPHY}) missing from font(s) SimHei.
   ```

4. **在飞书中查看图表：**
   - 排名区域应该显示 🏆 🥇 🥈 等 emoji
   - 不再是方框

---

## 📊 判断标准

### ✅ 成功的标志

1. **日志中没有 ParseException**
2. **日志中没有 "Glyph ... missing" 警告**
3. **Symbola 只被添加一次**（数量保持为 1）
4. **findfont() 成功返回 Symbola 路径**
5. **飞书图表中 emoji 正常显示**

### ❌ 如果仍然失败

#### 情况 A：findfont() 找到了 Symbola，但 emoji 仍显示为方框

**说明：** matplotlib 的 font fallback 机制不工作

**解决方案：** 实施备选方案 A（见下文）

#### 情况 B：仍然有 "Glyph missing" 警告

**说明：** Symbola 字体没有正确加载或包含的字形不全

**排查步骤：**
1. 在服务器上验证 Symbola 字体文件
2. 使用 `fc-query` 查看字体包含的字形
3. 考虑使用其他 emoji 字体

---

## 🔄 备选方案 A：使用 FontProperties 直接指定字体

如果 rcParams 的 font fallback 机制不工作，使用这个方案：

### 修改图表生成代码

在 `chart_generator.py` 中创建全局 FontProperties 对象：

```python
# 在文件顶部，setup_chinese_fonts() 之后
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

### 修改所有 `ax.text()` 调用

将：
```python
ax.text(x, y, "文本 🏆", fontsize=12)
```

改为：
```python
chinese_prop, emoji_prop = get_font_properties()

# 对于纯中文文本
ax.text(x, y, "纯中文文本", fontproperties=chinese_prop, fontsize=12)

# 对于包含 emoji 的文本（使用 emoji 字体）
ax.text(x, y, "🏆", fontproperties=emoji_prop, fontsize=12)

# 对于混合文本，可能需要分开渲染
ax.text(x1, y, "文本", fontproperties=chinese_prop, fontsize=12)
ax.text(x2, y, "🏆", fontproperties=emoji_prop, fontsize=12)
```

**优点：** 最可靠，完全绕过 matplotlib 的 fallback 机制
**缺点：** 需要修改所有文本渲染代码

---

## 📂 相关文件

### 本地
- `f:\monthly_report_bot_link_pack\monthly_report_bot_link_pack\chart_generator.py` - 主要修改文件
- `f:\monthly_report_bot_link_pack\monthly_report_bot_link_pack\task_stats.json` - 任务数据
- `f:\monthly_report_bot_link_pack\sync_task_data.bat` - 同步脚本
- `f:\monthly_report_bot_link_pack\PITFALLS_EMOJI_FONT_DEBUG.md` - 错题本

### 服务器
- `/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/chart_generator.py`
- `/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/task_stats.json`
- `/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf` - Symbola 字体

### GitHub
- https://github.com/chaochaoying-ui/monthly-report-bot
- 最新 commit: `6dfb11d`

---

## 🔗 快速命令参考

```bash
# 部署
ssh hdi918072@34.145.43.77
cd /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack
git pull && sudo systemctl restart monthly-report-bot

# 查看日志
sudo journalctl -u monthly-report-bot -f

# 查看最近50行日志（不跟踪）
sudo journalctl -u monthly-report-bot -n 50

# 查看 task_stats.json
cat /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/task_stats.json | head -50

# 验证 Symbola 字体
ls -la /usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf
fc-query /usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf | grep family
```

---

**最后更新：** 2025-11-11 13:35 (UTC+8)
**下次继续：** 执行上述三个步骤，查看结果
