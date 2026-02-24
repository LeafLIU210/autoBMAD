"""Independent Agent prompt template - Story 4.5.

This module exports the Independent Agent prompt template as a constant.
"""

from pathlib import Path

# Load template from markdown file
_TEMPLATE_PATH = Path(__file__).parent / "independent_agent.md"

with open(_TEMPLATE_PATH, encoding="utf-8") as f:
    TEMPLATE: str = f.read()
