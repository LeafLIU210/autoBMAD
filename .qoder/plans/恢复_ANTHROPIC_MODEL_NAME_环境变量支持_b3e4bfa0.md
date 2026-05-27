# 恢复 ANTHROPIC_MODEL_NAME 环境变量支持

## 背景与决策

- 优先级：`ANTHROPIC_MODEL_NAME`（用户自定义，docuswarm 显式读取并传给 SDK）> `ANTHROPIC_MODEL`（CLI 子进程原生识别，docuswarm 不强制解析）> SDK 默认
- 所有 Agent（independent / evaluator / summary）共用同一个模型名
- 清理 `llm/config.py`、`llm/mode_mapper.py` 的硬编码模型名，统一从 `Config.model_name` 取值
- DeepSeek 后端对未知模型名会自动降级到 `deepseek-v4-flash`，所以文档示例推荐 `deepseek-v4-pro`

## Task 1：`Config` 增加 `model_name` 字段

文件：[autoBMAD/docuswarm/config.py](file:///home/leafliu/autoBMAD/autoBMAD/docuswarm/config.py)

- 新增默认常量：`DEFAULT_MODEL_NAME: str | None = None`（None 表示交给 CLI 子进程自行处理）
- `Config` dataclass 增加 `model_name: str | None = field(default=None)`
- `Config.from_env()` 读取顺序：
  ```python
  model_name = (
      os.environ.get("ANTHROPIC_MODEL_NAME")
      or os.environ.get("ANTHROPIC_MODEL")
      or DEFAULT_MODEL_NAME
  )
  ```
  注意：`ANTHROPIC_MODEL` 参与回退只是为了让 docuswarm 的日志/`ClaudeAgentOptions.model` 能获得非空值；即使这里读到 None，CLI 子进程仍会自行识别它。

## Task 2：`session_manager._create_options` 注入 model 并透传环境变量

文件：[autoBMAD/docuswarm/llm/session_manager.py](file:///home/leafliu/autoBMAD/autoBMAD/docuswarm/llm/session_manager.py#L317-L484)

修改点：

1. **注入 `ClaudeAgentOptions.model`**（仅当 `self._config` 提供且非空）：
   ```python
   model_name = getattr(self._config, "model_name", None) if self._config else None
   if model_name:
       options_dict["model"] = model_name
   ```

2. **扩展 `env_vars` 透传白名单**，让 CLI 子进程继承：
   ```python
   for key in (
       "ANTHROPIC_API_KEY",
       "ANTHROPIC_BASE_URL",
       "ANTHROPIC_MODEL",
       "ANTHROPIC_MODEL_NAME",
       "ANTHROPIC_DEFAULT_OPUS_MODEL",
       "ANTHROPIC_DEFAULT_SONNET_MODEL",
       "ANTHROPIC_DEFAULT_HAIKU_MODEL",
       "CLAUDE_CODE_SUBAGENT_MODEL",
       "CLAUDE_CODE_EFFORT_LEVEL",
       "ANTHROPIC_AUTH_TOKEN",
   ):
       val = os.environ.get(key)
       if val:
           env_vars[key] = val
   ```
   —— 保证 CLI 子进程即便在 docuswarm 没显式传 model 时也能原生识别。

3. 日志 `api_credentials_configured` 事件新增 `model_name` 字段便于排错。

## Task 3：清理 llm/config.py 硬编码

文件：[autoBMAD/docuswarm/llm/config.py](file:///home/leafliu/autoBMAD/autoBMAD/docuswarm/llm/config.py)

- `MODELS` 字典的 `model` 字段改为 `None`（仅保留 temperature / max_tokens 等参数差异）
- `LLMConfig.from_mode(...)` 新增可选参数 `model_name: str | None = None`，优先级：显式参数 > `Config.from_env().model_name` > `None`
- `LLMConfig.__init__` 同步更新，避免 `data.setdefault("model", config["model"])` 时把 `None` 写入当成合法值的场景（若无人使用可直接不 setdefault）

## Task 4：清理 mode_mapper.py 硬编码

文件：[autoBMAD/docuswarm/llm/mode_mapper.py](file:///home/leafliu/autoBMAD/autoBMAD/docuswarm/llm/mode_mapper.py#L37-L53)

- `SDKModeParams.model` 改为 `str | None`
- `MODE_MAP` 三个条目的 `model="kimi"` 改为 `model=None`
- `map_mode()` 不变；调用方若需要拿到真实模型名，应从 `Config.model_name` 取

## Task 5：更新 `.env.example` 与示例 `.env`

文件：`.env.example`

- 在 `ANTHROPIC_BASE_URL` 之后新增一段：
  ```
  # -----------------------------------------------------------------------------
  # OPTIONAL: Model Selection
  # -----------------------------------------------------------------------------
  # Primary model name. docuswarm reads this variable first and passes it
  # explicitly to the Claude Agent SDK.
  # Examples:
  #   deepseek-v4-pro   (DeepSeek via https://api.deepseek.com/anthropic)
  #   kimi-for-coding   (Kimi Code platform)
  # ANTHROPIC_MODEL_NAME=deepseek-v4-pro
  #
  # Fallback: when ANTHROPIC_MODEL_NAME is unset, the Claude Code CLI
  # subprocess will read ANTHROPIC_MODEL natively.
  # ANTHROPIC_MODEL=deepseek-v4-pro
  ```

## Task 6：测试

文件：`tests/`（沿用 `conftest.py` 的 `isolated_state_manager`）

新增 3 个测试点：

1. **`test_config_model_name_priority`**：`monkeypatch` 同时设置 `ANTHROPIC_MODEL_NAME=A`、`ANTHROPIC_MODEL=B`，`Config.from_env().model_name == "A"`
2. **`test_config_model_name_fallback_to_anthropic_model`**：只设 `ANTHROPIC_MODEL=B`，`model_name == "B"`
3. **`test_session_manager_injects_model`**：构造带 `model_name` 的 `Config`，调用 `_create_options`，断言返回的 `ClaudeAgentOptions` 的 `model` 字段等于该值，且 `env` 字典包含 `ANTHROPIC_MODEL_NAME`

## 风险与回退

- **风险 1**：若用户 `.env` 留了旧的 `ANTHROPIC_MODEL_NAME=kimi-for-coding` 但 `BASE_URL` 指向 DeepSeek，DeepSeek 后端会降级到 `deepseek-v4-flash`。→ 在 `.env.example` 中明确示例，并在 `session_manager` 的初始化日志里打印 `model_name` + `base_url` 方便排错。
- **风险 2**：清理 `MODES["*"]["model"]` 硬编码后，若有其他模块通过 `MODELS[mode.value]["model"]` 直接读值会拿到 `None`。已搜索确认当前 `session_manager._create_options` 未使用；若后续发现遗漏，再在 `LLMConfig.__init__` 里加守卫。
- **回退**：所有改动集中在 4 个文件 + 1 个示例 + 1 个测试文件，可通过 `git revert` 单次回滚。

## 验收

```bash
# 1. 能读到自定义变量
ANTHROPIC_MODEL_NAME=deepseek-v4-pro python -c \
  "from autoBMAD.docuswarm.config import load_config; print(load_config().model_name)"
# 输出：deepseek-v4-pro

# 2. 新测试通过
pytest tests/ -k "model_name" -v

# 3. lint / 类型
ruff check autoBMAD/docuswarm/config.py autoBMAD/docuswarm/llm/
basedpyright autoBMAD/docuswarm/config.py autoBMAD/docuswarm/llm/
```
