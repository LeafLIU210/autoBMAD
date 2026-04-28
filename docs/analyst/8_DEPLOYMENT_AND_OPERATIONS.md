# DocuSwarm Deployment & Operations Analysis

**Version**: 2.0 (Occam's Razor Simplified)  
**Date**: 2026-02-19  
**Category**: Deployment & Operations  
**Topics Covered**: 8.1 - 8.4  
**Status**: Analysis Complete - Simplified

---

## Executive Summary

This analysis covers 4 topics related to deployment and operational concerns for DocuSwarm. The focus is on standalone Python deployment, simplified output structure, and basic cost tracking.

**Key Simplifications from Occam's Razor Analysis**:
- Standalone Python application (VCPToolBox plugin deferred)
- Simplified output directory (flat structure)
- Basic Python logging (no Pino/Prometheus for MVP)
- Simple cost tracking (per-pipeline reporting)

**Key Findings**:
- Standalone Python app is fastest to deploy and test
- Flat output directory sufficient for MVP
- Python logging provides adequate observability
- Simple cost tracking enables budget awareness

**Critical Dependencies**: All previous section decisions must be finalized for deployment planning.

**Development Time Savings**: ~3-4 weeks compared to VCPToolBox plugin architecture.

---

## Topic 8.1: Output Directory Structure (Simplified)

### Context

**Occam's Razor Decision**: Simplified flat output directory instead of BMAD-aligned nested structure.

### Implementation Guidance

**Simplified Structure**:

```
output/
├── pipelines/
│   └── {pipeline-id}/
│       ├── state.json              # Pipeline state
│       ├── analyst-report.md       # Analyst deliverable
│       ├── prd.md                  # PM deliverable
│       ├── ux-design.md            # UX deliverable
│       ├── architecture.md         # Architect deliverable
│       ├── epics-stories.md        # PO deliverable
│       └── questions.json          # All questions collected
│
├── logs/
│   └── docuswarm.log               # Application logs
│
└── docuswarm.db                    # SQLite database
```

**Path Manager (Simplified)**:

```python
from pathlib import Path
from typing import Optional

class PathManager:
    """Simplified path management for MVP."""
    
    def __init__(self, base_path: str = "output"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "docuswarm.db"
        self.logs_path = self.base_path / "logs"
    
    def get_pipeline_dir(self, pipeline_id: str) -> Path:
        """Get pipeline output directory."""
        return self.base_path / "pipelines" / pipeline_id
    
    def get_deliverable_path(self, pipeline_id: str, node_id: str) -> Path:
        """Get deliverable file path."""
        filename_map = {
            "analyst": "analyst-report.md",
            "pm": "prd.md",
            "ux": "ux-design.md",
            "architect": "architecture.md",
            "po": "epics-stories.md"
        }
        filename = filename_map.get(node_id, f"{node_id}.md")
        return self.get_pipeline_dir(pipeline_id) / filename
    
    def get_state_path(self, pipeline_id: str) -> Path:
        """Get pipeline state file path."""
        return self.get_pipeline_dir(pipeline_id) / "state.json"
    
    def get_questions_path(self, pipeline_id: str) -> Path:
        """Get questions collection file path."""
        return self.get_pipeline_dir(pipeline_id) / "questions.json"
    
    def ensure_directories(self, pipeline_id: str):
        """Create necessary directories."""
        self.get_pipeline_dir(pipeline_id).mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)
```

### Recommendation

**Flat directory structure** for MVP.

Benefits:
- Simple to understand and navigate
- Easy backup (single directory)
- Clear per-pipeline organization
- No nested complexity

---

## Topic 8.2: Deployment Model (Standalone Python)

### Context

**Occam's Razor Decision**: Standalone Python application for MVP. VCPToolBox plugin and BMAD module deferred to Phase 2.

### Implementation Guidance

**Project Structure**:

```
docuswarm/
├── pyproject.toml
├── README.md
├── docuswarm/
│   ├── __init__.py
│   ├── __main__.py           # Entry point
│   ├── cli.py                # CLI interface
│   ├── config.py             # Configuration
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── graph.py          # LangGraph pipeline
│   │   └── state.py          # State definitions
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── independent.py
│   │   ├── evaluator.py
│   │   └── orchestrator.py
│   │
│   ├── nodes/
│   │   ├── __init__.py
│   │   └── dual_agent.py
│   │
│   └── storage/
│       ├── __init__.py
│       └── sqlite.py
│
├── nodes/                    # Node configurations
│   ├── analyst/
│   ├── pm/
│   ├── ux/
│   ├── architect/
│   └── po/
│
├── output/                   # Output directory
└── tests/
```

**CLI Implementation**:

```python
# docuswarm/cli.py
import argparse
import asyncio
from .pipeline.graph import SequentialPipeline
from .storage.sqlite import SQLiteStateManager
from .config import load_config

def main():
    parser = argparse.ArgumentParser(
        description="DocuSwarm - Multi-agent document orchestration"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run a pipeline")
    run_parser.add_argument("intent", help="Pipeline intent/request")
    run_parser.add_argument("--config", "-c", help="Config file path")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check pipeline status")
    status_parser.add_argument("pipeline_id", nargs="?", help="Pipeline ID")
    
    # Resume command
    resume_parser = subparsers.add_parser("resume", help="Resume a pipeline")
    resume_parser.add_argument("pipeline_id", help="Pipeline ID to resume")
    
    args = parser.parse_args()
    
    if args.command == "run":
        asyncio.run(run_pipeline(args.intent, args.config))
    elif args.command == "status":
        show_status(args.pipeline_id)
    elif args.command == "resume":
        asyncio.run(resume_pipeline(args.pipeline_id))
    else:
        parser.print_help()

async def run_pipeline(intent: str, config_path: str = None):
    """Run a new pipeline."""
    config = load_config(config_path)
    
    print(f"Starting pipeline with intent: {intent}")
    print("-" * 50)
    
    pipeline = SequentialPipeline(config)
    result = await pipeline.run({"intent": intent})
    
    print("-" * 50)
    print(f"Pipeline completed: {result['pipeline_id']}")
    print(f"Status: {result['status']}")
    print(f"Deliverables: {len(result.get('deliverables', {}))}")

def show_status(pipeline_id: str = None):
    """Show pipeline status."""
    state_manager = SQLiteStateManager()
    
    if pipeline_id:
        state = state_manager.get_pipeline(pipeline_id)
        if state:
            print(f"Pipeline: {pipeline_id}")
            print(f"Status: {state['status']}")
            print(f"Current node: {state.get('current_node', 'N/A')}")
            print(f"Completed nodes: {state_manager.get_completed_nodes(pipeline_id)}")
        else:
            print(f"Pipeline not found: {pipeline_id}")
    else:
        # List recent pipelines
        print("Recent pipelines:")
        # Would need method to list pipelines

async def resume_pipeline(pipeline_id: str):
    """Resume a pipeline."""
    config = load_config()
    pipeline = SequentialPipeline(config)
    
    print(f"Resuming pipeline: {pipeline_id}")
    result = await pipeline.resume(pipeline_id)
    
    print(f"Pipeline resumed and completed: {result['status']}")

if __name__ == "__main__":
    main()
```

**Entry Point (__main__.py)**:

```python
# docuswarm/__main__.py
from .cli import main

if __name__ == "__main__":
    main()
```

**Installation & Usage**:

```bash
# Install from source
pip install -e .

# Or install dependencies directly
pip install langgraph kimi-agent-sdk pyyaml

# Run pipeline
python -m docuswarm run "Create a project management tool for remote teams"

# Check status
python -m docuswarm status ds-2026-02-19-001

# Resume failed pipeline
python -m docuswarm resume ds-2026-02-19-001
```

### Recommendation

**Standalone Python CLI** for MVP.

Benefits:
- Fastest to implement and test
- No plugin architecture complexity
- Easy to debug and iterate
- Clear upgrade path to Phase 2

Phase 2 Options:
- VCPToolBox Plugin wrapper
- BMAD Module integration
- Web API (FastAPI)

---

## Topic 8.3: Monitoring and Logging (Simplified)

### Context

**Occam's Razor Decision**: Python standard logging instead of Pino/Prometheus.

### Implementation Guidance

**Simple Logging Setup**:

```python
# docuswarm/logging_config.py
import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(
    log_level: str = "INFO",
    log_file: str = None
):
    """Setup basic logging for DocuSwarm."""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # File handler (optional)
    handlers = [console_handler]
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers
    )
    
    # Suppress noisy libraries
    logging.getLogger("kimi_agent_sdk").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get a logger for a component."""
    return logging.getLogger(f"docuswarm.{name}")
```

**Pipeline Logger**:

```python
# docuswarm/pipeline_logger.py
import logging
from datetime import datetime
from typing import Optional

class PipelineLogger:
    """Simple pipeline execution logger."""
    
    def __init__(self, pipeline_id: str):
        self.pipeline_id = pipeline_id
        self.logger = logging.getLogger(f"docuswarm.pipeline.{pipeline_id}")
        self.start_time = datetime.now()
    
    def pipeline_started(self, intent: str):
        self.logger.info(f"Pipeline started - Intent: {intent[:100]}...")
    
    def node_started(self, node_id: str):
        self.logger.info(f"Node started: {node_id}")
    
    def node_completed(
        self, 
        node_id: str, 
        score: float, 
        verdict: str,
        iterations: int,
        duration_ms: int
    ):
        self.logger.info(
            f"Node completed: {node_id} - "
            f"verdict={verdict}, score={score:.2f}, "
            f"iterations={iterations}, duration={duration_ms}ms"
        )
    
    def node_failed(self, node_id: str, error: str):
        self.logger.error(f"Node failed: {node_id} - {error}")
    
    def api_call(
        self, 
        provider: str, 
        input_tokens: int, 
        output_tokens: int,
        cost: float
    ):
        self.logger.debug(
            f"API call: {provider} - "
            f"tokens={input_tokens}+{output_tokens}, cost=${cost:.4f}"
        )
    
    def pipeline_completed(self, status: str):
        duration = (datetime.now() - self.start_time).total_seconds()
        self.logger.info(
            f"Pipeline completed - status={status}, duration={duration:.1f}s"
        )
```

### Recommendation

**Python standard logging** for MVP.

Configuration:
- Console output for interactive use
- File logging for debugging (optional)
- Log level configurable via environment

Benefits:
- Zero external dependencies
- Familiar Python patterns
- Easy to upgrade later

---

## Topic 8.4: Cost Optimization (Simplified)

### Context

**Occam's Razor Decision**: Simple cost tracking instead of full optimization infrastructure.

### Implementation Guidance

**Simple Cost Tracker**:

```python
# docuswarm/cost_tracker.py
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime

@dataclass
class APICallRecord:
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PipelineCost:
    pipeline_id: str
    calls: List[APICallRecord] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    
    @property
    def total_cost(self) -> float:
        return sum(c.cost for c in self.calls)
    
    @property
    def total_tokens(self) -> int:
        return sum(c.input_tokens + c.output_tokens for c in self.calls)

class CostTracker:
    """Simple cost tracking for MVP."""
    
    # Pricing per million tokens
    RATES = {
        "kimi-k2.5": {"input": 0.60, "output": 2.50},
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00}
    }
    
    def __init__(self):
        self.pipelines: Dict[str, PipelineCost] = {}
    
    def start_pipeline(self, pipeline_id: str):
        """Start tracking a pipeline."""
        self.pipelines[pipeline_id] = PipelineCost(pipeline_id=pipeline_id)
    
    def record_call(
        self,
        pipeline_id: str,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Record an API call and return cost."""
        cost = self._calculate_cost(model, input_tokens, output_tokens)
        
        if pipeline_id not in self.pipelines:
            self.start_pipeline(pipeline_id)
        
        self.pipelines[pipeline_id].calls.append(APICallRecord(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost
        ))
        
        return cost
    
    def get_pipeline_cost(self, pipeline_id: str) -> PipelineCost:
        """Get cost summary for a pipeline."""
        return self.pipelines.get(pipeline_id)
    
    def print_summary(self, pipeline_id: str):
        """Print cost summary."""
        cost = self.get_pipeline_cost(pipeline_id)
        if not cost:
            print(f"No cost data for pipeline: {pipeline_id}")
            return
        
        print(f"\n=== Cost Summary: {pipeline_id} ===")
        print(f"Total cost: ${cost.total_cost:.4f}")
        print(f"Total tokens: {cost.total_tokens:,}")
        print(f"API calls: {len(cost.calls)}")
        
        # Breakdown by provider
        by_provider: Dict[str, float] = {}
        for call in cost.calls:
            by_provider[call.provider] = by_provider.get(call.provider, 0) + call.cost
        
        print("\nBy provider:")
        for provider, provider_cost in sorted(by_provider.items()):
            print(f"  {provider}: ${provider_cost:.4f}")
    
    def _calculate_cost(
        self, 
        model: str, 
        input_tokens: int, 
        output_tokens: int
    ) -> float:
        """Calculate cost for tokens."""
        rates = self.RATES.get(model, {"input": 0, "output": 0})
        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]
        return input_cost + output_cost
```

**Usage in Pipeline**:

```python
# In pipeline execution
cost_tracker = CostTracker()
cost_tracker.start_pipeline(pipeline_id)

# After each LLM call
cost = cost_tracker.record_call(
    pipeline_id=pipeline_id,
    provider="kimi",
    model="kimi-k2.5",
    input_tokens=response.usage.prompt_tokens,
    output_tokens=response.usage.completion_tokens
)

# At end of pipeline
cost_tracker.print_summary(pipeline_id)
```

### Recommendation

**Simple per-pipeline cost tracking** for MVP.

Features:
- Track cost per API call
- Summarize per pipeline
- Breakdown by provider

Expected Costs:
- Per pipeline: ~$0.30-0.50
- Per deliverable: ~$0.05-0.10

Phase 2 Enhancements:
- Budget limits and alerts
- Historical cost analysis
- Optimization recommendations

---

## Deployment Checklist (Simplified)

```markdown
# DocuSwarm MVP Deployment Checklist

## Environment Setup
- [ ] Python 3.10+ installed
- [ ] Dependencies installed (pip install -r requirements.txt)
- [ ] KIMI_API_KEY environment variable set
- [ ] Output directory created (./output)

## Configuration
- [ ] config.yaml reviewed and customized
- [ ] Node configurations in place (./nodes/*)
- [ ] Logging level appropriate for environment

## Validation
- [ ] Run test: python -m docuswarm run "Test project"
- [ ] Check output files created
- [ ] Verify SQLite database created
- [ ] Review logs for errors

## Production (if applicable)
- [ ] API keys secured
- [ ] Log rotation configured
- [ ] Backup strategy for output/ directory
```

---

## Cross-Topic Dependencies (Updated)

```
8.1 Output Directory Structure
 └─→ Simplified flat structure
 └─→ 5.1 SQLite State Storage

8.2 Deployment Model
 └─→ Standalone Python CLI
 └─→ 4.6 Python/LangGraph

8.3 Monitoring and Logging
 └─→ Python standard logging
 └─→ 5.6 State Observability

8.4 Cost Optimization
 └─→ Simple cost tracking
 └─→ 6.1 Kimi Mode Selection
```

---

## Summary of Occam's Razor Simplifications

| Topic | Original Design | Simplified Design | Savings |
|-------|----------------|-------------------|---------|
| 8.1 Output | BMAD-aligned nested | Flat directory | Simpler |
| 8.2 Deployment | VCPToolBox Plugin | Standalone Python | ~2-3 weeks |
| 8.3 Monitoring | Pino + Prometheus | Python logging | ~1 week |
| 8.4 Cost | Full optimization | Simple tracking | Simpler |

**Total Estimated Savings**: ~3-4 weeks development time

---

## References

### Research Sources
- Python Packaging Documentation (packaging.python.org)
- Python Logging Documentation (docs.python.org)
- LLM Cost Analysis (2026)

### Related Analysis Documents
- [4_TECHNOLOGY_STACK.md](4_TECHNOLOGY_STACK.md) - Python/LangGraph stack
- [5_STATE_MANAGEMENT.md](5_STATE_MANAGEMENT.md) - SQLite storage

---

**Document Status**: Version 2.0 - Occam's Razor Simplified  
**Key Change**: Standalone Python (not VCPToolBox plugin)  
**Development Time Savings**: ~3-4 weeks compared to plugin architecture
