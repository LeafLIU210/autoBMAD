"""BMAD工作流模板系统

提供预定义的工作流模板，支持：
1. 不同项目类型的配置模板
2. 自定义工作流模板
3. 模板继承和扩展
4. 模板验证和生成
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..config import BMADWorkflowConfig


class ProjectType(Enum):
    """项目类型枚举"""
    PYTHON_LIBRARY = "python_library"
    PYTHON_WEB = "python_web"
    PYTHON_CLI = "python_cli"
    PYTHON_DATA_SCIENCE = "python_data_science"
    PYTHON_MACHINE_LEARNING = "python_machine_learning"
    DJANGO_PROJECT = "django_project"
    FASTAPI_PROJECT = "fastapi_project"
    GENERAL_PYTHON = "general_python"


class WorkflowType(Enum):
    """工作流类型枚举"""
    DEVELOPMENT = "development"
    CI_CD = "ci_cd"
    PRODUCTION = "production"
    TESTING = "testing"
    CODE_REVIEW = "code_review"


@dataclass
class TemplateMetadata:
    """模板元数据"""
    name: str
    description: str
    version: str
    author: str
    project_type: ProjectType
    workflow_type: WorkflowType
    tags: List[str]
    requirements: List[str]
    created_at: str
    updated_at: str


class BaseTemplate(ABC):
    """模板基类"""

    def __init__(self, metadata: TemplateMetadata):
        """初始化模板

        Args:
            metadata: 模板元数据
        """
        self.metadata = metadata

    @abstractmethod
    def generate_config(self) -> BMADWorkflowConfig:
        """生成配置

        Returns:
            BMADWorkflowConfig: 生成的配置对象
        """
        pass

    @abstractmethod
    def validate_environment(self) -> List[str]:
        """验证环境是否适合使用此模板

        Returns:
            List[str]: 验证错误列表，空列表表示验证通过
        """
        pass

    def save_template(self, output_path: Path) -> None:
        """保存模板到文件

        Args:
            output_path: 输出文件路径
        """
        try:
            template_data = {
                "metadata": asdict(self.metadata),
                "config": asdict(self.generate_config())
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)

            print(f"模板已保存到: {output_path}")

        except Exception as e:
            print(f"保存模板失败: {e}")


class PythonLibraryTemplate(BaseTemplate):
    """Python库项目模板"""

    def __init__(self):
        metadata = TemplateMetadata(
            name="Python Library Template",
            description="适用于Python库项目的BMAD工作流模板，包含严格的类型检查和全面的代码质量分析",
            version="1.0.0",
            author="BMAD Team",
            project_type=ProjectType.PYTHON_LIBRARY,
            workflow_type=WorkflowType.DEVELOPMENT,
            tags=["python", "library", "strict", "quality"],
            requirements=["python>=3.8", "basedpyright", "pytest"],
            created_at="2024-01-01",
            updated_at="2024-01-01"
        )
        super().__init__(metadata)

    def generate_config(self) -> BMADWorkflowConfig:
        """生成Python库项目配置"""
        config = BMADWorkflowConfig()

        # 基础配置
        config.project_name = "Python Library"
        config.auto_fix_enabled = True
        config.backup_before_fix = True
        config.git_integration = True

        # 检查器配置
        config.checker.strict_mode = True
        config.checker.type_check_mode = "strict"
        config.checker.python_version = "3.8"
        config.checker.exclude_files = [
            "**/__pycache__/**",
            "**/build/**",
            "**/dist/**",
            "**/.eggs/**",
            "**/tests/**",  # 测试文件通常使用更宽松的检查
        ]

        # 分析器配置
        config.analyzer.auto_classify = True
        config.analyzer.confidence_threshold = 0.8  # 更严格的阈值
        config.analyzer.enable_grouping = True
        config.analyzer.fix_suggestions = True

        # 报告器配置
        config.reporter.include_trends = True
        config.reporter.include_file_comparison = True
        config.reporter.include_category_analysis = True
        config.reporter.include_fix_recommendations = True
        config.reporter.max_error_details = 100

        # 批量处理配置
        config.batch.parallel_processing = True
        config.batch.max_workers = 4
        config.batch.retry_attempts = 3

        return config

    def validate_environment(self) -> List[str]:
        """验证Python库项目环境"""
        errors = []

        # 检查是否有setup.py或pyproject.toml
        if not Path("setup.py").exists() and not Path("pyproject.toml").exists():
            errors.append("未找到setup.py或pyproject.toml文件")

        # 检查是否有src目录
        if not Path("src").exists():
            errors.append("未找到src目录，建议使用src布局")

        return errors


class PythonWebTemplate(BaseTemplate):
    """Python Web应用模板"""

    def __init__(self):
        metadata = TemplateMetadata(
            name="Python Web Application Template",
            description="适用于Python Web应用项目的BMAD工作流模板，平衡开发效率与代码质量",
            version="1.0.0",
            author="BMAD Team",
            project_type=ProjectType.PYTHON_WEB,
            workflow_type=WorkflowType.DEVELOPMENT,
            tags=["python", "web", "django", "fastapi", "balanced"],
            requirements=["python>=3.9", "basedpyright", "django|fastapi"],
            created_at="2024-01-01",
            updated_at="2024-01-01"
        )
        super().__init__(metadata)

    def generate_config(self) -> BMADWorkflowConfig:
        """生成Python Web应用配置"""
        config = BMADWorkflowConfig()

        # 基础配置
        config.project_name = "Python Web Application"
        config.auto_fix_enabled = True
        config.backup_before_fix = True

        # 检查器配置
        config.checker.strict_mode = False  # Web项目通常需要更灵活
        config.checker.type_check_mode = "basic"
        config.checker.python_version = "3.9"
        config.checker.exclude_files = [
            "**/__pycache__/**",
            "**/migrations/**",  # 数据库迁移文件
            "**/venv/**",
            "**/node_modules/**",
            "**/static/**",
            "**/media/**",
        ]

        # 分析器配置
        config.analyzer.auto_classify = True
        config.analyzer.confidence_threshold = 0.7  # 平衡阈值
        config.analyzer.enable_grouping = True
        config.analyzer.fix_suggestions = True

        # 报告器配置
        config.reporter.include_trends = True
        config.reporter.include_file_comparison = False  # Web项目文件变化较大
        config.reporter.include_category_analysis = True
        config.reporter.max_error_details = 50

        return config

    def validate_environment(self) -> List[str]:
        """验证Web应用环境"""
        errors = []

        # 检查常见Web框架文件
        web_files = ["manage.py", "wsgi.py", "asgi.py", "requirements.txt"]
        if not any(Path(f).exists() for f in web_files):
            errors.append("未检测到常见的Web项目文件")

        return errors


class DataScienceTemplate(BaseTemplate):
    """数据科学项目模板"""

    def __init__(self):
        metadata = TemplateMetadata(
            name="Data Science Project Template",
            description="适用于数据科学项目的BMAD工作流模板，重视Jupyter notebooks和数据处理脚本",
            version="1.0.0",
            author="BMAD Team",
            project_type=ProjectType.PYTHON_DATA_SCIENCE,
            workflow_type=WorkflowType.DEVELOPMENT,
            tags=["python", "data-science", "jupyter", "pandas", "numpy"],
            requirements=["python>=3.9", "basedpyright", "jupyter", "pandas"],
            created_at="2024-01-01",
            updated_at="2024-01-01"
        )
        super().__init__(metadata)

    def generate_config(self) -> BMADWorkflowConfig:
        """生成数据科学项目配置"""
        config = BMADWorkflowConfig()

        # 基础配置
        config.project_name = "Data Science Project"
        config.auto_fix_enabled = False  # 数据科学项目需要更谨慎的自动修复
        config.backup_before_fix = True

        # 检查器配置
        config.checker.strict_mode = False
        config.checker.type_check_mode = "basic"
        config.checker.include_files = [
            "**/*.py",
            "!**/notebooks/**",  # Jupyter notebooks通常单独处理
        ]

        # 分析器配置
        config.analyzer.auto_classify = True
        config.analyzer.confidence_threshold = 0.6  # 更宽松的阈值
        config.analyzer.enable_grouping = True
        config.analyzer.fix_suggestions = True

        # 报告器配置
        config.reporter.include_trends = True
        config.reporter.include_file_comparison = True
        config.reporter.max_error_details = 30

        return config

    def validate_environment(self) -> List[str]:
        """验证数据科学项目环境"""
        errors = []

        # 检查常见数据科学文件
        ds_files = ["requirements.txt", "environment.yml", "Dockerfile"]
        if not any(Path(f).exists() for f in ds_files):
            errors.append("未检测到依赖管理文件")

        return errors


class CICDTemplate(BaseTemplate):
    """CI/CD流水线模板"""

    def __init__(self):
        metadata = TemplateMetadata(
            name="CI/CD Pipeline Template",
            description="适用于CI/CD流水线的BMAD工作流模板，重点关注自动化和质量门禁",
            version="1.0.0",
            author="BMAD Team",
            project_type=ProjectType.GENERAL_PYTHON,
            workflow_type=WorkflowType.CI_CD,
            tags=["ci-cd", "automation", "quality-gate", "production"],
            requirements=["python>=3.8", "basedpyright", "git"],
            created_at="2024-01-01",
            updated_at="2024-01-01"
        )
        super().__init__(metadata)

    def generate_config(self) -> BMADWorkflowConfig:
        """生成CI/CD配置"""
        config = BMADWorkflowConfig()

        # 基础配置
        config.project_name = "CI/CD Pipeline"
        config.auto_fix_enabled = False  # CI/CD环境不自动修复
        config.backup_before_fix = False
        config.git_integration = True

        # 检查器配置
        config.checker.strict_mode = True
        config.checker.type_check_mode = "strict"
        config.checker.timeout_seconds = 600  # CI/CD环境可能需要更长时间

        # 分析器配置
        config.analyzer.auto_classify = True
        config.analyzer.confidence_threshold = 0.9  # 生产环境需要高置信度
        config.analyzer.enable_grouping = True
        config.analyzer.fix_suggestions = False  # CI/CD不提供修复建议

        # 报告器配置
        config.reporter.include_trends = False  # CI/CD通常不需要趋势分析
        config.reporter.include_file_comparison = True
        config.reporter.include_category_analysis = True
        config.reporter.output_formats = ["json", "markdown"]  # CI/CD需要机器可读格式

        # 批量处理配置
        config.batch.parallel_processing = True
        config.batch.max_workers = 2  # CI/CD环境资源有限
        config.batch.retry_attempts = 1  # CI/CD通常不重试

        return config

    def validate_environment(self) -> List[str]:
        """验证CI/CD环境"""
        errors = []

        # 检查CI环境变量
        import os
        if not any(env in os.environ for env in ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "TRAVIS"]):
            errors.append("未检测到CI/CD环境变量")

        return errors


class TemplateManager:
    """模板管理器"""

    def __init__(self):
        """初始化模板管理器"""
        self.templates: Dict[str, BaseTemplate] = {}
        self.template_dir = Path(__file__).parent
        self._load_builtin_templates()

    def _load_builtin_templates(self) -> None:
        """加载内置模板"""
        builtin_templates = [
            ("python_library", PythonLibraryTemplate()),
            ("python_web", PythonWebTemplate()),
            ("data_science", DataScienceTemplate()),
            ("ci_cd", CICDTemplate()),
        ]

        for name, template in builtin_templates:
            self.templates[name] = template

    def list_templates(self) -> List[TemplateMetadata]:
        """列出所有可用模板

        Returns:
            List[TemplateMetadata]: 模板元数据列表
        """
        return [template.metadata for template in self.templates.values()]

    def get_template(self, name: str) -> Optional[BaseTemplate]:
        """获取指定模板

        Args:
            name: 模板名称

        Returns:
            Optional[BaseTemplate]: 模板对象，如果不存在则返回None
        """
        return self.templates.get(name)

    def create_config_from_template(self, template_name: str, project_path: Path = None) -> Optional[BMADWorkflowConfig]:
        """从模板创建配置

        Args:
            template_name: 模板名称
            project_path: 项目路径，用于环境验证

        Returns:
            Optional[BMADWorkflowConfig]: 生成的配置，如果失败则返回None
        """
        template = self.get_template(template_name)
        if not template:
            return None

        # 验证环境
        if project_path:
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(project_path)
                errors = template.validate_environment()
                if errors:
                    print(f"环境验证警告: {', '.join(errors)}")
            finally:
                os.chdir(original_cwd)

        return template.generate_config()

    def save_template_config(self, template_name: str, output_path: Path, project_path: Path = None) -> bool:
        """保存模板配置到文件

        Args:
            template_name: 模板名称
            output_path: 输出文件路径
            project_path: 项目路径

        Returns:
            bool: 是否成功保存
        """
        config = self.create_config_from_template(template_name, project_path)
        if not config:
            return False

        try:
            # 序列化配置
            config_dict = asdict(config)

            # 处理特殊类型
            config_dict = self._serialize_config(config_dict)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)

            print(f"模板配置已保存到: {output_path}")
            return True

        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def _serialize_config(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """序列化配置字典"""
        result = {}

        for key, value in config_dict.items():
            if isinstance(value, Path):
                result[key] = str(value)
            elif hasattr(value, 'value'):  # 枚举类型
                result[key] = value.value
            elif isinstance(value, dict):
                result[key] = self._serialize_config(value)
            elif isinstance(value, list):
                result[key] = [
                    v.value if hasattr(v, 'value') else str(v) if isinstance(v, Path) else v
                    for v in value
                ]
            else:
                result[key] = value

        return result

    def auto_detect_template(self, project_path: Path) -> Optional[str]:
        """自动检测适合的模板

        Args:
            project_path: 项目路径

        Returns:
            Optional[str]: 推荐的模板名称
        """
        import os
        original_cwd = os.getcwd()

        try:
            os.chdir(project_path)

            # 检测CI/CD环境
            import os as env_os
            if any(env in env_os.environ for env in ["CI", "GITHUB_ACTIONS", "GITLAB_CI"]):
                return "ci_cd"

            # 检测Python库项目
            if Path("setup.py").exists() or Path("pyproject.toml").exists():
                if Path("src").exists():
                    return "python_library"

            # 检测Web项目
            web_indicators = [
                "requirements.txt", "Dockerfile", "manage.py",
                "wsgi.py", "asgi.py", ".env.example"
            ]
            if any(Path(f).exists() for f in web_indicators):
                return "python_web"

            # 检测数据科学项目
            ds_indicators = [
                "notebooks", "data", "environment.yml",
                "requirements.txt", "Jupyterfile", "conda.yml"
            ]
            if any(Path(f).exists() for f in ds_indicators):
                return "data_science"

            return "python_library"  # 默认返回库项目模板

        finally:
            os.chdir(original_cwd)

    def register_custom_template(self, name: str, template: BaseTemplate) -> None:
        """注册自定义模板

        Args:
            name: 模板名称
            template: 模板对象
        """
        self.templates[name] = template
        print(f"自定义模板 '{name}' 已注册")


# 全局模板管理器实例
_template_manager: Optional[TemplateManager] = None


def get_template_manager() -> TemplateManager:
    """获取全局模板管理器实例

    Returns:
        TemplateManager: 模板管理器实例
    """
    global _template_manager
    if _template_manager is None:
        _template_manager = TemplateManager()
    return _template_manager