# 05 — 游戏参数速查

> 本文档列出所有可调游戏参数的**当前值**与**修改位置**，方便快速定位。

---

## 一、植物

所有植物定义在 `source/entity/plant.py`。

### 1.1 攻击型植物

| 植物 | 参数 | 字段 | 当前值 | 说明 |
|------|------|------|--------|------|
| 豌豆射手 | 攻击力 | `PeaShooter.BULLET_DAMAGE` | 20 | 每颗豌豆伤害 |
| 豌豆射手 | 攻速 | `PeaShooter.SHOOT_INTERVAL` | 1.5s | 射击间隔 |
| 寒冰射手 | 攻击力 | `SnowPea.BULLET_DAMAGE` | 20 | 每颗冰豆伤害 |
| 寒冰射手 | 攻速 | `SnowPea.SHOOT_INTERVAL` | 1.5s | 射击间隔 |
| 寒冰射手 | 减速 | `SnowPea.SLOW_DURATION` | 3.0s | 减速持续时间 |
| 双发射手 | 攻击力 | `Repeater.BULLET_DAMAGE` | 20 | 每颗豌豆伤害 |
| 双发射手 | 攻速 | `Repeater.SHOOT_INTERVAL` | 1.5s | 射击间隔 |
| 樱桃炸弹 | 伤害 | `CherryBomb.DAMAGE` | 1800 | 范围秒杀 |
| 樱桃炸弹 | 引爆延迟 | `CherryBomb.FUSE_TIME` | 1.0s | 放置后引爆时间 |
| 樱桃炸弹 | 范围 | `CherryBomb.EXPLODE_RADIUS` | 1 | 3×3 格 |
| 土豆地雷 | 伤害 | `PotatoMine.DAMAGE` | 1800 | 踩踏引爆 |
| 土豆地雷 | 激活时间 | `PotatoMine.ARM_TIME` | 15.0s | 放置后激活等待 |

### 1.2 生产 / 防御植物

| 植物 | 参数 | 字段 | 当前值 | 说明 |
|------|------|------|--------|------|
| 向日葵 | 产阳光间隔 | `SunFlower.SUN_INTERVAL` | **6.0s** | 每轮产出一个阳光 |
| 向日葵 | 阳光值 | `SunFlower.SUN_VALUE` | 25 | 每个阳光数值 |
| 坚果墙 | 血量 | `WallNut.HP_FULL` | 4000 | 最大 HP |
| 坚果墙 | 裂纹1阈值 | `WallNut.HP_CRACKED1` | 2666 | HP 低于此值出现裂纹 |
| 坚果墙 | 裂纹2阈值 | `WallNut.HP_CRACKED2` | 1333 | HP 低于此值严重裂纹 |

### 1.3 植物血量

各植物构造函数 `__init__` 中的 `hp=` 参数：

| 植物 | 文件行位置 | hp 值 |
|------|-----------|-------|
| 向日葵 | `SunFlower.__init__`: `hp=300` | 300 |
| 豌豆射手 | `PeaShooter.__init__`: `hp=300` | 300 |
| 寒冰射手 | `SnowPea.__init__`: `hp=300` | 300 |
| 双发射手 | `Repeater.__init__`: `hp=300` | 300 |
| 坚果墙 | `WallNut.__init__`: `hp=self.HP_FULL` | 4000 |
| 樱桃炸弹 | `CherryBomb.__init__`: `hp=1` | 1（一次性） |
| 土豆地雷 | `PotatoMine.__init__`: `hp=300` | 300 |

---

## 二、植物卡片（费用 + 冷却）

定义在 `source/ui/card_panel.py` → `ALL_CARDS` 字典。

格式：`"plant_type": (sun_cost, cooldown_seconds, "中文名")`

| 植物 | 阳光费用 | 冷却时间 | 字段位置 |
|------|---------|---------|----------|
| 向日葵 | 50 | **7.5s** | `ALL_CARDS["sunflower"]` |
| 豌豆射手 | 100 | 7.5s | `ALL_CARDS["peashooter"]` |
| 坚果墙 | 50 | 30.0s | `ALL_CARDS["wallnut"]` |
| 樱桃炸弹 | 150 | 50.0s | `ALL_CARDS["cherrybomb"]` |
| 土豆地雷 | 25 | 30.0s | `ALL_CARDS["potatomine"]` |
| 寒冰射手 | 175 | 7.5s | `ALL_CARDS["snowpea"]` |
| 双发射手 | 200 | 7.5s | `ALL_CARDS["repeater"]` |

---

## 三、阳光系统

定义在 `source/system/sun_manager.py`。

| 参数 | 字段 | 当前值 | 说明 |
|------|------|--------|------|
| 初始阳光 | `SunManager.INITIAL_SUN` | **300** | 游戏开始时阳光数 |
| 自然掉落间隔 | `SunManager.NATURAL_INTERVAL` | **8.0s** | 天空掉落阳光频率 |

---

## 四、僵尸

定义在 `source/entity/zombie.py`。

### 4.1 血量

| 僵尸 | 文件行位置 | HP |
|------|-----------|-----|
| 普通僵尸 | `NormalZombie.__init__`: `hp=120` | 120 |
| 路障僵尸 | `ConeheadZombie.__init__`: `hp=350` | 350 |
| 铁桶僵尸 | `BucketheadZombie.__init__`: `hp=800` | 800 |
| 旗帜僵尸 | `FlagZombie.__init__`: `hp=120` | 120 |

### 4.2 速度

| 参数 | 方法 | 当前值 |
|------|------|--------|
| 普通/路障/铁桶 移速 | `Zombie._get_speed()` | **15.0** px/s |
| 旗帜僵尸 移速 | `FlagZombie._get_speed()` | **22.0** px/s |
| 减速效果 | `is_slowed` → `speed *= 0.5` | 移速减半 |

### 4.3 攻击力

| 参数 | 方法 | 当前值 |
|------|------|--------|
| 所有僵尸啃食伤害 | `Zombie._get_damage()` | **100.0** HP/s |

---

## 五、子弹

定义在 `source/entity/bullet.py`。

| 子弹 | 速度 | 当前值 |
|------|------|--------|
| 豌豆 / 冰豆 | `Bullet.speed` | 350.0 px/s |

---

## 六、无尽模式

定义在 `source/state/level_state.py`。

| 参数 | 当前值 | 说明 |
|------|--------|------|
| 初始刷怪间隔 | 6.0s | 随时间递减 |
| 最小刷怪间隔 | 1.5s | 下限 |
| 间隔递减速率 | `6.0 - elapsed / 60.0` | 每 60 秒减 1 秒 |
| 难度阶段 1 | 0-60s | 普通 + 路障为主 |
| 难度阶段 2 | 60-120s | 路障 + 铁桶 + 旗帜增多 |
| 难度阶段 3 | 120s+ | 铁桶 + 旗帜主导 |
| 种植列范围 | col 0-7 | col 8 不可种（道路） |

---

## 七、快速索引

| 你想改的 | 文件 | 字段 / 位置 |
|----------|------|------------|
| 植物伤害 | `source/entity/plant.py` | 各 `DAMAGE` / `BULLET_DAMAGE` |
| 植物血量 | `source/entity/plant.py` | 各 `__init__` 的 `hp=` |
| 植物攻速 | `source/entity/plant.py` | 各 `SHOOT_INTERVAL` |
| 卡片冷却 | `source/ui/card_panel.py` | `ALL_CARDS` 字典第 2 个值 |
| 卡片费用 | `source/ui/card_panel.py` | `ALL_CARDS` 字典第 1 个值 |
| 向日葵产阳光 | `source/entity/plant.py` | `SunFlower.SUN_INTERVAL` |
| 初始阳光数 | `source/system/sun_manager.py` | `SunManager.INITIAL_SUN` |
| 阳光掉落频率 | `source/system/sun_manager.py` | `SunManager.NATURAL_INTERVAL` |
| 僵尸血量 | `source/entity/zombie.py` | 各子类 `__init__` 的 `hp=` |
| 僵尸速度 | `source/entity/zombie.py` | `_get_speed()` 返回值 |
| 僵尸攻击力 | `source/entity/zombie.py` | `_get_damage()` 返回值 |
| 子弹速度 | `source/entity/bullet.py` | `Bullet.speed` |
| 无尽刷怪间隔 | `source/state/level_state.py` | `_update_endless_spawn()` |
| 种植范围 | `source/state/level_state.py` | `VALID_COL_MIN/MAX` |
