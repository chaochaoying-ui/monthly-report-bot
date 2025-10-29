#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试字体配置 - 添加 print 语句来绕过 logger 配置问题
"""

import sys
import os

# 测试直接调用 setup_chinese_fonts
print("=" * 60)
print("DEBUG: 开始测试 setup_chinese_fonts()")
print("=" * 60)

try:
    from chart_generator import setup_chinese_fonts
    print("DEBUG: 成功导入 setup_chinese_fonts")

    print("\nDEBUG: 调用 setup_chinese_fonts()...")
    setup_chinese_fonts()
    print("DEBUG: setup_chinese_fonts() 执行完成")

except Exception as e:
    print(f"DEBUG: 错误发生: {e}")
    import traceback
    traceback.print_exc()

# 检查最终的字体配置
print("\n" + "=" * 60)
print("DEBUG: 检查 matplotlib 字体配置")
print("=" * 60)

import matplotlib.pyplot as plt

print(f"font.sans-serif: {plt.rcParams['font.sans-serif']}")
print(f"font.serif: {plt.rcParams.get('font.serif', 'N/A')}")
print(f"font.monospace: {plt.rcParams.get('font.monospace', 'N/A')}")
print(f"font.family: {plt.rcParams['font.family']}")
