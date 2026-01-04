# 奥卡姆剃刀原则 - 4脚本测试修复工作流

基于奥卡姆剃刀原则（"如无必要，勿增实体"）改造的简化测试修复工作流。

## 核心理念

- **最小假设**: 不需要额外的状态管理或持久化
- **最简方案**: 4个脚本，线性依赖，直接委托
- **无冗余**: 复用现有代码，避免重复逻辑
- **直接解决**: 简单直接的实现，无过度抽象

## 4个脚本说明

### 脚本1: `scan_test_files.py` (复用)
**功能**: 扫描tests目录，生成测试文件列表

```bash
python scan_test_files.py
```

**输入**: 无
**输出**: `fileslist/test_files_list_{timestamp}.json`

---

### 脚本2: `run_tests.py` (已优化)
**功能**: 执行pytest测试，收集FAIL/ERROR到汇总JSON

```bash
python run_tests.py
```

**输入**: `fileslist/test_files_list_*.json`
**输出**: `summaries/test_results_summary_{timestamp}.json`

**优化点**:
- 简化实时保存逻辑（避免频繁I/O）
- 保持统一的JSON结构
- 清晰的错误和失败信息收集

---

### 脚本3: `debug_test_with_pytest.py` (新增)
**功能**: 使用debugpy调试失败测试，更新汇总JSON

```bash
python debug_test_with_pytest.py
```

**输入**: `summaries/test_results_summary_*.json`
**输出**: 更新的汇总JSON（添加debug_info字段）

**特点**:
- 可选步骤（只有需要深入调试时才执行）
- 集成debugpy调试会话
- 自动收集调试信息并更新JSON

---

### 脚本4: `generate_prompt_and_fix.py` (新增)
**功能**: 生成Claude提示词，调用修复

```bash
python generate_prompt_and_fix.py
```

**输入**: 汇总JSON（可能包含debug_info）
**输出**: `prompts/fix_prompt_{timestamp}.md` + claude调用

**特点**:
- 自动生成结构化提示词
- 包含错误信息、失败信息和调试信息
- 直接调用 `claude --dangerously-skip-permissions`

## 数据流转

```
脚本1: scan_test_files.py
    ↓ fileslist/test_files_list_*.json
脚本2: run_tests.py
    ↓ summaries/test_results_summary_*.json
脚本3: debug_test_with_pytest.py (可选)
    ↓ summaries/test_results_summary_*.json (updated)
脚本4: generate_prompt_and_fix.py
    ↓ prompts/fix_prompt_*.md + claude调用
```

## 统一JSON结构

所有数据通过一个统一的汇总JSON流转：

```json
{
  "scan_timestamp": "2026-01-04T13:34:05",
  "test_start_time": "2026-01-04T13:34:17",
  "timestamp": "20260104_133417",
  "total_files": 0,
  "files_with_errors": [
    {
      "relative_path": "test_xxx.py",
      "status": "completed",
      "result": "error",
      "errors": [...],
      "failures": [...],
      "execution_time": 0.21,
      "timestamp": "2026-01-04T13:34:17",
      "timeout": false,
      "debug_info": {  // 脚本3添加
        "debug_session_id": "ds_xxx",
        "debug_port": 5678,
        "breakpoints": [],
        "debug_log": "...",
        "start_time": "2026-01-04T13:35:00",
        "end_time": "2026-01-04T13:36:00",
        "success": true
      }
    }
  ],
  "summary": {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": 0,
    "timeouts": 0
  },
  "prompt_generated": false,  // 脚本4添加
  "prompt_file": "prompts/fix_prompt_xxx.md",
  "prompt_timestamp": "2026-01-04T13:37:00"
}
```

## 执行流程

### 完整流程（包含调试）
```bash
cd fixtest-workflow

# 步骤1：扫描测试文件
python scan_test_files.py

# 步骤2：执行测试（收集FAIL/ERROR）
python run_tests.py

# 步骤3：调试失败文件（可选）
python debug_test_with_pytest.py

# 步骤4：生成提示词并调用Claude
python generate_prompt_and_fix.py
```

### 快速流程（跳过调试）
```bash
cd fixtest-workflow

python scan_test_files.py
python run_tests.py
python generate_prompt_and_fix.py
```

## 消除的冗余

| 原有方案 | 奥卡姆方案 |
|---------|-----------|
| 多JSON文件分散 | 统一汇总JSON作为唯一数据源 |
| 重复的pytest执行逻辑 | 复用现有函数 |
| 调试功能缺失 | 脚本3集成debugpy |
| 提示词生成硬编码 | 统一提示词生成器 |
| 双工作流并存 | 线性4脚本流程 |

## 目录结构

```
fixtest-workflow/
├── scan_test_files.py              # 脚本1：扫描测试文件
├── run_tests.py                    # 脚本2：执行测试
├── debug_test_with_pytest.py       # 脚本3：调试失败测试 (新增)
├── generate_prompt_and_fix.py      # 脚本4：生成提示词并修复 (新增)
├── fileslist/                      # 测试文件列表
├── summaries/                      # 测试结果汇总JSON
└── prompts/                        # 提示词文件
```

## 奥卡姆剃刀原则落实

✅ **最小假设**: 不需要额外的状态管理或持久化
✅ **最简方案**: 4个脚本，线性依赖，直接委托
✅ **无冗余**: 复用现有代码，避免重复逻辑
✅ **直接解决**: 简单直接的实现，无过度抽象

## 使用示例

### 场景1: 正常测试修复
```bash
# 扫描并执行测试
python scan_test_files.py
python run_tests.py

# 发现3个失败文件，直接生成提示词并修复
python generate_prompt_and_fix.py
```

### 场景2: 需要深入调试
```bash
# 扫描并执行测试
python scan_test_files.py
python run_tests.py

# 发现复杂错误，使用debugpy调试
python debug_test_with_pytest.py

# 生成包含调试信息的提示词并修复
python generate_prompt_and_fix.py
```

## 优势

1. **简单**: 4个独立脚本，职责单一
2. **高效**: 线性流程，无循环依赖
3. **灵活**: 可选调试步骤，按需使用
4. **可维护**: 最小化代码，消除冗余
5. **可扩展**: 基于统一JSON结构，易于扩展

## 注意事项

1. 确保已安装debugpy（脚本3需要）:
   ```bash
   pip install debugpy
   ```

2. 确保已安装pytest（脚本2需要）:
   ```bash
   pip install pytest
   ```

3. 确保已安装claude CLI工具（脚本4需要）:
   - 按照Claude官方文档安装
   - 确保添加到PATH中

4. 项目需要有tests目录和test_*.py文件

## 作者

基于奥卡姆剃刀原则设计，遵循"如无必要，勿增实体"的哲学思想。
