@echo off
chcp 65001 >nul
echo ============================================================
echo 启动月报机器人最终版
echo ============================================================
echo 核心功能：
echo - 17日创建任务@负责人
echo - 每日统计@未完成负责人
echo - 23日催办@未完成负责人
echo - 发送最终统计结果
echo.
echo 任务配置：24个具体任务，每个都有明确负责人
echo 群聊ID：oc_07f2d3d314f00fc29baf323a3a589972
echo.

cd /d "C:\Users\Administrator\Desktop\monthly_report_bot_link_pack"
echo 当前目录: %CD%
echo 启动最终版程序...
python monthly_report_bot_final.py
pause
