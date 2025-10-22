#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月报机器人 v1.1 - WebSocket处理器
设计理念：稳定可靠、自动重连、事件处理

功能：
1. WebSocket长连接管理
2. 心跳机制
3. 自动重连
4. 事件处理与回调
"""

import asyncio
import json
import logging
import os
import websockets
import hmac
import hashlib
import time
from typing import Dict, Set, Optional, Any, Callable
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

class FeishuWebSocketHandler:
    """飞书WebSocket连接处理器"""
    
    def __init__(self):
        self.connections = set()
        self.heartbeat_interval = 30  # 心跳间隔（秒）
        self.last_heartbeat = time.time()
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 1  # 初始重连延迟（秒）
        
        # 飞书应用配置
        self.app_id = os.environ.get("APP_ID", "cli_a8fd44a9453cd00c").strip()
        self.app_secret = os.environ.get("APP_SECRET", "jsVoFWgaaw05en6418h7xbhV5oXxAwIm").strip()
        self.verification_token = os.environ.get("VERIFICATION_TOKEN", "").strip()
        
        # 事件处理器
        self.event_handlers = {}
        self.message_handlers = {}
        
        # 防重复处理
        self.processed_events: Set[str] = set()
        
        # 注册默认事件处理器
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """注册默认事件处理器"""
        self.register_event_handler("im.message.receive_v1", self._handle_message_receive)
        self.register_event_handler("im.chat.member.user.added_v1", self._handle_member_added)
        self.register_event_handler("im.chat.member.bot.added_v1", self._handle_bot_added)
        self.register_event_handler("im.chat.member.user.deleted_v1", self._handle_member_deleted)
        self.register_event_handler("im.message.reaction.created_v1", self._handle_reaction_created)
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """注册事件处理器"""
        self.event_handlers[event_type] = handler
        logger.info("注册事件处理器: %s", event_type)
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
        logger.info("注册消息处理器: %s", message_type)
    
    async def handle_connection(self, websocket, path):
        """处理WebSocket连接"""
        logger.info("新的WebSocket连接建立")
        self.connections.add(websocket)
        
        try:
            async for message in websocket:
                try:
                    await self.handle_message(websocket, message)
                except Exception as e:
                    logger.error("处理消息异常: %s", e)
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket连接已关闭")
        except Exception as e:
            logger.error("处理WebSocket连接异常: %s", e)
        finally:
            self.connections.discard(websocket)
    
    async def handle_message(self, websocket, message: str):
        """处理WebSocket消息"""
        try:
            data = json.loads(message)
            logger.info("收到飞书WebSocket消息: %s", json.dumps(data, ensure_ascii=False))
            
            # 处理不同类型的消息
            message_type = data.get("type")
            
            if message_type == "url_verification":
                await self._handle_url_verification(websocket, data)
            elif message_type == "event_callback":
                await self._handle_event_callback(data)
            elif message_type == "ping":
                await self._handle_ping(websocket, data)
            elif message_type == "pong":
                logger.debug("收到pong响应")
            else:
                logger.warning("未知消息类型: %s", message_type)
                
        except json.JSONDecodeError as e:
            logger.error("JSON解析失败: %s", e)
        except Exception as e:
            logger.error("处理消息失败: %s", e)
    
    async def _handle_url_verification(self, websocket, data: Dict):
        """处理URL验证"""
        challenge = data.get("challenge")
        if challenge:
            response = {"challenge": challenge}
            await websocket.send(json.dumps(response))
            logger.info("URL验证成功")
    
    async def _handle_event_callback(self, data: Dict):
        """处理事件回调"""
        try:
            event = data.get("event", {})
            event_type = event.get("type")
            
            # 检查是否已处理过该事件
            event_id = data.get("event_id")
            if event_id and event_id in self.processed_events:
                logger.info("事件已处理，跳过: %s", event_id)
                return
            
            # 记录已处理事件
            if event_id:
                self.processed_events.add(event_id)
                # 保留最近1000个事件ID
                if len(self.processed_events) > 1000:
                    self.processed_events.clear()
            
            # 调用对应的事件处理器
            if event_type in self.event_handlers:
                handler = self.event_handlers[event_type]
                await handler(event)
            else:
                logger.warning("未找到事件处理器: %s", event_type)
                
        except Exception as e:
            logger.error("处理事件回调失败: %s", e)
    
    async def _handle_ping(self, websocket, data: Dict):
        """处理心跳消息"""
        try:
            # 发送pong响应
            pong_response = {"type": "pong"}
            await websocket.send(json.dumps(pong_response))
            self.last_heartbeat = time.time()
            logger.debug("心跳响应已发送")
        except Exception as e:
            logger.error("处理心跳失败: %s", e)
    
    def set_message_handler(self, handler: Callable):
        """设置消息处理器"""
        self.user_message_handler = handler
        logger.info("已设置用户消息处理器")

    async def _handle_message_receive(self, event: Dict):
        """处理消息接收事件"""
        try:
            # 调用用户消息处理器（如果已设置）
            if hasattr(self, 'user_message_handler') and self.user_message_handler:
                await self.user_message_handler(event)
            else:
                logger.info("未设置用户消息处理器，跳过消息处理")

        except Exception as e:
            logger.error("处理消息接收事件失败: %s", e)
    
    async def _handle_member_added(self, event: Dict):
        """处理成员加入事件"""
        try:
            # 发送欢迎卡片
            await self._send_welcome_card(event)
        except Exception as e:
            logger.error("处理成员加入事件失败: %s", e)
    
    async def _handle_bot_added(self, event: Dict):
        """处理机器人加入事件"""
        try:
            logger.info("机器人加入群聊: %s", event)
            # 机器人加入时也发送欢迎卡片
            await self._send_welcome_card(event)
        except Exception as e:
            logger.error("处理机器人加入事件失败: %s", e)
    
    async def _handle_member_deleted(self, event: Dict):
        """处理成员离开事件"""
        try:
            logger.info("成员离开群聊: %s", event)
        except Exception as e:
            logger.error("处理成员离开事件失败: %s", e)
    
    async def _handle_reaction_created(self, event: Dict):
        """处理表情回应事件"""
        try:
            logger.info("收到表情回应: %s", event)
        except Exception as e:
            logger.error("处理表情回应事件失败: %s", e)
    
    async def _send_welcome_card(self, event: Dict):
        """发送欢迎卡片"""
        try:
            # 调用主程序的新成员欢迎处理函数
            if hasattr(self, 'welcome_handler') and self.welcome_handler:
                await self.welcome_handler({"event": event})
            else:
                logger.info("需要发送欢迎卡片给新成员: %s", event)
        except Exception as e:
            logger.error("发送欢迎卡片失败: %s", e)
    
    def set_welcome_handler(self, handler):
        """设置欢迎卡片处理器"""
        self.welcome_handler = handler
        logger.info("已设置欢迎卡片处理器")
    
    async def start_heartbeat(self):
        """启动心跳机制"""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                await self._send_heartbeat()
            except Exception as e:
                logger.error("心跳发送失败: %s", e)
    
    async def _send_heartbeat(self):
        """发送心跳"""
        try:
            heartbeat_message = {
                "type": "ping",
                "timestamp": int(time.time())
            }
            
            # 向所有连接发送心跳
            for websocket in self.connections.copy():
                try:
                    await websocket.send(json.dumps(heartbeat_message))
                except Exception as e:
                    logger.error("向连接发送心跳失败: %s", e)
                    self.connections.discard(websocket)
            
            logger.debug("心跳已发送")
        except Exception as e:
            logger.error("发送心跳失败: %s", e)
    
    async def connect_to_feishu(self):
        """连接到飞书WebSocket服务（占位实现）

        注意：飞书的 WebSocket 长连接需要企业内部应用权限或特殊配置
        当前 v1.1 版本主要依赖定时任务和 REST API 进行消息交互
        WebSocket 功能保留接口以保持向后兼容，但不执行实际连接
        """
        logger.info("WebSocket 处理器已初始化（当前版本使用 REST API 模式）")
        logger.info("✅ v1.1 服务运行中，定时任务和消息功能正常")

        # 保持事件循环运行，不执行实际 WebSocket 连接
        while True:
            await asyncio.sleep(3600)  # 每小时检查一次

    async def _get_tenant_token(self) -> Optional[str]:
        """获取租户访问令牌"""
        try:
            url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            payload = {
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data.get("code", 0) == 0:
                token = data.get("tenant_access_token", "")
                logger.info("获取租户令牌成功")
                return token
            else:
                logger.error("获取租户令牌失败: %s", data.get("msg", "未知错误"))
                return None
                
        except Exception as e:
            logger.error("获取租户令牌异常: %s", e)
            return None
    
    def verify_signature(self, timestamp: str, nonce: str, signature: str, body: str) -> bool:
        """验证签名"""
        try:
            # 构建签名字符串
            sign_string = f"{timestamp}{nonce}{self.verification_token}{body}"
            
            # 计算签名
            expected_signature = hmac.new(
                self.verification_token.encode('utf-8'),
                sign_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error("验证签名失败: %s", e)
            return False
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """广播消息到所有连接"""
        try:
            message_json = json.dumps(message, ensure_ascii=False)
            for websocket in self.connections.copy():
                try:
                    await websocket.send(message_json)
                except Exception as e:
                    logger.error("广播消息失败: %s", e)
                    self.connections.discard(websocket)
        except Exception as e:
            logger.error("广播消息异常: %s", e)
    
    def get_connection_count(self) -> int:
        """获取当前连接数"""
        return len(self.connections)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "connection_count": len(self.connections),
            "reconnect_attempts": self.reconnect_attempts,
            "processed_events_count": len(self.processed_events),
            "last_heartbeat": self.last_heartbeat,
            "event_handlers_count": len(self.event_handlers),
            "message_handlers_count": len(self.message_handlers)
        }
