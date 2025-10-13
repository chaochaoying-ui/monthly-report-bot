#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月报机器人 v1.1 - 测试脚本
设计理念：全面验证、自动化测试、详细报告

功能：
1. 环境变量验证
2. 模块功能测试
3. 智能交互测试
4. 卡片设计测试
5. WebSocket连接测试
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any

# 导入测试模块
from smart_interaction_ws_v1_1 import SmartInteractionEngine
from card_design_ws_v1_1 import (
    build_welcome_card, build_monthly_task_card, 
    build_final_reminder_card, build_help_card
)
from websocket_handler_v1_1 import FeishuWebSocketHandler

class BotTester:
    """机器人测试器"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
    
    def log_test(self, test_name: str, success: bool, message: str = "", details: Dict = None):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} {test_name}: {message}")
    
    def test_environment_variables(self) -> bool:
        """测试环境变量"""
        print("\n=== 环境变量测试 ===")
        
        required_vars = [
            "APP_ID", "APP_SECRET", "CHAT_ID", "FILE_URL", "TZ"
        ]
        
        all_passed = True
        for var in required_vars:
            value = os.environ.get(var, "").strip()
            if value:
                self.log_test(f"环境变量 {var}", True, f"已设置: {value[:20]}...")
            else:
                self.log_test(f"环境变量 {var}", False, "未设置")
                all_passed = False
        
        return all_passed
    
    def test_smart_interaction_engine(self) -> bool:
        """测试智能交互引擎"""
        print("\n=== 智能交互引擎测试 ===")
        
        try:
            engine = SmartInteractionEngine()
            
            # 测试中文意图识别
            test_cases = [
                ("我的任务", "query_tasks"),
                ("已完成", "mark_completed"),
                ("延期到明天17:00", "request_extension"),
                ("查看进度", "view_progress"),
                ("帮助", "help_setting")
            ]
            
            all_passed = True
            for text, expected_intent in test_cases:
                result = engine.analyze_intent(text, "test_user")
                actual_intent = result.get("intent", "unknown")
                confidence = result.get("confidence", 0)
                
                if actual_intent == expected_intent and confidence > 0.5:
                    self.log_test(f"意图识别: {text}", True, f"识别为: {actual_intent} (置信度: {confidence:.2f})")
                else:
                    self.log_test(f"意图识别: {text}", False, f"期望: {expected_intent}, 实际: {actual_intent}")
                    all_passed = False
            
            # 测试多语言支持
            multilingual_tests = [
                ("my tasks", "en"),
                ("mis tareas", "es"),
                ("我的清单", "zh")
            ]
            
            for text, expected_lang in multilingual_tests:
                result = engine.analyze_intent(text, "test_user")
                actual_lang = result.get("language", "unknown")
                
                if actual_lang == expected_lang:
                    self.log_test(f"语言检测: {text}", True, f"检测为: {actual_lang}")
                else:
                    self.log_test(f"语言检测: {text}", False, f"期望: {expected_lang}, 实际: {actual_lang}")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log_test("智能交互引擎初始化", False, f"异常: {str(e)}")
            return False
    
    def test_card_design(self) -> bool:
        """测试卡片设计"""
        print("\n=== 卡片设计测试 ===")
        
        try:
            # 测试配置
            test_config = {
                "push_time": "09:30",
                "file_url": "https://example.com/file",
                "timezone": "America/Argentina/Buenos_Aires"
            }
            
            all_passed = True
            
            # 测试欢迎卡片
            welcome_card = build_welcome_card(test_config)
            if welcome_card and "header" in welcome_card:
                self.log_test("欢迎卡片构建", True, "卡片结构正确")
            else:
                self.log_test("欢迎卡片构建", False, "卡片结构错误")
                all_passed = False
            
            # 测试月报任务卡片
            task_card = build_monthly_task_card(test_config, "2024年12月20日", 5, 10)
            if task_card and "header" in task_card:
                self.log_test("月报任务卡片构建", True, "卡片结构正确")
            else:
                self.log_test("月报任务卡片构建", False, "卡片结构错误")
                all_passed = False
            
            # 测试最终提醒卡片
            reminder_card = build_final_reminder_card(test_config)
            if reminder_card and "header" in reminder_card:
                self.log_test("最终提醒卡片构建", True, "卡片结构正确")
            else:
                self.log_test("最终提醒卡片构建", False, "卡片结构错误")
                all_passed = False
            
            # 测试帮助卡片
            help_card = build_help_card("zh")
            if help_card and "header" in help_card:
                self.log_test("帮助卡片构建", True, "卡片结构正确")
            else:
                self.log_test("帮助卡片构建", False, "卡片结构错误")
                all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log_test("卡片设计模块", False, f"异常: {str(e)}")
            return False
    
    def test_websocket_handler(self) -> bool:
        """测试WebSocket处理器"""
        print("\n=== WebSocket处理器测试 ===")
        
        try:
            handler = FeishuWebSocketHandler()
            
            # 测试统计信息
            stats = handler.get_stats()
            if isinstance(stats, dict) and "connection_count" in stats:
                self.log_test("WebSocket处理器初始化", True, "处理器创建成功")
            else:
                self.log_test("WebSocket处理器初始化", False, "处理器创建失败")
                return False
            
            # 测试事件处理器注册
            test_handler = lambda x: None
            handler.register_event_handler("test.event", test_handler)
            
            if "test.event" in handler.event_handlers:
                self.log_test("事件处理器注册", True, "处理器注册成功")
            else:
                self.log_test("事件处理器注册", False, "处理器注册失败")
                return False
            
            # 测试欢迎卡片处理器
            if hasattr(handler, 'set_welcome_handler'):
                welcome_handler = lambda x: None
                handler.set_welcome_handler(welcome_handler)
                if hasattr(handler, 'welcome_handler') and handler.welcome_handler:
                    self.log_test("欢迎卡片处理器", True, "欢迎处理器设置成功")
                else:
                    self.log_test("欢迎卡片处理器", False, "欢迎处理器设置失败")
            else:
                self.log_test("欢迎卡片处理器", False, "缺少set_welcome_handler方法")
            
            return True
            
        except Exception as e:
            self.log_test("WebSocket处理器", False, f"异常: {str(e)}")
            return False
    
    def test_welcome_card_functionality(self) -> bool:
        """测试新成员欢迎卡片功能"""
        print("\n=== 欢迎卡片功能测试 ===")
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("bot", "monthly_report_bot_ws_v1.1.py")
            bot = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(bot)
            
            # 测试欢迎卡片ID配置
            welcome_card_id = getattr(bot, 'WELCOME_CARD_ID', None)
            if welcome_card_id:
                self.log_test("欢迎卡片ID配置", True, f"WELCOME_CARD_ID: {welcome_card_id}")
            else:
                self.log_test("欢迎卡片ID配置", False, "缺少WELCOME_CARD_ID环境变量")
                return False
            
            # 测试发送欢迎卡片函数
            if hasattr(bot, 'send_welcome_card_to_user'):
                self.log_test("发送欢迎卡片函数", True, "send_welcome_card_to_user函数存在")
            else:
                self.log_test("发送欢迎卡片函数", False, "缺少send_welcome_card_to_user函数")
                return False
            
            # 测试新成员事件处理函数
            if hasattr(bot, 'handle_chat_member_bot_added_event'):
                self.log_test("新成员事件处理", True, "handle_chat_member_bot_added_event函数存在")
            else:
                self.log_test("新成员事件处理", False, "缺少handle_chat_member_bot_added_event函数")
                return False
            
            # 测试WebSocket处理器集成
            ws_handler = getattr(bot, 'ws_handler', None)
            if ws_handler and hasattr(ws_handler, 'welcome_handler'):
                self.log_test("WebSocket集成", True, "欢迎处理器已注册到WebSocket")
            else:
                self.log_test("WebSocket集成", False, "WebSocket未集成欢迎处理器")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("欢迎卡片功能", False, f"异常: {str(e)}")
            return False
    
    def test_config_files(self) -> bool:
        """测试配置文件"""
        print("\n=== 配置文件测试 ===")
        
        all_passed = True
        
        # 测试tasks.yaml
        if os.path.exists("tasks.yaml"):
            try:
                import yaml
                with open("tasks.yaml", "r", encoding="utf-8") as f:
                    tasks = yaml.safe_load(f)
                
                if isinstance(tasks, list) and len(tasks) > 0:
                    self.log_test("tasks.yaml", True, f"包含 {len(tasks)} 个任务")
                else:
                    self.log_test("tasks.yaml", False, "文件格式错误或为空")
                    all_passed = False
            except Exception as e:
                self.log_test("tasks.yaml", False, f"解析失败: {str(e)}")
                all_passed = False
        else:
            self.log_test("tasks.yaml", False, "文件不存在")
            all_passed = False
        
        # 测试requirements.txt
        if os.path.exists("requirements.txt"):
            self.log_test("requirements.txt", True, "依赖文件存在")
        else:
            self.log_test("requirements.txt", False, "依赖文件不存在")
            all_passed = False
        
        return all_passed
    
    def test_api_connection(self) -> bool:
        """测试API连接"""
        print("\n=== API连接测试 ===")
        
        try:
            import requests
            
            # 测试飞书API连接
            app_id = os.environ.get("APP_ID", "").strip()
            app_secret = os.environ.get("APP_SECRET", "").strip()
            
            if not app_id or not app_secret:
                self.log_test("API连接", False, "缺少APP_ID或APP_SECRET")
                return False
            
            # 获取租户令牌
            url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            payload = {"app_id": app_id, "app_secret": app_secret}
            
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()
            
            if data.get("code", 0) == 0:
                self.log_test("API连接", True, "飞书API连接成功")
                return True
            else:
                self.log_test("API连接", False, f"API连接失败: {data.get('msg', '未知错误')}")
                return False
                
        except Exception as e:
            self.log_test("API连接", False, f"连接异常: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("🚀 开始月报机器人 v1.1 测试")
        print("=" * 50)
        
        test_functions = [
            ("环境变量", self.test_environment_variables),
            ("智能交互引擎", self.test_smart_interaction_engine),
            ("卡片设计", self.test_card_design),
            ("WebSocket处理器", self.test_websocket_handler),
            ("欢迎卡片功能", self.test_welcome_card_functionality),
            ("配置文件", self.test_config_files),
            ("API连接", self.test_api_connection)
        ]
        
        passed_tests = 0
        total_tests = len(test_functions)
        
        for test_name, test_func in test_functions:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, False, f"测试异常: {str(e)}")
        
        # 生成测试报告
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "duration_seconds": duration,
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            "test_results": self.test_results
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """打印测试报告"""
        print("\n" + "=" * 50)
        print("📊 测试报告")
        print("=" * 50)
        
        summary = report["summary"]
        print(f"总测试数: {summary['total_tests']}")
        print(f"通过测试: {summary['passed_tests']}")
        print(f"失败测试: {summary['failed_tests']}")
        print(f"成功率: {summary['success_rate']:.1f}%")
        print(f"测试耗时: {summary['duration_seconds']:.2f}秒")
        
        if summary['success_rate'] >= 80:
            print("\n🎉 测试结果: 优秀")
        elif summary['success_rate'] >= 60:
            print("\n✅ 测试结果: 良好")
        else:
            print("\n⚠️ 测试结果: 需要改进")
        
        # 保存报告到文件
        report_file = f"test_report_v1_1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: {report_file}")

def main():
    """主函数"""
    tester = BotTester()
    report = tester.run_all_tests()
    tester.print_report(report)

if __name__ == "__main__":
    main()
