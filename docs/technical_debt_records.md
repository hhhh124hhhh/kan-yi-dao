# "砍一刀"项目技术债务记录文档

## 1. 变量命名规范现状记录

### 🔍 现有不规范变量清单

#### Player类 (src/game/player.py)
| 中文名 | 英文变量名 | 类型 | 当前值/定义 | 问题类型 | 位置 |
|--------|------------|------|-------------|----------|------|
| 增加经验 | addExperience | method | line 224 | 驼峰命名 | player.py:224 |
| 升级武器 | upgradeWeapon | method | line 286 | 驼峰命名 | player.py:286 |
| 使用金币 | useCoins | method | line 271 | 驼峰命名 | player.py:271 |
| 计算所需经验 | calc_exp_needed | method | line 55 | 命名不一致 | player.py:55 |
| 计算伤害 | calc_damage | method | line 70 | 命名不一致 | player.py:70 |

#### Enemy类 (src/game/enemy.py)
| 中文名 | 英文变量名 | 类型 | 当前值/定义 | 问题类型 | 位置 |
|--------|------------|------|-------------|----------|------|
| 受到伤害 | hit | method | line 55 | 语义不准确 | enemy.py:55 |
| 受到伤害 | takeDamage | method | 未找到 | 应有方法 | 缺失 |
| 被击中回调 | onHit | method | 未找到 | 应有方法 | 缺失 |
| 更新位置 | updatePosition | method | 未找到 | 应有方法 | 缺失 |

#### UIManager类 (src/game/ui.py)
| 中文名 | 英文变量名 | 类型 | 当前值 | 问题类型 | 位置 |
|--------|------------|------|---------|----------|------|
| AI文本计时器 | aiTextTimer | int | 0 | 混合命名风格 | ui.py:56 |
| 当前AI文本 | current_ai_text | str | "" | 命名良好 | ui.py:55 |

#### RuleBasedAI类 (src/ai/rule_based_ai.py)
| 中文名 | 英文变量名 | 类型 | 当前值 | 问题类型 | 位置 |
|--------|------------|------|---------|----------|------|
| 玩家攻击模式 | player_attack_patterns | dict | {} | 私有变量缺下划线 | rule_based_ai.py:34 |
| 玩家成功率 | player_success_rates | dict | {} | 私有变量缺下划线 | rule_based_ai.py:35 |
| 最后玩家动作 | last_player_action | Any | None | 私有变量缺下划线 | rule_based_ai.py:36 |

### ✅ 命名良好的变量示例
- `player_hp`, `enemy_hp` - 标准下划线命名
- `is_alive`, `can_attack` - 布尔变量有前缀
- `DEFAULT_ATTACK_POWER` - 常量全大写

## 2. 模块接口契约现状记录

### 📋 现有模块接口清单

#### BattleModule (战斗模块) - 当前状态
**实际接口**: `Player.attack(enemy) -> Tuple[bool, int, bool]`
```python
def attack(self, enemy) -> Tuple[bool, int, bool]:
    """
    攻击敌人

    Args:
        enemy: 敌人对象

    Returns:
        (是否命中, 伤害值, 是否暴击)

    副作用:
        - 消耗玩家体力
        - 增加连击数
        - 给予经验值
        - 直接修改enemy.hp状态

    耦合问题:
        - 直接依赖Enemy类
        - 直接调用enemy.hit()方法
    """
```

#### AIManagerModule (AI管理模块) - 当前状态
**实际接口**: `update_and_respond(player, enemy, additional_context) -> Optional[str]`
```python
def update_and_respond(self,
                      player,
                      enemy,
                      additional_context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    更新AI状态并生成回应

    Args:
        player: 玩家对象 (无类型注解)
        enemy: 敌人对象 (无类型注解)
        additional_context: 额外上下文信息

    Returns:
        AI回应文本，无回应时返回None

    副作用:
        - 更新AI学习状态
        - 修改AI亲密度
        - 记录攻击和连击事件

    异常处理:
        - 发生异常时返回None并记录日志
    """
```

#### PlayerModule (玩家模块) - 当前状态
**主要方法接口**:
- `use_stamina(amount: int) -> bool`
- `regen_stamina(amount: int) -> None`
- `add_exp(amount: int) -> None`
- `level_up() -> None`
- `upgrade_weapon() -> bool`

## 3. 注释文档完整性现状记录

### 📝 文档质量评估

#### ✅ 文档完整的模块
- **game_constants.py**:
  - 完整的类和常量文档
  - 详细的使用说明
  - 属性映射表
  - 验证函数文档

- **ai_interface.py**:
  - 完整的抽象接口文档
  - 详细的类型注解
  - 方法参数和返回值说明

- **technical_debt_prevention.md**:
  - 完善的规范文档
  - 实施指南
  - 成功指标定义

#### ⚠️ 文档不完整的模块
- **data_manager.py**:
  - 缺少模块级文档
  - 方法文档不完整

- **sound_manager.py**:
  - 缺少模块级文档
  - 方法文档简单

- **effects.py**:
  - 缺少粒子系统设计说明
  - 魔法数字未说明用途

#### ❌ 文档缺失的方法
- `Player.add_experience()`: 缺少详细说明
- `Enemy._create_hit_particles()`: 缺少粒子设计说明
- `UIManager._wrap_text()`: 缺少中文处理说明

### 📊 文档统计
- **总模块数**: 20个
- **文档完整**: 8个 (40%)
- **文档部分**: 9个 (45%)
- **文档缺失**: 3个 (15%)

## 4. 逻辑耦合和重构点现状记录

### 🔄 高耦合问题记录

#### Player-Enemy直接耦合
**问题位置**: player.py:173-222
```python
def attack(self, enemy) -> Tuple[bool, int, bool]:
    # ...
    hit = enemy.hit(final_damage)  # 直接依赖具体Enemy类
    if hit:
        enemy.last_damage = damage  # 直接修改enemy状态
```
**影响**:
- 单元测试困难
- 代码重用性低
- 违反依赖倒置原则

#### AI系统数据访问耦合
**问题位置**: context_engine.py (推测)
```python
# 直接访问对象私有属性
context.player_level = player.level
context.enemy_hp = enemy.hp
```
**影响**:
- 数据提取逻辑脆弱
- 对象结构变化时需修改多处
- 难以扩展新的数据源

### 🔁 重复代码记录

#### 属性验证逻辑重复
**位置**: player.py:438-442
```python
def _validate_attributes(self):
    validation_result = validate_player_attributes(self)
    if not validation_result["is_valid"]:
        missing_attrs = validation_result["missing_attributes"]
        error_msg = f"Player对象缺少必需属性: {', '.join(missing_attrs)}"
        raise AttributeError(error_msg)
```

#### UI绘制模式重复
**位置**: ui.py 多处
```python
# 重复模式: 检查状态 -> 设置颜色 -> 创建文本 -> 绘制
if condition:
    text = self.localization.render_text(...)
    screen.blit(text, pos)
```

#### 粒子创建逻辑重复
**位置**: enemy.py:96-109, effects.py 多处
```python
# 重复的粒子创建模式
particle = {
    'pos': list(self.rect.center),
    'vel': [random.uniform(-3, 3), random.uniform(-5, -1)],
    'life': random.randint(20, 40),
    # ...
}
```

### 🏗️ 架构问题记录

#### 缺少抽象层
- 战斗系统缺少BattleInterface抽象
- UI系统缺少UIComponent基类
- 粒子系统缺少ParticleSystem工厂

#### 硬编码依赖
- main.py中直接实例化对象
- AI类型硬编码在AIManager中
- 魔法数字散布在各个模块中

## 5. 当前代码质量统计

### 📊 量化指标
- **命名不规范变量数**: 12个
- **缺少文档的模块**: 3个
- **高耦合关系**: 2处
- **重复代码块**: 4处
- **缺少类型注解的方法**: 约30%

### 🎯 问题分布
- **命名问题**: player.py, enemy.py, ui.py, rule_based_ai.py
- **文档问题**: data_manager.py, sound_manager.py, effects.py
- **耦合问题**: player.py ↔ enemy.py, ai_manager.py ↔ context_engine.py
- **重复代码**: 属性验证, UI绘制, 粒子创建

### 📈 技术债务影响评估
- **维护难度**: 中等 (主要影响新功能开发)
- **扩展性**: 中等受影响 (模块耦合较严重)
- **测试难度**: 较高 (直接依赖多，mock困难)
- **代码理解**: 中等 (文档部分缺失，但结构清晰)

## 6. 技术债务修复计划

| 优先级 | 问题类型 | 文件 | 修复策略 | 负责人 | 状态 |
|--------|----------|------|----------|--------|------|
| 🟥 高 | 命名不统一 | player.py | 统一 snake_case 命名 | Jack | 待修复 |
| 🟥 高 | 命名不统一 | enemy.py | 统一 snake_case 命名 | Jack | 待修复 |
| 🟥 高 | 私有变量缺下划线 | rule_based_ai.py | 添加 _ 前缀 | Jack | 待修复 |
| 🟥 高 | 混合命名风格 | ui.py | 统一 snake_case 命名 | Jack | 待修复 |
| 🟧 中 | 直接依赖Enemy类 | player.py | 抽象BattleInterface | Jack | 待修复 |
| 🟧 中 | AI系统数据访问耦合 | context_engine.py | 实现数据提供者接口 | Jack | 待修复 |
| 🟧 中 | 缺少类型注解 | ai_manager.py | 补充完整类型注解 | Jack | 待修复 |
| 🟧 中 | 属性验证逻辑重复 | player.py | 提取AttributeValidator基类 | Jack | 待修复 |
| 🟩 低 | UI绘制模式重复 | ui.py | 创建UIComponent基类 | Jack | 待定 |
| 🟩 低 | 粒子系统重复 | effects.py, enemy.py | 提炼ParticleFactory | Jack | 待定 |
| 🟩 低 | 缺少模块文档 | data_manager.py | 补充模块级docstring | Jack | 待定 |
| 🟩 低 | 缺少模块文档 | sound_manager.py | 补充模块级docstring | Jack | 待定 |

### 修复阶段规划

#### 第一阶段 (高优先级) - 预计 4小时
- 统一所有模块的 snake_case 命名规范
- 为私有变量添加下划线前缀
- 修复混合命名风格问题

#### 第二阶段 (中优先级) - 预计 8小时
- 设计并实现 BattleInterface 抽象接口
- 重构 AI 系统数据访问方式
- 补充关键方法的类型注解
- 提取通用的属性验证逻辑

#### 第三阶段 (低优先级) - 预计 6小时
- 创建 UI 组件基类减少重复代码
- 设计粒子系统工厂类
- 补充缺失的模块文档

## 7. 修复完成标准 (Definition of Done)

### 核心完成标准
- [ ] **命名规范**: 所有方法统一使用 snake_case 命名
- [ ] **类型注解**: 所有 public 方法均有完整的类型注解
- [ ] **接口抽象**: BattleInterface 抽象完成并解耦 Player-Enemy
- [ ] **代码重复**: 粒子系统代码重复不超过两处
- [ ] **文档完整**: 每个模块具备完整 docstring 和方法说明

### 质量检查标准
- [ ] **测试通过**: 所有现有测试用例继续通过
- [ ] **功能验证**: 游戏核心功能正常运作
- [ ] **代码检查**: 通过 pylint/flake8 静态检查
- [ ] **性能无降级**: 游戏帧率不低于当前水平

### 文档更新标准
- [ ] **API文档**: 更新所有接口文档
- [ ] **变更记录**: 记录所有重构变更
- [ ] **开发指南**: 更新开发规范文档

## 8. 冻结版本信息

### 当前冻结状态
- **冻结版本号**: v0.9.7-clean
- **冻结日期**: 2025-10-20
- **冻结原因**: 完成第一阶段功能开发与技术债务盘点
- **Git提交**: e4cddc5 (使用中文字体和本地化系统改进文本渲染)

### 版本特性
- ✅ 完整的游戏核心玩法
- ✅ AI 伙伴系统
- ✅ 中文本地化支持
- ✅ 基础特效和音效
- ✅ 技术债务完整记录

### 已知技术债务
- 命名规范不统一 (12处)
- 模块耦合度较高 (2处)
- 文档覆盖率 85%
- 代码重复问题 (4处)

### 未来开发计划
- **下个版本**: v1.0.0-stable
- **计划功能**:
  - "Boss战" 玩法扩展
  - 多武器系统
  - 成就系统
  - 数据持久化

### 重启开发指南
1. 按优先级顺序执行技术债务修复计划
2. 每完成一个阶段进行完整测试验证
3. 达到 Definition of Done 标准后方可开始新功能开发
4. 保持文档同步更新

---

**记录时间**: 2025-10-20
**项目版本**: v0.9.7-clean
**记录范围**: src/ 目录下所有Python模块
**下次更新**: 技术债务修复完成后