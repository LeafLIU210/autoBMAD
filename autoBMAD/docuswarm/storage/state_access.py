"""State access utilities for unified state management - Phase 2 P1."""

from typing import Any


class PipelineStateView:
    """Pipeline 状态视图 - 提供统一的状态访问接口。

    此类封装了从 state_json 读取状态的逻辑，确保所有状态访问
    都使用单一来源（state_json），消除双重来源风险。

    Example:
        >>> pipeline = state_manager.get_pipeline(pipeline_id)
        >>> view = PipelineStateView(pipeline)
        >>> print(view.current_node)  # 从 state_json 读取
        >>> print(view.status)        # 从 state_json 读取
    """

    def __init__(self, pipeline_data: dict[str, Any]) -> None:
        """初始化状态视图。

        Args:
            pipeline_data: pipeline 数据字典，包含 state 字段
        """
        self._data = pipeline_data
        state = pipeline_data.get("state")
        self._state = state if isinstance(state, dict) else {}

    @property
    def pipeline_id(self) -> str:
        """Pipeline ID"""
        return self._data.get("pipeline_id", "")

    @property
    def subject(self) -> str:
        """主题"""
        return self._data.get("subject", "")

    @property
    def status(self) -> str:
        """Pipeline 状态（从 state_json 读取）"""
        return self._state.get("status", "unknown")

    @property
    def current_node(self) -> str | None:
        """当前节点（从 state_json 读取）"""
        return self._state.get("current_node")

    @property
    def completed_nodes(self) -> list[str]:
        """已完成节点列表"""
        return self._state.get("completed_nodes", [])

    @property
    def is_running(self) -> bool:
        """是否运行中"""
        return self.status == "running"

    @property
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status == "completed"

    def is_node_completed(self, node_id: str) -> bool:
        """检查节点是否已完成。

        Args:
            node_id: 节点 ID

        Returns:
            True if 节点在 completed_nodes 中
        """
        return node_id in self.completed_nodes

    def get_node_deliverable(self, node_id: str) -> dict[str, Any] | None:
        """获取节点的交付物。

        Args:
            node_id: 节点 ID

        Returns:
            交付物字典，或 None
        """
        deliverables = self._state.get("deliverables", {})
        return deliverables.get(node_id)

    def get_node_iterations(self, node_id: str) -> int:
        """获取节点迭代次数。

        Args:
            node_id: 节点 ID

        Returns:
            迭代次数，默认为 0
        """
        iterations = self._state.get("node_iterations", {})
        return iterations.get(node_id, 0)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典（用于序列化）。

        Returns:
            包含所有字段的字典
        """
        return {
            "pipeline_id": self.pipeline_id,
            "subject": self.subject,
            "status": self.status,
            "current_node": self.current_node,
            "completed_nodes": self.completed_nodes,
            "is_running": self.is_running,
            "is_completed": self.is_completed,
        }


class PipelineStateAccess:
    """静态状态访问工具类。

    提供便捷的状态字段访问，无需创建 PipelineStateView 实例。
    """

    @staticmethod
    def get_current_node(pipeline: dict[str, Any]) -> str | None:
        """统一从 state_json 获取 current_node。"""
        state = pipeline.get("state", {}) if isinstance(pipeline.get("state"), dict) else {}
        return state.get("current_node")

    @staticmethod
    def get_status(pipeline: dict[str, Any]) -> str:
        """统一从 state_json 获取 status。"""
        state = pipeline.get("state", {}) if isinstance(pipeline.get("state"), dict) else {}
        return state.get("status", "unknown")

    @staticmethod
    def get_completed_nodes(pipeline: dict[str, Any]) -> list[str]:
        """统一从 state_json 获取 completed_nodes。"""
        state = pipeline.get("state", {}) if isinstance(pipeline.get("state"), dict) else {}
        return state.get("completed_nodes", [])
