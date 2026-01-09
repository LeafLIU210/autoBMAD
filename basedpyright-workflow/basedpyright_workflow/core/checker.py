"""类型检查核心模块.

提供基于 basedpyright 的类型检查功能，支持生成 TXT 和 JSON 输出。
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ..utils.scanner import get_python_files


class TypeChecker:
    """BasedPyright 类型检查器.

    提供统一的类型检查接口，支持生成文本和JSON格式的检查结果。

    Examples:
        >>> from pathlib import Path
        >>> checker = TypeChecker(Path("src"), Path("results"))
        >>> result = checker.run_check()
        >>> "txt_file" in result
        True
    """

    def __init__(self, source_dir: Path, output_dir: Path):
        """初始化类型检查器.

        Args:
            source_dir: 源代码目录
            output_dir: 输出结果目录

        Raises:
            NotADirectoryError: 如果 source_dir 不是目录
        """
        if not source_dir.exists():
            raise FileNotFoundError(f"源目录不存在: {source_dir}")

        if not source_dir.is_dir():
            raise NotADirectoryError(f"路径不是目录: {source_dir}")

        self.source_dir = source_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def scan_files(self) -> List[Path]:
        """扫描源代码目录中的所有 Python 文件.

        Returns:
            Python 文件路径列表（已排序）
        """
        return get_python_files(self.source_dir)

    def run_text_check(self, python_files: List[Path]) -> subprocess.CompletedProcess:
        """运行 basedpyright 文本格式检查.

        Args:
            python_files: Python 文件列表（用于统计）

        Returns:
            subprocess.CompletedProcess 对象

        Raises:
            FileNotFoundError: 如果 basedpyright 命令不存在
            subprocess.CalledProcessError: 如果检查失败
        """
        try:
            return subprocess.run(
                ["basedpyright", str(self.source_dir)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,  # 允许错误退出码
            )
        except FileNotFoundError:
            raise FileNotFoundError(
                "未找到 basedpyright 命令，请安装: pip install basedpyright"
            )

    def run_json_check(self) -> subprocess.CompletedProcess:
        """运行 basedpyright JSON 格式检查.

        Returns:
            subprocess.CompletedProcess 对象

        Raises:
            FileNotFoundError: 如果 basedpyright 命令不存在
        """
        try:
            return subprocess.run(
                ["basedpyright", str(self.source_dir), "--outputjson"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
        except FileNotFoundError:
            raise FileNotFoundError(
                "未找到 basedpyright 命令，请安装: pip install basedpyright"
            )

    def parse_json_output(self, output: str, python_files: List[Path]) -> Dict[str, Any] | None:
        """解析 basedpyright JSON 输出.

        Args:
            output: JSON 字符串
            python_files: Python 文件列表（用于元数据）

        Returns:
            解析后的字典，如果解析失败返回 None
        """
        if not output or not output.strip():
            return None

        try:
            data = json.loads(output)

            # 添加元数据
            try:
                file_paths = [str(f.relative_to(Path.cwd())) for f in python_files]
            except ValueError:
                # 如果无法获取相对路径，使用绝对路径
                file_paths = [str(f) for f in python_files]

            data['metadata'] = {
                'check_time': datetime.now().isoformat(),
                'check_directory': str(self.source_dir),
                'python_files_count': len(python_files),
                'python_files': file_paths
            }

            return data
        except json.JSONDecodeError:
            return None

    def save_text_output(
        self,
        result: subprocess.CompletedProcess,
        python_files: List[Path],
        output_file: Path
    ) -> None:
        """保存文本格式检查结果到文件.

        Args:
            result: subprocess 结果对象
            python_files: Python 文件列表
            output_file: 输出文件路径
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("BasedPyright 检查结果\n")
            f.write("=" * 80 + "\n")
            f.write(f"检查时间: {timestamp}\n")
            f.write(f"检查目录: {self.source_dir}\n")
            f.write(f"Python文件数量: {len(python_files)}\n")
            f.write("=" * 80 + "\n\n")

            # 写入所有检查的文件列表
            f.write("检查的文件列表:\n")
            f.write("-" * 80 + "\n")
            for i, py_file in enumerate(python_files, 1):
                try:
                    rel_path = py_file.relative_to(Path.cwd())
                except ValueError:
                    rel_path = py_file
                f.write(f"{i:3d}. {rel_path}\n")
            f.write("-" * 80 + "\n\n")

            # 写入检查结果
            f.write("检查输出结果:\n")
            f.write("=" * 80 + "\n")
            f.write(result.stdout)
            f.write("\n")

            if result.stderr:
                f.write("\n错误信息:\n")
                f.write("=" * 80 + "\n")
                f.write(result.stderr)
                f.write("\n")

    def save_json_output(self, data: Dict[str, Any], output_file: Path) -> None:
        """保存 JSON 格式检查结果到文件.

        Args:
            data: JSON 数据字典
            output_file: 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def count_errors(self, stdout: str) -> tuple[int, int, int]:
        """从文本输出中统计错误、警告和信息数量.

        Args:
            stdout: basedpyright 的标准输出

        Returns:
            (error_count, warning_count, info_count) 元组
        """
        error_count = stdout.count(' error:')
        warning_count = stdout.count(' warning:')
        info_count = stdout.count(' information:')
        return error_count, warning_count, info_count

    def run_check(self) -> Dict[str, Any]:
        """运行完整的类型检查流程.

        执行以下步骤：
        1. 扫描 Python 文件
        2. 运行文本格式检查
        3. 运行 JSON 格式检查
        4. 保存结果到文件
        5. 返回检查结果字典

        Returns:
            检查结果字典，包含：
            - txt_file: 文本结果文件路径
            - json_file: JSON 结果文件路径
            - python_files: Python 文件列表
            - error_count: 错误数量
            - warning_count: 警告数量
            - info_count: 信息数量
            - json_data: 解析后的 JSON 数据

        Raises:
            FileNotFoundError: 如果 basedpyright 未安装
        """
        print("开始运行 BasedPyright 检查...")
        print(f"检查目录: {self.source_dir}")
        print("=" * 80)

        # 扫描 Python 文件
        python_files = self.scan_files()
        print(f"找到 {len(python_files)} 个 Python 文件")
        print("-" * 80)

        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 运行文本格式检查
        print("运行文本格式检查...")
        result_text = self.run_text_check(python_files)

        # 保存文本输出
        txt_file = self.output_dir / f"basedpyright_check_result_{timestamp}.txt"
        self.save_text_output(result_text, python_files, txt_file)

        # 运行 JSON 格式检查
        print("运行 JSON 格式检查...")
        result_json = self.run_json_check()
        json_data = self.parse_json_output(result_json.stdout, python_files)

        # 保存 JSON 输出
        json_file = self.output_dir / f"basedpyright_check_result_{timestamp}.json"
        if json_data:
            self.save_json_output(json_data, json_file)
            print(f"JSON 结果已保存到: {json_file}")
        else:
            print("警告: JSON 输出为空或解析失败")

        # 统计错误
        error_count, warning_count, info_count = self.count_errors(result_text.stdout)

        # 打印完成信息
        print("\n" + "=" * 80)
        print("检查完成统计:")
        print("-" * 80)
        print(f"检查文件数: {len(python_files)}")
        print(f"错误 (Error): {error_count}")
        print(f"警告 (Warning): {warning_count}")
        print(f"信息 (Information): {info_count}")

        if json_data and 'summary' in json_data:
            summary = json_data['summary']
            print("\n详细统计 (来自 JSON):")
            print(f"  分析文件数: {summary.get('filesAnalyzed', 0)}")
            print(f"  错误数: {summary.get('errorCount', 0)}")
            print(f"  警告数: {summary.get('warningCount', 0)}")
            print(f"  信息数: {summary.get('informationCount', 0)}")
            print(f"  检查耗时: {summary.get('timeInSec', 0):.2f} 秒")

        print("=" * 80)

        return {
            'txt_file': txt_file,
            'json_file': json_file,
            'python_files': python_files,
            'error_count': error_count,
            'warning_count': warning_count,
            'info_count': info_count,
            'json_data': json_data,
        }
