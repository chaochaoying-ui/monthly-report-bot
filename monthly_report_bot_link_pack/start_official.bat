@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 月报机器人 v1.1 - 基于飞书官方文档标准版本
echo ========================================

REM 设置环境变量
set APP_ID=cli_a8fd44a9453cd00c
set APP_SECRET=jsVoFWgaaw05en6418h7xbhV5oXxAwIm
set CHAT_ID=oc_07f2d3d314f00fc29baf323a3a589972
set FILE_URL=https://be9bhmcgo2.feishu.cn/file/Wn5AbQAmVo32OExC5zIcIiAXnKc?office_edit=1
set WELCOME_CARD_ID=AAqInYqWzIiu6
set VERIFICATION_TOKEN=test_token
set TZ=America/Argentina/Buenos_Aires

REM 切换到项目目录
cd /d "C:\Users\Administrator\Desktop\monthly_report_bot_link_pack"

echo 当前目录: %CD%
echo 环境变量已设置
echo.

echo 基于飞书官方文档标准版本功能:
echo - 严格按照飞书官方文档实现
echo - 使用lark-oapi官方SDK
echo - 定时任务管理（月报任务创建和提醒）
echo - 新成员欢迎卡片（模拟事件处理）
echo - 模板卡片发送
echo - 自动重连和错误处理
echo - 更稳定的API调用
echo.

echo 启动基于飞书官方文档标准版本...
python monthly_report_bot_official.py

pause
endlocal

