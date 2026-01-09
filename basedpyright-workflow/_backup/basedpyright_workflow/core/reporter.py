"""报告生成核心模块.

提供基于检查结果的 Markdown 报告生成功能。
仅支持 Markdown 格式输出，不包含 HTML 生成。
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from collections import defaultdict


class ReportGenerator:
    """基于 basedpyright 检查结果的报告生成器.

    从检查结果文件（TXT 和/或 JSON）生成详细的 Markdown 分析报告。
    仅支持 Markdown 格式，不包含 HTML 生成。

    Examples:
        >>> generator = ReportGenerator(
        ...     txt_file=Path("results/check_result.txt"),
        ...     json_file=Path("results/check_result.json")
        ... )
        >>> generator.load_results()
        True
        >>> generator.generate_markdown(Path("reports/report.md"))
        Path("reports/report.md")
    """

    def __init__(self, txt_file: Path | None = None, json_file: Path | None = None):
        """初始化报告生成器.

        Args:
            txt_file: 文本格式检查结果文件路径
            json_file: JSON 格式检查结果文件路径
        """
        self.txt_file = txt_file
        self.json_file = json_file
        self.txt_content = ""
        self.json_data: dict[str, Any] = {}

        # 统计数据
        self.stats: dict[str, Any] = {
            "total_files": 0,
            "total_errors": 0,
            "total_warnings": 0,
            "total_info": 0,
            "errors_by_file": defaultdict(int),
            "errors_by_rule": defaultdict(int),
        }

        # 错误详情列表
        self.errors: list[dict[str, Any]] = []
        self.warnings: list[dict[str, Any]] = []
        self.infos: list[dict[str, Any]] = []

    def load_results(self) -> bool:
        """加载检查结果文件.

        尝试加载 TXT 和/或 JSON 格式的检查结果文件。
        至少有一个文件成功加载即返回 True。

        Returns:
            是否成功加载至少一个文件
        """
        success = False

        # 加载文本结果
        if self.txt_file and self.txt_file.exists():
            try:
                self.txt_content = self.txt_file.read_text(encoding="utf-8")
                print(f"[OK] Loaded text file: {self.txt_file}")
                success = True
            except Exception as e:
                print(f"WARNING: Cannot read text file {self.txt_file}: {e}")

        # 加载 JSON 结果
        if self.json_file and self.json_file.exists():
            try:
                self.json_data = json.loads(self.json_file.read_text(encoding="utf-8"))
                print(f"[OK] Loaded JSON file: {self.json_file}")
                success = True
            except Exception as e:
                print(f"WARNING: Cannot read JSON file {self.json_file}: {e}")

        return success

    def parse_json_data(self) -> None:
        """解析 JSON 数据并提取统计信息."""
        if not self.json_data:
            return

        # 提取 summary 信息
        if "summary" in self.json_data:
            summary = self.json_data["summary"]
            self.stats["total_files"] = summary.get("filesAnalyzed", 0)
            self.stats["total_errors"] = summary.get("errorCount", 0)
            self.stats["total_warnings"] = summary.get("warningCount", 0)
            self.stats["total_info"] = summary.get("informationCount", 0)
            self.stats["time_in_sec"] = summary.get("timeInSec", 0)

        # 提取诊断信息
        if "generalDiagnostics" in self.json_data:
            for diag in self.json_data["generalDiagnostics"]:
                severity = diag.get("severity", "unknown")
                file_path = diag.get("file", "unknown")
                message = diag.get("message", "")
                rule = diag.get("rule", "unknown")

                # 提取位置信息
                range_info = diag.get("range", {})
                start = range_info.get("start", {})
                line = start.get("line", 0) + 1  # basedpyright 使用 0-based 行号
                character = start.get("character", 0)

                error_item = {
                    "file": file_path,
                    "line": line,
                    "column": character,
                    "severity": severity,
                    "message": message,
                    "rule": rule,
                }

                # 按严重程度分类
                if severity == "error":
                    self.errors.append(error_item)
                    self.stats["errors_by_file"][file_path] += 1
                    self.stats["errors_by_rule"][rule] += 1
                elif severity == "warning":
                    self.warnings.append(error_item)
                elif severity == "information":
                    self.infos.append(error_item)

    def parse_text_data(self) -> None:
        """从文本内容中提取统计信息（作为备用）."""
        if not self.txt_content:
            return

        # 统计错误、警告、信息数量
        self.stats["total_errors"] = self.txt_content.count(" error:")
        self.stats["total_warnings"] = self.txt_content.count(" warning:")
        self.stats["total_info"] = self.txt_content.count(" information:")

        # 提取文件列表
        files_section = re.search(
            r"检查的文件列表:.*?-{80}(.*?)-{80}", self.txt_content, re.DOTALL
        )
        if files_section:
            file_lines = files_section.group(1).strip().split("\n")
            self.stats["total_files"] = len([l for l in file_lines if l.strip()])

    def generate_markdown(self, output_file: Path) -> Path:
        """生成 Markdown 格式报告.

        Args:
            output_file: 输出文件路径（必须是以 .md 结尾）

        Returns:
            输出文件路径

        Raises:
            ValueError: 如果 output_file 不是 .md 扩展名
        """
        if output_file.suffix.lower() != ".md":
            raise ValueError(f"输出文件必须是 Markdown 格式（.md）: {output_file}")

        # 解析数据
        if self.json_data:
            self.parse_json_data()
        elif self.txt_content:
            self.parse_text_data()

        # 生成报告
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = []

        # 标题和元数据
        lines.append("# BasedPyright 检查报告\n")
        lines.append(f"**生成时间**: {timestamp}\n")

        if self.json_data.get("metadata"):
            meta = self.json_data["metadata"]
            lines.append(f"**检查时间**: {meta.get('check_time', 'N/A')}\n")
            lines.append(f"**检查目录**: `{meta.get('check_directory', 'N/A')}`\n")

        lines.append("\n")

        # 执行摘要
        lines.append("## 📊 执行摘要\n\n")
        lines.append("| 项目 | 数量 |\n")
        lines.append("|------|------|\n")
        lines.append(f"| 检查文件数 | {self.stats['total_files']} |\n")
        lines.append(f"| ❌ 错误 (Error) | {self.stats['total_errors']} |\n")
        lines.append(f"| ⚠️ 警告 (Warning) | {self.stats['total_warnings']} |\n")
        lines.append(f"| ℹ️ 信息 (Information) | {self.stats['total_info']} |\n")

        if "time_in_sec" in self.stats:
            lines.append(f"| ⏱️ 检查耗时 | {self.stats['time_in_sec']:.2f} 秒 |\n")

        lines.append("\n")

        # 错误统计
        if self.errors:
            lines.append("## 🔴 错误详情\n\n")
            lines.append(f"共发现 **{len(self.errors)}** 个错误\n\n")

            # 按文件分组
            lines.append("### 按文件分组\n\n")
            for file_path, count in sorted(
                self.stats["errors_by_file"].items(),
                key=lambda x: x[1],
                reverse=True,
            ):
                lines.append(f"- `{file_path}`: {count} 个错误\n")
            lines.append("\n")

            # 按规则分组
            lines.append("### 按规则分组\n\n")
            for rule, count in sorted(
                self.stats["errors_by_rule"].items(),
                key=lambda x: x[1],
                reverse=True,
            ):
                lines.append(f"- `{rule}`: {count} 次\n")
            lines.append("\n")

            # 详细错误列表
            lines.append("### 详细错误列表\n\n")
            for i, error in enumerate(self.errors, 1):
                lines.append(f"#### {i}. {error['file']}:{error['line']}\n\n")
                lines.append(f"- **规则**: `{error['rule']}`\n")
                # 兼容不同的键名 (character 或 column)
                col = error.get('character') or error.get('column') or 0
                lines.append(f"- **位置**: 第 {error['line']} 行, 第 {col} 列\n")
                lines.append(f"- **错误信息**: {error['message']}\n")
                lines.append("\n")
        else:
            lines.append("## ✅ 无错误\n\n")
            lines.append("恭喜！没有发现任何错误。\n\n")

        # 警告详情
        if self.warnings:
            lines.append("## ⚠️ 警告详情\n\n")
            lines.append(f"共发现 **{len(self.warnings)}** 个警告\n\n")

            for i, warning in enumerate(self.warnings[:20], 1):
                lines.append(
                    f"{i}. `{warning['file']}:{warning['line']}` - {warning['message']} (`{warning['rule']}`)\n"
                )

            if len(self.warnings) > 20:
                lines.append(f"\n... 还有 {len(self.warnings) - 20} 个警告未显示\n")
            lines.append("\n")

        # 检查的文件列表
        if self.json_data.get("metadata", {}).get("python_files"):
            lines.append("## 📁 检查的文件列表\n\n")
            files = self.json_data["metadata"]["python_files"]
            for i, file in enumerate(files, 1):
                lines.append(f"{i}. `{file}`\n")
            lines.append("\n")

        # 原始文本输出（可选）
        if self.txt_content:
            lines.append("## 📄 原始检查输出\n\n")
            lines.append("```\n")
            # 只包含输出结果部分
            output_section = re.search(
                r"检查输出结果:.*?={80}(.*)", self.txt_content, re.DOTALL
            )
            if output_section:
                lines.append(output_section.group(1).strip())
            else:
                lines.append(self.txt_content[-5000:])  # 最后5000字符
            lines.append("\n```\n\n")

        # 写入文件
        output_file.write_text("".join(lines), encoding="utf-8")
        print(f"[OK] Markdown report generated: {output_file}")

        return output_file

    def generate_reports(self, output_dir: Path) -> tuple[Path, None]:
        """生成所有格式的报告.

        Args:
            output_dir: 输出目录

        Returns:
            (markdown_file, None) 元组

        Note:
            本版本仅支持 Markdown 格式，第二个元素始终为 None
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 解析数据
        if self.json_data:
            self.parse_json_data()
        elif self.txt_content:
            self.parse_text_data()

        # 生成 Markdown 报告
        md_file = output_dir / f"basedpyright_report_{timestamp}.md"
        self.generate_markdown(md_file)

        print("\n" + "=" * 80)
        print("Report generation completed!")
        print(f"  - Markdown: {md_file}")
        print("=" * 80)

        return md_file, None
