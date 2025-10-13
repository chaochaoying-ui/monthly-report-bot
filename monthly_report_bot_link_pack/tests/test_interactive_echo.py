#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试：monthly_report_bot_final_interactive.generate_echo_reply
"""

import os
import sys

# 确保可以从项目根目录导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monthly_report_bot_final_interactive import generate_echo_reply


def test_interactive_echo__help_text():
    text = generate_echo_reply("帮助")
    assert "月报机器人帮助" in text
    assert "状态" in text
    assert "已完成" in text

def test_interactive_echo__help_text_with_plain_mention():
    # 纯文本@提及
    text = generate_echo_reply("@_user_1 帮助")
    assert "月报机器人帮助" in text
    assert "状态" in text
    assert "已完成" in text

def test_interactive_echo__help_text_with_rich_mention():
    # 富文本@提及
    rt = '<at user_id="ou_xxx">周超</at> 帮助'
    text = generate_echo_reply(rt)
    assert "月报机器人帮助" in text
    assert "状态" in text
    assert "已完成" in text

def test_interactive_echo__status_and_lists():
    # 状态/进度
    t1 = generate_echo_reply("状态")
    assert "当前进度" in t1 or "完成率" in t1
    # 未完成列表
    t2 = generate_echo_reply("未完成")
    assert ("未完成任务" in t2) or ("没有未完成" in t2) or ("当前没有未完成" in t2)

def test_interactive_echo__file_and_time():
    # 文件链接
    t3 = generate_echo_reply("文件")
    assert "链接" in t3
    # 时间安排
    t4 = generate_echo_reply("时间")
    assert "时间安排" in t4 or "提醒" in t4

def test_interactive_echo__done_hint():
    t5 = generate_echo_reply("已完成")
    assert "标记完成" in t5 or "同步" in t5


def test_interactive_echo__echo_roundtrip():
    msg = "hello world"
    text = generate_echo_reply(msg)
    assert text == f"Echo: {msg}"


if __name__ == "__main__":
    # 冒烟运行，避免依赖 pytest
    t = generate_echo_reply("帮助")
    assert "月报机器人帮助" in t and "状态" in t and "已完成" in t
    e = generate_echo_reply("hello world")
    assert e == "Echo: hello world"
    print("ECHO_SMOKE_OK")


