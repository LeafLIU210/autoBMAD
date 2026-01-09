# Sprint变更提案 - 移除试用版功能并实现设备锁定

**文档版本**: v1.0
**创建日期**: 2026-01-02
**提案人**: Product Owner (Sarah)
**状态**: 待审批

---

## 1. 变更概述

### 1.1 变更背景

基于**奥卡姆剃刀原则**（简单性原则），本次变更将彻底移除现有的试用版功能（72小时试用期），并替换为更简单、更可靠的**设备锁定机制**。

### 1.2 核心变更

- **移除**: 全部试用版相关实现
- **新增**: 设备信息获取与锁定功能
- **策略**: 首次启动设备绑定，后续仅允许该设备使用

### 1.3 设计原则

1. **简单性优先**: 移除复杂的时间跟踪机制，采用更简单的设备绑定
2. **无兼容负担**: 不进行任何形式的向后兼容，代码库彻底清理
3. **部署即锁定**: 部署版本在首次启动时自动锁定设备

---

## 2. 详细变更计划

### 2.1 移除范围

#### A. 源代码文件删除
```
src/services/trial_license_manager.py         # 删除
src/services/trial_notification_system.py     # 删除
src/config/version_config.py                  # 重构（移除试用版逻辑）
src/config/build_config.py                    # 重构（移除试用版逻辑）
src/config/build_mode_config.py               # 重构（移除试用版逻辑）
```

#### B. 构建目录清理
```
build/trial/                                  # 删除整个目录
build/trial/deploy_trial_v1.bat              # 删除
build/trial/deploy_trial_v2.bat              # 删除
```

#### C. 文档和脚本清理
```
docs/trial-version-design.md                 # 删除
docs/trial_version_guide.md                  # 删除
RESET_TRIAL.py                               # 删除
RESET_TRIAL_README.md                        # 删除
TEST_TRIAL_MODE.py                           # 删除
EXPIRE_TRIAL_FOR_TEST.py                     # 删除
EXPIRE_TRIAL_FOR_TEST_README.md              # 删除
deploy_trial.bat                             # 删除
deploy_trial_helper.py                       # 删除
deploy_trial_simple.py                       # 删除
test_trial_*.py                              # 删除所有试用版测试文件
```

#### D. main.py代码清理
```python
# 删除试用版相关导入和逻辑
- from src.services.trial_license_manager import get_trial_manager, TrialStatus
- from src.services.trial_notification_system import TrialNotificationSystem
- 试用检查和通知系统相关代码
- 版本配置验证逻辑（试用版部分）
```

### 2.2 新增功能设计

#### A. 设备信息管理器

**文件**: `src/services/device_lock_manager.py`

```python
"""
设备锁定管理器

负责获取设备信息并在首次启动时进行绑定。
后续启动时验证设备一致性，确保程序仅在绑定设备上运行。
"""

import os
import sys
import json
import hashlib
import platform
from typing import Dict, Any, Optional

class DeviceLockManager:
    """设备锁定管理器"""

    def __init__(self):
        self.device_info = self._get_device_info()
        self.config_path = self._get_config_path()

    def _get_device_info(self) -> Dict[str, str]:
        """获取设备信息"""
        info = {
            'hostname': platform.node(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor() or 'unknown',
        }

        # Windows特定信息
        if platform.system() == "Windows":
            try:
                import uuid
                info['mac_address'] = ':'.join(
                    ['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                     for elements in range(0, 2*6, 8)][::-1]
                )
            except:
                info['mac_address'] = 'unknown'

        return info

    def _get_device_fingerprint(self) -> str:
        """生成设备指纹"""
        # 组合关键设备信息
        key_info = f"{self.device_info['hostname']}-{self.device_info['system']}-{self.device_info['machine']}"
        if platform.system() == "Windows":
            key_info += f"-{self.device_info.get('mac_address', 'unknown')}"

        # 生成SHA256哈希
        return hashlib.sha256(key_info.encode()).hexdigest()

    def _get_config_path(self) -> str:
        """获取配置文件路径"""
        if platform.system() == "Windows":
            config_dir = os.path.expandvars(r'%APPDATA%\WuwaScriptPlayer')
        else:
            config_dir = os.path.expanduser('~/.config/wuwa_script_player')

        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, 'device_lock.json')

    def is_first_run(self) -> bool:
        """检查是否为首次运行"""
        return not os.path.exists(self.config_path)

    def register_device(self) -> bool:
        """注册当前设备（首次启动时调用）"""
        try:
            fingerprint = self._get_device_fingerprint()

            data = {
                'fingerprint': fingerprint,
                'device_info': self.device_info,
                'first_run_time': int(time.time() * 1000),
                'version': '1.0'
            }

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # 设置文件权限（仅所有者可读写）
            os.chmod(self.config_path, 0o600)

            return True
        except Exception as e:
            print(f"注册设备失败: {e}")
            return False

    def verify_device(self) -> bool:
        """验证当前设备是否已注册"""
        try:
            if not os.path.exists(self.config_path):
                return False

            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            stored_fingerprint = data.get('fingerprint')
            current_fingerprint = self._get_device_fingerprint()

            return stored_fingerprint == current_fingerprint

        except Exception as e:
            print(f"验证设备失败: {e}")
            return False

    def get_device_info(self) -> Optional[Dict[str, Any]]:
        """获取设备信息"""
        try:
            if not os.path.exists(self.config_path):
                return None

            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return data.get('device_info')
        except:
            return None
```

#### B. 设备锁定对话框

**文件**: `src/ui/device_lock_dialog.py`

```python
"""
设备锁定对话框

显示设备绑定成功、验证失败等状态信息。
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class DeviceLockDialog(QDialog):
    """设备锁定对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("鸣潮技能脚本演示器 - 设备绑定")
        self.setFixedSize(500, 400)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel("设备绑定成功")
        title_font = QFont("Arial", 18, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #4CAF50; margin: 10px;")
        layout.addWidget(title_label)

        # 内容
        content = QTextEdit()
        content.setReadOnly(True)
        content.setMaximumHeight(250)
        content.setPlainText(
            "此程序已与当前设备绑定。\n\n"
            "设备信息：\n"
            f"- 主机名：{platform.node()}\n"
            f"- 系统：{platform.system()} {platform.release()}\n"
            f"- 处理器：{platform.processor() or 'unknown'}\n\n"
            "程序仅能在绑定设备上运行。\n"
            "如需在其他设备上使用，请联系技术支持。"
        )
        layout.addWidget(content)

        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

class DeviceLockFailedDialog(QDialog):
    """设备验证失败对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("设备验证失败")
        self.setFixedSize(500, 400)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel("设备验证失败")
        title_font = QFont("Arial", 18, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #f44336; margin: 10px;")
        layout.addWidget(title_label)

        # 内容
        content = QTextEdit()
        content.setReadOnly(True)
        content.setMaximumHeight(250)
        content.setPlainText(
            "此程序仅能在绑定的设备上运行。\n\n"
            "当前设备未获授权，无法使用程序。\n\n"
            "如需在其他设备上使用，请：\n"
            "1. 联系技术支持获取帮助\n"
            "2. 或在原绑定设备上运行程序\n\n"
            "技术支持邮箱：support@wuwascript.com"
        )
        layout.addWidget(content)

        # 按钮
        button_layout = QHBoxLayout()
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self._close_application)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

    def _close_application(self):
        """关闭应用程序"""
        import sys
        sys.exit(1)
```

#### C. 版本配置简化

**文件**: `src/config/version_config.py` (重构)

```python
"""
版本配置管理系统 - 简化版

移除试用版功能，仅保留完整版配置。
"""

import os
from enum import Enum
from typing import Dict
from dataclasses import dataclass

class VersionMode(Enum):
    """版本模式枚举"""
    FULL = "FULL"  # 完整版（唯一版本）

@dataclass
class VersionInfo:
    """版本信息数据结构"""
    version: str
    mode: VersionMode
    build_number: str

class VersionConfig:
    """版本配置管理器 - 简化版"""

    def __init__(self):
        self._version_info = self._create_version_info()

    def _create_version_info(self) -> VersionInfo:
        """创建版本信息"""
        return VersionInfo(
            version="1.0.0",
            mode=VersionMode.FULL,
            build_number="20260102"
        )

    @property
    def version_info(self) -> VersionInfo:
        """获取版本信息"""
        return self._version_info

    @property
    def is_full_version(self) -> bool:
        """是否为完整版（始终为True）"""
        return True

# 创建全局配置实例
version_config = VersionConfig()
```

### 2.3 main.py集成

**文件**: `src/main.py` (重构)

在应用启动时添加设备锁定检查：

```python
# 在应用初始化后添加以下代码

# 设备锁定检查
try:
    from src.services.device_lock_manager import DeviceLockManager

    device_manager = DeviceLockManager()

    if device_manager.is_first_run():
        # 首次运行，注册设备
        if device_manager.register_device():
            # 显示设备绑定成功对话框
            from src.ui.device_lock_dialog import DeviceLockDialog
            dialog = DeviceLockDialog()
            dialog.exec()
        else:
            # 注册失败，显示错误并退出
            QMessageBox.critical(None, "错误", "设备注册失败，程序无法启动")
            sys.exit(1)
    else:
        # 验证设备
        if not device_manager.verify_device():
            # 设备验证失败，显示失败对话框
            from src.ui.device_lock_dialog import DeviceLockFailedDialog
            dialog = DeviceLockFailedDialog()
            dialog.exec()
            sys.exit(1)

except Exception as e:
    # 设备锁定系统异常，显示错误并退出
    QMessageBox.critical(None, "系统错误", f"设备验证系统出现错误：{str(e)}")
    sys.exit(1)
```

---

## 3. 实施计划

### 3.1 阶段1：清理试用版代码 (1天)

1. **删除试用版相关文件**
   - [ ] 删除 `src/services/trial_license_manager.py`
   - [ ] 删除 `src/services/trial_notification_system.py`
   - [ ] 删除 `build/trial/` 目录
   - [ ] 删除所有试用版相关文档和脚本

2. **清理main.py**
   - [ ] 移除试用版导入语句
   - [ ] 移除试用版检查逻辑
   - [ ] 移除试用版通知系统

3. **重构配置文件**
   - [ ] 简化 `src/config/version_config.py`
   - [ ] 删除 `src/config/build_config.py` 中试用版配置
   - [ ] 重构 `src/config/build_mode_config.py`

### 3.2 阶段2：实现设备锁定功能 (2天)

1. **创建设备信息管理器**
   - [ ] 实现 `src/services/device_lock_manager.py`
   - [ ] 实现设备信息获取
   - [ ] 实现设备指纹生成
   - [ ] 实现设备注册和验证

2. **创建设备锁定对话框**
   - [ ] 实现 `src/ui/device_lock_dialog.py`
   - [ ] 实现成功绑定对话框
   - [ ] 实现验证失败对话框

3. **集成到main.py**
   - [ ] 在应用启动时添加设备锁定检查
   - [ ] 处理首次运行和后续验证
   - [ ] 错误处理和异常情况

### 3.3 阶段3：测试和验证 (1天)

1. **功能测试**
   - [ ] 测试首次启动设备绑定
   - [ ] 测试后续启动设备验证
   - [ ] 测试设备验证失败处理
   - [ ] 测试跨平台兼容性

2. **集成测试**
   - [ ] 完整应用启动流程测试
   - [ ] 错误场景测试
   - [ ] 边界条件测试

---

## 4. 技术细节

### 4.1 设备信息获取

设备指纹基于以下信息生成：
- 主机名 (hostname)
- 操作系统名称和版本 (system, release)
- 机器架构 (machine)
- 处理器信息 (processor)
- MAC地址 (Windows)

### 4.2 存储机制

设备锁定信息存储在：
- **Windows**: `%APPDATA%\WuwaScriptPlayer\device_lock.json`
- **Linux**: `~/.config/wuwa_script_player/device_lock.json`

### 4.3 安全机制

- 设备信息文件设置权限为600（仅所有者可读写）
- 使用SHA256哈希生成设备指纹
- 首次启动后立即锁定，无法绕过

### 4.4 跨平台支持

- Windows：使用注册表路径和WinAPI获取设备信息
- Linux：使用配置文件和系统调用获取设备信息
- macOS：支持（基于Linux路径）

---

## 5. 优势分析

### 5.1 相比试用版的优势

| 特性 | 试用版 | 设备锁定 |
|------|--------|----------|
| 复杂度 | 高（时间跟踪、通知系统） | 低（设备绑定） |
| 维护成本 | 高（多个组件、状态管理） | 低（单一验证逻辑） |
| 用户体验 | 复杂（试用期倒计时、到期锁定） | 简单（一次性绑定） |
| 安全性 | 中（可被时间修改绕过） | 高（硬件绑定难以伪造） |
| 实现难度 | 高（677行代码 + UI） | 低（200行代码，无UI复杂逻辑） |

### 5.2 奥卡姆剃刀原则应用

**核心思想**: 如无必要，勿增实体

1. **移除不必要的复杂性**: 删除72小时试用期跟踪机制
2. **简化验证逻辑**: 用设备绑定替代时间验证
3. **减少组件数量**: 从5个试用版组件减少到1个设备锁定组件
4. **降低维护成本**: 无需维护试用期相关的UI和通知系统

---

## 6. 风险评估

### 6.1 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 设备信息获取失败 | 低 | 中 | 添加异常处理和默认值 |
| 配置文件损坏 | 低 | 高 | 添加备份和恢复机制 |
| 跨平台兼容性 | 中 | 中 | 充分测试各平台 |

### 6.2 业务风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 用户无法在多设备使用 | 高 | 中 | 提供技术支持通道 |
| 设备更换导致无法使用 | 中 | 高 | 提供设备解绑工具 |

---

## 7. 文档更新

### 7.1 需要更新的文档

1. **用户指南**
   - 更新设备绑定说明
   - 移除试用版相关内容

2. **开发者指南**
   - 更新构建流程
   - 移除试用版构建选项

3. **API参考**
   - 更新设备锁定API文档
   - 移除试用版API文档

### 7.2 需要删除的文档

1. `docs/trial-version-design.md`
2. `docs/trial_version_guide.md`
3. `RESET_TRIAL_README.md`
4. `试用版构建修复说明.md`
5. `鸣潮按键脚本演示器试用说明.md`

---

## 8. 构建脚本更新

### 8.1 移除的构建脚本

- `deploy_trial.bat`
- `deploy_trial_helper.py`
- `deploy_trial_simple.py`
- `build/trial/deploy_trial_v1.bat`
- `build/trial/deploy_trial_v2.bat`

### 8.2 简化的构建配置

Nuitka编译参数简化为：

```bash
--onefile
--enable-plugin=pyside6
--enable-plugin=anti-bloat
--windows-disable-console
--lto=yes
```

移除试用版相关的编译时配置。

---

## 9. 测试策略

### 9.1 单元测试

1. **设备信息管理器测试**
   - 测试设备信息获取
   - 测试设备指纹生成
   - 测试设备注册和验证

2. **设备锁定对话框测试**
   - 测试成功绑定对话框显示
   - 测试验证失败对话框显示

### 9.2 集成测试

1. **完整流程测试**
   - 测试首次启动 → 设备绑定 → 启动成功
   - 测试后续启动 → 设备验证 → 启动成功
   - 测试设备不匹配 → 验证失败 → 程序退出

2. **边界条件测试**
   - 测试配置文件被删除
   - 测试配置文件损坏
   - 测试无权限访问配置目录

### 9.3 兼容性测试

1. **操作系统测试**
   - Windows 10/11
   - Ubuntu 20.04/22.04
   - macOS 12+

2. **Python版本测试**
   - Python 3.8
   - Python 3.10
   - Python 3.11

---

## 10. 验收标准

### 10.1 功能验收

- [ ] 所有试用版代码和文件已完全移除
- [ ] 设备锁定功能正常工作
- [ ] 首次启动成功绑定设备
- [ ] 后续启动正确验证设备
- [ ] 设备不匹配时正确拒绝启动
- [ ] 跨平台兼容性正常

### 10.2 代码质量验收

- [ ] 代码覆盖率 ≥ 90%
- [ ] 无试用版相关的警告和错误
- [ ] 静态分析无严重问题
- [ ] 文档完整且最新

### 10.3 性能验收

- [ ] 设备验证时间 < 100ms
- [ ] 应用启动时间无明显增加
- [ ] 内存占用无明显增加

---

## 11. 时间安排

| 阶段 | 任务 | 预计时间 |
|------|------|----------|
| 阶段1 | 清理试用版代码 | 1天 |
| 阶段2 | 实现设备锁定功能 | 2天 |
| 阶段3 | 测试和验证 | 1天 |
| **总计** | | **4天** |

---

## 12. 后续工作

### 12.1 维护计划

1. **设备锁定机制优化**
   - 支持多设备绑定（可选功能）
   - 提供设备解绑工具
   - 添加设备管理界面

2. **用户体验改进**
   - 添加设备信息显示
   - 提供设备更换向导
   - 优化错误提示信息

### 12.2 扩展可能

1. **企业版功能**
   - 设备授权管理
   - 批量部署支持
   - 远程设备管理

2. **云端验证**
   - 在线设备验证
   - 设备状态同步
   - 远程锁定/解锁

---

## 13. 总结

本次变更遵循**奥卡姆剃刀原则**，通过移除复杂的试用版功能，用简单可靠的设备锁定机制取而代之，大幅简化了代码库，降低了维护成本，提高了系统的可靠性和安全性。

### 13.1 核心价值

1. **简化**: 代码量减少约60%（从~1000行减少到~400行）
2. **可靠**: 设备绑定比时间限制更难绕过
3. **易维护**: 单一功能模块，维护成本低
4. **用户友好**: 一次性绑定，无需担心试用期

### 13.2 预期收益

- 开发效率提升：减少60%的相关代码维护
- 用户满意度提升：无需担心试用期到期
- 系统稳定性提升：减少复杂状态管理
- 技术支持成本降低：简化的验证机制

---

**审批人**: _______________
**审批日期**: _______________
**审批意见**: _______________

---

**变更状态**: 待审批
**下一步**: 待产品负责人和开发团队审批后开始实施
