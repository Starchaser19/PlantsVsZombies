# 01 — 系统架构

## 1. 总体架构

```
┌─────────────────────────────────────────────────────┐
│                     main.py                          │
│         初始化 Pygame → 启动状态机 → 主循环           │
└─────────────────────┬───────────────────────────────┘
                      │
         ┌────────────▼────────────┐
         │    GameStateMachine     │  ← 栈式管理
         │  push / pop / change    │
         └────────────┬────────────┘
                      │
      ┌───────────────┼───────────────┐
      │               │               │
  ┌───▼───┐     ┌─────▼────┐   ┌──────▼──────┐
  │ Menu  │     │  Level   │   │  GameOver   │
  │ State │     │  State   │   │   State     │
  └───────┘     └─────┬────┘   └─────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   ┌────▼────┐  ┌─────▼─────┐  ┌───▼───┐
   │ Entity  │  │  Systems  │  │  UI   │
   │ Layer   │  │  Layer    │  │ Layer │
   └─────────┘  └───────────┘  └───────┘
```

三层分离：
- **Entity Layer** — 植物、僵尸、子弹、阳光等游戏对象
- **Systems Layer** — 碰撞检测、波次管理、阳光经济、计时器
- **UI Layer** — 菜单栏、卡片面板、HUD、暂停菜单

## 2. 状态机设计

### 2.1 状态接口

```python
class GameState(ABC):
    def enter(self, *args, **kwargs) -> None: ...
    def exit(self) -> None: ...
    def handle_event(self, event: pygame.Event) -> None: ...
    def update(self, dt: float) -> None: ...
    def draw(self, screen: pygame.Surface) -> None: ...
```

### 2.2 状态转移图

```
                 ┌──────────┐
                 │  Splash  │  (可选启动画面)
                 └────┬─────┘
                      │ 2s 后自动
                 ┌────▼─────┐
        ┌───────│   Menu   │
        │       └────┬─────┘
        │            │ 选择关卡
        │       ┌────▼─────┐      ESC
        │       │   Level  │◄──────────┐
        │       └──┬───┬───┘           │
        │          │   │               │
        │    胜利/失败 │         ┌─────┴─────┐
        │          │   │         │   Pause   │
        │     ┌────▼───▼──┐      └───────────┘
        │     │  GameOver  │
        │     └─────┬──────┘
        │           │ 重试 / 下一关 / 返回
        └───────────┘
```

### 2.3 LevelState 主循环详解

```python
# LevelState.update(dt) 每帧执行顺序：

 1. SunManager.update(dt)         # 阳光自然掉落 + 向日葵产出
 2. WaveManager.update(dt)        # 按 JSON 时间线 spawn 僵尸
 3. plants.update_all(dt)         # 所有植物：射击计时器 / 生产计时器
 4. bullets.update_all(dt)        # 子弹位移
 5. zombies.update_all(dt, map)   # 僵尸 AI：寻路 → 移动 → 攻击
 6. CollisionSystem.check()       # 碰撞检测（见 §5）
 7. LawnMowerManager.update(dt)   # 割草机触发检测
 8. EntityManager.cleanup()       # 移除死亡实体
 9. WinLoseChecker.check()        # 胜负判定
```

## 3. 实体继承体系

```
GameObject (ABC)
├── attributes: rect, image, hp, alive, row, col
├── methods: update(dt), draw(screen), take_damage(n), kill()
│
├── Plant (ABC)
│   ├── sun_cost: int
│   ├── cooldown: int (ms)
│   ├── plant_type: str
│   │
│   ├── SunFlower     → 每隔 N 秒产出一个 Sun 实体
│   ├── PeaShooter    → 每隔 N 秒向右发射 PeaBullet
│   ├── SnowPea       → 发射 SnowPeaBullet（命中附加 slow 效果）
│   ├── Repeater      → 每次发射 2 颗豌豆
│   ├── Threepeater   → 三线射击
│   ├── WallNut       → 高 HP，纯防御
│   ├── TallNut      → 更高 HP，可阻挡跳跃僵尸
│   ├── CherryBomb    → 放置后延迟爆炸，范围伤害
│   ├── PotatoMine    → 放置后延迟激活，僵尸踩踏引爆
│   ├── Chomper       → 吞噬前方僵尸，咀嚼冷却
│   ├── Squash        → 碾压前方最近僵尸
│   ├── Spikeweed     → 地面持续伤害
│   ├── Torchwood     → 豌豆穿过变火焰弹（双倍伤害）
│   ├── Jalapeno      → 整行火焰伤害
│   ├── SnowPea       → 减速效果
│   ├── SunShroom     → 夜间经济植物
│   ├── PuffShroom    → 免费短射程
│   ├── ScaredyShroom → 僵尸靠近躲藏
│   ├── IceShroom     → 全屏冰冻
│   ├── HypnoShroom   → 策反僵尸
│   ├── LilyPad       → 泳池种植平台
│   ├── FlowerPot     → 屋顶种植平台
│   └── CoffeeBean    → 唤醒蘑菇
│
├── Zombie (ABC)
│   ├── speed: float
│   ├── damage: int (每次攻击伤害)
│   ├── state: WALK | ATTACK | DEATH | FROZEN
│   │
│   ├── NormalZombie     → 标准属性
│   ├── FlagZombie       → 加速波次，移速略快
│   ├── ConeheadZombie   → 2× HP
│   ├── BucketheadZombie → 4× HP
│   ├── PoleVaulting     → 跳跃越过第一株植物
│   ├── NewspaperZombie  → 报纸损毁后狂暴加速
│   ├── FootballZombie   → 极高 HP + 快速
│   ├── SnorkelZombie    → 潜行（泳池）
│   ├── Zomboni          → 冰车，碾压植物 + 铺冰道
│   ├── BalloonZombie    → 飞行，需仙人掌/三叶草
│   ├── DancingZombie    → 召唤伴舞
│   ├── Gargantuar       → BOSS，投掷小鬼
│   └── Imp              → 小鬼（被投掷/从巨人背上来）
│
├── Bullet (ABC)
│   ├── speed: float
│   ├── damage: int
│   │
│   ├── PeaBullet       → 标准子弹
│   ├── SnowPeaBullet   → 附加 frozen 状态
│   ├── FirePeaBullet   → 穿甲（不因命中消失）
│   └── Spore           → 蘑菇孢子
│
├── Sun
│   ├── value: int (25 / 50)
│   ├── target_y: int  (掉落终点)
│   ├── lifetime: int   (超时自动消失)
│   └── collected: bool
│
└── LawnMower
    ├── row: int
    ├── triggered: bool
    └── speed: float
```

## 4. 网格地图系统

```
草坪 = 9 列 × 5 行 网格

     col 0  1  2  3  4  5  6  7  8
row 0 [ ][ ][ ][ ][ ][ ][ ][ ][ ]
row 1 [ ][ ][ ][ ][ ][ ][ ][ ][ ]
row 2 [ ][ ][ ][ ][ ][ ][ ][ ][ ]
row 3 [ ][ ][ ][ ][ ][ ][ ][ ][ ]
row 4 [ ][ ][ ][ ][ ][ ][ ][ ][ ]
       ↑                        ↑
     左侧                     右侧（僵尸方向→）
    (植物侧)                 (房屋侧)

特殊列:
  col 0       → 割草机列（不种植）
  col 1-7     → 可种植区域
  col 8       → 僵尸生成边界
```

**坐标转换：**
```python
# 屏幕坐标 → 网格坐标
def screen_to_grid(screen_x: int, screen_y: int) -> tuple[int, int]:
    grid_x = (screen_x - MAP_OFFSET_X) // GRID_X_SIZE
    grid_y = (screen_y - MAP_OFFSET_Y) // GRID_Y_SIZE
    return grid_x, grid_y

# 网格坐标 → 屏幕坐标（用于放置植物）
def grid_to_screen(grid_x: int, grid_y: int) -> tuple[int, int]:
    screen_x = grid_x * GRID_X_SIZE + MAP_OFFSET_X
    screen_y = grid_y * GRID_Y_SIZE + MAP_OFFSET_Y
    return screen_x, screen_y
```

## 5. 碰撞检测系统

```
CollisionSystem.check() 每帧执行:

1. Bullet × Zombie
   for bullet in bullets:
       for zombie in zombies:
           if bullet.rect.colliderect(zombie.rect):
               zombie.take_damage(bullet.damage)
               if bullet.has_slow:
                   zombie.apply_status(Status.FROZEN, duration=3000)
               bullet.kill()
               break  # 一颗子弹只命中一个僵尸（火焰弹除外）

2. Zombie × Plant
   for zombie in zombies:
       plant = map.get_plant_at(zombie.row, zombie.col)
       if plant and zombie.rect.colliderect(plant.rect):
           zombie.state = ZombieState.ATTACK  # 停止移动，开始啃食
           plant.take_damage(zombie.damage * dt)

3. Zombie × House (触发线)
   if zombie.rect.left <= HOUSE_X_THRESHOLD:
       game_over(win=False)

4. Zombie × LawnMower
   if lawnmower.rect.colliderect(zombie.rect):
       zombie.kill()
       lawnmower.trigger(row)  # 启动割草机，碾压该行所有僵尸

5. Mouse × Sun (点击收集)
   if event.type == MOUSEBUTTONDOWN:
       for sun in suns:
           if sun.rect.collidepoint(event.pos):
               sun.collect()
```

## 6. 僵尸 AI 状态机

```
                    ┌──────────┐
     spawn ───────▶ │   WALK   │
                    └────┬─────┘
                         │ 前方有植物且进入攻击范围
                         ▼
                    ┌──────────┐
                    │  ATTACK  │──── 植物死亡 ────▶ WALK
                    └────┬─────┘
                         │ HP ≤ 0
                         ▼
                    ┌──────────┐
                    │  DEATH   │──── 播放死亡动画 ──▶ remove
                    └──────────┘

附加状态（可与上述叠加）:
  - FROZEN:  移速 × 0.5，蓝色着色，持续 N ms
  - HYPNOTIZED: 反向移动，攻击其他僵尸
  - BURNING:  持续掉血
```

## 7. 数据流

```
level_01.json ──加载──▶ WaveManager
                          │
                          │ spawn_at(time, zombie_type, row)
                          ▼
                      Zombie 实例
                          │
                          │ update(dt, map)
                          ▼
                    ┌─────────────┐
                    │ 碰撞检测系统 │◄── bullets
                    └──────┬──────┘
                           │ 命中
                           ▼
                    zombie.take_damage(dmg)
                           │
                    ┌──────▼───────┐
                    │ HP ≤ 0?      │
                    │  → kill()    │──── 触发 WaveManager.on_zombie_death()
                    │  → cleanup() │──── 触发 WinLoseChecker.check()
                    └──────────────┘
```

## 8. 关键设计原则

1. **数据驱动** — 关卡、植物属性全在 JSON，代码改动不应成为调参前提
2. **单一职责** — 碰撞检测、波次管理、阳光经济各自独立模块
3. **依赖注入** — LevelState 接收 Map/Config 作为构造参数，方便测试
4. **优先组合** — 用组件（StatusEffect、AnimationController）而非深层继承
5. **帧率无关** — 所有 Update 使用 `dt`（delta time），确保不同帧率下行为一致
