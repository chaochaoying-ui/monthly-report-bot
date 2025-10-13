#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础测试：验证模块导入和基本功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_import_ws_wrapper():
    """测试WS包装器模块导入"""
    try:
        import app.ws_wrapper as wrapper
        assert wrapper is not None
        print("✅ WS包装器模块导入成功")
        return True
    except Exception as e:
        print(f"❌ WS包装器模块导入失败: {e}")
        return False

def test_import_long_polling_handler():
    """测试长轮询处理器模块导入"""
    try:
        import long_polling_handler as lp_handler
        assert lp_handler is not None
        print("✅ 长轮询处理器模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 长轮询处理器模块导入失败: {e}")
        return False

def test_import_card_design():
    """测试卡片设计模块导入"""
    try:
        import card_design_ws_v1_1 as card_design
        assert card_design is not None
        print("✅ 卡片设计模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 卡片设计模块导入失败: {e}")
        return False

def test_import_smart_interaction():
    """测试智能交互模块导入"""
    try:
        import smart_interaction_ws_v1_1 as smart_interaction
        assert smart_interaction is not None
        print("✅ 智能交互模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 智能交互模块导入失败: {e}")
        return False

def test_create_ws_handler():
    """测试创建WS处理器"""
    try:
        import app.ws_wrapper as wrapper
        handler = wrapper.create_ws_handler()
        assert handler is not None
        assert hasattr(handler, 'app_id')
        assert hasattr(handler, 'app_secret')
        print("✅ WS处理器创建成功")
        return True
    except Exception as e:
        print(f"❌ WS处理器创建失败: {e}")
        return False

def test_build_welcome_card():
    """测试构建欢迎卡片"""
    try:
        from card_design_ws_v1_1 import build_welcome_card
        config = {
            "push_time": "09:30",
            "timezone": "America/Argentina/Buenos_Aires",
            "file_url": "https://example.com"
        }
        card = build_welcome_card(config)
        assert isinstance(card, dict)
        assert "header" in card
        assert "elements" in card
        print("✅ 欢迎卡片构建成功")
        return True
    except Exception as e:
        print(f"❌ 欢迎卡片构建失败: {e}")
        return False

def test_smart_interaction_engine():
    """测试智能交互引擎"""
    try:
        from smart_interaction_ws_v1_1 import SmartInteractionEngine
        engine = SmartInteractionEngine()
        assert engine is not None
        assert hasattr(engine, 'analyze_intent')
        print("✅ 智能交互引擎创建成功")
        return True
    except Exception as e:
        print(f"❌ 智能交互引擎创建失败: {e}")
        return False

def main():
    """运行所有基础测试"""
    print("=" * 50)
    print("月报机器人WS长连接版 - 基础测试")
    print("=" * 50)
    
    tests = [
        test_import_long_polling_handler,
        test_import_card_design,
        test_import_smart_interaction,
        test_import_ws_wrapper,
        test_create_ws_handler,
        test_build_welcome_card,
        test_smart_interaction_engine,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有基础测试通过！")
        return True
    else:
        print("⚠️  部分测试失败，请检查依赖和配置")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)










