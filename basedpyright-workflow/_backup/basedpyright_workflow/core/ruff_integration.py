"""Ruff集成核心模块

提供ruff与basedpyright工作流的集成功能，包括：
- Ruff检查器执行
- 结果格式转换和整合
- 冲突解决策略
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import tempfile
import shutil

from ..config.settings import RuffConfig
from ..utils.ruff_utils import (
    run_ruff_check, run_ruff_format,
    parse_ruff_json_output, convert_ruff_to_pyright_format,
    generate_ruff_config, RuffNotInstalledError, RuffExecutionError
)


class RuffIntegrator:
    """Ruff集成器，负责ruff的执行和输出解析"""

    def __init__(self, config: RuffConfig, source_dir: Path, output_dir: Path):
        """初始化ruff集成器

        Args:
            config: ruff配置
            source_dir: 源代码目录
            output_dir: 输出目录
        """
        self.config = config
        self.source_dir = source_dir
        self.output_dir = output_dir
        self._config_file: Optional[Path] = None

    def _prepare_config_file(self) -> Path:
        """准备ruff配置文件

        Returns:
            Path: 配置文件路径
        """
        if self._config_file is None:
            config_dict = {
                "line_length": self.config.line_length,
                "target_version": self.config.target_version,
                "select_rules": self.config.select_rules,
                "ignore_rules": self.config.ignore_rules,
                "extend_exclude": self.config.extend_exclude,
                "preview": self.config.preview,
                "fix_only": self.config.fix_only
            }

            # 使用临时目录创建配置文件
            temp_dir = Path(tempfile.mkdtemp(prefix="ruff_config_"))
            self._config_file = generate_ruff_config(config_dict, temp_dir / "ruff.toml")

        return self._config_file

    def run_check(self, fix: bool = False, dry_run: bool = False) -> Dict[str, Any]:
        """运行ruff检查

        Args:
            fix: 是否应用自动修复
            dry_run: 是否仅预览修复（不实际应用）

        Returns:
            Dict[str, Any]: 检查结果
        """
        if not self.config.check_enabled:
            return {
                "version": "ruff",
                "totalFiles": 0,
                "errors": 0,
                "warnings": 0,
                "time": "0s",
                "files": [],
                "summary": {"error_count": 0, "warning_count": 0, "fixable_count": 0},
                "tool": "ruff",
                "enabled": False
            }

        try:
            config_file = self._prepare_config_file()

            # 构建配置字典用于执行
            config_dict = {
                "timeout_seconds": 300,
                "extend_exclude": self.config.extend_exclude,
                "preview": self.config.preview
            }

            returncode, stdout, stderr = run_ruff_check(
                source_dir=self.source_dir,
                config=config_dict,
                output_format="json",
                fix=fix and not dry_run,
                fix_only=self.config.fix_only if (fix and not dry_run) else None,
                config_file=config_file
            )

            # 解析结果
            ruff_result = parse_ruff_json_output(stdout)

            # 转换为basedpyright格式
            converted_result = convert_ruff_to_pyright_format(ruff_result)
            converted_result["returncode"] = returncode
            converted_result["stderr"] = stderr
            converted_result["fix_applied"] = fix and not dry_run
            converted_result["dry_run"] = dry_run

            return converted_result

        except RuffNotInstalledError as e:
            return {
                "error": str(e),
                "tool": "ruff",
                "enabled": True,
                "execution_failed": True
            }
        except RuffExecutionError as e:
            return {
                "error": str(e),
                "tool": "ruff",
                "enabled": True,
                "execution_failed": True
            }

    def preview_fixes(self) -> Dict[str, Any]:
        """预览可修复的问题

        Returns:
            Dict[str, Any]: 修复预览结果
        """
        check_result = self.run_check(fix=False, dry_run=True)

        if check_result.get("execution_failed"):
            return check_result

        # 统计可修复的问题
        fixable_issues = []
        total_fixable = 0

        for file_data in check_result.get("files", []):
            file_fixable = []
            for issue in file_data.get("errors", []):
                if issue.get("fix"):
                    file_fixable.append({
                        "line": issue["range"]["start"]["line"] + 1,
                        "column": issue["range"]["start"]["character"] + 1,
                        "message": issue["message"],
                        "code": issue["code"],
                        "fix": issue["fix"]
                    })
                    total_fixable += 1

            if file_fixable:
                fixable_issues.append({
                    "file": file_data["file"],
                    "fixable_count": len(file_fixable),
                    "issues": file_fixable
                })

        return {
            "total_fixable": total_fixable,
            "files_with_fixes": len(fixable_issues),
            "fixable_details": fixable_issues,
            "summary": check_result.get("summary", {}),
            "tool": "ruff",
            "enabled": True
        }

    def apply_fixes(self, rules: Optional[List[str]] = None, unsafe: bool = None) -> Dict[str, Any]:
        """应用ruff自动修复

        Args:
            rules: 指定要修复的规则列表，None表示修复所有
            unsafe: 是否应用unsafe修复，None表示使用配置值

        Returns:
            Dict[str, Any]: 修复结果
        """
        if not self.config.fix_enabled:
            return {
                "fixed": False,
                "message": "ruff修复功能已禁用",
                "tool": "ruff",
                "enabled": False
            }

        # 先预览修复
        preview_result = self.preview_fixes()

        if preview_result.get("total_fixable", 0) == 0:
            return {
                "fixed": False,
                "message": "没有可自动修复的问题",
                "tool": "ruff",
                "enabled": True
            }

        try:
            config_file = self._prepare_config_file()

            # 构建修复配置
            config_dict = {
                "timeout_seconds": 300,
                "extend_exclude": self.config.extend_exclude,
                "preview": self.config.preview
            }

            # 使用指定的规则或配置的fix_only规则
            fix_rules = rules or self.config.fix_only
            use_unsafe = unsafe if unsafe is not None else self.config.unsafe_fixes

            returncode, stdout, stderr = run_ruff_check(
                source_dir=self.source_dir,
                config=config_dict,
                output_format="json",
                fix=True,
                fix_only=fix_rules,
                config_file=config_file
            )

            # 解析修复后结果
            after_fix_result = parse_ruff_json_output(stdout)

            # 统计修复效果
            before_count = preview_result.get("total_fixable", 0)
            after_fix_result_data = convert_ruff_to_pyright_format(after_fix_result)

            return {
                "fixed": True,
                "before_count": before_count,
                "after_count": after_fix_result_data.get("errors", 0),
                "fixed_count": max(0, before_count - after_fix_result_data.get("errors", 0)),
                "rules_used": fix_rules or ["all"],
                "unsafe_used": use_unsafe,
                "returncode": returncode,
                "stdout": stdout,
                "stderr": stderr,
                "after_result": after_fix_result_data,
                "tool": "ruff",
                "enabled": True
            }

        except (RuffNotInstalledError, RuffExecutionError) as e:
            return {
                "error": str(e),
                "tool": "ruff",
                "enabled": True,
                "execution_failed": True
            }

    def run_format_check(self) -> Dict[str, Any]:
        """运行ruff格式化检查（不修改文件）

        Returns:
            Dict[str, Any]: 格式化检查结果
        """
        if not self.config.format_enabled:
            return {
                "needs_formatting": False,
                "files": [],
                "tool": "ruff-format",
                "enabled": False
            }

        try:
            config_file = self._prepare_config_file()

            config_dict = {
                "timeout_seconds": 300,
                "extend_exclude": self.config.extend_exclude
            }

            returncode, stdout, stderr = run_ruff_format(
                source_dir=self.source_dir,
                config=config_dict,
                check_only=True,
                config_file=config_file
            )

            # ruff format --check 返回0表示无需格式化，1表示需要格式化
            needs_formatting = returncode != 0

            # 解析文件列表（从标准输出中提取）
            files_needing_format = []
            format_diffs = {}

            if stdout:
                for line in stdout.strip().split('\n'):
                    if line.strip():
                        if line.startswith('---') or line.startswith('+++'):
                            # 处理diff格式输出
                            continue
                        elif ':' in line and len(line.split(':')) >= 2:
                            # 可能是文件路径
                            file_path = line.strip()
                            if file_path and not file_path.startswith('All files'):
                                files_needing_format.append(file_path)

            # 如果有格式化差异，尝试生成更详细的报告
            if needs_formatting and files_needing_format:
                format_diffs = self._generate_format_diffs(files_needing_format)

            return {
                "needs_formatting": needs_formatting,
                "files": files_needing_format,
                "diffs": format_diffs,
                "returncode": returncode,
                "stdout": stdout,
                "stderr": stderr,
                "tool": "ruff-format",
                "enabled": True
            }

        except (RuffNotInstalledError, RuffExecutionError) as e:
            return {
                "error": str(e),
                "tool": "ruff-format",
                "enabled": True,
                "execution_failed": True
            }

    def _generate_format_diffs(self, files: List[str]) -> Dict[str, str]:
        """生成格式化差异报告

        Args:
            files: 需要格式化的文件列表

        Returns:
            Dict[str, str]: 文件到差异内容的映射
        """
        diffs = {}

        try:
            # 对每个文件生成格式化差异
            from ..utils.ruff_utils import run_ruff_format

            for file_path in files[:10]:  # 限制处理文件数量，避免过长时间
                full_path = self.source_dir / file_path
                if not full_path.exists():
                    continue

                config_file = self._prepare_config_file()
                config_dict = {
                    "timeout_seconds": 30,  # 短超时
                    "extend_exclude": self.config.extend_exclude
                }

                # 生成差异
                returncode, stdout, stderr = run_ruff_format(
                    source_dir=full_path.parent,
                    config=config_dict,
                    diff=True,
                    config_file=config_file
                )

                if returncode != 0 and stdout:
                    diffs[file_path] = stdout

        except Exception:
            # 如果生成差异失败，忽略错误继续处理其他文件
            pass

        return diffs

    def apply_formatting(self) -> Dict[str, Any]:
        """应用ruff格式化

        Returns:
            Dict[str, Any]: 格式化结果
        """
        if not self.config.format_enabled:
            return {
                "formatted": False,
                "files": [],
                "tool": "ruff-format",
                "enabled": False
            }

        try:
            config_file = self._prepare_config_file()

            config_dict = {
                "timeout_seconds": 300,
                "extend_exclude": self.config.extend_exclude
            }

            returncode, stdout, stderr = run_ruff_format(
                source_dir=self.source_dir,
                config=config_dict,
                check_only=False,
                config_file=config_file
            )

            # 解析格式化的文件
            formatted_files = []
            changed_files_count = 0

            if stdout:
                for line in stdout.strip().split('\n'):
                    line = line.strip()
                    if line:
                        if "files" in line.lower() and "formatted" in line.lower():
                            # 尝试从类似 "5 files formatted" 的行中提取数量
                            try:
                                changed_files_count = int(line.split()[0])
                            except (ValueError, IndexError):
                                pass
                        elif line.endswith('.py') or line.endswith('.pyi'):
                            # 可能是文件路径
                            formatted_files.append(line)

            return {
                "formatted": True,
                "files": formatted_files,
                "files_count": changed_files_count,
                "returncode": returncode,
                "stdout": stdout,
                "stderr": stderr,
                "tool": "ruff-format",
                "enabled": True
            }

        except (RuffNotInstalledError, RuffExecutionError) as e:
            return {
                "error": str(e),
                "tool": "ruff-format",
                "enabled": True,
                "execution_failed": True
            }

    def format_and_check(self) -> Dict[str, Any]:
        """格式化代码并验证结果

        Returns:
            Dict[str, Any]: 格式化和验证结果
        """
        # 先检查是否需要格式化
        check_result = self.run_format_check()

        if not check_result.get("enabled", False):
            return check_result

        if not check_result.get("needs_formatting", False):
            return {
                "formatted": False,
                "files": [],
                "verification": "passed",
                "message": "代码格式良好，无需格式化",
                "tool": "ruff-format",
                "enabled": True
            }

        # 应用格式化
        format_result = self.apply_formatting()

        if format_result.get("execution_failed"):
            return {
                "formatted": False,
                "verification": "failed",
                "error": format_result.get("error", "格式化执行失败"),
                "tool": "ruff-format",
                "enabled": True
            }

        # 验证格式化结果
        verification_result = self.run_format_check()

        return {
            "formatted": True,
            "files": format_result.get("files", []),
            "files_count": format_result.get("files_count", 0),
            "verification": "passed" if not verification_result.get("needs_formatting", False) else "failed",
            "pre_check_files": check_result.get("files", []),
            "post_check_needs_formatting": verification_result.get("needs_formatting", False),
            "tool": "ruff-format",
            "enabled": True
        }

    def save_results(self, results: Dict[str, Any], timestamp: str) -> Tuple[Path, Path]:
        """保存ruff结果

        Args:
            results: 检查结果
            timestamp: 时间戳

        Returns:
            Tuple[Path, Path]: (JSON文件路径, 文本文件路径)
        """
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        base_name = f"ruff_check_result_{timestamp}"
        json_file = self.output_dir / f"{base_name}.json"
        txt_file = self.output_dir / f"{base_name}.txt"

        # 保存JSON结果
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存ruff JSON结果失败: {e}")

        # 保存文本结果
        try:
            with open(txt_file, 'w', encoding='utf-8') as f:
                self._write_text_results(results, f)
        except Exception as e:
            print(f"保存ruff文本结果失败: {e}")

        return json_file, txt_file

    def _write_text_results(self, results: Dict[str, Any], file) -> None:
        """写入文本格式结果

        Args:
            results: 检查结果
            file: 文件对象
        """
        file.write("Ruff检查结果\n")
        file.write(f"{'='*50}\n")
        file.write(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"源目录: {self.source_dir}\n\n")

        if results.get("execution_failed"):
            file.write(f"执行失败: {results.get('error', '未知错误')}\n")
            return

        if not results.get("enabled", True):
            file.write("Ruff检查已禁用\n")
            return

        # 写入统计信息
        summary = results.get("summary", {})
        file.write("统计信息:\n")
        file.write(f"  总问题数: {summary.get('total_count', 0)}\n")
        file.write(f"  错误数: {summary.get('error_count', 0)}\n")
        file.write(f"  警告数: {summary.get('warning_count', 0)}\n")
        file.write(f"  可自动修复: {summary.get('fixable_count', 0)}\n")
        file.write(f"  检查文件数: {results.get('totalFiles', 0)}\n")

        if results.get("fix_applied"):
            file.write("  已应用自动修复\n")

        file.write("\n")

        # 写入文件详情
        files_data = results.get("files", [])
        if files_data:
            file.write("文件详情:\n")
            file.write(f"{'-'*50}\n")

            for file_data in files_data:
                file_path = file_data.get("file", "")
                errors = file_data.get("errors", [])
                warnings = file_data.get("warnings", [])

                if errors or warnings:
                    file.write(f"\n文件: {file_path}\n")

                    if errors:
                        file.write(f"  错误 ({len(errors)}):\n")
                        for error in errors:
                            line_num = error.get("range", {}).get("start", {}).get("line", 0) + 1
                            col_num = error.get("range", {}).get("start", {}).get("character", 0) + 1
                            message = error.get("message", "")
                            code = error.get("code", "")
                            file.write(f"    第{line_num}行第{col_num}列: [{code}] {message}\n")

                    if warnings:
                        file.write(f"  警告 ({len(warnings)}):\n")
                        for warning in warnings:
                            line_num = warning.get("range", {}).get("start", {}).get("line", 0) + 1
                            col_num = warning.get("range", {}).get("start", {}).get("character", 0) + 1
                            message = warning.get("message", "")
                            code = warning.get("code", "")
                            file.write(f"    第{line_num}行第{col_num}列: [{code}] {message}\n")
        else:
            file.write("未发现问题，代码质量良好！\n")

    def cleanup(self) -> None:
        """清理临时文件"""
        if self._config_file and self._config_file.exists():
            try:
                shutil.rmtree(self._config_file.parent)
            except Exception:
                pass


class ResultMerger:
    """结果合并器，整合basedpyright和ruff的结果"""

    def __init__(self):
        """初始化结果合并器"""
        pass

    def merge_results(
        self,
        basedpyright_result: Dict[str, Any],
        ruff_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """合并两个工具的检查结果

        Args:
            basedpyright_result: basedpyright检查结果
            ruff_result: ruff检查结果

        Returns:
            Dict[str, Any]: 合并后的结果
        """
        # 检查是否有执行失败
        if basedpyright_result.get("execution_failed") and ruff_result.get("execution_failed"):
            return {
                "execution_failed": True,
                "error": "Both tools failed to execute",
                "basedpyright_error": basedpyright_result.get("error"),
                "ruff_error": ruff_result.get("error")
            }

        # 合并基础统计信息
        merged_result = {
            "version": "basedpyright+ruff",
            "totalFiles": 0,
            "errors": 0,
            "warnings": 0,
            "time": "0s",
            "files": [],
            "tools": {
                "basedpyright": {
                    "enabled": True,
                    "execution_failed": basedpyright_result.get("execution_failed", False)
                },
                "ruff": {
                    "enabled": ruff_result.get("enabled", True),
                    "execution_failed": ruff_result.get("execution_failed", False)
                }
            }
        }

        # 合并文件和问题
        merged_files = {}

        # 处理basedpyright结果
        if not basedpyright_result.get("execution_failed"):
            merged_result["tools"]["basedpyright"]["errors"] = basedpyright_result.get("errors", 0)
            merged_result["tools"]["basedpyright"]["warnings"] = basedpyright_result.get("warnings", 0)
            merged_result["tools"]["basedpyright"]["files"] = basedpyright_result.get("totalFiles", 0)

            for file_data in basedpyright_result.get("files", []):
                file_path = file_data.get("file", "")
                if file_path:
                    if file_path not in merged_files:
                        merged_files[file_path] = {
                            "file": file_path,
                            "errors": [],
                            "warnings": []
                        }

                    # 添加工具来源标记
                    for error in file_data.get("errors", []):
                        error_copy = error.copy()
                        error_copy["tool"] = "basedpyright"
                        merged_files[file_path]["errors"].append(error_copy)

                    for warning in file_data.get("warnings", []):
                        warning_copy = warning.copy()
                        warning_copy["tool"] = "basedpyright"
                        merged_files[file_path]["warnings"].append(warning_copy)

        # 处理ruff结果
        if not ruff_result.get("execution_failed") and ruff_result.get("enabled", True):
            merged_result["tools"]["ruff"]["errors"] = ruff_result.get("errors", 0)
            merged_result["tools"]["ruff"]["warnings"] = ruff_result.get("warnings", 0)
            merged_result["tools"]["ruff"]["files"] = ruff_result.get("totalFiles", 0)

            for file_data in ruff_result.get("files", []):
                file_path = file_data.get("file", "")
                if file_path:
                    if file_path not in merged_files:
                        merged_files[file_path] = {
                            "file": file_path,
                            "errors": [],
                            "warnings": []
                        }

                    # 添加工具来源标记
                    for error in file_data.get("errors", []):
                        error_copy = error.copy()
                        error_copy["tool"] = "ruff"
                        merged_files[file_path]["errors"].append(error_copy)

                    for warning in file_data.get("warnings", []):
                        warning_copy = warning.copy()
                        warning_copy["tool"] = "ruff"
                        merged_files[file_path]["warnings"].append(warning_copy)

        # 统计总数
        merged_result["files"] = list(merged_files.values())
        merged_result["totalFiles"] = len(merged_files)
        merged_result["errors"] = sum(len(f["errors"]) for f in merged_files.values())
        merged_result["warnings"] = sum(len(f["warnings"]) for f in merged_files.values())

        # 合并时间信息
        bp_time = basedpyright_result.get("time", "0s")
        ruff_time = "0s"  # ruff很快，但可以估算
        merged_result["tool_times"] = {
            "basedpyright": bp_time,
            "ruff": ruff_time
        }

        return merged_result


class ConflictResolver:
    """冲突解决器，处理两个工具之间的建议冲突"""

    def __init__(self, strategy: str = "basedpyright_priority"):
        """初始化冲突解决器

        Args:
            strategy: 解决策略
                - "basedpyright_priority": basedpyright优先
                - "ruff_priority": ruff优先
                - "smart": 智能决策
        """
        self.strategy = strategy

    def resolve_conflicts(self, merged_result: Dict[str, Any]) -> Dict[str, Any]:
        """解决结果中的冲突

        Args:
            merged_result: 合并后的结果

        Returns:
            Dict[str, Any]: 解决冲突后的结果
        """
        if self.strategy == "basedpyright_priority":
            return self._basedpyright_priority(merged_result)
        elif self.strategy == "ruff_priority":
            return self._ruff_priority(merged_result)
        elif self.strategy == "smart":
            return self._smart_resolution(merged_result)
        else:
            return merged_result

    def _basedpyright_priority(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """basedpyright优先策略"""
        # 类型检查问题优先级最高，代码风格问题其次
        # 这里主要是标记优先级，实际处理在应用修复时
        result["conflict_strategy"] = "basedpyright_priority"
        return result

    def _ruff_priority(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """ruff优先策略"""
        # 代码风格和快速修复优先
        result["conflict_strategy"] = "ruff_priority"
        return result

    def _smart_resolution(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """智能解决策略"""
        # 根据问题类型自动选择最佳工具
        result["conflict_strategy"] = "smart"

        # 标记问题优先级
        for file_data in result.get("files", []):
            # 对错误按严重程度排序
            file_data["errors"].sort(key=self._error_priority_key)

        return result

    def _error_priority_key(self, error: Dict[str, Any]) -> Tuple[int, str]:
        """错误优先级排序键

        Args:
            error: 错误信息

        Returns:
            Tuple[int, str]: 排序键
        """
        tool = error.get("tool", "")
        severity = error.get("severity", "error")

        # 优先级：basedpyright类型错误 > ruff错误 > basedpyright警告 > ruff警告
        if tool == "basedpyright" and severity == "error":
            return (1, tool)
        elif tool == "ruff" and severity == "error":
            return (2, tool)
        elif tool == "basedpyright" and severity != "error":
            return (3, tool)
        else:
            return (4, tool)

    def get_fix_suggestions(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取修复建议

        Args:
            result: 检查结果

        Returns:
            List[Dict[str, Any]]: 修复建议列表
        """
        suggestions = []

        for file_data in result.get("files", []):
            file_path = file_data.get("file", "")

            # 收集所有问题
            all_issues = file_data.get("errors", []) + file_data.get("warnings", [])

            # 按工具分组
            basedpyright_issues = [i for i in all_issues if i.get("tool") == "basedpyright"]
            ruff_issues = [i for i in all_issues if i.get("tool") == "ruff"]

            # 生成修复建议
            if basedpyright_issues:
                suggestions.append({
                    "file": file_path,
                    "tool": "basedpyright",
                    "issues": basedpyright_issues,
                    "fix_type": "type_related",
                    "priority": "high"
                })

            if ruff_issues:
                # 检查是否有可自动修复的问题
                fixable_ruff = [i for i in ruff_issues if i.get("fix")]
                if fixable_ruff:
                    suggestions.append({
                        "file": file_path,
                        "tool": "ruff",
                        "issues": fixable_ruff,
                        "fix_type": "auto_fixable",
                        "priority": "medium",
                        "auto_fix": True
                    })

                # 非自动修复的问题
                non_fixable_ruff = [i for i in ruff_issues if not i.get("fix")]
                if non_fixable_ruff:
                    suggestions.append({
                        "file": file_path,
                        "tool": "ruff",
                        "issues": non_fixable_ruff,
                        "fix_type": "manual",
                        "priority": "low"
                    })

        return suggestions


class FixSuggestionMerger:
    """修复建议合并器，智能合并basedpyright和ruff的修复建议"""

    def __init__(self, strategy: str = "basedpyright_priority"):
        """初始化修复建议合并器

        Args:
            strategy: 解决策略
                - "basedpyright_priority": basedpyright优先
                - "ruff_priority": ruff优先
                - "smart": 智能决策
        """
        self.strategy = strategy

        # 定义问题严重程度排序
        self.severity_order = {
            "type_error": 5,      # BasedPyright类型错误 - 最高优先级
            "syntax_error": 4,    # 语法错误
            "import_error": 3,    # 导入错误
            "runtime_error": 3,   # 运行时错误
            "style_error": 2,     # Ruff风格错误
            "formatting_error": 1, # 格式化错误
            "warning": 1,         # 警告
        }

        # 定义工具优先级（用于相同严重程度的情况）
        self.tool_priority = {
            "basedpyright": 2,  # 类型检查优先级较高
            "ruff": 1,          # 代码检查优先级较低
        }

    def categorize_issue(self, issue: Dict[str, Any]) -> str:
        """对问题进行分类

        Args:
            issue: 问题信息

        Returns:
            str: 问题分类
        """
        tool = issue.get("tool", "basedpyright")
        rule = issue.get("rule", "").lower()
        message = issue.get("message", "").lower()

        # BasedPyright类型错误
        if tool == "basedpyright":
            if any(keyword in message for keyword in ["type", "argument", "return", "assignment"]):
                return "type_error"
            elif any(keyword in message for keyword in ["import", "module"]):
                return "import_error"
            elif "syntax" in message:
                return "syntax_error"
            else:
                return "runtime_error"

        # Ruff错误分类
        elif tool == "ruff":
            if rule.startswith("E"):
                if any(code in rule for code in ["E999", "E902", "E901"]):
                    return "syntax_error"
                elif rule in ["E401", "E402"]:
                    return "import_error"
                else:
                    return "style_error"
            elif rule.startswith("F"):
                # Pyflakes errors
                if "name" in message and "not defined" in message:
                    return "runtime_error"
                elif "import" in message:
                    return "import_error"
                else:
                    return "style_error"
            elif rule.startswith("B"):
                # Flake8-bugbear - 潜在运行时错误
                return "runtime_error"
            else:
                return "style_error"

        return "unknown"

    def calculate_priority(self, issue: Dict[str, Any]) -> tuple:
        """计算问题优先级

        Args:
            issue: 问题信息

        Returns:
            tuple: (严重程度, 工具优先级, 行号) 用于排序
        """
        category = self.categorize_issue(issue)
        severity = self.severity_order.get(category, 1)
        tool = issue.get("tool", "basedpyright")
        tool_priority = self.tool_priority.get(tool, 1)
        line_num = issue.get("line", 0)

        # 负数用于降序排序（高优先级在前）
        return (-severity, -tool_priority, line_num)

    def merge_fix_suggestions(self, basedpyright_result: Dict[str, Any], ruff_result: Dict[str, Any]) -> Dict[str, Any]:
        """合并两个工具的修复建议

        Args:
            basedpyright_result: basedpyright检查结果
            ruff_result: ruff检查结果

        Returns:
            Dict[str, Any]: 合并后的修复建议
        """
        all_suggestions = []

        # 收集basedpyright建议
        if not basedpyright_result.get("execution_failed"):
            bp_suggestions = self._extract_basedpyright_suggestions(basedpyright_result)
            all_suggestions.extend(bp_suggestions)

        # 收集ruff建议
        if not ruff_result.get("execution_failed") and ruff_result.get("enabled", True):
            ruff_suggestions = self._extract_ruff_suggestions(ruff_result)
            all_suggestions.extend(ruff_suggestions)

        # 按文件分组
        suggestions_by_file = {}
        for suggestion in all_suggestions:
            file_path = suggestion["file"]
            if file_path not in suggestions_by_file:
                suggestions_by_file[file_path] = []
            suggestions_by_file[file_path].append(suggestion)

        # 对每个文件的建议进行排序和去重
        for file_path in suggestions_by_file:
            suggestions = suggestions_by_file[file_path]

            # 按优先级排序
            suggestions.sort(key=self.calculate_priority)

            # 去重和冲突解决
            suggestions_by_file[file_path] = self._resolve_conflicts_in_file(suggestions)

        # 生成统计信息
        stats = self._generate_merge_statistics(all_suggestions)

        return {
            "merged_suggestions": suggestions_by_file,
            "statistics": stats,
            "total_files": len(suggestions_by_file),
            "total_suggestions": sum(len(suggestions) for suggestions in suggestions_by_file.values()),
            "strategy_used": self.strategy
        }

    def _extract_basedpyright_suggestions(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取basedpyright修复建议"""
        suggestions = []

        for file_data in result.get("files", []):
            file_path = file_data.get("file", "")
            for error in file_data.get("errors", []):
                suggestion = {
                    "file": file_path,
                    "line": error.get("range", {}).get("start", {}).get("line", 0) + 1,
                    "column": error.get("range", {}).get("start", {}).get("character", 0) + 1,
                    "message": error.get("message", ""),
                    "rule": error.get("rule", ""),
                    "tool": "basedpyright",
                    "fix_available": False,  # BasedPyright通常不提供自动修复
                    "category": self.categorize_issue({
                        "tool": "basedpyright",
                        "message": error.get("message", ""),
                        "rule": error.get("rule", "")
                    }),
                    "priority": self.calculate_priority({
                        "tool": "basedpyright",
                        "message": error.get("message", ""),
                        "rule": error.get("rule", ""),
                        "line": error.get("range", {}).get("start", {}).get("line", 0) + 1
                    })
                }
                suggestions.append(suggestion)

        return suggestions

    def _extract_ruff_suggestions(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取ruff修复建议"""
        suggestions = []

        for file_data in result.get("files", []):
            file_path = file_data.get("file", "")
            for error in file_data.get("errors", []):
                suggestion = {
                    "file": file_path,
                    "line": error.get("line", 0),
                    "column": error.get("column", 0),
                    "message": error.get("message", ""),
                    "rule": error.get("rule", ""),
                    "tool": "ruff",
                    "fix_available": error.get("fixable", False),
                    "fix_details": error.get("fix"),
                    "category": self.categorize_issue({
                        "tool": "ruff",
                        "message": error.get("message", ""),
                        "rule": error.get("rule", "")
                    }),
                    "priority": self.calculate_priority({
                        "tool": "ruff",
                        "message": error.get("message", ""),
                        "rule": error.get("rule", ""),
                        "line": error.get("line", 0)
                    })
                }
                suggestions.append(suggestion)

        return suggestions

    def _resolve_conflicts_in_file(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解决单个文件中的建议冲突"""
        if not suggestions:
            return suggestions

        # 按位置分组，查找可能的冲突
        position_groups = {}
        for suggestion in suggestions:
            key = (suggestion["line"], suggestion["column"])
            if key not in position_groups:
                position_groups[key] = []
            position_groups[key].append(suggestion)

        resolved_suggestions = []
        for position, group_suggestions in position_groups.items():
            if len(group_suggestions) == 1:
                # 没有冲突，直接添加
                resolved_suggestions.extend(group_suggestions)
            else:
                # 有冲突，需要解决
                resolved = self._resolve_position_conflicts(group_suggestions)
                resolved_suggestions.extend(resolved)

        return resolved_suggestions

    def _resolve_position_conflicts(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解决同一位置的冲突建议"""
        if len(suggestions) == 1:
            return suggestions

        # 按照策略解决冲突
        if self.strategy == "basedpyright_priority":
            # 优先保留basedpyright的建议
            basedpyright_suggestions = [s for s in suggestions if s["tool"] == "basedpyright"]
            ruff_suggestions = [s for s in suggestions if s["tool"] == "ruff"]

            if basedpyright_suggestions:
                # 如果有basedpyright建议，优先使用
                return basedpyright_suggestions + [s for s in ruff_suggestions if not self._overlaps_with(basedpyright_suggestions, s)]
            else:
                # 否则使用ruff建议中优先级最高的
                return [max(ruff_suggestions, key=lambda s: s["priority"])]

        elif self.strategy == "ruff_priority":
            # 优先保留ruff的建议
            ruff_suggestions = [s for s in suggestions if s["tool"] == "ruff"]
            basedpyright_suggestions = [s for s in suggestions if s["tool"] == "basedpyright"]

            if ruff_suggestions:
                # 如果有ruff建议，优先使用
                return ruff_suggestions + [s for s in basedpyright_suggestions if not self._overlaps_with(ruff_suggestions, s)]
            else:
                # 否则使用basedpyright建议
                return basedpyright_suggestions

        elif self.strategy == "smart":
            # 智能决策：根据问题类型和工具优势选择
            return self._smart_conflict_resolution(suggestions)

        return suggestions

    def _overlaps_with(self, primary_suggestions: List[Dict[str, Any]], suggestion: Dict[str, Any]) -> bool:
        """检查建议是否与主要建议重叠"""
        for primary in primary_suggestions:
            # 如果问题类型相同，认为重叠
            if primary["category"] == suggestion["category"]:
                return True
            # 如果规则相关，认为重叠
            if self._rules_are_related(primary["rule"], suggestion["rule"]):
                return True
        return False

    def _rules_are_related(self, rule1: str, rule2: str) -> bool:
        """检查两个规则是否相关"""
        # 简化的相关性检查
        if rule1 == rule2:
            return True

        # 导入相关的规则
        import_rules = {"F401", "F811", "E401", "E402", "F821"}
        if rule1 in import_rules and rule2 in import_rules:
            return True

        return False

    def _smart_conflict_resolution(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """智能冲突解决"""
        # 按优先级排序
        suggestions.sort(key=lambda s: s["priority"])

        # 保留最高优先级的建议
        primary = suggestions[0]
        result = [primary]

        # 检查其他建议是否可以保留
        for suggestion in suggestions[1:]:
            if not self._overlaps_with([primary], suggestion):
                result.append(suggestion)

        return result

    def _generate_merge_statistics(self, suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成合并统计信息"""
        stats = {
            "total_suggestions": len(suggestions),
            "by_tool": {"basedpyright": 0, "ruff": 0},
            "by_category": {},
            "auto_fixable": 0,
            "requires_manual_fix": 0
        }

        for suggestion in suggestions:
            tool = suggestion["tool"]
            category = suggestion["category"]
            fix_available = suggestion.get("fix_available", False)

            stats["by_tool"][tool] += 1
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

            if fix_available:
                stats["auto_fixable"] += 1
            else:
                stats["requires_manual_fix"] += 1

        return stats