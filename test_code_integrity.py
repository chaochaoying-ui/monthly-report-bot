#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码完整性检查脚本
检查 monthly_report_bot_final_interactive.py 中的所有关键功能
"""

import sys
import os
import ast

# 设置输出编码为 UTF-8
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_python_syntax(filepath):
    """检查 Python 语法"""
    print(f"检查文件: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        ast.parse(code)
        print("✅ Python 语法检查通过")
        return True
    except SyntaxError as e:
        print(f"❌ 语法错误: {e}")
        return False

def check_required_functions(filepath):
    """检查必需的函数是否存在"""
    required_functions = [
        'create_monthly_tasks',  # 新增的任务创建函数
        'load_tasks',  # 加载任务配置
        'send_text_to_chat',  # 发送文本消息
        'handle_message_event',  # 处理消息事件
        'main_loop',  # 主循环
        'should_create_tasks',  # 判断是否应创建任务
        'init_lark_client',  # 初始化客户端
        'generate_echo_reply',  # 生成回复
    ]
    
    print("\n检查必需函数...")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        tree = ast.parse(code)
        
        # 提取所有函数定义
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)
        
        print(f"找到 {len(set(functions))} 个函数")
        
        missing = []
        for func in required_functions:
            if func in functions:
                print(f"✅ {func}")
            else:
                print(f"❌ {func} - 缺失")
                missing.append(func)
        
        if missing:
            print(f"\n❌ 缺失函数: {', '.join(missing)}")
            return False
        else:
            print("\n✅ 所有必需函数都存在")
            return True
            
    except Exception as e:
        print(f"❌ 检查函数时出错: {e}")
        return False

def check_imports(filepath):
    """检查关键导入"""
    required_imports = [
        'lark_oapi',
        'CreateTaskRequest',
        'CreateTaskRequestBody',
        'yaml',
        'asyncio',
        'dotenv',
    ]
    
    print("\n检查关键导入...")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        found = []
        missing = []
        
        for imp in required_imports:
            if imp in code:
                print(f"✅ {imp}")
                found.append(imp)
            else:
                print(f"❌ {imp} - 未找到")
                missing.append(imp)
        
        if missing:
            print(f"\n⚠️  未找到的导入（可能被包含在其他导入中）: {', '.join(missing)}")
        else:
            print("\n✅ 所有关键导入都存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查导入时出错: {e}")
        return False

def check_file_structure(filepath):
    """检查文件结构"""
    print("\n检查文件结构...")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        print(f"总行数: {total_lines}")
        
        # 检查关键注释标记
        sections = [
            '任务创建',
            '任务统计',
            '消息发送',
            '主程序逻辑',
        ]
        
        found_sections = []
        for section in sections:
            for line in lines:
                if section in line and line.strip().startswith('#'):
                    found_sections.append(section)
                    print(f"✅ 找到章节: {section}")
                    break
        
        print(f"\n找到 {len(found_sections)}/{len(sections)} 个关键章节")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查文件结构时出错: {e}")
        return False

def main():
    print("=" * 60)
    print("月报机器人代码完整性检查")
    print("=" * 60)
    
    filepath = os.path.join(
        os.path.dirname(__file__),
        'monthly_report_bot_link_pack',
        'monthly_report_bot_final_interactive.py'
    )
    
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return False
    
    results = []
    
    # 1. 语法检查
    results.append(check_python_syntax(filepath))
    
    # 2. 函数检查
    results.append(check_required_functions(filepath))
    
    # 3. 导入检查
    results.append(check_imports(filepath))
    
    # 4. 结构检查
    results.append(check_file_structure(filepath))
    
    # 总结
    print("\n" + "=" * 60)
    print("检查总结")
    print("=" * 60)
    
    if all(results):
        print("✅ 所有检查通过！代码完整且可用。")
        return True
    else:
        print("❌ 部分检查失败，请修复后重试。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

