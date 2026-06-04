"""Logic game MONSTERA ECLIPSE: class karakter, battle engine, dan screen.
"""

import pygame
import sys
import random
import math

from config import *
from aset_game import asset_manager

# ─── PARTICLE SYSTEM ─────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color, vx=None, vy=None, life=None, size=None):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx if vx is not None else random.uniform(-2, 2)
        self.vy = vy if vy is not None else random.uniform(-3, -0.5)
        self.life = life if life is not None else random.randint(30, 70)
        self.max_life = self.life
        self.size = size if size is not None else random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05
        self.life -= 1

    def draw(self, surf):
        alpha = self.life / self.max_life
        r = int(self.color[0] * alpha)
        g = int(self.color[1] * alpha)
        b = int(self.color[2] * alpha)
        sz = max(1, int(self.size * alpha))
        pygame.draw.circle(surf, (r, g, b), (int(self.x), int(self.y)), sz)

particles = []

def spawn_particles(x, y, color, count=15, spread=20):
    for _ in range(count):
        px = x + random.randint(-spread, spread)
        py = y + random.randint(-spread, spread)
        particles.append(Particle(px, py, color))

def update_particles(surf):
    for p in particles[:]:
        p.update()
        p.draw(surf)
        if p.life <= 0:
            particles.remove(p)


# ══════════════════════════════════════════════════════════════════════════════
#  LEVEL SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

class LevelSystem:
    """
    Mengelola level/wave saat ini, scaling difficulty musuh,
    dan reward HP heal untuk hero setelah menang.

    Scaling bertahap:
      - Level 1–3  : Tier 1, 2–3 musuh, mix Shadow/DarkMage
      - Level 4–6  : Tier 2, 3–4 musuh, mulai ada musuh campuran
      - Level 7–9  : Tier 3, 4 musuh, semua kuat
      - Level 10+  : Tier 4+, 4 musuh, elite mode — enemy boss ikut muncul
    """
    MAX_LEVELS = 12  # setelah ini dianggap "clear game"

    def __init__(self):
        self.current_level = 1
        self.total_score   = 0  # akumulasi damage dealt (opsional future use)

    @property
    def tier(self) -> int:
        """Tier musuh naik setiap 3 level."""
        return min(4, (self.current_level - 1) // 3 + 1)

    @property
    def enemy_count(self) -> int:
        """Jumlah musuh: 2 di level 1, max 4 setelah level 3."""
        if self.current_level == 1:
            return 2
        elif self.current_level == 2:
            return 3
        else:
            return 4

    @property
    def heal_percent(self) -> float:
        """Persentase HP max yang dipulihkan setelah menang (0.0–1.0)."""
        # Makin tinggi level, makin sedikit heal reward
        if self.current_level <= 3:
            return 0.40
        elif self.current_level <= 6:
            return 0.30
        elif self.current_level <= 9:
            return 0.20
        else:
            return 0.15

    @property
    def enemy_pool(self) -> list:
        """Kelas musuh yang tersedia di level ini."""
        if self.current_level <= 3:
            return [Shadow, DarkMage]
        elif self.current_level <= 6:
            return [Shadow, DarkMage, Shadow]   # Shadow lebih sering
        elif self.current_level <= 9:
            return [Shadow, DarkMage, BossEclipse]
        else:
            return [DarkMage, BossEclipse, BossEclipse]  # Level elite

    def generate_enemies(self) -> list:
        """Generate daftar musuh sesuai level saat ini."""
        pool  = self.enemy_pool
        count = self.enemy_count
        tier  = self.tier
        enemies = []
        for _ in range(count):
            cls = random.choice(pool)
            enemies.append(cls(tier))
        return enemies

    def apply_post_win_heal(self, heroes: list):
        """Pulihkan sebagian HP hero setelah menang satu level."""
        pct = self.heal_percent
        for hero in heroes:
            if hero.alive:
                amount = int(hero.max_hp * pct)
                hero.heal(amount)

    def advance(self):
        """Naik ke level berikutnya."""
        self.current_level += 1

    @property
    def is_game_cleared(self) -> bool:
        return self.current_level > self.MAX_LEVELS

    def level_label(self) -> str:
        tier_labels = {1: "🌿 Hijau", 2: "🌑 Redup", 3: "☄️ Gelap", 4: "💀 Eclipse"}
        return tier_labels.get(self.tier, "??")

    def difficulty_stars(self) -> str:
        stars = min(5, 1 + (self.current_level - 1) // 2)
        return "⭐" * stars + "☆" * (5 - stars)


# ══════════════════════════════════════════════════════════════════════════════
#  ABSTRACTION & INHERITANCE — Base Classes
# ══════════════════════════════════════════════════════════════════════════════

class Character:
    """
    [ABSTRACTION] Base abstract class untuk semua karakter.
    [ENCAPSULATION] Semua atribut diakses melalui property/method.
    """
    def __init__(self, name: str, max_hp: int, attack: int,
                 defense: int, speed: int, color: tuple):
        self._name    = name
        self._max_hp  = max_hp
        self._hp      = max_hp
        self._attack  = attack
        self._defense = defense
        self._speed   = speed
        self._color   = color
        self._alive   = True
        self._skills  = []
        self._status_effects = []

    @property
    def name(self):      return self._name
    @property
    def hp(self):        return self._hp
    @property
    def max_hp(self):    return self._max_hp
    @property
    def attack(self):    return self._attack
    @property
    def defense(self):   return self._defense
    @property
    def speed(self):     return self._speed
    @property
    def color(self):     return self._color
    @property
    def alive(self):     return self._alive
    @property
    def skills(self):    return self._skills

    def take_damage(self, raw_dmg: int) -> int:
        actual = max(1, raw_dmg - self._defense)
        self._hp = max(0, self._hp - actual)
        if self._hp == 0:
            self._alive = False
        return actual

    def heal(self, amount: int) -> int:
        healed = min(amount, self._max_hp - self._hp)
        self._hp += healed
        return healed

    def hp_ratio(self) -> float:
        return self._hp / self._max_hp

    def get_description(self) -> str:
        raise NotImplementedError

    def get_role_icon(self) -> str:
        raise NotImplementedError

    def use_skill(self, skill_index: int, targets: list, allies: list) -> dict:
        raise NotImplementedError


class Skill:
    def __init__(self, name, description, skill_type, power, color, icon):
        self.name        = name
        self.description = description
        self.skill_type  = skill_type
        self.power       = power
        self.color       = color
        self.icon        = icon


# ══════════════════════════════════════════════════════════════════════════════
#  HERO CLASSES
# ══════════════════════════════════════════════════════════════════════════════

class Hero(Character):
    def __init__(self, name, max_hp, attack, defense, speed, color, role):
        super().__init__(name, max_hp, attack, defense, speed, color)
        self._role = role

    @property
    def role(self): return self._role

    def get_description(self):
        return f"HP:{self._max_hp} ATK:{self._attack} DEF:{self._defense} SPD:{self._speed}"

    def get_role_icon(self):
        return "🌿"


class Warrior(Hero):
    def __init__(self, name="Verdant Knight"):
        super().__init__(name, max_hp=180, attack=35, defense=20,
                         speed=12, color=C_GREEN, role="Warrior")
        self._skills = [
            Skill("Vine Slash",  "Serangan fisik kuat ke 1 musuh",         "attack",  1.4, C_GREEN,  "⚔️"),
            Skill("Root Shield", "Pertahanan diri sendiri +20 DEF 2 turn", "defense", 0,   C_CYAN,   "🛡️"),
            Skill("Thorn Burst", "Serang semua musuh dengan duri",          "aoe",     0.8, C_GREEN2, "🌵"),
            Skill("Earth Smash", "Serangan brutal ke 1 musuh",             "attack",  2.0, C_ORANGE, "💥"),
        ]

    def get_role_icon(self): return "⚔️"

    def use_skill(self, skill_index, targets, allies):
        sk = self._skills[skill_index]
        result = {"skill": sk.name, "log": [], "particles": []}
        if sk.skill_type == "attack":
            for t in targets[:1]:
                dmg = int(self._attack * sk.power)
                actual = t.take_damage(dmg)
                result["log"].append(f"{self._name} → {t.name}: {actual} DMG")
                result["particles"].append((t, sk.color))
        elif sk.skill_type == "aoe":
            for t in targets:
                dmg = int(self._attack * sk.power)
                actual = t.take_damage(dmg)
                result["log"].append(f"{self._name} → {t.name}: {actual} DMG")
                result["particles"].append((t, sk.color))
        elif sk.skill_type == "defense":
            self._defense += 20
            result["log"].append(f"{self._name} mengaktifkan Root Shield! DEF+20")
            result["particles"].append((self, sk.color))
        return result


class Mage(Hero):
    def __init__(self, name="Flora Sorceress"):
        super().__init__(name, max_hp=110, attack=55, defense=8,
                         speed=16, color=C_PURPLE, role="Mage")
        self._skills = [
            Skill("Petal Storm",  "Sihir ke 1 musuh — damage tinggi",   "attack",  1.6, C_PURPLE,  "🌸"),
            Skill("Spore Cloud",  "Racun ke semua musuh (ATK×0.6)",      "aoe",     0.6, C_PURPLE2, "☁️"),
            Skill("Arcane Bloom", "Serangan sihir ultimate — 1 musuh",   "attack",  2.2, C_GOLD,    "✨"),
            Skill("Mystic Veil",  "Lindungi 1 ally dari 1 serangan",     "defense", 0,   C_CYAN,    "🌀"),
        ]

    def get_role_icon(self): return "🔮"

    def use_skill(self, skill_index, targets, allies):
        sk = self._skills[skill_index]
        result = {"skill": sk.name, "log": [], "particles": []}
        if sk.skill_type in ("attack", "aoe"):
            tlist = targets[:1] if sk.skill_type == "attack" else targets
            for t in tlist:
                dmg = int(self._attack * sk.power)
                actual = t.take_damage(dmg)
                result["log"].append(f"{self._name} ✨ {t.name}: {actual} DMG")
                result["particles"].append((t, sk.color))
        elif sk.skill_type == "defense":
            result["log"].append(f"{self._name} membungkus ally dengan Mystic Veil!")
            result["particles"].append((self, sk.color))
        return result


class Healer(Hero):
    def __init__(self, name="Bloom Sage"):
        super().__init__(name, max_hp=130, attack=22, defense=14,
                         speed=14, color=C_HEAL, role="Healer")
        self._skills = [
            Skill("Nature's Touch", "Pulihkan 50 HP ke 1 ally",           "heal",     50, C_HEAL,   "💚"),
            Skill("Rain of Life",   "Pulihkan 25 HP ke semua ally",       "heal_all", 25, C_GREEN,  "🌧️"),
            Skill("Thorn Whip",     "Serang 1 musuh dengan sulur",        "attack",   1.1,C_GREEN2, "🌿"),
            Skill("Revitalize",     "Pulihkan 80 HP ke ally HP terendah", "heal",     80, C_GOLD,   "⭐"),
        ]

    def get_role_icon(self): return "💚"

    def use_skill(self, skill_index, targets, allies):
        sk = self._skills[skill_index]
        result = {"skill": sk.name, "log": [], "particles": []}
        if sk.skill_type == "heal":
            target_ally = min(allies, key=lambda a: a.hp) if sk.name == "Revitalize" else random.choice(allies)
            healed = target_ally.heal(int(sk.power))
            result["log"].append(f"{self._name} 💚 {target_ally.name}: +{healed} HP")
            result["particles"].append((target_ally, sk.color))
        elif sk.skill_type == "heal_all":
            for a in allies:
                healed = a.heal(int(sk.power))
                result["log"].append(f"{self._name} 🌧️ {a.name}: +{healed} HP")
                result["particles"].append((a, sk.color))
        elif sk.skill_type == "attack":
            for t in targets[:1]:
                dmg = int(self._attack * sk.power)
                actual = t.take_damage(dmg)
                result["log"].append(f"{self._name} → {t.name}: {actual} DMG")
                result["particles"].append((t, sk.color))
        return result


class Ranger(Hero):
    def __init__(self, name="Moss Hunter"):
        super().__init__(name, max_hp=145, attack=40, defense=12,
                         speed=18, color=C_GOLD, role="Ranger")
        self._skills = [
            Skill("Seed Shot",     "Tembak 1 musuh — cepat & akurat",     "attack",  1.3, C_GOLD,   "🏹"),
            Skill("Scatter Arrow", "Tembak 2 musuh acak",                 "multi",   1.0, C_ORANGE, "🎯"),
            Skill("Camouflage",    "Hindari serangan berikutnya",          "defense", 0,   C_GREEN,  "🍃"),
            Skill("Eagle Strike",  "Tembak tepat sasaran — damage kritis","attack",  1.8, C_RED,    "🦅"),
        ]

    def get_role_icon(self): return "🏹"

    def use_skill(self, skill_index, targets, allies):
        sk = self._skills[skill_index]
        result = {"skill": sk.name, "log": [], "particles": []}
        if sk.skill_type == "attack":
            for t in targets[:1]:
                dmg = int(self._attack * sk.power)
                actual = t.take_damage(dmg)
                result["log"].append(f"{self._name} 🏹 {t.name}: {actual} DMG")
                result["particles"].append((t, sk.color))
        elif sk.skill_type == "multi":
            chosen = random.sample(targets, min(2, len(targets)))
            for t in chosen:
                dmg = int(self._attack * sk.power)
                actual = t.take_damage(dmg)
                result["log"].append(f"{self._name} 🎯 {t.name}: {actual} DMG")
                result["particles"].append((t, sk.color))
        elif sk.skill_type == "defense":
            result["log"].append(f"{self._name} bersembunyi — serangan berikutnya meleset!")
            result["particles"].append((self, sk.color))
        return result


# ══════════════════════════════════════════════════════════════════════════════
#  ENEMY CLASSES
# ══════════════════════════════════════════════════════════════════════════════

class Enemy(Character):
    def __init__(self, name, max_hp, attack, defense, speed, color, tier=1):
        super().__init__(name, max_hp, attack, defense, speed, color)
        self._tier = tier

    def get_description(self):
        return f"HP:{self._max_hp} ATK:{self._attack} DEF:{self._defense}"

    def get_role_icon(self): return "🌑"

    def ai_turn(self, heroes: list) -> dict:
        raise NotImplementedError


class Shadow(Enemy):
    def __init__(self, tier=1):
        mult = 1 + (tier - 1) * 0.35
        super().__init__(f"Shadow Lv{tier}",
                         max_hp=int(80 * mult), attack=int(28 * mult),
                         defense=int(5 * mult), speed=20,
                         color=C_PURPLE2, tier=tier)
        self._skills = [
            Skill("Dark Slash",  "Serangan cepat ke 1 hero",  "attack", 1.2, C_PURPLE2, "🗡️"),
            Skill("Void Strike", "Serangan brutal ke 1 hero", "attack", 1.8, C_RED,     "💀"),
        ]

    def get_role_icon(self): return "🌑"

    def use_skill(self, skill_index, targets, allies):
        sk = self._skills[skill_index]
        result = {"skill": sk.name, "log": [], "particles": []}
        for t in targets[:1]:
            dmg = int(self._attack * sk.power)
            actual = t.take_damage(dmg)
            result["log"].append(f"{self._name} ⚡ {t.name}: {actual} DMG")
            result["particles"].append((t, C_PURPLE2))
        return result

    def ai_turn(self, heroes):
        alive = [h for h in heroes if h.alive]
        if not alive: return {"log": [], "particles": []}
        target = min(alive, key=lambda h: h.hp)
        sk_idx = 1 if random.random() < 0.3 else 0
        return self.use_skill(sk_idx, [target], [])


class DarkMage(Enemy):
    def __init__(self, tier=1):
        mult = 1 + (tier - 1) * 0.35
        super().__init__(f"Dark Mage Lv{tier}",
                         max_hp=int(70 * mult), attack=int(38 * mult),
                         defense=int(8 * mult), speed=15,
                         color=C_RED2, tier=tier)
        self._skills = [
            Skill("Curse Bolt",    "Sihir gelap ke 1 hero",   "attack", 1.3, C_RED,  "🔥"),
            Skill("Eclipse Blast", "Sihir AOE ke semua hero", "aoe",    0.7, C_RED2, "💣"),
        ]

    def get_role_icon(self): return "☄️"

    def use_skill(self, skill_index, targets, allies):
        sk = self._skills[skill_index]
        result = {"skill": sk.name, "log": [], "particles": []}
        tlist = targets if sk.skill_type == "aoe" else targets[:1]
        for t in tlist:
            dmg = int(self._attack * sk.power)
            actual = t.take_damage(dmg)
            result["log"].append(f"{self._name} ☄️ {t.name}: {actual} DMG")
            result["particles"].append((t, C_RED))
        return result

    def ai_turn(self, heroes):
        alive = [h for h in heroes if h.alive]
        if not alive: return {"log": [], "particles": []}
        if random.random() < 0.4:
            return self.use_skill(1, alive, [])
        else:
            target = random.choice(alive)
            return self.use_skill(0, [target], [])


class BossEclipse(Enemy):
    """
    [INHERITANCE + POLYMORPHISM] Boss enemy, muncul di level 7+.
    HP dan ATK jauh lebih tinggi, punya skill khusus rage.
    """
    def __init__(self, tier=3):
        mult = 1 + (tier - 1) * 0.4
        super().__init__(f"Eclipse Lord Lv{tier}",
                         max_hp=int(200 * mult), attack=int(50 * mult),
                         defense=int(18 * mult), speed=10,
                         color=C_RED, tier=tier)
        self._skills = [
            Skill("Doom Slash",   "Tebasan gelap ke 1 hero, sangat kuat",  "attack", 1.5, C_RED,    "💢"),
            Skill("Dark Pulse",   "Gelombang AOE ke semua hero",           "aoe",    0.8, C_RED2,   "🌊"),
            Skill("Eclipse Rage", "Berserk — ATK ×1.5 turn ini",          "buff",   0,   C_PURPLE2,"😡"),
        ]
        self._raged = False

    def get_role_icon(self): return "💀"

    def use_skill(self, skill_index, targets, allies):
        sk = self._skills[skill_index]
        result = {"skill": sk.name, "log": [], "particles": []}
        if sk.skill_type == "buff":
            self._attack = int(self._attack * 1.5)
            self._raged  = True
            result["log"].append(f"{self._name} 😡 mengamuk! ATK melonjak!")
            result["particles"].append((self, C_RED))
        elif sk.skill_type == "attack":
            for t in targets[:1]:
                dmg = int(self._attack * sk.power)
                actual = t.take_damage(dmg)
                result["log"].append(f"{self._name} 💢 {t.name}: {actual} DMG")
                result["particles"].append((t, C_RED))
        elif sk.skill_type == "aoe":
            for t in targets:
                dmg = int(self._attack * sk.power)
                actual = t.take_damage(dmg)
                result["log"].append(f"{self._name} 🌊 {t.name}: {actual} DMG")
                result["particles"].append((t, C_RED2))
        return result

    def ai_turn(self, heroes):
        alive = [h for h in heroes if h.alive]
        if not alive: return {"log": [], "particles": []}
        # HP rendah → rage dulu jika belum
        hp_ratio = self._hp / self._max_hp
        if hp_ratio < 0.4 and not self._raged:
            return self.use_skill(2, alive, [])
        # Pilih AOE atau single attack
        roll = random.random()
        if roll < 0.35:
            return self.use_skill(1, alive, [])   # AOE
        else:
            target = min(alive, key=lambda h: h.hp)
            return self.use_skill(0, [target], [])


# ══════════════════════════════════════════════════════════════════════════════
#  BATTLE ENGINE
# ══════════════════════════════════════════════════════════════════════════════

class BattleEngine:
    def __init__(self, heroes: list, enemies: list):
        self.heroes  = heroes
        self.enemies = enemies
        self.turn    = 0
        self.log     = []
        self.winner  = None

    def alive_heroes(self):
        return [h for h in self.heroes if h.alive]

    def alive_enemies(self):
        return [e for e in self.enemies if e.alive]

    def add_log(self, msg):
        self.log.append(msg)
        if len(self.log) > 8:
            self.log.pop(0)

    def check_winner(self):
        if not self.alive_heroes():
            self.winner = "enemy"
        elif not self.alive_enemies():
            self.winner = "hero"

    def enemy_use_turn(self, enemy: Enemy):
        if not enemy.alive:
            return {"log": [], "particles": []}
        res = enemy.ai_turn(self.alive_heroes())
        for msg in res["log"]:
            self.add_log(msg)
        self.check_winner()
        return res

    def hero_use_skill(self, hero: Hero, skill_idx: int, targets: list):
        res = hero.use_skill(skill_idx, targets, self.alive_heroes())
        for msg in res["log"]:
            self.add_log(msg)
        self.check_winner()
        return res


# ══════════════════════════════════════════════════════════════════════════════
#  UI COMPONENTS
# ══════════════════════════════════════════════════════════════════════════════

class Button:
    def __init__(self, rect, text, color, hover_color, font=None, text_color=C_WHITE, radius=10):
        self.rect        = pygame.Rect(rect)
        self.text        = text
        self.color       = color
        self.hover_color = hover_color
        self.font        = font or F_MED
        self.text_color  = text_color
        self.radius      = radius
        self.hovered     = False

    def draw(self, surf):
        col = self.hover_color if self.hovered else self.color
        draw_rounded_rect(surf, col, self.rect, self.radius,
                          border=2, border_color=C_BORDER if not self.hovered else C_GREEN)
        draw_text_centered(surf, self.text, self.font, self.text_color,
                           self.rect.centerx, self.rect.centery)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(pos)


class HPBar:
    def __init__(self, x, y, w, h, char: Character):
        self.x = x; self.y = y; self.w = w; self.h = h
        self.char = char
        self._display_hp = char.hp

    def update(self):
        self._display_hp += (self.char.hp - self._display_hp) * 0.12

    def draw(self, surf):
        ratio = max(0, self._display_hp / self.char.max_hp)
        draw_rounded_rect(surf, C_GRAY2, (self.x, self.y, self.w, self.h), 4)
        if ratio > 0.6:
            col = C_GREEN
        elif ratio > 0.3:
            col = C_GOLD
        else:
            col = C_RED
        fill_w = int(self.w * ratio)
        if fill_w > 0:
            draw_rounded_rect(surf, col, (self.x, self.y, fill_w, self.h), 4)
        pygame.draw.rect(surf, C_BORDER, (self.x, self.y, self.w, self.h), 1, border_radius=4)
        hp_text = F_TINY.render(f"{int(self._display_hp)}/{self.char.max_hp}", True, C_WHITE)
        surf.blit(hp_text, (self.x + self.w // 2 - hp_text.get_width() // 2,
                             self.y + self.h // 2 - hp_text.get_height() // 2))


# ══════════════════════════════════════════════════════════════════════════════
#  LEVEL UP SCREEN — Transisi setelah menang
# ══════════════════════════════════════════════════════════════════════════════

class LevelUpScreen:
    """
    Layar transisi setelah hero menang satu level.
    Menampilkan:
      - Level yang baru saja dilewati
      - HP yang dipulihkan per hero
      - Preview kesulitan level berikutnya
      - Tombol lanjut ke level berikutnya
    """
    def __init__(self, level_system: LevelSystem, heroes: list, heal_log: list):
        self.level_system = level_system
        self.heroes    = heroes
        self.heal_log  = heal_log          # list string dari heal reward
        self.tick      = 0
        self.continue_btn = Button(
            (SCREEN_W // 2 - 160, SCREEN_H - 110, 320, 56),
            "⚔️  LANJUT KE LEVEL BERIKUTNYA", C_GREEN2, C_GREEN, F_BIG
        )
        self.menu_btn = Button(
            (SCREEN_W // 2 - 100, SCREEN_H - 46, 200, 34),
            "↩ Kembali ke Menu", C_PANEL2, C_PANEL, F_SMALL
        )
        # Spawn celebration particles
        for _ in range(30):
            x = random.randint(100, SCREEN_W - 100)
            y = random.randint(100, SCREEN_H - 100)
            spawn_particles(x, y, random.choice([C_GREEN, C_GOLD, C_CYAN]), count=3)

    def update(self, events):
        self.tick += 1
        mx, my = pygame.mouse.get_pos()
        self.continue_btn.check_hover((mx, my))
        self.menu_btn.check_hover((mx, my))
        # Terus spawn partikel kecil
        if self.tick % 15 == 0:
            x = random.randint(60, SCREEN_W - 60)
            spawn_particles(x, SCREEN_H // 2, C_GREEN, count=4, spread=40)
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if self.continue_btn.is_clicked((mx, my), e):
                return "battle_next"
            if self.menu_btn.is_clicked((mx, my), e):
                return "menu"
        return "level_up"

    def draw(self):
        screen.fill(C_BG)

        # Judul
        glow = abs(math.sin(self.tick * 0.05))
        title_col = lerp_color(C_GREEN, C_GOLD, glow)
        draw_text_centered(screen, "🌿 LEVEL CLEAR! 🌿", F_TITLE, title_col, SCREEN_W // 2, 70)

        prev_level = self.level_system.current_level - 1
        draw_text_centered(screen, f"Level {prev_level} Selesai!", F_BIG, C_WHITE, SCREEN_W // 2, 130)

        # Panel info level berikutnya
        next_lv = self.level_system.current_level
        panel = pygame.Rect(SCREEN_W // 2 - 280, 165, 560, 115)
        draw_rounded_rect(screen, C_PANEL, panel, 14, border=2, border_color=C_GOLD)
        draw_text_centered(screen, f"Level Berikutnya: {next_lv}  |  {self.level_system.level_label()}",
                           F_MED, C_GOLD, SCREEN_W // 2, 190)
        draw_text_centered(screen, f"Kesulitan: {self.level_system.difficulty_stars()}",
                           F_MED, C_WHITE, SCREEN_W // 2, 218)
        draw_text_centered(screen,
                           f"Musuh: {self.level_system.enemy_count} unit  |  Tier {self.level_system.tier}",
                           F_SMALL, C_GRAY, SCREEN_W // 2, 246)
        draw_text_centered(screen, f"Heal reward: {int(self.level_system.heal_percent * 100)}% Max HP",
                           F_SMALL, C_CYAN, SCREEN_W // 2, 268)

        # Panel HP hero setelah heal
        hp_panel = pygame.Rect(SCREEN_W // 2 - 280, 295, 560, 50 + len(self.heroes) * 34)
        draw_rounded_rect(screen, C_PANEL, hp_panel, 14, border=2, border_color=C_GREEN)
        draw_text_centered(screen, "Status Tim Setelah Heal Reward:", F_SMALL, C_GREEN,
                           SCREEN_W // 2, 315)
        for i, hero in enumerate(self.heroes):
            y = 340 + i * 34
            status = f"{hero.get_role_icon()}  {hero.name}  —  HP: {hero.hp} / {hero.max_hp}"
            col = C_GREEN if hero.alive else C_GRAY
            if not hero.alive:
                status += "  (K.O.)"
            draw_text_centered(screen, status, F_SMALL, col, SCREEN_W // 2, y)

        update_particles(screen)
        self.continue_btn.draw(screen)
        self.menu_btn.draw(screen)


class GameClearScreen:
    """Layar khusus jika player berhasil clear semua 12 level."""
    def __init__(self):
        self.tick = 0
        self.back_btn = Button((SCREEN_W // 2 - 120, SCREEN_H - 80, 240, 50),
                               "↩ Kembali ke Menu", C_GREEN2, C_GREEN, F_BIG)

    def update(self, events):
        self.tick += 1
        mx, my = pygame.mouse.get_pos()
        self.back_btn.check_hover((mx, my))
        if self.tick % 8 == 0:
            x = random.randint(50, SCREEN_W - 50)
            spawn_particles(x, random.randint(100, SCREEN_H - 100),
                            random.choice([C_GREEN, C_GOLD, C_CYAN, C_PURPLE]), count=5)
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if self.back_btn.is_clicked((mx, my), e):
                return "menu"
        return "game_clear"

    def draw(self):
        screen.fill(C_BG)
        glow = abs(math.sin(self.tick * 0.04))
        col1 = lerp_color(C_GOLD, C_GREEN, glow)
        draw_text_centered(screen, "✨ MONSTERA ECLIPSE ✨", F_TITLE, col1, SCREEN_W // 2, 120)
        draw_text_centered(screen, "GAME CLEAR!", F_TITLE, C_GOLD, SCREEN_W // 2, 210)
        draw_text_centered(screen, "Semua 12 level telah ditaklukkan!", F_BIG, C_WHITE, SCREEN_W // 2, 290)
        draw_text_centered(screen, "Alam Monstera kembali bersinar abadi.", F_MED, C_GREEN, SCREEN_W // 2, 340)
        draw_text_centered(screen, "🌿 Terima kasih sudah bermain! 🌿", F_MED, C_CYAN, SCREEN_W // 2, 390)
        update_particles(screen)
        self.back_btn.draw(screen)


# ══════════════════════════════════════════════════════════════════════════════
#  GAME SCREENS
# ══════════════════════════════════════════════════════════════════════════════

def get_character_asset_key(char):
    if isinstance(char, Warrior):    return "warrior"
    if isinstance(char, Mage):       return "mage"
    if isinstance(char, Healer):     return "healer"
    if isinstance(char, Ranger):     return "ranger"
    if isinstance(char, Shadow):     return "shadow"
    if isinstance(char, DarkMage):   return "dark_mage"
    if isinstance(char, BossEclipse): return "boss_eclipse"
    return None


def draw_character_sprite_or_icon(surf, char, center, size, fallback_font, flip=False):
    key = get_character_asset_key(char)
    if key and asset_manager.draw_sprite(surf, key, center, size=size, flip=flip):
        return
    draw_text_centered(surf, char.get_role_icon(), fallback_font, char.color, center[0], center[1])


class MenuScreen:
    def __init__(self):
        self.tick = 0
        self.buttons = [
            Button((SCREEN_W // 2 - 130, 330, 260, 52), "START GAME", C_GREEN2, C_GREEN, F_BIG),
            Button((SCREEN_W // 2 - 130, 400, 260, 52), "SETTINGS",   C_PANEL2, C_PANEL, F_BIG),
            Button((SCREEN_W // 2 - 130, 470, 260, 52), "EXIT",        C_RED2,   C_RED,   F_BIG),
        ]
        self.orbs = [(random.randint(50, SCREEN_W - 50),
                      random.randint(50, SCREEN_H - 50),
                      random.uniform(0, math.pi * 2),
                      random.uniform(0.5, 2),
                      random.choice([C_GREEN, C_PURPLE, C_GOLD, C_CYAN])) for _ in range(18)]

    def update(self, events):
        self.tick += 1
        mx, my = pygame.mouse.get_pos()
        for b in self.buttons:
            b.check_hover((mx, my))
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            for i, b in enumerate(self.buttons):
                if b.is_clicked((mx, my), e):
                    if i == 0: return "select_party"
                    if i == 1: return "settings"
                    if i == 2: pygame.quit(); sys.exit()
        return "menu"

    def draw(self):
        screen.fill(C_BG)
        for ox, oy, phase, spd, col in self.orbs:
            x = ox + math.sin(self.tick * 0.01 * spd + phase) * 30
            y = oy + math.cos(self.tick * 0.008 * spd + phase) * 20
            alpha_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surf, (*col, 60), (10, 10), 10)
            screen.blit(alpha_surf, (int(x) - 10, int(y) - 10))
        glow = abs(math.sin(self.tick * 0.04))
        title_col = lerp_color(C_GREEN, C_CYAN, glow)
        draw_text_centered(screen, "MONSTERA", F_TITLE, title_col, SCREEN_W // 2, 170)
        draw_text_centered(screen, "ECLIPSE",  F_TITLE, lerp_color(C_PURPLE, C_RED, glow), SCREEN_W // 2, 240)
        draw_text_centered(screen, "⚔️ Turn-Based RPG ⚔️", F_SMALL, C_GRAY, SCREEN_W // 2, 295)
        for b in self.buttons:
            b.draw(screen)
        draw_text_centered(screen, "© Monstera Eclipse Team", F_TINY, C_GRAY2, SCREEN_W // 2, SCREEN_H - 20)


class SettingsScreen:
    def __init__(self, music_on):
        self.music_on = music_on
        self.back_btn  = Button((30, 30, 120, 40), "← Back", C_PANEL2, C_PANEL, F_SMALL)
        self.music_btn = Button((SCREEN_W // 2 - 130, 280, 260, 52),
                                 "🔊 Music: ON" if music_on else "🔇 Music: OFF",
                                 C_GREEN2 if music_on else C_GRAY2, C_GREEN, F_MED)

    def update(self, events):
        mx, my = pygame.mouse.get_pos()
        self.back_btn.check_hover((mx, my))
        self.music_btn.check_hover((mx, my))
        for e in events:
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if self.back_btn.is_clicked((mx, my), e):
                return "menu", self.music_on
            if self.music_btn.is_clicked((mx, my), e):
                self.music_on = not self.music_on
                self.music_btn.text  = "🔊 Music: ON" if self.music_on else "🔇 Music: OFF"
                self.music_btn.color = C_GREEN2 if self.music_on else C_GRAY2
        return "settings", self.music_on

    def draw(self):
        screen.fill(C_BG)
        draw_text_centered(screen, "⚙️  SETTINGS", F_BIG, C_WHITE, SCREEN_W // 2, 120)
        draw_rounded_rect(screen, C_PANEL, (SCREEN_W // 2 - 200, 220, 400, 200), 16,
                          border=2, border_color=C_BORDER)
        draw_text_centered(screen, "Background Music", F_MED, C_GRAY, SCREEN_W // 2, 255)
        self.music_btn.draw(screen)
        draw_text_centered(screen, "Controls: Mouse + Click to play", F_SMALL, C_GRAY, SCREEN_W // 2, 370)
        self.back_btn.draw(screen)


class PartySelectScreen:
    HERO_CLASSES = [Warrior, Mage, Healer, Ranger]
    HERO_NAMES   = ["Verdant Knight", "Flora Sorceress", "Bloom Sage", "Moss Hunter"]
    HERO_ROLES   = ["Warrior ⚔️", "Mage 🔮", "Healer 💚", "Ranger 🏹"]
    HERO_DESCS   = [
        ["HP: 180 (Tinggi)", "ATK: 35 | DEF: 20", "SPD: 12 — Tank tangguh", "Skill AoE & Shield"],
        ["HP: 110 (Rendah)", "ATK: 55 | DEF: 8",  "SPD: 16 — Glass Cannon", "Skill burst damage"],
        ["HP: 130 (Medium)", "ATK: 22 | DEF: 14", "SPD: 14 — Support",      "Heal tim & serangan"],
        ["HP: 145 (Medium)", "ATK: 40 | DEF: 12", "SPD: 18 — Tercepat",     "Serangan ganda/kritis"],
    ]
    HERO_COLORS  = [C_GREEN, C_PURPLE, C_HEAL, C_GOLD]

    def __init__(self):
        self.selected  = set(range(4))
        self.hovered   = -1
        self.start_btn = Button((SCREEN_W // 2 - 140, SCREEN_H - 70, 280, 48),
                                 "⚔️  START BATTLE", C_GREEN2, C_GREEN, F_BIG)
        self.back_btn  = Button((30, 30, 120, 40), "← Back", C_PANEL2, C_PANEL, F_SMALL)
        self.card_rects = []
        cw, ch = 220, 280
        gap    = 24
        total_w = 4 * cw + 3 * gap
        sx = (SCREEN_W - total_w) // 2
        for i in range(4):
            self.card_rects.append(pygame.Rect(sx + i * (cw + gap), 130, cw, ch))

    def update(self, events):
        mx, my = pygame.mouse.get_pos()
        self.start_btn.check_hover((mx, my))
        self.back_btn.check_hover((mx, my))
        self.hovered = -1
        for i, r in enumerate(self.card_rects):
            if r.collidepoint(mx, my):
                self.hovered = i
        for e in events:
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if self.back_btn.is_clicked((mx, my), e): return "menu", []
            if e.type == pygame.MOUSEBUTTONDOWN:
                for i, r in enumerate(self.card_rects):
                    if r.collidepoint(mx, my):
                        if i in self.selected:
                            self.selected.discard(i)
                        elif len(self.selected) < 4:
                            self.selected.add(i)
            if self.start_btn.is_clicked((mx, my), e):
                if len(self.selected) == 4:
                    heroes = [self.HERO_CLASSES[i]() for i in sorted(self.selected)]
                    return "battle", heroes
        return "select_party", []

    def draw(self):
        screen.fill(C_BG)
        draw_text_centered(screen, "🌿 TIM HERO (4 ROLE)", F_BIG, C_WHITE, SCREEN_W // 2, 55)
        draw_text_centered(screen, f"Dipilih: {len(self.selected)}/4 — Warrior, Mage, Healer, Ranger", F_MED,
                           C_GREEN if len(self.selected) == 4 else C_GRAY, SCREEN_W // 2, 95)
        for i, (r, cls) in enumerate(zip(self.card_rects, self.HERO_CLASSES)):
            sel = i in self.selected
            hov = i == self.hovered
            bg  = C_PANEL2 if not sel else (20, 55, 35)
            border_col = self.HERO_COLORS[i] if sel else (C_BORDER if not hov else C_WHITE)
            draw_rounded_rect(screen, bg, r, 16, border=2 if not sel else 3, border_color=border_col)
            cx = r.centerx
            asset_key = ["warrior", "mage", "healer", "ranger"][i]
            if not asset_manager.draw_sprite(screen, asset_key, (cx, r.y + 48), size=(76, 76)):
                icon = F_TITLE.render(["⚔️", "🔮", "💚", "🏹"][i], True, self.HERO_COLORS[i])
                screen.blit(icon, (cx - icon.get_width() // 2, r.y + 12))
            draw_text_centered(screen, self.HERO_ROLES[i], F_MED, self.HERO_COLORS[i], cx, r.y + 90)
            draw_text_centered(screen, self.HERO_NAMES[i], F_SMALL, C_WHITE, cx, r.y + 118)
            for j, desc in enumerate(self.HERO_DESCS[i]):
                draw_text_centered(screen, desc, F_TINY, C_GRAY, cx, r.y + 146 + j * 22)
            if sel:
                draw_text_centered(screen, "✔ DIPILIH", F_SMALL, C_GREEN, cx, r.bottom - 22)
        if len(self.selected) == 4:
            self.start_btn.draw(screen)
        else:
            draw_rounded_rect(screen, C_GRAY2, (SCREEN_W // 2 - 140, SCREEN_H - 70, 280, 48), 10)
            draw_text_centered(screen, "Tim harus berisi 4 hero", F_MED, C_GRAY, SCREEN_W // 2, SCREEN_H - 46)
        self.back_btn.draw(screen)


# ══════════════════════════════════════════════════════════════════════════════
#  BATTLE SCREEN — dengan level_system
# ══════════════════════════════════════════════════════════════════════════════

class BattleScreen:
    """
    Battle screen yang sekarang menerima LevelSystem.
    Setelah menang → kirim sinyal ke main loop untuk ke LevelUpScreen.
    Setelah kalah  → kirim sinyal ke menu.
    """
    def __init__(self, heroes: list, level_system: LevelSystem):
        self.heroes       = heroes
        self.level_system = level_system
        self.enemies      = level_system.generate_enemies()
        self.engine       = BattleEngine(self.heroes, self.enemies)
        self.hp_bars_h    = {h: HPBar(0, 0, 140, 14, h) for h in heroes}
        self.hp_bars_e    = {e: HPBar(0, 0, 120, 12, e) for e in self.enemies}

        self.phase              = "player_turn"
        self.selected_hero_idx  = 0
        self.selected_enemy_idx = 0
        self.anim_timer         = 0
        self.anim_result        = None
        self.turn_label         = ""
        self.tick               = 0

        self.acted_heroes      = set()
        self.enemy_turn_index  = 0
        self.last_actor        = None

        # ── Charge animation (Warrior maju ke musuh) ──────────────────────
        # anim_charge_hero  : hero yang sedang charge
        # anim_charge_target: center (x,y) musuh tujuan
        # anim_charge_phase : "charge" | "hold" | "return" | None
        # anim_charge_timer : frame counter per sub-phase
        # anim_hero_offset  : dict {hero_index: (offset_x, offset_y)}
        self.anim_charge_hero   = None
        self.anim_charge_target = None
        self.anim_charge_phase  = None
        self.anim_charge_timer  = 0
        self.anim_hero_offset   = {}   # {hero_index: (ox, oy)}

        self.hero_rects  = []
        self.enemy_rects = []
        self.skill_btns  = []
        self._build_layout()
        self._select_next_available_hero()

    def _gen_enemies(self):
        # Tidak dipakai langsung, delegate ke level_system
        return self.level_system.generate_enemies()

    def _build_layout(self):
        hw, hh = 160, 110
        gap = 14
        sx  = 30
        for i in range(len(self.heroes)):
            self.hero_rects.append(pygame.Rect(sx + i * (hw + gap), SCREEN_H - hh - 14, hw, hh))

        ew, eh   = 150, 100
        ex_start = SCREEN_W - (len(self.enemies) * (ew + gap)) - 20
        for i in range(len(self.enemies)):
            self.enemy_rects.append(pygame.Rect(ex_start + i * (ew + gap), 14, ew, eh))

    def _available_heroes(self):
        return [h for h in self.heroes if h.alive and h not in self.acted_heroes]

    def _select_next_available_hero(self):
        available = self._available_heroes()
        if not available:
            self.acted_heroes.clear()
            available = self._available_heroes()
            self.engine.turn += 1
        if not available:
            return
        hero = available[0]
        self.selected_hero_idx = self.heroes.index(hero)
        self._build_skill_buttons(hero)

    def _select_hero_by_index(self, idx):
        if idx < 0 or idx >= len(self.heroes):
            return
        hero = self.heroes[idx]
        if not hero.alive:
            self.engine.add_log(f"{hero.name} sudah kalah.")
            return
        if hero in self.acted_heroes:
            self.engine.add_log(f"{hero.name} sudah menyerang ronde ini.")
            return
        self.selected_hero_idx = idx
        self._build_skill_buttons(hero)

    def _select_enemy_by_index(self, idx):
        if idx < 0 or idx >= len(self.enemies):
            return
        if self.enemies[idx].alive:
            self.selected_enemy_idx = idx

    def _current_hero(self):
        if not self.heroes:
            return None
        hero = self.heroes[self.selected_hero_idx]
        if hero.alive and hero not in self.acted_heroes:
            return hero
        self._select_next_available_hero()
        return self.heroes[self.selected_hero_idx] if self.heroes else None

    def _current_target_enemy(self):
        alive = self.engine.alive_enemies()
        if not alive:
            return None
        if self.selected_enemy_idx >= len(self.enemies) or not self.enemies[self.selected_enemy_idx].alive:
            self.selected_enemy_idx = self.enemies.index(alive[0])
        return self.enemies[self.selected_enemy_idx]

    def _build_skill_buttons(self, hero):
        self.skill_btns = []
        bw, bh = 190, 42
        sx = SCREEN_W // 2 - (2 * bw + 10) // 2
        for i, sk in enumerate(hero.skills):
            col_map = {"attack": C_RED2, "defense": C_BLUE, "heal": C_GREEN2,
                       "heal_all": C_GREEN2, "aoe": C_PURPLE2, "multi": C_ORANGE}
            col = col_map.get(sk.skill_type, C_PANEL2)
            row, col_pos = divmod(i, 2)
            btn = Button((sx + col_pos * (bw + 10), SCREEN_H - 240 + row * (bh + 8), bw, bh),
                          f"{sk.icon} {sk.name}", col, lerp_color(col, C_WHITE, 0.2), F_SMALL)
            self.skill_btns.append(btn)

    def update(self, events):
        self.tick += 1
        mx, my = pygame.mouse.get_pos()

        for bar in self.hp_bars_h.values(): bar.update()
        for bar in self.hp_bars_e.values(): bar.update()

        if self.engine.winner:
            self.phase = "result"

        if self.phase == "anim":
            self.anim_timer -= 1

            # ── Update charge animation offset ───────────────────────────
            self._update_charge_anim()

            if self.anim_timer <= 0:
                if self.turn_label == "player":
                    self._do_one_enemy_turn()
                else:
                    self.phase = "player_turn"
                    self._select_next_available_hero()
            return "battle"

        if self.phase == "result":
            for e in events:
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if self.engine.winner == "hero":
                        # Terapkan heal reward lalu pindah ke LevelUpScreen
                        return "hero_win"
                    else:
                        return "menu"
            return "battle"

        if self.phase == "player_turn":
            hero = self._current_hero()
            if hero:
                for btn in self.skill_btns:
                    btn.check_hover((mx, my))

            for e in events:
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()

                if e.type == pygame.KEYDOWN:
                    available = self._available_heroes()
                    if available and hero in available:
                        current_pos = available.index(hero)
                        if e.key in (pygame.K_LEFT, pygame.K_a):
                            next_hero = available[(current_pos - 1) % len(available)]
                            self._select_hero_by_index(self.heroes.index(next_hero))
                        if e.key in (pygame.K_RIGHT, pygame.K_d):
                            next_hero = available[(current_pos + 1) % len(available)]
                            self._select_hero_by_index(self.heroes.index(next_hero))

                if e.type == pygame.MOUSEBUTTONDOWN:
                    for i, r in enumerate(self.hero_rects):
                        if r.collidepoint(mx, my):
                            self._select_hero_by_index(i)
                    for i, r in enumerate(self.enemy_rects):
                        if r.collidepoint(mx, my):
                            self._select_enemy_by_index(i)

                for i, btn in enumerate(self.skill_btns):
                    if btn.is_clicked((mx, my), e):
                        self._use_hero_skill(i)

        return "battle"

    def _use_hero_skill(self, skill_idx):
        hero = self._current_hero()
        alive_enemies = self.engine.alive_enemies()
        alive_heroes  = self.engine.alive_heroes()
        if not hero or not alive_enemies or hero in self.acted_heroes:
            return

        sk = hero.skills[skill_idx]
        target_enemy = self._current_target_enemy()

        if sk.skill_type in ("heal", "heal_all", "defense"):
            targets = alive_heroes
        elif sk.skill_type in ("aoe", "multi"):
            targets = alive_enemies
        else:
            targets = [target_enemy] if target_enemy else alive_enemies[:1]

        result = self.engine.hero_use_skill(hero, skill_idx, targets)
        self.acted_heroes.add(hero)
        self.last_actor = hero
        for char, col in result.get("particles", []):
            pos = self._get_char_center(char)
            spawn_particles(pos[0], pos[1], col, count=20)
        self.anim_result = result
        self.anim_timer  = 45
        self.turn_label  = "player"
        self.phase       = "anim"

        # ── Charge animation: Warrior maju ke musuh saat attack/aoe ──────
        hero_idx = self.heroes.index(hero)
        if isinstance(hero, Warrior) and sk.skill_type in ("attack", "aoe"):
            # Hitung target posisi: tengah musuh (atau rata-rata semua musuh jika AOE)
            if sk.skill_type == "aoe" and self.enemy_rects:
                alive_rects = [self.enemy_rects[i] for i, e in enumerate(self.enemies)
                               if e.alive and i < len(self.enemy_rects)]
                if alive_rects:
                    avg_x = sum(r.centerx for r in alive_rects) // len(alive_rects)
                    avg_y = sum(r.centery for r in alive_rects) // len(alive_rects)
                    target_center = (avg_x, avg_y)
                else:
                    target_center = (SCREEN_W // 2, SCREEN_H // 2)
            else:
                t_idx = self.selected_enemy_idx
                if t_idx < len(self.enemy_rects):
                    target_center = self.enemy_rects[t_idx].center
                else:
                    target_center = (SCREEN_W // 2, SCREEN_H // 2)

            self.anim_charge_hero   = hero_idx
            self.anim_charge_target = target_center
            self.anim_charge_phase  = "charge"
            self.anim_charge_timer  = 0
            self.anim_hero_offset[hero_idx] = (0, 0)
            # Extend anim_timer supaya cukup untuk animasi charge penuh
            self.anim_timer = 55

    def _update_charge_anim(self):
        """
        Update offset posisi Warrior saat animasi charge ke musuh.

        Timeline (total ~55 frame):
          charge  : frame 0–14  → maju cepat ke arah musuh
          hold    : frame 15–24 → diam sejenak di posisi musuh (impact!)
          return  : frame 25–54 → balik ke posisi asal secara smooth
        """
        if self.anim_charge_phase is None or self.anim_charge_hero is None:
            return

        hidx = self.anim_charge_hero
        if hidx >= len(self.hero_rects):
            self._reset_charge_anim()
            return

        home_center = self.hero_rects[hidx].center        # posisi asal hero
        tx, ty      = self.anim_charge_target             # posisi target musuh

        # Vektor dari home ke target (pendek sedikit supaya tidak numpuk di atas musuh)
        dx = tx - home_center[0]
        dy = ty - home_center[1]
        dist = math.hypot(dx, dy) or 1
        # Maju sejauh 70% jarak supaya berhenti di depan musuh, bukan di atasnya
        reach_x = int(dx * 0.70)
        reach_y = int(dy * 0.70)

        self.anim_charge_timer += 1
        t = self.anim_charge_timer

        if self.anim_charge_phase == "charge":
            # Easing out: mulai cepat, melambat saat hampir sampai
            progress = min(1.0, t / 15)
            ease     = 1 - (1 - progress) ** 2   # ease-out quad
            ox = int(reach_x * ease)
            oy = int(reach_y * ease)
            self.anim_hero_offset[hidx] = (ox, oy)
            if t >= 15:
                self.anim_charge_phase  = "hold"
                self.anim_charge_timer  = 0

        elif self.anim_charge_phase == "hold":
            # Diam di posisi impact — efek shake kecil
            shake = int(math.sin(t * 1.8) * 3)
            self.anim_hero_offset[hidx] = (reach_x + shake, reach_y)
            if t >= 10:
                self.anim_charge_phase  = "return"
                self.anim_charge_timer  = 0

        elif self.anim_charge_phase == "return":
            # Ease-in kembali ke posisi asal
            progress = min(1.0, t / 20)
            ease     = progress ** 2             # ease-in quad (lambat dulu, lalu cepat)
            ox = int(reach_x * (1 - ease))
            oy = int(reach_y * (1 - ease))
            self.anim_hero_offset[hidx] = (ox, oy)
            if t >= 20:
                self._reset_charge_anim()

    def _reset_charge_anim(self):
        """Bersihkan semua state charge animation."""
        if self.anim_charge_hero is not None:
            self.anim_hero_offset.pop(self.anim_charge_hero, None)
        self.anim_charge_hero   = None
        self.anim_charge_target = None
        self.anim_charge_phase  = None
        self.anim_charge_timer  = 0

    def _do_one_enemy_turn(self):
        if self.engine.winner:
            self.phase = "result"
            return

        alive_enemies = self.engine.alive_enemies()
        if not alive_enemies:
            self.phase = "result"
            return

        if self.enemy_turn_index >= len(self.enemies):
            self.enemy_turn_index = 0

        enemy   = None
        checked = 0
        while checked < len(self.enemies):
            cand = self.enemies[self.enemy_turn_index]
            self.enemy_turn_index = (self.enemy_turn_index + 1) % len(self.enemies)
            checked += 1
            if cand.alive:
                enemy = cand
                break

        if enemy is None:
            self.phase = "result"
            return

        result = self.engine.enemy_use_turn(enemy)
        self.last_actor = enemy
        for char, col in result.get("particles", []):
            pos = self._get_char_center(char)
            spawn_particles(pos[0], pos[1], col, count=18)
        self.anim_timer = 45
        self.turn_label = "enemy"
        self.phase      = "anim"
        if self.engine.winner:
            self.phase = "result"

    def _get_char_center(self, char):
        for i, h in enumerate(self.heroes):
            if h is char and i < len(self.hero_rects):
                return self.hero_rects[i].center
        for i, e in enumerate(self.enemies):
            if e is char and i < len(self.enemy_rects):
                return self.enemy_rects[i].center
        return (SCREEN_W // 2, SCREEN_H // 2)

    def draw(self):
        screen.fill(C_BG)
        self._draw_bg_effects()
        self._draw_level_badge()    # ← baru: tampilkan badge level
        self._draw_enemies()
        self._draw_heroes()
        self._draw_battle_log()
        self._draw_skills()
        self._draw_turn_info()
        update_particles(screen)
        if self.phase == "result":
            self._draw_result()

    def _draw_level_badge(self):
        """Tampilkan level saat ini dan difficulty stars di pojok kiri atas."""
        lv = self.level_system.current_level
        stars = self.level_system.difficulty_stars()
        label = self.level_system.level_label()
        badge_rect = pygame.Rect(8, 55, 180, 52)
        draw_rounded_rect(screen, C_PANEL, badge_rect, 10, border=2, border_color=C_GOLD)
        draw_text(screen, f"Level {lv}  {label}", F_SMALL, C_GOLD, 16, 63)
        draw_text(screen, stars, F_TINY, C_WHITE, 16, 85)

    def _draw_bg_effects(self):
        for x in range(0, SCREEN_W, 60):
            pygame.draw.line(screen, (15, 22, 35), (x, 0), (x, SCREEN_H))
        for y in range(0, SCREEN_H, 60):
            pygame.draw.line(screen, (15, 22, 35), (0, y), (SCREEN_W, y))
        glow_r = 180 + int(math.sin(self.tick * 0.03) * 20)
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        for r in range(glow_r, 0, -20):
            a = int(8 * (r / glow_r))
            pygame.draw.circle(glow_surf, (80, 20, 100, a), (glow_r, glow_r), r)
        screen.blit(glow_surf, (SCREEN_W // 2 - glow_r, SCREEN_H // 2 - glow_r - 80))

    def _draw_enemies(self):
        for i, (enemy, rect) in enumerate(zip(self.enemies, self.enemy_rects)):
            selected = (i == self.selected_enemy_idx and enemy.alive and self.phase == "player_turn")
            if not enemy.alive:
                draw_rounded_rect(screen, (12, 12, 16), rect, 12, border=1, border_color=C_GRAY2)
                draw_text_centered(screen, "💀 DEFEATED", F_TINY, C_GRAY, rect.centerx, rect.centery)
                continue
            border = C_GOLD if selected else C_BORDER2
            draw_rounded_rect(screen, C_SHADOW_E, rect, 12, border=3 if selected else 2, border_color=border)
            if selected:
                draw_text_centered(screen, "▼ TARGET", F_TINY, C_GOLD, rect.centerx, rect.bottom + 12)
            if self.last_actor is enemy:
                draw_text_centered(screen, "ACTION", F_TINY, C_RED, rect.centerx, rect.top - 10)
            draw_character_sprite_or_icon(screen, enemy, (rect.centerx, rect.y + 30), (56, 56), F_BIG, flip=True)
            draw_text_centered(screen, enemy.name, F_TINY, C_WHITE, rect.centerx, rect.y + 58)
            bar = self.hp_bars_e[enemy]
            bar.x = rect.x + 8; bar.y = rect.y + 70; bar.w = rect.w - 16; bar.h = 14
            bar.draw(screen)
            draw_text_centered(screen, f"ATK:{enemy.attack} DEF:{enemy.defense}", F_TINY, C_GRAY, rect.centerx, rect.y + 90)

    def _draw_heroes(self):
        for i, (hero, rect) in enumerate(zip(self.heroes, self.hero_rects)):
            is_selected   = (i == self.selected_hero_idx and self.phase == "player_turn"
                             and hero.alive and hero not in self.acted_heroes)
            already_acted = hero in self.acted_heroes

            # Ambil charge offset jika ada (untuk animasi Warrior maju)
            ox, oy = self.anim_hero_offset.get(i, (0, 0))

            if not hero.alive:
                draw_rounded_rect(screen, (12, 12, 16), rect, 12, border=1, border_color=C_GRAY2)
                draw_text_centered(screen, "💀", F_MED, C_GRAY, rect.centerx, rect.centery)
                draw_text_centered(screen, "K.O.", F_TINY, C_GRAY, rect.centerx, rect.centery + 24)
                continue

            bg_c     = (18, 22, 28) if already_acted else ((15, 35, 20) if is_selected else C_PANEL)
            border_c = C_GRAY2 if already_acted else (hero.color if is_selected else C_BORDER)
            draw_rounded_rect(screen, bg_c, rect, 12, border=3 if is_selected else 2, border_color=border_c)

            if is_selected:
                glow  = abs(math.sin(self.tick * 0.08))
                g_surf = pygame.Surface((rect.w + 20, rect.h + 20), pygame.SRCALPHA)
                pygame.draw.rect(g_surf, (*hero.color, int(40 * glow)),
                                 (0, 0, rect.w + 20, rect.h + 20), border_radius=14)
                screen.blit(g_surf, (rect.x - 10, rect.y - 10))

            # ── Sprite: tambahkan offset charge jika warrior sedang charge ──
            sprite_cx = rect.centerx + ox
            sprite_cy = rect.y + 30 + oy

            # Efek motion blur tipis saat charge (overlay transparan di posisi sebelumnya)
            if ox != 0 or oy != 0:
                blur_surf = pygame.Surface((58, 58), pygame.SRCALPHA)
                blur_surf.set_alpha(55)
                draw_character_sprite_or_icon(blur_surf, hero,
                                              (29, 29), (58, 58), F_MED)
                screen.blit(blur_surf,
                            (sprite_cx - 29 - ox // 3, sprite_cy - 29 - oy // 3))

            draw_character_sprite_or_icon(screen, hero, (sprite_cx, sprite_cy), (58, 58), F_MED)

            col_name = C_WHITE if not already_acted else C_GRAY
            draw_text_centered(screen, hero.name, F_TINY, col_name, rect.centerx, rect.y + 58)
            draw_text_centered(screen, hero.role, F_TINY, hero.color if not already_acted else C_GRAY,
                               rect.centerx, rect.y + 72)
            bar = self.hp_bars_h[hero]
            bar.x = rect.x + 8; bar.y = rect.y + 84; bar.w = rect.w - 16; bar.h = 14
            bar.draw(screen)
            draw_text_centered(screen, f"ATK:{hero.attack} DEF:{hero.defense}", F_TINY, C_GRAY,
                               rect.centerx, rect.y + 104)

            if is_selected:
                draw_text_centered(screen, "▲ ACTIVE", F_TINY, C_GREEN, rect.centerx, rect.top - 12)
            elif already_acted:
                draw_text_centered(screen, "DONE", F_TINY, C_GRAY, rect.centerx, rect.top - 12)

    def _draw_battle_log(self):
        lx, ly, lw, lh = SCREEN_W - 310, 130, 290, 200
        draw_rounded_rect(screen, C_PANEL, (lx, ly, lw, lh), 12, border=1, border_color=C_BORDER)
        draw_text(screen, "📜 Battle Log", F_TINY, C_GOLD, lx + 10, ly + 8)
        for i, msg in enumerate(self.engine.log[-7:]):
            col = C_WHITE if i == len(self.engine.log[-7:]) - 1 else C_GRAY
            txt = F_TINY.render(msg[:40], True, col)
            screen.blit(txt, (lx + 8, ly + 28 + i * 22))

    def _draw_skills(self):
        if self.phase != "player_turn": return
        hero = self._current_hero()
        if not hero: return
        panel_rect = (SCREEN_W // 2 - 230, SCREEN_H - 260, 460, 145)
        draw_rounded_rect(screen, C_PANEL, panel_rect, 14, border=1, border_color=C_BORDER)
        draw_text_centered(screen, f"Pilih Skill — {hero.name} ({hero.role})", F_SMALL, hero.color,
                           SCREEN_W // 2, SCREEN_H - 250)
        for btn in self.skill_btns:
            btn.draw(screen)
        target = self._current_target_enemy()
        target_name = target.name if target else "-"
        draw_text_centered(screen,
                           f"Klik hero untuk pilih penyerang | Klik musuh untuk target: {target_name}",
                           F_TINY, C_GRAY, SCREEN_W // 2, SCREEN_H - 115)

    def _draw_turn_info(self):
        phase_text = {
            "player_turn": "🌿 PILIH HERO + SKILL",
            "anim":        "⚡ AKSI BERJALAN...",
            "result":      "SELESAI",
        }.get(self.phase, "")
        col = C_GREEN if self.phase == "player_turn" else C_RED
        draw_text_centered(screen, f"Round {self.engine.turn + 1} | {phase_text}",
                           F_MED, col, SCREEN_W // 2, 12)
        if self.phase == "player_turn":
            remaining = len(self._available_heroes())
            draw_text_centered(screen, f"Hero yang belum menyerang: {remaining}",
                               F_TINY, C_GRAY, SCREEN_W // 2, 38)
        draw_text_centered(screen, "— VS —", F_SMALL, C_GRAY, SCREEN_W // 2, SCREEN_H // 2 - 30)

    def _draw_result(self):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        screen.blit(ov, (0, 0))
        won   = self.engine.winner == "hero"
        title = "🌿 LEVEL CLEAR!" if won else "🌑 ECLIPSE MENANG!"
        msg   = "Klik untuk melihat reward..." if won else "Kegelapan menyelimuti dunia..."
        col   = C_GREEN if won else C_RED
        box   = pygame.Rect(SCREEN_W // 2 - 260, SCREEN_H // 2 - 120, 520, 240)
        draw_rounded_rect(screen, C_DARK, box, 20, border=3, border_color=col)
        draw_text_centered(screen, title, F_BIG, col, SCREEN_W // 2, SCREEN_H // 2 - 70)
        draw_text_centered(screen, msg,   F_MED, C_WHITE, SCREEN_W // 2, SCREEN_H // 2 - 20)
        draw_text_centered(screen, "Klik di mana saja untuk melanjutkan",
                           F_SMALL, C_GRAY, SCREEN_W // 2, SCREEN_H // 2 + 40)
        if won and self.tick % 4 == 0:
            x = random.randint(100, SCREEN_W - 100)
            spawn_particles(x, SCREEN_H // 2, C_GREEN, count=5)