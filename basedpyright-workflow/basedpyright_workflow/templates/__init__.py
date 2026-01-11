"""BMAD工作流模板系统

提供预定义的工作流模板，支持不同项目类型和工作流场景的快速配置。
"""

from .manager import (
    BaseTemplate,
    TemplateManager,
    TemplateMetadata,
    ProjectType,
    WorkflowType,
    PythonLibraryTemplate,
    PythonWebTemplate,
    DataScienceTemplate,
    CICDTemplate,
    get_template_manager,
)

__all__ = [
    'BaseTemplate',
    'TemplateManager',
    'TemplateMetadata',
    'ProjectType',
    'WorkflowType',
    'PythonLibraryTemplate',
    'PythonWebTemplate',
    'DataScienceTemplate',
    'CICDTemplate',
    'get_template_manager',
]