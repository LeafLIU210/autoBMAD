"""Configuration module for DocuSwarm.

Provides configuration management for DocuSwarm agents and services.
"""

# Import SummaryAgent configuration classes (must be at top to avoid E402)
# Re-export the main Config class from the sibling config.py module
# Note: config.py is a module at the parent level, we import it via sys.modules
import sys
from pathlib import Path

from autoBMAD.docuswarm.config.summary_agent_config import (
    CachingConfig,
    FileDiscoveryConfig,
    LLMConfig,
    OutputSchemaConfig,
    PerformanceConfig,
    SummaryAgentConfig,
    SummaryAgentConfigError,
    SummaryAgentConfigLoader,
)

# Add the parent directory to sys.path temporarily to import the config module
_parent_dir = str(Path(__file__).parent.parent)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)


# Import the main Config class from the sibling config.py
# We need to use importlib to avoid import conflicts with this package
def _import_config():
    import importlib.util

    config_path = Path(__file__).parent.parent / "config.py"
    spec = importlib.util.spec_from_file_location("_config_module", config_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load config module from {config_path}")
    config_module = importlib.util.module_from_spec(spec)
    sys.modules["_config_module"] = config_module
    spec.loader.exec_module(config_module)
    return config_module.Config


# Import Config lazily to avoid circular imports
try:
    Config = _import_config()
except Exception as _e:
    # Fallback: Config will be None if import fails
    Config = None  # type: ignore

# Import load_config from the sibling config.py module
def _import_load_config():
    import importlib.util

    config_path = Path(__file__).parent.parent / "config.py"
    spec = importlib.util.spec_from_file_location("_config_module_load", config_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load config module from {config_path}")
    config_module = importlib.util.module_from_spec(spec)
    sys.modules["_config_module_load"] = config_module
    spec.loader.exec_module(config_module)
    return config_module.load_config


try:
    load_config = _import_load_config()
except Exception as _e:
    load_config = None  # type: ignore

__all__ = [
    "CachingConfig",
    "Config",
    "FileDiscoveryConfig",
    "LLMConfig",
    "load_config",
    "OutputSchemaConfig",
    "PerformanceConfig",
    "SummaryAgentConfig",
    "SummaryAgentConfigError",
    "SummaryAgentConfigLoader",
]
