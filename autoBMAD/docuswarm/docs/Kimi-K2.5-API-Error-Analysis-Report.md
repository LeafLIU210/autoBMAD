# Kimi K2.5 API 404 错误深度分析报告

## 错误概述

**错误时间**: 2026-02-23 05:45:18  
**错误组件**: KimiSessionManager  
**错误类型**: HTTP 404 - Resource Not Found

```
[error] single_prompt_failed agent_file=None component=KimiSessionManager 
error="Error code: 404 - {'error': {'message': 'The requested resource was not found', 'type': 'resource_not_found_error'}}" 
work_dir=D:\GITHUB\pptx-video
```

---

## 一、根本原因分析

### 1.1 核心问题：SDK配置优先级

根据 [Config Overrides](file:///d:/GITHUB/pptx-video/kimi-code-cli/overrides.md) 文档，配置优先级从高到低：

| 优先级 | 来源 | 说明 |
|--------|------|------|
| 1 | **环境变量** | `KIMI_BASE_URL`, `KIMI_API_KEY`, `KIMI_MODEL_NAME` 等 |
| 2 | **CLI flags** | `--config`, `--config-file`, `--model` 等 |
| 3 | **配置文件** | `~/.kimi/config.toml` |

### 1.2 docuswarm 配置问题定位

| 文件 | 配置项 | 错误值 | 正确值 |
|------|--------|--------|--------|
| `session_manager.py:100` | `base_url` 默认值 | `https://api.kimi.com/coding/` | `https://api.kimi.com/coding/` |
| `session_manager.py:112` | `model` 名称 | `kimi-k2.5` | `kimi-for-coding` |
| `session_manager.py:181` | `model` 变量 | `kimi-k2.5` | `kimi-for-coding` |
| `config.py:18` | `API_BASE` | `https://api.moonshot.cn/v1` | `https://api.kimi.com/coding/` |
| `config.py:28-41` | 模型名称 | `kimi-k2.5-*` | `kimi-for-coding` |

**根因**: `base_url` 缺少 `/v1` 后缀，且模型名称与 Kimi Code 平台不匹配。

### 1.3 Kimi Code CLI 数据目录结构

根据 [Data Locations](file:///d:/GITHUB/pptx-video/kimi-code-cli/data-locations.md)：

```
~/.kimi/
├── config.toml          # 主配置文件 (必须正确配置)
├── credentials/         # OAuth 凭证 (/login 后自动生成)
├── sessions/            # 会话数据
└── logs/kimi.log        # 运行日志
```

---

## 二、错误触发流程追踪

### 2.1 调用链

```
docuswarm start -c docs/proposal.md
    │
    ▼
orchestrator.py:215 → session_manager.single_prompt()
    │
    ▼
session_manager.py:400 → create_session(mode="instant", yolo=True)
    │
    ▼
session_manager.py:97-119 → 构建错误的 Config 对象
    │  - base_url: "https://api.kimi.com/coding/" (缺少 /v1)
    │  - model: "kimi-k2.5" (不存在的模型名)
    │
    ▼
kimi_agent_sdk: Session.create() → 使用错误配置
    │
    ▼
HTTP 404 错误返回
```

### 2.2 问题代码定位

#### 问题点 1: session_manager.py L96-119

```python
# 文件: autoBMAD/docuswarm/llm/session_manager.py
# 问题: base_url 默认值缺少 /v1，模型名称错误

if config is None and (api_key or base_url):
    effective_api_key = api_key or os.environ.get("KIMI_API_KEY", "")
    effective_base_url = base_url or os.environ.get(
        "KIMI_BASE_URL", 
        "https://api.kimi.com/coding/"  # ← 错误: 缺少 /v1
    )

    config = Config(
        providers={
            "kimi": {
                "type": "kimi",
                "base_url": effective_base_url,
                "api_key": effective_api_key,
            }
        },
        models={
            "kimi-k2.5": {  # ← 错误: 不存在的模型名
                "provider": "kimi",
                "model": "kimi-k2.5",
                "max_context_size": 128000,
            }
        },
        default_model="kimi-k2.5",
    )
```

#### 问题点 2: session_manager.py L181

```python
# 问题: 硬编码错误的模型名
model = "kimi-k2.5"  # ← 错误: 应为 "kimi-for-coding"
```

#### 问题点 3: config.py L18, L26-41

```python
# 文件: autoBMAD/docuswarm/llm/config.py
# 问题: 使用 Moonshot 中国区 URL，模型名称不正确

API_BASE = "https://api.moonshot.cn/v1"  # ← 与 Kimi Code 平台不一致

MODELS = {
    "instant": {"model": "kimi-k2.5-instant", ...},   # ← 不存在
    "thinking": {"model": "kimi-k2.5-thinking", ...}, # ← 不存在  
    "agent": {"model": "kimi-k2.5-agent", ...},       # ← 不存在
}
```

---

## 三、解决方案（使用 Kimi Code CLI 原生配置）

根据 [Config Files](file:///d:/GITHUB/pptx-video/kimi-code-cli/config-files.md) 和 [Providers](file:///d:/GITHUB/pptx-video/kimi-code-cli/providers.md) 文档。

### 3.2 配置项详解

根据 [Config Files](file:///d:/GITHUB/pptx-video/kimi-code-cli/config-files.md):

| 配置项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `default_model` | string | 是 | 默认模型，必须在 `models` 中定义 |
| `providers.*.type` | string | 是 | Provider 类型: `kimi`, `openai_legacy`, `anthropic` 等 |
| `providers.*.base_url` | string | 是 | API 基础 URL，**必须包含 `/v1`** |
| `providers.*.api_key` | string | 是 | API 密钥 |
| `models.*.provider` | string | 是 | 引用的 provider 名称 |
| `models.*.model` | string | 是 | API 调用时使用的模型标识符 |
| `models.*.max_context_size` | integer | 是 | 最大上下文长度 (tokens) |

### 3.3 环境变量配置

根据 [Environment Variables](file:///d:/GITHUB/pptx-video/kimi-code-cli/env-vars.md)，支持以下环境变量：

| 环境变量 | 说明 |
|----------|------|
| `KIMI_BASE_URL` | 覆盖 provider 的 `base_url` |
| `KIMI_API_KEY` | 覆盖 provider 的 `api_key` |
| `KIMI_MODEL_NAME` | 覆盖模型的 `model` 字段 |
| `KIMI_MODEL_MAX_CONTEXT_SIZE` | 覆盖 `max_context_size` |
| `KIMI_MODEL_CAPABILITIES` | 覆盖模型能力，如 `thinking,image_in` |
| `KIMI_SHARE_DIR` | 自定义共享目录路径 (默认 `~/.kimi`) |

```

### 3.4 修改 session_manager.py

```python
# 文件: autoBMAD/docuswarm/llm/session_manager.py

# 修复点 1: __init__ 方法 (L96-119)
def __init__(
    self,
    work_dir: KaosPath,
    agent_file: Path | None = None,
    config: ConfigParam = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> None:
    self._work_dir = work_dir
    self._agent_file = agent_file

    if config is None and (api_key or base_url):
        effective_api_key = api_key or os.environ.get("KIMI_API_KEY", "")
        # 修复: base_url 必须包含 /v1
        effective_base_url = base_url or os.environ.get(
            "KIMI_BASE_URL", 
            "https://api.kimi.com/coding/"  # ← 修复: 添加 /v1
        )
        # 修复: 使用正确的模型名称
        effective_model = os.environ.get("KIMI_MODEL_NAME", "kimi-for-coding")

        config = Config(
            default_model=effective_model,
            providers={
                effective_model: {  # provider 名称与 model 名称一致
                    "type": "kimi",
                    "base_url": effective_base_url,
                    "api_key": effective_api_key,
                }
            },
            models={
                effective_model: {
                    "provider": effective_model,
                    "model": effective_model,
                    "max_context_size": int(os.environ.get(
                        "KIMI_MODEL_MAX_CONTEXT_SIZE", "262144"
                    )),
                }
            },
        )

    self._config = config

# 修复点 2: create_session 方法 (L181)
async def create_session(self, ...):
    # 修复: 使用环境变量或默认值
    model = os.environ.get("KIMI_MODEL_NAME", "kimi-for-coding")  # ← 修复
```

### 3.5 修改 config.py

```python
# 文件: autoBMAD/docuswarm/llm/config.py

# 修复: 使用 Kimi Code 平台 URL
API_BASE = "https://api.kimi.com/coding/"  # ← 修复

# 修复: 使用正确的模型名称
MODELS = {
    "instant": {
        "model": "kimi-for-coding",  # ← 修复
        "temperature": 0.3,
        "max_tokens": 4096,
    },
    "thinking": {
        "model": "kimi-for-coding",  # ← 修复
        "temperature": 0.5,
        "max_tokens": 8000,
    },
    "agent": {
        "model": "kimi-for-coding",  # ← 修复
        "temperature": 0.7,
        "max_tokens": 32768,
    },
}
```

---

## 四、验证步骤

### 4.1 验证配置文件

```bash
# Windows PowerShell
Get-Content $env:USERPROFILE\.kimi\config.toml

# Linux/macOS
cat ~/.kimi/config.toml
```

### 4.2 验证 Kimi CLI

```bash
# 检查 Kimi CLI 是否安装
kimi --version

# 如果未安装
pip install kimi-cli

# 使用 /login 命令自动配置 (推荐)
kimi
# 在 CLI 中执行 /login 或 /setup
```

> **提示**: 使用 `/login` 命令时，`moonshot_search` 和 `moonshot_fetch` 服务会自动配置。

### 4.3 测试 SDK 基础功能

```python
import asyncio
from kimi_agent_sdk import prompt

async def test():
    async for msg in prompt("Hello", yolo=True):
        print(msg.extract_text(), end="", flush=True)
    print()

asyncio.run(test())
```

### 4.4 重新运行 docuswarm

```bash
python -m autoBMAD.docuswarm start -c docs/proposal.md
```

### 4.5 检查日志

```bash
# 查看 Kimi CLI 日志
# Windows
Get-Content $env:USERPROFILE\.kimi\logs\kimi.log -Tail 50

# Linux/macOS
tail -50 ~/.kimi/logs/kimi.log
```

---

## 五、配置优先级

根据 [Config Overrides](file:///d:/GITHUB/pptx-video/kimi-code-cli/overrides.md)，配置加载优先级：

| 优先级 | 来源 | 示例 |
|--------|------|------|
| 1 (最高) | 环境变量 | `KIMI_API_KEY=sk-xxx  kimi` |
| 2 | CLI flags | `kimi --model kimi-for-coding --yolo` |
| 3 (最低) | 配置文件 | `~/.kimi/config.toml` |

---

## 六、参考资料

| 资源 | 链接 |
|------|------|
| Config Files | [kimi-code-cli/config-files.md](file:///d:/GITHUB/pptx-video/kimi-code-cli/config-files.md) |
| Providers and Models | [kimi-code-cli/providers.md](file:///d:/GITHUB/pptx-video/kimi-code-cli/providers.md) |
| Environment Variables | [kimi-code-cli/env-vars.md](file:///d:/GITHUB/pptx-video/kimi-code-cli/env-vars.md) |
| Config Overrides | [kimi-code-cli/overrides.md](file:///d:/GITHUB/pptx-video/kimi-code-cli/overrides.md) |
| Data Locations | [kimi-code-cli/data-locations.md](file:///d:/GITHUB/pptx-video/kimi-code-cli/data-locations.md) |
| Kimi Agent SDK Quickstart | [kimi-agent-sdk/guides/python/quickstart.md](file:///d:/GITHUB/pptx-video/kimi-agent-sdk/guides/python/quickstart.md) |

---

## 七、附录：关键配置对比

### 7.1 配置值对比

| 配置项 | 错误配置 | 正确配置 |
|--------|----------|----------|
| `base_url` | `https://api.kimi.com/coding/` | `https://api.kimi.com/coding/` |
| `model` | `kimi-k2.5` | `kimi-for-coding` |
| `max_context_size` | `128000` | `262144` |

### 7.2 需修改文件清单

| 文件 | 修改内容 |
|------|----------|
| `~/.kimi/config.toml` | 创建/更新配置文件 |
| `.env` | 更新 `KIMI_BASE_URL`, `KIMI_MODEL_NAME` |
| `autoBMAD/docuswarm/llm/session_manager.py` | L100, L112-118, L181 |
| `autoBMAD/docuswarm/llm/config.py` | L18, L28-41 |

---

**报告生成时间**: 2026-02-23  
**分析工程师**: AI Assistant
