#!/usr/bin/env python3
"""强制重建 matplotlib 字体缓存"""

import matplotlib.font_manager as fm
import os
import shutil

print("=" * 60)
print("重建 Matplotlib 字体缓存")
print("=" * 60)

# 1. 显示当前缓存信息
print("\n1. 当前字体缓存信息:")
cache_dir = fm.get_cachedir()
print(f"   缓存目录: {cache_dir}")

if os.path.exists(cache_dir):
    files = os.listdir(cache_dir)
    print(f"   缓存文件: {files}")

    # 删除缓存
    print("\n2. 删除旧的字体缓存...")
    try:
        shutil.rmtree(cache_dir)
        print("   ✅ 缓存已删除")
    except Exception as e:
        print(f"   ❌ 删除失败: {e}")
else:
    print("   缓存目录不存在")

# 2. 强制重建字体缓存
print("\n3. 重建字体缓存...")
try:
    # 这会触发字体缓存重建
    fm._load_fontmanager(try_read_cache=False)
    print("   ✅ 字体缓存重建完成")
except Exception as e:
    print(f"   ❌ 重建失败: {e}")

# 3. 显示新的缓存信息
print("\n4. 新的字体缓存信息:")
print(f"   字体数量: {len(fm.fontManager.ttflist)}")

# 4. 查找关键字体
print("\n5. 查找关键字体:")
simhei_count = 0
symbola_count = 0
emoji_count = 0

for font in fm.fontManager.ttflist:
    if 'simhei' in font.name.lower():
        simhei_count += 1
        print(f"   ✅ SimHei: {font.name} ({font.fname})")
    if 'symbola' in font.name.lower():
        symbola_count += 1
        print(f"   ✅ Symbola: {font.name} ({font.fname})")
    if 'emoji' in font.name.lower():
        emoji_count += 1
        print(f"   ✅ Emoji: {font.name} ({font.fname})")

print(f"\n6. 统计:")
print(f"   SimHei 字体: {simhei_count} 个")
print(f"   Symbola 字体: {symbola_count} 个")
print(f"   Emoji 字体: {emoji_count} 个")

if simhei_count == 0:
    print("\n   ⚠️  警告: 未找到 SimHei 字体!")
if symbola_count == 0:
    print("   ⚠️  警告: 未找到 Symbola 字体!")
if emoji_count == 0:
    print("   ⚠️  警告: 未找到 Emoji 字体!")

print("\n=" * 60)
print("完成！请重启服务以应用新的字体缓存")
print("=" * 60)
