# Epic: BMAD SM-Dev-QA Cycle Automation

**Epic ID**: EPIC-001
**Version**: 1.1
**Date**: 2026-01-04
**Priority**: High
**Epic Owner**: Product Owner

---

## 📋 Epic Overview

### Business Objective

Automate the complete BMAD SM-Dev-QA cycle for epic development, enabling fully autonomous workflow execution from epic document to production-ready code with minimal human intervention.

### Success Criteria

- ✅ **Autonomous Execution**: Complete SM-Dev-QA cycle runs without manual intervention
- ✅ **Quality Gates**: Automated QA validation using BasedPyright-Workflow and Fixtest-Workflow
- ✅ **Progress Monitoring**: Real-time tracking with SQLite persistence
- ✅ **Error Recovery**: Automatic retry mechanism for failed stories
- ✅ **Template Portability**: Self-contained, no dependency on bmad-workflow
- ✅ **Knowledge Reuse**: Uses .bmad-core/tasks/*.md as agent prompts
- ✅ **Occam's Razor Compliance**: 5 files vs original 9 files (44% reduction)

### Scope

**In Scope**:
- Epic document parsing and story extraction
- Story creation using BMAD templates
- Code development with TDD methodology
- Code and document review
- QA validation and issue resolution
- Progress monitoring until completion

**Out of Scope**:
- Multi-epic coordination
- Resource scheduling optimization
- Advanced analytics and reporting

---

## 🎯 Stories

### Story 1: Self-Contained Python Driver Architecture
**Story ID**: 001
**Priority**: High
**Estimated Effort**: 3 days

**As a** BMAD automation system,
**I want to** implement a self-contained Python driver that reads .bmad-core/tasks/*.md as prompts,
**So that** I can have a portable solution independent of bmad-workflow.

**Acceptance Criteria**:
- [ ] Creates autoBMAD/epic_automation/ directory structure
- [ ] Implements epic_driver.py with async/await pattern (250-300 lines)
- [ ] Reads .bmad-core/tasks/*.md files as agent prompt knowledge
- [ ] Uses Claude Agent SDK directly (no bmad-workflow dependency)
- [ ] Implements SQLite state management (progress.db)
- [ ] Follows Occam's Razor principle (minimal entities)

**Implementation Notes**:
- Architecture: Single epic_driver.py + state_manager.py + 3 agent files
- Direct Claude SDK calls without command mapping layer
- Independent SQLite implementation for progress tracking
- Template portability - works in new projects without setup

---

### Story 2: Three-Agent Implementation (SM/Dev/QA)
**Story ID**: 002
**Priority**: High
**Estimated Effort**: 2 days

**As a** BMAD automation system,
**I want to** have dedicated Python agent classes for SM, Dev, and QA phases,
**So that** each phase can be tested and maintained independently.

**Acceptance Criteria**:
- [ ] Creates sm_agent.py (80-100 lines) - reads create-next-story.md
- [ ] Creates dev_agent.py (80-100 lines) - reads develop-story.md
- [ ] Creates qa_agent.py (80-100 lines) - reads review-story.md
- [ ] All agents share BaseAgent pattern with load_task_guidance()
- [ ] Each agent creates fresh Claude SDK client per session
- [ ] QA agent returns structured results (PASS/CONCERNS/FAIL/WAIVED)

**Implementation Notes**:
- BaseAgent class loads .bmad-core/tasks/*.md as system prompts
- Individual agents for clarity and maintainability
- Direct SDK integration without command mapping layer
- Error handling with informative messages

---

### Story 3: Independent State Management & Progress Tracking
**Story ID**: 003
**Priority**: High
**Estimated Effort**: 2 days

**As a** project manager,
**I want to** monitor workflow progress with persistent state management,
**So that** I can track completion status and recover from interruptions.

**Acceptance Criteria**:
- [ ] Creates state_manager.py (100-150 lines) - independent SQLite implementation
- [ ] Implements progress.db with stories table (id, epic_path, story_path, status, iteration, qa_result)
- [ ] Tracks story status transitions (pending → in_progress → review → pass/fail)
- [ ] Records iteration counts and QA results for analysis
- [ ] Supports interrupt/resume functionality
- [ ] Independent from @autonomous-coding - portable to new projects

**Implementation Notes**:
- Schema: stories table with comprehensive status tracking
- SQLite for simplicity and portability
- Clear status indicators for real-time monitoring
- Recovery mechanism after crashes or interruptions

---

### Story 4: QA Tools Integration & Automation
**Story ID**: 004
**Priority**: Medium
**Estimated Effort**: 2 days

**As a** QA engineer,
**I want to** automatically run BasedPyright and Fixtest workflows during development,
**So that** I can ensure code quality without manual intervention.

**Acceptance Criteria**:
- [ ] Integrates BasedPyright-Workflow via subprocess calls
- [ ] Integrates Fixtest-Workflow via subprocess calls
- [ ] Runs quality checks after Dev phase automatically
- [ ] Handles QA failures with automatic retry mechanism
- [ ] Parses QA tool output for pass/fail decisions
- [ ] Updates story status based on QA results

**Implementation Notes**:
- Use Python subprocess for tool integration
- BasedPyright: Type checking and code quality
- Fixtest: Automated test execution and repair
- Failure handling with informative error messages
- Seamless integration with story cycle

---

### Story 5: CLI Interface, Documentation & Template Portability
**Story ID**: 005
**Priority**: Low
**Estimated Effort**: 2 days

**As a** developer,
**I want to** use the automation system as a portable template in new projects,
**So that** I can quickly set up BMAD automation without complex configuration.

**Acceptance Criteria**:
- [ ] CLI interface: `python epic_driver.py <epic_path> [options]`
- [ ] Options: --max-iterations, --retry-failed, --verbose, --concurrent
- [ ] Creates comprehensive README.md with installation and usage instructions
- [ ] Example epic with 3-5 stories in test-docs/epics/example-epic.md
- [ ] Troubleshooting guide and common issues
- [ ] Template packaging - copy folder to new projects and run

**Implementation Notes**:
- Simple argparse interface in epic_driver.py
- Comprehensive documentation for easy adoption
- Error handling with informative messages
- Self-contained - no external dependencies beyond Claude SDK
- Works immediately in new projects without setup

---

## 🏗️ Technical Architecture

### Design Principle: Occam's Razor

Following the principle "如无必要,勿增实体" (Don't multiply entities beyond necessity):

| Aspect | Original Plan | Recommended Plan | Reduction |
|--------|---------------|------------------|-----------|
| **Files** | 9 files | 5 files | 44% ↓ |
| **Code** | 1500-2000 lines | 500-600 lines | 70% ↓ |
| **Time** | 4 weeks | 8-10 days | 75% ↓ |
| **Complexity** | High (Mixed Architecture) | Low (Self-Contained Python) | 80% ↓ |
| **Dependencies** | bmad-workflow required | **None** - Fully Independent | 100% ↓ |

### Architecture Diagram

```
autoBMAD/epic_automation/
├── epic_driver.py (250-300 lines)           # ✅ 主协调器
│   - Epic parsing & story extraction
│   - Claude SDK direct integration
│   - Loop control with safety guards
│   - Reads .bmad-core/tasks/*.md as prompts
├── state_manager.py (100-150 lines)         # ✅ 独立状态管理
│   - SQLite state persistence (progress.db)
│   - Stories table with status tracking
│   - Independent from @autonomous-coding
├── sm_agent.py (80-100 lines)               # ✅ SM阶段代理
│   - Loads create-next-story.md as prompt
│   - Creates story documents
├── dev_agent.py (80-100 lines)              # ✅ Dev阶段代理
│   - Loads develop-story.md as prompt
│   - Implements story code
├── qa_agent.py (80-100 lines)               # ✅ QA阶段代理
│   - Loads review-story.md as prompt
│   - Returns PASS/CONCERNS/FAIL/WAIVED
└── README.md (使用说明)

BMAD Knowledge Base
│  ┌─────────────────────────────────────┐
│  │  .bmad-core/tasks/*.md             │  ← Agent prompt knowledge
│  │  - create-next-story.md            │
│  │  - develop-story.md                │
│  │  - review-story.md                 │
│  └─────────────────┬───────────────────┘
                    ↓
          Claude Agent SDK (Direct调用)
```

### Key Components

1. **epic_driver.py** - Self-contained orchestrator
   - Epic parsing using regex
   - Direct Claude SDK calls (no bmad-workflow dependency)
   - Loop control with safety guards
   - Coordinates the three agent phases

2. **state_manager.py** - Independent SQLite implementation
   - SQLite state persistence (progress.db)
   - Stories table with comprehensive status tracking
   - Progress persistence and recovery
   - **Fully portable** - works in new projects without setup

3. **Three Agent Classes** - SM/Dev/QA phases
   - Each loads corresponding .bmad-core/tasks/*.md as system prompt
   - Individual classes for clarity and maintainability
   - Fresh Claude SDK client per session
   - Direct knowledge integration from BMAD ecosystem

4. **Knowledge Integration**
   - Reads .bmad-core/tasks/*.md files as agent prompts
   - No command mapping layer needed
   - Direct knowledge reuse from existing BMAD system

### Why autoBMAD Location?

**Template Independence**: As a **universal development template**, this project may be copied to create new projects. By placing epic automation in autoBMAD:
- ✅ Self-contained - No dependency on @autonomous-coding
- ✅ Portable - Can be used independently in new projects
- ✅ Scalable - Easy to extend without breaking existing patterns
- ✅ Modular - Clear separation of concerns

---

## 📊 Implementation Timeline

### Phase 1: Core Driver Implementation (Days 1-3)
**Stories**: Story 1 (Self-Contained Architecture) + Story 2 (Three Agents)
**Deliverable**: Functional epic_driver.py with SM/Dev/QA agents v1.0

- Day 1: Epic parsing & base epic_driver.py structure
- Day 2: Implement three agent classes (SM/Dev/QA) with BMAD knowledge integration
- Day 3: Main loop control with safety guards and error handling

### Phase 2: State Management & Progress Tracking (Day 4)
**Story**: Story 3 (Independent State Management)
**Deliverable**: Complete state management system

- Day 4: Implement state_manager.py with SQLite persistence and recovery

### Phase 3: QA Tools Integration (Days 5-6)
**Story**: Story 4 (QA Tools Integration)
**Deliverable**: Integrated QA workflow

- Day 5: BasedPyright-Workflow integration via subprocess
- Day 6: Fixtest-Workflow integration with failure handling

### Phase 4: CLI, Documentation & Template Portability (Days 7-8)
**Story**: Story 5 (CLI Interface & Template Portability)
**Deliverable**: Production-ready template

- Day 7: CLI interface with comprehensive options
- Day 8: Documentation, examples, and template packaging

**Total Duration**: 8 working days (1.5 weeks)

---

## ✅ Quality Assurance

### Testing Strategy

1. **Unit Tests** (Stories 1, 2)
   - Epic parsing logic
   - SQLite state transitions
   - BMAD command integration

2. **Integration Tests** (Stories 3, 4)
   - Full SM-Dev-QA cycle
   - QA tools workflow
   - Progress monitoring

3. **End-to-End Tests** (Story 5)
   - Complete epic automation
   - Error recovery scenarios
   - Performance benchmarks

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Development Time** | 8-10 days vs 28 days | **71% reduction** from original plan |
| **File Count** | 5 files vs 9 files | **44% reduction** - follows Occam's Razor |
| **Code Lines** | 500-600 vs 1500-2000 | **70% reduction** - self-contained Python |
| **Template Independence** | 100% vs 0% | **No bmad-workflow dependency** |
| **Maintenance Cost** | 1 hour/month vs 5 hours/month | **80% reduction** in ongoing maintenance |
| **Automation Rate** | ≥70% of stories | Stories completed without intervention |
| **Recovery Rate** | ≥95% from interruptions | Successful resume after crash |

---

## 🔄 Risks & Mitigations

### High Priority Risks

1. **Claude Agent SDK API Changes**
   - **Probability**: Medium
   - **Impact**: High
   - **Mitigation**: Encapsulate SDK calls in BaseAgent class

2. **Epic Format Variations**
   - **Probability**: Medium
   - **Impact**: Medium
   - **Mitigation**: Format validation + clear error messages

3. **Story Dependencies**
   - **Probability**: Low
   - **Impact**: High
   - **Mitigation**: Phase 1后评估，如需则添加依赖图

### Medium Priority Risks

1. **SQLite Concurrency Issues**
   - **Probability**: Low
   - **Impact**: Medium
   - **Mitigation**: File locking + transaction management

2. **Resource Exhaustion**
   - **Probability**: Low
   - **Impact**: Low
   - **Mitigation**: Iteration limits + resource monitoring

---

## 📚 Dependencies

### External Dependencies
- **BMAD Ecosystem**: Core orchestration capability
- **Claude Agent SDK**: Agent communication
- **BasedPyright-Workflow**: Code quality validation
- **Fixtest-Workflow**: Test automation

### Internal Dependencies
- **BMAD Templates**: Story and epic templates
- **autonomous-coding Pattern**: SQLite state management
- **BMAD Workflow Tools**: Command execution framework

---

## 📈 Success Metrics

### Quantitative Metrics
- **Development Time**: 8-10 days vs 28 days (71% reduction)
- **File Count**: 2 files vs 9 files (78% reduction)
- **Code Lines**: 350 lines vs 1750 lines (80% reduction)
- **Maintenance Cost**: 0.5 hours/month vs 5 hours/month (90% reduction)
- **Template Independence**: 100% vs 0% (无依赖@autonomous-coding)

### Qualitative Metrics
- **Simplicity**: Single file, no abstraction layers
- **Reliability**: Reuse of proven patterns
- **Maintainability**: BMAD native integration
- **Extensibility**: Easy to add features

---

## 🎯 Definition of Done

### For Epic Completion
- [ ] All 5 stories implemented and tested
- [ ] Documentation complete (README, examples, troubleshooting)
- [ ] End-to-end test passes with sample epic
- [ ] Code review completed
- [ ] Integration with BMAD ecosystem verified
- [ ] QA tools workflow validated
- [ ] Performance benchmarks met

### For Each Story
- [ ] Acceptance criteria met
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Code reviewed by peer
- [ ] Documentation updated
- [ ] No critical or high severity bugs

---

## 📞 Stakeholder Sign-off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| **Product Owner** | Sarah | Pending | | |
| **Tech Lead** | | Pending | | |
| **QA Lead** | | Pending | | |
| **Dev Team** | | Pending | | |

---

## 📝 Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | 2026-01-04 | Product Owner | Updated based on BMAD Epic Automation Evaluation Report:<br>- Changed to self-contained Python driver architecture<br>- Reduced from 9 files to 5 files (44% reduction)<br>- Updated to 8-10 days timeline (75% time reduction)<br>- Removed bmad-workflow dependency<br>- Updated stories to reflect recommended approach |
| 1.0 | 2026-01-04 | Product Owner | Initial epic creation |

---

**Epic Status**: 📋 Draft → Ready for Planning
**Next Step**: Story breakdown and task assignment

---

*Powered by BMAD™ Method - Breaking Through Agile AI-Driven Development*
