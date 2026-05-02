"""CLI commands for DocuSwarm.

This module contains Click command definitions.
Commands should delegate business logic to services.
"""

from autoBMAD.docuswarm.cli.commands.cancel import cancel
from autoBMAD.docuswarm.cli.commands.cancel_all import cancel_all
from autoBMAD.docuswarm.cli.commands.clean import clean
from autoBMAD.docuswarm.cli.commands.diagnostics import diagnostics
from autoBMAD.docuswarm.cli.commands.export import export
from autoBMAD.docuswarm.cli.commands.list import list_pipelines
from autoBMAD.docuswarm.cli.commands.resume import resume
from autoBMAD.docuswarm.cli.commands.start import start
from autoBMAD.docuswarm.cli.commands.status import status

__all__ = [
    "start",
    "status",
    "resume",
    "cancel",
    "cancel_all",
    "clean",
    "list_pipelines",
    "export",
    "diagnostics",
]
