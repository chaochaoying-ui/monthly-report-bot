#!/usr/bin/env python3
"""
GitHub Actions版本的月报机器人
专为云端定时任务设计，无需WebSocket长连接
"""

import os
import json
import logging
import requests
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class FeishuBot:
    def __init__(self, config: Dict[str, str]):
        self.app_id = config['FEISHU_APP_ID']
        self.app_secret = config['FEISHU_APP_SECRET']
        self.verification_token = config['FEISHU_VERIFICATION_TOKEN']
        self.encrypt_key = config.get('FEISHU_ENCRYPT_KEY', '')
        self.chat_id = config['CHAT_ID']
        self.welcome_card_id = config.get('WELCOME_CARD_ID', 'AAqInYqWzIiu6')
        self.timezone = config.get('TIMEZONE', 'America/Argentina/Buenos_Aires')
        
        # 获取访问令牌
        self.access_token = self._get_access_token()
        
    def _get_access_token(self) -> str:
        """获取飞书访问令牌"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                return data['tenant_access_token']
            else:
                logger.error(f"获取访问令牌失败: {data}")
                raise Exception(f"获取访问令牌失败: {data}")
        else:
            logger.error(f"请求失败: {response.status_code}")
            raise Exception(f"请求失败: {response.status_code}")
    
    def send_message(self, message_type: str, content: Dict) -> bool:
        """发送消息到群聊"""
        url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "receive_id": self.chat_id,
            "msg_type": message_type,
            "content": json.dumps(content, ensure_ascii=False)
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            logger.info(f"API请求详情: URL={url}, Status={response.status_code}")
            logger.info(f"请求载荷: {payload}")
            logger.info(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    logger.info(f"消息发送成功: {data.get('msg_id')}")
                    return True
                else:
                    logger.error(f"消息发送失败: {data}")
                    return False
            else:
                logger.error(f"请求失败: {response.status_code}, 响应: {response.text}")
                return False
        except Exception as e:
            logger.error(f"发送消息异常: {e}")
            return False
    
    def send_card(self, card_content: Dict) -> bool:
        """发送卡片消息"""
        return self.send_message("interactive", card_content)
    
    def send_text(self, text: str) -> bool:
        """发送文本消息"""
        return self.send_message("text", {"text": text})

def load_tasks() -> List[Dict]:
    """加载任务配置"""
    try:
        with open('tasks.yaml', 'r', encoding='utf-8') as f:
            tasks = yaml.safe_load(f)
        logger.info(f"加载了 {len(tasks)} 个任务")
        return tasks
    except Exception as e:
        logger.error(f"加载任务配置失败: {e}")
        return []

def create_task_card(task: Dict) -> Dict:
    """创建任务卡片"""
    return {
        "elements": [
            {
                "tag": "div",
                "text": {
                    "content": f"📋 **{task['title']}**",
                    "tag": "lark_md"
                }
            },
            {
                "tag": "div",
                "text": {
                    "content": f"📄 [查看文档]({task['doc_url']})",
                    "tag": "lark_md"
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "content": "✅ 已完成",
                            "tag": "plain_text"
                        },
                        "type": "primary",
                        "value": {
                            "action": "mark_complete",
                            "task_id": task['title']
                        }
                    }
                ]
            }
        ],
        "header": {
            "title": {
                "content": "月报任务",
                "tag": "plain_text"
            }
        }
    }

def test_api_connection() -> bool:
    """测试API连接"""
    logger.info("测试API连接...")
    
    try:
        bot = FeishuBot({
            'FEISHU_APP_ID': os.getenv('FEISHU_APP_ID'),
            'FEISHU_APP_SECRET': os.getenv('FEISHU_APP_SECRET'),
            'FEISHU_VERIFICATION_TOKEN': os.getenv('FEISHU_VERIFICATION_TOKEN'),
            'FEISHU_ENCRYPT_KEY': os.getenv('FEISHU_ENCRYPT_KEY', ''),
            'CHAT_ID': os.getenv('CHAT_ID'),
            'WELCOME_CARD_ID': os.getenv('WELCOME_CARD_ID', 'AAqInYqWzIiu6')
        })
        
        # 发送测试消息
        test_message = f"🧪 API连接测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        result = bot.send_text(test_message)
        
        if result:
            logger.info("✅ API连接测试成功")
            return True
        else:
            logger.error("❌ API连接测试失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ API连接测试异常: {e}")
        return False

def create_monthly_tasks() -> bool:
    """创建月度任务"""
    logger.info("开始创建月度任务...")
    
    # 先测试API连接
    if not test_api_connection():
        logger.error("API连接测试失败，终止任务创建")
        return False
    
    # 检查是否已经创建过（基于日期判断）
    current_date = datetime.now()
    month_key = f"{current_date.year}-{current_date.month}"
    
    # 这里可以添加幂等性检查逻辑
    # 比如检查是否已经创建过本月的任务
    
    tasks = load_tasks()
    if not tasks:
        logger.error("没有加载到任务配置")
        return False
    
    bot = FeishuBot({
        'FEISHU_APP_ID': os.getenv('FEISHU_APP_ID'),
        'FEISHU_APP_SECRET': os.getenv('FEISHU_APP_SECRET'),
        'FEISHU_VERIFICATION_TOKEN': os.getenv('FEISHU_VERIFICATION_TOKEN'),
        'FEISHU_ENCRYPT_KEY': os.getenv('FEISHU_ENCRYPT_KEY', ''),
        'CHAT_ID': os.getenv('CHAT_ID'),
        'WELCOME_CARD_ID': os.getenv('WELCOME_CARD_ID', 'AAqInYqWzIiu6')
    })
    
    success_count = 0
    for i, task in enumerate(tasks):
        try:
            logger.info(f"处理任务 {i+1}/{len(tasks)}: {task['title']}")
            
            # 创建任务卡片
            card = create_task_card(task)
            
            # 发送任务卡片
            if bot.send_card(card):
                success_count += 1
                logger.info(f"✅ 任务创建成功: {task['title']}")
            else:
                logger.error(f"❌ 任务创建失败: {task['title']}")
                
        except Exception as e:
            logger.error(f"❌ 创建任务异常: {task['title']}, {e}")
    
    logger.info(f"📊 任务创建完成: {success_count}/{len(tasks)}")
    return success_count > 0

def send_daily_stats() -> bool:
    """发送每日统计"""
    logger.info("发送每日统计...")
    
    bot = FeishuBot({
        'FEISHU_APP_ID': os.getenv('FEISHU_APP_ID'),
        'FEISHU_APP_SECRET': os.getenv('FEISHU_APP_SECRET'),
        'FEISHU_VERIFICATION_TOKEN': os.getenv('FEISHU_VERIFICATION_TOKEN'),
        'FEISHU_ENCRYPT_KEY': os.getenv('FEISHU_ENCRYPT_KEY', ''),
        'CHAT_ID': os.getenv('CHAT_ID'),
        'WELCOME_CARD_ID': os.getenv('WELCOME_CARD_ID', 'AAqInYqWzIiu6')
    })
    
    # 这里应该实现统计逻辑
    # 暂时发送一个简单的统计消息
    stats_text = f"📊 **每日统计** - {datetime.now().strftime('%Y-%m-%d')}\n\n"
    stats_text += "• 总任务数: 24\n"
    stats_text += "• 已完成: 待统计\n"
    stats_text += "• 完成率: 待计算\n\n"
    stats_text += "请各位负责人及时更新任务进度！"
    
    return bot.send_text(stats_text)

def send_final_reminder() -> bool:
    """发送最终提醒"""
    logger.info("发送最终提醒...")
    
    bot = FeishuBot({
        'FEISHU_APP_ID': os.getenv('FEISHU_APP_ID'),
        'FEISHU_APP_SECRET': os.getenv('FEISHU_APP_SECRET'),
        'FEISHU_VERIFICATION_TOKEN': os.getenv('FEISHU_VERIFICATION_TOKEN'),
        'FEISHU_ENCRYPT_KEY': os.getenv('FEISHU_ENCRYPT_KEY', ''),
        'CHAT_ID': os.getenv('CHAT_ID'),
        'WELCOME_CARD_ID': os.getenv('WELCOME_CARD_ID', 'AAqInYqWzIiu6')
    })
    
    reminder_text = f"🚨 **最终提醒** - {datetime.now().strftime('%Y-%m-%d')}\n\n"
    reminder_text += "⚠️ 月报截止日期临近，请未完成任务的负责人尽快完成！\n\n"
    reminder_text += "📋 未完成任务将另行通知\n"
    reminder_text += "📄 相关文档链接已在上方任务卡片中提供"
    
    return bot.send_text(reminder_text)

def send_final_stats() -> bool:
    """发送最终统计"""
    logger.info("发送最终统计...")
    
    bot = FeishuBot({
        'FEISHU_APP_ID': os.getenv('FEISHU_APP_ID'),
        'FEISHU_APP_SECRET': os.getenv('FEISHU_APP_SECRET'),
        'FEISHU_VERIFICATION_TOKEN': os.getenv('FEISHU_VERIFICATION_TOKEN'),
        'FEISHU_ENCRYPT_KEY': os.getenv('FEISHU_ENCRYPT_KEY', ''),
        'CHAT_ID': os.getenv('CHAT_ID'),
        'WELCOME_CARD_ID': os.getenv('WELCOME_CARD_ID', 'AAqInYqWzIiu6')
    })
    
    stats_text = f"📈 **月度统计报告** - {datetime.now().strftime('%Y年%m月')}\n\n"
    stats_text += "✅ 本月月报收集工作已完成\n"
    stats_text += "📊 详细统计信息:\n"
    stats_text += "• 总任务数: 24\n"
    stats_text += "• 完成情况: 待统计\n"
    stats_text += "• 完成率: 待计算\n\n"
    stats_text += "感谢各位负责人的配合！"
    
    return bot.send_text(stats_text)

if __name__ == "__main__":
    # 从命令行参数或环境变量确定要执行的任务
    task_type = os.getenv('TASK_TYPE', 'create_tasks')
    
    logger.info(f"执行任务类型: {task_type}")
    
    if task_type == 'create_tasks':
        success = create_monthly_tasks()
    elif task_type == 'daily_stats':
        success = send_daily_stats()
    elif task_type == 'final_reminder':
        success = send_final_reminder()
    elif task_type == 'final_stats':
        success = send_final_stats()
    else:
        logger.error(f"未知任务类型: {task_type}")
        success = False
    
    if success:
        logger.info("任务执行成功")
        sys.exit(0)
    else:
        logger.error("任务执行失败")
        sys.exit(1)
