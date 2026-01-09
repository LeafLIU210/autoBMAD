"""Specification generation functionality."""

from autoBMAD.spec_automation.spec_parser import SpecificationData


class SpecGenerator:
    """Generator for specification documents."""

    def __init__(self) -> None:
        """Initialize the generator."""
        pass

    def generate(
        self,
        name: str,
        version: str,
        description: str,
        requirements: list[str] | None = None,
    ) -> SpecificationData:
        """Generate a specification.

        Args:
            name: The name of the specification
            version: The version of the specification
            description: The description of the specification
            requirements: Optional list of requirements

        Returns:
            SpecificationData object
        """
        if requirements is None:
            requirements = []

        return SpecificationData(
            name=name,
            version=version,
            description=description,
            requirements=requirements,
        )

    def create_test_spec(self, module_name: str) -> SpecificationData:
        """Create a test specification for a module.

        Args:
            module_name: The name of the module to create test spec for

        Returns:
            SpecificationData object
        """
        # Clean module name for display
        display_name = module_name.replace("_", " ").title()

        requirements = [
            f"Implement {module_name} module",
            f"Provide basic functionality for {display_name}",
            "Include error handling",
            "Follow coding standards",
            "Include documentation",
        ]

        return self.generate(
            name=f"{display_name} Specification",
            version="1.0.0",
            description=f"Specification for the {display_name} module",
            requirements=requirements,
        )

    def to_markdown(self, spec: SpecificationData) -> str:
        """Convert specification to markdown format.

        Args:
            spec: The specification to convert

        Returns:
            Markdown string
        """
        markdown = f"# {spec.name}\n\n"
        markdown += f"## Version\n\n{spec.version}\n\n"
        markdown += f"## Description\n\n{spec.description}\n\n"

        if spec.requirements:
            markdown += "## Requirements\n\n"
            for i, req in enumerate(spec.requirements, 1):
                markdown += f"{i}. {req}\n"
            markdown += "\n"

        return markdown

    def to_yaml(self, spec: SpecificationData) -> str:
        """Convert specification to YAML format.

        Args:
            spec: The specification to convert

        Returns:
            YAML string
        """
        import yaml

        spec_dict = spec.to_dict()
        return yaml.dump(spec_dict, default_flow_style=False, sort_keys=False)


def generate_specification(
    name: str,
    version: str,
    description: str,
    requirements: list[str] | None = None,
) -> SpecificationData:
    """Generate a specification.

    Args:
        name: The name of the specification
        version: The version of the specification
        description: The description of the specification
        requirements: Optional list of requirements

    Returns:
        SpecificationData object
    """
    generator = SpecGenerator()
    return generator.generate(name, version, description, requirements)


def create_test_spec(module_name: str) -> SpecificationData:
    """Create a test specification for a module.

    Args:
        module_name: The name of the module to create test spec for

    Returns:
        SpecificationData object
    """
    generator = SpecGenerator()
    return generator.create_test_spec(module_name)
