#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BasedPyright错误提取脚本
从txt检查结果中提取ERROR信息，转化为JSON格式
每个JSON元素包含一个文件的所有ERROR信息汇总
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Any
from collections import defaultdict


class ErrorExtractor:
    """错误提取器"""
    
    def __init__(self, txt_file: str):
        """
        初始化错误提取器
        
        Args:
            txt_file: txt格式的检查结果文件
        """
        self.txt_file = txt_file
        self.txt_content = ""
        self.errors_by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    
    def load_txt_file(self) -> bool:
        """
        加载txt文件
        
        Returns:
            是否成功加载
        """
        txt_path = Path(self.txt_file)
        if not txt_path.exists():
            print(f"错误: 文件不存在 - {self.txt_file}")
            return False
        
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                self.txt_content = f.read()
            print(f"[OK] Loaded file: {self.txt_file}")
            return True
        except Exception as e:
            print(f"错误: 无法读取文件 - {e}")
            return False
    
    def parse_errors(self) -> None:
        """从txt内容中解析ERROR信息"""
        if not self.txt_content:
            print("警告: 文件内容为空")
            return
        
        # 正则表达式匹配ERROR行
        # 格式: /path/to/file.py:line:col - error: message (rule)
        # 示例: d:\Python\fcmrawler\src\models\database.py:1265:66 - error: "…" (reportArgumentType)
        error_pattern = r'\s+(.+?):(\d+):(\d+)\s+-\s+error:\s+(.+)$'
        
        lines = self.txt_content.split('\n')
        
        for line in lines:
            # 跳过空行和不包含 error: 的行
            if not line.strip() or ' - error:' not in line:
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
                    'line': line_num,
                    'column': col_num,
                    'message': error_msg,
                    'rule': self.extract_rule_from_message(error_msg)
                }
                
                # 按文件分组
                self.errors_by_file[file_path].append(error_item)
        
            print(f"[OK] Parsed: Found {len(self.errors_by_file)} files with errors")
        
        # 统计总错误数
        total_errors = sum(len(errors) for errors in self.errors_by_file.values())
        print(f"[OK] Total errors: {total_errors}")
    
    def extract_rule_from_message(self, message: str) -> str:
        """
        从错误消息中提取规则名称
        
        Args:
            message: 错误消息
            
        Returns:
            规则名称，如果找不到则返回'unknown'
        """
        # 匹配括号中的规则，如 (reportArgumentType)
        rule_match = re.search(r'\(([a-zA-Z]+)\)$', message)
        if rule_match:
            return rule_match.group(1)
        return 'unknown'
    
    def generate_json_list(self) -> list[dict[str, Any]]:
        """
        生成JSON列表
        每个元素包含一个文件的所有ERROR信息汇总
        
        Returns:
            JSON列表
        """
        json_list = []
        
        for file_path, errors in sorted(self.errors_by_file.items()):
            # 统计该文件的错误分布
            error_count = len(errors)
            rules_count: dict[str, int] = defaultdict(int)
            
            # 提取详细错误信息
            error_details = []
            for error in errors:
                rule = self.extract_rule_from_message(error['message'])
                rules_count[rule] += 1
                
                error_details.append({
                    'line': error['line'],
                    'column': error['column'],
                    'message': error['message'],
                    'rule': rule
                })
            
            # 创建文件错误汇总
            file_summary = {
                'file': file_path,
                'error_count': error_count,
                'errors_by_rule': dict(rules_count),
                'errors': error_details
            }
            
            json_list.append(file_summary)
        
        return json_list
    
    def save_to_json(self, output_file: str) -> None:
        """
        保存为JSON文件
        
        Args:
            output_file: 输出JSON文件路径
        """
        json_list = self.generate_json_list()
        
        if not json_list:
            print("警告: 没有发现任何ERROR，生成空列表")
        
        # 创建完整的JSON结构
        total_files = len(json_list)
        total_errs = sum(item['error_count'] for item in json_list)
        
        output_data = {
            'metadata': {
                'source_file': self.txt_file,
                'extraction_time': datetime.now().isoformat(),
                'total_files_with_errors': total_files,
                'total_errors': total_errs
            },
            'errors_by_file': json_list
        }
        
        # 保存为JSON
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print(f"[OK] JSON file saved: {output_file}")
            print(f"  - Files with errors: {total_files}")
            print(f"  - Total errors: {total_errs}")
        except Exception as e:
            print(f"错误: 无法保存JSON文件 - {e}")


def find_latest_txt_file() -> str | None:
    """
    查找最新的basedpyright检查结果txt文件
    
    Returns:
        最新的txt文件路径，如果没找到返回None
    """
    # 确定结果目录位置
    script_dir = Path(__file__).parent
    if script_dir.name == 'scripts':
        # 从scripts目录运行
        results_dir = script_dir.parent / 'results'
    else:
        # 从项目根目录运行
        results_dir = Path('basedpyright-workflow/results')
    
    # 在results目录查找
    if results_dir.exists():
        txt_files = sorted(
            results_dir.glob('basedpyright_check_result_*.txt'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        if txt_files:
            return str(txt_files[0])
    
    # 在当前目录查找
    txt_files = sorted(
        Path('.').glob('basedpyright_check_result_*.txt'),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    if txt_files:
        return str(txt_files[0])
    
    return None


def main():
    """主函数"""
    # Set output encoding to UTF-8 for Windows
    if sys.platform == 'win32':
        import os
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print("=" * 80)
    print("BasedPyright ERROR Extractor")
    print("=" * 80)
    print()
    
    # 解析命令行参数
    txt_file = None
    output_file = None
    
    if len(sys.argv) >= 2:
        txt_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    
    # 如果没有指定输入文件，自动查找最新的
    if not txt_file:
        print("未指定输入文件，正在查找最新的检查结果...")
        txt_file = find_latest_txt_file()
        
        if not txt_file:
            print("错误: 未找到检查结果txt文件")
            print("用法: python convert_errors_to_json.py [txt_file] [output_json]")
            sys.exit(1)
        
        print(f"使用文件: {txt_file}")
    
    # 生成输出文件名
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 确定结果输出目录
        script_dir = Path(__file__).parent
        if script_dir.name == 'scripts':
            # 从scripts目录运行，保存到 ../results/
            results_dir = script_dir.parent / 'results'
        else:
            # 从项目根目录运行，保存到 basedpyright-workflow/results/
            results_dir = Path('basedpyright-workflow/results')
        
        # 确保目录存在
        results_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = str(results_dir / f"basedpyright_errors_only_{timestamp}.json")
    
    print()
    
    # 创建提取器
    extractor = ErrorExtractor(txt_file)
    
    # 加载文件
    if not extractor.load_txt_file():
        sys.exit(1)
    
    # 解析错误
    print()
    print("正在解析ERROR信息...")
    extractor.parse_errors()
    
    # 保存为JSON
    print()
    print("正在生成JSON文件...")
    extractor.save_to_json(output_file)
    
    print()
    print("=" * 80)
    print("提取完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
