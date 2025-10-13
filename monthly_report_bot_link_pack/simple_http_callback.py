#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的HTTP回调服务器
用于处理新成员欢迎功能
"""

import os
import json
import logging
import requests
from flask import Flask, request, jsonify
import hmac
import hashlib
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 环境变量
APP_ID = os.environ.get("APP_ID", "cli_a8fd44a9453cd00c")
APP_SECRET = os.environ.get("APP_SECRET", "jsVoFWgaaw05en6418h7xbhV5oXxAwIm")
WELCOME_CARD_ID = os.environ.get("WELCOME_CARD_ID", "AAqInYqWzIiu6")
VERIFICATION_TOKEN = os.environ.get("VERIFICATION_TOKEN", "your_verification_token_here")

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

def send_welcome_card_to_user(user_id: str) -> bool:
    """向用户发送欢迎卡片"""
    token = get_tenant_token()
    if not token:
        return False
    
    try:
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 使用模板卡片格式（根据您的代码）
        payload = {
            "receive_id": user_id,
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
            params={"receive_id_type": "user_id"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                logger.info("欢迎卡片发送成功，用户ID: %s", user_id)
                return True
            else:
                logger.error("欢迎卡片发送失败: %s", data.get("msg"))
                return False
        else:
            logger.error("欢迎卡片发送HTTP错误: %d", response.status_code)
            return False
            
    except Exception as e:
        logger.error("发送欢迎卡片异常: %s", e)
        return False

def verify_signature(timestamp: str, nonce: str, signature: str, body: str) -> bool:
    """验证签名"""
    try:
        # 构建签名字符串
        sign_string = f"{timestamp}{nonce}{VERIFICATION_TOKEN}{body}"
        
        # 计算签名
        expected_signature = hmac.new(
            VERIFICATION_TOKEN.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        logger.error("验证签名失败: %s", e)
        return False

@app.route('/webhook', methods=['POST'])
def webhook():
    """处理飞书回调"""
    try:
        # 获取请求头
        timestamp = request.headers.get('X-Lark-Request-Timestamp', '')
        nonce = request.headers.get('X-Lark-Request-Nonce', '')
        signature = request.headers.get('X-Lark-Signature', '')
        
        # 获取请求体
        body = request.get_data(as_text=True)
        
        # 验证签名（暂时跳过以便测试）
        if timestamp and nonce and signature:
            if not verify_signature(timestamp, nonce, signature, body):
                logger.warning("签名验证失败")
                return jsonify({"code": 1, "msg": "签名验证失败"}), 401
        else:
            logger.info("跳过签名验证（测试模式）")
        
        # 解析请求数据
        data = json.loads(body)
        logger.info("收到回调: %s", json.dumps(data, ensure_ascii=False))
        
        # 处理URL验证
        if data.get("type") == "url_verification":
            challenge = data.get("challenge")
            if challenge:
                logger.info("URL验证成功")
                return jsonify({"challenge": challenge})
        
        # 处理事件回调
        elif data.get("type") == "event_callback":
            event = data.get("event", {})
            event_type = event.get("type")
            
            if event_type == "im.chat.member.user.added_v1":
                # 处理用户加入事件
                users = event.get("users", [])
                success_count = 0
                
                for user in users:
                    user_id = user.get("user_id")
                    if user_id:
                        if send_welcome_card_to_user(user_id):
                            success_count += 1
                            logger.info("成功向用户 %s 发送欢迎卡片", user_id)
                        else:
                            logger.error("向用户 %s 发送欢迎卡片失败", user_id)
                
                logger.info("用户加入事件处理完成，成功: %d/%d", success_count, len(users))
                
            elif event_type == "im.chat.member.bot.added_v1":
                # 处理机器人加入事件
                bots = event.get("bots", [])
                logger.info("机器人加入群聊: %s", bots)
                
                # 这里可以选择是否向机器人发送欢迎卡片
                # 通常不需要，因为机器人无法接收消息
                
            else:
                logger.info("收到其他事件: %s", event_type)
        
        return jsonify({"code": 0, "msg": "success"})
        
    except Exception as e:
        logger.error("处理回调异常: %s", e)
        return jsonify({"code": 1, "msg": "处理失败"}), 500

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "ok", "timestamp": time.time()})

if __name__ == "__main__":
    logger.info("启动HTTP回调服务器...")
    logger.info("欢迎卡片ID: %s", WELCOME_CARD_ID)
    
    # 启动服务器
    app.run(host='0.0.0.0', port=8080, debug=False)
