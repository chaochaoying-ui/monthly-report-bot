@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo HTTP回调服务器 - 新成员欢迎功能
echo ========================================

REM 设置环境变量
set APP_ID=cli_a8fd44a9453cd00c
set APP_SECRET=jsVoFWgaaw05en6418h7xbhV5oXxAwIm
set WELCOME_CARD_ID=AAqInYqWzIiu6
set VERIFICATION_TOKEN=your_verification_token_here

REM 切换到项目目录
cd /d "C:\Users\Administrator\Desktop\monthly_report_bot_link_pack"

echo 当前目录: %CD%
echo 环境变量已设置
echo.

echo HTTP回调服务器功能:
echo - 监听端口: 8080
echo - 处理新成员加入事件
echo - 自动发送欢迎卡片
echo - 支持用户和机器人加入
echo.

echo 启动HTTP回调服务器...
python simple_http_callback.py

pause
endlocal

