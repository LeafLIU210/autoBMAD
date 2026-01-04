# 核心开发原则详细说明

**版本**: 1.0
**最后更新**: 2026-01-04

---

## 目录

1. [四大黄金法则](#1-四大黄金法则)
2. [原则之间的关系](#2-原则之间的关系)
3. [实践示例](#3-实践示例)
4. [在项目中的应用](#4-在项目中的应用)

---

## 1. 四大黄金法则

### 1.1 DRY - Don't Repeat Yourself (不要重复你自己)

**目标**: 消除知识或逻辑在系统中的重复

**实践要求**:
- 任何重复超过一次的逻辑必须提取为函数或方法
- 利用继承与组合避免重复代码
- 配置与常量集中化管理

```python
# ❌ 反面例子
area1 = 3.14 * radius1 * radius1
area2 = 3.14 * radius2 * radius2

# ✅ 正面例子
def calculate_area(radius):
    return 3.14 * radius * radius

area1 = calculate_area(radius1)
area2 = calculate_area(radius2)
```

### 1.2 KISS - Keep It Simple, Stupid (保持简单和直接)

**目标**: 设计尽可能简单的解决方案

**实践要求**:
- 每个函数只做一件事，并且做好
- 使用清晰的自解释性命名
- 避免深度嵌套，使用提前返回（Guard Clauses）

```python
# ❌ 反面例子 (深度嵌套)
function checkUser(user) {
    if (user != null) {
        if (user.isActive) {
            // ... 核心逻辑
        }
    }
}

# ✅ 正面例子 (提前返回)
function checkUser(user) {
    if (user == null) return false;
    if (!user.isActive) return false;

    // ... 清晰的核心逻辑
    return true;
}
```

### 1.3 YAGNI - You Aren't Gonna Need It (你不会需要它)

**目标**: 只实现当前明确需要的功能

**实践要求**:
- 基于需求开发，不做猜测性抽象
- 等到第二次需要时再根据具体需求进行抽象
- 不要为实体添加"可能有用"的字段

```python
# ❌ 反面例子
# 为简单的 UserService 创建接口，尽管目前只有一种实现
class IUserService:
    pass

# ✅ 正面例子
# 直接编写具体实现，未来需要时再提取接口
class UserService:
    pass
```

### 1.4 奥卡姆剃刀原则 (如无必要,勿增实体)

**目标**: 在多个解决方案中，选择假设最少、最简单的那个

**实践要求**:
- 优先选择简单方案，减少不必要的抽象层
- 避免过早引入框架/库
- 在代码审查中应用剃刀原则

```python
# ❌ 反面例子 (过度抽象)
class DataAccessLayer:
    def get_repository(self): ...

class Repository:
    def get_service(self): ...

class Service:
    def get_data(self): ...

# ✅ 正面例子 (直接而清晰)
class UserRepository:
    def get_user_by_id(self, user_id):
        return db.query(User).filter_by(id=user_id).first()
```

---

## 2. 原则之间的关系

- **奥卡姆剃刀**是哲学基础，指导我们选择最简单的方案
- **KISS**是奥卡姆剃刀在软件设计中的具体体现
- **YAGNI**是从时间维度应用奥卡姆剃刀
- **DRY**通过消除重复来减少不必要的实体

---

## 3. 实践示例

### 3.1 代码重构示例

**重构前**:
```python
def calculate_discount(price, customer_type):
    if customer_type == "premium":
        if price > 100:
            discount = price * 0.15
        else:
            discount = price * 0.10
    elif customer_type == "regular":
        if price > 100:
            discount = price * 0.05
        else:
            discount = 0
    else:
        discount = 0
    return price - discount
```

**重构后** (应用KISS和DRY):
```python
def calculate_discount(price, customer_type):
    """计算折扣价格"""
    if price <= 0:
        return 0

    discount_rates = {
        "premium": 0.15 if price > 100 else 0.10,
        "regular": 0.05 if price > 100 else 0,
        "default": 0
    }

    rate = discount_rates.get(customer_type, discount_rates["default"])
    return price * rate
```

### 3.2 配置管理示例

**反模式**:
```python
# 在多个文件中重复定义
MAX_RETRIES = 3
TIMEOUT = 30
```

**正确做法**:
```python
# config.py
class Config:
    MAX_RETRIES = 3
    TIMEOUT = 30

# 在其他地方使用
from config import Config
retries = Config.MAX_RETRIES
```

---

## 4. 在项目中的应用

### 4.1 开发阶段

1. **分析需求**: 应用第一性原理，理解真实需求
2. **设计方案**: 使用奥卡姆剃刀选择最简单方案
3. **编写代码**: 遵循KISS和DRY原则
4. **避免过度设计**: 实践YAGNI原则

### 4.2 代码审查

在代码审查中检查：
- [ ] 是否存在重复代码？
- [ ] 代码是否过于复杂？
- [ ] 是否实现了不需要的功能？
- [ ] 是否有更简单的解决方案？

### 4.3 重构时机

- 发现重复代码时立即重构
- 函数过长时拆分为小函数
- 类承担过多职责时重新设计
- 抽象层过多时简化结构

---

**参考文档**:
- [开发规则与实践](./development_rules.md)
- [AI助手工作流程](./ai_workflow.md)

---

**版本历史**:
- v1.0 (2026-01-04): 初始版本，完整的核心原则说明
