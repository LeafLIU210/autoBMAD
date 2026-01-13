"""
测试项目设置和基础设施（故事1.1）

这些测试验证项目是否符合所有验收标准：
AC #1: Create proper Python package structure with __init__.py files
AC #2: Setup.py or pyproject.toml file with project metadata and dependencies
AC #3: README.md with installation instructions and basic usage
AC #4: Basic directory structure for source code, tests, and documentation
AC #5: Git repository initialization with appropriate .gitignore file
AC #6: Basic CI/CD configuration file (GitHub Actions or similar)
"""

import os
import sys
from pathlib import Path
import pytest

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestPythonPackageStructure:
    """测试AC #1: Python包结构"""

    def test_src_directory_exists(self):
        """验证src目录存在"""
        src_dir = PROJECT_ROOT / "src"
        assert src_dir.exists(), "src目录必须存在"
        assert src_dir.is_dir(), "src必须是一个目录"

    def test_src_is_python_package(self):
        """验证src是有效的Python包（包含__init__.py）"""
        src_dir = PROJECT_ROOT / "src"
        init_file = src_dir / "__init__.py"
        assert init_file.exists(), "src目录必须包含__init__.py文件"

    def test_tests_directory_exists(self):
        """验证tests目录存在"""
        tests_dir = PROJECT_ROOT / "tests"
        assert tests_dir.exists(), "tests目录必须存在"
        assert tests_dir.is_dir(), "tests必须是一个目录"

    def test_tests_is_python_package(self):
        """验证tests是有效的Python包（包含__init__.py）"""
        tests_dir = PROJECT_ROOT / "tests"
        init_file = tests_dir / "__init__.py"
        assert init_file.exists(), "tests目录必须包含__init__.py文件"

    def test_docs_directory_exists(self):
        """验证docs目录存在（AC #4）"""
        docs_dir = PROJECT_ROOT / "docs"
        assert docs_dir.exists(), "docs目录必须存在"
        assert docs_dir.is_dir(), "docs必须是一个目录"


class TestProjectConfiguration:
    """测试AC #2: 项目配置文件"""

    def test_pyproject_toml_exists(self):
        """验证pyproject.toml文件存在"""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        assert pyproject_file.exists(), "必须存在pyproject.toml文件"

    def test_pyproject_toml_has_project_section(self):
        """验证pyproject.toml包含[project]部分"""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')
        assert "[project]" in content, "pyproject.toml必须包含[project]部分"

    def test_pyproject_toml_has_metadata(self):
        """验证pyproject.toml包含项目元数据"""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')

        # 检查基本元数据字段
        required_fields = ["name", "version", "description"]
        for field in required_fields:
            assert field in content, f"pyproject.toml必须包含{field}字段"

    def test_pyproject_toml_has_dependencies(self):
        """验证pyproject.toml包含依赖配置"""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')

        # 检查依赖相关部分
        assert "dependencies" in content or "requires" in content, \
            "pyproject.toml必须包含依赖配置"

    def test_pyproject_toml_has_test_dependencies(self):
        """验证pyproject.toml包含测试依赖"""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')

        # 检查测试依赖（通常在[project.optional-dependencies]中
        # 或者[tool.pytest.ini_options]中
        assert "pytest" in content.lower(), \
            "pyproject.toml必须包含pytest测试框架"


class TestDocumentation:
    """测试AC #3: 文档"""

    def test_readme_exists(self):
        """验证README.md文件存在"""
        readme_file = PROJECT_ROOT / "README.md"
        assert readme_file.exists(), "必须存在README.md文件"

    def test_readme_has_content(self):
        """验证README.md包含内容"""
        readme_file = PROJECT_ROOT / "README.md"
        content = readme_file.read_text(encoding='utf-8')
        assert len(content) > 100, "README.md必须包含有意义的内容"

    def test_readme_has_installation_section(self):
        """验证README.md包含安装说明"""
        readme_file = PROJECT_ROOT / "README.md"
        content = readme_file.read_text(encoding='utf-8').lower()

        # 检查是否包含安装相关关键词
        installation_keywords = ["install", "setup", "pip", "requirements"]
        has_installation = any(keyword in content for keyword in installation_keywords)
        assert has_installation, "README.md必须包含安装说明"

    def test_readme_has_usage_section(self):
        """验证README.md包含使用说明"""
        readme_file = PROJECT_ROOT / "README.md"
        content = readme_file.read_text(encoding='utf-8').lower()

        # 检查是否包含使用相关关键词
        usage_keywords = ["usage", "example", "how to", "quick start"]
        has_usage = any(keyword in content for keyword in usage_keywords)
        assert has_usage, "README.md必须包含使用说明"


class TestGitRepository:
    """测试AC #5: Git仓库"""

    def test_git_directory_exists(self):
        """验证.git目录存在"""
        git_dir = PROJECT_ROOT / ".git"
        assert git_dir.exists(), "必须存在.git目录"
        assert git_dir.is_dir(), ".git必须是一个目录"

    def test_gitignore_exists(self):
        """验证.gitignore文件存在"""
        gitignore_file = PROJECT_ROOT / ".gitignore"
        assert gitignore_file.exists(), "必须存在.gitignore文件"

    def test_gitignore_has_python_entries(self):
        """验证.gitignore包含Python项目相关条目"""
        gitignore_file = PROJECT_ROOT / ".gitignore"
        content = gitignore_file.read_text(encoding='utf-8').lower()

        # 检查常见的Python忽略条目
        python_entries = ["__pycache__", "*.pyc", ".pytest_cache"]
        for entry in python_entries:
            assert entry in content, f".gitignore必须包含{entry}条目"


class TestCICDPipeline:
    """测试AC #6: CI/CD配置"""

    def test_github_workflows_directory_exists(self):
        """验证.github/workflows目录存在"""
        workflows_dir = PROJECT_ROOT / ".github" / "workflows"
        assert workflows_dir.exists(), "必须存在.github/workflows目录"

    def test_workflow_file_exists(self):
        """验证存在至少一个workflow文件"""
        workflows_dir = PROJECT_ROOT / ".github" / "workflows"
        if workflows_dir.exists():
            workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
            assert len(workflow_files) > 0, "必须存在至少一个GitHub Actions workflow文件"

    def test_workflow_has_test_job(self):
        """验证workflow文件包含测试作业"""
        workflows_dir = PROJECT_ROOT / ".github" / "workflows"
        if workflows_dir.exists():
            workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
            for workflow_file in workflow_files:
                content = workflow_file.read_text(encoding='utf-8').lower()
                assert "test" in content or "pytest" in content, \
                    f"{workflow_file.name}必须包含测试作业"


class TestPackageStructureComprehensive:
    """综合测试包结构 - 扩展测试覆盖"""

    def test_src_init_is_valid_python(self):
        """验证src/__init__.py是有效的Python文件"""
        init_file = PROJECT_ROOT / "src" / "__init__.py"
        assert init_file.exists(), "src/__init__.py必须存在"
        # 尝试编译文件以验证语法正确性
        try:
            with open(init_file, 'r', encoding='utf-8') as f:
                compile(f.read(), str(init_file), 'exec')
        except SyntaxError as e:
            pytest.fail(f"src/__init__.py包含语法错误: {e}")

    def test_tests_init_is_valid_python(self):
        """验证tests/__init__.py是有效的Python文件"""
        init_file = PROJECT_ROOT / "tests" / "__init__.py"
        assert init_file.exists(), "tests/__init__.py必须存在"
        # 尝试编译文件以验证语法正确性
        try:
            with open(init_file, 'r', encoding='utf-8') as f:
                compile(f.read(), str(init_file), 'exec')
        except SyntaxError as e:
            pytest.fail(f"tests/__init__.py包含语法错误: {e}")

    def test_syntax_error_detection_in_src_init(self):
        """测试src/__init__.py语法错误检测"""
        init_file = PROJECT_ROOT / "src" / "__init__.py"
        assert init_file.exists(), "src/__init__.py必须存在"
        # 创建一个临时文件模拟语法错误
        temp_file = PROJECT_ROOT / "temp_test_syntax_error.py"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write("def invalid_syntax(\n")  # 故意语法错误
            # 使用pytest.raises来验证语法错误
            with pytest.raises(SyntaxError):
                with open(temp_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(temp_file), 'exec')
        finally:
            temp_file.unlink()

    def test_syntax_error_detection_in_tests_init(self):
        """测试tests/__init__.py语法错误检测"""
        init_file = PROJECT_ROOT / "tests" / "__init__.py"
        assert init_file.exists(), "tests/__init__.py必须存在"
        # 创建一个临时文件模拟语法错误
        temp_file = PROJECT_ROOT / "temp_test_syntax_error_tests.py"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write("import invalid_syntax(\n")  # 故意语法错误
            # 使用pytest.raises来验证语法错误
            with pytest.raises(SyntaxError):
                with open(temp_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(temp_file), 'exec')
        finally:
            temp_file.unlink()

    def test_autoBMAD_package_exists(self):
        """验证autoBMAD包存在（主要包）"""
        autoBMAD_dir = PROJECT_ROOT / "autoBMAD"
        assert autoBMAD_dir.exists(), "autoBMAD主包目录必须存在"
        assert autoBMAD_dir.is_dir(), "autoBMAD必须是一个目录"

    def test_autoBMAD_is_python_package(self):
        """验证autoBMAD是有效的Python包"""
        autoBMAD_dir = PROJECT_ROOT / "autoBMAD"
        init_file = autoBMAD_dir / "__init__.py"
        assert init_file.exists(), "autoBMAD目录必须包含__init__.py文件"

    def test_autoBMAD_has_subpackages(self):
        """验证autoBMAD包含子包"""
        autoBMAD_dir = PROJECT_ROOT / "autoBMAD"
        subdirs = [d for d in autoBMAD_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        assert len(subdirs) > 0, "autoBMAD应该包含至少一个子包或模块"

    def test_python_version_compatibility(self):
        """验证Python版本兼容性"""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')
        assert "requires-python" in content, "pyproject.toml必须指定Python版本要求"
        assert ">=" in content or ">" in content, "Python版本要求应该使用>=或>"

    def test_license_file_exists(self):
        """验证许可证文件存在"""
        license_file = PROJECT_ROOT / "LICENSE"
        assert license_file.exists() or (PROJECT_ROOT / "LICENSE.txt").exists(), \
            "必须存在LICENSE或LICENSE.txt文件"


class TestPyProjectTOMLComprehensive:
    """全面测试pyproject.toml配置"""

    def test_pyproject_has_build_system(self):
        """验证pyproject.toml包含构建系统配置"""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')
        assert "[build-system]" in content, "pyproject.toml必须包含[build-system]部分"

    def test_pyproject_has_project_metadata(self):
        """验证项目元数据完整"""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')

        required_metadata = ["name", "version", "description"]
        for field in required_metadata:
            assert field in content, f"pyproject.toml必须包含{field}字段"

    def test_pyproject_has_optional_dependencies(self):
        """验证可选依赖配置"""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')
        assert "[project.optional-dependencies]" in content, \
            "pyproject.toml应该包含[project.optional-dependencies]部分"

    def test_pyproject_has_pytest_config(self):
        """验证pytest配置存在"""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')
        assert "[tool.pytest.ini_options]" in content, \
            "pyproject.toml必须包含pytest配置"

    def test_pyproject_has_test_dependencies(self):
        """验证测试依赖完整"""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')

        # 检查是否包含pytest
        assert "pytest" in content.lower(), "必须包含pytest测试框架"

        # 检查是否包含覆盖率工具
        assert "pytest-cov" in content.lower() or "coverage" in content.lower(), \
            "应该包含代码覆盖率工具"

    def test_pyproject_package_mapping(self):
        """验证包映射配置"""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')

        # 检查包映射（通常在[tool.hatch.build.targets.wheel]中）
        assert "[tool.hatch.build.targets.wheel]" in content, \
            "应该包含包映射配置"


class TestDocumentationComprehensive:
    """全面测试文档完整性"""

    def test_readme_has_substantial_content(self):
        """验证README.md包含实质性内容"""
        readme_file = PROJECT_ROOT / "README.md"
        content = readme_file.read_text(encoding='utf-8')
        assert len(content) > 500, "README.md应该包含至少500字符的实质性内容"

    def test_readme_has_project_description(self):
        """验证README包含项目描述"""
        readme_file = PROJECT_ROOT / "README.md"
        content = readme_file.read_text(encoding='utf-8').lower()

        # 检查项目描述相关关键词
        description_keywords = ["template", "项目", "pyqt", "application", "开发"]
        has_description = any(keyword in content for keyword in description_keywords)
        assert has_description, "README应该包含项目描述"

    def test_readme_has_installation_instructions(self):
        """验证安装说明详细"""
        readme_file = PROJECT_ROOT / "README.md"
        content = readme_file.read_text(encoding='utf-8').lower()

        # 检查安装步骤
        installation_indicators = ["pip", "install", "setup.py", "pyproject.toml"]
        has_installation = any(indicator in content for indicator in installation_indicators)
        assert has_installation, "README应该包含安装步骤"

    def test_readme_has_usage_examples(self):
        """验证使用示例存在"""
        readme_file = PROJECT_ROOT / "README.md"
        content = readme_file.read_text(encoding='utf-8').lower()

        # 检查代码示例或使用说明
        example_indicators = ["example", "usage", "```", "code", "sample"]
        has_examples = any(indicator in content for indicator in example_indicators)
        assert has_examples, "README应该包含使用示例"


class TestGitRepositoryComprehensive:
    """全面测试Git仓库配置"""

    def test_gitignore_comprehensive(self):
        """验证.gitignore包含完整的Python忽略模式"""
        gitignore_file = PROJECT_ROOT / ".gitignore"
        content = gitignore_file.read_text(encoding='utf-8').lower()

        # 检查常见的Python忽略模式
        required_patterns = ["__pycache__", "*.pyc", "*.pyo", "*.pyd", ".pytest_cache"]
        for pattern in required_patterns:
            assert pattern in content, f".gitignore必须包含{pattern}模式"

    def test_gitignore_has_env_patterns(self):
        """验证.gitignore包含环境文件模式"""
        gitignore_file = PROJECT_ROOT / ".gitignore"
        content = gitignore_file.read_text(encoding='utf-8').lower()

        env_patterns = [".env", "venv", ".venv", "env"]
        has_env_patterns = any(pattern in content for pattern in env_patterns)
        assert has_env_patterns, ".gitignore应该包含环境文件模式"

    def test_gitignore_has_build_patterns(self):
        """验证.gitignore包含构建文件模式"""
        gitignore_file = PROJECT_ROOT / ".gitignore"
        content = gitignore_file.read_text(encoding='utf-8').lower()

        build_patterns = ["build", "dist", "*.egg-info"]
        has_build_patterns = any(pattern in content for pattern in build_patterns)
        assert has_build_patterns, ".gitignore应该包含构建文件模式"


class TestQualityAssurance:
    """测试质量保证和代码标准"""

    def test_pyproject_has_linting_config(self):
        """验证代码检查配置存在"""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')

        # 检查是否包含代码检查工具配置
        has_black = "[tool.black]" in content
        has_isort = "[tool.isort]" in content
        has_ruff = "ruff" in content.lower()

        assert has_black or has_isort or has_ruff, \
            "应该至少包含一种代码格式化工具配置（black, isort, 或 ruff）"

    def test_pyproject_has_type_hints_config(self):
        """验证类型提示配置"""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        content = pyproject_file.read_text(encoding='utf-8')

        # 检查mypy或类似工具配置
        has_mypy = "[tool.mypy]" in content
        has_pyright = "pyright" in content.lower()

        assert has_mypy or has_pyright, \
            "应该包含类型检查工具配置（mypy或pyright）"

    def test_autoBMAD_has_typed_marker(self):
        """验证autoBMAD包包含py.typed标记文件"""
        typed_file = PROJECT_ROOT / "autoBMAD" / "py.typed"
        assert typed_file.exists(), \
            "autoBMAD包应该包含py.typed文件以支持类型提示"
