@echo off
chcp 65001 >nul
echo ========================================
echo 同步任务数据到服务器
echo ========================================
echo.

echo [1/2] 上传 task_stats.json 到服务器...
scp monthly_report_bot_link_pack/task_stats.json hdi918072@34.145.43.77:/home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack/

echo.
echo [2/2] 重启服务...
ssh hdi918072@34.145.43.77 "sudo systemctl restart monthly-report-bot"

echo.
echo ========================================
echo ✅ 任务数据已同步！
echo ========================================
echo.
echo 现在可以在飞书中发送 "进度图表" 或 "综合图表" 测试 emoji 显示
echo.
