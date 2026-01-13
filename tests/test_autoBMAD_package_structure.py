"""
测试autoBMAD包结构和模块

这些测试验证autoBMAD包的结构、模块组织和导入功能：
- 包结构完整性
- 模块导入功能
- 子包组织
- 包初始化
"""

import sys
from pathlib import Path
import pytest

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestAutoBMADPackageStructure:
    """测试autoBMAD包结构"""

    def test_autoBMAD_package_exists(self):
        """验证autoBMAD包存在"""
        autoBMAD_dir = PROJECT_ROOT / "autoBMAD"
        assert autoBMAD_dir.exists(), "autoBMAD包必须存在"
        assert autoBMAD_dir.is_dir(), "autoBMAD必须是一个目录"

    def test_autoBMAD_has_init_file(self):
        """验证autoBMAD包含__init__.py文件"""
        init_file = PROJECT_ROOT / "autoBMAD" / "__init__.py"
        assert init_file.exists(), "autoBMAD必须包含__init__.py文件"

    def test_autoBMAD_init_has_version(self):
        """验证autoBMAD的__init__.py包含版本信息"""
        init_file = PROJECT_ROOT / "autoBMAD" / "__init__.py"
        content = init_file.read_text(encoding='utf-8')
        assert "__version__" in content, "__init__.py应该定义__version__"

    def test_autoBMAD_has_typed_marker(self):
        """验证autoBMAD包含py.typed标记文件"""
        typed_file = PROJECT_ROOT / "autoBMAD" / "py.typed"
        assert typed_file.exists(), "autoBMAD必须包含py.typed文件"

    def test_autoBMAD_is_importable(self):
        """验证autoBMAD包可以成功导入"""
        try:
            import autoBMAD
            assert autoBMAD is not None, "autoBMAD包应该可以被导入"
        except ImportError as e:
            pytest.fail(f"无法导入autoBMAD包: {e}")

    def test_autoBMAD_has_version_attribute(self):
        """验证autoBMAD包具有版本属性"""
        try:
            import autoBMAD
            assert hasattr(autoBMAD, "__version__"), \
                "autoBMAD应该有__version__属性"
            version = autoBMAD.__version__
            assert version is not None, "__version__不应该为None"
            assert len(version) > 0, "__version__应该包含内容"
        except (ImportError, AttributeError) as e:
            pytest.fail(f"autoBMAD包缺少版本信息: {e}")

    def test_autoBMAD_has_epic_automation_subpackage(self):
        """验证autoBMAD包含epic_automation子包"""
        epic_dir = PROJECT_ROOT / "autoBMAD" / "epic_automation"
        assert epic_dir.exists(), "autoBMAD应该包含epic_automation子包"
        assert epic_dir.is_dir(), "epic_automation必须是一个目录"

    def test_epic_automation_is_valid_package(self):
        """验证epic_automation是有效的Python包"""
        epic_dir = PROJECT_ROOT / "autoBMAD" / "epic_automation"
        init_file = epic_dir / "__init__.py"
        assert init_file.exists(), "epic_automation必须包含__init__.py文件"

    def test_epic_automation_has_modules(self):
        """验证epic_automation包含Python模块"""
        epic_dir = PROJECT_ROOT / "autoBMAD" / "epic_automation"
        py_files = list(epic_dir.glob("*.py"))
        assert len(py_files) > 0, "epic_automation应该包含至少一个Python模块"

    def test_epic_automation_modules_are_valid_python(self):
        """验证epic_automation的模块是有效的Python文件"""
        epic_dir = PROJECT_ROOT / "autoBMAD" / "epic_automation"
        py_files = [f for f in epic_dir.glob("*.py") if not f.name.startswith("__")]

        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(py_file), 'exec')
            except SyntaxError as e:
                pytest.fail(f"{py_file.name}包含语法错误: {e}")

    def test_epic_automation_has_expected_modules(self):
        """验证epic_automation包含预期的模块"""
        epic_dir = PROJECT_ROOT / "autoBMAD" / "epic_automation"
        py_files = [f.name for f in epic_dir.glob("*.py") if not f.name.startswith("__")]

        # 检查至少包含一些核心模块
        expected_modules = [
            "agents.py",
            "epic_driver.py",
            "state_manager.py"
        ]

        # 至少应该有这些模块中的一部分
        found_modules = [mod for mod in expected_modules if mod in py_files]
        assert len(found_modules) >= 2, \
            f"epic_automation应该包含至少2个核心模块，发现: {found_modules}"


class TestAutoBMADSubpackages:
    """测试autoBMAD的子包"""

    def test_all_subpackages_have_init_files(self):
        """验证所有Python子包都包含__init__.py文件"""
        autoBMAD_dir = PROJECT_ROOT / "autoBMAD"

        # 查找所有子目录，但排除文档目录、缓存目录和生成目录
        subdirs = [d for d in autoBMAD_dir.iterdir()
                   if d.is_dir() and not d.name.startswith('.')
                   and d.name not in ['agentdocs', '__pycache__', 'htmlcov']]  # 排除文档、缓存和生成目录

        for subdir in subdirs:
            init_file = subdir / "__init__.py"
            assert init_file.exists(), \
                f"Python子包{subdir.name}必须包含__init__.py文件"

    def test_all_subpackages_are_valid_python(self):
        """验证所有Python子包的__init__.py都是有效的Python文件"""
        autoBMAD_dir = PROJECT_ROOT / "autoBMAD"

        # 查找所有子目录，但排除文档目录、缓存目录和生成目录
        subdirs = [d for d in autoBMAD_dir.iterdir()
                   if d.is_dir() and not d.name.startswith('.')
                   and d.name not in ['agentdocs', '__pycache__', 'htmlcov']]  # 排除文档、缓存和生成目录

        for subdir in subdirs:
            init_file = subdir / "__init__.py"
            if init_file.exists():
                try:
                    with open(init_file, 'r', encoding='utf-8') as f:
                        compile(f.read(), str(init_file), 'exec')
                except SyntaxError as e:
                    pytest.fail(f"{subdir.name}/__init__.py包含语法错误: {e}")

    def test_subpackage_structure_is_consistent(self):
        """验证Python子包结构的一致性"""
        autoBMAD_dir = PROJECT_ROOT / "autoBMAD"

        # 查找所有子目录，但排除文档目录、缓存目录和生成目录
        subdirs = [d for d in autoBMAD_dir.iterdir()
                   if d.is_dir() and not d.name.startswith('.')
                   and d.name not in ['agentdocs', '__pycache__', 'htmlcov']]  # 排除文档、缓存和生成目录

        # 每个Python子包应该至少有__init__.py或.py文件
        for subdir in subdirs:
            py_files = list(subdir.glob("*.py"))
            assert len(py_files) > 0, \
                f"Python子包{subdir.name}应该包含Python文件"



class TestAutoBMADImports:
    """测试autoBMAD的导入功能"""

    def test_can_import_autoBMAD(self):
        """验证可以导入autoBMAD"""
        try:
            import autoBMAD
            assert autoBMAD is not None
        except ImportError as e:
            pytest.fail(f"无法导入autoBMAD: {e}")

    def test_can_import_epic_automation(self):
        """验证可以导入epic_automation子包"""
        try:
            import autoBMAD.epic_automation
            assert autoBMAD.epic_automation is not None
        except ImportError as e:
            pytest.fail(f"无法导入autoBMAD.epic_automation: {e}")

    def test_autoBMAD_has_expected_attributes(self):
        """验证autoBMAD具有预期的属性"""
        try:
            import autoBMAD

            # 检查基本属性
            assert hasattr(autoBMAD, "__version__"), \
                "autoBMAD应该有__version__属性"
            assert hasattr(autoBMAD, "__author__") or hasattr(autoBMAD, "__author__"), \
                "autoBMAD应该有__author__属性"

        except (ImportError, AttributeError) as e:
            pytest.fail(f"autoBMAD缺少预期属性: {e}")


class TestAutoBMADCodeQuality:
    """测试autoBMAD代码质量"""

    def test_all_python_files_use_utf8_encoding(self):
        """验证所有Python文件使用UTF-8编码"""
        autoBMAD_dir = PROJECT_ROOT / "autoBMAD"
        py_files = [f for f in autoBMAD_dir.rglob("*.py")
                    if 'agentdocs' not in str(f)]  # 排除文档目录

        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    f.read()
            except UnicodeDecodeError as e:
                pytest.fail(f"{py_file}不是有效的UTF-8文件: {e}")

    def test_python_files_have_no_syntax_errors(self):
        """验证所有Python文件没有语法错误"""
        autoBMAD_dir = PROJECT_ROOT / "autoBMAD"
        py_files = [f for f in autoBMAD_dir.rglob("*.py")
                    if 'agentdocs' not in str(f)]  # 排除文档目录

        syntax_error_files = []
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(py_file), 'exec')
            except SyntaxError as e:
                syntax_error_files.append((py_file, str(e)))

        if syntax_error_files:
            error_msg = "发现语法错误:\n" + "\n".join(
                [f"  {f}: {e}" for f, e in syntax_error_files]
            )
            pytest.fail(error_msg)

    def test_init_files_are_not_empty(self):
        """验证__init__.py文件不为空（除非故意为空）"""
        autoBMAD_dir = PROJECT_ROOT / "autoBMAD"
        init_files = [f for f in autoBMAD_dir.rglob("__init__.py")
                      if 'agentdocs' not in str(f)]  # 排除文档目录

        for init_file in init_files:
            content = init_file.read_text(encoding='utf-8').strip()
            # 允许空的__init__.py文件，但如果没有__init__.py应该报错
            if init_file.name == "__init__.py" and init_file.parent.name == "autoBMAD":
                assert len(content) > 0, \
                    f"autoBMAD的__init__.py应该包含内容"

    def test_no_debug_statements_in_production_code(self):
        """验证生产代码中没有调试语句（基本检查）"""
        autoBMAD_dir = PROJECT_ROOT / "autoBMAD"
        py_files = [f for f in autoBMAD_dir.rglob("*.py")
                    if 'agentdocs' not in str(f)]  # 排除文档目录

        for py_file in py_files:
            content = py_file.read_text(encoding='utf-8')

            # 检查不应该出现的调试模式
            debug_patterns = ["import pdb", "pdb.set_trace()", "breakpoint()"]
            found_patterns = [pattern for pattern in debug_patterns if pattern in content]

            if found_patterns:
                pytest.fail(f"{py_file}包含调试语句: {found_patterns}")
