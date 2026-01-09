"""BasedPyright批量错误处理器

该模块提供对JSON格式的pyright错误报告进行批量分析和处理功能，
包括错误去重、分类、统计、智能分组和修复建议生成。

主要功能:
1. 错误去重: 按文件+错误类型去重，避免重复处理
2. 错误分类: 分为简单错误、复杂错误、需要人工审查的错误
3. 智能分组: 基于错误消息的相似性进行分组
4. 统计分析: 生成多维度的统计报告
5. 修复建议: 为常见错误类型提供自动修复建议
6. 交互式修复: 支持用户确认的批量修复操作
"""

import json
import re
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum


class ErrorCategory(Enum):
    """错误分类枚举"""
    SIMPLE = "simple"           # 简单错误：可以直接自动修复
    COMPLEX = "complex"         # 复杂错误：需要一定逻辑处理
    MANUAL = "manual"           # 人工错误：需要人工审查和决策


class ErrorSeverity(Enum):
    """错误严重程度枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorInfo:
    """错误信息数据类"""
    file: str
    line: int
    column: int
    severity: str
    message: str
    rule: str
    category: ErrorCategory = ErrorCategory.MANUAL
    severity_level: ErrorSeverity = ErrorSeverity.MEDIUM
    fix_suggestion: Optional[str] = None
    confidence: float = 0.8  # 修复建议的置信度
    group_id: Optional[str] = None  # 分组ID


@dataclass
class ErrorGroup:
    """错误分组信息"""
    group_id: str
    pattern: str
    errors: List[ErrorInfo]
    common_fix: Optional[str] = None
    auto_fixable: bool = False


@dataclass
class ProcessingStats:
    """处理统计信息"""
    total_errors: int
    unique_errors: int
    by_category: Dict[str, int]
    by_file: Dict[str, int]
    by_severity: Dict[str, int]
    groups_count: int
    auto_fixable_count: int
    processing_time: float


class BatchErrorProcessor:
    """BasedPyright批量错误处理器

    该类提供对JSON格式的pyright错误报告进行批量分析和处理的核心功能。
    """

    def __init__(self, errors_file: Optional[Path] = None):
        """初始化批量处理器

        Args:
            errors_file: 错误JSON文件路径，如果为None则后续需要手动加载
        """
        self.errors_file = errors_file
        self.raw_errors: List[Dict] = []
        self.processed_errors: List[ErrorInfo] = []
        self.error_groups: List[ErrorGroup] = []
        self.stats: Optional[ProcessingStats] = None

        # 错误分类规则
        self._init_classification_rules()

        # 常见错误修复建议
        self._init_fix_suggestions()

    def _init_classification_rules(self):
        """初始化错误分类规则"""
        self.classification_rules = {
            # 简单错误：可以直接自动修复的类型
            ErrorCategory.SIMPLE: [
                r"Missing import.*?",
                r"Unable to import.*?",
                r'.*" is not defined',
                r'.*" is unbound',
                r'Argument missing for parameter.*?',
                r'Too many arguments.*?',
                r'Unexpected keyword argument.*?',
                r'Incompatible type for argument.*?',
                r'Cannot access member.*?',
                r'Object of type.*?has no attribute.*?',
                # 添加泛型类型参数缺失错误 - 这些通常是简单修复
                r'".*?" 泛型类应有类型参数',
                r'".*?" generic class expects type arguments',
                r'Generic type.*?needs.*?type arguments',
            ],

            # 复杂错误：需要一定逻辑处理
            ErrorCategory.COMPLEX: [
                r'Incompatible return type.*?',
                r'Argument of type.*?cannot be assigned.*?',
                r'List comprehension has incompatible type.*?',
                r'Cannot assign to type.*?',
                r'Function is missing a return type annotation',
                r'Cannot infer type of variable.*?',
                r'Generic type.*?needs.*?type arguments',
            ],

            # 人工错误：需要人工审查
            ErrorCategory.MANUAL: [
                r'Expression of type.*?cannot be assigned.*?',
                r'Object of type.*?is not assignable.*?',
                r'Call expression expects.*?arguments.*?',
                r'Condition always evaluates to.*?',
                r'Unreachable code',
                r'Definition of.*?is not accessible',
            ]
        }

        # 严重程度判断规则
        self.severity_rules = {
            ErrorSeverity.CRITICAL: [
                r'Unable to import.*?',
                r'Module.*?has no attribute.*?',
                r'Cannot access member.*?',
            ],
            ErrorSeverity.HIGH: [
                r'.*" is not defined',
                r'Argument missing for parameter.*?',
                r'Incompatible return type.*?',
            ],
            ErrorSeverity.MEDIUM: [
                r'Unexpected keyword argument.*?',
                r'Incompatible type for argument.*?',
                r'Cannot assign to type.*?',
            ],
            ErrorSeverity.LOW: [
                r'Function is missing a return type annotation',
                r'Cannot infer type of variable.*?',
            ]
        }

    def _init_fix_suggestions(self):
        """初始化常见错误修复建议"""
        self.fix_suggestions = {
            # 导入相关错误
            r"Missing import (.+?)": "添加导入语句: import {match}",
            r"Unable to import (.+?)": "检查模块名拼写或安装对应的包: import {match}",

            # 未定义变量
            r'"(.+?)" is not defined': "检查变量名拼写或定义变量: {match}",
            r'"(.+?)" is unbound': "确保变量在使用前已赋值: {match}",

            # 函数参数相关
            r"Argument missing for parameter \"(.+?)\"": "为函数调用添加缺失的参数: {match}=",
            r"Too many arguments for function call": "移除多余的函数参数",
            r"Unexpected keyword argument \"(.+?)\"": "检查参数名拼写或移除该参数: {match}",

            # 类型相关
            r"Incompatible type for argument \"(.+?)\"": "确保参数类型匹配函数签名",
            r"Incompatible return value": "确保返回值类型与函数声明匹配",
            r"Cannot assign to type \"(.+?)\"": "确保赋值左右两侧类型匹配: {match}",

            # 属性访问相关
            r"Object of type \"(.+?)\" has no attribute \"(.+?)\"": "检查对象类型或属性名: {match}",
            r"Cannot access member \"(.+?)\" for type \"(.+?)\"": "检查对象是否包含该成员: {match}",

            # 类型注解相关
            r"Function is missing a return type annotation": "为函数添加返回类型注解",
            r"Cannot infer type of variable \"(.+?)\"": "为变量添加显式类型注解: {match}",
            r"Generic type \"(.+?)\" needs (.+?) type arguments": "为泛型添加所需的类型参数",

            # 泛型类型参数缺失
            r'"(.+?)" 泛型类应有类型参数': "为泛型类添加类型参数，例如: {match}[str, int]",
            r'"(.+?)" generic class expects type arguments': "Add type arguments to generic class, e.g., {match}[str, int]",

            # SQLAlchemy Column类型相关
            r'Column\[.*?\] 类型的实参无法赋值给.*? "str" 类型的形参': "检查Column类型使用，可能需要 .as_string() 或合适的类型转换",
        }

    def load_errors(self, errors_file: Optional[Path] = None) -> bool:
        """从JSON文件加载错误数据

        Args:
            errors_file: 错误文件路径，如果为None则使用初始化时指定的文件

        Returns:
            bool: 加载是否成功
        """
        if errors_file:
            self.errors_file = errors_file

        if not self.errors_file or not self.errors_file.exists():
            return False

        try:
            with open(self.errors_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 适配不同的JSON格式
            self.raw_errors = []

            # 格式1: 直接的errors数组
            if 'errors' in data:
                self.raw_errors = data['errors']
            # 格式2: diagnostics数组
            elif 'diagnostics' in data:
                self.raw_errors = data['diagnostics']
            # 格式3: errors_by_file格式（我们项目使用的格式）
            elif 'errors_by_file' in data:
                for file_info in data['errors_by_file']:
                    file_path = file_info.get('file', '')
                    errors = file_info.get('errors', [])
                    for error in errors:
                        # 添加文件路径到错误信息中
                        error['file'] = file_path
                        self.raw_errors.append(error)
            else:
                # 如果都不是，尝试使用整个数据作为错误数组
                if isinstance(data, list):
                    self.raw_errors = data
                else:
                    print("未识别的JSON格式")
                    return False

            print(f"成功加载 {len(self.raw_errors)} 个错误")
            return True

        except Exception as e:
            print(f"加载错误文件失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _classify_error(self, error: Dict) -> Tuple[ErrorCategory, ErrorSeverity]:
        """对错误进行分类和严重程度判断

        Args:
            error: 错误信息字典

        Returns:
            Tuple[ErrorCategory, ErrorSeverity]: 分类和严重程度
        """
        message = error.get('message', '')

        # 分类判断
        category = ErrorCategory.MANUAL  # 默认为需要人工审查
        for cat, patterns in self.classification_rules.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    category = cat
                    break
            if category != ErrorCategory.MANUAL:
                break

        # 严重程度判断
        severity = ErrorSeverity.MEDIUM  # 默认为中等严重程度
        for sev, patterns in self.severity_rules.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    severity = sev
                    break
            if severity != ErrorSeverity.MEDIUM:
                break

        return category, severity

    def _generate_fix_suggestion(self, error: Dict, category: ErrorCategory) -> Optional[str]:
        """为错误生成修复建议

        Args:
            error: 错误信息字典
            category: 错误分类

        Returns:
            Optional[str]: 修复建议，如果没有匹配的建议则返回None
        """
        message = error.get('message', '')

        # 尝试匹配修复建议规则
        for pattern, suggestion in self.fix_suggestions.items():
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                if match.groups():
                    # 替换占位符
                    try:
                        return suggestion.format(match=match.group(1) if match.groups() else '')
                    except IndexError:
                        return suggestion
                return suggestion

        # 根据分类提供通用建议
        category_suggestions = {
            ErrorCategory.SIMPLE: "这是一个常见的类型错误，通常可以通过修正类型注解或导入来解决",
            ErrorCategory.COMPLEX: "这个错误需要仔细分析类型逻辑，建议查看相关类型定义",
            ErrorCategory.MANUAL: "这个错误需要人工审查，建议检查代码逻辑和类型设计"
        }

        return category_suggestions.get(category)

    def _calculate_confidence(self, error: Dict, category: ErrorCategory, fix_suggestion: Optional[str]) -> float:
        """计算修复建议的置信度

        Args:
            error: 错误信息
            category: 错误分类
            fix_suggestion: 修复建议

        Returns:
            float: 置信度 (0.0-1.0)
        """
        base_confidence = {
            ErrorCategory.SIMPLE: 0.9,
            ErrorCategory.COMPLEX: 0.7,
            ErrorCategory.MANUAL: 0.5
        }

        confidence = base_confidence.get(category, 0.5)

        # 如果有具体的修复建议，提高置信度
        if fix_suggestion and "{" in fix_suggestion:
            confidence += 0.1

        # 根据错误严重程度调整置信度
        message = error.get('message', '')
        if any(keyword in message.lower() for keyword in ['import', 'not defined', 'missing']):
            confidence += 0.1

        return min(confidence, 1.0)

    def process_errors(self) -> None:
        """处理加载的错误数据

        该方法会对原始错误数据进行以下处理：
        1. 解析和分类每个错误
        2. 生成修复建议
        3. 计算置信度
        4. 去重处理
        """
        if not self.raw_errors:
            return

        seen_errors: Set[Tuple[str, int, str]] = set()  # (file, line, message)

        for error in self.raw_errors:
            # 获取基本信息
            file_path = error.get('file', error.get('location', {}).get('file', ''))
            line = error.get('line', error.get('location', {}).get('line', 0))
            column = error.get('column', error.get('location', {}).get('column', 0))
            severity = error.get('severity', 'ERROR')
            message = error.get('message', '')
            rule = error.get('rule', error.get('code', 'unknown'))

            # 去重检查
            error_key = (file_path, line, message)
            if error_key in seen_errors:
                continue
            seen_errors.add(error_key)

            # 分类和严重程度判断
            category, severity_level = self._classify_error(error)

            # 生成修复建议
            fix_suggestion = self._generate_fix_suggestion(error, category)

            # 计算置信度
            confidence = self._calculate_confidence(error, category, fix_suggestion)

            # 创建错误信息对象
            error_info = ErrorInfo(
                file=file_path,
                line=line,
                column=column,
                severity=severity,
                message=message,
                rule=rule,
                category=category,
                severity_level=severity_level,
                fix_suggestion=fix_suggestion,
                confidence=confidence
            )

            self.processed_errors.append(error_info)

    def _group_errors_by_pattern(self) -> None:
        """基于错误消息模式对错误进行分组"""
        pattern_groups: defaultdict[str, List[ErrorInfo]] = defaultdict(list)

        for error in self.processed_errors:
            # 简化错误消息，提取模式
            simplified_message = re.sub(r'"[^"]*"', '"<value>"', error.message)
            simplified_message = re.sub(r'\d+', '<num>', simplified_message)
            simplified_message = re.sub(r'[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*', '<obj.attr>', simplified_message)

            # 生成分组模式
            pattern = f"{error.rule}:{simplified_message[:50]}..."

            pattern_groups[pattern].append(error)
            error.group_id = pattern

        # 创建错误分组对象
        self.error_groups = []
        for pattern, errors in pattern_groups.items():
            if len(errors) > 1:  # 只为重复出现的错误创建分组
                common_fix = self._find_common_fix(errors)
                auto_fixable = all(e.category == ErrorCategory.SIMPLE for e in errors)

                group = ErrorGroup(
                    group_id=pattern,
                    pattern=pattern,
                    errors=errors,
                    common_fix=common_fix,
                    auto_fixable=auto_fixable
                )
                self.error_groups.append(group)

    def _find_common_fix(self, errors: List[ErrorInfo]) -> Optional[str]:
        """为一组错误寻找通用修复方案

        Args:
            errors: 错误列表

        Returns:
            Optional[str]: 通用修复方案
        """
        # 收集所有修复建议
        suggestions = [e.fix_suggestion for e in errors if e.fix_suggestion]

        if not suggestions:
            return None

        # 如果所有建议都相同，返回共同建议
        if len(set(suggestions)) == 1:
            return suggestions[0]

        # 尝试找到共同模式
        common_patterns = []
        for suggestion in suggestions:
            # 提取关键词
            words = re.findall(r'\b\w+\b', suggestion.lower())
            common_patterns.extend(words)

        # 找出最常见的词
        if common_patterns:
            counter = Counter(common_patterns)
            most_common = counter.most_common(3)
            return f"建议关注: {', '.join([word for word, _ in most_common])}"

        return None

    def _generate_statistics(self, processing_time: float) -> ProcessingStats:
        """生成处理统计信息

        Args:
            processing_time: 处理耗时（秒）

        Returns:
            ProcessingStats: 统计信息
        """
        total_errors = len(self.raw_errors)
        unique_errors = len(self.processed_errors)

        # 按分类统计
        by_category = {}
        for category in ErrorCategory:
            count = sum(1 for e in self.processed_errors if e.category == category)
            by_category[category.value] = count

        # 按文件统计
        by_file = Counter(e.file for e in self.processed_errors)
        by_file = dict(by_file.most_common(10))  # 只保留前10个文件

        # 按严重程度统计
        by_severity = {}
        for severity in ErrorSeverity:
            count = sum(1 for e in self.processed_errors if e.severity_level == severity)
            by_severity[severity.value] = count

        # 统计其他信息
        groups_count = len(self.error_groups)
        auto_fixable_count = sum(1 for e in self.processed_errors if e.category == ErrorCategory.SIMPLE)

        return ProcessingStats(
            total_errors=total_errors,
            unique_errors=unique_errors,
            by_category=by_category,
            by_file=by_file,
            by_severity=by_severity,
            groups_count=groups_count,
            auto_fixable_count=auto_fixable_count,
            processing_time=processing_time
        )

    def analyze(self) -> ProcessingStats:
        """执行完整的错误分析流程

        Returns:
            ProcessingStats: 分析统计信息
        """
        start_time = datetime.now()

        # 处理错误
        self.process_errors()

        # 分组错误
        self._group_errors_by_pattern()

        # 计算处理时间
        processing_time = (datetime.now() - start_time).total_seconds()

        # 生成统计信息
        self.stats = self._generate_statistics(processing_time)

        return self.stats

    def get_errors_by_category(self, category: ErrorCategory) -> List[ErrorInfo]:
        """获取指定分类的错误

        Args:
            category: 错误分类

        Returns:
            List[ErrorInfo]: 该分类的错误列表
        """
        return [error for error in self.processed_errors if error.category == category]

    def get_auto_fixable_errors(self) -> List[ErrorInfo]:
        """获取可以自动修复的错误

        Returns:
            List[ErrorInfo]: 可自动修复的错误列表
        """
        return [error for error in self.processed_errors
                if error.category == ErrorCategory.SIMPLE and error.confidence > 0.7]

    def get_error_groups(self) -> List[ErrorGroup]:
        """获取错误分组信息

        Returns:
            List[ErrorGroup]: 错误分组列表
        """
        return self.error_groups

    def export_analysis_report(self, output_file: Path) -> bool:
        """导出分析报告到JSON文件

        Args:
            output_file: 输出文件路径

        Returns:
            bool: 导出是否成功
        """
        try:
            report_data = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'source_file': str(self.errors_file) if self.errors_file else None,
                },
                'statistics': asdict(self.stats) if self.stats else {},
                'errors': [asdict(error) for error in self.processed_errors],
                'groups': [
                    {
                        'group_id': group.group_id,
                        'pattern': group.pattern,
                        'error_count': len(group.errors),
                        'common_fix': group.common_fix,
                        'auto_fixable': group.auto_fixable,
                        'errors': [asdict(error) for error in group.errors]
                    }
                    for group in self.error_groups
                ]
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)

            return True
        except Exception as e:
            print(f"导出报告失败: {e}")
            return False