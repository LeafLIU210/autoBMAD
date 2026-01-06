"""Test suite for package initialization."""


class TestPackageInit:
    """Test cases for package initialization."""

    def test_version_defined(self):
        """Test that version is defined in the package."""
        import src

        assert hasattr(src, "__version__")
        assert isinstance(src.__version__, str)

    def test_version_format(self):
        """Test that version follows semantic versioning."""
        import src

        version = src.__version__
        parts = version.split(".")
        assert len(parts) >= 2, "Version must have major.minor format"

    def test_author_defined(self):
        """Test that author is defined in the package."""
        import src

        assert hasattr(src, "__author__")
        assert isinstance(src.__author__, str)

    def test_package_import(self):
        """Test that the package can be imported without errors."""
        import src

        assert src is not None

    def test_module_imports(self):
        """Test that all expected modules can be imported."""
        import src
        import src.bubble_sort

        assert hasattr(src, "bubble_sort")
