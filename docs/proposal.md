# 深度研究深度改造 @autoBMAD/docuswarm 的详细方案，采用或创建完善调试工具 @tools 来深度研究方案，创建多份详细的研究报告，保存到 @docs/research 的新创建的文件夹中。具体要求如下：
## 1. 研究claude-agent-sdk的skills技能命令引入方案，参考 @autoBMAD/agentdocs 。
## 2. 各个节点的独立agent的任务应当修改更新，并应当使用相应的skill，要求：
### 1. analyst节点独立agent任务为`create-product-brief`，应采用技能skill `bmad-product-brief` ，参考 @.claude/skills/bmad-product-brief 和 @.claude/skills/bmad-product-brief/SKILL.md ；
### 2. pm节点独立agent任务为`create-prd`，应采用技能skill `bmad-create-prd` ，参考 @.claude/skills/bmad-create-prd 和 @.claude/skills/bmad-create-prd/workflow.md ；
### 3. ux节点独立agent任务为`create-ux-design`，应采用技能skill `bmad-create-ux-design` ，参考 @.claude/skills/bmad-create-ux-design 和 @.claude/skills/bmad-create-ux-design/workflow.md ；
### 4. architect节点独立agent任务为`create-architecture`，应采用技能skill `bmad-create-architecture` ，参考 @.claude/skills/bmad-create-architecture 和 @.claude/skills/bmad-create-architecture/workflow.md ；
### 5. po节点独立agent任务为`create-epics-and-stories`，应采用技能skill `bmad-create-epics-and-stories` ，参考 @.claude/skills/bmad-create-epics-and-stories 和 @.claude/skills/bmad-create-epics-and-stories/workflow.md 。
## 3. analyst、pm、ux节点要求且只能创建一份文档。architect和po节点能创建多份文档。po节点应当创建全部epic文档和全部story文档。所有节点文档模板应当参考 @_bmad/bmm 和 前面所述的bmad技能。
## 4. 所有节点的独立agent和评估agent都应当允许全部工具：create_deliverable / read_document / list_documents / grep_search / glob_search 。
## 5. 节点独立agent应当允许调用工具更新shared_context 。
## 6. 创建单独的摘要agent，用于调用工具遍历读取original_context里的所有文档，将文档内容总结，最后将所有文档的总结内容注入到 docs_context 。修改完善 context_builder.py 。
## 7. docs_context不能每次独立agent执行前重建，而应当在建立origin_context后就建立和持久化。