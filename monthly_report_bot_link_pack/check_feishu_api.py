#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查飞书API路径
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

def test_api_endpoints():
    """测试不同的API端点"""
    token = get_tenant_token()
    if not token:
        print("无法获取token")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 测试不同的API端点
    endpoints = [
        "https://open.feishu.cn/open-apis/ws/v2/connect",
        "https://open.feishu.cn/open-apis/ws/v2/connect/",
        "https://open.feishu.cn/open-apis/ws/connect",
        "https://open.feishu.cn/open-apis/event/v1/outbound_ip",
        "https://open.feishu.cn/open-apis/application/v3/applications/me"
    ]
    
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    
    for endpoint in endpoints:
        print(f"\n测试端点: {endpoint}")
        try:
            if "outbound_ip" in endpoint or "applications" in endpoint:
                response = requests.get(endpoint, headers=headers, timeout=10)
            else:
                response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            else:
                print(f"错误: {response.text}")
                
        except Exception as e:
            print(f"异常: {e}")

if __name__ == "__main__":
    print("🔍 检查飞书API端点...")
    test_api_endpoints()
    print("\n✅ 检查完成！")

