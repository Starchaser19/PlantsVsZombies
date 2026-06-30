# 02 — 技术规格

## 1. 技术选型

| 维度 | 选型 | 版本 | 理由 |
|------|------|------|------|
| 语言 | Python | ≥ 3.10 | match-case 语法糖，更好的类型系统 |
| 游戏框架 | **Pygame** | ≥ 2.5 | 社区最活跃的 2D 游戏库，底层 SDL2 |
| 包管理 | pip + venv | — | 标准工具链，无额外学习成本 |
| 关卡数据 | JSON | — | 人类可读，Python 原生支持 |
| 类型检查 | mypy | ≥ 1.0 | 静态类型检查，CI 集成 |
| 格式化 | ruff | latest | 替代 flake8 + isort + black，极快 |
| 测试 | pytest | ≥ 7.0 | 最流行的 Python 测试框架 |
| 打包 | PyInstaller | latest | 单文件 .exe 分发 |
| 精灵来源 | 占位色块 → 后期替换 | — | 先跑通逻辑，再管美术 |

### 备选方案对比

| 框架 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| Pygame | 文档丰富，2D 最佳实践多 | 无原生 UI 组件 | ✅ 首选 |
| Pygame-CE | Pygame 社区增强版，性能更好 | 相对较新 | 备选 |
| Pyglet | 纯 Python，OpenGL 加速 | 社区较小，参考少 | ❌ |
| Arcade | 更现代 API，内置物理 | Pygame 迁移成本高 | ❌ |
| Godot | 专业引擎 | 语言不同，学习曲线陡 | ❌ |

## 2. 项目目录结构

```
PythonPlantsVsZombies/
│
├── main.py                          # 入口：初始化 + 启动状态机
├── README.md                        # 项目说明 + 运行指南
├── requirements.txt                 # 依赖清单
├── pyproject.toml                   # 项目元数据 + 工具配置
│
├── docs/                            # 文档（你在这里）
│   ├── README.md
│   ├── 01-architecture.md
│   ├── 02-technical-spec.md
│   ├── 03-game-design.md
│   └── 04-roadmap.md
│
├── source/                          # 源代码
│   ├── __init__.py
│   ├── constants.py                 # 全局常量
│   ├── settings.py                  # 可配置参数（从 JSON 读取）
│   │
│   ├── state/                       # 状态机层
│   │   ├── __init__.py
│   │   ├── state_machine.py         # 状态机基类 + 栈管理
│   │   ├── menu_state.py            # 主菜单
│   │   ├── level_state.py           # ★ 核心游戏循环
│   │   ├── pause_state.py           # 暂停菜单
│   │   └── gameover_state.py        # 结算界面
│   │
│   ├── entity/                      # 实体层
│   │   ├── __init__.py
│   │   ├── game_object.py           # 基类 GameObject
│   │   ├── plant.py                 # Plant 基类 + 所有子类
│   │   ├── zombie.py                # Zombie 基类 + 所有子类
│   │   ├── bullet.py                # Bullet 基类 + 变体
│   │   ├── sun.py                   # 阳光实体
│   │   └── lawnmower.py             # 割草机
│   │
│   ├── system/                      # 系统层（纯逻辑，无渲染）
│   │   ├── __init__.py
│   │   ├── collision.py             # 碰撞检测
│   │   ├── wave_manager.py          # 波次管理（读 JSON 时间线）
│   │   ├── sun_manager.py           # 阳光经济
│   │   ├── entity_manager.py        # 实体生命周期管理
│   │   └── win_lose_checker.py      # 胜负判定
│   │
│   ├── ui/                          # UI 层
│   │   ├── __init__.py
│   │   ├── menu_bar.py              # 顶部栏（阳光数、进度条）
│   │   ├── card_panel.py            # 植物卡片选择面板
│   │   ├── card.py                  # 单张卡片
│   │   ├── button.py                # 通用按钮
│   │   └── hud.py                   # HUD 聚合
│   │
│   ├── map/                         # 地图
│   │   ├── __init__.py
│   │   └── grid_map.py              # 网格地图
│   │
│   ├── data/                        # 配置数据
│   │   ├── levels/                  # 关卡 JSON
│   │   │   ├── level_01.json
│   │   │   └── ...
│   │   ├── plants.json              # 植物属性表
│   │   ├── zombies.json             # 僵尸属性表
│   │   └── constants.json           # 游戏常量（可调）
│   │
│   └── utils/                       # 工具
│       ├── __init__.py
│       ├── sprite_loader.py         # 精灵加载 + 缓存
│       ├── animation.py             # 帧动画控制器
│       ├── timer.py                 # 通用计时器
│       └── resource_path.py         # 资源路径解析
│
├── resources/                       # 静态资源
│   ├── graphics/
│   │   ├── background/              # 背景（day/night/pool/roof）
│   │   ├── plants/                  # 植物精灵帧
│   │   ├── zombies/                 # 僵尸精灵帧
│   │   ├── bullets/                 # 子弹
│   │   ├── ui/                      # UI 元素
│   │   └── effects/                 # 特效
│   ├── fonts/
│   └── audio/
│       ├── bgm/                     # 背景音乐
│       └── sfx/                     # 音效
│
├── tests/                           # 测试
│   ├── __init__.py
│   ├── test_collision.py
│   ├── test_grid_map.py
│   ├── test_wave_manager.py
│   ├── test_zombie_ai.py
│   └── conftest.py                  # pytest fixtures
│
└── tools/                            # 开发工具脚本
    ├── level_editor.py              # 关卡可视化编辑器（后期）
    └── sprite_packer.py             # 精灵打包工具
```

## 3. 关键设计决策

### 3.1 帧率无关更新

所有 `update()` 方法接收 `dt: float`（秒），速度/计时器均乘以 dt：

```python
class Zombie:
    def update(self, dt: float) -> None:
        self.rect.x += self.speed * dt  # speed 单位为 px/s
        self.timer -= dt                 # 计时器单位为秒

class Game:
    def run(self) -> None:
        clock = pygame.time.Clock()
        while self.running:
            dt = clock.tick(60) / 1000.0  # 转换为秒
            self.state.update(dt)
```

### 3.2 对象池 (Object Pool)

子弹和阳光频繁创建/销毁 → 用对象池避免 GC 抖动：

```python
class BulletPool:
    def __init__(self, size: int = 200):
        self._pool = [Bullet() for _ in range(size)]
        self._available = deque(self._pool)

    def acquire(self, x, y, bullet_type) -> Bullet:
        b = self._available.popleft()  # O(1)
        b.reset(x, y, bullet_type)
        return b

    def release(self, bullet: Bullet) -> None:
        bullet.alive = False
        self._available.append(bullet)
```

### 3.3 精灵资源策略

**开发阶段：** 纯色几何形状占位
- 植物 = 绿色圆形 + 文字
- 僵尸 = 棕色矩形 + 文字
- 子弹 = 小黄点

**后期替换：**
- 资源路径集中管理在 `constants.py`
- 替换图片文件即可，代码不改

### 3.4 配置策略

```python
# settings.py — 从 JSON 加载，运行时可访问
@dataclass
class GameSettings:
    screen_width: int = 900
    screen_height: int = 600
    fps: int = 60
    grid_cols: int = 9
    grid_rows: int = 5
    grid_x_size: int = 80
    grid_y_size: int = 100
    # ...

# 从 plants.json 加载植物属性
@dataclass
class PlantConfig:
    name: str
    sun_cost: int
    cooldown_ms: int
    hp: int
    # ...

class ConfigLoader:
    @staticmethod
    def load_plants(path: str) -> dict[str, PlantConfig]: ...
    @staticmethod
    def load_zombies(path: str) -> dict[str, ZombieConfig]: ...
    @staticmethod
    def load_level(path: str) -> LevelConfig: ...
```

### 3.5 渲染分层

```
Layer 0: 背景图（草坪）
Layer 1: 植物（静止时）
Layer 2: 僵尸
Layer 3: 子弹
Layer 4: 阳光 + 特效粒子
Layer 5: 植物（射击动画覆盖层）
Layer 6: UI（菜单栏、卡片面板、HUD）
Layer 7: 鼠标预览（半透明植物 + 铲子图标）
```

## 4. 性能预算

| 实体类型 | 预计同时存在 | 内存 |
|----------|-------------|------|
| 植物 | ≤ 45 (9×5) | 可忽略 |
| 僵尸 | ≤ 50 (大波) | 可忽略 |
| 子弹 | ≤ 100 | 对象池复用 |
| 阳光 | ≤ 20 | 对象池复用 |
| 粒子 | ≤ 200 | 对象池复用 |

目标：稳定 60fps，CPU < 20%（现代硬件）。

优化手段：
1. 对象池（子弹/阳光/粒子）
2. 网格空间划分（碰撞检测 O(n×m) 而非 O(n²)）
3. 脏矩形渲染（仅重绘变化区域）
4. Sprite sheet 合并（减少 texture switching）
