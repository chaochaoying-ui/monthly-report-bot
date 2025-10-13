#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将月报机器人安装为Windows服务
"""

import os
import sys
import winreg
import subprocess
from pathlib import Path

def install_as_windows_service():
    """安装为Windows服务"""
    
    # 获取当前目录
    current_dir = Path(__file__).parent.absolute()
    python_exe = sys.executable
    bot_script = current_dir / "monthly_report_bot_official.py"
    
    # 创建服务安装脚本
    install_script = f"""
@echo off
echo 正在安装月报机器人Windows服务...

REM 使用nssm安装服务
nssm install MonthlyReportBot "{python_exe}" "{bot_script}"
nssm set MonthlyReportBot AppDirectory "{current_dir}"
nssm set MonthlyReportBot Description "月报机器人 - 基于飞书官方文档标准版本"
nssm set MonthlyReportBot Start SERVICE_AUTO_START

echo 服务安装完成！
echo 启动服务: net start MonthlyReportBot
echo 停止服务: net stop MonthlyReportBot
echo 删除服务: nssm remove MonthlyReportBot confirm
pause
"""
    
    # 写入安装脚本
    with open("install_service.bat", "w", encoding="utf-8") as f:
        f.write(install_script)
    
    print("✅ 服务安装脚本已创建: install_service.bat")
    print("📋 使用步骤:")
    print("1. 下载 nssm: https://nssm.cc/download")
    print("2. 将 nssm.exe 放到当前目录")
    print("3. 运行 install_service.bat")
    print("4. 启动服务: net start MonthlyReportBot")

def create_startup_script():
    """创建开机启动脚本"""
    
    # 获取当前目录
    current_dir = Path(__file__).parent.absolute()
    python_exe = sys.executable
    bot_script = current_dir / "monthly_report_bot_official.py"
    
    # 创建启动脚本
    startup_script = f"""@echo off
cd /d "{current_dir}"
echo 启动月报机器人...
"{python_exe}" "{bot_script}"
"""
    
    # 写入启动脚本
    with open("start_bot_auto.bat", "w", encoding="utf-8") as f:
        f.write(startup_script)
    
    print("✅ 自动启动脚本已创建: start_bot_auto.bat")

def add_to_startup():
    """添加到Windows开机启动"""
    
    try:
        # 获取启动脚本路径
        startup_script = Path(__file__).parent / "start_bot_auto.bat"
        
        # 添加到注册表启动项
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(
            key,
            "MonthlyReportBot",
            0,
            winreg.REG_SZ,
            str(startup_script)
        )
        
        winreg.CloseKey(key)
        print("✅ 已添加到Windows开机启动")
        
    except Exception as e:
        print(f"❌ 添加到开机启动失败: {e}")
        print("请手动将 start_bot_auto.bat 添加到开机启动项")

def create_systemd_service():
    """创建Linux systemd服务文件"""
    
    current_dir = Path(__file__).parent.absolute()
    python_exe = sys.executable
    bot_script = current_dir / "monthly_report_bot_official.py"
    
    service_content = f"""[Unit]
Description=Monthly Report Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={current_dir}
ExecStart={python_exe} {bot_script}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    with open("monthly-report-bot.service", "w", encoding="utf-8") as f:
        f.write(service_content)
    
    print("✅ Linux systemd服务文件已创建: monthly-report-bot.service")
    print("📋 Linux安装步骤:")
    print("1. sudo cp monthly-report-bot.service /etc/systemd/system/")
    print("2. sudo systemctl daemon-reload")
    print("3. sudo systemctl enable monthly-report-bot")
    print("4. sudo systemctl start monthly-report-bot")

def main():
    """主函数"""
    print("="*60)
    print("月报机器人自动运行配置工具")
    print("="*60)
    
    print("\n请选择部署方式:")
    print("1. Windows服务 (推荐)")
    print("2. Windows开机启动")
    print("3. Linux systemd服务")
    print("4. 全部创建")
    
    choice = input("\n请输入选择 (1-4): ").strip()
    
    if choice == "1":
        install_as_windows_service()
    elif choice == "2":
        create_startup_script()
        add_to_startup()
    elif choice == "3":
        create_systemd_service()
    elif choice == "4":
        install_as_windows_service()
        create_startup_script()
        add_to_startup()
        create_systemd_service()
    else:
        print("❌ 无效选择")
        return
    
    print("\n" + "="*60)
    print("配置完成！")
    print("现在月报机器人可以自动运行了！")
    print("="*60)

if __name__ == "__main__":
    main()
