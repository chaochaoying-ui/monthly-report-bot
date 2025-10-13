#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试欢迎卡片发送功能
"""

import os
import requests
import json

# 环境变量
APP_ID = os.environ.get("APP_ID", "cli_a8fd44a9453cd00c")
APP_SECRET = os.environ.get("APP_SECRET", "jsVoFWgaaw05en6418h7xbhV5oXxAwIm")
WELCOME_CARD_ID = os.environ.get("WELCOME_CARD_ID", "AAqInYqWzIiu6")

def get_tenant_token():
    """获取tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0:
            return data.get("tenant_access_token")
        else:
            print(f"获取token失败: {data.get('msg')}")
            return None
    except Exception as e:
        print(f"获取token异常: {e}")
        return None

def test_send_welcome_card():
    """测试发送欢迎卡片"""
    print("🧪 测试欢迎卡片发送功能...")
    
    # 1. 获取token
    print("\n1. 获取tenant token...")
    token = get_tenant_token()
    if not token:
        print("❌ 获取token失败")
        return False
    
    print("✅ 获取token成功")
    
    # 2. 测试发送欢迎卡片到群聊
    print("\n2. 测试发送欢迎卡片到群聊...")
    chat_id = "oc_07f2d3d314f00fc29baf323a3a589972"
    
    try:
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 使用模板卡片格式（根据您的代码）
        payload = {
            "receive_id": chat_id,
            "msg_type": "interactive",
            "content": json.dumps({
                "type": "template",  # 关键：使用template类型
                "data": {
                    "template_id": WELCOME_CARD_ID,  # 使用template_id
                    "template_variable": {   # 添加模板变量
                        "title": "欢迎新成员",
                        "content": "我们很高兴您加入我们的团队！",
                        "username": "系统管理员",
                        "welcome_message": "🎉 欢迎加入我们的群聊！"
                    }
                }
            }, ensure_ascii=False)
        }
        
        response = requests.post(
            url, 
            json=payload, 
            headers=headers, 
            timeout=30,
            params={"receive_id_type": "chat_id"}
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print("✅ 欢迎卡片发送成功")
                return True
            else:
                print(f"❌ 欢迎卡片发送失败: {data.get('msg')}")
                return False
        else:
            print(f"❌ 欢迎卡片发送HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 发送欢迎卡片异常: {e}")
        return False

def test_send_text_message():
    """测试发送文本消息"""
    print("\n3. 测试发送文本消息...")
    
    token = get_tenant_token()
    if not token:
        return False
    
    chat_id = "oc_07f2d3d314f00fc29baf323a3a589972"
    
    try:
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "receive_id": chat_id,
            "msg_type": "text",
            "content": json.dumps({
                "text": "🧪 测试消息：HTTP回调服务器已启动，欢迎卡片功能正常！"
            }, ensure_ascii=False)
        }
        
        response = requests.post(
            url, 
            json=payload, 
            headers=headers, 
            timeout=30,
            params={"receive_id_type": "chat_id"}
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print("✅ 文本消息发送成功")
                return True
            else:
                print(f"❌ 文本消息发送失败: {data.get('msg')}")
                return False
        else:
            print(f"❌ 文本消息发送HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 发送文本消息异常: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("欢迎卡片功能测试")
    print("=" * 60)
    
    # 设置环境变量
    os.environ["APP_ID"] = APP_ID
    os.environ["APP_SECRET"] = APP_SECRET
    os.environ["WELCOME_CARD_ID"] = WELCOME_CARD_ID
    
    print(f"APP_ID: {APP_ID}")
    print(f"WELCOME_CARD_ID: {WELCOME_CARD_ID}")
    print()
    
    # 测试欢迎卡片
    card_ok = test_send_welcome_card()
    
    # 测试文本消息
    text_ok = test_send_text_message()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print(f"欢迎卡片发送: {'✅ 成功' if card_ok else '❌ 失败'}")
    print(f"文本消息发送: {'✅ 成功' if text_ok else '❌ 失败'}")
    
    if card_ok and text_ok:
        print("\n🎉 所有测试通过！欢迎卡片功能正常工作")
        print("\n📋 下一步配置:")
        print("1. 在飞书后台配置HTTP回调")
        print("2. 设置回调URL: http://your-public-ip:8080/webhook")
        print("3. 订阅事件: im.chat.member.user.added_v1, im.chat.member.bot.added_v1")
    else:
        print("\n⚠️ 部分测试失败，请检查配置")
