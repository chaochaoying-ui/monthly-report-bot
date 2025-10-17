# 每日统计功能说明

## 📊 功能概述

月报机器人现已支持每天下午5点半（17:30）自动统计任务完成情况，并生成美观的图表展示。

## ✨ 主要特性

### 1. 定时统计
- **触发时间**：每天下午 17:30
- **执行频率**：每日一次
- **时区支持**：根据配置的时区自动计算

### 2. 图表展示
- **综合仪表板**：包含任务完成情况饼图、完成率进度条、任务数量对比
- **自动生成**：使用 `chart_generator.py` 自动生成统计图表
- **自动上传**：图表自动上传到飞书并在卡片中展示

### 3. 智能分析
- **完成率评估**：根据完成率自动评估任务进度
  - ≥ 100%：🎉 恭喜！所有任务已完成！
  - ≥ 80%：✅ 任务完成情况良好！
  - ≥ 60%：⚠️ 任务完成情况一般，需要关注！
  - < 60%：❌ 任务完成情况较差，需要改进！
- **颜色编码**：卡片颜色根据完成率自动调整
  - 绿色：完成率 100%
  - 蓝色：完成率 80-99%
  - 橙色：完成率 60-79%
  - 红色：完成率 < 60%

### 4. 任务同步
- **状态同步**：发送统计前自动同步飞书任务状态
- **实时数据**：确保统计数据的准确性

## 🔧 技术实现

### 1. 定时任务判断函数

```python
def should_send_daily_stats(now: Optional[datetime] = None) -> bool:
    """判断是否应该发送每日统计（每天17:30）"""
    if now is None:
        now = datetime.now(TZ)
    current_time = now.strftime("%H:%M")

    return current_time == "17:30"
```

### 2. 图表生成与上传

```python
async def build_daily_stats_card_with_chart() -> Dict:
    """构建带图表的每日统计卡片"""
    # 1. 同步任务状态
    await sync_task_completion_status()

    # 2. 获取统计数据
    stats = get_task_completion_stats()
    task_stats_full = load_task_stats()

    # 3. 生成图表
    chart_path = chart_generator.generate_comprehensive_dashboard(task_stats_full)

    # 4. 上传图表到飞书
    image_key = await upload_image(chart_path)

    # 5. 构建卡片（包含图表）
    # ...
```

### 3. 主循环集成

```python
async def main_loop():
    """主循环：保留原定时能力"""
    while True:
        now = datetime.now(TZ)

        # ... 其他定时任务 ...

        elif should_send_daily_stats(now):
            logger.info("发送每日统计（17:30）...")
            card = await build_daily_stats_card_with_chart()
            success = await send_card_to_chat(card)

        await asyncio.sleep(60)
```

## 📝 使用说明

### 自动触发

机器人启动后，每天下午 17:30 会自动发送统计卡片到群聊。无需手动操作。

### 手动测试

如需手动测试功能，可以运行测试脚本：

**Windows:**
```bash
test_daily_stats.bat
```

**Linux/macOS:**
```bash
python test_daily_stats.py
```

## 📊 卡片示例

统计卡片包含以下内容：

1. **标题**：📊 每日任务统计报告
2. **统计摘要**：
   - 月度报告进度统计
   - 完成情况评估（优秀/良好/一般/需改进）
3. **详细数据**：
   - 总任务数
   - 已完成数量
   - 待完成数量
   - 完成率百分比
4. **进度条**：可视化进度显示
5. **统计图表**：综合仪表板图片
   - 任务完成情况饼图
   - 完成率进度条
   - 任务数量对比柱状图
   - 关键指标面板
6. **操作按钮**：查看详情（链接到月报文件）
7. **统计时间**：精确到秒的统计时间戳

## 🎯 与现有功能的配合

### 定时任务时间表

| 时间 | 日期范围 | 任务类型 | 说明 |
|------|----------|----------|------|
| 09:30 | 17-19日 | 任务创建 | 创建本月任务 |
| 10:00 | 18-22日 | 每日提醒 | 提醒未完成任务 |
| 09:00 | 23日 | 最终催办 | 紧急提醒 |
| **17:30** | **每天** | **每日统计** | **统计并展示图表** |
| 18:00 | 23日 | 最终统计 | 月度总结 |

### 功能互补

- **每日提醒（10:00）**：文字提醒，@相关人员
- **每日统计（17:30）**：图表展示，可视化分析
- **最终统计（23日18:00）**：月度总结，全面评估

## 🔍 故障排查

### 1. 统计卡片未发送

**可能原因**：
- 时区配置错误
- 机器人未启动
- 环境变量未配置

**解决方法**：
```bash
# 检查时区配置
echo $TZ  # 应为 America/Argentina/Buenos_Aires

# 检查机器人日志
tail -f monthly_report_bot_final.log

# 确认环境变量
python -c "import os; print(os.environ.get('TZ'))"
```

### 2. 图表未生成

**可能原因**：
- matplotlib 未安装
- 字体文件缺失
- 权限问题

**解决方法**：
```bash
# 安装图表依赖
pip install matplotlib seaborn numpy

# 检查charts目录权限
ls -la charts/

# 手动测试图表生成
python -c "from chart_generator import chart_generator; print('OK')"
```

### 3. 图表未显示在卡片中

**可能原因**：
- 图片上传失败
- image_key 无效
- 飞书权限不足

**解决方法**：
```bash
# 检查日志中的上传错误
grep "图片上传" monthly_report_bot_final.log

# 检查飞书应用权限
# 需要开通：im:message, im:resource
```

## 📈 性能优化

### 1. 图表缓存
- 图表文件保存在 `charts/` 目录
- 自动清理24小时前的旧图表
- 避免磁盘空间占用

### 2. 异步处理
- 使用 `async/await` 异步生成和上传图表
- 避免阻塞主循环
- 提高响应速度

### 3. 错误处理
- 图表生成失败时返回简化版卡片
- 上传失败时仍然发送文字统计
- 确保功能降级可用

## 🔐 安全说明

### 1. 数据安全
- 统计数据仅存储在本地 `task_stats.json`
- 图表文件自动清理，不长期保存
- 不泄露敏感任务信息

### 2. 权限控制
- 统计功能仅在配置的群组中发送
- 需要机器人在群中有发送消息权限
- 图片上传需要 `im:resource` 权限

## 📚 相关文件

- 主程序：`monthly_report_bot_final_interactive.py`
- 图表生成：`chart_generator.py`
- 测试脚本：`test_daily_stats.py`
- 启动脚本：`test_daily_stats.bat`

## 🎓 扩展开发

### 自定义统计时间

修改 `should_send_daily_stats()` 函数：

```python
def should_send_daily_stats(now: Optional[datetime] = None) -> bool:
    """自定义统计时间"""
    if now is None:
        now = datetime.now(TZ)
    current_time = now.strftime("%H:%M")

    # 修改为其他时间，例如每天下午6点
    return current_time == "18:00"
```

### 自定义图表样式

修改 `chart_generator.py` 中的配置：

```python
# 自定义颜色主题
self.colors = {
    'primary': '#2E86AB',
    'success': '#A23B72',
    'warning': '#F18F01',
    # ...
}
```

### 添加更多统计维度

在 `build_daily_stats_card_with_chart()` 中添加：

```python
# 添加用户参与度统计
user_chart = chart_generator.generate_user_participation_chart(task_stats_full)

# 添加进度趋势图
trend_chart = chart_generator.generate_progress_trend_chart(task_stats_full)
```

## 📞 技术支持

如有问题，请查看：
- 项目文档：`README.md`
- 部署指南：`DEPLOYMENT_GUIDE_V1_1.md`
- 需求文档：`月报机器人需求说明书_WS长连接版_v1.1.md`

---

**版本**：v1.3.2
**更新时间**：2025-10-17
**作者**：月报机器人开发团队

