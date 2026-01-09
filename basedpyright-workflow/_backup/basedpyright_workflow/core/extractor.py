"""错误提取核心模块.

从 basedpyright 检查结果中提取 ERROR 级别错误，
生成结构化 JSON 数据用于自动化修复。
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from collections import defaultdict
import glob


class ErrorExtractor:
    """错误提取器，从检查结果中提取 ERROR 级别错误.

    支持从 TXT 格式或 JSON 格式的检查结果中提取错误信息，
    包括基于basedpyright和ruff的检查结果，
    生成按文件分组的结构化数据，用于自动化修复工作流。

    Examples:
        >>> from pathlib import Path
        >>> extractor = ErrorExtractor(txt_file=Path("results/check.txt"))
        >>> if extractor.load_file():
        ...     errors = extractor.extract_errors()
        ...     extractor.save_json(Path("results/errors.json"))
    """

    def __init__(
        self, txt_file: Path | None = None, json_file: Path | None = None,
        include_ruff: bool = False, results_dir: Path | None = None
    ):
        """初始化错误提取器.

        Args:
            txt_file: TXT 格式检查结果文件路径
            json_file: JSON 格式检查结果文件路径
            include_ruff: 是否包含ruff检查结果
            results_dir: 结果目录路径（用于查找ruff结果文件）

        Note:
            至少提供 txt_file 或 json_file 中的一个
        """
        self.txt_file = txt_file
        self.json_file = json_file
        self.include_ruff = include_ruff
        self.results_dir = results_dir
        self.txt_content = ""
        self.json_data: dict[str, Any] = {}
        self.ruff_data: dict[str, Any] = {}
        self.errors_by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def load_file(self) -> bool:
        """加载检查结果文件.

        优先加载 JSON 文件（结构化数据），如果未提供或失败，则尝试加载 TXT 文件。
        如果启用了ruff，还会加载ruff检查结果。

        Returns:
            是否成功加载文件
        """
        loaded_any = False

        # 加载 basedpyright JSON 文件（更可靠）
        if self.json_file and self.json_file.exists():
            try:
                self.json_data = json.loads(
                    self.json_file.read_text(encoding="utf-8")
                )
                print(f"[OK] Loaded basedpyright JSON file: {self.json_file}")
                loaded_any = True
            except Exception as e:
                print(f"WARNING: Cannot read JSON file {self.json_file}: {e}")

        # 尝试加载 basedpyright TXT 文件（备用）
        if self.txt_file and self.txt_file.exists():
            try:
                self.txt_content = self.txt_file.read_text(encoding="utf-8")
                print(f"[OK] Loaded basedpyright text file: {self.txt_file}")
                loaded_any = True
            except Exception as e:
                print(f"WARNING: Cannot read text file {self.txt_file}: {e}")

        # 加载 ruff 结果文件（如果启用）
        if self.include_ruff and self.results_dir:
            loaded_any |= self._load_ruff_results()

        return loaded_any

    def _load_ruff_results(self) -> bool:
        """加载ruff检查结果文件.

        Returns:
            是否成功加载ruff结果文件
        """
        try:
            # 查找最新的ruff JSON结果文件
            ruff_pattern = str(self.results_dir / "ruff_check_result_*.json")
            ruff_files = glob.glob(ruff_pattern)

            if not ruff_files:
                print("WARNING: No ruff result files found")
                return False

            # 选择最新的文件
            latest_ruff_file = max(ruff_files, key=lambda x: x.stat().st_mtime)
            ruff_path = Path(latest_ruff_file)

            try:
                with open(ruff_path, 'r', encoding='utf-8') as f:
                    self.ruff_data = json.load(f)
                print(f"[OK] Loaded ruff JSON file: {ruff_path}")
                return True
            except Exception as e:
                print(f"WARNING: Cannot read ruff JSON file {ruff_path}: {e}")
                return False

        except Exception as e:
            print(f"WARNING: Error loading ruff results: {e}")
            return False

    def extract_rule_from_message(self, message: str) -> str:
        """从错误消息中提取规则名称.

        从括号中提取规则名称，例如从 "message (reportArgumentType)" 中提取 "reportArgumentType"。

        Args:
            message: 错误消息

        Returns:
            规则名称，如果找不到则返回 'unknown'

        Examples:
            >>> extractor = ErrorExtractor()
            >>> extractor.extract_rule_from_message('Invalid type (reportArgumentType)')
            'reportArgumentType'
            >>> extractor.extract_rule_from_message('Unknown error')
            'unknown'
        """
        rule_match = re.search(r"\(([a-zA-Z]+)\)$", message)
        if rule_match:
            return rule_match.group(1)
        return "unknown"

    def parse_errors_from_text(self) -> None:
        """从 TXT 格式的文本中提取 ERROR 信息.

        从 basedpyright 的文本输出中解析错误行，格式例如：
        /path/to/file.py:123:45 - error: message (reportArgumentType)
        """
        if not self.txt_content:
            print("警告: 文件内容为空")
            return

        # 正则表达式匹配错误行
        # 格式: /path/to/file.py:line:col - error: message (rule)
        error_pattern = r"\s+(.+?):(\d+):(\d+)\s+-\s+error:\s+(.+)$"

        lines = self.txt_content.split("\n")
        match_count = 0

        for line in lines:
            # 跳过空行和不包含 error: 的行
            if not line.strip() or " - error:" not in line:
                continue

            # 尝试匹配错误行
            match = re.match(error_pattern, line)
            if match:
                file_path = match.group(1).strip()
                line_num = int(match.group(2))
                col_num = int(match.group(3))
                error_msg = match.group(4).strip()

                # 创建错误对象
                error_item = {
                    "line": line_num,
                    "column": col_num,
                    "message": error_msg,
                    "rule": self.extract_rule_from_message(error_msg),
                }

                # 按文件分组
                self.errors_by_file[file_path].append(error_item)
                match_count += 1

        print(f"[OK] Parsed {match_count} errors from text")

    def parse_errors_from_json(self) -> None:
        """从 JSON 格式的数据中提取 ERROR 信息.

        从 basedpyright 的 JSON 输出中提取严重级别为 'error' 的诊断信息。
        """
        if not self.json_data or "generalDiagnostics" not in self.json_data:
            print("警告: JSON 数据为空或不包含诊断信息")
            return

        error_count = 0

        for diagnostic in self.json_data["generalDiagnostics"]:
            if diagnostic.get("severity") == "error":
                file_path = diagnostic.get("file", "unknown")

                # 提取位置信息
                range_info = diagnostic.get("range", {})
                start_info = range_info.get("start", {})

                error_item = {
                    "line": start_info.get("line", 0) + 1,  # basedpyright 使用 0-based 行号
                    "column": start_info.get("character", 0) + 1,
                    "message": diagnostic.get("message", ""),
                    "rule": diagnostic.get("rule", "unknown"),
                }

                # 按文件分组
                self.errors_by_file[file_path].append(error_item)
                error_count += 1

        print(f"[OK] Extracted {error_count} errors from JSON")

    def parse_errors_from_ruff(self) -> None:
        """从ruff JSON格式的数据中提取错误信息.

        从ruff的JSON输出中提取错误信息，ruff主要使用error级别。
        """
        if not self.ruff_data or "issues" not in self.ruff_data:
            print("警告: ruff数据为空或不包含问题信息")
            return

        error_count = 0

        for issue in self.ruff_data["issues"]:
            # ruff主要使用error级别，但也有其他级别
            if issue.get("severity") in ["error", "warning"]:
                file_path = issue.get("filename", "unknown")

                # 提取位置信息
                location = issue.get("location", {})
                line_num = location.get("row", 0)
                col_num = location.get("column", 0)

                # 构建错误项
                error_item = {
                    "line": line_num,
                    "column": col_num,
                    "message": issue.get("message", ""),
                    "rule": issue.get("code", "unknown"),
                    "tool": "ruff",
                    "fixable": bool(issue.get("fix"))
                }

                # 按文件分组
                self.errors_by_file[file_path].append(error_item)
                error_count += 1

        print(f"[OK] Extracted {error_count} issues from ruff")

    def extract_errors(self) -> dict[str, Any]:
        """提取错误并返回结构化数据.

        从已加载的文件中提取所有 ERROR 级别错误，包括basedpyright和ruff的结果，
        生成按文件分组的数据结构。

        Returns:
            包含错误信息的字典:
            {
                "metadata": {
                    "source_file": "path/to/source",
                    "extraction_time": "2025-11-29T20:30:00",
                    "total_files_with_errors": 5,
                    "total_errors": 15,
                    "tools": ["basedpyright", "ruff"]
                },
                "errors_by_file": [
                    {
                        "file": "src/module.py",
                        "error_count": 3,
                        "errors_by_rule": {"reportArgumentType": 2},
                        "errors_by_tool": {"basedpyright": 2, "ruff": 1},
                        "errors": [...]
                    }
                ]
            }
        """
        # 清空之前的数据
        self.errors_by_file.clear()

        # 根据可用数据提取错误
        if self.json_data:
            self.parse_errors_from_json()
        elif self.txt_content:
            self.parse_errors_from_text()

        # 提取ruff错误（如果启用）
        if self.include_ruff and self.ruff_data:
            self.parse_errors_from_ruff()

        # 构建返回结构
        total_files = len(self.errors_by_file)
        total_errors = sum(len(errors) for errors in self.errors_by_file.values())

        # 转换 errors_by_file 为列表格式
        errors_list = []
        for file_path, errors in sorted(self.errors_by_file.items()):
            # 统计该文件的错误分布
            error_count = len(errors)
            rules_count: dict[str, int] = defaultdict(int)
            tools_count: dict[str, int] = defaultdict(int)

            for error in errors:
                rules_count[error["rule"]] += 1
                tool = error.get("tool", "basedpyright")
                tools_count[tool] += 1

            errors_list.append(
                {
                    "file": file_path,
                    "error_count": error_count,
                    "errors_by_rule": dict(rules_count),
                    "errors_by_tool": dict(tools_count),
                    "errors": errors,
                }
            )

        # 构建source文件信息
        source_files = []
        if self.json_file:
            source_files.append(str(self.json_file))
        if self.txt_file:
            source_files.append(str(self.txt_file))
        if self.include_ruff and self.ruff_data:
            source_files.append("ruff_results")

        source_file = ", ".join(source_files) if source_files else "unknown"

        # 构建工具列表
        tools = ["basedpyright"]
        if self.include_ruff and self.ruff_data:
            tools.append("ruff")

        result = {
            "metadata": {
                "source_file": source_file,
                "extraction_time": datetime.now().isoformat(),
                "total_files_with_errors": total_files,
                "total_errors": total_errors,
                "tools": tools,
            },
            "errors_by_file": errors_list,
        }

        return result

    def save_json(self, output_file: Path, data: dict[str, Any] | None = None) -> None:
        """保存错误数据到 JSON 文件.

        Args:
            output_file: 输出文件路径
            data: 错误数据（如果为 None，则调用 extract_errors() 获取）
        """
        if data is None:
            data = self.extract_errors()

        # 确保输出目录存在
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 保存为 JSON
        output_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        print(f"[OK] JSON file saved: {output_file}")

        # 显示统计信息
        metadata = data["metadata"]
        print("\n错误统计:")
        print(f"  有错误的文件数: {metadata['total_files_with_errors']}")
        print(f"  错误总数: {metadata['total_errors']}")

        # 显示前5个文件的错误分布
        if data["errors_by_file"]:
            print("\n错误最多的文件 (Top 5):")
            sorted_files = sorted(
                data["errors_by_file"],
                key=lambda x: x["error_count"],
                reverse=True,
            )[:5]

            for i, file_entry in enumerate(sorted_files, 1):
                print(f"  {i}. {file_entry['file']}: {file_entry['error_count']} 个错误")
