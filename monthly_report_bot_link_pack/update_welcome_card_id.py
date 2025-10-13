#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新欢迎卡片模板ID的脚本
"""

import os
import re

def update_welcome_card_id(new_card_id: str):
    """更新所有文件中的欢迎卡片模板ID"""
    
    # 需要更新的文件列表
    files_to_update = [
        "monthly_report_bot_official.py",
        "lark_official_handler.py", 
        "test_real_welcome.py",
        "test_official_welcome.py",
        "start_official.bat",
        "start_lark_sdk.bat",
        "start_long_polling.bat",
        "start_http_callback.bat",
        "start_bot_v1_1.bat",
        "simple_http_callback.py",
        "test_welcome_card.py",
        "monthly_report_bot_lark_sdk.py",
        "monthly_report_bot_long_polling.py",
        "monthly_report_bot_ws_v1.1.py"
    ]
    
    updated_files = []
    
    for filename in files_to_update:
        if os.path.exists(filename):
            try:
                # 读取文件内容
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 替换WELCOME_CARD_ID
                old_content = content
                content = re.sub(
                    r'WELCOME_CARD_ID.*?["\']([^"\']+)["\']',
                    f'WELCOME_CARD_ID = "{new_card_id}"',
                    content
                )
                content = re.sub(
                    r'set WELCOME_CARD_ID=([^\s]+)',
                    f'set WELCOME_CARD_ID={new_card_id}',
                    content
                )
                content = re.sub(
                    r'os\.environ\["WELCOME_CARD_ID"\] = "([^"]+)"',
                    f'os.environ["WELCOME_CARD_ID"] = "{new_card_id}"',
                    content
                )
                
                # 如果内容有变化，写回文件
                if content != old_content:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    updated_files.append(filename)
                    print(f"✅ 已更新: {filename}")
                else:
                    print(f"⏭️  无需更新: {filename}")
                    
            except Exception as e:
                print(f"❌ 更新失败: {filename} - {e}")
        else:
            print(f"⚠️  文件不存在: {filename}")
    
    return updated_files

def main():
    """主函数"""
    print("="*60)
    print("欢迎卡片模板ID更新工具")
    print("="*60)
    
    # 显示当前ID
    current_id = "AAqInYqWzIiu6"
    print(f"当前欢迎卡片模板ID: {current_id}")
    
    # 获取新ID
    new_id = input("\n请输入新的欢迎卡片模板ID: ").strip()
    
    if not new_id:
        print("❌ 未输入新的模板ID，操作取消")
        return
    
    if new_id == current_id:
        print("⚠️  新ID与当前ID相同，无需更新")
        return
    
    # 确认更新
    print(f"\n即将更新欢迎卡片模板ID:")
    print(f"从: {current_id}")
    print(f"到: {new_id}")
    
    confirm = input("\n确认更新吗？(y/N): ").strip().lower()
    if confirm not in ['y', 'yes', '是']:
        print("❌ 操作已取消")
        return
    
    # 执行更新
    print("\n开始更新文件...")
    updated_files = update_welcome_card_id(new_id)
    
    # 显示结果
    print("\n" + "="*60)
    print("更新完成！")
    print(f"共更新了 {len(updated_files)} 个文件")
    
    if updated_files:
        print("\n更新的文件:")
        for file in updated_files:
            print(f"  - {file}")
    
    print(f"\n新的欢迎卡片模板ID: {new_id}")
    print("现在可以重新启动程序来使用新的模板ID")
    print("="*60)

if __name__ == "__main__":
    main()
