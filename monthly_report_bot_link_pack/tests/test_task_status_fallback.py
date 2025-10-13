#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务状态检查回退逻辑测试：
1) 本地模拟任务ID（task_YYYY-MM_N）直接走本地回退
2) 远端返回 1470400 时降级为本地状态
"""

import os
import sys
import asyncio
import types

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

import monthly_report_bot_final as bot


@pytest.mark.asyncio
async def test_task_status_fallback__mock_id_uses_local_state(tmp_path, monkeypatch):
    """task_YYYY-MM_N 模拟ID应直接使用本地状态"""
    # 使用临时目录存放状态文件，避免污染
    monkeypatch.chdir(tmp_path)

    task_id = "task_2025-08_1"
    title = "示例任务"
    assignees = ["ou_mock_user_1"]

    # 初始标记为未完成
    bot.update_task_completion(task_id, title, assignees, completed=False)
    result1 = await bot.check_task_status_from_feishu(task_id)
    assert result1 is False

    # 更新为已完成，应读取到 True
    bot.update_task_completion(task_id, title, assignees, completed=True)
    result2 = await bot.check_task_status_from_feishu(task_id)
    assert result2 is True


class _StubResponse:
    def __init__(self, code: int):
        self.code = code

    def success(self) -> bool:
        return False


class _StubTaskAPI:
    async def aget(self, request):
        return _StubResponse(1470400)


class _StubTaskV2:
    def __init__(self):
        self.task = _StubTaskAPI()


class _StubTask:
    def __init__(self):
        self.v2 = _StubTaskV2()


class _StubClient:
    def __init__(self):
        self.task = _StubTask()


@pytest.mark.asyncio
async def test_task_status_fallback__1470400_uses_local_state(tmp_path, monkeypatch):
    """当远端返回 1470400 时，应降级使用本地状态"""
    # 使用临时目录存放状态文件，避免污染
    monkeypatch.chdir(tmp_path)

    # 构造一个非模拟的任务ID（不匹配 task_YYYY-MM_N），以走远端分支
    real_like_task_id = "real_guid_abc123"
    title = "真实任务占位"
    assignees = []

    # 本地设置为未完成
    bot.update_task_completion(real_like_task_id, title, assignees, completed=False)

    # 注入桩客户端，模拟远端返回 1470400
    bot.lark_client = _StubClient()

    res1 = await bot.check_task_status_from_feishu(real_like_task_id)
    assert res1 is False

    # 切换本地状态为已完成，再次调用应读到 True
    bot.update_task_completion(real_like_task_id, title, assignees, completed=True)
    res2 = await bot.check_task_status_from_feishu(real_like_task_id)
    assert res2 is True










