#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字体 fallback 机制
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import font_manager

# 测试 emoji
test_text = "完成 ✅ 进行中 ⏳ 未开始 ❌ 图表 📊📈 奖杯 🏆 目标 🎯"

print("=" * 70)
print("测试 1: 当前字体配置")
print("=" * 70)
print(f"font.sans-serif: {plt.rcParams['font.sans-serif']}")
print(f"font.family: {plt.rcParams['font.family']}")

print("\n" + "=" * 70)
print("测试 2: 检查 Symbola 是否在 fontManager 中")
print("=" * 70)

symbola_path = '/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf'
print(f"Symbola 路径: {symbola_path}")

# 加载 Symbola 字体
symbola_prop = fm.FontProperties(fname=symbola_path)
symbola_name = symbola_prop.get_name()
print(f"Symbola 真实名称: {symbola_name}")

# 检查 fontManager 中是否有 Symbola
all_fonts = [f.name for f in fm.fontManager.ttflist]
print(f"\nfontManager 中的字体总数: {len(all_fonts)}")
symbola_in_manager = [f for f in all_fonts if 'Symbola' in f or 'symbola' in f]
print(f"fontManager 中包含 'Symbola' 的字体: {symbola_in_manager}")

print("\n" + "=" * 70)
print("测试 3: 添加 Symbola 到 fontManager")
print("=" * 70)

try:
    fm.fontManager.addfont(symbola_path)
    print("✅ addfont() 成功")

    # 重新检查
    all_fonts_after = [f.name for f in fm.fontManager.ttflist]
    symbola_in_manager_after = [f for f in all_fonts_after if 'Symbola' in f or 'symbola' in f]
    print(f"添加后，fontManager 中包含 'Symbola' 的字体: {symbola_in_manager_after}")
except Exception as e:
    print(f"❌ addfont() 失败: {e}")

print("\n" + "=" * 70)
print("测试 4: 设置字体列表并测试渲染")
print("=" * 70)

# 设置字体列表
font_list = ['SimHei', symbola_name, 'DejaVu Sans']
plt.rcParams['font.sans-serif'] = font_list
plt.rcParams['font.serif'] = font_list
plt.rcParams['font.monospace'] = font_list
print(f"设置的字体列表: {font_list}")

# 创建一个简单的图表来测试
fig, ax = plt.subplots(figsize=(10, 6))
ax.text(0.5, 0.5, test_text, fontsize=16, ha='center', va='center')
ax.axis('off')

print("\n尝试保存图表...")
try:
    plt.savefig('/tmp/test_emoji.png', dpi=100, bbox_inches='tight')
    print("✅ 图表已保存到 /tmp/test_emoji.png")
except Exception as e:
    print(f"❌ 保存失败: {e}")

plt.close()

print("\n" + "=" * 70)
print("测试 5: 使用 FontProperties 直接指定字体")
print("=" * 70)

# 尝试直接使用 FontProperties
fig, ax = plt.subplots(figsize=(10, 6))

# 为不同的文本使用不同的字体
chinese_prop = fm.FontProperties(fname='/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/fonts/simhei.ttf')
emoji_prop = fm.FontProperties(fname=symbola_path)

ax.text(0.5, 0.7, "中文测试", fontproperties=chinese_prop, fontsize=20, ha='center')
ax.text(0.5, 0.5, "🏆 🎯 ✅ ⏳ ❌", fontproperties=emoji_prop, fontsize=20, ha='center')
ax.text(0.5, 0.3, test_text, fontproperties=chinese_prop, fontsize=14, ha='center')  # 混合
ax.axis('off')

print("尝试使用 FontProperties 保存图表...")
try:
    plt.savefig('/tmp/test_emoji_fontprop.png', dpi=100, bbox_inches='tight')
    print("✅ 图表已保存到 /tmp/test_emoji_fontprop.png")
except Exception as e:
    print(f"❌ 保存失败: {e}")

plt.close()

print("\n" + "=" * 70)
print("完成！")
print("=" * 70)
