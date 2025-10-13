@echo off
chcp 65001 >nul
echo ========================================
echo 月报机器人 v1.3.1 交互增强版
echo ========================================
echo.

REM 设置环境变量
echo [1/2] 设置环境变量...
set "APP_ID=cli_a8fd44a9453cd00c"
set "APP_SECRET=jsVoFWgaaw05en6418h7xbhV5oXxAwIm"
set "CHAT_ID=oc_e4218b232326ea81a077b65c4cd16ce5"
set "WELCOME_CARD_ID=AAqInYqWzIiu6"
set "FILE_URL=https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
set "TZ=Asia/Shanghai"
set "PYTHONIOENCODING=utf-8"

echo   [OK] 环境变量设置完成
echo   APP_ID: %APP_ID%
echo   CHAT_ID: %CHAT_ID%
echo.

REM 启动机器人
echo [2/2] 启动机器人...
echo.
echo ========================================
echo 机器人正在运行...
echo 按 Ctrl+C 可停止机器人
echo ========================================
echo.

C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe monthly_report_bot_final_interactive.py

REM 如果程序异常退出
echo.
echo ========================================
echo 机器人已停止
echo ========================================
echo.
pause

