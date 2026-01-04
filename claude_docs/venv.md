# Python 虚拟环境说明

## 概述
本项目使用 Python 3.12.10 创建了独立的虚拟环境，用于隔离项目依赖。

## 虚拟环境信息
- **Python 版本**: 3.12.10
- **环境路径**: `./venv/`
- **创建日期**: 2026-01-04

## 使用方法

### 激活虚拟环境

**Windows:**
```cmd
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/Scripts/activate
```

激活成功后，命令行提示符会显示 `(venv)` 前缀。

### 安装依赖包

激活虚拟环境后，使用 pip 安装所需的包：
```bash
pip install package_name
```

### 导出依赖列表
```bash
pip freeze > requirements.txt
```

### 从依赖列表安装
```bash
pip install -r requirements.txt
```

### 停用虚拟环境
```bash
deactivate
```

## 目录结构
```
venv/
├── Include/          # C 语言头文件
├── Lib/              # 标准库和第三方包
├── Scripts/          # 可执行脚本 (Windows)
├── bin/              # 可执行脚本 (Linux/macOS)
└── pyvenv.cfg        # 虚拟环境配置文件
```

## 注意事项
1. 每次工作前记得激活虚拟环境
2. 提交代码时，不要包含 `venv/` 目录
3. 使用 `requirements.txt` 管理项目依赖
4. 删除虚拟环境：`rm -rf venv/` (Linux/macOS) 或 `rmdir /s venv` (Windows)

## 常见问题

### Q: 激活失败怎么办？
A: 确保使用的是正确的命令，Windows 使用 `.bat` 文件，Linux/macOS 使用 `.sh` 文件。

### Q: 如何在 IDE 中使用虚拟环境？
A: 在 IDE 设置中将 Python 解释器路径指向 `venv/bin/python` (Linux/macOS) 或 `venv\Scripts\python.exe` (Windows)。

### Q: 如何重新创建虚拟环境？
A: 先删除现有目录，然后重新运行 `python -m venv venv`。