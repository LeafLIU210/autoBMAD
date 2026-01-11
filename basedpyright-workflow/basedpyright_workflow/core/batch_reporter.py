"""批量报告生成器模块

扩展现有的报告生成功能，支持批量处理报告、趋势分析和多文件比较。
基于原有的 ReportGenerator，增加批量处理能力。
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict

from .batch_processor import BatchErrorProcessor


@dataclass
class BatchReportConfig:
    """批量报告配置"""
    include_trends: bool = True
    include_file_comparison: bool = True
    include_category_analysis: bool = True
    include_fix_recommendations: bool = True
    max_error_details: int = 50
    max_files_in_summary: int = 20


@dataclass
class TrendAnalysis:
    """趋势分析数据"""
    period: str
    error_count: int
    warning_count: int
    file_count: int
    unique_errors: int
    auto_fixable: int
    timestamp: datetime


@dataclass
class FileComparison:
    """文件比较数据"""
    file_path: str
    current_errors: int
    previous_errors: int
    change: int
    change_percentage: float
    trend: str  # "improving", "worsening", "stable"


class BatchReportGenerator:
    """批量报告生成器

    支持以下功能：
    1. 多个错误文件的汇总报告
    2. 历史数据趋势分析
    3. 文件级别的变化追踪
    4. 增强的错误分析和建议
    5. 可配置的报告内容
    """

    def __init__(self, config: Optional[BatchReportConfig] = None):
        """初始化批量报告生成器

        Args:
            config: 批量报告配置，如果为None则使用默认配置
        """
        self.config = config or BatchReportConfig()
        self.processors: List[BatchErrorProcessor] = []
        self.reports: List[Dict] = []
        self.trend_data: List[TrendAnalysis] = []

    def add_processor(self, processor: BatchErrorProcessor) -> None:
        """添加批量处理器到报告生成器

        Args:
            processor: 已完成分析的批量处理器
        """
        if processor.stats:
            self.processors.append(processor)

    def load_from_files(self, error_files: List[Path]) -> bool:
        """从多个错误文件加载数据

        Args:
            error_files: 错误文件路径列表

        Returns:
            bool: 是否成功加载所有文件
        """
        success = True
        for file_path in error_files:
            try:
                processor = BatchErrorProcessor(file_path)
                if processor.load_errors():
                    processor.analyze()
                    self.add_processor(processor)
                    print(f"已加载: {file_path.name}")
                else:
                    print(f"加载失败: {file_path}")
                    success = False
            except Exception as e:
                print(f"处理文件失败 {file_path}: {e}")
                success = False

        return success

    def load_historical_data(self, results_dir: Path, days: int = 30) -> None:
        """加载历史数据用于趋势分析

        Args:
            results_dir: 结果目录路径
            days: 要分析的天数
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        # 查找历史报告文件
        pattern = "batch_analysis_report_*.json"
        historical_files = []

        for file_path in results_dir.glob(pattern):
            try:
                # 从文件名提取时间戳
                timestamp_str = file_path.stem.split('_')[-1]
                file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

                if file_date >= cutoff_date:
                    historical_files.append((file_path, file_date))
            except ValueError:
                continue

        # 按时间排序
        historical_files.sort(key=lambda x: x[1])

        # 生成趋势数据
        for file_path, file_date in historical_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                stats = data.get('statistics', {})
                trend = TrendAnalysis(
                    period=file_date.strftime("%Y-%m-%d"),
                    error_count=stats.get('total_errors', 0),
                    warning_count=stats.get('total_warnings', 0),
                    file_count=len(stats.get('by_file', {})),
                    unique_errors=stats.get('unique_errors', 0),
                    auto_fixable=stats.get('auto_fixable_count', 0),
                    timestamp=file_date
                )
                self.trend_data.append(trend)

            except Exception as e:
                print(f"处理历史文件失败 {file_path}: {e}")

    def _calculate_file_comparisons(self) -> List[FileComparison]:
        """计算文件级别的比较数据

        Returns:
            List[FileComparison]: 文件比较数据列表
        """
        if not self.trend_data or len(self.processors) == 0:
            return []

        # 获取当前和之前的错误数据
        current_processor = self.processors[-1]  # 最新的处理器
        current_file_errors = Counter(error.file for error in current_processor.processed_errors)

        # 如果有历史数据，使用最近的历史点作为比较基准
        if self.trend_data:
            # 查找最近的包含详细错误信息的历史报告
            previous_file_errors = Counter()
            # 这里简化处理，实际项目中可以从历史报告中解析详细错误信息

        comparisons = []
        for file_path, current_count in current_file_errors.items():
            previous_count = previous_file_errors.get(file_path, 0)
            change = current_count - previous_count
            change_percentage = (change / previous_count * 100) if previous_count > 0 else 100

            if change > 0:
                trend = "worsening"
            elif change < 0:
                trend = "improving"
            else:
                trend = "stable"

            comparison = FileComparison(
                file_path=file_path,
                current_errors=current_count,
                previous_errors=previous_count,
                change=change,
                change_percentage=change_percentage,
                trend=trend
            )
            comparisons.append(comparison)

        return sorted(comparisons, key=lambda x: abs(x.change), reverse=True)

    def _generate_trend_summary(self) -> Dict[str, Any]:
        """生成趋势分析摘要

        Returns:
            Dict: 趋势分析摘要
        """
        if not self.trend_data:
            return {}

        if len(self.trend_data) < 2:
            return {
                "period_count": len(self.trend_data),
                "latest_period": self.trend_data[0].period,
                "message": "需要更多数据点来进行趋势分析"
            }

        latest = self.trend_data[-1]
        earliest = self.trend_data[0]

        error_trend = "stable"
        if latest.error_count > earliest.error_count * 1.1:
            error_trend = "increasing"
        elif latest.error_count < earliest.error_count * 0.9:
            error_trend = "decreasing"

        return {
            "period_count": len(self.trend_data),
            "date_range": f"{earliest.period} to {latest.period}",
            "error_trend": error_trend,
            "error_change": latest.error_count - earliest.error_count,
            "error_change_percentage": (
                (latest.error_count - earliest.error_count) / earliest.error_count * 100
                if earliest.error_count > 0 else 0
            ),
            "auto_fixable_trend": "improving" if latest.auto_fixable > earliest.auto_fixable else "stable"
        }

    def generate_comprehensive_markdown(self, output_file: Path) -> Path:
        """生成综合批量处理 Markdown 报告

        Args:
            output_file: 输出文件路径

        Returns:
            Path: 生成的报告文件路径
        """
        lines = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 报告头部
        lines.append("# BasedPyright 批量处理综合报告\n\n")
        lines.append(f"**生成时间**: {timestamp}\n")
        lines.append(f"**分析文件数量**: {len(self.processors)}\n")
        lines.append(f"**报告配置**: 趋势分析={'启用' if self.config.include_trends else '禁用'}, "
                   f"文件比较={'启用' if self.config.include_file_comparison else '禁用'}\n\n")

        # 执行摘要
        self._add_executive_summary(lines)

        # 趋势分析
        if self.config.include_trends and self.trend_data:
            self._add_trend_analysis_section(lines)

        # 文件比较分析
        if self.config.include_file_comparison:
            self._add_file_comparison_section(lines)

        # 错误分类分析
        if self.config.include_category_analysis:
            self._add_category_analysis_section(lines)

        # 修复建议和优先级
        if self.config.include_fix_recommendations:
            self._add_fix_recommendations_section(lines)

        # 详细错误列表
        self._add_detailed_errors_section(lines)

        # 附录和统计
        self._add_appendix_section(lines)

        # 写入文件
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("".join(lines), encoding="utf-8")

        return output_file

    def _add_executive_summary(self, lines: List[str]) -> None:
        """添加执行摘要部分"""
        lines.append("## 📊 执行摘要\n\n")

        if not self.processors:
            lines.append("未找到可分析的数据。\n\n")
            return

        # 汇总统计
        total_errors = sum(p.stats.total_errors for p in self.processors if p.stats)
        total_unique = sum(p.stats.unique_errors for p in self.processors if p.stats)
        total_auto_fixable = sum(p.stats.auto_fixable_count for p in self.processors if p.stats)
        total_files = len(set(
            error.file
            for processor in self.processors
            for error in processor.processed_errors
        ))

        lines.append("| 指标 | 数值 | 说明 |\n")
        lines.append("|------|------|------|\n")
        lines.append(f"| 📁 涉及文件 | {total_files} | 存在错误的源代码文件数量 |\n")
        lines.append(f"| ❌ 总错误数 | {total_errors} | 所有检查中的原始错误总数 |\n")
        lines.append(f"| 🔄 去重错误 | {total_unique} | 去重后的唯一错误数量 |\n")
        lines.append(f"| 🔧 可自动修复 | {total_auto_fixable} | 置信度较高的可修复错误 |\n")
        lines.append(f"| 📈 修复率 | {total_auto_fixable/total_unique*100:.1f}% | 可修复错误占比 |\n\n")

        # 整体评估
        if total_unique == 0:
            status = "✅ 优秀"
            recommendation = "代码质量良好，继续保持"
        elif total_auto_fixable / total_unique > 0.7:
            status = "⚠️ 需要关注"
            recommendation = "大部分错误可以自动修复，建议运行批量修复"
        elif total_auto_fixable / total_unique > 0.3:
            status = "🔴 需要处理"
            recommendation = "需要人工审查和自动修复相结合"
        else:
            status = "🚨 高优先级"
            recommendation = "错误较为复杂，需要仔细分析并制定修复计划"

        lines.append(f"### 整体评估: {status}\n\n")
        lines.append(f"**建议**: {recommendation}\n\n")

    def _add_trend_analysis_section(self, lines: List[str]) -> None:
        """添加趋势分析部分"""
        lines.append("## 📈 趋势分析\n\n")

        trend_summary = self._generate_trend_summary()
        if not trend_summary:
            lines.append("暂无足够的历史数据进行趋势分析。\n\n")
            return

        lines.append(f"**分析周期**: {trend_summary.get('date_range', 'N/A')}\n")
        lines.append(f"**数据点数量**: {trend_summary.get('period_count', 0)}\n\n")

        # 趋势指标
        lines.append("### 关键趋势\n\n")
        lines.append("| 指标 | 趋势 | 变化 |\n")
        lines.append("|------|------|------|\n")

        error_trend = trend_summary.get('error_trend', 'stable')
        trend_icons = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}
        error_change = trend_summary.get('error_change', 0)

        lines.append(f"| 错误数量 | {trend_icons.get(error_trend, '➡️')} {error_trend} | {error_change:+d} |\n")

        auto_fixable_trend = trend_summary.get('auto_fixable_trend', 'stable')
        lines.append(f"| 可修复性 | {trend_icons.get(auto_fixable_trend, '➡️')} {auto_fixable_trend} | - |\n\n")

        # 趋势图表（简化版本）
        if len(self.trend_data) > 1:
            lines.append("### 历史趋势图\n\n")
            lines.append("```\n")
            lines.append("错误数量趋势:")
            for i, trend in enumerate(self.trend_data[-10:]):  # 显示最近10个数据点
                bar_length = min(50, trend.error_count)
                bar = "█" * bar_length
                lines.append(f"{trend.period} | {bar} {trend.error_count}")
            lines.append("```\n\n")

    def _add_file_comparison_section(self, lines: List[str]) -> None:
        """添加文件比较部分"""
        lines.append("## 📁 文件级别分析\n\n")

        # 收集所有文件的错误统计
        file_stats = defaultdict(lambda: {'errors': 0, 'categories': defaultdict(int)})

        for processor in self.processors:
            for error in processor.processed_errors:
                file_stats[error.file]['errors'] += 1
                file_stats[error.file]['categories'][error.category.value] += 1

        # 按错误数量排序
        sorted_files = sorted(file_stats.items(), key=lambda x: x[1]['errors'], reverse=True)

        lines.append(f"共涉及 **{len(sorted_files)}** 个文件\n\n")

        # Top 文件表格
        lines.append("### 错误数量最多的文件\n\n")
        lines.append("| 排名 | 文件路径 | 错误数 | 简单错误 | 复杂错误 | 需人工审查 |\n")
        lines.append("|------|----------|--------|----------|----------|------------|\n")

        for i, (file_path, stats) in enumerate(sorted_files[:self.config.max_files_in_summary], 1):
            simple = stats['categories']['simple']
            complex_err = stats['categories']['complex']
            manual = stats['categories']['manual']

            # 截断过长的文件路径
            display_path = file_path if len(file_path) <= 50 else "..." + file_path[-47:]

            lines.append(f"| {i} | `{display_path}` | {stats['errors']} | {simple} | {complex_err} | {manual} |\n")

        lines.append("\n")

    def _add_category_analysis_section(self, lines: List[str]) -> None:
        """添加错误分类分析部分"""
        lines.append("## 🏷️ 错误分类分析\n\n")

        # 汇总所有处理器的分类统计
        category_totals = defaultdict(int)
        severity_totals = defaultdict(int)

        for processor in self.processors:
            if processor.stats:
                for category, count in processor.stats.by_category.items():
                    category_totals[category] += count
                for severity, count in processor.stats.by_severity.items():
                    severity_totals[severity] += count

        total_errors = sum(category_totals.values())

        if total_errors == 0:
            lines.append("没有发现错误。\n\n")
            return

        # 分类统计表格
        lines.append("### 错误分类分布\n\n")
        lines.append("| 分类 | 数量 | 占比 | 修复难度 |\n")
        lines.append("|------|------|------|----------|\n")

        difficulty_map = {
            "simple": "🟢 简单",
            "complex": "🟡 中等",
            "manual": "🔴 复杂"
        }

        for category in ["simple", "complex", "manual"]:
            count = category_totals.get(category, 0)
            percentage = count / total_errors * 100 if total_errors > 0 else 0
            difficulty = difficulty_map.get(category, "未知")

            lines.append(f"| {difficulty} | {count} | {percentage:.1f}% | {category} |\n")

        lines.append("\n")

        # 严重程度分布
        lines.append("### 严重程度分布\n\n")
        lines.append("| 严重程度 | 数量 | 占比 | 优先级 |\n")
        lines.append("|----------|------|------|--------|\n")

        priority_map = {
            "critical": "🚨 立即",
            "high": "🔴 高",
            "medium": "🟡 中",
            "low": "🟢 低"
        }

        for severity in ["critical", "high", "medium", "low"]:
            count = severity_totals.get(severity, 0)
            percentage = count / total_errors * 100 if total_errors > 0 else 0
            priority = priority_map.get(severity, "未知")

            lines.append(f"| {priority} {severity} | {count} | {percentage:.1f}% | 立即修复 if severity == 'critical' else '高优先级' if severity == 'high' else '中等优先级' if severity == 'medium' else '低优先级' |\n")

        lines.append("\n")

    def _add_fix_recommendations_section(self, lines: List[str]) -> None:
        """添加修复建议部分"""
        lines.append("## 🔧 修复建议和优先级\n\n")

        # 收集所有可自动修复的错误
        auto_fixable_errors = []
        for processor in self.processors:
            auto_fixable_errors.extend(processor.get_auto_fixable_errors())

        if not auto_fixable_errors:
            lines.append("当前没有可自动修复的错误。\n\n")
            return

        lines.append(f"发现 **{len(auto_fixable_errors)}** 个可自动修复的错误\n\n")

        # 按置信度分组
        high_confidence = [e for e in auto_fixable_errors if e.confidence >= 0.9]
        medium_confidence = [e for e in auto_fixable_errors if 0.7 <= e.confidence < 0.9]
        low_confidence = [e for e in auto_fixable_errors if e.confidence < 0.7]

        lines.append("### 按置信度分组\n\n")
        lines.append(f"- 🟢 高置信度 (≥90%): {len(high_confidence)} 个错误")
        lines.append(f"- 🟡 中置信度 (70-89%): {len(medium_confidence)} 个错误")
        lines.append(f"- 🔴 低置信度 (<70%): {len(low_confidence)} 个错误\n\n")

        # 修复操作建议
        lines.append("### 推荐修复操作\n\n")

        if high_confidence:
            lines.append("1. **立即自动修复** (高置信度错误)\n")
            lines.append("   ```bash\n")
            lines.append("   basedpyright batch-fix --auto\n")
            lines.append("   ```\n\n")

        if medium_confidence:
            lines.append("2. **交互式修复** (中置信度错误)\n")
            lines.append("   ```bash\n")
            lines.append("   basedpyright batch-fix\n")
            lines.append("   ```\n\n")

        if low_confidence:
            lines.append("3. **人工审查** (低置信度错误)\n")
            lines.append("   建议手动检查这些错误，确认修复建议的准确性\n\n")

        # 常见错误模式
        lines.append("### 常见错误模式\n\n")
        error_patterns = defaultdict(int)
        for error in auto_fixable_errors:
            # 提取错误模式（简化版本）
            pattern = error.rule
            error_patterns[pattern] += 1

        for pattern, count in sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
            lines.append(f"- **{pattern}**: {count} 个错误\n")

        lines.append("\n")

    def _add_detailed_errors_section(self, lines: List[str]) -> None:
        """添加详细错误列表部分"""
        lines.append("## 📋 详细错误列表\n\n")

        # 收集所有错误并按优先级排序
        all_errors = []
        for processor in self.processors:
            all_errors.extend(processor.processed_errors)

        if not all_errors:
            lines.append("没有发现错误。\n\n")
            return

        # 按严重程度和类别排序
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        category_order = {"simple": 0, "complex": 1, "manual": 2}

        def sort_key(error):
            return (
                severity_order.get(error.severity_level.value, 3),
                category_order.get(error.category.value, 2),
                -error.confidence
            )

        sorted_errors = sorted(all_errors, key=sort_key)

        # 显示前N个最重要的错误
        display_count = min(len(sorted_errors), self.config.max_error_details)
        lines.append(f"显示前 {display_count} 个高优先级错误（共 {len(sorted_errors)} 个）\n\n")

        for i, error in enumerate(sorted_errors[:display_count], 1):
            severity_icon = {"critical": "🚨", "high": "🔴", "medium": "🟡", "low": "🟢"}
            category_icon = {"simple": "🟢", "complex": "🟡", "manual": "🔴"}

            icon = f"{severity_icon.get(error.severity_level.value, '❓')} {category_icon.get(error.category.value, '❓')}"

            lines.append(f"### {i}. {icon} {error.file}:{error.line}\n\n")
            lines.append(f"**错误信息**: {error.message}\n\n")
            lines.append(f"**规则**: `{error.rule}`\n")
            lines.append(f"**严重程度**: {error.severity_level.value}\n")
            lines.append(f"**分类**: {error.category.value}\n")
            lines.append(f"**置信度**: {error.confidence:.1%}\n")

            if error.fix_suggestion:
                lines.append(f"**修复建议**: {error.fix_suggestion}\n")

            lines.append("\n---\n\n")

    def _add_appendix_section(self, lines: List[str]) -> None:
        """添加附录部分"""
        lines.append("## 📖 附录\n\n")

        # 技术信息
        lines.append("### 技术信息\n\n")
        lines.append("- **报告生成器版本**: BatchReportGenerator v1.0\n")
        lines.append("- **分析器版本**: BatchErrorProcessor\n")
        lines.append(f"- **生成时间**: {datetime.now().isoformat()}\n")
        lines.append(f"- **配置选项**: {asdict(self.config)}\n\n")

        # 使用说明
        lines.append("### 使用说明\n\n")
        lines.append("1. **自动修复**: 运行 `basedpyright batch-fix --auto` 修复高置信度错误\n")
        lines.append("2. **交互修复**: 运行 `basedpyright batch-fix` 逐个确认修复\n")
        lines.append("3. **重新分析**: 运行 `basedpyright batch-analyze` 重新生成分析报告\n")
        lines.append("4. **持续监控**: 定期运行检查以跟踪代码质量趋势\n\n")

        # 故障排除
        lines.append("### 故障排除\n\n")
        lines.append("- 如果修复建议不准确，请检查具体的错误上下文\n")
        lines.append("- 复杂错误可能需要重新设计类型系统或代码结构\n")
        lines.append("- 建议在修复前创建代码分支以便回滚\n")
        lines.append("- 可以通过更新分类规则来改进错误分析准确性\n\n")

        lines.append("---\n")
        lines.append(f"*报告生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

    def generate_summary_report(self, output_file: Path) -> Path:
        """生成简化的摘要报告

        Args:
            output_file: 输出文件路径

        Returns:
            Path: 生成的报告文件路径
        """
        lines = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines.append("# BasedPyright 批量处理摘要\n\n")
        lines.append(f"**生成时间**: {timestamp}\n\n")

        if not self.processors:
            lines.append("未找到可分析的数据。\n\n")
            output_file.write_text("".join(lines), encoding="utf-8")
            return output_file

        # 快速统计
        total_errors = sum(p.stats.total_errors for p in self.processors if p.stats)
        total_unique = sum(p.stats.unique_errors for p in self.processors if p.stats)
        total_auto_fixable = sum(p.stats.auto_fixable_count for p in self.processors if p.stats)

        lines.append("## 📊 快速统计\n\n")
        lines.append(f"- 总错误数: {total_errors}\n")
        lines.append(f"- 去重错误: {total_unique}\n")
        lines.append(f"- 可修复: {total_auto_fixable} ({total_auto_fixable/total_unique*100:.1f}%)\n\n")

        # 下一步操作
        lines.append("## 🎯 建议操作\n\n")

        if total_auto_fixable > 0:
            lines.append("1. **立即修复可自动修复的错误**:\n")
            lines.append("   ```bash\n")
            lines.append("   basedpyright batch-fix --auto\n")
            lines.append("   ```\n\n")

        lines.append("2. **查看详细报告**:\n")
        lines.append("   运行 `basedpyright batch-report` 生成完整的分析报告\n\n")

        lines.append("3. **持续监控**:\n")
        lines.append("   定期运行检查以跟踪代码质量变化\n\n")

        output_file.write_text("".join(lines), encoding="utf-8")
        return output_file