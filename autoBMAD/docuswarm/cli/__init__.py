"""CLI module for DocuSwarm.

This module provides the command-line interface for the DocuSwarm system.
It follows a layered architecture:
- commands/: CLI command definitions (Click decorators)
- services/: Business logic layer
"""

from autoBMAD.docuswarm.cli.main import cli

__all__ = ["cli"]
