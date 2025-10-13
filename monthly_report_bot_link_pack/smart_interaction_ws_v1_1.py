#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月报机器人 v1.1 - 智能交互引擎
设计理念：文本优先、多语言支持、智能识别、安全权限

功能：
1. 多语言意图识别（中/英/西语）
2. 实体抽取（时间、人名、任务别名）
3. 权限控制与安全验证
4. 降级机制与回退策略
"""

from __future__ import annotations
import re
import json
import math
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# 多语言关键词配置（按照需求文档5.1）
INTENT_KEYWORDS = {
    "zh": {
        "query_tasks": ["我的任务", "我的清单", "查看任务", "任务列表", "我的工作"],
        "mark_completed": ["已完成", "完成", "完毕", "搞定", "ok", "好了", "结束", "做完了"],
        "request_extension": ["延期", "延后", "推迟", "延到", "延至", "延到明天", "延到后天"],
        "view_progress": ["进度", "完成率", "情况", "状态", "怎么样", "如何"],
        "assign_task": ["指派", "分配", "给", "让", "@"],
        "help_setting": ["帮助", "说明", "指南", "设置", "配置", "怎么", "如何"]
    },
    "en": {
        "query_tasks": ["my tasks", "my list", "show tasks", "task list", "my work"],
        "mark_completed": ["done", "finished", "completed", "ok", "ready", "complete"],
        "request_extension": ["extend", "delay", "postpone", "extend to", "delay to"],
        "view_progress": ["progress", "status", "how", "situation", "completion rate"],
        "assign_task": ["assign", "give", "let", "@"],
        "help_setting": ["help", "guide", "manual", "setup", "configure", "how to"]
    },
    "es": {
        "query_tasks": ["mis tareas", "mi lista", "mostrar tareas", "lista de tareas"],
        "mark_completed": ["hecho", "terminado", "completado", "ok", "listo"],
        "request_extension": ["extender", "retrasar", "posponer", "extender a"],
        "view_progress": ["progreso", "estado", "cómo", "situación"],
        "assign_task": ["asignar", "dar", "dejar", "@"],
        "help_setting": ["ayuda", "guía", "manual", "configurar", "cómo"]
    }
}

# 时间解析模式
TIME_PATTERNS = {
    "zh": [
        r"明天\s*(\d{1,2}):(\d{2})",
        r"后天\s*(\d{1,2}):(\d{2})",
        r"(\d{1,2})月(\d{1,2})日\s*(\d{1,2}):(\d{2})",
        r"(\d{1,2}):(\d{2})",
        r"(\d{1,2})点(\d{2})分"
    ],
    "en": [
        r"tomorrow\s*(\d{1,2}):(\d{2})",
        r"(\d{1,2})/(\d{1,2})\s*(\d{1,2}):(\d{2})",
        r"(\d{1,2}):(\d{2})",
        r"(\d{1,2})am",
        r"(\d{1,2})pm"
    ],
    "es": [
        r"mañana\s*(\d{1,2}):(\d{2})",
        r"(\d{1,2})/(\d{1,2})\s*(\d{1,2}):(\d{2})",
        r"(\d{1,2}):(\d{2})"
    ]
}

class SmartInteractionEngine:
    """智能交互引擎"""
    
    def __init__(self):
        self.intent_threshold = 0.75
        self.languages = ["zh", "en", "es"]
        self.user_profiles = {}  # 用户画像
        self.interaction_history = {}  # 交互历史
    
    def analyze_intent(self, text: str, user_open_id: str, context: Dict = None) -> Dict[str, Any]:
        """分析用户意图"""
        text_lower = text.lower().strip()
        
        # 语言检测
        detected_lang = self._detect_language(text_lower)
        
        # 意图识别
        intent_result = self._identify_intent(text_lower, detected_lang)
        
        # 实体抽取
        entities = self._extract_entities(text_lower, detected_lang)
        
        # 权限验证
        permissions = self._check_permissions(user_open_id, intent_result["intent"])
        
        # 构建结果
        result = {
            "intent": intent_result["intent"],
            "confidence": intent_result["confidence"],
            "language": detected_lang,
            "entities": entities,
            "permissions": permissions,
            "suggestions": self._generate_suggestions(intent_result, detected_lang),
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # 更新用户画像
        self._update_user_profile(user_open_id, result, text)
        
        return result
    
    def _detect_language(self, text: str) -> str:
        """检测语言"""
        # 简单的语言检测逻辑
        if re.search(r'[a-zA-Z]', text):
            if re.search(r'[áéíóúñ]', text):
                return "es"
            else:
                return "en"
        else:
            return "zh"
    
    def _identify_intent(self, text: str, language: str) -> Dict[str, Any]:
        """识别意图"""
        max_confidence = 0.0
        best_intent = "unknown"
        
        # 遍历所有意图类型
        for intent_type, keywords in INTENT_KEYWORDS.get(language, {}).items():
            confidence = self._calculate_intent_confidence(text, keywords)
            if confidence > max_confidence:
                max_confidence = confidence
                best_intent = intent_type
        
        # 检查是否达到阈值
        if max_confidence < self.intent_threshold:
            return {
                "intent": "unknown",
                "confidence": max_confidence,
                "needs_clarification": True
            }
        
        return {
            "intent": best_intent,
            "confidence": max_confidence,
            "needs_clarification": False
        }
    
    def _calculate_intent_confidence(self, text: str, keywords: List[str]) -> float:
        """计算意图置信度"""
        if not keywords:
            return 0.0
        
        matches = 0
        for keyword in keywords:
            if keyword.lower() in text.lower():
                matches += 1
        
        return matches / len(keywords)
    
    def _extract_entities(self, text: str, language: str) -> Dict[str, Any]:
        """抽取实体"""
        entities = {
            "time": None,
            "person": None,
            "task_alias": None,
            "reason": None
        }
        
        # 时间实体抽取
        entities["time"] = self._extract_time(text, language)
        
        # 人名实体抽取（@符号）
        person_match = re.search(r'@([^\s]+)', text)
        if person_match:
            entities["person"] = person_match.group(1)
        
        # 任务别名抽取
        entities["task_alias"] = self._extract_task_alias(text)
        
        # 原因抽取
        entities["reason"] = self._extract_reason(text, language)
        
        return entities
    
    def _extract_time(self, text: str, language: str) -> Optional[str]:
        """抽取时间实体"""
        patterns = TIME_PATTERNS.get(language, [])
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                # 根据语言处理时间格式
                if language == "zh":
                    return self._parse_chinese_time(match, text)
                elif language == "en":
                    return self._parse_english_time(match, text)
                elif language == "es":
                    return self._parse_spanish_time(match, text)
        
        return None
    
    def _parse_chinese_time(self, match, text: str) -> str:
        """解析中文时间"""
        try:
            if "明天" in text:
                tomorrow = datetime.now() + timedelta(days=1)
                hour, minute = match.groups()
                return tomorrow.replace(hour=int(hour), minute=int(minute)).isoformat()
            elif "后天" in text:
                day_after = datetime.now() + timedelta(days=2)
                hour, minute = match.groups()
                return day_after.replace(hour=int(hour), minute=int(minute)).isoformat()
            else:
                # 其他时间格式
                return datetime.now().isoformat()
        except:
            return None
    
    def _parse_english_time(self, match, text: str) -> str:
        """解析英文时间"""
        try:
            if "tomorrow" in text:
                tomorrow = datetime.now() + timedelta(days=1)
                hour, minute = match.groups()
                return tomorrow.replace(hour=int(hour), minute=int(minute)).isoformat()
            else:
                return datetime.now().isoformat()
        except:
            return None
    
    def _parse_spanish_time(self, match, text: str) -> str:
        """解析西班牙语时间"""
        try:
            if "mañana" in text:
                tomorrow = datetime.now() + timedelta(days=1)
                hour, minute = match.groups()
                return tomorrow.replace(hour=int(hour), minute=int(minute)).isoformat()
            else:
                return datetime.now().isoformat()
        except:
            return None
    
    def _extract_task_alias(self, text: str) -> Optional[str]:
        """抽取任务别名"""
        # 简单的任务别名识别
        task_keywords = ["发电系统", "数据更新", "照片收集", "系统", "数据", "照片"]
        for keyword in task_keywords:
            if keyword in text:
                return keyword
        return None
    
    def _extract_reason(self, text: str, language: str) -> Optional[str]:
        """抽取原因"""
        reason_patterns = {
            "zh": [r"原因[：:]\s*(.+)", r"因为\s*(.+)", r"由于\s*(.+)"],
            "en": [r"reason[：:]\s*(.+)", r"because\s*(.+)", r"due to\s*(.+)"],
            "es": [r"razón[：:]\s*(.+)", r"porque\s*(.+)", r"debido a\s*(.+)"]
        }
        
        patterns = reason_patterns.get(language, [])
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _check_permissions(self, user_open_id: str, intent: str) -> Dict[str, bool]:
        """检查权限"""
        permissions = {
            "can_query_tasks": True,  # 所有用户都可以查询任务
            "can_mark_completed": True,  # 需要验证任务负责人/协作人
            "can_request_extension": True,  # 需要验证任务负责人
            "can_assign_task": False,  # 需要管理员权限
            "can_configure": False  # 需要管理员权限
        }
        
        # 这里应该根据实际的用户角色和任务分配关系进行验证
        # 暂时返回默认权限，实际使用时需要从数据库或配置中获取
        
        return permissions
    
    def _generate_suggestions(self, intent_result: Dict[str, Any], language: str) -> List[str]:
        """生成建议"""
        suggestions = []
        
        if intent_result["intent"] == "unknown":
            suggestions = self._get_unknown_intent_suggestions(language)
        elif intent_result["intent"] == "query_tasks":
            suggestions = self._get_query_suggestions(language)
        elif intent_result["intent"] == "mark_completed":
            suggestions = self._get_completion_suggestions(language)
        elif intent_result["intent"] == "request_extension":
            suggestions = self._get_extension_suggestions(language)
        
        return suggestions
    
    def _get_unknown_intent_suggestions(self, language: str) -> List[str]:
        """获取未知意图的建议"""
        suggestions_map = {
            "zh": [
                "您可以尝试：",
                "• 查看我的任务",
                "• 标记任务完成",
                "• 申请任务延期",
                "• 查看帮助"
            ],
            "en": [
                "You can try:",
                "• Show my tasks",
                "• Mark task as completed",
                "• Request extension",
                "• Show help"
            ],
            "es": [
                "Puedes intentar:",
                "• Mostrar mis tareas",
                "• Marcar tarea como completada",
                "• Solicitar extensión",
                "• Mostrar ayuda"
            ]
        }
        return suggestions_map.get(language, suggestions_map["zh"])
    
    def _get_query_suggestions(self, language: str) -> List[str]:
        """获取查询建议"""
        suggestions_map = {
            "zh": ["正在为您查询任务列表..."],
            "en": ["Querying your task list..."],
            "es": ["Consultando tu lista de tareas..."]
        }
        return suggestions_map.get(language, suggestions_map["zh"])
    
    def _get_completion_suggestions(self, language: str) -> List[str]:
        """获取完成建议"""
        suggestions_map = {
            "zh": ["正在标记任务为已完成..."],
            "en": ["Marking task as completed..."],
            "es": ["Marcando tarea como completada..."]
        }
        return suggestions_map.get(language, suggestions_map["zh"])
    
    def _get_extension_suggestions(self, language: str) -> List[str]:
        """获取延期建议"""
        suggestions_map = {
            "zh": ["正在处理延期申请..."],
            "en": ["Processing extension request..."],
            "es": ["Procesando solicitud de extensión..."]
        }
        return suggestions_map.get(language, suggestions_map["zh"])
    
    def _update_user_profile(self, user_open_id: str, intent_result: Dict[str, Any], text: str) -> None:
        """更新用户画像"""
        if user_open_id not in self.user_profiles:
            self.user_profiles[user_open_id] = {
                "first_interaction": datetime.now().isoformat(),
                "interaction_count": 0,
                "preferred_language": "zh",
                "common_intents": {},
                "last_interaction": None
            }
        
        profile = self.user_profiles[user_open_id]
        profile["interaction_count"] += 1
        profile["last_interaction"] = datetime.now().isoformat()
        profile["preferred_language"] = intent_result.get("language", "zh")
        
        # 更新常用意图
        intent = intent_result.get("intent", "unknown")
        if intent not in profile["common_intents"]:
            profile["common_intents"][intent] = 0
        profile["common_intents"][intent] += 1
    
    def get_user_profile(self, user_open_id: str) -> Dict[str, Any]:
        """获取用户画像"""
        return self.user_profiles.get(user_open_id, {})
    
    def should_use_card_fallback(self, confidence: float) -> bool:
        """判断是否应该使用卡片回退"""
        return confidence < self.intent_threshold
    
    def generate_fallback_card(self, intent_result: Dict[str, Any], language: str) -> Dict[str, Any]:
        """生成回退卡片"""
        # 根据意图生成候选选项卡片
        candidates = self._get_intent_candidates(intent_result, language)
        
        return {
            "header": {
                "title": self._get_fallback_title(language),
                "template": "orange"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": self._get_fallback_content(language),
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "action_group",
                    "actions": candidates
                }
            ]
        }
    
    def _get_fallback_title(self, language: str) -> str:
        """获取回退卡片标题"""
        titles = {
            "zh": "请选择您要执行的操作",
            "en": "Please select the action you want to perform",
            "es": "Por favor selecciona la acción que quieres realizar"
        }
        return titles.get(language, titles["zh"])
    
    def _get_fallback_content(self, language: str) -> str:
        """获取回退卡片内容"""
        contents = {
            "zh": "我无法准确理解您的意图，请选择以下操作之一：",
            "en": "I cannot accurately understand your intent, please select one of the following actions:",
            "es": "No puedo entender exactamente tu intención, por favor selecciona una de las siguientes acciones:"
        }
        return contents.get(language, contents["zh"])
    
    def _get_intent_candidates(self, intent_result: Dict[str, Any], language: str) -> List[Dict[str, Any]]:
        """获取意图候选选项"""
        candidates = []
        
        # 根据当前意图和置信度生成候选选项
        if intent_result.get("confidence", 0) < 0.5:
            # 低置信度，提供多个选项
            options = [
                ("query_tasks", "查看我的任务", "View my tasks", "Ver mis tareas"),
                ("mark_completed", "标记完成", "Mark as completed", "Marcar como completado"),
                ("request_extension", "申请延期", "Request extension", "Solicitar extensión"),
                ("help_setting", "查看帮助", "Show help", "Mostrar ayuda")
            ]
            
            for intent, zh_text, en_text, es_text in options:
                text_map = {"zh": zh_text, "en": en_text, "es": es_text}
                candidates.append({
                    "tag": "button",
                    "text": text_map.get(language, zh_text),
                    "type": "default",
                    "value": {"action": intent}
                })
        else:
            # 中等置信度，提供确认选项
            candidates.append({
                "tag": "button",
                "text": "确认",
                "type": "primary",
                "value": {"action": intent_result.get("intent", "unknown")}
            })
            candidates.append({
                "tag": "button",
                "text": "重新选择",
                "type": "default",
                "value": {"action": "show_options"}
            })
        
        return candidates

