# PyQt Windows应用程序模板 - 使用指南

## 快速开始

### 1. 激活虚拟环境
```bash
cd /d/GITHUB/pytQt_template
/d/GITHUB/pytQt_template/venv/Scripts/activate
```

### 2. 运行应用程序
```bash
# 方法1: 使用快速启动脚本
python run_app.py

# 方法2: 直接运行主程序
python src/main.py
```

### 3. 验证安装
```bash
# 运行测试脚本
python test_pyside6_app.py
```

## 项目特性

### 技术栈
- **PySide6**: 现代Qt框架 (v6.10.1)
- **Python**: 3.14.2
- **BMAD**: AI驱动的敏捷开发方法论
- **代码质量工具**: basedpyright, ruff

### 应用程序功能
- ✅ 现代化GUI界面
- ✅ 响应式布局设计
- ✅ 事件处理系统
- ✅ 错误处理机制
- ✅ 用户友好的交互设计

## 文件结构

```
src/
├── main.py                    # 应用程序入口点
└── my_qt_app/
    ├── __init__.py            # 包初始化文件
    └── widgets/
        └── main_window.py     # 主窗口实现

run_app.py                     # 快速启动脚本
test_pyside6_app.py           # 测试验证脚本
PYQT_APP_GUIDE.md             # 详细修复报告
```

## 使用说明

### 启动应用程序
```bash
python run_app.py
```

### 运行测试
```bash
python test_pyside6_app.py
```

### 开发模式
```bash
python src/main.py
```

## 常见问题

### Q: 如何激活虚拟环境？
A: 使用以下命令：
```bash
/d/GITHUB/pytQt_template/venv/Scripts/activate
```

### Q: 如何安装依赖？
A: 运行：
```bash
/d/GITHUB/pytQt_template/venv/Scripts/pip install -r requirements.txt
```

### Q: 如何验证安装？
A: 运行测试脚本：
```bash
python test_pyside6_app.py
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 支持

如有问题，请查看 `PYQT_APP_GUIDE.md` 获取详细信息。
