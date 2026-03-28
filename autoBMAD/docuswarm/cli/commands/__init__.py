"""CLI commands for DocuSwarm.

This module contains Click command definitions.
Commands should delegate business logic to services.
"""

from autoBMAD.docuswarm.cli.commands.start import start
from autoBMAD.docuswarm.cli.commands.status import status
from autoBMAD.docuswarm.cli.commands.resume import resume
from autoBMAD.docuswarm.cli.commands.cancel import cancel
from autoBMAD.docuswarm.cli.commands.clean import clean
from autoBMAD.docuswarm.cli.commands.list import list_pipelines
from autoBMAD.docuswarm.cli.commands.export import export
from autoBMAD.docuswarm.cli.commands.questions import questions
from autoBMAD.docuswarm.cli.commands.answer import answer

__all__ = [
    "start",
    "status",
    "resume",
    "cancel",
    "clean",
    "list_pipelines",
    "export",
    "questions",
    "answer",
]
