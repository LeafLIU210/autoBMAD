"""
诊断脚本 - Diagnostic Script

诊断Epic自动化系统中的问题并提供解决方案建议。
"""

import asyncio
import json
import logging
import os
import psutil
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# 设置UTF-8编码输出
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 添加父目录到路径
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)


class SystemDiagnostic:
    """系统诊断器"""

    def __init__(self):
        self.findings = []
        self.recommendations = []
        self.critical_issues = []

    def run_full_diagnostic(self) -> Dict[str, Any]:
        """运行完整诊断"""
        print("=" * 80)
        print("Epic自动化系统诊断")
        print("=" * 80)
        print()

        # 1. 检查系统资源
        self.check_system_resources()

        # 2. 检查文件结构
        self.check_file_structure()

        # 3. 检查数据库状态
        self.check_database_status()

        # 4. 检查日志文件
        self.check_log_files()

        # 5. 检查进程状态
        self.check_process_status()

        # 6. 检查Python环境
        self.check_python_environment()

        # 7. 生成诊断报告
        return self.generate_diagnostic_report()

    def check_system_resources(self):
        """检查系统资源"""
        print("1. 检查系统资源...")

        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f"   CPU使用率: {cpu_percent}%")

            # 内存使用率
            memory = psutil.virtual_memory()
            print(f"   内存使用率: {memory.percent}%")
            print(f"   可用内存: {memory.available / (1024**3):.1f}GB")

            # 磁盘使用率
            disk = psutil.disk_usage('/')
            print(f"   磁盘使用率: {disk.percent}%")
            print(f"   可用空间: {disk.free / (1024**3):.1f}GB")

            # 检查资源问题
            if cpu_percent > 90:
                self.critical_issues.append(f"CPU使用率过高: {cpu_percent}%")
                self.recommendations.append("关闭不必要的应用程序以释放CPU资源")

            if memory.percent > 90:
                self.critical_issues.append(f"内存使用率过高: {memory.percent}%")
                self.recommendations.append("释放内存或增加虚拟内存")

            if disk.percent > 90:
                self.critical_issues.append(f"磁盘空间不足: {disk.percent}%")
                self.recommendations.append("清理磁盘空间或扩展存储")

            print("   ✅ 系统资源检查完成")
            self.findings.append("系统资源状态正常")

        except Exception as e:
            print(f"   ❌ 系统资源检查失败: {e}")
            self.errors.append(f"系统资源检查错误: {e}")

        print()

    def check_file_structure(self):
        """检查文件结构"""
        print("2. 检查文件结构...")

        # 检查关键文件和目录
        key_paths = [
            "autoBMAD/epic_automation",
            "autoBMAD/epic_automation/sdk_wrapper.py",
            "autoBMAD/epic_automation/sdk_session_manager.py",
            "autoBMAD/epic_automation/state_manager.py",
            "autoBMAD/epic_automation/qa_agent.py",
            "autoBMAD/epic_automation/logs",
            "docs/stories",
            "docs/qa/gates"
        ]

        missing_paths = []
        for path in key_paths:
            if Path(path).exists():
                print(f"   ✅ {path}")
            else:
                print(f"   ❌ {path}")
                missing_paths.append(path)

        if missing_paths:
            self.findings.append(f"缺失路径: {missing_paths}")
            self.recommendations.append("创建缺失的目录和文件")

        print()

    def check_database_status(self):
        """检查数据库状态"""
        print("3. 检查数据库状态...")

        db_path = Path("progress.db")

        if not db_path.exists():
            print("   ⚠️  数据库文件不存在")
            self.findings.append("数据库文件不存在")
            self.recommendations.append("初始化数据库或运行系统初始化")
            print()
            return

        try:
            # 检查数据库大小
            db_size = db_path.stat().st_size
            print(f"   数据库大小: {db_size / 1024:.1f}KB")

            # 检查数据库内容
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 检查stories表
            cursor.execute("SELECT COUNT(*) FROM stories")
            story_count = cursor.fetchone()[0]
            print(f"   故事记录数: {story_count}")

            # 检查状态分布
            cursor.execute("SELECT status, COUNT(*) FROM stories GROUP BY status")
            status_counts = cursor.fetchall()
            print("   状态分布:")
            for status, count in status_counts:
                print(f"      {status}: {count}")

            # 检查锁状态
            cursor.execute("PRAGMA lock_status")
            lock_status = cursor.fetchone()
            print(f"   数据库锁状态: {lock_status}")

            conn.close()

            # 检查问题
            if db_size > 100 * 1024 * 1024:  # 100MB
                self.findings.append("数据库文件过大")
                self.recommendations.append("清理旧记录或归档数据")

            if story_count > 1000:
                self.findings.append("数据库记录数较多")
                self.recommendations.append("考虑分表或数据清理")

        except Exception as e:
            print(f"   ❌ 数据库检查失败: {e}")
            self.errors.append(f"数据库检查错误: {e}")

        print()

    def check_log_files(self):
        """检查日志文件"""
        print("4. 检查日志文件...")

        logs_dir = Path("autoBMAD/epic_automation/logs")
        if not logs_dir.exists():
            print("   ⚠️  日志目录不存在")
            self.findings.append("日志目录不存在")
            print()
            return

        # 查找最近的日志文件
        log_files = list(logs_dir.glob("*.log"))
        if not log_files:
            print("   ⚠️  没有找到日志文件")
            self.findings.append("没有日志文件")
            print()
            return

        # 按修改时间排序
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        print(f"   找到 {len(log_files)} 个日志文件")
        print(f"   最新日志: {log_files[0].name}")

        # 检查最新日志文件中的错误
        try:
            error_count = 0
            warning_count = 0
            cancel_scope_errors = 0

            with open(log_files[0], "r", encoding="utf-8") as f:
                for line in f:
                    if "ERROR" in line:
                        error_count += 1
                        if "cancel scope" in line.lower():
                            cancel_scope_errors += 1
                    elif "WARNING" in line:
                        warning_count += 1

            print(f"   最新日志中的错误: {error_count}")
            print(f"   最新日志中的警告: {warning_count}")
            print(f"   Cancel scope错误: {cancel_scope_errors}")

            # 记录问题
            if cancel_scope_errors > 0:
                self.critical_issues.append(f"发现 {cancel_scope_errors} 个cancel scope错误")
                self.recommendations.append("应用cancel scope修复方案")

            if error_count > 100:
                self.findings.append("日志中错误较多")
                self.recommendations.append("检查错误日志并修复问题")

        except Exception as e:
            print(f"   ❌ 日志检查失败: {e}")
            self.errors.append(f"日志检查错误: {e}")

        print()

    def check_process_status(self):
        """检查进程状态"""
        print("5. 检查进程状态...")

        try:
            # 检查当前进程
            process = psutil.Process()
            process_info = {
                "pid": process.pid,
                "name": process.name(),
                "cpu_percent": process.cpu_percent(),
                "memory_mb": process.memory_info().rss / (1024 * 1024),
                "status": process.status()
            }

            print(f"   进程ID: {process_info['pid']}")
            print(f"   进程名: {process_info['name']}")
            print(f"   CPU使用率: {process_info['cpu_percent']:.1f}%")
            print(f"   内存使用: {process_info['memory_mb']:.1f}MB")
            print(f"   进程状态: {process_info['status']}")

            # 检查打开的文件
            try:
                open_files = process.open_files()
                print(f"   打开的文件数: {len(open_files)}")
            except Exception:
                print("   无法获取打开的文件信息")

            # 检查网络连接
            try:
                connections = process.connections()
                print(f"   网络连接数: {len(connections)}")
            except Exception:
                print("   无法获取网络连接信息")

            # 检查问题
            if process_info['cpu_percent'] > 50:
                self.findings.append("进程CPU使用率较高")
                self.recommendations.append("优化代码或增加CPU资源")

            if process_info['memory_mb'] > 500:
                self.findings.append("进程内存使用量较大")
                self.recommendations.append("检查内存泄漏或优化内存使用")

        except Exception as e:
            print(f"   ❌ 进程检查失败: {e}")
            self.errors.append(f"进程检查错误: {e}")

        print()

    def check_python_environment(self):
        """检查Python环境"""
        print("6. 检查Python环境...")

        try:
            # Python版本
            python_version = sys.version
            print(f"   Python版本: {python_version}")

            # 检查关键包
            required_packages = [
                "asyncio",
                "sqlite3",
                "pathlib",
                "logging",
                "json",
                "datetime"
            ]

            missing_packages = []
            for package in required_packages:
                try:
                    __import__(package)
                    print(f"   ✅ {package}")
                except ImportError:
                    print(f"   ❌ {package}")
                    missing_packages.append(package)

            if missing_packages:
                self.critical_issues.append(f"缺少Python包: {missing_packages}")
                self.recommendations.append("安装缺失的Python包")

            # 检查可选包
            optional_packages = [
                "psutil",
                "claude_agent_sdk"
            ]

            for package in optional_packages:
                try:
                    __import__(package)
                    print(f"   ✅ {package} (可选)")
                except ImportError:
                    print(f"   ⚠️  {package} (可选，未安装)")
                    self.recommendations.append(f"安装可选包: {package}")

        except Exception as e:
            print(f"   ❌ Python环境检查失败: {e}")
            self.errors.append(f"Python环境检查错误: {e}")

        print()

    def generate_diagnostic_report(self) -> Dict[str, Any]:
        """生成诊断报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform
            },
            "findings": self.findings,
            "critical_issues": self.critical_issues,
            "recommendations": self.recommendations,
            "errors": getattr(self, 'errors', []),
            "overall_status": "HEALTHY" if len(self.critical_issues) == 0 else "NEEDS_ATTENTION",
            "summary": {
                "total_findings": len(self.findings),
                "critical_issues": len(self.critical_issues),
                "total_recommendations": len(self.recommendations)
            }
        }

        # 保存报告
        report_file = Path("diagnostic_report.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # 打印摘要
        print("=" * 80)
        print("诊断摘要")
        print("=" * 80)
        print(f"总体状态: {report['overall_status']}")
        print(f"发现的问题: {len(self.findings)}")
        print(f"严重问题: {len(self.critical_issues)}")
        print(f"建议数量: {len(self.recommendations)}")
        print()

        if self.critical_issues:
            print("⚠️  严重问题:")
            for issue in self.critical_issues:
                print(f"  • {issue}")
            print()

        if self.findings:
            print("📋 发现的问题:")
            for finding in self.findings:
                print(f"  • {finding}")
            print()

        if self.recommendations:
            print("💡 建议:")
            for recommendation in self.recommendations:
                print(f"  • {recommendation}")
            print()

        print(f"详细报告已保存到: {report_file}")
        print("=" * 80)

        return report


async def main():
    """主函数"""
    diagnostic = SystemDiagnostic()
    report = diagnostic.run_full_diagnostic()

    # 根据诊断结果设置退出码
    if report['overall_status'] == 'HEALTHY':
        print("\n✅ 系统状态健康!")
        sys.exit(0)
    else:
        print("\n⚠️  系统需要关注，请检查诊断报告")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
