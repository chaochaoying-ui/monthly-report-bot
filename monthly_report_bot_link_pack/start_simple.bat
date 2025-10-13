@echo off
chcp 65001 >nul
echo ============================================================
echo 启动月报机器人简化版
echo ============================================================
echo 包含功能：
echo - 定时任务发送（F1-F4）
echo - 任务配置管理（24个任务）
echo - 自动运行和错误恢复
echo - 不依赖WebSocket，稳定可靠
echo.

cd /d "C:\Users\Administrator\Desktop\monthly_report_bot_link_pack"
echo 当前目录: %CD%
echo 启动简化版程序...
python monthly_report_bot_simple.py
pause
