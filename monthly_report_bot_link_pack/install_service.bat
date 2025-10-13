@echo off
echo 正在安装月报机器人为Windows服务...

REM 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 检测到管理员权限，继续安装...
) else (
    echo 错误：需要管理员权限来安装Windows服务
    echo 请右键点击此文件，选择"以管理员身份运行"
    pause
    exit /b 1
)

REM 设置服务参数
set SERVICE_NAME=MonthlyReportBot
set SERVICE_DISPLAY_NAME=月报机器人服务
set SERVICE_DESCRIPTION=月报收集系统机器人服务
set PYTHON_PATH=python
set SCRIPT_PATH=%~dp0monthly_report_bot_final_interactive.py

REM 创建服务
sc create %SERVICE_NAME% binPath= "%PYTHON_PATH% -X utf8 \"%SCRIPT_PATH%\"" DisplayName= "%SERVICE_DISPLAY_NAME%" start= auto

if %errorLevel% == 0 (
    echo 服务创建成功！
    
    REM 设置服务描述
    sc description %SERVICE_NAME% "%SERVICE_DESCRIPTION%"
    
    REM 启动服务
    echo 正在启动服务...
    sc start %SERVICE_NAME%
    
    if %errorLevel% == 0 (
        echo 服务启动成功！
        echo 月报机器人已设置为开机自启动
    ) else (
        echo 服务启动失败，请检查日志
    )
) else (
    echo 服务创建失败！
)

echo.
echo 服务管理命令：
echo 启动服务: sc start %SERVICE_NAME%
echo 停止服务: sc stop %SERVICE_NAME%
echo 删除服务: sc delete %SERVICE_NAME%
echo 查看状态: sc query %SERVICE_NAME%

pause

