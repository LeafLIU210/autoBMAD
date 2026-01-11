---
active: true
iteration: 1
max_iterations: 10
completion_promise: "DONE"
started_at: "2026-01-10T16:53:07Z"
---

参考@CANCEL_SCOPE_综合修复报告_20260111.md, 采用 @autoBMAD\epic_automation 工作流针对src进行开发，执行相关Bash命令'
cd /d/GITHUB/pytQt_template/ && source venv/Scripts/activate && python -m autoBMAD.epic_automation.epic_driver docs/epics/epic-2-algorithm-optimization-and-analysis.md --verbose --source-dir src --test-dir tests 2>&1 | tee autoBMAD/epic_automation/logs/epic_run_{时间戳}.log
'，并审查src文件夹是否有依照epic文档和stories文档进行开发，以及检查工作流是否中断。如果src实际并未执行开发或者工作流中断，应当修改工作流代码。代码修改要求：1. **只允许修改位于 autoBMAD\epic_automation 的代码**； 2. 每次代码修改后，用basedpyright（不是basedpyright-workflow）检查代码是否有错误error，如有则修复错误；3. **严禁直接修改故事文档和src文件夹**；4. **严禁修改py文件中的prompt**；5. **严禁修改涉及claude_agent_sdk的任何相关参数和代码**。当所有最终要求完成：1. @docs\stories 的所有故事文档Status 为 'Done' 或 'Ready for Done' (**严禁直接或间接修改故事文档**); 2.src文件夹依照epic文档和stories文档开发完成。输出 <promise>DONE</promise>
