# 错题本 #6 - Emoji 字体显示问题调试历程

> **日期：** 2025-10-29
> **问题：** 图表中 emoji 字符显示为方框
> **状态：** 🔄 调试中（已定位关键问题，待最终验证）

---

## 一、问题描述

### 用户反馈
- 图表的任务完成排名区域，emoji (🏆🥇🥈📊📈) 显示为方框/乱码
- 中文字符显示正常（已在之前的会话中修复）
- 用户提供截图明确指出红圈区域应显示金牌、银牌 emoji

### 初始症状
```
UserWarning: Glyph 127942 (\N{TROPHY}) missing from font(s) SimHei.
UserWarning: Glyph 128200 (\N{CHART WITH UPWARDS TREND}) missing from font(s) SimHei.
```

**关键观察：** 警告信息只提到 `SimHei`（单数），说明 matplotlib **没有尝试 fallback 到其他字体**。

---

## 二、错误的假设和弯路

### ❌ 错误 1：认为字体没有安装
**假设：** 服务器上没有 emoji 字体
**实际：**
- Symbola 字体已安装: `/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf`
- `fc-list` 显示系统有 39 个字体

**教训：** 先验证字体是否存在，再考虑其他问题

---

### ❌ 错误 2：认为 logger 配置有问题
**假设：** `logger.info()` 没有输出是因为日志级别配置错误
**实际：**
- LOG_LEVEL 默认是 "INFO"，配置正确
- 问题是函数根本没有被调用，或者执行路径不对

**教训：** 当日志缺失时，先用 `print()` 验证代码是否执行

---

### ❌ 错误 3：认为字体名称不对
**假设：** 硬编码 `'Symbola'` 字符串与字体真实名称不匹配
**实际：**
- 使用 `FontProperties.get_name()` 获取的真实名称就是 `'Symbola'`
- 字体名称正确，问题在别处

**教训：** 验证假设后，如果问题依旧，要重新思考根本原因

---

### ❌ 错误 4：认为 fontManager.addfont() 立即生效
**假设：** 调用 `fm.fontManager.addfont(symbola_path)` 后，字体就能用于 fallback
**实际：**
- `addfont()` 只是把字体加到 fontManager 的字体列表
- **但 matplotlib 的 font fallback 机制在某些情况下不会自动使用这些字体**
- 需要在 `rcParams['font.sans-serif']` 中正确配置字体顺序

**教训：** 理解工具的内部机制，不要想当然

---

### ❌ 错误 5：字体缓存重建覆盖了已添加的字体
**假设：** 在函数开始时 `addfont()` 会一直有效
**实际：**
```python
# 错误的顺序
fm.fontManager.addfont(symbola_path)  # 添加字体
fm._load_fontmanager(try_read_cache=False)  # 重建缓存 - 覆盖了上面的添加！
```

**正确的顺序：**
```python
# 先重建缓存
fm._load_fontmanager(try_read_cache=False)
# 再添加自定义字体
fm.fontManager.addfont(symbola_path)
```

**教训：** 注意函数调用顺序，某些操作会重置之前的状态

---

## 三、关键发现

### 🔍 发现 1：matplotlib 警告的深层含义
```
UserWarning: Glyph 127942 (\N{TROPHY}) missing from font(s) SimHei.
```

**分析：**
- 只提到 `SimHei`（单数），不是 "SimHei, Symbola"（复数）
- 说明 matplotlib **根本没有尝试 fallback**
- 即使 `rcParams['font.sans-serif'] = ['SimHei', 'Symbola', 'DejaVu Sans']`

---

### 🔍 发现 2：字体列表构建逻辑错误
**问题代码：**
```python
font_list = []
font_list.append(chinese_font_name)  # 添加中文字体
# ... 中间其他操作 ...
font_list.insert(1, symbola_font_name)  # 插入到索引1 - 逻辑混乱
font_list.append('DejaVu Sans')  # 添加后备
```

**修复后：**
```python
font_list = [chinese_font_name]  # 先添加中文字体
font_list.append(symbola_font_name)  # 顺序添加 emoji 字体
font_list.append('DejaVu Sans')  # 最后添加后备
```

**教训：** 使用 `insert()` 要特别小心，明确列表的当前状态

---

### 🔍 发现 3：调试输出的重要性
**有效的调试策略：**
```python
# 1. 函数入口
print("DEBUG: setup_chinese_fonts() 被调用")

# 2. 关键步骤
print(f"DEBUG: 找到 Symbola 字体: {symbola_path}")
print(f"DEBUG: Symbola 字体的真实名称: {symbola_font_name}")

# 3. 验证状态
symbola_fonts_in_manager = [f.name for f in fm.fontManager.ttflist if symbola_font_name in f.name]
print(f"DEBUG: fontManager 中的 Symbola 字体: {symbola_fonts_in_manager}")
print(f"DEBUG: fontManager 字体总数: {len(fm.fontManager.ttflist)}")

# 4. 最终配置
print(f"DEBUG: ✅ 字体列表: {font_list}")
print(f"DEBUG: ✅ 最终 rcParams['font.sans-serif']: {plt.rcParams['font.sans-serif']}")

# 5. 测试机制
from matplotlib.font_manager import findfont, FontProperties
test_prop = FontProperties(family='sans-serif')
found_font = findfont(test_prop)
print(f"DEBUG: ✅ findfont() 返回: {found_font}")
```

**教训：**
- 使用 `print()` 而不是 `logger.info()`，确保输出到 systemd 日志
- 在每个关键步骤验证状态
- 测试工具的实际行为，不要假设

---

## 四、当前解决方案

### 已实施的修复

1. **修复字体缓存重建时机**
   - 确保 `_load_fontmanager()` 在 `addfont()` 之前调用

2. **修复字体列表构建逻辑**
   - 使用清晰的顺序构建字体列表
   - 避免使用 `insert()` 造成混乱

3. **添加详细的调试输出**
   - 验证 Symbola 是否在 fontManager 中
   - 输出最终的 rcParams 配置
   - 测试 `findfont()` 的实际行为

4. **在图表生成时重新应用字体配置**
   - 在 `generate_comprehensive_dashboard()` 中调用 `setup_chinese_fonts()`

### 待验证的假设

**核心问题可能是：** matplotlib 的 font fallback 机制在某些版本中不够智能，或者需要特定的配置方式。

**下一步调试方向：**
- 查看 `findfont()` 返回的路径，验证是否找到 Symbola
- 如果 `findfont()` 找不到 Symbola，说明 fontManager 注册有问题
- 如果找到了但还是显示方框，可能需要使用 `FontProperties` 直接指定字体

---

## 五、备选方案（如果当前方案失败）

### 方案 A：使用 FontProperties 直接指定
```python
# 为每个 Text 对象设置 FontProperties
chinese_prop = fm.FontProperties(fname='/path/to/simhei.ttf')
emoji_prop = fm.FontProperties(fname='/path/to/Symbola_hint.ttf')

# 在绘图时指定
ax.text(x, y, "中文文本", fontproperties=chinese_prop)
ax.text(x, y, "🏆 emoji", fontproperties=emoji_prop)
```

**优点：** 直接控制，绕过 matplotlib 的 fallback 机制
**缺点：** 需要修改所有绘图代码，分别处理中文和 emoji

---

### 方案 B：使用复合字体
创建一个包含中文和 emoji 的复合字体文件（需要字体编辑工具）

**优点：** 一劳永逸
**缺点：** 需要额外工具和步骤

---

### 方案 C：用文字替代 emoji
```python
# 替换 emoji 为文字
"🏆" -> "[奖杯]"
"🥇" -> "[金牌]"
"📊" -> "[图表]"
```

**优点：** 最简单，保证兼容性
**缺点：** 不美观，不符合用户需求

---

## 六、知识点总结

### matplotlib 字体配置机制

1. **fontManager**
   - 管理系统中所有可用字体
   - `addfont(path)` 添加字体到列表
   - `_load_fontmanager()` 重建缓存会覆盖手动添加的字体

2. **rcParams 字体配置**
   ```python
   plt.rcParams['font.sans-serif'] = ['Font1', 'Font2', 'Font3']
   plt.rcParams['font.serif'] = [...]
   plt.rcParams['font.monospace'] = [...]  # 很多图表标签用这个！
   plt.rcParams['font.family'] = 'sans-serif'
   ```

3. **Font Fallback 机制**
   - matplotlib 应该按顺序尝试字体列表中的每个字体
   - 如果第一个字体缺少某个字形，应该 fallback 到下一个
   - **但在实践中，这个机制可能不总是有效**

4. **FontProperties**
   - 直接指定字体文件路径
   - 绕过 fontManager 和 rcParams
   - 最可靠，但需要手动管理

---

### Python 调试技巧

1. **使用 print() 而不是 logger**
   - 当怀疑 logger 配置有问题时
   - print() 直接输出到 stdout/stderr，systemd 会捕获

2. **验证每个假设**
   - 不要想当然
   - 用代码验证工具的实际行为

3. **渐进式调试**
   - 先验证最基础的部分（字体文件存在？）
   - 再验证中间层（fontManager 有这个字体？）
   - 最后验证高层逻辑（rcParams 配置正确？）

4. **记录所有尝试**
   - 避免重复相同的错误
   - 帮助理解问题的全貌

---

## 七、下次遇到类似问题的 SOP

1. **验证资源存在**
   - 字体文件在服务器上吗？
   - 路径正确吗？

2. **验证工具识别**
   - fontManager 中有这个字体吗？
   - `findfont()` 能找到吗？

3. **验证配置正确**
   - rcParams 设置了吗？
   - 设置的值是期望的吗？

4. **验证机制工作**
   - 创建简单测试用例
   - 隔离问题变量

5. **查阅文档和源码**
   - 不要依赖假设
   - 理解工具的实际行为

6. **考虑备选方案**
   - 如果标准方法不工作
   - 是否有其他途径达到目标？

---

## 八、待办事项

- [ ] 部署最新代码到服务器
- [ ] 查看 `findfont()` 的输出
- [ ] 根据输出判断是 fontManager 问题还是 fallback 问题
- [ ] 如果 fallback 机制确实不工作，实施方案 A（FontProperties）
- [ ] 最终验证 emoji 在飞书图表中正常显示
- [ ] 移除调试 print 语句（或改为 logger.debug）
- [ ] 更新部署文档

---

## 九、参考资料

- matplotlib font configuration: https://matplotlib.org/stable/tutorials/text/text_props.html
- matplotlib font_manager API: https://matplotlib.org/stable/api/font_manager_api.html
- Symbola font: https://fontlibrary.org/en/font/symbola
- Unicode emoji: https://unicode.org/emoji/charts/full-emoji-list.html

---

**最后更新：** 2025-10-29 20:55 (UTC+8)
**下次继续时查看：** `sudo journalctl -u monthly-report-bot -n 200` 查找 DEBUG 输出
