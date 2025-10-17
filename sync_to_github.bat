@echo off
chcp 65001 >nul
echo ============================================================
echo 开始同步代码到GitHub
echo ============================================================

echo.
echo 1. 添加所有更改...
git add .
if %errorlevel% neq 0 (
    echo 添加文件失败
    pause
    exit /b 1
)

echo.
echo 2. 查看Git状态...
git status

echo.
echo 3. 提交更改...
git commit -m "Add daily statistics feature with charts - Add should_send_daily_stats() for 17:30 daily trigger - Add upload_image() to upload charts to Feishu - Add build_daily_stats_card_with_chart() for chart display - Integrate daily stats into main loop - Add test scripts and documentation - Update workflow configuration - Generate comprehensive dashboard with charts"

echo.
echo 4. 推送到GitHub...
git push
if %errorlevel% neq 0 (
    echo 推送失败
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 代码已成功同步到GitHub!
echo ============================================================
echo.
echo 访问: https://github.com/chaochaoying-ui/monthly-report-bot
pause


