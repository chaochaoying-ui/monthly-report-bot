#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
长轮询事件处理器
作为WebSocket的替代方案，使用HTTP长轮询来接收飞书事件
"""

import os
import json
import logging
import requests
import asyncio
import time
from typing import Dict, Set, Optional, Any, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class FeishuLongPollingHandler:
    """飞书长轮询事件处理器"""
    
    def __init__(self):
        # 飞书应用配置
        self.app_id = os.environ.get("APP_ID", "cli_a8fd44a9453cd00c")
        self.app_secret = os.environ.get("APP_SECRET", "jsVoFWgaaw05en6418h7xbhV5oXxAwIm")
        self.verification_token = os.environ.get("VERIFICATION_TOKEN", "test_token")
        
        # 事件处理器
        self.event_handlers = {}
        self.message_handlers = {}
        
        # 防重复处理
        self.processed_events: Set[str] = set()
        
        # 轮询配置
        self.polling_interval = 5  # 轮询间隔（秒）
        self.max_retries = 3
        self.retry_delay = 10
        
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
    
    async def _poll_events(self):
        """轮询事件"""
        token = await self._get_tenant_token()
        if not token:
            return
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 尝试获取事件（这里使用模拟的事件数据）
        # 实际实现中，飞书可能提供事件轮询API
        try:
            # 模拟事件轮询
            await self._simulate_event_polling()
        except Exception as e:
            logger.error("轮询事件异常: %s", e)
    
    async def _simulate_event_polling(self):
        """模拟事件轮询（用于测试）"""
        logger.info("模拟事件轮询...")
        
        # 模拟一些事件数据
        mock_events = [
            {
                "type": "event_callback",
                "event_id": f"mock_event_{int(time.time())}",
                "event": {
                    "type": "im.chat.member.user.added_v1",
                    "chat_id": "oc_07f2d3d314f00fc29baf323a3a589972",
                    "users": [
                        {
                            "user_id": "mock_user_123",
                            "name": "模拟用户"
                        }
                    ]
                }
            }
        ]
        
        for event_data in mock_events:
            await self._handle_event_callback(event_data)
    
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
            
            logger.info("收到事件: %s", event_type)
            
            # 调用对应的事件处理器
            if event_type in self.event_handlers:
                handler = self.event_handlers[event_type]
                await handler(event)
            else:
                logger.warning("未找到事件处理器: %s", event_type)
                
        except Exception as e:
            logger.error("处理事件回调失败: %s", e)
    
    async def _handle_message_receive(self, event: Dict):
        """处理消息接收事件"""
        try:
            message = event.get("message", {})
            message_type = message.get("content", {}).get("type")
            
            # 调用对应的消息处理器
            if message_type in self.message_handlers:
                handler = self.message_handlers[message_type]
                await handler(event)
            else:
                logger.info("未找到消息处理器: %s", message_type)
                
        except Exception as e:
            logger.error("处理消息接收事件失败: %s", e)
    
    async def _handle_member_added(self, event: Dict):
        """处理成员加入事件"""
        try:
            logger.info("处理成员加入事件: %s", event)
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
    
    async def start_polling(self):
        """启动长轮询"""
        logger.info("启动长轮询事件处理...")
        
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                await self._poll_events()
                retry_count = 0  # 重置重试计数
                
                # 等待下次轮询
                await asyncio.sleep(self.polling_interval)
                
            except Exception as e:
                logger.error("轮询异常: %s", e)
                retry_count += 1
                
                if retry_count < self.max_retries:
                    logger.info("等待 %d 秒后重试...", self.retry_delay)
                    await asyncio.sleep(self.retry_delay)
        
        logger.error("达到最大重试次数，停止轮询")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "processed_events_count": len(self.processed_events),
            "event_handlers_count": len(self.event_handlers),
            "message_handlers_count": len(self.message_handlers),
            "polling_interval": self.polling_interval
        }

