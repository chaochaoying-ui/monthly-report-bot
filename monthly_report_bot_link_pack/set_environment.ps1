# PowerShell环境变量设置脚本
$env:APP_ID = "cli_a8fd44a9453cd00c"
$env:APP_SECRET = "jsVoFWgaaw05en6418h7xbhV5oXxAwIm"
$env:CHAT_ID = "oc_e4218b232326ea81a077b65c4cd16ce5"
$env:WELCOME_CARD_ID = "AAqInYqWzIiu6"
$env:FILE_URL = "https://be9bhmcgo2.feishu.cn/drive/folder/OJP5fbjlSlwrf6dTF5acnRw3nzd"
$env:VERIFICATION_TOKEN = "v_01J6RE0Q4VEcCQ0hFg1RbdLT"
$env:TZ = "Asia/Shanghai"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "环境变量设置完成！" -ForegroundColor Green
Write-Host "CHAT_ID: $env:CHAT_ID" -ForegroundColor Yellow

