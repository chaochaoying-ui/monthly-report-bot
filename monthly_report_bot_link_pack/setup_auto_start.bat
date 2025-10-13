@echo off
echo 正在设置月报机器人开机自启动...

REM 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 检测到管理员权限，继续设置...
) else (
    echo 错误：需要管理员权限来设置开机自启动
    echo 请右键点击此文件，选择"以管理员身份运行"
    pause
    exit /b 1
)

REM 获取当前脚本目录
set SCRIPT_DIR=%~dp0
set STARTUP_SCRIPT=%SCRIPT_DIR%start_bot.bat

echo 脚本目录: %SCRIPT_DIR%
echo 启动脚本: %STARTUP_SCRIPT%

REM 创建任务计划程序任务
schtasks /create /tn "月报机器人自启动" /tr "\"%STARTUP_SCRIPT%\"" /sc onlogon /ru "SYSTEM" /f

if %errorLevel% == 0 (
    echo.
    echo ✅ 开机自启动设置成功！
    echo 任务名称: 月报机器人自启动
    echo 启动方式: 系统登录时自动启动
    echo.
    echo 管理命令：
    echo 查看任务: schtasks /query /tn "月报机器人自启动"
    echo 删除任务: schtasks /delete /tn "月报机器人自启动" /f
    echo 立即运行: schtasks /run /tn "月报机器人自启动"
) else (
    echo ❌ 开机自启动设置失败！
    echo 请检查权限或手动设置
)

echo.
echo 手动设置方法：
echo 1. 按 Win+R，输入 taskschd.msc
echo 2. 创建基本任务
echo 3. 触发器：计算机启动时
echo 4. 操作：启动程序 "%STARTUP_SCRIPT%"

pause

