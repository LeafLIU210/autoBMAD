"""
Spec Automation Module

Independent workflow module for handling non-BMAD format planning documents.
Provides document-centric development and QA automation.
"""

__version__ = "1.0.0"
__author__ = "BMAD Automation System"

# Import main components
from .doc_parser import DocParser
from .spec_state_manager import SpecStateManager
from .spec_dev_agent import SpecDevAgent
from .spec_qa_agent import SpecQAAgent
from .spec_driver import SpecDriver

__all__ = [
    "DocParser",
    "SpecStateManager",
    "SpecDevAgent",
    "SpecQAAgent",
    "SpecDriver",
]
