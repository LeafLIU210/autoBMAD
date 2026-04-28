"""Context chaining module for node execution.

This module provides the ContextChainer class for automatically injecting
predecessor node deliverables into the current node's execution context.
"""

import logging
from typing import Any

# Node execution sequence - order matters for chaining
SEQUENCE = ["analyst", "pm", "ux", "architect", "po"]

logger = logging.getLogger(__name__)


class ContextChainer:
    """Handles automatic injection of predecessor deliverables into node context.

    This class queries previous successful node runs with the same context_hash
    and injects their deliverables into the current node's execution context.

    The chaining follows the SEQUENCE order: analyst -> pm -> ux -> architect -> po

    Each predecessor's deliverable is injected with a key format of:
    {node_id}_deliverable (e.g., "analyst_deliverable", "pm_deliverable")

    Args:
        state_manager: The state manager instance for querying previous runs.

    Example:
        >>> chainer = ContextChainer(state_manager)
        >>> context = await chainer.get_chained_deliverables(
        ...     node_id="pm",
        ...     context_hash="abc123",
        ...     no_chain=False
        ... )
        >>> # Returns {"analyst_deliverable": {...}} if analyst ran successfully
    """

    def __init__(self, state_manager: Any) -> None:
        """Initialize the ContextChainer.

        Args:
            state_manager: The state manager for querying previous runs.
        """
        self._state_manager = state_manager

    def get_chained_deliverables(
        self,
        node_id: str,
        context_hash: str,
        no_chain: bool = False,
    ) -> dict[str, Any]:
        """Get deliverables from predecessor nodes for context chaining.

        Queries all predecessor nodes in the SEQUENCE that have completed
        successfully with the same context_hash and returns their deliverables
        keyed by {node_id}_deliverable format.

        Args:
            node_id: The current node ID being executed.
            context_hash: The context hash to match against previous runs.
            no_chain: If True, skip chaining and return empty dict.

        Returns:
            Dictionary containing predecessor deliverables with keys like
            "analyst_deliverable", "pm_deliverable", etc. Empty dict if
            no_chain=True or no predecessors found.
        """
        # Return empty dict if chaining is disabled
        if no_chain:
            return {}

        # Find predecessors in the sequence
        try:
            node_index = SEQUENCE.index(node_id)
        except ValueError:
            # Node not in sequence, no predecessors to chain
            return {}

        # Get all predecessor node IDs
        predecessor_ids = SEQUENCE[:node_index]

        if not predecessor_ids:
            return {}

        # Query each predecessor and collect their deliverables
        chained_context: dict[str, Any] = {}

        for pred_id in predecessor_ids:
            try:
                # Query the state manager for the latest successful run
                run_result = self._state_manager.get_latest_successful_run(pred_id, context_hash)

                if run_result is not None and run_result.get("deliverable") is not None:
                    # Inject deliverable with proper key naming
                    deliverable_key = f"{pred_id}_deliverable"
                    chained_context[deliverable_key] = run_result["deliverable"]
                    logger.debug(
                        "Chained deliverable from "
                        + pred_id
                        + " to "
                        + node_id
                        + ": "
                        + deliverable_key
                    )
                else:
                    # No successful run found for this predecessor
                    msg = (
                        "No successful run found for predecessor "
                        + pred_id
                        + " with context_hash "
                        + context_hash
                        + ". Continuing without its deliverable."
                    )
                    logger.warning(msg)

            except AttributeError:
                # State manager doesn't have the method yet - log warning and continue
                msg = (
                    "State manager does not support get_latest_successful_run method. "
                    + "Cannot chain from "
                    + pred_id
                    + ". Continuing without chaining."
                )
                logger.warning(msg)
                break
            except Exception as e:
                # Handle any other errors gracefully - warn but don't block
                msg = (
                    "Error chaining from "
                    + pred_id
                    + ": "
                    + str(e)
                    + ". Continuing without its deliverable."
                )
                logger.warning(msg)
                continue

        return chained_context


def get_sequence() -> list[str]:
    """Get the node execution sequence.

    Returns:
        List of node IDs in execution order.
    """
    return SEQUENCE.copy()


def get_predecessors(node_id: str) -> list[str]:
    """Get predecessor node IDs for a given node.

    Args:
        node_id: The node ID to get predecessors for.

    Returns:
        List of predecessor node IDs in order.
    """
    try:
        node_index = SEQUENCE.index(node_id)
        return SEQUENCE[:node_index]
    except ValueError:
        return []
