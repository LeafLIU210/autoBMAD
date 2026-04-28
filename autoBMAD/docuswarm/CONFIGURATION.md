# DocuSwarm 配置说明

## Anthropic API 配置

DocuSwarm 使用 Anthropic API 与 Claude 模型进行交互。配置方式支持两种方式：

### 方式 1：环境变量（推荐）

在项目根目录的 `.env` 文件中配置：

```env
# Anthropic API 配置
ANTHROPIC_API_KEY=your-api-key-here
ANTHROPIC_BASE_URL=https://api.anthropic.com/v1/
```

### 方式 2：系统环境变量（回退方式）

如果 `.env` 文件不存在或未设置，系统会尝试从系统环境变量读取：

```bash
export ANTHROPIC_API_KEY=your-api-key-here
export ANTHROPIC_BASE_URL=https://api.anthropic.com/v1/
```

## 配置优先级

配置加载的优先级顺序（从高到低）：

1. **环境变量** - 从 `.env` 文件或系统环境变量读取
2. **YAML 配置** - 从 `config/docuswarm.yaml` 读取
3. **默认值** - 代码中定义的默认配置

### 示例：base_url 配置优先级

```python
# 优先级 1: 环境变量 ANTHROPIC_BASE_URL
ANTHROPIC_BASE_URL=https://custom-api.example.com/v1

# 优先级 2: YAML 配置
# config/docuswarm.yaml
base_url: https://api.anthropic.com/v1/

# 优先级 3: 默认值
DEFAULT_BASE_URL = "https://api.anthropic.com/v1/"
```

## 自定义 Anthropic API Endpoint

如果需要使用自定义的 Anthropic API endpoint（例如私有部署或镜像地址），只需设置 `ANTHROPIC_BASE_URL` 环境变量：

### 在 .env 文件中

```env
ANTHROPIC_API_KEY=your-api-key
ANTHROPIC_BASE_URL=https://your-custom-endpoint.com/v1
```

### 在命令行中

```bash
# Linux/macOS
export ANTHROPIC_BASE_URL=https://your-custom-endpoint.com/v1
python -m autoBMAD.docuswarm start -c context.md

# Windows PowerShell
$env:ANTHROPIC_BASE_URL="https://your-custom-endpoint.com/v1"
python -m autoBMAD.docuswarm start -c context.md
```

## SDK Config 对象

内部实现中，`SessionManager` 会自动将 `ANTHROPIC_API_KEY` 和 `ANTHROPIC_BASE_URL` 转换为 SDK 配置：

```python
from autoBMAD.docuswarm.config import load_config

config = load_config()
# config.api_key 来自 ANTHROPIC_API_KEY
# config.base_url 来自 ANTHROPIC_BASE_URL 或默认值
```

## 配置验证

启动时，系统会验证必需的配置：

- ✅ `ANTHROPIC_API_KEY` **必需** - 如果未设置会抛出 `ConfigurationError`
- ✅ `ANTHROPIC_BASE_URL` **可选** - 如果未设置使用默认值 `https://api.anthropic.com/v1/`

## 完整配置示例

### .env 文件示例

```env
# =============================================================================
# REQUIRED - Anthropic API 配置
# =============================================================================
ANTHROPIC_API_KEY=your-anthropic-api-key-here
ANTHROPIC_BASE_URL=https://api.anthropic.com/v1/

# =============================================================================
# OPTIONAL - DocuSwarm 配置
# =============================================================================

# 数据库路径 (默认: docuswarm.db)
DOCUSWARM_DB_PATH=docuswarm.db

# 输出目录 (默认: output)
DOCUSWARM_OUTPUT_DIR=output

# 日志级别 (默认: INFO, 选项: DEBUG, INFO, WARNING, ERROR)
DOCUSWARM_LOG_LEVEL=INFO

# 最大迭代次数 (默认: 100)
DOCUSWARM_MAX_ITERATIONS=100

# =============================================================================
# EPIC AUTOMATION - autoBMAD 配置
# =============================================================================

# 源代码目录 (默认: "src", DocuSwarm: "docuswarm")
EPIC_SOURCE_DIR=docuswarm

# 测试目录 (默认: "tests")
EPIC_TEST_DIR=tests
```

## 故障排查

### 错误：ConfigurationError: ANTHROPIC_API_KEY is required

**原因**：未设置 `ANTHROPIC_API_KEY` 环境变量。

**解决方案**：
1. 确保 `.env` 文件存在于项目根目录
2. 检查 `.env` 文件中是否包含 `ANTHROPIC_API_KEY=your-api-key`
3. 验证 API Key 格式正确

### 错误：Connection refused / API endpoint not reachable

**原因**：`ANTHROPIC_BASE_URL` 配置错误或网络问题。

**解决方案**：
1. 检查 `ANTHROPIC_BASE_URL` 是否正确
2. 验证网络连接
3. 尝试使用默认的 `https://api.anthropic.com/v1/`

### 验证配置

使用以下命令验证配置是否正确加载：

```python
from autoBMAD.docuswarm.config import load_config

config = load_config()
print(f"API Key: {config.api_key[:10]}...")  # 只显示前10个字符
print(f"Base URL: {config.base_url}")
print(f"DB Path: {config.db_path}")
print(f"Output Dir: {config.output_dir}")
```

## 相关文档

- [Anthropic API 文档](https://docs.anthropic.com/)
- [README.md - 配置说明](./README.md#配置说明)
