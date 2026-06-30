# Python Plants vs Zombies — 项目文档

> 基于 Python + Pygame 的 2D 塔防游戏复刻，参考 [marblexu/PythonPlantsVsZombies](https://github.com/marblexu/PythonPlantsVsZombies)

## 文档索引

| 编号 | 文档 | 用途 |
|------|------|------|
| 01 | [architecture](./01-architecture.md) | 系统架构、模块职责、状态机、实体继承体系、数据流 |
| 02 | [technical-spec](./02-technical-spec.md) | 技术选型、目录结构、关键设计决策、性能策略 |
| 03 | [game-design](./03-game-design.md) | GDD：植物/僵尸属性表、关卡设计、阳光经济、碰撞规则 |
| 04 | [roadmap](./04-roadmap.md) | 分阶段实现路线图、里程碑、可交付物 |

## 参考项目分析

marblexu/PythonPlantsVsZombies 是一个 **纯 Python + Pygame 1.9.6** 的复刻项目，约 2.6k stars。

**借鉴点：**
- JSON 驱动关卡配置（不改代码即可调关卡）
- OOP 继承体系（Plant → SunFlower/PeaShooter/...)
- 栈式状态机管理游戏流程
- 半透明种植预览（`set_alpha(128)`）
- 帧循环精灵动画

**改进方向：**
- 升级 Pygame 2.x + Python 3.10+
- 植物属性 JSON 化（替代硬编码平行数组）
- 全类型注解（type hints）
- 单元测试覆盖核心逻辑
- Sprite sheet 替代零散图片

## 约定

- 分支策略：`main` 保持可运行，功能在 feature 分支开发
- 提交信息：中文，动词开头（"新增向日葵实体"）
- 代码风格：PEP 8，类型注解强制
