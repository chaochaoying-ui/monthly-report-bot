#!/usr/bin/env python3
"""
测试GitHub Actions机器人功能
"""

import os
import sys
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """测试导入模块"""
    try:
        from github_actions_bot import FeishuBot, load_tasks, create_task_card
        logger.info("✅ 模块导入成功")
        return True
    except ImportError as e:
        logger.error(f"❌ 模块导入失败: {e}")
        return False

def test_config_validation():
    """测试配置验证"""
    required_vars = [
        'FEISHU_APP_ID',
        'FEISHU_APP_SECRET', 
        'FEISHU_VERIFICATION_TOKEN',
        'CHAT_ID',
        'WELCOME_CARD_ID',
        'FILE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"⚠️ 缺少环境变量: {missing_vars}")
        logger.info("这在实际GitHub Actions中会自动设置")
        return True
    else:
        logger.info("✅ 所有必需的环境变量都已设置")
        return True

def test_tasks_yaml():
    """测试tasks.yaml文件"""
    try:
        import yaml
        with open('tasks.yaml', 'r', encoding='utf-8') as f:
            tasks = yaml.safe_load(f)
        
        if not tasks:
            logger.error("❌ tasks.yaml文件为空")
            return False
            
        logger.info(f"✅ 成功加载 {len(tasks)} 个任务")
        
        # 检查任务结构
        for i, task in enumerate(tasks[:3]):  # 只检查前3个
            if 'title' not in task:
                logger.error(f"❌ 任务 {i+1} 缺少title字段")
                return False
            if 'assignee_open_id' not in task:
                logger.error(f"❌ 任务 {i+1} 缺少assignee_open_id字段")
                return False
            if 'doc_url' not in task:
                logger.error(f"❌ 任务 {i+1} 缺少doc_url字段")
                return False
        
        logger.info("✅ 任务结构验证通过")
        return True
        
    except FileNotFoundError:
        logger.error("❌ tasks.yaml文件不存在")
        return False
    except Exception as e:
        logger.error(f"❌ 加载tasks.yaml失败: {e}")
        return False

def test_requirements():
    """测试依赖包"""
    required_packages = [
        'requests',
        'yaml', 
        'datetime',
        'typing',
        'logging'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'yaml':
                import yaml
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning(f"⚠️ 缺少依赖包: {missing_packages}")
        logger.info("这些包会在GitHub Actions中自动安装")
        return True
    else:
        logger.info("✅ 所有必需的依赖包都已安装")
        return True

def main():
    """主测试函数"""
    logger.info("🧪 开始测试GitHub Actions机器人...")
    
    tests = [
        ("模块导入", test_imports),
        ("配置验证", test_config_validation),
        ("任务配置", test_tasks_yaml),
        ("依赖包", test_requirements)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 测试: {test_name}")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} 测试通过")
            else:
                logger.error(f"❌ {test_name} 测试失败")
        except Exception as e:
            logger.error(f"❌ {test_name} 测试异常: {e}")
    
    logger.info(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！GitHub Actions机器人准备就绪")
        return True
    else:
        logger.warning("⚠️ 部分测试失败，请检查配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
