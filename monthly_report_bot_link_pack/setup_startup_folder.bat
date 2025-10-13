@echo off
echo 正在设置月报机器人开机自启动（启动文件夹方式）...

REM 获取当前脚本目录和启动脚本路径
set SCRIPT_DIR=%~dp0
set STARTUP_SCRIPT=%SCRIPT_DIR%start_bot.bat
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set STARTUP_LINK=%STARTUP_FOLDER%\月报机器人启动.bat

echo 脚本目录: %SCRIPT_DIR%
echo 启动脚本: %STARTUP_SCRIPT%
echo 启动文件夹: %STARTUP_FOLDER%

REM 检查启动脚本是否存在
if not exist "%STARTUP_SCRIPT%" (
    echo 错误：启动脚本不存在: %STARTUP_SCRIPT%
    pause
    exit /b 1
)

REM 创建启动文件夹的快捷方式
echo 正在创建启动快捷方式...
copy "%STARTUP_SCRIPT%" "%STARTUP_LINK%"

if %errorLevel% == 0 (
    echo.
    echo ✅ 开机自启动设置成功！
    echo 启动方式: Windows启动文件夹
    echo 快捷方式: %STARTUP_LINK%
    echo.
    echo 管理方法：
    echo 1. 按 Win+R，输入 shell:startup
    echo 2. 可以找到"月报机器人启动.bat"文件
    echo 3. 删除该文件即可取消开机自启动
    echo.
    echo 测试方法：
    echo 1. 重启计算机
    echo 2. 登录后检查任务管理器中的python.exe进程
) else (
    echo ❌ 开机自启动设置失败！
)

echo.
echo 当前启动文件夹内容：
dir "%STARTUP_FOLDER%" /b

pause

