#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于飞书官方SDK的长轮询事件处理器
使用lark-oapi SDK实现更稳定的事件处理
"""

import os
import json
import logging
import asyncio
import time
from typing import Dict, Set, Optional, Any, Callable
from datetime import datetime

import lark_oapi as lark
from lark_oapi.api.im.v1 import *

logger = logging.getLogger(__name__)

class LarkSDKHandler:
    """基于飞书官方SDK的事件处理器"""
    
    def __init__(self):
        # 飞书应用配置
        self.app_id = os.environ.get("APP_ID", "cli_a8fd44a9453cd00c")
        self.app_secret = os.environ.get("APP_SECRET", "jsVoFWgaaw05en6418h7xbhV5oXxAwIm")
        self.verification_token = os.environ.get("VERIFICATION_TOKEN", "test_token")
        
        # 创建飞书客户端
        self.client = lark.Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .log_level(lark.LogLevel.INFO) \
            .build()
        
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
    
    async def send_template_card(self, user_id: str, template_id: str, template_variables: Dict) -> bool:
        """使用官方SDK发送模板卡片"""
        try:
            # 构造请求对象
            request = CreateMessageRequest.builder() \
                .receive_id_type("user_id") \
                .request_body(CreateMessageRequestBody.builder()
                            .receive_id(user_id)
                            .msg_type("interactive")
                            .content(json.dumps({
                                "type": "template",
                                "data": {
                                    "template_id": template_id,
                                    "template_variable": template_variables
                                }
                            }, ensure_ascii=False))
                            .build()) \
                .build()
            
            # 发起请求
            response = await self.client.im.v1.message.acreate(request)
            
            # 处理失败返回
            if not response.success():
                logger.error(f"发送模板卡片失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
                return False
            
            # 处理业务结果
            logger.info("模板卡片发送成功: %s", lark.JSON.marshal(response.data, indent=4))
            return True
            
        except Exception as e:
            logger.error("发送模板卡片异常: %s", e)
            return False
    
    async def send_text_message(self, user_id: str, text: str) -> bool:
        """使用官方SDK发送文本消息"""
        try:
            # 构造请求对象
            request = CreateMessageRequest.builder() \
                .receive_id_type("user_id") \
                .request_body(CreateMessageRequestBody.builder()
                            .receive_id(user_id)
                            .msg_type("text")
                            .content(json.dumps({"text": text}, ensure_ascii=False))
                            .build()) \
                .build()
            
            # 发起请求
            response = await self.client.im.v1.message.acreate(request)
            
            # 处理失败返回
            if not response.success():
                logger.error(f"发送文本消息失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
                return False
            
            # 处理业务结果
            logger.info("文本消息发送成功: %s", lark.JSON.marshal(response.data, indent=4))
            return True
            
        except Exception as e:
            logger.error("发送文本消息异常: %s", e)
            return False
    
    async def start_polling(self):
        """启动长轮询"""
        logger.info("启动基于官方SDK的长轮询事件处理...")
        
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                await self._simulate_event_polling()
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
            "polling_interval": self.polling_interval,
            "sdk_version": "lark-oapi"
        }
