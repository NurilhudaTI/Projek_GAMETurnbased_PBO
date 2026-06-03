import pygame
import sys
import random
import math

from config import *

# PARTICLE SYSTEM
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
        pygame.draw.circle(surf, (r,g,b), (int(self.x), int(self.y)), sz)

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


#  ABSTRACTION & INHERITANCE — Base Classes


class Character:

    def __init__(self, name: str, max_hp: int, attack: int,
                 defense: int, speed: int, color: tuple):
        self._name    = name        # Encapsulated attributes
        self._max_hp  = max_hp
        self._hp      = max_hp
        self._attack  = attack
        self._defense = defense
        self._speed   = speed
        self._color   = color
        self._alive   = True
        self._skills  = []
        self._status_effects = []   # e.g. [("burn", 2)]

    # ── Properties (Encapsulation) ──
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

    # ── Abstract methods (Abstraction) ──
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
        self.skill_type  = skill_type   # "attack", "defense", "heal", "aoe"
        self.power       = power
        self.color       = color
        self.icon        = icon



#  HERO CLASSES — Inheritance from Character


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
            Skill("Vine Slash",    "Serangan fisik kuat ke 1 musuh",         "attack",  1.4, C_GREEN,  "⚔️"),
            Skill("Root Shield",   "Pertahanan diri sendiri +20 DEF 2 turn", "defense", 0,   C_CYAN,   "🛡️"),
            Skill("Thorn Burst",   "Serang semua musuh dengan duri",          "aoe",     0.8, C_GREEN2, "🌵"),
            Skill("Earth Smash",   "Serangan brutal ke 1 musuh",             "attack",  2.0, C_ORANGE, "💥"),
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
            Skill("Petal Storm",   "Sihir ke 1 musuh — damage tinggi",       "attack",  1.6, C_PURPLE,  "🌸"),
            Skill("Spore Cloud",   "Racun ke semua musuh (ATK×0.6)",          "aoe",     0.6, C_PURPLE2, "☁️"),
            Skill("Arcane Bloom",  "Serangan sihir ultimate — 1 musuh",       "attack",  2.2, C_GOLD,    "✨"),
            Skill("Mystic Veil",   "Lindungi 1 ally dari 1 serangan",         "defense", 0,   C_CYAN,    "🌀"),
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
            Skill("Nature's Touch", "Pulihkan 50 HP ke 1 ally",              "heal",    50,  C_HEAL,    "💚"),
            Skill("Rain of Life",   "Pulihkan 25 HP ke semua ally",          "heal_all", 25, C_GREEN,   "🌧️"),
            Skill("Thorn Whip",     "Serang 1 musuh dengan sulur",           "attack",  1.1, C_GREEN2,  "🌿"),
            Skill("Revitalize",     "Pulihkan 80 HP ke ally HP terendah",    "heal",    80,  C_GOLD,    "⭐"),
        ]

    def get_role_icon(self): return "💚"

    def use_skill(self, skill_index, targets, allies):
        sk = self._skills[skill_index]
        result = {"skill": sk.name, "log": [], "particles": []}
        if sk.skill_type == "heal":
            # Revitalize targets lowest HP ally
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
            Skill("Seed Shot",     "Tembak 1 musuh — cepat & akurat",        "attack",  1.3, C_GOLD,    "🏹"),
            Skill("Scatter Arrow", "Tembak 2 musuh acak",                    "multi",   1.0, C_ORANGE,  "🎯"),
            Skill("Camouflage",    "Hindari serangan berikutnya",             "defense", 0,   C_GREEN,   "🍃"),
            Skill("Eagle Strike",  "Tembak tepat sasaran — damage kritis",   "attack",  1.8, C_RED,     "🦅"),
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



#  ENEMY CLASSES — Inheritance from Character


class Enemy(Character):

    """[INHERITANCE] Base enemy class."""
    def __init__(self, name, max_hp, attack, defense, speed, color, tier=1):
        super().__init__(name, max_hp, attack, defense, speed, color)
        self._tier = tier

    def get_description(self):
        return f"HP:{self._max_hp} ATK:{self._attack} DEF:{self._defense}"

    def get_role_icon(self): return "🌑"

    def ai_turn(self, heroes: list) -> dict:
        """[POLYMORPHISM] AI behavior overridden per enemy type."""
        raise NotImplementedError


class Shadow(Enemy):

    """[INHERITANCE + POLYMORPHISM] Fast striker enemy."""
    def __init__(self, tier=1):
        mult = 1 + (tier-1)*0.3
        super().__init__(f"Shadow Lv{tier}",
                         max_hp=int(80*mult), attack=int(28*mult),
                         defense=int(5*mult), speed=20,
                         color=C_PURPLE2, tier=tier)
        self._skills = [
            Skill("Dark Slash",   "Serangan cepat ke 1 hero",   "attack", 1.2, C_PURPLE2, "🗡️"),
            Skill("Void Strike",  "Serangan brutal ke 1 hero",  "attack", 1.8, C_RED,     "💀"),
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
        # Shadow targets lowest HP hero
        target = min(alive, key=lambda h: h.hp)
        sk_idx = 1 if random.random() < 0.3 else 0
        return self.use_skill(sk_idx, [target], [])


class DarkMage(Enemy):

    """[INHERITANCE + POLYMORPHISM] AOE magic enemy."""
    def __init__(self, tier=1):
        mult = 1 + (tier-1)*0.3
        super().__init__(f"Dark Mage Lv{tier}",
                         max_hp=int(70*mult), attack=int(38*mult),
                         defense=int(8*mult), speed=15,
                         color=C_RED2, tier=tier)
        self._skills = [
            Skill("Curse Bolt",    "Sihir gelap ke 1 hero",      "attack", 1.3, C_RED,    "🔥"),
            Skill("Eclipse Blast", "Sihir AOE ke semua hero",    "aoe",    0.7, C_RED2,   "💣"),
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
        # Dark Mage uses AOE 40% chance
        if random.random() < 0.4:
            return self.use_skill(1, alive, [])
        else:
            target = random.choice(alive)
            return self.use_skill(0, [target], [])



#  BATTLE ENGINE


class BattleEngine:

    def __init__(self, heroes: list, enemies: list):
        self.heroes  = heroes
        self.enemies = enemies
        self.turn    = 0
        self.log     = []
        self.winner  = None  # "hero" / "enemy"

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



#  UI COMPONENTS


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
        self.alpha       = 1.0

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
        # Background
        draw_rounded_rect(surf, C_GRAY2, (self.x, self.y, self.w, self.h), 4)
        # HP fill color based on ratio
        if ratio > 0.6:
            col = C_GREEN
        elif ratio > 0.3:
            col = C_GOLD
        else:
            col = C_RED
        fill_w = int(self.w * ratio)
        if fill_w > 0:
            draw_rounded_rect(surf, col, (self.x, self.y, fill_w, self.h), 4)
        # Border
        pygame.draw.rect(surf, C_BORDER, (self.x, self.y, self.w, self.h), 1, border_radius=4)
        # Text
        hp_text = F_TINY.render(f"{int(self._display_hp)}/{self.char.max_hp}", True, C_WHITE)
        surf.blit(hp_text, (self.x + self.w//2 - hp_text.get_width()//2,
                             self.y + self.h//2 - hp_text.get_height()//2))



#  GAME SCREENS


class MenuScreen:

    def __init__(self):
        self.tick = 0
        self.buttons = [
            Button((SCREEN_W//2-130, 330, 260, 52), "START GAME", C_GREEN2, C_GREEN, F_BIG),
            Button((SCREEN_W//2-130, 400, 260, 52), "SETTINGS",   C_PANEL2, C_PANEL, F_BIG),
            Button((SCREEN_W//2-130, 470, 260, 52), "EXIT",        C_RED2,   C_RED,   F_BIG),
        ]
        self.orbs = [(random.randint(50, SCREEN_W-50),
                      random.randint(50, SCREEN_H-50),
                      random.uniform(0, math.pi*2),
                      random.uniform(0.5,2),
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
        # Floating orbs
        for ox, oy, phase, spd, col in self.orbs:
            x = ox + math.sin(self.tick*0.01*spd + phase)*30
            y = oy + math.cos(self.tick*0.008*spd + phase)*20
            alpha_surf = pygame.Surface((20,20), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surf, (*col, 60), (10,10), 10)
            screen.blit(alpha_surf, (int(x)-10, int(y)-10))

        # Title
        glow = abs(math.sin(self.tick*0.04))
        title_col = lerp_color(C_GREEN, C_CYAN, glow)
        draw_text_centered(screen, "MONSTERA", F_TITLE, title_col, SCREEN_W//2, 170)
        draw_text_centered(screen, "ECLIPSE",  F_TITLE, lerp_color(C_PURPLE, C_RED, glow), SCREEN_W//2, 240)
        draw_text_centered(screen, "⚔️ Turn-Based RPG ⚔️", F_SMALL, C_GRAY, SCREEN_W//2, 295)

        for b in self.buttons:
            b.draw(screen)

        draw_text_centered(screen, "© Monstera Eclipse Team", F_TINY, C_GRAY2, SCREEN_W//2, SCREEN_H-20)


class SettingsScreen:

    def __init__(self, music_on):
        self.music_on = music_on
        self.back_btn = Button((30, 30, 120, 40), "← Back", C_PANEL2, C_PANEL, F_SMALL)
        self.music_btn = Button((SCREEN_W//2-130, 280, 260, 52),
                                 "🔊 Music: ON" if music_on else "🔇 Music: OFF",
                                 C_GREEN2 if music_on else C_GRAY2, C_GREEN, F_MED)

    def update(self, events):
        mx, my = pygame.mouse.get_pos()
        self.back_btn.check_hover((mx,my))
        self.music_btn.check_hover((mx,my))
        for e in events:
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if self.back_btn.is_clicked((mx,my), e):
                return "menu", self.music_on
            if self.music_btn.is_clicked((mx,my), e):
                self.music_on = not self.music_on
                self.music_btn.text = "🔊 Music: ON" if self.music_on else "🔇 Music: OFF"
                self.music_btn.color = C_GREEN2 if self.music_on else C_GRAY2
        return "settings", self.music_on

    def draw(self):
        screen.fill(C_BG)
        draw_text_centered(screen, "⚙️  SETTINGS", F_BIG, C_WHITE, SCREEN_W//2, 120)
        draw_rounded_rect(screen, C_PANEL, (SCREEN_W//2-200, 220, 400, 200), 16,
                          border=2, border_color=C_BORDER)
        draw_text_centered(screen, "Background Music", F_MED, C_GRAY, SCREEN_W//2, 255)
        self.music_btn.draw(screen)
        draw_text_centered(screen, "Controls: Mouse + Click to play", F_SMALL, C_GRAY, SCREEN_W//2, 370)
        self.back_btn.draw(screen)


class PartySelectScreen:

    HERO_CLASSES = [Warrior, Mage, Healer, Ranger]
    HERO_NAMES   = ["Verdant Knight", "Flora Sorceress", "Bloom Sage", "Moss Hunter"]
    HERO_ROLES   = ["Warrior ⚔️", "Mage 🔮", "Healer 💚", "Ranger 🏹"]
    HERO_DESCS   = [
        ["HP: 180 (Tinggi)", "ATK: 35 | DEF: 20", "SPD: 12 — Tank tangguh", "Skill AoE & Shield"],
        ["HP: 110 (Rendah)", "ATK: 55 | DEF: 8",  "SPD: 16 — Glass Cannon","Skill burst damage"],
        ["HP: 130 (Medium)", "ATK: 22 | DEF: 14", "SPD: 14 — Support",     "Heal tim & serangan"],
        ["HP: 145 (Medium)", "ATK: 40 | DEF: 12", "SPD: 18 — Tercepat",    "Serangan ganda/kritis"],
    ]
    HERO_COLORS  = [C_GREEN, C_PURPLE, C_HEAL, C_GOLD]

    def __init__(self):
        # Tim default berisi 4 karakter sesuai role: Warrior, Mage, Healer, Ranger
        self.selected = set(range(4))
        self.hovered  = -1
        self.start_btn = Button((SCREEN_W//2-140, SCREEN_H-70, 280, 48),
                                 "⚔️  START BATTLE", C_GREEN2, C_GREEN, F_BIG)
        self.back_btn  = Button((30, 30, 120, 40), "← Back", C_PANEL2, C_PANEL, F_SMALL)
        self.card_rects = []
        # Layout: 4 cards across
        cw, ch = 220, 280
        gap = 24
        total_w = 4*cw + 3*gap
        sx = (SCREEN_W - total_w) // 2
        for i in range(4):
            self.card_rects.append(pygame.Rect(sx + i*(cw+gap), 130, cw, ch))

    def update(self, events):
        mx, my = pygame.mouse.get_pos()
        self.start_btn.check_hover((mx,my))
        self.back_btn.check_hover((mx,my))
        self.hovered = -1
        for i, r in enumerate(self.card_rects):
            if r.collidepoint(mx, my):
                self.hovered = i
        for e in events:
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if self.back_btn.is_clicked((mx,my), e): return "menu", []
            if e.type == pygame.MOUSEBUTTONDOWN:
                for i, r in enumerate(self.card_rects):
                    if r.collidepoint(mx, my):
                        if i in self.selected:
                            self.selected.discard(i)
                        elif len(self.selected) < 4:
                            self.selected.add(i)
            if self.start_btn.is_clicked((mx,my), e):
                if len(self.selected) == 4:
                    heroes = [self.HERO_CLASSES[i]() for i in sorted(self.selected)]
                    return "battle", heroes
        return "select_party", []

    def draw(self):
        screen.fill(C_BG)
        draw_text_centered(screen, "🌿 TIM HERO (4 ROLE)", F_BIG, C_WHITE, SCREEN_W//2, 55)
        draw_text_centered(screen, f"Dipilih: {len(self.selected)}/4 — Warrior, Mage, Healer, Ranger", F_MED,
                           C_GREEN if len(self.selected) == 4 else C_GRAY, SCREEN_W//2, 95)

        for i, (r, cls) in enumerate(zip(self.card_rects, self.HERO_CLASSES)):
            sel = i in self.selected
            hov = i == self.hovered
            bg = C_PANEL2 if not sel else (20, 55, 35)
            border_col = self.HERO_COLORS[i] if sel else (C_BORDER if not hov else C_WHITE)
            draw_rounded_rect(screen, bg, r, 16, border=2 if not sel else 3, border_color=border_col)

            cx = r.centerx
            # Icon
            icon = F_TITLE.render(["⚔️","🔮","💚","🏹"][i], True, self.HERO_COLORS[i])
            screen.blit(icon, (cx - icon.get_width()//2, r.y + 12))
            # Role
            draw_text_centered(screen, self.HERO_ROLES[i], F_MED, self.HERO_COLORS[i], cx, r.y+90)
            draw_text_centered(screen, self.HERO_NAMES[i], F_SMALL, C_WHITE, cx, r.y+118)
            # Stats
            for j, desc in enumerate(self.HERO_DESCS[i]):
                draw_text_centered(screen, desc, F_TINY, C_GRAY, cx, r.y+146+j*22)
            # Selected checkmark
            if sel:
                draw_text_centered(screen, "✔ DIPILIH", F_SMALL, C_GREEN, cx, r.bottom-22)

        if len(self.selected) == 4:
            self.start_btn.draw(screen)
        else:
            # Dimmed button
            draw_rounded_rect(screen, C_GRAY2,
                              (SCREEN_W//2-140, SCREEN_H-70, 280, 48), 10)
            draw_text_centered(screen, "Tim harus berisi 4 hero", F_MED, C_GRAY,
                               SCREEN_W//2, SCREEN_H-46)
        self.back_btn.draw(screen)


class BattleScreen:

    def __init__(self, heroes: list):
        self.heroes  = heroes
        self.enemies = self._gen_enemies()
        self.engine  = BattleEngine(self.heroes, self.enemies)
        self.hp_bars_h = {h: HPBar(0,0,140,14,h) for h in heroes}
        self.hp_bars_e = {e: HPBar(0,0,120,12,e) for e in self.enemies}

        self.phase = "player_turn"  # player_turn / anim / result
        self.selected_hero_idx = 0
        self.selected_enemy_idx = 0
        self.anim_timer = 0
        self.anim_result = None
        self.turn_label  = ""
        self.tick = 0

        # Sistem giliran bergantian ala RPG/HSR sederhana
        self.acted_heroes = set()
        self.enemy_turn_index = 0
        self.last_actor = None

        self.hero_rects   = []
        self.enemy_rects  = []
        self.skill_btns   = []
        self._build_layout()
        self._select_next_available_hero()

    def _gen_enemies(self):
        tier = 1
        pool = [Shadow, DarkMage]
        count = random.randint(3, 4)
        enems = []
        for _ in range(count):
            cls = random.choice(pool)
            enems.append(cls(tier))
        return enems

    def _build_layout(self):
        hw, hh = 160, 110
        gap = 14
        sx = 30
        for i in range(len(self.heroes)):
            self.hero_rects.append(pygame.Rect(sx + i*(hw+gap), SCREEN_H-hh-14, hw, hh))

        ew, eh = 150, 100
        ex_start = SCREEN_W - (len(self.enemies)*(ew+gap)) - 20
        for i in range(len(self.enemies)):
            self.enemy_rects.append(pygame.Rect(ex_start + i*(ew+gap), 14, ew, eh))

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
        sx = SCREEN_W//2 - (2*bw + 10)//2
        for i, sk in enumerate(hero.skills):
            col_map = {"attack":C_RED2,"defense":C_BLUE,"heal":C_GREEN2,
                       "heal_all":C_GREEN2,"aoe":C_PURPLE2,"multi":C_ORANGE}
            col = col_map.get(sk.skill_type, C_PANEL2)
            row, col_pos = divmod(i, 2)
            btn = Button((sx + col_pos*(bw+10), SCREEN_H-240 + row*(bh+8), bw, bh),
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
                    return "menu"
            return "battle"

        if self.phase == "player_turn":
            hero = self._current_hero()
            if hero:
                for btn in self.skill_btns:
                    btn.check_hover((mx,my))

            for e in events:
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()

                if e.type == pygame.KEYDOWN:
                    available = self._available_heroes()
                    if available:
                        current_pos = available.index(hero) if hero in available else 0
                        if e.key in (pygame.K_LEFT, pygame.K_a):
                            next_hero = available[(current_pos-1) % len(available)]
                            self._select_hero_by_index(self.heroes.index(next_hero))
                        if e.key in (pygame.K_RIGHT, pygame.K_d):
                            next_hero = available[(current_pos+1) % len(available)]
                            self._select_hero_by_index(self.heroes.index(next_hero))

                if e.type == pygame.MOUSEBUTTONDOWN:
                    for i, r in enumerate(self.hero_rects):
                        if r.collidepoint(mx,my):
                            self._select_hero_by_index(i)

                    for i, r in enumerate(self.enemy_rects):
                        if r.collidepoint(mx,my):
                            self._select_enemy_by_index(i)

                for i, btn in enumerate(self.skill_btns):
                    if btn.is_clicked((mx,my), e):
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

        if sk.skill_type in ("heal", "heal_all"):
            targets = alive_heroes
        elif sk.skill_type == "defense":
            targets = alive_heroes
        elif sk.skill_type == "aoe":
            targets = alive_enemies
        elif sk.skill_type == "multi":
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

        enemy = None
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
        return (SCREEN_W//2, SCREEN_H//2)

    def draw(self):
        screen.fill(C_BG)
        self._draw_bg_effects()
        self._draw_enemies()
        self._draw_heroes()
        self._draw_battle_log()
        self._draw_skills()
        self._draw_turn_info()
        update_particles(screen)
        if self.phase == "result":
            self._draw_result()

    def _draw_bg_effects(self):
        for x in range(0, SCREEN_W, 60):
            pygame.draw.line(screen, (15, 22, 35), (x, 0), (x, SCREEN_H))
        for y in range(0, SCREEN_H, 60):
            pygame.draw.line(screen, (15, 22, 35), (0, y), (SCREEN_W, y))
        glow_r = 180 + int(math.sin(self.tick*0.03)*20)
        glow_surf = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
        for r in range(glow_r, 0, -20):
            a = int(8 * (r/glow_r))
            pygame.draw.circle(glow_surf, (80, 20, 100, a), (glow_r, glow_r), r)
        screen.blit(glow_surf, (SCREEN_W//2 - glow_r, SCREEN_H//2 - glow_r - 80))

    def _draw_enemies(self):
        for i, (enemy, rect) in enumerate(zip(self.enemies, self.enemy_rects)):
            selected = i == self.selected_enemy_idx and enemy.alive and self.phase == "player_turn"
            if not enemy.alive:
                draw_rounded_rect(screen, (12,12,16), rect, 12, border=1, border_color=C_GRAY2)
                draw_text_centered(screen, "💀 DEFEATED", F_TINY, C_GRAY, rect.centerx, rect.centery)
                continue

            border = C_GOLD if selected else C_BORDER2
            draw_rounded_rect(screen, C_SHADOW_E, rect, 12, border=3 if selected else 2, border_color=border)
            if selected:
                draw_text_centered(screen, "▼ TARGET", F_TINY, C_GOLD, rect.centerx, rect.bottom+12)
            if self.last_actor is enemy:
                draw_text_centered(screen, "ACTION", F_TINY, C_RED, rect.centerx, rect.top-10)
            draw_text_centered(screen, enemy.get_role_icon(), F_BIG, enemy.color, rect.centerx, rect.y+22)
            draw_text_centered(screen, enemy.name, F_TINY, C_WHITE, rect.centerx, rect.y+52)
            bar = self.hp_bars_e[enemy]
            bar.x = rect.x+8; bar.y = rect.y+68; bar.w = rect.w-16; bar.h = 14
            bar.draw(screen)
            draw_text_centered(screen, f"ATK:{enemy.attack} DEF:{enemy.defense}", F_TINY, C_GRAY, rect.centerx, rect.y+88)

    def _draw_heroes(self):
        for i, (hero, rect) in enumerate(zip(self.heroes, self.hero_rects)):
            is_selected = (i == self.selected_hero_idx and self.phase == "player_turn" and
                           hero.alive and hero not in self.acted_heroes)
            already_acted = hero in self.acted_heroes

            if not hero.alive:
                draw_rounded_rect(screen, (12,12,16), rect, 12, border=1, border_color=C_GRAY2)
                draw_text_centered(screen, "💀", F_MED, C_GRAY, rect.centerx, rect.centery)
                draw_text_centered(screen, "K.O.", F_TINY, C_GRAY, rect.centerx, rect.centery+24)
                continue

            if already_acted:
                bg_c = (18, 22, 28)
                border_c = C_GRAY2
            else:
                bg_c = (15,35,20) if is_selected else C_PANEL
                border_c = hero.color if is_selected else C_BORDER

            draw_rounded_rect(screen, bg_c, rect, 12, border=3 if is_selected else 2, border_color=border_c)

            if is_selected:
                glow = abs(math.sin(self.tick*0.08))
                g_surf = pygame.Surface((rect.w+20, rect.h+20), pygame.SRCALPHA)
                pygame.draw.rect(g_surf, (*hero.color, int(40*glow)),
                                 (0,0,rect.w+20,rect.h+20), border_radius=14)
                screen.blit(g_surf, (rect.x-10, rect.y-10))

            draw_text_centered(screen, hero.get_role_icon(), F_MED, hero.color, rect.centerx, rect.y+18)
            draw_text_centered(screen, hero.name, F_TINY, C_WHITE if not already_acted else C_GRAY, rect.centerx, rect.y+40)
            draw_text_centered(screen, hero.role,  F_TINY, hero.color if not already_acted else C_GRAY, rect.centerx, rect.y+56)
            bar = self.hp_bars_h[hero]
            bar.x = rect.x+8; bar.y = rect.y+72; bar.w = rect.w-16; bar.h = 14
            bar.draw(screen)
            draw_text_centered(screen, f"ATK:{hero.attack} DEF:{hero.defense}", F_TINY, C_GRAY, rect.centerx, rect.y+93)

            if is_selected:
                draw_text_centered(screen, "▲ ACTIVE", F_TINY, C_GREEN, rect.centerx, rect.top-12)
            elif already_acted:
                draw_text_centered(screen, "DONE", F_TINY, C_GRAY, rect.centerx, rect.top-12)

    def _draw_battle_log(self):
        lx, ly, lw, lh = SCREEN_W - 310, 130, 290, 200
        draw_rounded_rect(screen, C_PANEL, (lx, ly, lw, lh), 12, border=1, border_color=C_BORDER)
        draw_text(screen, "📜 Battle Log", F_TINY, C_GOLD, lx+10, ly+8)
        for i, msg in enumerate(self.engine.log[-7:]):
            col = C_WHITE if i == len(self.engine.log[-7:])-1 else C_GRAY
            txt = F_TINY.render(msg[:40], True, col)
            screen.blit(txt, (lx+8, ly+28+i*22))

    def _draw_skills(self):
        if self.phase != "player_turn": return
        hero = self._current_hero()
        if not hero: return
        panel_rect = (SCREEN_W//2 - 230, SCREEN_H - 260, 460, 145)
        draw_rounded_rect(screen, C_PANEL, panel_rect, 14, border=1, border_color=C_BORDER)
        draw_text_centered(screen, f"Pilih Skill — {hero.name} ({hero.role})", F_SMALL, hero.color,
                           SCREEN_W//2, SCREEN_H-250)
        for btn in self.skill_btns:
            btn.draw(screen)
        target = self._current_target_enemy()
        target_name = target.name if target else "-"
        draw_text_centered(screen, f"Klik hero untuk pilih penyerang | Klik musuh untuk target: {target_name}",
                           F_TINY, C_GRAY, SCREEN_W//2, SCREEN_H-115)

    def _draw_turn_info(self):
        phase_text = {
            "player_turn": "🌿 PILIH HERO + SKILL",
            "anim":        "⚡ AKSI BERJALAN...",
            "result":      "SELESAI",
        }.get(self.phase, "")
        col = C_GREEN if self.phase=="player_turn" else C_RED
        draw_text_centered(screen, f"Round {self.engine.turn+1} | {phase_text}",
                           F_MED, col, SCREEN_W//2, 12)
        if self.phase == "player_turn":
            remaining = len(self._available_heroes())
            draw_text_centered(screen, f"Hero yang belum menyerang: {remaining}", F_TINY, C_GRAY, SCREEN_W//2, 38)
        draw_text_centered(screen, "— VS —", F_SMALL, C_GRAY, SCREEN_W//2, SCREEN_H//2 - 30)

    def _draw_result(self):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0,0,0,160))
        screen.blit(ov, (0,0))
        won = self.engine.winner == "hero"
        title  = "🌿 MONSTERA MENANG!" if won else "🌑 ECLIPSE MENANG!"
        msg    = "Alam kembali bersinar!" if won else "Kegelapan menyelimuti dunia..."
        col    = C_GREEN if won else C_RED
        box = pygame.Rect(SCREEN_W//2-260, SCREEN_H//2-120, 520, 240)
        draw_rounded_rect(screen, C_DARK, box, 20, border=3, border_color=col)
        draw_text_centered(screen, title, F_BIG, col, SCREEN_W//2, SCREEN_H//2-70)
        draw_text_centered(screen, msg,  F_MED, C_WHITE, SCREEN_W//2, SCREEN_H//2-20)
        draw_text_centered(screen, "Klik di mana saja untuk kembali ke menu", F_SMALL, C_GRAY, SCREEN_W//2, SCREEN_H//2+40)
        if won and self.tick % 4 == 0:
            x = random.randint(100, SCREEN_W-100)
            spawn_particles(x, SCREEN_H//2, C_GREEN, count=5)

