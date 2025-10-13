@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo Monthly Report Bot v1.1 - WS Version
echo ========================================

REM Set environment variables (as per requirements doc 8.1)
set APP_ID=cli_a8fd44a9453cd00c
set APP_SECRET=jsVoFWgaaw05en6418h7xbhV5oXxAwIm
set CHAT_ID=oc_07f2d3d314f00fc29baf323a3a589972
set FILE_URL=https://be9bhmcgo2.feishu.cn/file/Wn5AbQAmVo32OExC5zIcIiAXnKc?office_edit=1
set TZ=America/Argentina/Buenos_Aires
set VERIFICATION_TOKEN=your_verification_token_here

REM WebSocket configuration
set WS_ENDPOINT=wss://open.feishu.cn/ws/v2
set WS_HEARTBEAT_INTERVAL=30
set WS_RECONNECT_MAX_ATTEMPTS=5

REM Welcome card configuration
set WELCOME_CARD_ID=AAqInYqWzIiu6

REM Smart interaction configuration
set ENABLE_NLU=true
set INTENT_THRESHOLD=0.75
set LANGS=["zh","en","es"]

REM Logging and monitoring
set LOG_LEVEL=INFO
set METRICS_ENDPOINT=http://localhost:9090/metrics

REM Switch to project directory
cd /d "C:\Users\Administrator\Desktop\monthly_report_bot_link_pack"

echo Current directory: %CD%
echo Environment variables set
echo.

echo Monthly Report Bot v1.1 Features:
echo - WebSocket long connection callback (WS only)
echo - Smart interaction engine (multi-language)
echo - Group-level configuration management
echo - Idempotency and catch-up mechanism
echo - Professional card design
echo - New member welcome cards
echo.

echo Please select running mode:
echo 1. Full Mode (Main Program + WebSocket Service)
echo 2. Main Program Only (Scheduled Tasks)
echo 3. WebSocket Service Only (Event Handling)
echo 4. Test Mode
echo.

set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" goto run_full_mode
if "%choice%"=="2" goto run_main_only
if "%choice%"=="3" goto run_websocket_only
if "%choice%"=="4" goto run_test_mode
goto invalid_choice

:run_full_mode
echo.
echo Starting Full Mode...
echo Includes: Scheduled tasks + WebSocket long connection + Smart interaction
python monthly_report_bot_ws_v1.1.py
goto end

:run_main_only
echo.
echo Starting Main Program...
echo Features: Task creation, card push, final reminders
python monthly_report_bot_ws_v1.1.py --main-only
goto end

:run_websocket_only
echo.
echo Starting WebSocket Service...
echo Features: Event handling, smart interaction, card callbacks
python monthly_report_bot_ws_v1.1.py --websocket-only
goto end

:run_test_mode
echo.
echo Starting Test Mode...
echo Features: Verify configuration, test connections, simulate events
python test_bot_v1_1.py
goto end

:invalid_choice
echo Invalid choice, please run the script again
goto end

:end
echo.
echo Script execution completed
pause
endlocal
