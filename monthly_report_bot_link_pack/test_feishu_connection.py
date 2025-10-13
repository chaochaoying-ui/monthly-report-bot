#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试飞书WebSocket连接
"""

import os
import asyncio
import requests
import json

# 环境变量
APP_ID = os.environ.get("APP_ID", "cli_a8fd44a9453cd00c")
APP_SECRET = os.environ.get("APP_SECRET", "jsVoFWgaaw05en6418h7xbhV5oXxAwIm")

async def test_feishu_connection():
    """测试飞书连接"""
    print("🧪 测试飞书WebSocket连接...")
    
    # 1. 获取tenant token
    print("\n1. 获取tenant token...")
    token = await get_tenant_token()
    if not token:
        print("❌ 获取token失败")
        return False
    
    print("✅ 获取token成功")
    
    # 2. 获取WebSocket连接URL
    print("\n2. 获取WebSocket连接URL...")
    ws_url = await get_websocket_url(token)
    if not ws_url:
        print("❌ 获取WebSocket URL失败")
        return False
    
    print(f"✅ 获取WebSocket URL成功: {ws_url}")
    
    # 3. 测试连接
    print("\n3. 测试WebSocket连接...")
    try:
        import websockets
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket连接成功")
            
            # 等待一些消息
            print("等待飞书消息...")
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"📥 收到消息: {message}")
            except asyncio.TimeoutError:
                print("⏰ 10秒内没有收到消息（这是正常的）")
            
            return True
            
    except Exception as e:
        print(f"❌ WebSocket连接失败: {e}")
        return False

async def get_tenant_token():
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

async def get_websocket_url(token):
    """获取WebSocket连接URL"""
    # 飞书官方文档的正确API路径
    url = "https://open.feishu.cn/open-apis/ws/v2/connect"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print(f"API响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        if data.get("code", 0) == 0:
            ws_url = data.get("data", {}).get("ws_url")
            return ws_url
        else:
            print(f"获取WebSocket URL失败: {data.get('msg', '未知错误')}")
            return None
            
    except Exception as e:
        print(f"获取WebSocket URL异常: {e}")
        return None

if __name__ == "__main__":
    success = asyncio.run(test_feishu_connection())
    if success:
        print("\n✅ 飞书连接测试成功！")
    else:
        print("\n❌ 飞书连接测试失败！")
