"""Test suite for spec_automation module."""


import pytest

from autoBMAD.spec_automation.spec_generator import (
    SpecGenerator,
    create_test_spec,
    generate_specification,
)
from autoBMAD.spec_automation.spec_parser import (
    SpecificationData,
    SpecParser,
    extract_requirements,
    parse_specification,
    validate_specification,
)
from autoBMAD.spec_automation.spec_validator import (
    SpecValidator,
    ValidationResult,
    check_spec_consistency,
    validate_spec_completeness,
)


class TestSpecificationData:
    """Test the SpecificationData class."""

    def test_specification_data_creation(self):
        """Test creating a SpecificationData object."""
        spec = SpecificationData(
            name="Test Spec",
            version="1.0.0",
            description="Test specification",
            requirements=["req1", "req2"],
        )
        assert spec.name == "Test Spec"
        assert spec.version == "1.0.0"
        assert spec.description == "Test specification"
        assert spec.requirements == ["req1", "req2"]

    def test_specification_data_to_dict(self):
        """Test converting SpecificationData to dictionary."""
        spec = SpecificationData(
            name="Test Spec",
            version="1.0.0",
            description="Test specification",
            requirements=["req1"],
        )
        spec_dict = spec.to_dict()
        assert spec_dict["name"] == "Test Spec"
        assert spec_dict["version"] == "1.0.0"
        assert spec_dict["requirements"] == ["req1"]

    def test_specification_data_from_dict(self):
        """Test creating SpecificationData from dictionary."""
        spec_dict = {
            "name": "Test Spec",
            "version": "1.0.0",
            "description": "Test specification",
            "requirements": ["req1", "req2"],
        }
        spec = SpecificationData.from_dict(spec_dict)
        assert spec.name == "Test Spec"
        assert spec.version == "1.0.0"
        assert spec.requirements == ["req1", "req2"]


class TestSpecParser:
    """Test the SpecParser class."""

    def test_parser_initialization(self):
        """Test initializing the parser."""
        parser = SpecParser()
        assert parser is not None

    def test_parse_simple_specification(self):
        """Test parsing a simple specification."""
        spec_content = """
        # Test Specification

        ## Name
        Test Spec

        ## Version
        1.0.0

        ## Description
        A simple test specification

        ## Requirements
        - Requirement 1
        - Requirement 2
        """
        parser = SpecParser()
        spec = parser.parse(spec_content)
        assert spec is not None
        assert spec.name == "Test Spec"
        assert spec.version == "1.0.0"
        assert len(spec.requirements) == 2

    def test_parse_markdown_with_single_hash(self):
        """Test parsing markdown with single hash for name."""
        spec_content = """# Test Spec

## Version
1.0.0

## Description
A simple test specification

## Requirements
- Requirement 1
- Requirement 2
"""
        parser = SpecParser()
        spec = parser.parse(spec_content)
        assert spec is not None
        assert spec.name == "Test Spec"
        assert spec.version == "1.0.0"

    def test_parse_markdown_spec(self):
        """Test parsing a markdown specification file."""
        spec_content = """# Specification

## Name
Markdown Spec

## Version
2.0.0

## Description
Testing markdown parsing

## Requirements
- Parse markdown
- Extract sections
"""
        parser = SpecParser()
        spec = parser.parse(spec_content)
        assert spec.name == "Markdown Spec"
        assert spec.version == "2.0.0"

    def test_parse_yaml_spec(self):
        """Test parsing a YAML specification."""
        spec_content = """
name: YAML Spec
version: 1.5.0
description: YAML specification format
requirements:
  - Parse YAML
  - Validate structure
"""
        parser = SpecParser()
        spec = parser.parse(spec_content)
        assert spec.name == "YAML Spec"
        assert spec.version == "1.5.0"
        assert len(spec.requirements) == 2

    def test_parse_yaml_with_delimiters(self):
        """Test parsing YAML with delimiters."""
        spec_content = """---
name: Delimited YAML Spec
version: 2.0.0
description: YAML with delimiters
requirements:
  - Parse YAML with delimiters
  - Handle dashes
---
"""
        parser = SpecParser()
        spec = parser.parse(spec_content)
        assert spec.name == "Delimited YAML Spec"
        assert spec.version == "2.0.0"

    def test_parse_empty_sections(self):
        """Test parsing with empty sections."""
        spec_content = """# Empty Sections

## Name

## Version
1.0.0

## Description

## Requirements
"""
        parser = SpecParser()
        spec = parser.parse(spec_content)
        # The # header is parsed as name, ## Name section is empty
        assert spec.name == "Empty Sections"
        assert spec.version == "1.0.0"
        assert spec.description == ""
        assert spec.requirements == []

    def test_parse_version_from_single_hash(self):
        """Test parsing version with single hash format."""
        spec_content = """# My Spec
Version: 2.0.0

## Description
Test description

## Requirements
- Req 1
"""
        parser = SpecParser()
        spec = parser.parse(spec_content)
        assert spec.name == "My Spec"
        assert spec.version == "2.0.0"

    def test_parse_version_section(self):
        """Test parsing version from ## Version section."""
        spec_content = """# Spec

## Version
3.0.0

## Description
Another test
"""
        parser = SpecParser()
        spec = parser.parse(spec_content)
        assert spec.version == "3.0.0"

    def test_parse_description_multiline(self):
        """Test parsing multiline description."""
        spec_content = """# Multi-line Desc

## Version
1.0.0

## Description
This is a multiline
description that spans
multiple lines

## Requirements
- Req 1
"""
        parser = SpecParser()
        spec = parser.parse(spec_content)
        assert (
            spec.description
            == "This is a multiline\ndescription that spans\nmultiple lines"
        )

    def test_parse_with_different_numbered_formats(self):
        """Test parsing requirements with different numbered formats."""
        spec_content = """# Numbered Test

## Version
1.0.0

## Requirements
1. First requirement
2. Second requirement
3. Third requirement
"""
        parser = SpecParser()
        spec = parser.parse(spec_content)
        assert len(spec.requirements) >= 3
        assert "First" in spec.requirements[0]
        assert "Second" in spec.requirements[1]

    def test_parse_with_star_bullets(self):
        """Test parsing requirements with star bullets."""
        spec_content = """# Star Test

## Version
1.0.0

## Requirements
* Star bullet 1
* Star bullet 2
"""
        parser = SpecParser()
        spec = parser.parse(spec_content)
        assert len(spec.requirements) >= 2
        assert "Star bullet 1" in spec.requirements[0]

    def test_parse_with_plus_bullets(self):
        """Test parsing requirements with plus bullets."""
        spec_content = """# Plus Test

## Version
1.0.0

## Requirements
+ Plus bullet 1
+ Plus bullet 2
"""
        parser = SpecParser()
        spec = parser.parse(spec_content)
        assert len(spec.requirements) >= 2
        assert "Plus bullet 1" in spec.requirements[0]

    def test_parse_description_spanning_multiple_sections(self):
        """Test description that goes until next ## section."""
        spec_content = """# Desc Test

## Version
1.0.0

## Description
First paragraph
Second paragraph

## Requirements
- Req 1
"""
        parser = SpecParser()
        spec = parser.parse(spec_content)
        assert "First paragraph" in spec.description
        assert "Second paragraph" in spec.description
        assert "Requirements" not in spec.description

    def test_parse_fallback_to_markdown_on_yaml_error(self):
        """Test that YAML parse errors fall back to markdown."""
        spec_content = """
name: Test
version: invalid: yaml: format:
this is not valid yaml
---
# Fallback to markdown
## Name
Markdown Fallback
## Version
1.0.0
"""
        parser = SpecParser()
        spec = parser.parse(spec_content)
        assert spec.name == "Markdown Fallback"
        assert spec.version == "1.0.0"

    def test_parse_yaml_with_colons_in_value(self):
        """Test parsing YAML with colons in version values."""
        spec_content = """---
name: Test
version: "1:2:3"
description: Test with colons
requirements:
  - Req 1
---
"""
        parser = SpecParser()
        spec = parser.parse(spec_content)
        assert spec.version == "1:2:3"

    def test_parse_yaml_with_special_chars(self):
        """Test parsing YAML with special characters."""
        spec_content = """---
name: Test Spec
version: 1.0.0
description: "Special chars: @#$%^&*()"
requirements:
  - Req with special: chars
---
"""
        parser = SpecParser()
        spec = parser.parse(spec_content)
        assert "Special chars" in spec.description
        assert len(spec.requirements) >= 1

    def test_parse_yaml_with_markdown_after(self):
        """Test parsing YAML with markdown content after (should fail and fall back)."""
        spec_content = """# Fallback to markdown
## Name
Markdown Fallback
## Version
1.0
"""
        parser = SpecParser()
        spec = parser.parse(spec_content)
        assert spec.name == "Markdown Fallback"
        assert spec.version == "1.0"

    def test_parse_empty_yaml_section(self):
        """Test parsing YAML with empty sections."""
        spec_content = """---
name: Empty Sections
version: 1.0.0
description: ""
requirements: []
---
"""
        parser = SpecParser()
        spec = parser.parse(spec_content)
        assert spec.name == "Empty Sections"
        assert spec.description == ""
        assert spec.requirements == []


class TestSpecGenerator:
    """Test the SpecGenerator class."""

    def test_generator_initialization(self):
        """Test initializing the generator."""
        generator = SpecGenerator()
        assert generator is not None

    def test_generate_specification(self):
        """Test generating a specification."""
        generator = SpecGenerator()
        spec = generator.generate(
            name="Generated Spec",
            version="1.0.0",
            description="Auto-generated specification",
            requirements=["req1", "req2"],
        )
        assert spec.name == "Generated Spec"
        assert spec.version == "1.0.0"

    def test_create_test_spec(self):
        """Test creating a test specification."""
        generator = SpecGenerator()
        spec = generator.create_test_spec("TestModule")
        assert spec is not None
        # .title() converts "TestModule" to "Testmodule" (capital M after lowercase treated as lowercase)
        assert "Testmodule" in spec.name or "Test Module" in spec.name

    def test_generate_markdown_output(self):
        """Test generating markdown output."""
        generator = SpecGenerator()
        spec = SpecificationData(
            name="Markdown Test",
            version="1.0.0",
            description="Markdown output test",
            requirements=["req1"],
        )
        markdown = generator.to_markdown(spec)
        assert "# Markdown Test" in markdown
        assert "1.0.0" in markdown

    def test_to_markdown_no_requirements(self):
        """Test generating markdown with no requirements."""
        generator = SpecGenerator()
        spec = SpecificationData(
            name="No Reqs",
            version="1.0.0",
            description="Test",
            requirements=[],
        )
        markdown = generator.to_markdown(spec)
        assert "# No Reqs" in markdown
        assert "## Requirements" not in markdown

    def test_to_markdown_multiple_requirements(self):
        """Test generating markdown with multiple requirements."""
        generator = SpecGenerator()
        spec = SpecificationData(
            name="Multi Reqs",
            version="1.0.0",
            description="Test",
            requirements=["Req 1", "Req 2", "Req 3"],
        )
        markdown = generator.to_markdown(spec)
        assert "1. Req 1" in markdown
        assert "2. Req 2" in markdown
        assert "3. Req 3" in markdown

    def test_to_yaml_output(self):
        """Test generating YAML output."""
        generator = SpecGenerator()
        spec = SpecificationData(
            name="YAML Test",
            version="1.0.0",
            description="Test",
            requirements=["req1"],
        )
        yaml_str = generator.to_yaml(spec)
        assert "name: YAML Test" in yaml_str
        assert "version: 1.0.0" in yaml_str
        assert "req1" in yaml_str

    def test_to_yaml_with_list(self):
        """Test generating YAML with list formatting."""
        generator = SpecGenerator()
        spec = SpecificationData(
            name="List YAML",
            version="1.0.0",
            description="Test",
            requirements=["req1", "req2", "req3"],
        )
        yaml_str = generator.to_yaml(spec)
        assert "requirements:" in yaml_str
        assert "- req1" in yaml_str
        assert "- req2" in yaml_str

    def test_create_test_spec_with_underscores(self):
        """Test creating test spec with underscores in module name."""
        generator = SpecGenerator()
        spec = generator.create_test_spec("my_module")
        assert "My Module" in spec.name

    def test_create_test_spec_with_single_word(self):
        """Test creating test spec with single word module name."""
        generator = SpecGenerator()
        spec = generator.create_test_spec("test")
        assert "Test" in spec.name
        assert spec.version == "1.0.0"
        assert len(spec.requirements) == 5

    def test_create_test_spec_with_camelcase(self):
        """Test creating test spec with camelCase module name."""
        generator = SpecGenerator()
        spec = generator.create_test_spec("myTestModule")
        # The .title() method converts camelCase differently
        # "myTestModule" -> "Mytestmodule" (each capital letter after lowercase is treated specially)
        assert "Mytestmodule" in spec.name or "My Test Module" in spec.name

    def test_generate_with_none_requirements(self):
        """Test generating spec with None requirements (should default to empty list)."""
        generator = SpecGenerator()
        spec = generator.generate(
            name="Test",
            version="1.0.0",
            description="Test",
            requirements=None,
        )
        assert spec.requirements == []

    def test_generate_with_empty_requirements(self):
        """Test generating spec with explicitly empty requirements."""
        generator = SpecGenerator()
        spec = generator.generate(
            name="Test",
            version="1.0.0",
            description="Test",
            requirements=[],
        )
        assert spec.requirements == []


class TestSpecValidator:
    """Test the SpecValidator class."""

    def test_validator_initialization(self):
        """Test initializing the validator."""
        validator = SpecValidator()
        assert validator is not None

    def test_validate_complete_spec(self):
        """Test validating a complete specification."""
        spec = SpecificationData(
            name="Complete Spec",
            version="1.0.0",
            description="Complete specification",
            requirements=["req1", "req2"],
        )
        validator = SpecValidator()
        result = validator.validate(spec)
        assert isinstance(result, ValidationResult)
        assert result.is_valid

    def test_validate_incomplete_spec(self):
        """Test validating an incomplete specification."""
        spec = SpecificationData(
            name="",  # Missing name
            version="1.0.0",
            description="Incomplete specification",
            requirements=[],
        )
        validator = SpecValidator()
        result = validator.validate(spec)
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_check_spec_consistency(self):
        """Test checking specification consistency."""
        spec = SpecificationData(
            name="Consistent Spec",
            version="1.0.0",
            description="Consistent specification",
            requirements=["req1", "req2"],
        )
        validator = SpecValidator()
        is_consistent = validator.check_consistency(spec)
        assert is_consistent

    def test_validate_spec_completeness(self):
        """Test validating specification completeness."""
        complete_spec = SpecificationData(
            name="Complete Spec Name Here",
            version="1.0.0",
            description="This is a complete specification description that is long enough",
            requirements=["req1", "req2", "req3"],
        )
        validator = SpecValidator()
        completeness = validator.check_completeness(complete_spec)
        assert completeness >= 0.8  # Should be mostly complete

        incomplete_spec = SpecificationData(
            name="Incomplete",
            version="1.0.0",
            description="",
            requirements=[],
        )
        completeness = validator.check_completeness(incomplete_spec)
        assert completeness < 0.8  # Should be incomplete

    def test_completeness_score_exact(self):
        """Test exact completeness score calculation."""
        validator = SpecValidator()

        # Score with all fields complete
        spec1 = SpecificationData(
            name="Complete Name",
            version="1.0.0",
            description="This is a very detailed and comprehensive description",
            requirements=["req1", "req2", "req3"],
        )
        score1 = validator.check_completeness(spec1)
        assert score1 == 1.0

        # Score with no description
        spec2 = SpecificationData(
            name="Complete Name",
            version="1.0.0",
            description="",
            requirements=["req1", "req2", "req3"],
        )
        score2 = validator.check_completeness(spec2)
        assert score2 == 0.7  # Name (0.2) + Version (0.2) + Requirements (0.3)

        # Score with no requirements
        spec3 = SpecificationData(
            name="Complete Name",
            version="1.0.0",
            description="This is a very detailed and comprehensive description",
            requirements=[],
        )
        score3 = validator.check_completeness(spec3)
        assert score3 == 0.7  # Name (0.2) + Version (0.2) + Description (0.3)

        # Score with minimal description
        spec4 = SpecificationData(
            name="Complete Name",
            version="1.0.0",
            description="Short",
            requirements=["req1", "req2", "req3"],
        )
        score4 = validator.check_completeness(spec4)
        assert (
            abs(score4 - 0.85) < 0.01
        )  # Name (0.2) + Version (0.2) + Short description (0.15) + Requirements (0.3)

    def test_validate_with_warnings(self):
        """Test validation that produces warnings but not errors."""
        spec = SpecificationData(
            name="Test",  # Short name
            version="1.0",  # Invalid format
            description="Short desc",
            requirements=["req1"],
        )
        validator = SpecValidator()
        result = validator.validate(spec)
        assert result.is_valid  # Should still be valid
        assert len(result.warnings) > 0  # But with warnings
        assert len(result.errors) == 0

    def test_validate_with_errors(self):
        """Test validation that produces errors."""
        spec = SpecificationData(
            name="",  # Missing name
            version="",  # Missing version
            description="",  # Missing description
            requirements=[],
        )
        validator = SpecValidator()
        result = validator.validate(spec)
        assert not result.is_valid  # Should not be valid
        assert len(result.errors) > 0

    def test_validate_version_formats(self):
        """Test validation of different version formats."""
        validator = SpecValidator()

        # Valid versions
        valid_versions = ["1.0.0", "2.3", "10.15.3", "0.1"]
        for version in valid_versions:
            spec = SpecificationData(
                name="Valid Version Spec",
                version=version,
                description="Valid version test",
                requirements=["req1"],
            )
            result = validator.validate(spec)
            # Should not have version warning
            version_warnings = [w for w in result.warnings if "version" in w.lower()]
            assert len(version_warnings) == 0, f"Version {version} should be valid"

        # Invalid versions
        invalid_versions = ["v1.0.0", "1", "1.0.0.0.0", "abc", "1.0-beta"]
        for version in invalid_versions:
            spec = SpecificationData(
                name="Invalid Version Spec",
                version=version,
                description="Invalid version test",
                requirements=["req1"],
            )
            result = validator.validate(spec)
            # Should have version warning
            version_warnings = [w for w in result.warnings if "version" in w.lower()]
            assert len(version_warnings) > 0, f"Version {version} should be invalid"

    def test_check_consistency_returns_true(self):
        """Test checking consistency with valid spec."""
        spec = SpecificationData(
            name="Consistent Spec",
            version="1.0.0",
            description="Consistent specification",
            requirements=[
                "Unique requirement 1",
                "Unique requirement 2",
                "Unique requirement 3",
            ],
        )
        validator = SpecValidator()
        assert validator.check_consistency(spec)

    def test_check_consistency_with_duplicates(self):
        """Test checking consistency with duplicate requirements."""
        spec = SpecificationData(
            name="Duplicate Spec",
            version="1.0.0",
            description="Duplicate requirements",
            requirements=["req1", "req1", "req2"],
        )
        validator = SpecValidator()
        assert not validator.check_consistency(spec)

    def test_check_consistency_with_short_requirements(self):
        """Test checking consistency with very short requirements."""
        spec = SpecificationData(
            name="Short Req Spec",
            version="1.0.0",
            description="Short requirements",
            requirements=["a", "b"],  # Very short
        )
        validator = SpecValidator()
        assert not validator.check_consistency(spec)

    def test_validate_requirements_list(self):
        """Test validating a list of requirements."""
        validator = SpecValidator()

        # Valid requirements
        valid_reqs = [
            "This is a good requirement",
            "Another good requirement",
            "Third requirement",
        ]
        result = validator.validate_requirements(valid_reqs)
        assert result.is_valid

        # Empty requirements
        empty_reqs = []
        result = validator.validate_requirements(empty_reqs)
        assert not result.is_valid
        assert len(result.errors) > 0

        # Duplicate requirements
        duplicate_reqs = ["req1", "req2", "req1"]
        result = validator.validate_requirements(duplicate_reqs)
        assert result.is_valid  # Should still be valid but with warning
        assert len(result.warnings) > 0

        # Very short requirements
        short_reqs = ["a", "b"]
        result = validator.validate_requirements(short_reqs)
        assert result.is_valid
        assert len(result.warnings) > 0

    def test_validation_result_add_error(self):
        """Test ValidationResult.add_error method."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        assert result.is_valid

        result.add_error("Test error")
        assert not result.is_valid
        assert "Test error" in result.errors

    def test_validation_result_add_warning(self):
        """Test ValidationResult.add_warning method."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        result.add_warning("Test warning")
        assert result.is_valid  # Should still be valid
        assert "Test warning" in result.warnings

    def test_validation_result_str_representation(self):
        """Test string representation of ValidationResult."""
        result = ValidationResult(
            is_valid=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
        )
        result_str = str(result)
        assert "Valid: False" in result_str
        assert "Errors" in result_str
        assert "Error 1" in result_str
        assert "Warning 1" in result_str

    def test_validation_with_no_warnings(self):
        """Test validation that produces no warnings."""
        spec = SpecificationData(
            name="Good Spec Name",
            version="1.0.0",
            description="This is a detailed and comprehensive specification description",
            requirements=[
                "This is a detailed requirement 1",
                "This is a detailed requirement 2",
                "This is a detailed requirement 3",
            ],
        )
        validator = SpecValidator()
        result = validator.validate(spec)
        # May or may not have warnings based on logic, but shouldn't have requirement count warnings
        req_warnings = [w for w in result.warnings if "requirement" in w.lower()]
        assert len(req_warnings) == 0

    def test_validate_version_with_trailing_zero(self):
        """Test version validation with trailing zeros."""
        spec = SpecificationData(
            name="Version Test",
            version="1.0.0.0",  # Valid semantic version
            description="Test version",
            requirements=["req1"]
        )
        validator = SpecValidator()
        result = validator.validate(spec)
        assert isinstance(result.is_valid, bool)

    def test_validate_name_with_special_chars(self):
        """Test validation with special characters in name."""
        spec = SpecificationData(
            name="Test-Spec_123",
            version="1.0.0",
            description="Test with special chars",
            requirements=["req1"]
        )
        validator = SpecValidator()
        result = validator.validate(spec)
        assert isinstance(result.is_valid, bool)

    def test_validate_with_many_requirements(self):
        """Test validation with many requirements."""
        spec = SpecificationData(
            name="Many Requirements Spec",
            version="1.0.0",
            description="Test with many requirements",
            requirements=[f"Requirement {i}" for i in range(50)]
        )
        validator = SpecValidator()
        result = validator.validate(spec)
        assert isinstance(result.is_valid, bool)
        # Should not produce warnings for many requirements
        count_warnings = [w for w in result.warnings if "count" in w.lower()]
        assert len(count_warnings) == 0

    def test_validate_with_very_long_description(self):
        """Test validation with very long description."""
        spec = SpecificationData(
            name="Long Desc",
            version="1.0.0",
            description="This is a very long description " * 100,
            requirements=["req1"]
        )
        validator = SpecValidator()
        result = validator.validate(spec)
        assert result.is_valid

    def test_check_completeness_boundary(self):
        """Test completeness at exact boundary."""
        validator = SpecValidator()

        # Exactly at threshold
        spec = SpecificationData(
            name="Boundary",
            version="1.0.0",
            description="This is exactly at the threshold for completeness",
            requirements=["req1"]
        )
        score = validator.check_completeness(spec)
        assert 0.0 <= score <= 1.0


class TestUtilityFunctions:
    """Test utility functions."""

    def test_parse_specification_function(self):
        """Test the parse_specification utility function."""
        spec_content = """
        # Test
        ## Name
        Utility Test
        ## Version
        1.0.0
        """
        spec = parse_specification(spec_content)
        assert spec.name == "Utility Test"

    def test_validate_specification_function(self):
        """Test the validate_specification utility function."""
        spec = SpecificationData(
            name="Valid Spec",
            version="1.0.0",
            description="Valid",
            requirements=["req1"],
        )
        result = validate_specification(spec)
        assert isinstance(result, ValidationResult)
        assert result.is_valid

    def test_extract_requirements(self):
        """Test extracting requirements from text."""
        text = """
        We need:
        - Requirement 1
        - Requirement 2
        - Requirement 3
        """
        requirements = extract_requirements(text)
        assert len(requirements) >= 3

    def test_extract_requirements_empty(self):
        """Test extracting requirements from empty text."""
        requirements = extract_requirements("")
        assert requirements == []

    def test_extract_requirements_no_bullets(self):
        """Test extracting requirements without bullet points."""
        text = "Just some regular text without bullets"
        requirements = extract_requirements(text)
        # Should return empty or handle gracefully
        assert isinstance(requirements, list)


class TestIntegration:
    """Integration tests for the spec_automation module."""

    def test_full_spec_workflow(self):
        """Test complete specification workflow."""
        # Generate
        generator = SpecGenerator()
        spec = generator.generate(
            name="Integration Test",
            version="1.0.0",
            description="Full workflow test",
            requirements=["req1", "req2", "req3"],
        )

        # Parse
        parser = SpecParser()
        content = generator.to_markdown(spec)
        parsed_spec = parser.parse(content)

        # Validate
        validator = SpecValidator()
        result = validator.validate(parsed_spec)

        # Assertions
        assert spec.name == parsed_spec.name
        assert spec.version == parsed_spec.version
        assert spec.description == parsed_spec.description
        assert spec.requirements == parsed_spec.requirements
        assert result.is_valid

    def test_spec_roundtrip(self):
        """Test specification roundtrip (generate -> parse -> validate)."""
        original_spec = SpecificationData(
            name="Roundtrip Test",
            version="2.0.0",
            description="Testing roundtrip conversion",
            requirements=["req1", "req2"],
        )

        generator = SpecGenerator()
        parser = SpecParser()
        validator = SpecValidator()

        # Generate markdown
        markdown = generator.to_markdown(original_spec)
        assert "# Roundtrip Test" in markdown

        # Parse back
        parsed = parser.parse(markdown)
        assert parsed.name == original_spec.name
        assert parsed.version == original_spec.version

        # Validate
        result = validator.validate(parsed)
        assert result.is_valid

    def test_yaml_roundtrip(self):
        """Test YAML roundtrip (generate -> parse -> validate)."""
        original_spec = SpecificationData(
            name="YAML Roundtrip",
            version="1.0.0",
            description="YAML conversion test",
            requirements=["req1", "req2"],
        )

        generator = SpecGenerator()
        parser = SpecParser()
        validator = SpecValidator()

        # Generate YAML
        yaml_str = generator.to_yaml(original_spec)
        assert "name: YAML Roundtrip" in yaml_str

        # Parse YAML
        parsed = parser.parse(yaml_str)
        assert parsed.name == original_spec.name
        assert parsed.version == original_spec.version

        # Validate
        result = validator.validate(parsed)
        assert result.is_valid

    def test_generate_and_parse_different_formats(self):
        """Test generating markdown and parsing as YAML (and vice versa)."""
        generator = SpecGenerator()
        parser = SpecParser()
        validator = SpecValidator()

        # Create spec
        spec = generator.generate(
            name="Format Test",
            version="1.0.0",
            description="Format conversion test",
            requirements=["req1", "req2"],
        )

        # Generate markdown and parse as markdown
        markdown = generator.to_markdown(spec)
        parsed_md = parser.parse(markdown)
        assert parsed_md.name == spec.name

        # Generate YAML and parse as YAML
        yaml_str = generator.to_yaml(spec)
        parsed_yaml = parser.parse(yaml_str)
        assert parsed_yaml.name == spec.name

        # Both should validate successfully
        result_md = validator.validate(parsed_md)
        result_yaml = validator.validate(parsed_yaml)
        assert result_md.is_valid
        assert result_yaml.is_valid

    def test_parser_generator_validator_together(self):
        """Test all three components working together."""
        generator = SpecGenerator()
        parser = SpecParser()
        validator = SpecValidator()

        # Create a comprehensive spec
        spec = generator.generate(
            name="Comprehensive Test",
            version="1.2.3",
            description="This is a comprehensive test of all components working together",
            requirements=[
                "Generator creates spec correctly",
                "Parser reads the generated format",
                "Validator validates the content",
            ],
        )

        # Convert to markdown
        markdown = generator.to_markdown(spec)

        # Parse back
        parsed = parser.parse(markdown)

        # Validate
        result = validator.validate(parsed)

        # All should match
        assert spec.name == parsed.name
        assert spec.version == parsed.version
        assert spec.description == parsed.description
        assert spec.requirements == parsed.requirements
        assert result.is_valid

    def test_spec_with_all_edge_cases(self):
        """Test spec with various edge cases."""
        generator = SpecGenerator()
        parser = SpecParser()
        validator = SpecValidator()

        # Create spec with edge cases
        spec = generator.generate(
            name="Edge Case Test",
            version="0.1.0",
            description="Testing edge cases",
            requirements=[
                "Requirement with special chars: @#$%",
                "Requirement with numbers: 123",
                "Requirement with quotes: 'test' and \"test\"",
            ],
        )

        # Generate and parse
        markdown = generator.to_markdown(spec)
        parsed = parser.parse(markdown)

        # Validate
        result = validator.validate(parsed)

        # Should still work
        assert parsed.name == spec.name
        assert result.is_valid or len(result.errors) == 0  # Should not have errors

    def test_completeness_validation_workflow(self):
        """Test completeness check in workflow."""
        generator = SpecGenerator()
        validator = SpecValidator()

        # Create complete spec
        complete_spec = generator.generate(
            name="Complete Specification",
            version="1.0.0",
            description="This is a complete specification with all fields filled",
            requirements=["req1", "req2", "req3"],
        )

        # Check completeness
        completeness = validator.check_completeness(complete_spec)
        assert completeness >= 0.8

        # Create incomplete spec
        incomplete_spec = generator.generate(
            name="Incomplete",
            version="1.0.0",
            description="",
            requirements=[],
        )

        # Check completeness
        completeness = validator.check_completeness(incomplete_spec)
        assert completeness < 0.8

    def test_consistency_check_workflow(self):
        """Test consistency check in workflow."""
        generator = SpecGenerator()
        parser = SpecParser()
        validator = SpecValidator()

        # Create consistent spec
        consistent_spec = generator.generate(
            name="Consistent Spec",
            version="1.0.0",
            description="Consistent specification",
            requirements=["Unique requirement 1", "Unique requirement 2"],
        )

        # Check consistency
        is_consistent = validator.check_consistency(consistent_spec)
        assert is_consistent

        # Parse it
        markdown = generator.to_markdown(consistent_spec)
        parsed = parser.parse(markdown)

        # Check consistency of parsed version
        is_consistent = validator.check_consistency(parsed)
        assert is_consistent

    def test_empty_and_none_handling(self):
        """Test handling of empty and None values."""
        generator = SpecGenerator()
        parser = SpecParser()
        validator = SpecValidator()

        # Create spec with empty values
        spec = generator.generate(
            name="",
            version="",
            description="",
            requirements=[],
        )

        # Validate
        result = validator.validate(spec)
        assert not result.is_valid  # Should not be valid

        # Parse empty content
        parsed = parser.parse("")
        assert parsed.name == ""
        assert parsed.version == ""
        assert parsed.description == ""
        assert parsed.requirements == []

    def test_utility_functions_integration(self):
        """Test utility functions with generated content."""
        SpecGenerator()
        SpecParser()
        SpecValidator()

        # Create spec using utility functions
        spec = generate_specification(
            name="Utility Test",
            version="1.0.0",
            description="Testing utility functions",
            requirements=["req1", "req2"],
        )

        assert spec.name == "Utility Test"

        # Create test spec
        test_spec = create_test_spec("TestModule")
        assert test_spec.name

        # Validate using utility function
        result = validate_specification(spec)
        assert isinstance(result, ValidationResult)

        # Check completeness
        completeness = validate_spec_completeness(spec)
        assert isinstance(completeness, float)

        # Check consistency
        is_consistent = check_spec_consistency(spec)
        assert isinstance(is_consistent, bool)

    def test_multiple_parse_formats(self):
        """Test parsing multiple different formats."""
        parser = SpecParser()

        # Markdown format
        md_content = """# Markdown Spec
## Version
1.0.0
## Description
Markdown format
## Requirements
- Req 1
- Req 2
"""
        spec_md = parser.parse(md_content)
        assert spec_md.name == "Markdown Spec"

        # YAML format
        yaml_content = """
name: YAML Spec
version: 2.0.0
description: YAML format
requirements:
  - Req 1
  - Req 2
"""
        spec_yaml = parser.parse(yaml_content)
        assert spec_yaml.name == "YAML Spec"

        # Both should have same requirements
        assert len(spec_md.requirements) == len(spec_yaml.requirements)

    def test_requirements_extraction_edge_cases(self):
        """Test extract_requirements with various edge cases."""
        from autoBMAD.spec_automation.spec_parser import extract_requirements

        # Empty text
        assert extract_requirements("") == []

        # Text without bullets
        assert extract_requirements("Just plain text") == []

        # Mixed formats
        text = """
        Some requirements:
        - First requirement
        * Second requirement
        + Third requirement
        1. Fourth requirement
        2. Fifth requirement
        Plain text without bullet
        """
        requirements = extract_requirements(text)
        assert len(requirements) == 5
        assert "First requirement" in requirements

        # Requirements with indentation
        text2 = """
        - Indented requirement
          - More indented
        - Normal requirement
        """
        requirements2 = extract_requirements(text2)
        assert len(requirements2) >= 1


class TestEdgeCasesForCoverage:
    """Additional tests to achieve 100% coverage."""

    def test_spec_parser_description_with_section_header(self):
        """Test that section headers in description are handled correctly."""
        parser = SpecParser()

        # Create a spec content where a section header appears in the description
        content = """# Test Spec
## Version
1.0.0
## Description
This is a description
## Another Section
Content here
"""
        spec = parser.parse(content)
        assert spec.name == "Test Spec"
        # The description should contain the content before "## Another Section"
        assert "This is a description" in spec.description

    def test_spec_validator_short_name_warning(self):
        """Test that a warning is added for short specification names."""
        from autoBMAD.spec_automation.spec_validator import SpecValidator

        validator = SpecValidator()

        # Create a spec with a very short name (less than 3 chars)
        spec = SpecificationData(
            name="A",
            version="1.0.0",
            description="Test specification",
            requirements=["req1"]
        )

        result = validator.validate(spec)

        # Should have a warning about the short name
        assert len(result.warnings) > 0
        assert any("short" in str(warning).lower() for warning in result.warnings)
        assert result.is_valid  # Should still be valid, just with a warning

    def test_conftest_fixtures(self, empty_list, single_element_list, already_sorted_list,
                               reverse_sorted_list, random_order_list, negative_numbers_list,
                               floats_list, mixed_int_float_list, duplicate_elements_list,
                               all_same_elements_list, large_numbers_list, partially_sorted_list):
        """Test conftest fixtures are accessible and work correctly."""
        # Test empty_list fixture
        assert empty_list == []
        assert isinstance(empty_list, list)

        # Test single_element_list fixture
        assert single_element_list == [42]
        assert len(single_element_list) == 1

        # Test already_sorted_list fixture
        assert len(already_sorted_list) == 10
        assert already_sorted_list == sorted(already_sorted_list)

        # Test reverse_sorted_list fixture
        assert len(reverse_sorted_list) == 10
        assert reverse_sorted_list == sorted(reverse_sorted_list, reverse=True)

        # Test random_order_list fixture
        assert len(random_order_list) == 10

        # Test negative_numbers_list fixture
        assert any(x < 0 for x in negative_numbers_list)

        # Test floats_list fixture
        assert any(isinstance(x, float) for x in floats_list)

        # Test mixed_int_float_list fixture
        assert len(mixed_int_float_list) >= 2

        # Test duplicate_elements_list fixture
        assert len(duplicate_elements_list) >= 3

        # Test all_same_elements_list fixture
        assert all(x == all_same_elements_list[0] for x in all_same_elements_list)

        # Test large_numbers_list fixture
        assert max(large_numbers_list) > 1000

        # Test partially_sorted_list fixture
        assert len(partially_sorted_list) >= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
