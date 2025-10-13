#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试HTTP回调服务器
"""

import requests
import json
import time

def test_health_check():
    """测试健康检查"""
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 健康检查成功")
            print(f"状态: {data.get('status')}")
            print(f"时间戳: {data.get('timestamp')}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_webhook():
    """测试webhook端点"""
    try:
        # 模拟URL验证请求
        url_verification_data = {
            "type": "url_verification",
            "challenge": "test_challenge_123"
        }
        
        response = requests.post(
            "http://localhost:8080/webhook",
            json=url_verification_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("challenge") == "test_challenge_123":
                print("✅ URL验证测试成功")
                return True
            else:
                print("❌ URL验证响应不正确")
                return False
        else:
            print(f"❌ URL验证失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook测试异常: {e}")
        return False

def test_member_added_event():
    """测试成员加入事件"""
    try:
        # 模拟用户加入事件
        member_added_data = {
            "type": "event_callback",
            "event_id": "test_event_001",
            "event": {
                "type": "im.chat.member.user.added_v1",
                "chat_id": "oc_07f2d3d314f00fc29baf323a3a589972",
                "users": [
                    {
                        "user_id": "test_user_123",
                        "name": "测试用户"
                    }
                ]
            }
        }
        
        response = requests.post(
            "http://localhost:8080/webhook",
            json=member_added_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print("✅ 用户加入事件测试成功")
                return True
            else:
                print(f"❌ 用户加入事件响应错误: {data}")
                return False
        else:
            print(f"❌ 用户加入事件失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 用户加入事件测试异常: {e}")
        return False

def test_bot_added_event():
    """测试机器人加入事件"""
    try:
        # 模拟机器人加入事件
        bot_added_data = {
            "type": "event_callback",
            "event_id": "test_event_002",
            "event": {
                "type": "im.chat.member.bot.added_v1",
                "chat_id": "oc_07f2d3d314f00fc29baf323a3a589972",
                "bots": [
                    {
                        "bot_id": "test_bot_456",
                        "name": "测试机器人"
                    }
                ]
            }
        }
        
        response = requests.post(
            "http://localhost:8080/webhook",
            json=bot_added_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print("✅ 机器人加入事件测试成功")
                return True
            else:
                print(f"❌ 机器人加入事件响应错误: {data}")
                return False
        else:
            print(f"❌ 机器人加入事件失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 机器人加入事件测试异常: {e}")
        return False

if __name__ == "__main__":
    print("🧪 测试HTTP回调服务器...")
    print("=" * 50)
    
    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(3)
    
    # 测试健康检查
    print("\n1. 测试健康检查...")
    health_ok = test_health_check()
    
    # 测试webhook
    print("\n2. 测试webhook端点...")
    webhook_ok = test_webhook()
    
    # 测试用户加入事件
    print("\n3. 测试用户加入事件...")
    user_ok = test_member_added_event()
    
    # 测试机器人加入事件
    print("\n4. 测试机器人加入事件...")
    bot_ok = test_bot_added_event()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"健康检查: {'✅ 通过' if health_ok else '❌ 失败'}")
    print(f"Webhook端点: {'✅ 通过' if webhook_ok else '❌ 失败'}")
    print(f"用户加入事件: {'✅ 通过' if user_ok else '❌ 失败'}")
    print(f"机器人加入事件: {'✅ 通过' if bot_ok else '❌ 失败'}")
    
    if all([health_ok, webhook_ok, user_ok, bot_ok]):
        print("\n🎉 所有测试通过！HTTP回调服务器工作正常")
    else:
        print("\n⚠️ 部分测试失败，请检查服务器状态")

