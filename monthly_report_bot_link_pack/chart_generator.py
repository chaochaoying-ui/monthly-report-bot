#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表生成模块
为月报机器人提供美观的统计图表功能
"""

import os
import io
import base64
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np
from collections import Counter
import json

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 设置图表样式
sns.set_style("whitegrid")
plt.style.use('seaborn-v0_8')

logger = logging.getLogger(__name__)

class ChartGenerator:
    """图表生成器"""
    
    def __init__(self):
        self.chart_dir = "charts"
        self.ensure_chart_dir()
        
        # 设置颜色主题
        self.colors = {
            'primary': '#2E86AB',      # 主色调 - 蓝色
            'success': '#A23B72',      # 成功 - 紫红色
            'warning': '#F18F01',      # 警告 - 橙色
            'danger': '#C73E1D',       # 危险 - 红色
            'info': '#7209B7',         # 信息 - 紫色
            'light': '#F8F9FA',        # 浅色
            'dark': '#212529'          # 深色
        }
        
        # 饼图配色方案
        self.pie_colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
            '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
        ]
    
    def ensure_chart_dir(self):
        """确保图表目录存在"""
        if not os.path.exists(self.chart_dir):
            os.makedirs(self.chart_dir)
    
    def generate_task_completion_pie_chart(self, stats: Dict[str, Any]) -> str:
        """生成任务完成情况饼状图"""
        try:
            # 准备数据
            completed = stats.get('completed_tasks', 0)
            pending = stats.get('pending_tasks', 0)
            total = stats.get('total_tasks', 0)
            
            if total == 0:
                return self._generate_empty_chart("暂无任务数据")
            
            # 创建图表
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # 数据标签和数值
            labels = ['已完成', '待完成']
            sizes = [completed, pending]
            colors = [self.colors['success'], self.colors['warning']]
            
            # 突出显示已完成部分
            explode = (0.05, 0)
            
            # 绘制饼图
            wedges, texts, autotexts = ax.pie(
                sizes, 
                labels=labels,
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                explode=explode,
                shadow=True,
                textprops={'fontsize': 12, 'weight': 'bold'}
            )
            
            # 美化文本
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(14)
                autotext.set_weight('bold')
            
            # 添加标题和统计信息
            completion_rate = stats.get('completion_rate', 0)
            title = f'任务完成情况统计\n{stats.get("current_month", "")}'
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            
            # 添加图例
            legend_labels = [f'{label}: {size}个' for label, size in zip(labels, sizes)]
            ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            # 添加完成率信息
            info_text = f'总任务: {total}个\n完成率: {completion_rate}%'
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
                   fontsize=11, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            plt.tight_layout()
            
            # 保存图表
            filename = f"task_completion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.chart_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            logger.info(f"任务完成情况饼状图已生成: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"生成任务完成情况饼状图失败: {e}")
            return self._generate_error_chart("图表生成失败")
    
    def generate_user_participation_chart(self, stats: Dict[str, Any]) -> str:
        """生成用户参与度图表"""
        try:
            # 从任务统计中提取用户数据
            tasks = stats.get('tasks', {})
            user_stats = {}
            
            for task_id, task_info in tasks.items():
                assignees = task_info.get('assignees', [])
                completed = task_info.get('completed', False)
                
                for user_id in assignees:
                    if user_id not in user_stats:
                        user_stats[user_id] = {'total': 0, 'completed': 0}
                    
                    user_stats[user_id]['total'] += 1
                    if completed:
                        user_stats[user_id]['completed'] += 1
            
            if not user_stats:
                return self._generate_empty_chart("暂无用户参与数据")
            
            # 准备数据
            users = list(user_stats.keys())
            completed_counts = [user_stats[user]['completed'] for user in users]
            pending_counts = [user_stats[user]['total'] - user_stats[user]['completed'] for user in users]
            
            # 限制显示用户数量（最多10个）
            if len(users) > 10:
                # 按完成数量排序，取前10个
                user_completion = [(user, user_stats[user]['completed']) for user in users]
                user_completion.sort(key=lambda x: x[1], reverse=True)
                top_users = [user for user, _ in user_completion[:10]]
                
                users = top_users
                completed_counts = [user_stats[user]['completed'] for user in users]
                pending_counts = [user_stats[user]['total'] - user_stats[user]['completed'] for user in users]
            
            # 创建图表
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # 绘制堆叠柱状图
            x = np.arange(len(users))
            width = 0.6
            
            bars1 = ax.bar(x, completed_counts, width, label='已完成', 
                          color=self.colors['success'], alpha=0.8)
            bars2 = ax.bar(x, pending_counts, width, bottom=completed_counts, 
                          label='待完成', color=self.colors['warning'], alpha=0.8)
            
            # 美化图表
            ax.set_xlabel('用户', fontsize=12, fontweight='bold')
            ax.set_ylabel('任务数量', fontsize=12, fontweight='bold')
            ax.set_title('用户任务参与度统计', fontsize=16, fontweight='bold', pad=20)
            ax.set_xticks(x)
            ax.set_xticklabels([f'用户{i+1}' for i in range(len(users))], rotation=45)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # 添加数值标签
            for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
                height1 = bar1.get_height()
                height2 = bar2.get_height()
                total_height = height1 + height2
                
                if height1 > 0:
                    ax.text(bar1.get_x() + bar1.get_width()/2., height1/2,
                           f'{int(height1)}', ha='center', va='center', 
                           fontweight='bold', color='white')
                
                if height2 > 0:
                    ax.text(bar2.get_x() + bar2.get_width()/2., height1 + height2/2,
                           f'{int(height2)}', ha='center', va='center', 
                           fontweight='bold', color='white')
            
            plt.tight_layout()
            
            # 保存图表
            filename = f"user_participation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.chart_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            logger.info(f"用户参与度图表已生成: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"生成用户参与度图表失败: {e}")
            return self._generate_error_chart("图表生成失败")
    
    def generate_progress_trend_chart(self, stats: Dict[str, Any]) -> str:
        """生成进度趋势图"""
        try:
            # 模拟进度趋势数据（实际应用中可以从历史数据获取）
            current_rate = stats.get('completion_rate', 0)
            total_tasks = stats.get('total_tasks', 0)
            
            if total_tasks == 0:
                return self._generate_empty_chart("暂无进度数据")
            
            # 生成模拟的每日进度数据
            days = 30  # 假设30天
            daily_progress = []
            target_progress = []
            
            for day in range(1, days + 1):
                # 模拟实际进度（非线性增长）
                actual_rate = min(current_rate * (day / days) ** 0.8, 100)
                daily_progress.append(actual_rate)
                
                # 目标进度（线性增长）
                target_rate = min(100 * day / days, 100)
                target_progress.append(target_rate)
            
            # 创建图表
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # 绘制趋势线
            x = range(1, days + 1)
            ax.plot(x, daily_progress, label='实际进度', 
                   color=self.colors['primary'], linewidth=3, marker='o', markersize=4)
            ax.plot(x, target_progress, label='目标进度', 
                   color=self.colors['danger'], linewidth=2, linestyle='--', alpha=0.7)
            
            # 填充区域
            ax.fill_between(x, daily_progress, alpha=0.3, color=self.colors['primary'])
            
            # 添加当前进度标记
            current_day = int(days * current_rate / 100) if current_rate > 0 else 1
            ax.axvline(x=current_day, color=self.colors['warning'], 
                      linestyle=':', linewidth=2, alpha=0.8)
            ax.text(current_day, current_rate + 5, f'当前: {current_rate}%', 
                   fontsize=10, ha='center', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
            
            # 美化图表
            ax.set_xlabel('天数', fontsize=12, fontweight='bold')
            ax.set_ylabel('完成率 (%)', fontsize=12, fontweight='bold')
            ax.set_title('月度任务进度趋势', fontsize=16, fontweight='bold', pad=20)
            ax.set_ylim(0, 105)
            ax.set_xlim(1, days)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # 添加关键节点标注
            milestones = [25, 50, 75, 100]
            for milestone in milestones:
                if milestone <= current_rate:
                    ax.axhline(y=milestone, color='green', linestyle='-', alpha=0.5)
                    ax.text(days * 0.02, milestone, f'{milestone}%', 
                           fontsize=9, ha='left', va='center', color='green')
            
            plt.tight_layout()
            
            # 保存图表
            filename = f"progress_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.chart_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            logger.info(f"进度趋势图已生成: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"生成进度趋势图失败: {e}")
            return self._generate_error_chart("图表生成失败")
    
    def generate_comprehensive_dashboard(self, stats: Dict[str, Any]) -> str:
        """生成综合仪表板"""
        try:
            # 创建子图
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'月报任务统计仪表板 - {stats.get("current_month", "")}', 
                        fontsize=20, fontweight='bold', y=0.95)
            
            # 1. 任务完成情况饼图
            completed = stats.get('completed_tasks', 0)
            pending = stats.get('pending_tasks', 0)
            total = stats.get('total_tasks', 0)
            
            if total > 0:
                labels = ['已完成', '待完成']
                sizes = [completed, pending]
                colors = [self.colors['success'], self.colors['warning']]
                
                wedges, texts, autotexts = ax1.pie(
                    sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                    startangle=90, textprops={'fontsize': 10}
                )
                ax1.set_title('任务完成情况', fontsize=14, fontweight='bold')
            else:
                ax1.text(0.5, 0.5, '暂无数据', ha='center', va='center', 
                        transform=ax1.transAxes, fontsize=12)
                ax1.set_title('任务完成情况', fontsize=14, fontweight='bold')
            
            # 2. 完成率进度条
            completion_rate = stats.get('completion_rate', 0)
            ax2.barh(0, completion_rate, color=self.colors['primary'], height=0.5)
            ax2.set_xlim(0, 100)
            ax2.set_ylim(-0.5, 0.5)
            ax2.set_xlabel('完成率 (%)', fontsize=12)
            ax2.set_title(f'总体完成率: {completion_rate}%', fontsize=14, fontweight='bold')
            ax2.text(completion_rate/2, 0, f'{completion_rate}%', 
                    ha='center', va='center', fontsize=16, fontweight='bold', color='white')
            
            # 3. 任务数量对比
            categories = ['总任务', '已完成', '待完成']
            values = [total, completed, pending]
            colors_bar = [self.colors['info'], self.colors['success'], self.colors['warning']]
            
            bars = ax3.bar(categories, values, color=colors_bar, alpha=0.8)
            ax3.set_ylabel('任务数量', fontsize=12)
            ax3.set_title('任务数量统计', fontsize=14, fontweight='bold')
            
            # 添加数值标签
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{value}', ha='center', va='bottom', fontweight='bold')
            
            # 4. 关键指标
            ax4.axis('off')
            metrics_text = f"""
关键指标

📊 总任务数: {total}
✅ 已完成: {completed}
⏳ 待完成: {pending}
📈 完成率: {completion_rate}%
🎯 目标: 100%

状态评估:
{'🎉 优秀' if completion_rate >= 90 else '✅ 良好' if completion_rate >= 70 else '⚠️ 一般' if completion_rate >= 50 else '❌ 需改进'}
            """
            ax4.text(0.1, 0.9, metrics_text, transform=ax4.transAxes, 
                    fontsize=12, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
            
            plt.tight_layout()
            
            # 保存图表
            filename = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.chart_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            logger.info(f"综合仪表板已生成: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"生成综合仪表板失败: {e}")
            return self._generate_error_chart("仪表板生成失败")
    
    def _generate_empty_chart(self, message: str) -> str:
        """生成空数据图表"""
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, message, ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16, 
                   bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            filename = f"empty_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.chart_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filepath
        except Exception as e:
            logger.error(f"生成空数据图表失败: {e}")
            return ""
    
    def _generate_error_chart(self, message: str) -> str:
        """生成错误图表"""
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, f"❌ {message}", ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16, color='red',
                   bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            filename = f"error_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.chart_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filepath
        except Exception as e:
            logger.error(f"生成错误图表失败: {e}")
            return ""
    
    def cleanup_old_charts(self, max_age_hours: int = 24):
        """清理旧图表文件"""
        try:
            current_time = datetime.now()
            max_age = timedelta(hours=max_age_hours)
            
            for filename in os.listdir(self.chart_dir):
                if filename.endswith('.png'):
                    filepath = os.path.join(self.chart_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                    
                    if current_time - file_time > max_age:
                        os.remove(filepath)
                        logger.info(f"已清理旧图表文件: {filename}")
                        
        except Exception as e:
            logger.error(f"清理旧图表文件失败: {e}")

# 全局图表生成器实例
chart_generator = ChartGenerator()



