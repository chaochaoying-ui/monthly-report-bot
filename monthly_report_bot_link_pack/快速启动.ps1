# 月报机器人快速启动脚本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "月报机器人 v1.3.1 快速启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 设置环境变量
$env:APP_ID = "cli_a8fd44a9453cd00c"
$env:APP_SECRET = "jsVoFWgaaw05en6418h7xbhV5oXxAwIm"
$env:CHAT_ID = "oc_e4218b232326ea81a077b65c4cd16ce5"
$env:FILE_URL = "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
$env:TZ = "Asia/Shanghai"
$env:WELCOME_CARD_ID = "AAqInYqWzIiu6"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "环境变量已设置" -ForegroundColor Green
Write-Host "APP_ID: $env:APP_ID" -ForegroundColor Yellow
Write-Host "CHAT_ID: $env:CHAT_ID" -ForegroundColor Yellow
Write-Host ""

Write-Host "正在启动机器人..." -ForegroundColor Green
Write-Host "按 Ctrl+C 停止机器人" -ForegroundColor Yellow
Write-Host ""

# 启动机器人
python monthly_report_bot_final_interactive.py







