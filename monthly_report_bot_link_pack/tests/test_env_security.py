"""
环境变量安全性测试 - 确保敏感信息不再硬编码
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_main_ws_no_default_secrets():
    """测试 app/main_ws.py 不包含默认密钥"""
    from app import main_ws
    
    # 临时清除环境变量
    old_app_id = os.environ.get('APP_ID')
    old_app_secret = os.environ.get('APP_SECRET')
    
    if 'APP_ID' in os.environ:
        del os.environ['APP_ID']
    if 'APP_SECRET' in os.environ:
        del os.environ['APP_SECRET']
    
    try:
        # 检查默认值应该为空
        app_id = os.environ.get('APP_ID', '')
        app_secret = os.environ.get('APP_SECRET', '')
        
        assert app_id == '', f"APP_ID 应该为空，但得到: {app_id}"
        assert app_secret == '', f"APP_SECRET 应该为空，但得到: {app_secret}"
        
        # 检查源码中不应该包含已知的默认密钥
        import inspect
        source = inspect.getsource(main_ws)
        
        # 不应该包含这些已知的硬编码值
        forbidden_patterns = [
            'cli_a8fd44a9453cd00c',
            'jsVoFWgaaw05en6418h7xbhV5oXxAwIm'
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in source, f"源码中不应该包含硬编码密钥: {pattern}"
            
        print("✓ app/main_ws.py 安全检查通过")
        
    finally:
        # 恢复环境变量
        if old_app_id:
            os.environ['APP_ID'] = old_app_id
        if old_app_secret:
            os.environ['APP_SECRET'] = old_app_secret

def test_main_ws_simple_no_default_secrets():
    """测试 app/main_ws_simple.py 不包含默认密钥"""
    from app import main_ws_simple
    
    # 临时清除环境变量
    old_app_id = os.environ.get('APP_ID')
    old_app_secret = os.environ.get('APP_SECRET')
    
    if 'APP_ID' in os.environ:
        del os.environ['APP_ID']
    if 'APP_SECRET' in os.environ:
        del os.environ['APP_SECRET']
    
    try:
        # 检查默认值应该为空
        app_id = os.environ.get('APP_ID', '')
        app_secret = os.environ.get('APP_SECRET', '')
        
        assert app_id == '', f"APP_ID 应该为空，但得到: {app_id}"
        assert app_secret == '', f"APP_SECRET 应该为空，但得到: {app_secret}"
        
        # 检查源码中不应该包含已知的默认密钥
        import inspect
        source = inspect.getsource(main_ws_simple)
        
        # 不应该包含这些已知的硬编码值
        forbidden_patterns = [
            'cli_a8fd44a9453cd00c',
            'jsVoFWgaaw05en6418h7xbhV5oXxAwIm'
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in source, f"源码中不应该包含硬编码密钥: {pattern}"
            
        print("✓ app/main_ws_simple.py 安全检查通过")
        
    finally:
        # 恢复环境变量
        if old_app_id:
            os.environ['APP_ID'] = old_app_id
        if old_app_secret:
            os.environ['APP_SECRET'] = old_app_secret

def test_interactive_bot_no_default_secrets():
    """测试 monthly_report_bot_final_interactive.py 不包含默认密钥"""
    import monthly_report_bot_final_interactive
    
    # 检查源码中不应该包含已知的默认密钥
    import inspect
    source = inspect.getsource(monthly_report_bot_final_interactive)
    
    # 不应该包含这些已知的硬编码值
    forbidden_patterns = [
        'cli_a8fd44a9453cd00c',
        'jsVoFWgaaw05en6418h7xbhV5oXxAwIm'
    ]
    
    for pattern in forbidden_patterns:
        assert pattern not in source, f"源码中不应该包含硬编码密钥: {pattern}"
        
    print("✓ monthly_report_bot_final_interactive.py 安全检查通过")

if __name__ == '__main__':
    print("Start env security & perf regression tests...")
    
    try:
        test_main_ws_no_default_secrets()
        test_main_ws_simple_no_default_secrets()
        test_interactive_bot_no_default_secrets()
        # TZ 尾空格鲁棒性
        import os
        os.environ['TZ'] = 'Asia/Shanghai '
        import importlib
        m = importlib.reload(__import__('monthly_report_bot_final_interactive'))
        assert getattr(m, 'TZ_NAME', '').endswith('Shanghai')
        # 校验“已完成”新文案
        reply = m.generate_echo_reply("已完成")
        assert "不再催办" in reply
        print("\nAll security tests passed.")
    except Exception as e:
        try:
            # 显示更明确的失败原因（避免终端编码问题）
            print("\nFAILED:", repr(e))
        except Exception:
            print("\nFAILED: <unprintable exception>")
        sys.exit(1)
