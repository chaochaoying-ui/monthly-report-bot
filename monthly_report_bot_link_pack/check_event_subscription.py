#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查飞书事件订阅配置
"""

import os
import requests
import json

# 环境变量
APP_ID = os.environ.get("APP_ID", "cli_a8fd44a9453cd00c")
APP_SECRET = os.environ.get("APP_SECRET", "jsVoFWgaaw05en6418h7xbhV5oXxAwIm")

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

def check_event_subscription():
    """检查事件订阅配置"""
    token = get_tenant_token()
    if not token:
        print("无法获取access token")
        return
    
    url = "https://open.feishu.cn/open-apis/event/v1/outbound_ip"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print("=== 飞书事件订阅配置检查 ===")
        print(f"响应状态: {data.get('code')}")
        print(f"响应消息: {data.get('msg')}")
        
        if data.get("code") == 0:
            print("✅ 事件订阅配置正常")
        else:
            print("❌ 事件订阅配置异常")
            
    except Exception as e:
        print(f"检查事件订阅异常: {e}")

def check_app_info():
    """检查应用信息"""
    token = get_tenant_token()
    if not token:
        print("无法获取access token")
        return
    
    url = "https://open.feishu.cn/open-apis/application/v3/applications/me"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print("\n=== 应用信息 ===")
        if data.get("code") == 0:
            app_info = data.get("data", {})
            print(f"应用名称: {app_info.get('name')}")
            print(f"应用描述: {app_info.get('description')}")
            print(f"应用状态: {app_info.get('status')}")
        else:
            print(f"获取应用信息失败: {data.get('msg')}")
            
    except Exception as e:
        print(f"获取应用信息异常: {e}")

if __name__ == "__main__":
    print("开始检查飞书配置...")
    check_event_subscription()
    check_app_info()
    print("\n检查完成！")

