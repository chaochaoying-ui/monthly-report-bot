#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试飞书WebSocket长连接API
检查最新的API端点和连接方式
"""

import os
import json
import requests
import asyncio
import websockets
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

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
            logger.error("获取token失败: %s", data.get("msg"))
            return None
    except Exception as e:
        logger.error("获取token异常: %s", e)
        return None

def test_websocket_endpoints():
    """测试不同的WebSocket端点"""
    token = get_tenant_token()
    if not token:
        logger.error("无法获取token")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 测试不同的WebSocket端点
    endpoints = [
        "https://open.feishu.cn/open-apis/ws/v2/connect",
        "https://open.feishu.cn/open-apis/ws/v3/connect",
        "https://open.feishu.cn/open-apis/ws/connect",
        "https://open.feishu.cn/open-apis/event/v1/outbound_ip",
        "https://open.feishu.cn/open-apis/application/v3/applications/me"
    ]
    
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    
    for endpoint in endpoints:
        logger.info(f"\n测试端点: {endpoint}")
        try:
            if "outbound_ip" in endpoint or "applications" in endpoint:
                response = requests.get(endpoint, headers=headers, timeout=10)
            else:
                response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            
            logger.info(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            else:
                logger.error(f"错误: {response.text}")
                
        except Exception as e:
            logger.error(f"异常: {e}")

async def test_websocket_connection():
    """测试WebSocket连接"""
    token = get_tenant_token()
    if not token:
        logger.error("无法获取token")
        return
    
    # 尝试不同的WebSocket URL格式
    ws_urls = [
        "wss://open.feishu.cn/ws/v2",
        "wss://open.feishu.cn/ws/v3",
        "wss://open.feishu.cn/ws"
    ]
    
    for ws_url in ws_urls:
        logger.info(f"\n尝试连接WebSocket: {ws_url}")
        try:
            async with websockets.connect(ws_url) as websocket:
                logger.info(f"✅ 成功连接到 {ws_url}")
                
                # 发送认证消息
                auth_message = {
                    "type": "auth",
                    "app_id": APP_ID,
                    "app_secret": APP_SECRET
                }
                await websocket.send(json.dumps(auth_message))
                logger.info("已发送认证消息")
                
                # 等待响应
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10)
                    logger.info(f"收到响应: {response}")
                except asyncio.TimeoutError:
                    logger.warning("等待响应超时")
                
                break
                
        except Exception as e:
            logger.error(f"❌ 连接失败 {ws_url}: {e}")

def test_event_subscription():
    """测试事件订阅配置"""
    token = get_tenant_token()
    if not token:
        logger.error("无法获取token")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 测试获取应用信息
    try:
        url = "https://open.feishu.cn/open-apis/application/v3/applications/me"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info("应用信息:")
            logger.info(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            logger.error(f"获取应用信息失败: {response.status_code}")
            
    except Exception as e:
        logger.error(f"获取应用信息异常: {e}")

if __name__ == "__main__":
    logger.info("🔍 测试飞书WebSocket长连接API...")
    
    # 1. 测试WebSocket端点
    logger.info("\n1. 测试WebSocket端点...")
    test_websocket_endpoints()
    
    # 2. 测试WebSocket连接
    logger.info("\n2. 测试WebSocket连接...")
    asyncio.run(test_websocket_connection())
    
    # 3. 测试事件订阅
    logger.info("\n3. 测试事件订阅...")
    test_event_subscription()
    
    logger.info("\n✅ 测试完成！")

