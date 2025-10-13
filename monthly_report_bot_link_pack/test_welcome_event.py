#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新成员欢迎事件
"""

import json
import asyncio
import websockets

# 模拟新成员加入事件数据
MOCK_USER_ADDED_EVENT = {
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

MOCK_BOT_ADDED_EVENT = {
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

async def test_welcome_event():
    """测试欢迎事件处理"""
    uri = "ws://localhost:8080"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ 连接到WebSocket服务器成功")
            
            # 发送用户加入事件
            print("\n📤 发送用户加入事件...")
            await websocket.send(json.dumps(MOCK_USER_ADDED_EVENT))
            
            # 等待响应
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 收到响应: {response}")
            except asyncio.TimeoutError:
                print("⏰ 等待响应超时（这是正常的，因为事件处理是异步的）")
            
            # 发送机器人加入事件
            print("\n📤 发送机器人加入事件...")
            await websocket.send(json.dumps(MOCK_BOT_ADDED_EVENT))
            
            # 等待响应
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 收到响应: {response}")
            except asyncio.TimeoutError:
                print("⏰ 等待响应超时（这是正常的，因为事件处理是异步的）")
                
    except Exception as e:
        print(f"❌ 连接失败: {e}")

if __name__ == "__main__":
    print("🧪 开始测试新成员欢迎事件...")
    asyncio.run(test_welcome_event())
    print("\n✅ 测试完成！")

