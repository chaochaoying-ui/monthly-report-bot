#!/usr/bin/env python3
"""
同步代码到GitHub的脚本
"""
import subprocess
import sys

def run_command(cmd):
    """执行命令并打印输出"""
    print(f"\n执行: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if result.stdout:
            print(result.stdout.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
        if result.stderr:
            print(result.stderr.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
        return result.returncode
    except Exception as e:
        print(f"命令执行错误: {e}")
        return 1

def main():
    """主函数"""
    print("=" * 60)
    print("开始同步代码到GitHub")
    print("=" * 60)

    # 1. 添加所有更改
    print("\n1. 添加所有更改...")
    if run_command("git add .") != 0:
        print("❌ 添加文件失败")
        return False

    # 2. 查看状态
    print("\n2. 查看Git状态...")
    run_command("git status")

    # 3. 提交更改
    print("\n3. 提交更改...")
    commit_message = """Add daily statistics feature with charts

- Add should_send_daily_stats() for 17:30 daily trigger
- Add upload_image() to upload charts to Feishu
- Add build_daily_stats_card_with_chart() for chart display
- Integrate daily stats into main loop
- Add test scripts: test_daily_stats.py, create_test_tasks.py
- Add documentation: DAILY_STATS_FEATURE.md, IMPLEMENTATION_SUMMARY.md
- Update workflow configuration for automatic scheduling
- Generate comprehensive dashboard with charts
- Smart assessment based on completion rate"""

    if run_command(f'git commit -m "{commit_message}"') != 0:
        print("⚠️ 提交失败（可能没有更改）")

    # 4. 推送到GitHub
    print("\n4. 推送到GitHub...")
    if run_command("git push") != 0:
        print("❌ 推送失败")
        return False

    print("\n" + "=" * 60)
    print("✅ 代码已成功同步到GitHub！")
    print("=" * 60)
    print("\n访问: https://github.com/chaochaoying-ui/monthly-report-bot")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

