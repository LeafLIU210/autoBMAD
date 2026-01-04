#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BasedPyright检查脚本 - 遍历src文件夹及其子文件夹的每一个Python文件
生成UTF-8格式的txt输出结果
"""

import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path


from typing import Any


def get_all_python_files(src_dir: Path) -> list[Path]:
    """
    递归获取src目录下所有Python文件
    
    Args:
        src_dir: 源代码目录路径
        
    Returns:
        Python文件路径列表
    """
    python_files = []
    for py_file in src_dir.rglob("*.py"):
        if not py_file.name.startswith('.'):  # 排除隐藏文件
            python_files.append(py_file)
    return sorted(python_files)


def run_basedpyright_check(src_dir: str = "src") -> dict[str, Any]:
    """
    运行basedpyright检查并生成结果
    
    Args:
        src_dir: 要检查的源代码目录
        
    Returns:
        检查结果字典
    """
    print("[Console]::OutputEncoding = [System.Text.Encoding]::UTF8")
    print("开始运行BasedPyright检查...")
    print(f"检查目录: {src_dir}")
    print("=" * 80)
    
    src_path = Path(src_dir)
    if not src_path.exists():
        print(f"错误: 目录 {src_dir} 不存在")
        sys.exit(1)
    
    # 获取所有Python文件
    python_files = get_all_python_files(src_path)
    print(f"找到 {len(python_files)} 个Python文件")
    print("-" * 80)
    
    # 生成时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 确定结果输出目录（相对于项目根目录）
    # 脚本可能从项目根目录或scripts目录运行
    script_dir = Path(__file__).parent
    if script_dir.name == 'scripts':
        # 从scripts目录运行，结果保存到 ../results/
        results_dir = script_dir.parent / 'results'
    else:
        # 从项目根目录运行，结果保存到 basedpyright-workflow/results/
        results_dir = Path('basedpyright-workflow/results')
    
    # 确保结果目录存在
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # 输出文件路径
    txt_output_file = results_dir / f"basedpyright_check_result_{timestamp}.txt"
    json_output_file = results_dir / f"basedpyright_check_result_{timestamp}.json"
    
    # 运行basedpyright检查（文本格式）
    print("运行文本格式检查...")
    try:
        result_text = subprocess.run(
            ["basedpyright", src_dir],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # 保存文本输出
        with open(txt_output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("BasedPyright 检查结果\n")
            f.write("=" * 80 + "\n")
            f.write(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"检查目录: {src_dir}\n")
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
            f.write(result_text.stdout)
            f.write("\n")
            
            if result_text.stderr:
                f.write("\n错误信息:\n")
                f.write("=" * 80 + "\n")
                f.write(result_text.stderr)
                f.write("\n")
        
        print(f"[OK] Text result saved to: {txt_output_file}")
        
    except FileNotFoundError:
        print("错误: 未找到basedpyright命令，请确保已安装basedpyright")
        print("安装命令: pip install basedpyright")
        sys.exit(1)
    except Exception as e:
        print(f"运行文本检查时出错: {e}")
        sys.exit(1)
    
    # 运行basedpyright检查（JSON格式）
    print("运行JSON格式检查...")
    try:
        result_json = subprocess.run(
            ["basedpyright", src_dir, "--outputjson"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # 解析JSON输出
        if result_json.stdout.strip():
            try:
                json_data = json.loads(result_json.stdout)
                
                # 添加元数据
                # 安全地转换文件路径
                try:
                    file_paths = [str(f.relative_to(Path.cwd())) for f in python_files]
                except ValueError:
                    # 如果无法获取相对路径，使用绝对路径
                    file_paths = [str(f) for f in python_files]
                
                json_data['metadata'] = {
                    'check_time': datetime.now().isoformat(),
                    'check_directory': src_dir,
                    'python_files_count': len(python_files),
                    'python_files': file_paths
                }
                
                # 保存JSON输出
                with open(json_output_file, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                
                print(f"[OK] JSON result saved to: {json_output_file}")
                
            except json.JSONDecodeError as e:
                print(f"警告: 无法解析JSON输出: {e}")
                json_data = None
        else:
            print("警告: JSON输出为空")
            json_data = None
            
    except Exception as e:
        print(f"运行JSON检查时出错: {e}")
        json_data = None
    
    # 统计信息
    print("\n" + "=" * 80)
    print("检查完成统计:")
    print("-" * 80)
    
    # 从文本输出中统计
    stdout_text = result_text.stdout
    error_count = stdout_text.count(' error:')
    warning_count = stdout_text.count(' warning:')
    info_count = stdout_text.count(' information:')
    
    print(f"检查文件数: {len(python_files)}")
    print(f"错误 (Error): {error_count}")
    print(f"警告 (Warning): {warning_count}")
    print(f"信息 (Information): {info_count}")
    
    # 如果有JSON数据，显示更详细的统计
    if json_data and 'summary' in json_data:
        summary = json_data['summary']
        print("\n详细统计 (来自JSON):")
        print(f"  分析文件数: {summary.get('filesAnalyzed', 0)}")
        print(f"  错误数: {summary.get('errorCount', 0)}")
        print(f"  警告数: {summary.get('warningCount', 0)}")
        print(f"  信息数: {summary.get('informationCount', 0)}")
        print(f"  检查耗时: {summary.get('timeInSec', 0):.2f} 秒")
    
    print("=" * 80)
    
    return {
        'txt_file': str(txt_output_file),
        'json_file': str(json_output_file),
        'python_files': python_files,
        'error_count': error_count,
        'warning_count': warning_count,
        'info_count': info_count,
        'json_data': json_data
    }


def main():
    """主函数"""
    # 设置输出编码为UTF-8
    if sys.platform == 'win32':
        import os
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        # Use io.TextIOWrapper for proper UTF-8 encoding
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # 检查命令行参数
    src_dir = "src"
    if len(sys.argv) > 1:
        src_dir = sys.argv[1]
    
    # 运行检查
    result = run_basedpyright_check(src_dir)
    
    print("\n生成的文件:")
    print(f"  - 文本结果: {result['txt_file']}")
    if result['json_file']:
        print(f"  - JSON结果: {result['json_file']}")
    
    # 返回退出码
    error_count = result.get('error_count', 0)
    if isinstance(error_count, int) and error_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
