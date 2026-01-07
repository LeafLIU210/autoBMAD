# @.bmad-core/agents/po.md *correct-course 采用增量交互模式，依据奥卡姆剃刀原则，针对@autoBMAD\epic_automation 创建sprint-change-proposal文档保存至 @docs，要求：

## 1. 创建ruff Agent

### 1.  Agent进入条件
autoBMAD\epic_automation\epic_driver.py 之中的 execute_dev_qa_cycle() 方法 返回 True

### 2.  Agent流程
1. 执行ruff check --fix --output-format=json {源代码文件夹的相对路径} 。如果没有任何错误errors，ruff Agent结束。如果有，则继续。
2. 获取json输出中的errors部分，按照文件路径分类错误，生成 文件路径-错误 字典，错误信息为用于claude SDK修复的必要字段信息的汇总
3. 遍历字典的文件路径，每次遍历调用独立的claude agent SDK，执行 claude bypasspermissions，根据文件路径和错误信息创建提示词要求修复ruff错误。遍历调用延时1 min，SDK超时10 min。
4. 参考 @autoBMAD\agentdocs 所有SDK的会话成功结束标志： ResultMessage (is_error=False) - Claude明确声明成功 以及 StopAsyncIteration (有消息计数) - 隐式成功结束。
5. 如果SDK会话失败结束，进行重试，重试次数最大2次
6. 所有SDK会话成功结束或者会话失败结束但超过最大重试次数，结束SDK修复，执行执行ruff check --fix --output-format=json {源代码文件夹的相对路径}，检查是否有错误。如果没有任何错误errors，ruff Agent结束。如果有，则继续循环。
7. ruff检查和SDK修复的循环，最大次数为3次。超过最大次数，ruff Agent结束。

### 3. 注意事项
采用虚拟环境  venv\Scripts
可参考 @autoBMAD 和 ruff 官方文档 ，**不要参考basedpyright-workflow**
参考 ruff --help




## 2. 创建basedpyright Agent

### 1.  Agent进入条件
ruff Agent结束

### 2.  Agent流程
1. 执行basedpyright --outputjson {源代码文件夹的相对路径} 。如果没有任何错误errors，basedpyright Agent结束。如果有，则继续。
2. 获取json输出中的errors部分，按照文件路径分类错误，生成 文件路径-错误 字典，错误信息为用于claude SDK修复的必要字段信息的汇总
3. 遍历字典的文件路径，每次遍历调用独立的claude agent SDK，执行 claude bypasspermissions，根据文件路径和错误信息创建提示词要求修复basedpyright错误。遍历调用延时1 min，SDK超时10 min。
4. 参考 @autoBMAD\agentdocs 所有SDK的会话成功结束标志： ResultMessage (is_error=False) - Claude明确声明成功 以及 StopAsyncIteration (有消息计数) - 隐式成功结束。
5. 如果SDK会话失败结束，进行重试，重试次数最大2次
6. 所有SDK会话成功结束或者会话失败结束但超过最大重试次数，结束SDK修复，执行basedpyright --outputjson {源代码文件夹的相对路径} ，检查是否有错误。如果没有任何错误errors，basedpyright Agent结束。如果有，则继续循环。
7. basedpyright检查和SDK修复的循环，最大次数为3次。超过最大次数，basedpyright Agent结束。

### 3. 注意事项
采用虚拟环境  venv\Scripts
可参考 @autoBMAD 和 basedpyright 官方文档 ，**不要参考basedpyright-workflow**
参考 basedpyright--help


## 3. 创建pytest Agent

### 1.  Agent进入条件
basedpyright Agent结束

### 2.  Agent流程
1. 虚拟环境安装pytest-json-report，执行pytest -v --tb=short --json-report {测试文件夹的相对路径} 。如果没有任何错误error或失败failed，pytest Agent结束。如果有，则继续。
2. 获取json输出中的error和failed部分，按照文件路径分类错误，生成 文件路径-失败错误 字典，失败错误信息为用于claude SDK修复的必要字段信息的汇总
3. 遍历字典的文件路径，每次遍历调用独立的claude agent SDK，执行 claude bypasspermissions，根据文件路径和失败错误信息创建提示词要求修复pytest错误。遍历调用延时1 min，SDK超时20 min。
4. 参考 @autoBMAD\agentdocs 所有SDK的会话成功结束标志： ResultMessage (is_error=False) - Claude明确声明成功 以及 StopAsyncIteration (有消息计数) - 隐式成功结束。
5. 如果SDK会话失败结束，进行重试，重试次数最大2次
6. 所有SDK会话成功结束或者会话失败结束但超过最大重试次数，结束SDK修复，执行pytest -v --tb=short --json-report {测试文件夹的相对路径} ，检查是否有错误。。如果没有任何错误error或失败failed，pytest Agent结束。如果有，则继续循环。
7. pytest检查和SDK修复的循环，最大次数为3次。超过最大次数，pytest Agent结束。

### 3. 注意事项
采用虚拟环境  venv\Scripts
可参考 @autoBMAD 和 pytest 官方文档
参考 pytest--help


## pytest agent结束，则 epic_automation工作流(autoBMAD\epic_automation\epic_driver.py运行)结束