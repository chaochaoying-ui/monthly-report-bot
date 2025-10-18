#!/bin/bash

# Service Diagnostic Script
# 诊断服务启动问题

echo "=========================================="
echo "月报机器人服务诊断工具"
echo "=========================================="

# 检查服务状态
echo -e "\n【1. 服务状态】"
sudo systemctl status monthly-report-bot --no-pager -l

# 查看最近的错误日志
echo -e "\n【2. 最近 50 条日志】"
sudo journalctl -u monthly-report-bot -n 50 --no-pager

# 检查服务配置文件
echo -e "\n【3. 服务配置文件】"
cat /etc/systemd/system/monthly-report-bot.service

# 检查项目目录结构
echo -e "\n【4. 项目目录结构】"
ls -la ~/monthly-report-bot/monthly_report_bot_link_pack/*.py

# 检查虚拟环境
echo -e "\n【5. 虚拟环境】"
ls -la ~/monthly-report-bot/monthly_report_bot_link_pack/venv/bin/python*

# 检查 .env 文件
echo -e "\n【6. .env 文件是否存在】"
ls -la ~/monthly-report-bot/monthly_report_bot_link_pack/.env

# 测试 Python 脚本是否可以运行（不实际启动机器人）
echo -e "\n【7. Python 脚本语法检查】"
~/monthly-report-bot/monthly_report_bot_link_pack/venv/bin/python3 -m py_compile ~/monthly-report-bot/monthly_report_bot_link_pack/monthly_report_bot_final_interactive.py 2>&1

echo -e "\n=========================================="
echo "诊断完成"
echo "=========================================="

