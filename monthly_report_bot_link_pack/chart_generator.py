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
        """生成美化版综合仪表板"""
        try:
            # 用户ID到中文名映射
            user_mapping = {
                "ou_b96c7ed4a604dc049569102d01c6c26d": "刘野",
                "ou_07443a67428d8741eab5eac851b754b9": "范明杰",
                "ou_3b14801caa065a0074c7d6db8603f288": "袁阿虎",
                "ou_33d81ce8839d93132e4417530f60c4a9": "高雅慧",
                "ou_17b6bee82dd946d92a322cc7dea40eb7": "马富凡",
                "ou_03491624846d90ea22fa64177860a8cf": "刘智辉",
                "ou_7552fdb195c3ad2c0453258fb157c12a": "成自飞",
                "ou_f5338c49049621c36310e2215204d0be": "景晓东",
                "ou_2f93cb9407ca5a281a92d1f5a72fdf7b": "唐进",
                "ou_d85dd7bb7625ab3e3f8b129e54934aea": "何寨",
                "ou_50c492f1d2b2ee2107c4e28ab4416732": "闵国政",
            }

            # 统计已完成人员
            completed_users = {}
            tasks = stats.get('tasks', {})
            for task_id, task_info in tasks.items():
                if task_info.get('completed', False):
                    for assignee in task_info.get('assignees', []):
                        user_name = user_mapping.get(assignee, f"用户{assignee[:8]}")
                        completed_users[user_name] = completed_users.get(user_name, 0) + 1

            # 创建子图
            fig = plt.figure(figsize=(18, 12))
            gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

            # 设置整体背景色
            fig.patch.set_facecolor('#F8F9FA')

            # 主标题
            fig.suptitle(f'📊 月报任务统计仪表板 - {stats.get("current_month", "")}',
                        fontsize=24, fontweight='bold', y=0.98, color='#2C3E50')

            # 1. 任务完成情况饼图（左上，跨2列）
            ax1 = fig.add_subplot(gs[0, :2])
            completed = stats.get('completed_tasks', 0)
            pending = stats.get('pending_tasks', 0)
            total = stats.get('total_tasks', 0)

            if total > 0:
                labels = ['✅ 已完成', '⏳ 待完成']
                sizes = [completed, pending]
                # 使用渐变色
                colors = ['#2ECC71', '#F39C12']
                explode = (0.08, 0.02)

                wedges, texts, autotexts = ax1.pie(
                    sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                    startangle=90, explode=explode, shadow=True,
                    textprops={'fontsize': 13, 'weight': 'bold'},
                    wedgeprops={'edgecolor': 'white', 'linewidth': 3}
                )

                # 美化百分比文本
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontsize(16)
                    autotext.set_weight('bold')

                # 添加中心圆圈，制造环形图效果
                centre_circle = plt.Circle((0, 0), 0.70, fc='white')
                ax1.add_artist(centre_circle)

                # 在中心显示完成率
                completion_rate = stats.get('completion_rate', 0)
                ax1.text(0, 0, f'{completion_rate}%', ha='center', va='center',
                        fontsize=36, fontweight='bold', color='#2C3E50')
                ax1.text(0, -0.15, '总完成率', ha='center', va='center',
                        fontsize=14, color='#7F8C8D')

                ax1.set_title('📈 任务完成情况分布', fontsize=16, fontweight='bold',
                             pad=20, color='#34495E')
            else:
                ax1.text(0.5, 0.5, '暂无数据', ha='center', va='center',
                        transform=ax1.transAxes, fontsize=14)
                ax1.set_title('任务完成情况', fontsize=16, fontweight='bold')

            # 2. 关键指标卡片（右上）
            ax2 = fig.add_subplot(gs[0, 2])
            ax2.axis('off')
            ax2.set_facecolor('#ECF0F1')

            completion_rate = stats.get('completion_rate', 0)
            status_emoji = '🎉' if completion_rate >= 90 else '✅' if completion_rate >= 70 else '⚠️' if completion_rate >= 50 else '❌'
            status_text = '优秀' if completion_rate >= 90 else '良好' if completion_rate >= 70 else '一般' if completion_rate >= 50 else '需改进'
            status_color = '#27AE60' if completion_rate >= 70 else '#F39C12' if completion_rate >= 50 else '#E74C3C'

            metrics_text = f"""
{status_emoji} 状态评估: {status_text}

━━━━━━━━━━━━━━

📊 总任务数
   {total} 个

✅ 已完成
   {completed} 个

⏳ 待完成
   {pending} 个

📈 完成率
   {completion_rate}%

🎯 目标完成率
   100%
            """

            ax2.text(0.5, 0.5, metrics_text, transform=ax2.transAxes,
                    fontsize=13, verticalalignment='center', ha='center',
                    bbox=dict(boxstyle='round,pad=1.5', facecolor='white',
                             edgecolor=status_color, linewidth=3, alpha=0.95),
                    linespacing=1.8, family='monospace')

            # 3. 已完成人员排行榜（左中，跨2列）
            ax3 = fig.add_subplot(gs[1, :2])

            if completed_users:
                # 按完成数量排序
                sorted_users = sorted(completed_users.items(), key=lambda x: x[1], reverse=True)
                names = [item[0] for item in sorted_users[:8]]  # 最多显示8个
                counts = [item[1] for item in sorted_users[:8]]

                # 渐变色条形图
                colors_gradient = plt.cm.viridis(np.linspace(0.3, 0.9, len(names)))

                bars = ax3.barh(names, counts, color=colors_gradient,
                               edgecolor='white', linewidth=2, height=0.7)

                # 添加数值标签
                for i, (bar, count) in enumerate(zip(bars, counts)):
                    width = bar.get_width()
                    ax3.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                            f'{count}个任务', ha='left', va='center',
                            fontsize=11, fontweight='bold', color='#2C3E50')

                ax3.set_xlabel('完成任务数', fontsize=13, fontweight='bold', color='#34495E')
                ax3.set_title('🏆 已完成人员排行榜 (TOP 8)', fontsize=16,
                             fontweight='bold', pad=15, color='#34495E')
                ax3.spines['top'].set_visible(False)
                ax3.spines['right'].set_visible(False)
                ax3.grid(axis='x', alpha=0.3, linestyle='--')
                ax3.set_axisbelow(True)
            else:
                ax3.text(0.5, 0.5, '暂无已完成人员数据', ha='center', va='center',
                        transform=ax3.transAxes, fontsize=14, color='#7F8C8D')
                ax3.set_title('🏆 已完成人员排行榜', fontsize=16, fontweight='bold')
                ax3.axis('off')

            # 4. 进度条可视化（右中）
            ax4 = fig.add_subplot(gs[1, 2])
            ax4.axis('off')

            completion_rate = stats.get('completion_rate', 0)

            # 绘制背景进度条
            bar_height = 0.3
            bar_y = 0.5
            ax4.barh(bar_y, 100, height=bar_height, color='#ECF0F1',
                    left=0, edgecolor='#BDC3C7', linewidth=2)

            # 绘制实际进度（渐变效果）
            if completion_rate > 0:
                # 根据完成率选择颜色
                if completion_rate >= 80:
                    bar_color = '#27AE60'  # 绿色
                elif completion_rate >= 50:
                    bar_color = '#F39C12'  # 橙色
                else:
                    bar_color = '#E74C3C'  # 红色

                ax4.barh(bar_y, completion_rate, height=bar_height,
                        color=bar_color, left=0, edgecolor='white', linewidth=2,
                        alpha=0.9)

            # 添加百分比文本
            ax4.text(50, bar_y, f'{completion_rate}%', ha='center', va='center',
                    fontsize=20, fontweight='bold', color='white',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='#34495E', alpha=0.8))

            # 添加刻度标记
            for i in [0, 25, 50, 75, 100]:
                ax4.text(i, bar_y - 0.25, f'{i}%', ha='center', va='top',
                        fontsize=9, color='#7F8C8D')
                ax4.plot([i, i], [bar_y - 0.15, bar_y - bar_height/2],
                        color='#BDC3C7', linewidth=1)

            ax4.set_xlim(-5, 105)
            ax4.set_ylim(0, 1)
            ax4.set_title('📊 总体完成进度', fontsize=14, fontweight='bold',
                         pad=20, color='#34495E')

            # 5. 任务数量对比（底部，跨3列）
            ax5 = fig.add_subplot(gs[2, :])

            categories = ['📋 总任务', '✅ 已完成', '⏳ 待完成']
            values = [total, completed, pending]
            colors_bar = ['#3498DB', '#2ECC71', '#F39C12']

            bars = ax5.bar(categories, values, color=colors_bar, alpha=0.85,
                          edgecolor='white', linewidth=3, width=0.6)

            # 添加数值标签
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax5.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                        f'{value}', ha='center', va='bottom',
                        fontsize=18, fontweight='bold', color='#2C3E50')

            ax5.set_ylabel('任务数量', fontsize=13, fontweight='bold', color='#34495E')
            ax5.set_title('📊 任务数量统计对比', fontsize=16, fontweight='bold',
                         pad=15, color='#34495E')
            ax5.spines['top'].set_visible(False)
            ax5.spines['right'].set_visible(False)
            ax5.grid(axis='y', alpha=0.3, linestyle='--')
            ax5.set_axisbelow(True)
            ax5.tick_params(labelsize=12)

            # 设置y轴范围
            if max(values) > 0:
                ax5.set_ylim(0, max(values) * 1.2)

            # 保存图表
            filename = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.chart_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight',
                       facecolor='#F8F9FA', edgecolor='none')
            plt.close()

            logger.info(f"美化版综合仪表板已生成: {filepath}")
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



