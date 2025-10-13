#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模板卡片发送功能
基于用户提供的代码
"""

import os
import json
import requests

# 配置信息 - 使用环境变量或默认值
APP_ID = os.getenv("APP_ID", "cli_a8fd44a9453cd00c")
APP_SECRET = os.getenv("APP_SECRET", "jsVoFWgaaw05en6418h7xbhV5oXxAwIm")
CHAT_ID = os.getenv("CHAT_ID", "oc_07f2d3d314f00fc29baf323a3a589972")
CARD_ID = "AAqInYqWzIiu6"  # 请确认卡片ID正确（应该是16位字符）

print("=" * 60)
print("模板卡片发送测试")
print("=" * 60)
print(f"APP_ID: {APP_ID}")
print(f"CHAT_ID: {CHAT_ID}")
print(f"CARD_ID: {CARD_ID} (长度: {len(CARD_ID)})")
print()

def test_template_card():
    """测试发送模板卡片"""
    try:
        # 获取 tenant_access_token
        print("1. 获取 tenant_access_token...")
        token_resp = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": APP_ID, "app_secret": APP_SECRET}
        ).json()

        print("Token响应:", token_resp)

        if token_resp.get("code") != 0:
            print(f"❌ 获取 token 失败: {token_resp}")
            return False

        token = token_resp["tenant_access_token"]
        print(f"✅ Token 获取成功: {token[:10]}...")
        print()

        # 正确的模板卡片消息格式
        print("2. 发送模板卡片...")
        payload = {
            "receive_id": CHAT_ID,
            "msg_type": "interactive",
            "content": json.dumps({
                "type": "template",  # 关键修改：type改为template
                "data": {
                    "template_id": CARD_ID,  # 关键修改：使用template_id
                    "template_variable": {   # 添加模板变量
                        "title": "月度报告",
                        "content": "这是通过Python发送的卡片消息",
                        "username": "系统管理员",
                        "welcome_message": "🎉 欢迎加入我们的群聊！"
                    }
                }
            }, ensure_ascii=False)
        }

        print("发送的payload:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print()

        # 发送消息（使用params参数更规范）
        resp = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/messages",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8"
            },
            params={"receive_id_type": "chat_id"},  # 参数移出URL
            json=payload
        ).json()

        print("完整响应:", json.dumps(resp, indent=2, ensure_ascii=False))
        print()

        # 结果分析
        if resp.get("code") == 0:
            print("✅ 消息发送成功!")
            print(f"消息ID: {resp['data']['message_id']}")
            
            # 获取消息内容验证卡片类型
            print("\n3. 获取消息内容验证...")
            message_id = resp['data']['message_id']
            content_resp = requests.get(
                f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}",
                headers={"Authorization": f"Bearer {token}"},
                params={"user_id_type": "user_id"}
            ).json()
            
            if content_resp.get("code") == 0:
                card_content = content_resp.get('data', {}).get('body', {}).get('content', '')
                print(f"消息内容: {card_content[:200]}...")
            else:
                print(f"❌ 无法获取消息内容: {content_resp.get('msg')}")
            
            return True
        else:
            print(f"❌ 发送失败: {resp.get('msg')}")
            print(f"错误代码: {resp.get('code')}")
            print("排查建议: https://open.feishu.cn/document/server-docs/im-v1/message/create")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_text_message():
    """测试发送文本消息"""
    try:
        print("\n4. 测试发送文本消息...")
        
        # 获取 token
        token_resp = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": APP_ID, "app_secret": APP_SECRET}
        ).json()
        
        if token_resp.get("code") != 0:
            print(f"❌ 获取 token 失败: {token_resp}")
            return False
            
        token = token_resp["tenant_access_token"]
        
        # 发送文本消息
        payload = {
            "receive_id": CHAT_ID,
            "msg_type": "text",
            "content": json.dumps({
                "text": "🧪 测试消息：模板卡片功能测试完成！"
            }, ensure_ascii=False)
        }
        
        resp = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/messages",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8"
            },
            params={"receive_id_type": "chat_id"},
            json=payload
        ).json()
        
        if resp.get("code") == 0:
            print("✅ 文本消息发送成功!")
            return True
        else:
            print(f"❌ 文本消息发送失败: {resp.get('msg')}")
            return False
            
    except Exception as e:
        print(f"❌ 文本消息测试异常: {e}")
        return False

if __name__ == "__main__":
    # 设置环境变量
    os.environ["APP_ID"] = APP_ID
    os.environ["APP_SECRET"] = APP_SECRET
    os.environ["CHAT_ID"] = CHAT_ID
    
    # 测试模板卡片
    card_ok = test_template_card()
    
    # 测试文本消息
    text_ok = test_text_message()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print(f"模板卡片发送: {'✅ 成功' if card_ok else '❌ 失败'}")
    print(f"文本消息发送: {'✅ 成功' if text_ok else '❌ 失败'}")
    
    if card_ok and text_ok:
        print("\n🎉 所有测试通过！模板卡片功能正常工作")
        print("\n📋 下一步配置:")
        print("1. 在飞书后台配置HTTP回调")
        print("2. 设置回调URL: http://190.210.214.21:8080/webhook")
        print("3. 订阅事件: im.chat.member.user.added_v1, im.chat.member.bot.added_v1")
    else:
        print("\n⚠️ 部分测试失败，请检查配置")

