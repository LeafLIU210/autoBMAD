# DocuSwarm F1-F5 快速实施指南

**目标**: 快速修复 F1-F5 所有问题  
**预计时间**: 3-5 天  
**前提**: 熟悉 `autoBMAD/docuswarm` 代码结构

---

## 快速导航

| 问题 | 文件数 | 难度 | 预计时间 |
|------|--------|------|----------|
| F1 - 多文档验证 | 2 | ⭐⭐⭐ | 4h |
| F2 - update_context | 3 | ⭐⭐ | 3h |
| F3 - SDK Skills | 3 | ⭐⭐ | 2h |
| F4 - 模板映射 | 3+ | ⭐⭐⭐ | 6h |
| F5 - allowed_keys | 2 | ⭐ | 2h |

---

## 实施前准备

### 1. 创建分支

```bash
git checkout -b fix/f1-f5-deep-reform-implementation
git push -u origin fix/f1-f5-deep-reform-implementation
```

### 2. 备份关键文件

```bash
# 创建备份目录
mkdir -p .backup/$(date +%Y%m%d)

# 备份关键文件
cp autoBMAD/docuswarm/context/validator.py .backup/$(date +%Y%m%d)/
cp autoBMAD/docuswarm/llm/session_manager.py .backup/$(date +%Y%m%d)/
cp autoBMAD/docuswarm/llm/tool_filter.py .backup/$(date +%Y%m%d)/
cp autoBMAD/docuswarm/agents/independent.py .backup/$(date +%Y%m%d)/
cp autoBMAD/docuswarm/pipeline/orchestrator.py .backup/$(date +%Y%m%d)/
cp autoBMAD/docuswarm/prompts/contract_builder.py .backup/$(date +%Y%m%d)/
cp autoBMAD/docuswarm/tools/update_context_sdk.py .backup/$(date +%Y%m%d)/
```

### 3. 创建测试文件框架

```bash
# 创建测试目录
mkdir -p tests/docuswarm/{context,llm,prompts,tools,integration}

# 创建空测试文件
touch tests/docuswarm/context/test_multi_document_validation.py
touch tests/docuswarm/llm/test_update_context_server_creation.py
touch tests/docuswarm/llm/test_sdk_skills_discovery.py
touch tests/docuswarm/prompts/test_template_mapping.py
touch tests/docuswarm/tools/test_update_context_allowed_keys.py
touch tests/docuswarm/integration/test_f1_f5_fixes.py
```

---

## Day 1: F1 - 多文档验证 (4小时)

### 上午: 编写失败测试 (2h)

**步骤 1**: 将测试代码复制到测试文件

```bash
cat > tests/docuswarm/context/test_multi_document_validation.py << 'EOF'
"""F1: 多文档验证测试"""
import pytest
from autoBMAD.docuswarm.context.validator import (
    ContextValidator,
    MaxDeliverablesValidationStrategy,
)


class TestMultiDocumentValidation:
    """测试多文档格式验证"""
    
    @pytest.fixture
    def multi_doc_output(self):
        return {
            "deliverable": {
                "title": "PO Deliverables Set",
                "type": "multi-document",
                "documents": [
                    {
                        "title": "Product Vision",
                        "file_path": "output/pipe-123/po/product-vision.md",
                        "sha256": "abc123...",
                        "content_summary": "Summary...",
                        "word_count": 500,
                        "document_type": "product-vision",
                        "document_index": 1,
                        "document_total": 4,
                    },
                    {
                        "title": "Roadmap",
                        "file_path": "output/pipe-123/po/roadmap.md",
                        "sha256": "def456...",
                        "content_summary": "Summary...",
                        "word_count": 800,
                        "document_type": "roadmap",
                        "document_index": 2,
                        "document_total": 4,
                    },
                ],
                "total_word_count": 1300,
            },
            "questions": [],
            "action": "create_deliverable",
        }
    
    def test_multi_document_should_pass_validation(self, multi_doc_output):
        validator = ContextValidator()
        result = validator.validate_independent_output(multi_doc_output, node_id="po")
        assert result.valid, f"多文档验证失败: {result.issues}"
    
    def test_multi_document_should_detect_correct_count(self, multi_doc_output):
        strategy = MaxDeliverablesValidationStrategy()
        document_count = strategy._detect_document_count(multi_doc_output["deliverable"])
        assert document_count == 2, f"应检测到 2 个文档，实际检测到 {document_count}"
EOF
```

**步骤 2**: 运行测试确认失败

```bash
pytest tests/docuswarm/context/test_multi_document_validation.py -v
# 预期: 2 failed
```

### 下午: 实现修复 (2h)

**步骤 3**: 修改 validator.py

```bash
# 在 autoBMAD/docuswarm/context/validator.py 中添加以下方法

# 1. 找到 IndependentOutputValidationStrategy._validate_deliverable 方法
# 2. 在方法开头添加多文档检测
```

**具体修改**:

```python
# 在 line 678 附近，替换现有 _validate_deliverable 方法

def _validate_deliverable(self, data, result, _is_submit_report_format=False):
    """Validate deliverable field structure."""
    if "deliverable" not in data:
        result.add_error(field="deliverable", message="required", code="MISSING")
        return
    
    deliverable = data["deliverable"]
    
    if not isinstance(deliverable, dict):
        result.add_error(field="deliverable", message="must be dict", code="TYPE_ERROR")
        return
    
    # F1 FIX: 检测多文档格式
    if deliverable.get("type") == "multi-document":
        self._validate_multi_document_deliverable(deliverable, result)
    else:
        self._validate_single_document_deliverable(deliverable, result)

# 在 line 789 后添加新方法

def _validate_multi_document_deliverable(self, deliverable, result):
    """验证多文档格式."""
    # 验证必需字段
    if "title" not in deliverable:
        result.add_error(field="deliverable.title", message="required", code="MISSING")
    
    if "documents" not in deliverable or not isinstance(deliverable["documents"], list):
        result.add_error(field="deliverable.documents", message="required array", code="MISSING")
        return
    
    # 验证每个子文档
    for idx, doc in enumerate(deliverable["documents"]):
        prefix = f"deliverable.documents[{idx}]"
        if not isinstance(doc, dict):
            result.add_error(field=prefix, message="must be dict", code="TYPE_ERROR")
            continue
            
        if "file_path" not in doc:
            result.add_error(field=f"{prefix}.file_path", message="required", code="MISSING")
        if "sha256" not in doc:
            result.add_error(field=f"{prefix}.sha256", message="required", code="MISSING")

def _validate_single_document_deliverable(self, deliverable, result):
    """原有的单文档验证逻辑 - 保持不变."""
    # ... 复制现有验证代码 ...
```

**步骤 4**: 修改 MaxDeliverablesValidationStrategy

```python
# 在 line 1288 附近，替换 _detect_document_count 方法

def _detect_document_count(self, deliverable: dict) -> int:
    """检测文档数量."""
    # F1 FIX: 多文档格式
    if deliverable.get("type") == "multi-document":
        documents = deliverable.get("documents", [])
        return len(documents)
    
    document_total = deliverable.get("document_total")
    if document_total is not None and isinstance(document_total, int):
        return document_total
    
    return 1
```

**步骤 5**: 运行测试确认通过

```bash
pytest tests/docuswarm/context/test_multi_document_validation.py -v
# 预期: 2 passed
```

---

## Day 2: F2 - update_context 链路 (3小时)

### 上午: 编写测试 + 修改 SessionManager (1.5h)

**步骤 1**: 创建测试

```bash
cat > tests/docuswarm/llm/test_update_context_server_creation.py << 'EOF'
"""F2: update_context MCP Server 测试"""
import pytest
from unittest.mock import Mock, patch
from autoBMAD.docuswarm.llm.session_manager import SessionManager
from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter
from autoBMAD.nodes.loader import NodeSharedContextConfig, NodeToolPermissions


class TestUpdateContextServerCreation:
    def test_session_manager_should_pass_pipeline_id(self):
        with patch.object(NodeToolFilter, 'create_mcp_servers') as mock_create:
            mock_create.return_value = {}
            
            # F2 FIX: SessionManager 应支持 pipeline_id 参数
            sm = SessionManager(
                cwd="/tmp",
                output_dir="/tmp/output",
                node_id="analyst",
                tool_permissions=NodeToolPermissions(
                    shared_context=NodeSharedContextConfig(enabled=True),
                ),
                pipeline_id="pipe-123",
            )
            
            try:
                options = sm._create_options()
            except TypeError:
                pytest.fail("SessionManager 不支持 pipeline_id 参数")
            
            mock_create.assert_called_once()
            # 验证传递了 pipeline_id
EOF
```

**步骤 2**: 修改 SessionManager

```python
# autoBMAD/docuswarm/llm/session_manager.py

# 1. __init__ 添加 pipeline_id 参数

def __init__(
    self,
    work_dir=None,
    agent_file=None,
    config=None,
    node_id=None,
    file_dirs=None,
    search_dirs=None,
    tool_permissions=None,
    cwd=None,
    output_dir=None,
    pipeline_id=None,  # F2 FIX
):
    # ... 现有代码 ...
    self._pipeline_id = pipeline_id  # F2 FIX

# 2. _create_options 传递 pipeline_id

def _create_options(self, ...):
    # ... 现有代码 ...
    
    # F2 FIX: 传递 pipeline_id
    mcp_servers = node_filter.create_mcp_servers(pipeline_id=self._pipeline_id)
```

### 下午: 修改 IndependentAgent (1.5h)

**步骤 3**: 修改 IndependentAgent

```python
# autoBMAD/docuswarm/agents/independent.py

# 1. _create_pipeline_session_manager 添加 pipeline_id

def _create_pipeline_session_manager(
    self,
    work_dir,
    node_id,
    file_dirs,
    search_dirs,
    tool_permissions=None,
    pipeline_id=None,  # F2 FIX
):
    return SessionManager(
        work_dir=work_dir,
        cwd=work_dir,  # 或其他 cwd
        output_dir=work_dir,
        agent_file=self._agent_file,
        config=...,
        node_id=node_id,
        file_dirs=file_dirs,
        search_dirs=search_dirs,
        tool_permissions=tool_permissions,
        pipeline_id=pipeline_id,  # F2 FIX
    )

# 2. execute 方法传递 pipeline_id

async def execute(self, input_data):
    # ... 现有代码 ...
    
    pipeline_id = getattr(input_data, 'pipeline_id', None)  # F2 FIX
    
    session_manager = self._create_pipeline_session_manager(
        work_dir=node_output_dir,
        node_id=self.node_id,
        file_dirs=file_dirs,
        search_dirs=search_dirs,
        tool_permissions=tool_permissions,
        pipeline_id=pipeline_id,  # F2 FIX
    )
```

**步骤 4**: 运行测试

```bash
pytest tests/docuswarm/llm/test_update_context_server_creation.py -v
```

---

## Day 3: F3 - SDK Skills (2小时)

### 上午: 修改 Orchestrator 和 IndependentAgent

**步骤 1**: 修改 Orchestrator

```python
# autoBMAD/docuswarm/pipeline/orchestrator.py

# 1. _create_session_manager 添加 project_root 检测

def _create_session_manager(self, pipeline_id=None):
    # F3 FIX: 检测项目根目录
    project_root = self._detect_project_root()
    
    work_dir = KaosPath(str(Path(self._work_dir) / pipeline_id)) if pipeline_id else KaosPath(self._work_dir)
    
    session_manager = SessionManager(
        work_dir=work_dir,
        cwd=project_root,  # F3 FIX: 使用项目根目录
        output_dir=work_dir,
        config=None,
    )
    return session_manager

# 2. 添加 _detect_project_root 方法

def _detect_project_root(self) -> Path:
    """检测项目根目录."""
    current = Path(self._work_dir).resolve()
    
    while current != current.parent:
        if (current / ".claude" / "skills").exists():
            return current
        if (current / "pyproject.toml").exists():
            return current
        if (current / ".git").exists():
            return current
        current = current.parent
    
    return Path(self._work_dir)
```

**步骤 2**: 修改 IndependentAgent (同上 F2，添加 project_root)

```python
def _create_pipeline_session_manager(
    self,
    work_dir,
    node_id,
    file_dirs,
    search_dirs,
    tool_permissions=None,
    pipeline_id=None,
    project_root=None,  # F3 FIX
):
    return SessionManager(
        work_dir=work_dir,
        cwd=project_root or work_dir,  # F3 FIX
        output_dir=work_dir,
        # ... 其他参数 ...
        pipeline_id=pipeline_id,
    )
```

**步骤 3**: 运行测试

```bash
pytest tests/docuswarm/llm/test_sdk_skills_discovery.py -v
```

---

## Day 4-5: F4 - 模板映射 (6小时)

### Day 4 上午: 创建模板映射配置 (2h)

**步骤 1**: 创建 template_mapping.yaml

```bash
cat > autoBMAD/docuswarm/templates/template_mapping.yaml << 'EOF'
# 模板 ID 映射配置
mappings:
  analyst:
    product-brief: market_research
  
  architect:
    architecture: system_architecture
  
  pm:
    prd: prd
  
  po:
    epics-stories: null
    document_types:
      product-vision: product_vision
      roadmap: roadmap
      epic-list: epic_list
      story-list: story_list
  
  ux:
    ux-design: user_personas
EOF
```

**步骤 2**: 创建测试

```bash
cat > tests/docuswarm/prompts/test_template_mapping.py << 'EOF'
"""F4: 模板运行时映射测试"""
import pytest
from autoBMAD.docuswarm.prompts.contract_builder import NodePromptContractBuilder


class TestTemplateMapping:
    @pytest.mark.parametrize("node_id,deliverable_type", [
        ("analyst", "product-brief"),
        ("architect", "architecture"),
        ("pm", "prd"),
        ("po", "epics-stories"),
        ("ux", "ux-design"),
    ])
    def test_should_find_template(self, node_id, deliverable_type):
        builder = NodePromptContractBuilder()
        template = builder._load_node_template(node_id, deliverable_type)
        assert template is not None, f"{node_id}: 应找到模板"
EOF
```

### Day 4 下午 - Day 5: 修改 ContractBuilder

**步骤 3**: 修改 contract_builder.py

```python
# autoBMAD/docuswarm/prompts/contract_builder.py

# 1. _load_node_template 添加映射支持

def _load_node_template(self, node_id, template_id):
    """加载模板."""
    # F4 FIX: 应用映射
    mapped_id = self._apply_template_mapping(node_id, template_id)
    if mapped_id:
        template_id = mapped_id
    
    # ... 现有加载逻辑 ...
    
    # F4 FIX: 增强匹配
    if template_id:
        for template in templates:
            if template.get("template_id") == template_id:
                return template
            # 模糊匹配
            if self._template_id_matches(template_id, template):
                return template

def _apply_template_mapping(self, node_id, template_id):
    """应用模板映射."""
    import yaml
    from pathlib import Path
    
    mapping_file = Path(__file__).parent.parent / "templates" / "template_mapping.yaml"
    if not mapping_file.exists():
        return None
    
    try:
        with open(mapping_file) as f:
            config = yaml.safe_load(f)
        
        mappings = config.get("mappings", {})
        node_mappings = mappings.get(node_id, {})
        return node_mappings.get(template_id)
    except:
        return None

def _template_id_matches(self, lookup_id, template):
    """检查模板 ID 是否匹配."""
    template_id = template.get("template_id", "").lower()
    title = template.get("title", "").lower()
    lookup = lookup_id.lower().replace("-", "_")
    
    return lookup in template_id or lookup in title.replace(" ", "_")
```

**步骤 4**: 运行测试

```bash
pytest tests/docuswarm/prompts/test_template_mapping.py -v
```

---

## Day 5 下午: F5 - allowed_keys (2小时)

### 步骤 1: 修改 create_update_context_server

```python
# autoBMAD/docuswarm/tools/update_context_sdk.py

def create_update_context_server(
    pipeline_id,
    node_id,
    allowed_operations=None,
    allowed_keys=None,  # F5 FIX
):
    """创建 update_context MCP server."""
    
    @tool(...)
    async def update_context_tool(args):
        tool = UpdateContextTool(
            state_manager=StateManager(),
            pipeline_id=pipeline_id,
            allowed_keys=allowed_keys,  # F5 FIX
        )
        # ... 其余代码 ...
```

### 步骤 2: 修改 NodeToolFilter

```python
# autoBMAD/docuswarm/llm/tool_filter.py

def create_mcp_servers(self, pipeline_id=None):
    # ... 现有代码 ...
    
    if pipeline_id and self.tool_permissions.shared_context.enabled:
        update_server = create_update_context_server(
            pipeline_id=pipeline_id,
            node_id=self.node_id,
            allowed_operations=self.tool_permissions.shared_context.operations,
            allowed_keys=self.tool_permissions.shared_context.allowed_keys,  # F5 FIX
        )
```

### 步骤 3: 确保 NodeSharedContextConfig 支持 allowed_keys

```python
# autoBMAD/nodes/loader.py

@dataclass
class NodeSharedContextConfig:
    enabled: bool = False
    operations: list[str] = field(default_factory=lambda: ["set", "append", "remove"])
    allowed_keys: list[str] | None = None  # F5 FIX
```

### 步骤 4: 运行测试

```bash
pytest tests/docuswarm/tools/test_update_context_allowed_keys.py -v
```

---

## 验证与回归测试

### 全量测试

```bash
# 1. F1-F5 专项测试
pytest tests/docuswarm/context/test_multi_document_validation.py -v
pytest tests/docuswarm/llm/test_update_context_server_creation.py -v
pytest tests/docuswarm/llm/test_sdk_skills_discovery.py -v
pytest tests/docuswarm/prompts/test_template_mapping.py -v
pytest tests/docuswarm/tools/test_update_context_allowed_keys.py -v

# 2. 模块级回归测试
pytest tests/docuswarm/context/ -v --tb=short
pytest tests/docuswarm/llm/ -v --tb=short
pytest tests/docuswarm/prompts/ -v --tb=short
pytest tests/docuswarm/tools/ -v --tb=short

# 3. 全量回归测试
pytest tests/ -v --tb=short -x
```

### 手动验证

```bash
# 运行调试工具验证修复
python tools/docuswarm_f1_multidoc_validator_debugger.py
python tools/docuswarm_f2_update_context_debugger.py
python tools/docuswarm_f3_sdk_skills_debugger.py
python tools/docuswarm_f4_template_mapping_debugger.py
python tools/docuswarm_f5_allowed_keys_debugger.py

# 批量运行
python tools/docuswarm_all_findings_runner.py
```

---

## 提交与合并

### 提交规范

```bash
# 按问题分别提交
git add -A
git commit -m "F1: 修复多文档验证器支持 multi-document 格式

- 添加 _validate_multi_document_deliverable 方法
- 修改 _detect_document_count 支持多文档
- 添加测试: test_multi_document_validation.py"

git add -A
git commit -m "F2: 修复 update_context MCP Server 创建链路

- SessionManager 添加 pipeline_id 参数
- IndependentAgent 传递 pipeline_id
- 添加测试: test_update_context_server_creation.py"

git add -A
git commit -m "F3: 修复 SDK Skills 发现机制 cwd 路径

- Orchestrator 添加 _detect_project_root 方法
- SessionManager 使用项目根目录作为 cwd
- 添加测试: test_sdk_skills_discovery.py"

git add -A
git commit -m "F4: 修复模板运行时映射

- 添加 template_mapping.yaml 配置
- ContractBuilder 支持模板 ID 映射
- 添加测试: test_template_mapping.py"

git add -A
git commit -m "F5: 修复 shared_context.allowed_keys 传递

- create_update_context_server 添加 allowed_keys 参数
- NodeToolFilter 传递 allowed_keys
- 添加测试: test_update_context_allowed_keys.py"
```

### 创建 PR

```bash
git push origin fix/f1-f5-deep-reform-implementation

# 在 GitHub/GitLab 创建 PR
# 标题: fix: F1-F5 Deep Reform implementation gaps
# 描述: 修复多文档验证、update_context链路、SDK Skills发现、模板映射、allowed_keys传递
```

---

## 故障排除

### 常见问题

**Q1: 测试找不到模块**
```bash
# 确保 PYTHONPATH 包含项目根目录
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m pytest tests/...
```

**Q2: 修改后测试仍失败**
```bash
# 清除 Python 缓存
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 重新运行测试
pytest tests/... -v
```

**Q3: 与其他功能冲突**
```bash
# 从备份恢复
.cp backup/YYYYMMDD/validator.py autoBMAD/docuswarm/context/validator.py

# 重新应用修复
```

---

## 完成检查清单

- [ ] F1: 多文档验证测试通过
- [ ] F2: update_context server 创建测试通过
- [ ] F3: SDK Skills 发现测试通过
- [ ] F4: 模板映射测试通过 (匹配率 100%)
- [ ] F5: allowed_keys 传递测试通过
- [ ] 所有模块级回归测试通过
- [ ] 全量回归测试通过 (>90%)
- [ ] 调试工具报告所有问题已修复
- [ ] 代码审查完成
- [ ] PR 合并到主分支

---

*快速实施指南 - 预计完成时间: 3-5 天*
