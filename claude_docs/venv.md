# Python 虚拟环境说明 - DocuSwarm

## 概述
DocuSwarm 使用 Python 虚拟环境来隔离项目依赖，确保开发环境的一致性。

## 虚拟环境信息
- **Python 版本**: 3.12+
- **环境路径**: `./venv/` (推荐)
- **项目**: DocuSwarm Multi-Agent Orchestration System
- **核心框架**: LangGraph, LangChain, claude-agent-sdk, Kimi K2.5

## 使用方法

### 创建虚拟环境

首次设置项目时创建虚拟环境：

```bash
# 使用 venv (推荐)
python -m venv venv

# 或使用 venv
python -m venv venv
```

### 激活虚拟环境

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
# 或
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
# 或
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source venv/bin/activate
# 或
source venv/bin/activate
```

激活成功后，命令行提示符会显示 `(venv)` 或 `(venv)` 前缀。

### 安装 DocuSwarm 依赖

激活虚拟环境后，安装项目依赖：

```bash
# 升级 pip
pip install --upgrade pip

# 安装生产依赖
pip install -r requirements.txt

# 安装开发依赖（包含测试工具）
pip install -r requirements-dev.txt
```

**核心依赖包括**:
- `langgraph>=0.2.0` - 多代理工作流状态机
- `langchain>=0.3.0` - LLM 集成框架
- `claude-agent-sdk>=0.1.0` - Claude SDK（通过 Kimi Code API）
- `pyyaml>=6.0.0` - 配置文件管理
- `pydantic>=2.0.0` - 数据验证
- `python-dotenv>=1.0.0` - 环境变量管理
- `loguru>=0.7.0` - 日志系统

### 验证安装

```bash
# 检查 Python 版本
python --version

# 检查已安装的包
pip list

# 验证核心依赖
python -c "import langgraph; print('LangGraph:', langgraph.__version__)"
python -c "import langchain; print('LangChain:', langchain.__version__)"
```

### 更新依赖列表

```bash
# 导出当前环境的依赖
pip freeze > requirements-frozen.txt

# 不建议直接覆盖 requirements.txt
# 应该手动维护 requirements.txt 和 requirements-dev.txt
```

### 停用虚拟环境
```bash
deactivate
```

## 虚拟环境目录结构

```
venv/  (或 venv/)
├── Include/          # C 语言头文件
├── Lib/              # 标准库和第三方包
│   └── site-packages/
│       ├── langgraph/
│       ├── langchain/
│       ├── pydantic/
│       └── ...
├── Scripts/          # 可执行脚本 (Windows)
│   ├── activate.bat
│   ├── Activate.ps1
│   ├── python.exe
│   └── pip.exe
├── bin/              # 可执行脚本 (Linux/macOS)
│   ├── activate
│   ├── python
│   └── pip
└── pyvenv.cfg        # 虚拟环境配置文件
```

## 注意事项

### ⚠️ 重要提醒

1. **每次运行 Python 程序前必须激活虚拟环境**
   ```bash
   # 确认已激活（看到前缀）
   (venv) PS D:\GITHUB\DocuSwarm>
   ```

2. **不要提交虚拟环境到 Git**
   - `.gitignore` 已配置忽略 `venv/`, `venv/`, `env/` 等
   - 只提交 `requirements.txt` 和 `requirements-dev.txt`

3. **使用 requirements 文件管理依赖**
   - 不要手动修改已安装的包
   - 新增依赖应更新到 requirements 文件

4. **删除虚拟环境**
   ```bash
   # Linux/macOS
   rm -rf venv
   
   # Windows PowerShell
   Remove-Item -Recurse -Force venv
   
   # Windows CMD
   rmdir /s /q venv
   ```

5. **API 配置**
   ```bash
   # 创建 .env 文件（不会被提交）
   echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
   # Optional: for Kimi Code API
   echo "ANTHROPIC_BASE_URL=https://api.kimi.com/coding/" >> .env
   ```

## 常见问题

### Q: 激活失败怎么办？

**Windows PowerShell 执行策略错误**:
```powershell
# 临时允许脚本执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 然后激活
venv\Scripts\Activate.ps1
```

**Linux/macOS 权限问题**:
```bash
chmod +x venv/bin/activate
source venv/bin/activate
```

### Q: 如何在 IDE 中使用虚拟环境？

**VS Code**:
1. 打开命令面板 (Ctrl+Shift+P)
2. 输入 "Python: Select Interpreter"
3. 选择 `venv\Scripts\python.exe` (Windows) 或 `venv/bin/python` (Linux/macOS)

**PyCharm**:
1. File → Settings → Project → Python Interpreter
2. 点击齿轮图标 → Add
3. 选择 "Existing environment"
4. 选择虚拟环境中的 python 可执行文件

### Q: 如何重新创建虚拟环境？

```bash
# 1. 停用当前环境
deactivate

# 2. 删除虚拟环境
rm -rf venv  # Linux/macOS
Remove-Item -Recurse -Force venv  # Windows PowerShell

# 3. 重新创建
python -m venv venv

# 4. 激活并安装依赖
source venv/bin/activate  # Linux/macOS
venv\Scripts\Activate.ps1  # Windows PowerShell

pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Q: 为什么使用 venv 而不是 venv？

A: `venv` 是推荐的命名方式：
- 以 `.` 开头的目录在 Linux/macOS 中默认隐藏
- 与 Python 官方文档推荐一致
- 更清晰地标识为项目配置目录
- 两者功能完全相同，本项目都支持

### Q: DocuSwarm 特定依赖问题？

**LangGraph 安装失败**:
```bash
pip install --upgrade pip setuptools wheel
pip install langgraph
```

**API 测试**:
```python
import os
from autoBMAD.docuswarm.config import load_config

# 测试配置加载
config = load_config()
print(f"API Key: {config.api_key[:10]}...")
print(f"Base URL: {config.base_url}")
```

## 快速参考

```bash
# 创建环境
python -m venv venv

# 激活环境 (Windows)
venv\Scripts\Activate.ps1

# 激活环境 (Linux/macOS)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 配置 API
echo "ANTHROPIC_API_KEY=your_key" > .env

# 验证安装
python -c "import langgraph; print('OK')"

# 运行程序
python -m autoBMAD.docuswarm --help

# 停用环境
deactivate
```