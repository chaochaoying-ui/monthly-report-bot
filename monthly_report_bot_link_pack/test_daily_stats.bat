@echo off
chcp 65001 >nul
echo ========================================
echo 测试每日统计功能（17:30定时任务）
echo ========================================
echo.

cd /d "%~dp0"

if not exist "venv\" (
    echo 错误: 找不到虚拟环境
    echo 请先运行 install_environment.ps1 安装环境
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo 当前Python版本:
python --version
echo.

echo 开始测试...
echo.

python test_daily_stats.py

echo.
echo ========================================
echo 测试完成
echo ========================================
pause

