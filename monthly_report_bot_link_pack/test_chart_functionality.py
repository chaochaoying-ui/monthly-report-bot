#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表功能测试脚本
测试月报机器人的图表生成功能
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
import tempfile

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_test_environment():
    """设置测试环境"""
    # 设置必要的环境变量
    os.environ['TZ'] = 'Asia/Shanghai'
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # 确保项目根目录在 Python 路径中
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

def create_test_task_stats():
    """创建测试任务统计数据"""
    current_month = datetime.now().strftime("%Y-%m")
    
    # 创建测试任务数据
    test_stats = {
        "current_month": current_month,
        "total_tasks": 10,
        "completed_tasks": 7,
        "completion_rate": 70.0,
        "tasks": {
            "task_001": {
                "title": "测试任务1",
                "assignees": ["user_001", "user_002"],
                "completed": True,
                "completed_at": datetime.now().isoformat()
            },
            "task_002": {
                "title": "测试任务2",
                "assignees": ["user_003"],
                "completed": True,
                "completed_at": datetime.now().isoformat()
            },
            "task_003": {
                "title": "测试任务3",
                "assignees": ["user_001", "user_004"],
                "completed": False,
                "completed_at": None
            },
            "task_004": {
                "title": "测试任务4",
                "assignees": ["user_005"],
                "completed": True,
                "completed_at": datetime.now().isoformat()
            },
            "task_005": {
                "title": "测试任务5",
                "assignees": ["user_002", "user_006"],
                "completed": False,
                "completed_at": None
            }
        },
        "last_update": datetime.now().isoformat()
    }
    
    # 保存测试数据到文件
    test_stats_file = "test_task_stats.json"
    with open(test_stats_file, 'w', encoding='utf-8') as f:
        json.dump(test_stats, f, ensure_ascii=False, indent=2)
    
    logger.info(f"测试任务统计数据已创建: {test_stats_file}")
    return test_stats

def test_chart_generator():
    """测试图表生成器"""
    try:
        from chart_generator import ChartGenerator
        
        logger.info("开始测试图表生成器...")
        
        # 创建图表生成器实例
        chart_gen = ChartGenerator()
        
        # 创建测试数据
        test_stats = create_test_task_stats()
        
        # 测试任务完成情况饼状图
        logger.info("测试任务完成情况饼状图...")
        pie_chart_path = chart_gen.generate_task_completion_pie_chart(test_stats)
        if pie_chart_path and os.path.exists(pie_chart_path):
            logger.info(f"✅ 任务完成情况饼状图生成成功: {pie_chart_path}")
        else:
            logger.error("❌ 任务完成情况饼状图生成失败")
        
        # 测试用户参与度图表
        logger.info("测试用户参与度图表...")
        user_chart_path = chart_gen.generate_user_participation_chart(test_stats)
        if user_chart_path and os.path.exists(user_chart_path):
            logger.info(f"✅ 用户参与度图表生成成功: {user_chart_path}")
        else:
            logger.error("❌ 用户参与度图表生成失败")
        
        # 测试进度趋势图
        logger.info("测试进度趋势图...")
        trend_chart_path = chart_gen.generate_progress_trend_chart(test_stats)
        if trend_chart_path and os.path.exists(trend_chart_path):
            logger.info(f"✅ 进度趋势图生成成功: {trend_chart_path}")
        else:
            logger.error("❌ 进度趋势图生成失败")
        
        # 测试综合仪表板
        logger.info("测试综合仪表板...")
        dashboard_path = chart_gen.generate_comprehensive_dashboard(test_stats)
        if dashboard_path and os.path.exists(dashboard_path):
            logger.info(f"✅ 综合仪表板生成成功: {dashboard_path}")
        else:
            logger.error("❌ 综合仪表板生成失败")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ 图表生成器导入失败: {e}")
        logger.error("请确保已安装必要的依赖库: matplotlib, seaborn, numpy")
        return False
    except Exception as e:
        logger.error(f"❌ 图表生成器测试失败: {e}")
        return False

def test_main_program_integration():
    """测试主程序集成"""
    try:
        # 临时修改任务统计文件路径
        import monthly_report_bot_final_interactive as main_program
        
        # 备份原始文件路径
        original_stats_file = getattr(main_program, 'TASK_STATS_FILE', 'task_stats.json')
        
        # 设置测试文件路径
        test_stats_file = "test_task_stats.json"
        main_program.TASK_STATS_FILE = test_stats_file
        
        logger.info("开始测试主程序集成...")
        
        # 测试图表响应生成
        logger.info("测试图表响应生成...")
        chart_response = main_program.generate_chart_response()
        
        if "统计图表已生成" in chart_response:
            logger.info("✅ 图表响应生成成功")
            logger.info(f"响应内容: {chart_response[:100]}...")
        else:
            logger.error(f"❌ 图表响应生成失败: {chart_response}")
        
        # 测试帮助信息更新
        logger.info("测试帮助信息更新...")
        help_response = main_program.generate_echo_reply("帮助")
        
        if "图表" in help_response and "可视化" in help_response:
            logger.info("✅ 帮助信息更新成功")
        else:
            logger.error("❌ 帮助信息更新失败")
        
        # 恢复原始文件路径
        main_program.TASK_STATS_FILE = original_stats_file
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 主程序集成测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖库"""
    logger.info("检查依赖库...")
    
    required_packages = [
        'matplotlib',
        'seaborn', 
        'numpy',
        'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} 已安装")
        except ImportError:
            logger.error(f"❌ {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"缺少依赖库: {', '.join(missing_packages)}")
        logger.error("请运行: pip install matplotlib seaborn numpy pandas")
        return False
    
    return True

def cleanup_test_files():
    """清理测试文件"""
    test_files = [
        "test_task_stats.json",
        "charts"
    ]
    
    for file_path in test_files:
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                logger.info(f"已删除测试文件: {file_path}")
            elif os.path.isdir(file_path):
                import shutil
                shutil.rmtree(file_path)
                logger.info(f"已删除测试目录: {file_path}")
        except Exception as e:
            logger.warning(f"清理文件失败 {file_path}: {e}")

def main():
    """主测试函数"""
    logger.info("=" * 60)
    logger.info("月报机器人图表功能测试")
    logger.info("=" * 60)
    
    # 设置测试环境
    setup_test_environment()
    
    # 测试依赖库
    if not test_dependencies():
        logger.error("依赖库检查失败，测试终止")
        return False
    
    # 测试图表生成器
    chart_test_passed = test_chart_generator()
    
    # 测试主程序集成
    integration_test_passed = test_main_program_integration()
    
    # 输出测试结果
    logger.info("=" * 60)
    logger.info("测试结果汇总:")
    logger.info(f"依赖库检查: {'✅ 通过' if test_dependencies() else '❌ 失败'}")
    logger.info(f"图表生成器: {'✅ 通过' if chart_test_passed else '❌ 失败'}")
    logger.info(f"主程序集成: {'✅ 通过' if integration_test_passed else '❌ 失败'}")
    
    overall_success = chart_test_passed and integration_test_passed
    
    if overall_success:
        logger.info("🎉 所有测试通过！图表功能已成功集成到主程序中")
    else:
        logger.error("❌ 部分测试失败，请检查错误信息")
    
    # 清理测试文件
    cleanup_test_files()
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



