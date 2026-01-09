"""BMAD工作流配置系统

提供灵活的配置管理，支持：
1. 默认配置
2. 用户自定义配置文件
3. 环境变量覆盖
4. 命令行参数集成
"""

import json
import os
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class OutputFormat(Enum):
    """输出格式枚举"""
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"
    TXT = "txt"


@dataclass
class CheckerConfig:
    """类型检查器配置"""
    enabled: bool = True
    python_version: str = "3.11"  # 默认Python版本
    strict_mode: bool = True
    type_check_mode: str = "basic"  # basic, strict, off
    include_files: List[str] = field(default_factory=lambda: ["**/*.py"])
    exclude_files: List[str] = field(default_factory=lambda: [
        "**/__pycache__/**",
        "**/node_modules/**",
        "**/.venv/**",
        "**/venv/**",
        "**/env/**",
    ])
    exclude_rules: List[str] = field(default_factory=list)
    timeout_seconds: int = 300


@dataclass
class AnalyzerConfig:
    """分析器配置"""
    enabled: bool = True
    auto_classify: bool = True
    confidence_threshold: float = 0.7
    enable_grouping: bool = True
    min_group_size: int = 2
    fix_suggestions: bool = True
    max_errors_per_file: int = 1000


@dataclass
class ReporterConfig:
    """报告生成器配置"""
    output_formats: List[OutputFormat] = field(default_factory=lambda: [OutputFormat.MARKDOWN])
    include_trends: bool = True
    include_file_comparison: bool = True
    include_category_analysis: bool = True
    include_fix_recommendations: bool = True
    max_error_details: int = 50
    max_files_in_summary: int = 20
    trend_analysis_days: int = 30
    generate_summary: bool = True


@dataclass
class BatchConfig:
    """批量处理配置"""
    parallel_processing: bool = True
    max_workers: int = 4
    batch_size: int = 100
    retry_attempts: int = 3
    retry_delay: float = 1.0
    memory_limit_mb: int = 1024
    temp_dir: Optional[Path] = None


@dataclass
class LoggingConfig:
    """日志配置"""
    level: LogLevel = LogLevel.INFO
    log_to_file: bool = True
    log_dir: Path = field(default_factory=lambda: Path("logs"))
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    max_log_size_mb: int = 10
    backup_count: int = 5


@dataclass
class NotificationConfig:
    """通知配置"""
    enabled: bool = False
    email_enabled: bool = False
    webhook_url: Optional[str] = None
    slack_token: Optional[str] = None
    teams_webhook: Optional[str] = None
    notify_on_error: bool = True
    notify_on_completion: bool = False


@dataclass
class RuffConfig:
    """Ruff代码检查器配置"""
    enabled: bool = True
    check_enabled: bool = True
    format_enabled: bool = True
    fix_enabled: bool = True
    line_length: int = 88
    target_version: str = "py311"
    preview: bool = False
    select_rules: List[str] = field(default_factory=lambda: ["E", "W", "F", "I", "B", "C4", "UP", "N"])
    ignore_rules: List[str] = field(default_factory=lambda: ["E501"])  # Line too long (handled by formatter)
    extend_exclude: List[str] = field(default_factory=lambda: [
        "**/__pycache__/**",
        "**/.venv/**",
        "**/venv/**",
        "**/env/**",
        "**/build/**",
        "**/dist/**",
        "**/.git/**",
    ])
    fix_only: List[str] = field(default_factory=list)
    unsafe_fixes: bool = False


@dataclass
class BMADWorkflowConfig:
    """BMAD工作流完整配置"""
    # 基础配置
    project_name: str = "Python项目"
    source_directory: Path = field(default_factory=lambda: Path("src"))
    output_directory: Path = field(default_factory=lambda: Path(".bpr"))
    results_directory: Path = field(default_factory=lambda: Path(".bpr/results"))
    reports_directory: Path = field(default_factory=lambda: Path(".bpr/reports"))

    # 子模块配置
    checker: CheckerConfig = field(default_factory=CheckerConfig)
    analyzer: AnalyzerConfig = field(default_factory=AnalyzerConfig)
    reporter: ReporterConfig = field(default_factory=ReporterConfig)
    batch: BatchConfig = field(default_factory=BatchConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)
    ruff: RuffConfig = field(default_factory=RuffConfig)

    # 全局设置
    auto_fix_enabled: bool = True
    backup_before_fix: bool = True
    git_integration: bool = True
    dry_run_mode: bool = False
    verbose: bool = False


class ConfigManager:
    """配置管理器

    支持多种配置方式：
    1. 默认配置
    2. 配置文件 (JSON/YAML)
    3. 环境变量
    4. 命令行参数
    """

    def __init__(self, config_file: Optional[Path] = None):
        """初始化配置管理器

        Args:
            config_file: 配置文件路径，如果为None则查找默认位置
        """
        self.config_file = self._find_config_file(config_file)
        self.config = BMADWorkflowConfig()
        self._load_config()

    def _find_config_file(self, config_file: Optional[Path]) -> Optional[Path]:
        """查找配置文件

        按优先级查找：
        1. 指定的配置文件
        2. 当前目录及上级目录中的 .bpr.json（递归向上查找）
        3. 当前目录及上级目录中的 basedpyright-workflow.config.json
        4. 用户主目录下的 .bpr.json

        Args:
            config_file: 指定的配置文件路径

        Returns:
            Optional[Path]: 找到的配置文件路径
        """
        if config_file and config_file.exists():
            return config_file

        # 从当前目录开始向上级目录查找
        current_dir = Path.cwd()

        # 使用 current_dir.parent != current_dir 检测是否到达根目录
        # 在 Windows 上，根目录的 parent 仍然是自身，避免无限循环
        while current_dir != current_dir.parent:
            # 查找 .bpr.json
            bpr_config = current_dir / ".bpr.json"
            if bpr_config.exists():
                return bpr_config

            # 查找 basedpyright-workflow.config.json
            workflow_config = current_dir / "basedpyright-workflow.config.json"
            if workflow_config.exists():
                return workflow_config

            # 向上级目录移动
            current_dir = current_dir.parent

        # 最后检查根目录（此时 current_dir 已经是根目录）
        bpr_config = current_dir / ".bpr.json"
        if bpr_config.exists():
            return bpr_config

        workflow_config = current_dir / "basedpyright-workflow.config.json"
        if workflow_config.exists():
            return workflow_config

        # 检查用户主目录（最后备用）
        home_config = Path.home() / ".bpr.json"
        if home_config.exists():
            return home_config

        return None

    def _load_config(self) -> None:
        """加载配置"""
        # 1. 加载默认配置
        self.config = BMADWorkflowConfig()

        # 2. 加载配置文件
        if self.config_file:
            self._load_config_file()

        # 3. 加载环境变量
        self._load_environment_variables()

        # 4. 创建必要的目录
        self._ensure_directories()

    def _load_config_file(self) -> None:
        """从文件加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 递归更新配置
            self._update_config_dict(self.config, data)

        except Exception as e:
            print(f"警告: 配置文件加载失败 {self.config_file}: {e}")

    def _update_config_dict(self, config_obj: Any, data: Dict[str, Any]) -> None:
        """递归更新配置对象

        Args:
            config_obj: 配置对象
            data: 配置数据字典
        """
        for key, value in data.items():
            if hasattr(config_obj, key):
                attr = getattr(config_obj, key)
                if hasattr(attr, '__dataclass_fields__') and isinstance(value, dict):
                    # 如果是dataclass，递归更新
                    self._update_config_dict(attr, value)
                else:
                    # 直接设置值
                    if hasattr(attr, '__dataclass_fields__') and isinstance(value, dict):
                        # 处理枚举类型
                        if key == 'level' and isinstance(value, str):
                            try:
                                setattr(config_obj, key, LogLevel(value.upper()))
                            except ValueError:
                                pass
                        elif key == 'output_formats' and isinstance(value, list):
                            try:
                                formats = [OutputFormat(f.lower()) for f in value]
                                setattr(config_obj, key, formats)
                            except ValueError:
                                pass
                        else:
                            setattr(config_obj, key, value)
                    else:
                        # 处理Path类型
                        if 'directory' in key or 'dir' in key:
                            setattr(config_obj, key, Path(value))
                        else:
                            setattr(config_obj, key, value)

    def _load_environment_variables(self) -> None:
        """从环境变量加载配置"""
        env_mappings = {
            # 基础配置
            'BMAD_PROJECT_NAME': ('project_name', str),
            'BMAD_SOURCE_DIR': ('source_directory', Path),
            'BMAD_OUTPUT_DIR': ('output_directory', Path),
            'BMAD_BPR_DIR': ('output_directory', Path),
            'BMAD_AUTO_FIX': ('auto_fix_enabled', bool),

            # 检查器配置
            'BMAD_PYTHON_VERSION': ('checker.python_version', str),
            'BMAD_STRICT_MODE': ('checker.strict_mode', bool),
            'BMAD_TIMEOUT': ('checker.timeout_seconds', int),

            # 分析器配置
            'BMAD_CONFIDENCE_THRESHOLD': ('analyzer.confidence_threshold', float),
            'BMAD_MAX_ERRORS': ('analyzer.max_errors_per_file', int),

            # 报告器配置
            'BMAD_INCLUDE_TRENDS': ('reporter.include_trends', bool),
            'BMAD_MAX_ERROR_DETAILS': ('reporter.max_error_details', int),

            # 批量处理配置
            'BMAD_MAX_WORKERS': ('batch.max_workers', int),
            'BMAD_BATCH_SIZE': ('batch.batch_size', int),

            # 日志配置
            'BMAD_LOG_LEVEL': ('logging.level', LogLevel),
            'BMAD_LOG_DIR': ('logging.log_dir', Path),

            # Ruff配置
            'BMAD_RUFF_ENABLED': ('ruff.enabled', bool),
            'BMAD_RUFF_LINE_LENGTH': ('ruff.line_length', int),
            'BMAD_RUFF_TARGET_VERSION': ('ruff.target_version', str),
            'BMAD_RUFF_PREVIEW': ('ruff.preview', bool),
            'BMAD_RUFF_UNSAFE_FIXES': ('ruff.unsafe_fixes', bool),
        }

        for env_var, (config_path, value_type) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    # 类型转换
                    if value_type == bool:
                        value = value.lower() in ('true', '1', 'yes', 'on')
                    elif value_type == int:
                        value = int(value)
                    elif value_type == float:
                        value = float(value)
                    elif value_type == Path:
                        value = Path(value)
                    elif value_type == LogLevel:
                        value = LogLevel(value.upper())
                    elif value_type == OutputFormat:
                        value = OutputFormat(value.lower())

                    # 设置配置值
                    self._set_nested_value(config_path, value)

                except (ValueError, AttributeError) as e:
                    print(f"警告: 环境变量 {env_var} 值无效: {e}")

    def _set_nested_value(self, path: str, value: Any) -> None:
        """设置嵌套配置值

        Args:
            path: 配置路径，如 'checker.strict_mode'
            value: 配置值
        """
        parts = path.split('.')
        current = self.config

        for part in parts[:-1]:
            current = getattr(current, part)

        setattr(current, parts[-1], value)

    def _ensure_directories(self) -> None:
        """确保必要的目录存在"""
        directories = [
            self.config.output_directory,
            self.config.results_directory,
            self.config.reports_directory,
            self.config.logging.log_dir,
        ]

        for directory in directories:
            if directory:
                directory.mkdir(parents=True, exist_ok=True)

    def get_config(self) -> BMADWorkflowConfig:
        """获取完整配置

        Returns:
            BMADWorkflowConfig: 完整配置对象
        """
        return self.config

    def save_config(self, file_path: Optional[Path] = None) -> None:
        """保存配置到文件

        Args:
            file_path: 保存路径，如果为None则使用当前配置文件路径
        """
        target_file = file_path or self.config_file or Path(".bmadrc.json")

        try:
            config_dict = asdict(self.config)

            # 处理Path对象和枚举
            config_dict = self._serialize_config(config_dict)

            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)

            print(f"配置已保存到: {target_file}")

        except Exception as e:
            print(f"保存配置失败: {e}")

    def _serialize_config(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """序列化配置字典，处理特殊类型

        Args:
            config_dict: 配置字典

        Returns:
            Dict[str, Any]: 序列化后的配置字典
        """
        result = {}

        for key, value in config_dict.items():
            if isinstance(value, Path):
                result[key] = str(value)
            elif isinstance(value, (LogLevel, OutputFormat)):
                result[key] = value.value.lower()
            elif isinstance(value, dict):
                result[key] = self._serialize_config(value)
            elif isinstance(value, list):
                result[key] = [
                    v.value.lower() if isinstance(v, (LogLevel, OutputFormat))
                    else str(v) if isinstance(v, Path)
                    else v
                    for v in value
                ]
            else:
                result[key] = value

        return result

    def update_from_args(self, args) -> None:
        """从命令行参数更新配置

        Args:
            args: 命令行参数对象
        """
        # 更新基础配置
        if hasattr(args, 'path') and args.path:
            self.config.source_directory = Path(args.path)

        if hasattr(args, 'output') and args.output:
            self.config.output_directory = Path(args.output)

        if hasattr(args, 'verbose') and args.verbose:
            self.config.verbose = True
            self.config.logging.level = LogLevel.DEBUG

        if hasattr(args, 'dry_run') and args.dry_run:
            self.config.dry_run_mode = True

        # 更新报告器配置
        if hasattr(args, 'no_trends') and args.no_trends:
            self.config.reporter.include_trends = False

        if hasattr(args, 'no_file_comparison') and args.no_file_comparison:
            self.config.reporter.include_file_comparison = False

        if hasattr(args, 'max_error_details') and args.max_error_details:
            self.config.reporter.max_error_details = args.max_error_details

        # 更新批量处理配置
        if hasattr(args, 'auto') and args.auto:
            self.config.auto_fix_enabled = True

    def validate_config(self) -> List[str]:
        """验证配置有效性

        Returns:
            List[str]: 验证错误列表，空列表表示验证通过
        """
        errors = []

        # 验证路径
        if not self.config.source_directory.exists():
            errors.append(f"源目录不存在: {self.config.source_directory}")

        # 验证数值范围
        if self.config.analyzer.confidence_threshold < 0 or self.config.analyzer.confidence_threshold > 1:
            errors.append("置信度阈值必须在0-1之间")

        if self.config.batch.max_workers < 1:
            errors.append("最大工作线程数必须大于0")

        if self.config.checker.timeout_seconds < 1:
            errors.append("超时时间必须大于0秒")

        # 验证输出格式
        if not self.config.reporter.output_formats:
            errors.append("至少需要指定一种输出格式")

        # 验证ruff配置
        if self.config.ruff.enabled:
            if self.config.ruff.line_length < 1:
                errors.append("Ruff行长度必须大于0")

            if self.config.ruff.target_version not in ['py36', 'py37', 'py38', 'py39', 'py310', 'py311', 'py312']:
                errors.append("Ruff目标Python版本无效")

            # 验证规则代码格式
            valid_prefixes = ['E', 'W', 'F', 'I', 'B', 'C4', 'UP', 'N', 'A', 'C', 'D', 'DTZ', 'EM', 'EXE',
                             'FA', 'FBT', 'FIX', 'FLY', 'FURB', 'G', 'ICN', 'INP', 'INT', 'ISC', 'LOG', 'NPY',
                             'PD', 'PGH', 'PIE', 'PL', 'PT', 'PTH', 'PYI', 'RET', 'RSE', 'RUF', 'S', 'SIM',
                             'SLF', 'SLOT', 'T', 'T10', 'T20', 'TCH', 'TD', 'TID', 'TRY', 'UP', 'YTT']

            for rule in self.config.ruff.select_rules:
                if rule != "ALL" and not any(rule.startswith(prefix) for prefix in valid_prefixes):
                    errors.append(f"无效的ruff规则代码: {rule}")

            for rule in self.config.ruff.ignore_rules:
                if rule != "ALL" and not any(rule.startswith(prefix) for prefix in valid_prefixes):
                    errors.append(f"无效的ruff规则代码: {rule}")

        return errors

    def create_sample_config(self, output_path: Path) -> None:
        """创建示例配置文件

        Args:
            output_path: 输出文件路径
        """
        sample_config = BMADWorkflowConfig()

        # 添加示例注释
        config_dict = asdict(sample_config)
        config_dict['_comments'] = {
            'project_name': '项目名称，用于报告标识',
            'source_directory': '源代码根目录',
            'auto_fix_enabled': '是否启用自动修复功能',
            'checker.strict_mode': '是否启用严格模式检查',
            'analyzer.confidence_threshold': '自动修复的置信度阈值',
            'reporter.include_trends': '是否在报告中包含趋势分析',
            'batch.max_workers': '批量处理的最大并发数',
        }

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)

            print(f"示例配置文件已创建: {output_path}")

        except Exception as e:
            print(f"创建示例配置文件失败: {e}")


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_file: Optional[Path] = None) -> ConfigManager:
    """获取全局配置管理器实例

    Args:
        config_file: 配置文件路径

    Returns:
        ConfigManager: 配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_file)
    return _config_manager


def get_config() -> BMADWorkflowConfig:
    """获取当前配置

    Returns:
        BMADWorkflowConfig: 当前配置对象
    """
    return get_config_manager().get_config()