#!/usr/bin/env python3
"""测试 emoji 字体是否被 matplotlib 正确加载"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

print("=" * 60)
print("Matplotlib 字体配置测试")
print("=" * 60)

# 1. 查看当前字体配置
print("\n1. 当前 sans-serif 字体列表:")
print(plt.rcParams['font.sans-serif'])

# 2. 查找系统中的 Symbola 字体
print("\n2. 查找 Symbola 字体:")
symbola_fonts = [f for f in fm.findSystemFonts() if 'symbola' in f.lower() or 'Symbola' in f]
if symbola_fonts:
    print(f"   找到: {symbola_fonts[0]}")
else:
    print("   ❌ 未找到 Symbola 字体")

# 3. 查找 Noto Color Emoji 字体
print("\n3. 查找 Noto Color Emoji 字体:")
emoji_fonts = [f for f in fm.findSystemFonts() if 'emoji' in f.lower() or 'Emoji' in f]
if emoji_fonts:
    for font in emoji_fonts:
        print(f"   找到: {font}")
else:
    print("   ❌ 未找到 Emoji 字体")

# 4. 测试加载 Symbola 字体
print("\n4. 测试加载 Symbola 字体:")
if symbola_fonts:
    try:
        font_prop = fm.FontProperties(fname=symbola_fonts[0])
        font_name = font_prop.get_name()
        print(f"   ✅ 字体名称: {font_name}")
    except Exception as e:
        print(f"   ❌ 加载失败: {e}")

# 5. 检查 matplotlib 的字体缓存
print("\n5. Matplotlib 字体管理器:")
print(f"   缓存的字体数量: {len(fm.fontManager.ttflist)}")

# 6. 搜索 matplotlib 可用的字体
print("\n6. Matplotlib 中可用的 emoji 相关字体:")
for font in fm.fontManager.ttflist:
    if 'symbola' in font.name.lower() or 'emoji' in font.name.lower():
        print(f"   - {font.name} ({font.fname})")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
