# Epic 012 故事状态回退根因研究报告

## 1. 背景

- 分析对象命令：`PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py run-epic docs/epics/epic-012-compose-video-slot-refactor.md --verbose 2>&1 | tee autoBMAD/epic_automation/logs/epic_run_epic-012.log`
- 日志文件：`autoBMAD/epic_automation/logs/epic_run_epic-012.log`
- 关注故事：`docs/stories/012.1.md` ~ `docs/stories/012.8.md`
- 关注问题：为什么命令执行完成后，部分故事文档状态仍为 `Ready for Development`，到底是故事未开发完成，还是 `autoBMAD/epic_automation` 状态同步机制有问题。

本报告基于以下三类证据交叉分析：

1. 运行日志
2. 当前故事文档内容
3. `autoBMAD/epic_automation` 与 `src/` 中的实现代码

---

## 2. 结论摘要

### 2.1 最终结论

本次现象 **主要不是故事未开发完成**，而是 **`autoBMAD/epic_automation` 的状态同步链路存在缺陷，导致已完成或已处于终态的故事被错误回写为 `Ready for Development`**。

### 2.2 具体判断

- `012.5`、`012.6`、`012.7`、`012.8`：本次运行中确实进入 Dev-QA 流程，最终被写成 `Ready for Done`，状态与日志一致。
- `012.1`、`012.2`、`012.3`、`012.4`：在本次运行开始时，日志已显示它们处于 `Ready for Done`，说明它们并不是“未开发”；但在最后的“数据库 → Markdown 同步”阶段，被错误改回 `Ready for Development`。

因此：

- **故事 012.1 ~ 012.4 很大概率已经开发完成，至少在本次运行开始时系统自己也判定为 `Ready for Done`。**
- **最终状态错误是 automation bug，不是开发未完成的直接证据。**

---

## 3. 现象复盘

## 3.1 运行开始时的真实状态

日志显示：

- `012.1` 在 `2026-03-06 20:45:04` 被 `state_agent` 解析为 `Ready for Done`
- `012.2` 在 `2026-03-06 20:45:06` 被解析为 `Ready for Done`
- `012.3` 在 `2026-03-06 20:45:09` 被解析为 `Ready for Done`
- `012.4` 在 `2026-03-06 20:45:11` 被解析为 `Ready for Done`

随后 Epic Driver 直接记录这些故事 `completed (Status: Ready for Done)`，没有再进入开发。

这说明：

- 这 4 个故事在运行起点就已经被视为“完成态”
- 系统并没有把它们当成待开发故事

## 3.2 运行结束时发生的错误回写

在 `2026-03-06 21:02:56` 之后，日志进入：

- `=== Syncing Story Statuses ===`

随后状态同步器输出：

- `012.8`: `completed -> Ready for Done`
- `012.7`: `completed -> Ready for Done`
- `012.6`: `completed -> Ready for Done`
- `012.5`: `completed -> Ready for Done`
- `012.4`: `ready_for_development -> Ready for Development`
- `012.3`: `ready_for_development -> Ready for Development`
- `012.2`: `ready_for_development -> Ready for Development`
- `012.1`: `ready_for_development -> Ready for Development`

之后 SDK 逐个成功更新 Markdown，最终导致当前文档状态变成：

- `012.1` ~ `012.4`：`Ready for Development`
- `012.5` ~ `012.8`：`Ready for Done`

这不是“同步失败”，而是 **同步成功地把错误状态写回了文档**。

---

## 4. 当前状态与数据库状态核对

当前 Markdown 文档中：

- `docs/stories/012.1.md`：`Ready for Development`
- `docs/stories/012.2.md`：`Ready for Development`
- `docs/stories/012.3.md`：`Ready for Development`
- `docs/stories/012.4.md`：`Ready for Development`
- `docs/stories/012.5.md`：`Ready for Done`
- `docs/stories/012.6.md`：`Ready for Done`
- `docs/stories/012.7.md`：`Ready for Done`
- `docs/stories/012.8.md`：`Ready for Done`

数据库 `progress.db` 中该 Epic 的记录为：

- `012.1` ~ `012.4`：`status = ready_for_development`，`phase = initialization`
- `012.5` ~ `012.8`：`status = completed`，`phase = completed`

这说明：

1. `012.1` ~ `012.4` 的数据库状态不是“开发后写入的最终状态”，而只是 **初始化阶段留下的状态**。
2. 最后同步时，`StatusUpdateAgent` 把这个初始化状态当作权威来源，覆盖了真实的 Markdown 完成态。

---

## 5. 根因分析

本次问题不是单点 bug，而是 **三层问题叠加**。

## 5.1 第一层根因：状态字段语义混用

相关代码：

- `autoBMAD/epic_automation/epic_driver.py`
- `autoBMAD/epic_automation/state_manager.py`
- `autoBMAD/epic_automation/agents/status_update_agent.py`

### 问题描述

`state_manager.stories.status` 字段被混用了两种不同语义：

1. **Markdown 核心状态**：如 `Ready for Done`
2. **流程处理状态**：如 `in_progress`、`review`、`completed`

但是 `StatusUpdateAgent` 的设计假设是：

- 数据库里的 `status` 只存 **processing_status**
- 然后通过映射：
  - `ready_for_development -> Ready for Development`
  - `in_progress -> Ready for Development`
  - `review -> Ready for Review`
  - `completed -> Ready for Done`

也就是说：

- **同步器把数据库 `status` 当成“流程状态”来解释**
- **Epic Driver 却会在初始化时把“当前故事状态”直接塞进同一个字段**

这导致状态源语义不一致。

### 为什么这很危险

对于已经完成的故事，如果数据库里没有一个明确的 `completed`，而只是残留初始化值，那么最终同步就会把该初始化值回写到 Markdown。

这正是本次 `012.1` ~ `012.4` 的表现。

---

## 5.2 第二层根因：已处于终态的故事没有把数据库同步到终态

相关逻辑：

- `epic_driver.py` 在故事处理开始时，会先把 `story.get("status")` 写入数据库，标记为 `phase="initialization"`
- 之后再读取真实 Markdown 状态
- 如果发现当前状态是 `Done` / `Ready for Done`，就直接 `return True`

### 实际后果

对于 `012.1` ~ `012.4`：

1. 初始化把数据库写成了 `ready_for_development`
2. 随后真实解析发现 Markdown 已是 `Ready for Done`
3. 因为已完成，流程直接跳过开发
4. **但数据库没有被修正为 `completed`**
5. 最终同步阶段又拿数据库回写 Markdown
6. 于是把完成态覆盖成 `Ready for Development`

### 这意味着

即使故事真实状态已经完成，只要数据库没有被同步到 `completed`，最终状态就可能被错误降级。

---

## 5.3 第三层根因：同步解析器错误识别 `**Status**: Ready for Done`

相关代码：

- `epic_driver.py` 中 `_parse_story_status_sync()`
- `epic_driver.py` 中 `_parse_story_status_fallback()`

### 问题描述

同步解析器的 fallback 逻辑只处理两类形式：

1. `**Status**: **Ready for Development**`
2. `Status: Ready for Development`

但当前故事文档实际采用的是：

- `**Status**: Ready for Done`

这个格式具有两个特点：

1. `Status` 本身是加粗的，行内并不包含裸字符串 `Status:`
2. 状态值没有再被 `**` 包起来

因此 fallback 解析失败后，直接返回默认值：

- `ready_for_development`

### 本次运行中的直接影响

这使得 `parse_epic()` 阶段构造出来的 `story["status"]` 对于 `012.1` ~ `012.4` 全部是：

- `ready_for_development`

于是初始化写库时，进一步放大了状态污染。

### 重要说明

这不是唯一根因，但它是本次日志里最直接的触发器。

---

## 5.4 根因之间的关系

三层问题的关系如下：

### 直接触发器

- fallback 状态解析失败，错误返回 `ready_for_development`

### 机制性缺陷

- 数据库 `status` 字段混用核心状态和处理状态
- 已完成故事在跳过执行时，没有把数据库状态修正为 `completed`

### 最终表现

- 最终同步阶段把错误的数据库状态成功回写进了 Markdown

因此，本次是：

**“错误初始化 + 错误状态语义 + 错误最终同步” 三者叠加导致的状态回退事故。**

---

## 6. 为什么 012.5 ~ 012.8 正常，而 012.1 ~ 012.4 异常

## 6.1 012.5 ~ 012.8 的路径

这 4 个故事在运行开始时是 `Ready for Development`，因此进入了完整 Dev-QA 流程：

- Dev 完成后写 `review`
- QA 通过后写 `completed`
- 最终同步时，`completed -> Ready for Done`

所以它们的数据库状态和文档状态是一致的。

## 6.2 012.1 ~ 012.4 的路径

这 4 个故事在运行开始时已经是 `Ready for Done`，所以：

- 没有进入 Dev-QA
- 没有走 `completed` 的 processing_status 写入链路
- 只留下了初始化阶段写入的错误/不合语义状态
- 最终被同步器回写为 `Ready for Development`

换句话说：

- **已完成故事反而更容易被这个 bug 误伤**
- **未完成并完成于本次运行的故事反而能得到正确状态**

---

## 7. 对“故事是否开发完成”的判定

## 7.1 012.1 ~ 012.4 是否“未开发完成”？

综合判断：**不是**。

证据如下：

1. 日志在运行开始时将 `012.1` ~ `012.4` 解析为 `Ready for Done`
2. Epic Driver 随后直接把它们判定为 completed，而非进入待开发流程
3. 对应源码中已经存在这些故事对应的实现痕迹，例如：
   - `src/models/compose_models.py`
   - `src/models/video_slot.py`
   - `src/my_qt_app/cli/main.py`
   - `src/my_qt_app/core/nodes/compose_node.py`
   - `src/my_qt_app/core/video_composer.py`
   - `src/my_qt_app/core/video_slot_extractor.py`
4. 对应测试文件也已存在，例如：
   - `tests/unit/test_compose_models.py`
   - `tests/unit/test_video_slot.py`
   - `tests/unit/nodes/test_compose_node.py`
5. `012.1`、`012.4` 文档内可见 `Dev Agent Record`、`Implementation Summary`、`QA Results PASS` 等完成痕迹；`012.2`、`012.3` 文档中也存在测试通过、覆盖率、文件列表等完成痕迹

### 审慎结论

在不重新执行完整测试的前提下，不能仅凭文档状态断言“100%已交付无误”；但可以明确判断：

- **当前 `Ready for Development` 状态不能作为“尚未开发”的证据**
- **更合理的判断是：这些故事曾经已经完成，但被自动化状态同步错误降级**

---

## 8. autoBMAD 存在的具体缺陷

## 8.1 缺陷一：状态解析 fallback 正则不兼容当前文档格式

表现：

- 不能正确解析 `**Status**: Ready for Done`
- 默认回落到 `ready_for_development`

影响：

- 在 `parse_epic()` 阶段污染故事初始状态

## 8.2 缺陷二：数据库 `status` 字段语义设计不一致

表现：

- 有时写入核心状态
- 有时写入 processing_status
- 最终同步器却只按 processing_status 解读

影响：

- 状态同步不可预测
- 已完成故事尤其容易被回写错

## 8.3 缺陷三：终态故事跳过执行时没有写 `completed`

表现：

- Markdown 已经是 `Ready for Done`
- 流程直接返回成功
- 但数据库没有被修正成 `completed`

影响：

- 最终同步拿不到正确的权威状态

## 8.4 缺陷四：同步器对异常状态过于宽松，默认降级到 `Ready for Development`

表现：

- `StatusUpdateAgent._map_to_core_status()` 对未知状态默认回退到 `Ready for Development`

影响：

- 一旦数据库状态脏了，最终写回会把故事“降级”而不是“保守不动”
- 这是非常危险的默认策略

---

## 9. 根因判定

## 9.1 主责归因

**主责在 `autoBMAD/epic_automation`，不是故事文档本身。**

更准确地说，是以下子系统组合导致：

- `epic_driver.py` 的初始状态写库逻辑
- `epic_driver.py` 的同步 fallback 状态解析逻辑
- `state_manager.py` 的单字段状态存储策略
- `agents/status_update_agent.py` 的最终回写策略

## 9.2 不是根因的项

以下项不是本次主根因：

- 不是 `StatusUpdateAgent` “没执行”——它执行成功了
- 不是 Markdown “没被修改”——它被修改了，而且改错了
- 不是 `012.1` ~ `012.4` 必然未开发——日志恰恰显示它们一开始就处于完成态

---

## 10. 修复建议

## 10.1 立即修复（高优先级）

1. 修复 `_parse_story_status_fallback()`，兼容当前文档格式：
   - `**Status**: Ready for Done`
   - `**Status**: Ready for Review`
   - `**Status**: Ready for Development`

2. 在故事开始时，如果真实 Markdown 状态已是：
   - `Done`
   - `Ready for Done`
   则数据库应直接写入 `completed`，而不是保留初始化值。

3. 在最终同步前增加防降级保护：
   - 如果当前 Markdown 已是 `Ready for Done` / `Done`
   - 而数据库准备回写 `Ready for Development`
   - 默认拒绝回写并输出告警

## 10.2 结构性修复（中高优先级）

4. 拆分数据库状态语义：
   - `core_status`：Markdown 面向人的状态
   - `processing_status`：Dev-QA 流程状态

5. `StatusUpdateAgent` 只读取 `processing_status`，不要再复用 `status` 混存。

6. 对未知状态不要默认写 `Ready for Development`，应改为：
   - 记录错误
   - 跳过该故事的回写
   - 输出告警报告

## 10.3 质量保障（建议补充测试）

7. 为以下场景补单测/集成测试：
   - 故事起始即为 `Ready for Done`
   - 故事起始为 `Done`
   - fallback 解析 `**Status**: Ready for Done`
   - 最终同步禁止终态降级
   - 数据库含非法状态时同步器应 fail-safe

---

## 11. 最终判语

本次现象的根因不是“故事未开发完成”，而是：

> `autoBMAD/epic_automation` 在 Epic 012 这次运行中，把已经完成的故事（012.1 ~ 012.4）错误识别/初始化为 `ready_for_development`，又在最终同步阶段将该错误状态成功回写到了 Markdown，造成状态回退。

因此最终答案是：

- **`012.1` ~ `012.4` 不是因为未开发完成才保持 `Ready for Development`**
- **而是 `autoBMAD/epic_automation` 的状态管理与同步机制存在缺陷，导致状态被错误降级**

---

## 12. 建议的后续动作

建议按以下顺序处理：

1. 先修 `autoBMAD/epic_automation` 的状态同步缺陷
2. 再根据日志与代码实现，把 `012.1` ~ `012.4` 的状态人工恢复为 `Ready for Done`
3. 补上回归测试后，再重新运行 `run-epic` 验证状态不会再次回退

