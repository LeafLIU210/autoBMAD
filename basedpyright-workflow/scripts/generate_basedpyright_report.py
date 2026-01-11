#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BasedPyright检查报告生成脚本
从检查结果文件生成详细的分析报告
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from collections import defaultdict


class BasedPyrightReportGenerator:
    """BasedPyright报告生成器"""
    
    def __init__(self, txt_file: str | None = None, json_file: str | None = None):
        """
        初始化报告生成器
        
        Args:
            txt_file: 文本格式检查结果文件
            json_file: JSON格式检查结果文件
        """
        self.txt_file = txt_file
        self.json_file = json_file
        self.txt_content = ""
        self.json_data: dict[str, Any] = {}
        
        # 统计数据
        self.stats: dict[str, Any] = {
            'total_files': 0,
            'total_errors': 0,
            'total_warnings': 0,
            'total_info': 0,
            'errors_by_file': defaultdict(int),
            'errors_by_type': defaultdict(int),
            'errors_by_rule': defaultdict(int),
        }
        
        # 错误详情列表
        self.errors: list[dict[str, Any]] = []
        self.warnings: list[dict[str, Any]] = []
        self.infos: list[dict[str, Any]] = []
    
    def load_results(self) -> bool:
        """
        加载检查结果文件
        
        Returns:
            是否成功加载
        """
        success = False
        
        # 加载文本结果
        if self.txt_file and Path(self.txt_file).exists():
            try:
                with open(self.txt_file, 'r', encoding='utf-8') as f:
                    self.txt_content = f.read()
                print(f"[OK] Loaded text file: {self.txt_file}")
                success = True
            except Exception as e:
                print(f"WARNING: Cannot read text file {self.txt_file}: {e}")
        
        # 加载JSON结果
        if self.json_file and Path(self.json_file).exists():
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    self.json_data = json.load(f)
                print(f"[OK] Loaded JSON file: {self.json_file}")
                success = True
            except Exception as e:
                print(f"WARNING: Cannot read JSON file {self.json_file}: {e}")
        
        return success
    
    def parse_json_data(self) -> None:
        """解析JSON数据并提取统计信息"""
        if not self.json_data:
            return
        
        # 提取summary信息
        if 'summary' in self.json_data:
            summary = self.json_data['summary']
            self.stats['total_files'] = summary.get('filesAnalyzed', 0)
            self.stats['total_errors'] = summary.get('errorCount', 0)
            self.stats['total_warnings'] = summary.get('warningCount', 0)
            self.stats['total_info'] = summary.get('informationCount', 0)
            self.stats['time_in_sec'] = summary.get('timeInSec', 0)
        
        # 提取诊断信息
        if 'generalDiagnostics' in self.json_data:
            for diag in self.json_data['generalDiagnostics']:
                severity = diag.get('severity', 'unknown')
                file_path = diag.get('file', 'unknown')
                message = diag.get('message', '')
                rule = diag.get('rule', 'unknown')
                
                # 提取位置信息
                range_info = diag.get('range', {})
                start = range_info.get('start', {})
                line = start.get('line', 0) + 1  # basedpyright使用0-based行号
                character = start.get('character', 0)
                
                error_item = {
                    'file': file_path,
                    'line': line,
                    'character': character,
                    'severity': severity,
                    'message': message,
                    'rule': rule
                }
                
                # 按严重程度分类
                if severity == 'error':
                    self.errors.append(error_item)
                    self.stats['errors_by_file'][file_path] += 1
                    self.stats['errors_by_rule'][rule] += 1
                elif severity == 'warning':
                    self.warnings.append(error_item)
                elif severity == 'information':
                    self.infos.append(error_item)
    
    def parse_text_data(self) -> None:
        """从文本内容中提取统计信息（作为备用）"""
        if not self.txt_content:
            return
        
        # 统计错误、警告、信息数量
        self.stats['total_errors'] = self.txt_content.count(' error:')
        self.stats['total_warnings'] = self.txt_content.count(' warning:')
        self.stats['total_info'] = self.txt_content.count(' information:')
        
        # 提取文件列表
        files_section = re.search(r'检查的文件列表:.*?-{80}(.*?)-{80}', 
                                 self.txt_content, re.DOTALL)
        if files_section:
            file_lines = files_section.group(1).strip().split('\n')
            self.stats['total_files'] = len([l for l in file_lines if l.strip()])
    
    def generate_markdown_report(self, output_file: str) -> None:
        """
        生成Markdown格式报告
        
        Args:
            output_file: 输出文件路径
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # 标题和元数据
            f.write("# BasedPyright 检查报告\n\n")
            f.write(f"**生成时间**: {timestamp}\n\n")
            
            if self.json_data.get('metadata'):
                meta = self.json_data['metadata']
                f.write(f"**检查时间**: {meta.get('check_time', 'N/A')}\n")
                f.write(f"**检查目录**: `{meta.get('check_directory', 'N/A')}`\n\n")
            
            # 执行摘要
            f.write("## 📊 执行摘要\n\n")
            f.write("| 项目 | 数量 |\n")
            f.write("|------|------|\n")
            f.write(f"| 检查文件数 | {self.stats['total_files']} |\n")
            f.write(f"| ❌ 错误 (Error) | {self.stats['total_errors']} |\n")
            f.write(f"| ⚠️ 警告 (Warning) | {self.stats['total_warnings']} |\n")
            f.write(f"| ℹ️ 信息 (Information) | {self.stats['total_info']} |\n")
            
            if 'time_in_sec' in self.stats:
                f.write(f"| ⏱️ 检查耗时 | {self.stats['time_in_sec']:.2f} 秒 |\n")
            
            f.write("\n")
            
            # 错误统计
            if self.errors:
                f.write("## 🔴 错误详情\n\n")
                f.write(f"共发现 **{len(self.errors)}** 个错误\n\n")
                
                # 按文件分组
                f.write("### 按文件分组\n\n")
                for file_path, count in sorted(self.stats['errors_by_file'].items(), 
                                               key=lambda x: x[1], reverse=True):
                    f.write(f"- `{file_path}`: {count} 个错误\n")
                f.write("\n")
                
                # 按规则分组
                f.write("### 按规则分组\n\n")
                for rule, count in sorted(self.stats['errors_by_rule'].items(), 
                                         key=lambda x: x[1], reverse=True):
                    f.write(f"- `{rule}`: {count} 次\n")
                f.write("\n")
                
                # 详细错误列表
                f.write("### 详细错误列表\n\n")
                for i, error in enumerate(self.errors, 1):
                    f.write(f"#### {i}. {error['file']}:{error['line']}\n\n")
                    f.write(f"- **规则**: `{error['rule']}`\n")
                    f.write(f"- **位置**: 第 {error['line']} 行, 第 {error['character']} 列\n")
                    f.write(f"- **错误信息**: {error['message']}\n")
                    f.write("\n")
            else:
                f.write("## ✅ 无错误\n\n")
                f.write("恭喜！没有发现任何错误。\n\n")
            
            # 警告详情
            if self.warnings:
                f.write("## ⚠️ 警告详情\n\n")
                f.write(f"共发现 **{len(self.warnings)}** 个警告\n\n")
                
                for i, warning in enumerate(self.warnings[:20], 1):  # 只显示前20个
                    f.write(f"{i}. `{warning['file']}:{warning['line']}` - {warning['message']} (`{warning['rule']}`)\n")
                
                if len(self.warnings) > 20:
                    f.write(f"\n... 还有 {len(self.warnings) - 20} 个警告未显示\n")
                f.write("\n")
            
            # 检查的文件列表
            if self.json_data.get('metadata', {}).get('python_files'):
                f.write("## 📁 检查的文件列表\n\n")
                files = self.json_data['metadata']['python_files']
                for i, file in enumerate(files, 1):
                    f.write(f"{i}. `{file}`\n")
                f.write("\n")
            
            # 原始文本输出（可选）
            if self.txt_content:
                f.write("## 📄 原始检查输出\n\n")
                f.write("```\n")
                # 只包含输出结果部分
                output_section = re.search(r'检查输出结果:.*?={80}(.*)', 
                                          self.txt_content, re.DOTALL)
                if output_section:
                    f.write(output_section.group(1).strip())
                else:
                    f.write(self.txt_content[-5000:])  # 最后5000字符
                f.write("\n```\n\n")
        
        print(f"[OK] Markdown report generated: {output_file}")
    
    def generate_html_report(self, output_file: str) -> None:
        """
        生成HTML格式报告
        
        Args:
            output_file: 输出文件路径
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("<!DOCTYPE html>\n")
            f.write("<html lang='zh-CN'>\n")
            f.write("<head>\n")
            f.write("    <meta charset='UTF-8'>\n")
            f.write("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n")
            f.write("    <title>BasedPyright 检查报告</title>\n")
            f.write("    <style>\n")
            f.write(self._get_html_styles())
            f.write("    </style>\n")
            f.write("</head>\n")
            f.write("<body>\n")
            f.write("    <div class='container'>\n")
            f.write("        <h1>BasedPyright 检查报告</h1>\n")
            f.write(f"        <p class='timestamp'>生成时间: {timestamp}</p>\n")
            
            # 摘要卡片
            f.write("        <div class='summary'>\n")
            f.write("            <h2>📊 执行摘要</h2>\n")
            f.write("            <div class='stats-grid'>\n")
            f.write("                <div class='stat-card'>\n")
            f.write(f"                    <div class='stat-value'>{self.stats['total_files']}</div>\n")
            f.write("                    <div class='stat-label'>检查文件数</div>\n")
            f.write("                </div>\n")
            f.write("                <div class='stat-card error'>\n")
            f.write(f"                    <div class='stat-value'>{self.stats['total_errors']}</div>\n")
            f.write("                    <div class='stat-label'>❌ 错误</div>\n")
            f.write("                </div>\n")
            f.write("                <div class='stat-card warning'>\n")
            f.write(f"                    <div class='stat-value'>{self.stats['total_warnings']}</div>\n")
            f.write("                    <div class='stat-label'>⚠️ 警告</div>\n")
            f.write("                </div>\n")
            f.write("                <div class='stat-card info'>\n")
            f.write(f"                    <div class='stat-value'>{self.stats['total_info']}</div>\n")
            f.write("                    <div class='stat-label'>ℹ️ 信息</div>\n")
            f.write("                </div>\n")
            f.write("            </div>\n")
            f.write("        </div>\n")
            
            # 错误详情
            if self.errors:
                f.write("        <div class='errors-section'>\n")
                f.write("            <h2>🔴 错误详情</h2>\n")
                
                # 按规则分组的图表
                f.write("            <h3>按规则分组</h3>\n")
                f.write("            <table>\n")
                f.write("                <thead><tr><th>规则</th><th>出现次数</th></tr></thead>\n")
                f.write("                <tbody>\n")
                for rule, count in sorted(self.stats['errors_by_rule'].items(), 
                                         key=lambda x: x[1], reverse=True):
                    f.write(f"                <tr><td><code>{rule}</code></td><td>{count}</td></tr>\n")
                f.write("                </tbody>\n")
                f.write("            </table>\n")
                
                # 详细错误列表
                f.write("            <h3>详细错误列表</h3>\n")
                for i, error in enumerate(self.errors, 1):
                    f.write("            <div class='error-item'>\n")
                    f.write("                <div class='error-header'>\n")
                    f.write(f"                    <strong>#{i}</strong> {error['file']}:{error['line']}\n")
                    f.write("                </div>\n")
                    f.write("                <div class='error-body'>\n")
                    f.write(f"                    <p><strong>规则:</strong> <code>{error['rule']}</code></p>\n")
                    f.write(f"                    <p><strong>错误信息:</strong> {error['message']}</p>\n")
                    f.write("                </div>\n")
                    f.write("            </div>\n")
                f.write("        </div>\n")
            
            f.write("    </div>\n")
            f.write("</body>\n")
            f.write("</html>\n")
        
        print(f"[OK] HTML report generated: {output_file}")
    
    def _get_html_styles(self) -> str:
        """获取HTML样式"""
        return """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
               background: #f5f5f5; color: #333; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #2c3e50; margin-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
        h3 { color: #555; margin-top: 20px; margin-bottom: 10px; }
        .timestamp { color: #7f8c8d; margin-bottom: 20px; }
        .summary { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 15px; }
        .stat-card { background: #ecf0f1; padding: 20px; border-radius: 6px; text-align: center; }
        .stat-card.error { background: #fadbd8; }
        .stat-card.warning { background: #fcf3cf; }
        .stat-card.info { background: #d6eaf8; }
        .stat-value { font-size: 2em; font-weight: bold; color: #2c3e50; }
        .stat-label { margin-top: 5px; font-size: 0.9em; color: #7f8c8d; }
        .errors-section { background: white; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #3498db; color: white; }
        tr:hover { background: #f5f5f5; }
        .error-item { background: #fff5f5; border-left: 4px solid #e74c3c; padding: 15px; margin: 10px 0; border-radius: 4px; }
        .error-header { font-size: 1.1em; margin-bottom: 10px; color: #c0392b; }
        .error-body p { margin: 5px 0; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }
"""
    
    def generate_reports(self, output_prefix: str = "basedpyright_report") -> None:
        """
        生成所有格式的报告
        
        Args:
            output_prefix: 输出文件名前缀
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 确定报告输出目录
        script_dir = Path(__file__).parent
        if script_dir.name == 'scripts':
            # 从scripts目录运行，报告保存到 ../reports/
            reports_dir = script_dir.parent / 'reports'
        else:
            # 从项目根目录运行，报告保存到 basedpyright-workflow/reports/
            reports_dir = Path('basedpyright-workflow/reports')
        
        # 确保报告目录存在
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 解析数据
        if self.json_data:
            self.parse_json_data()
        elif self.txt_content:
            self.parse_text_data()
        
        # 生成Markdown报告
        md_file = reports_dir / f"{output_prefix}_{timestamp}.md"
        self.generate_markdown_report(str(md_file))
        
        # 生成HTML报告
        html_file = reports_dir / f"{output_prefix}_{timestamp}.html"
        self.generate_html_report(str(html_file))
        
        print("\n" + "=" * 80)
        print("Report generation completed!")
        print(f"  - Markdown: {md_file}")
        print(f"  - HTML: {html_file}")
        print("=" * 80)


def find_latest_result_files() -> tuple[str | None, str | None]:
    """
    查找最新的检查结果文件
    
    Returns:
        (txt_file, json_file) 元组
    """
    # 确定结果目录位置
    script_dir = Path(__file__).parent
    if script_dir.name == 'scripts':
        # 从scripts目录运行
        results_dir = script_dir.parent / 'results'
    else:
        # 从项目根目录运行
        results_dir = Path('basedpyright-workflow/results')
    
    txt_file = None
    json_file = None
    
    # 在results目录查找
    if results_dir.exists():
        txt_files = sorted(
            results_dir.glob('basedpyright_check_result_*.txt'), 
            key=lambda p: p.stat().st_mtime, 
            reverse=True
        )
        txt_file = str(txt_files[0]) if txt_files else None
        
        json_files = sorted(
            results_dir.glob('basedpyright_check_result_*.json'), 
            key=lambda p: p.stat().st_mtime, 
            reverse=True
        )
        json_file = str(json_files[0]) if json_files else None
    
    # 如果results目录没找到，在当前目录查找
    if not txt_file:
        txt_files = sorted(
            Path('.').glob('basedpyright_check_result_*.txt'), 
            key=lambda p: p.stat().st_mtime, 
            reverse=True
        )
        txt_file = str(txt_files[0]) if txt_files else None
    
    if not json_file:
        json_files = sorted(
            Path('.').glob('basedpyright_check_result_*.json'), 
            key=lambda p: p.stat().st_mtime, 
            reverse=True
        )
        json_file = str(json_files[0]) if json_files else None
    
    return txt_file, json_file


def main():
    """主函数"""
    # Set output encoding to UTF-8 for Windows
    if sys.platform == 'win32':
        import os
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print("BasedPyright Report Generator")
    print("="* 80)
    
    # 解析命令行参数
    txt_file = None
    json_file = None
    
    if len(sys.argv) >= 2:
        txt_file = sys.argv[1]
    if len(sys.argv) >= 3:
        json_file = sys.argv[2]
    
    # 如果没有指定文件，自动查找最新的
    if not txt_file and not json_file:
        print("No input file specified, searching for latest results...")
        txt_file, json_file = find_latest_result_files()
        
        if not txt_file and not json_file:
            print("ERROR: No check result files found")
            print("Usage: python generate_basedpyright_report.py [txt_file] [json_file]")
            sys.exit(1)
    
    print("Using files:")
    if txt_file:
        print(f"  - Text result: {txt_file}")
    if json_file:
        print(f"  - JSON result: {json_file}")
    print()
    
    # 创建报告生成器
    generator = BasedPyrightReportGenerator(txt_file, json_file)
    
    # 加载结果
    if not generator.load_results():
        print("ERROR: Cannot load any result files")
        sys.exit(1)
    
    # 生成报告
    generator.generate_reports()


if __name__ == "__main__":
    main()
