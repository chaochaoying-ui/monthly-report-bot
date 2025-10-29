@echo off
chcp 65001 >nul
echo ========================================
echo 部署带调试输出的字体配置修复
echo ========================================
echo.

echo [1/5] 添加修改到 Git...
git add monthly_report_bot_link_pack/chart_generator.py
git add monthly_report_bot_link_pack/debug_font_setup.py

echo.
echo [2/5] 提交更改...
git commit -m "debug: add print statements to trace font setup execution

添加 print() 调试语句来追踪字体配置执行流程：

1. 在 setup_chinese_fonts() 入口添加 DEBUG 输出
2. 在 Symbola 字体加载处添加详细日志
3. 在字体列表配置完成后输出最终配置
4. 在异常处理中添加 traceback 输出

这些 print 语句会直接输出到 systemd 日志，
不受 logger 配置影响，帮助我们确认：
- 函数是否被调用
- 在哪个分支执行
- 字体是否成功加载
- 最终配置的字体列表

同时添加 debug_font_setup.py 独立测试脚本。

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo.
echo [3/5] 推送到 GitHub...
git push

echo.
echo [4/5] 连接服务器并部署...
ssh hdi918072@34.145.43.77 "cd /home/hdi918072/monthly-report-bot/monthly_report_bot_link_pack && git pull && sudo systemctl restart monthly-report-bot"

echo.
echo [5/5] 查看实时日志（按 Ctrl+C 退出）...
echo.
echo 请在飞书中触发一个图表生成，查看 DEBUG 输出
echo.
ssh hdi918072@34.145.43.77 "sudo journalctl -u monthly-report-bot -f"
