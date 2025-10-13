@echo off
chcp 65001 >nul
echo ============================================================
echo 启动月报机器人完整功能版本...
echo ============================================================
echo 包含功能：
echo - 定时任务发送
echo - 任务完成统计
echo - 文本交互功能
echo - 智能意图识别
echo - 多语言支持
echo.

cd /d "C:\Users\Administrator\Desktop\monthly_report_bot_link_pack"
echo 当前目录: %CD%
echo 启动程序...
python monthly_report_bot_official.py
pause
