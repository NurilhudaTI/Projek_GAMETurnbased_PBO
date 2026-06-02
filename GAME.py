"""
╔══════════════════════════════════════════════════════╗
║         MONSTERA ECLIPSE — game.py                  ║
║                                                      ║
║  Isi file ini:                                       ║
║  [1] Skill — data satu kemampuan                     ║
║  [2] Character — base class abstrak (OOP)            ║
║  [3] Hero & subclass — Warrior, Mage, Healer, Ranger ║
║  [4] Enemy & subclass — Shadow, DarkMage             ║
║  [5] BattleEngine — giliran, log, cek menang         ║
║  [6] BattleScreen — tampilan & input layar battle    ║
╚══════════════════════════════════════════════════════╝
"""

import pygame
import sys
import random
import math

from config import (
    screen,
    SCREEN_W, SCREEN_H,
    C_BG, C_DARK, C_PANEL, C_BORDER, C_BORDER2,
    C_GREEN, C_GREEN2, C_PURPLE, C_PURPLE2,
    C_GOLD, C_ORANGE, C_RED, C_RED2,
    C_BLUE, C_CYAN, C_HEAL,
    C_WHITE, C_GRAY, C_GRAY2, C_SHADOW_E,
    F_BIG, F_MED, F_SMALL, F_TINY,
    draw_rounded_rect, draw_text_centered, draw_text, lerp_color,
    spawn_particles, update_particles,
    Button, HPBar,
)


# ════════════════════════════════════════════════════════════════════
#  [1] SKILL
#      Menyimpan data satu kemampuan karakter.
# ════════════════════════════════════════════════════════════════════

class Skill:
    """
    [ENCAPSULATION] Data satu skill disimpan dalam satu objek.

    skill_type:
        "attack"  — serang 1 musuh
        "aoe"     — serang semua musuh
        "multi"   — serang beberapa musuh acak
        "heal"    — pulihkan HP 1 ally
        "heal_all"— pulihkan HP semua ally
        "defense" — buff pertahanan diri / ally
    """

    def __init__(self, name: str, description: str, skill_type: str,
                 power: float, color: tuple, icon: str):
        self.name        = name
        self.description = description
        self.skill_type  = skill_type
        self.power       = power       # pengali damage / jumlah heal
        self.color       = color       # warna partikel efek
        self.icon        = icon        # emoji ikon tombol


# ════════════════════════════════════════════════════════════════════
#  [2] CHARACTER — Base Class (Abstraction + Encapsulation)
# ════════════════════════════════════════════════════════════════════

class Character:
    """
    [ABSTRACTION]  Kelas dasar abstrak untuk SEMUA karakter.
                   Mendefinisikan interface tanpa implementasi detail.
    [ENCAPSULATION] Atribut diawali _ dan dibaca via property.
    """

    def __init__(self, name: str, max_hp: int, attack: int,
                 defense: int, speed: int, color: tuple):
        # ── Atribut privat (Encapsulation) ──────────────────────────
        self._name    = name
        self._max_hp  = max_hp
        self._hp      = max_hp
        self._attack  = attack
        self._defense = defense
        self._speed   = speed
        self._color   = color
        self._alive   = True
        self._skills: list[Skill] = []

    # ── Properti publik ─────────────────────────────────────────────
    @property
    def name(self):    return self._name
    @property
    def hp(self):      return self._hp
    @property
    def max_hp(self):  return self._max_hp
    @property
    def attack(self):  return self._attack
    @property
    def defense(self): return self._defense
    @property
    def speed(self):   return self._speed
    @property
    def color(self):   return self._color
    @property
    def alive(self):   return self._alive
    @property
    def skills(self):  return self._skills

    # ── Mekanik bersama ─────────────────────────────────────────────
    def take_damage(self, raw_dmg: int) -> int:
        """Kurangi HP setelah diperhitungkan defense. Min damage = 1."""
        actual = max(1, raw_dmg - self._defense)
        self._hp = max(0, self._hp - actual)
        if self._hp == 0:
            self._alive = False
        return actual

    def heal(self, amount: int) -> int:
        """Pulihkan HP, tidak melebihi max_hp."""
        healed = min(amount, self._max_hp - self._hp)
        self._hp += healed
        return healed

    def hp_ratio(self) -> float:
        return self._hp / self._max_hp

    # ── Interface abstrak (wajib diimplementasikan subclass) ────────
    def get_description(self) -> str:
        raise NotImplementedError

    def get_role_icon(self) -> str:
        raise NotImplementedError

    def use_skill(self, skill_index: int, targets: list, allies: list) -> dict:
        """
        [POLYMORPHISM] Setiap subclass mengimplementasikan logikanya sendiri.
        Return: {"skill": str, "log": [str], "particles": [(char, color)]}
        """
        raise NotImplementedError


# ════════════════════════════════════════════════════════════════════
#  [3] HERO — Inheritance dari Character
# ════════════════════════════════════════════════════════════════════

class Hero(Character):
    """[INHERITANCE] Kelas hero dasar. Menambahkan atribut role."""

    def __init__(self, name, max_hp, attack, defense, speed, color, role):
        super().__init__(name, max_hp, attack, defense, speed, color)
        self._role = role

    @property
    def role(self): return self._role

    def get_description(self) -> str:
        return (f"HP:{self._max_hp}  ATK:{self._attack}  "
                f"DEF:{self._defense}  SPD:{self._speed}")

    def get_role_icon(self) -> str:
        return "🌿"


# ── Warrior ──────────────────────────────────────────────────────────────────
class Warrior(Hero):
    """
    [INHERITANCE + POLYMORPHISM]
    Peran  : Tank — HP & DEF tinggi, serangan fisik.
    Skills : Vine Slash | Root Shield | Thorn Burst (AoE) | Earth Smash
    """

    def __init__(self, name="Verdant Knight"):
        super().__init__(name, max_hp=180, attack=35, defense=20,
                         speed=12, color=C_GREEN, role="Warrior")
        self._skills = [
            Skill("Vine Slash",  "Serangan fisik kuat ke 1 musuh",         "attack",  1.4, C_GREEN,  "⚔️"),
            Skill("Root Shield", "Pertahanan diri +20 DEF",                "defense", 0,   C_CYAN,   "🛡️"),
            Skill("Thorn Burst", "Serang semua musuh dengan duri",          "aoe",     0.8, C_GREEN2, "🌵"),
            Skill("Earth Smash", "Serangan brutal ke 1 musuh",             "attack",  2.0, C_ORANGE, "💥"),
        ]

    def get_role_icon(self): return "⚔️"

    def use_skill(self, skill_index, targets, allies):
        sk     = self._skills[skill_index]
        result = {"skill": sk.name, "log": [], "particles": []}

        if sk.skill_type == "attack":
            for t in targets[:1]:
                actual = t.take_damage(int(self._attack * sk.power))
                result["log"].append(f"{self._name} → {t.name}: {actual} DMG")
                result["particles"].append((t, sk.color))

        elif sk.skill_type == "aoe":
            for t in targets:
                actual = t.take_damage(int(self._attack * sk.power))
                result["log"].append(f"{self._name} → {t.name}: {actual} DMG")
                result["particles"].append((t, sk.color))

        elif sk.skill_type == "defense":
            self._defense += 20
            result["log"].append(f"{self._name} aktifkan Root Shield! DEF+20")
            result["particles"].append((self, sk.color))

        return result


# ── Mage ─────────────────────────────────────────────────────────────────────
class Mage(Hero):
    """
    [INHERITANCE + POLYMORPHISM]
    Peran  : Glass Cannon — ATK tertinggi, HP terendah.
    Skills : Petal Storm | Spore Cloud (AoE) | Arcane Bloom | Mystic Veil
    """

    def __init__(self, name="Flora Sorceress"):
        super().__init__(name, max_hp=110, attack=55, defense=8,
                         speed=16, color=C_PURPLE, role="Mage")
        self._skills = [
            Skill("Petal Storm",  "Sihir burst ke 1 musuh",          "attack",  1.6, C_PURPLE,  "🌸"),
            Skill("Spore Cloud",  "Racun ke semua musuh (ATK×0.6)",   "aoe",     0.6, C_PURPLE2, "☁️"),
            Skill("Arcane Bloom", "Sihir ultimate ke 1 musuh",        "attack",  2.2, C_GOLD,    "✨"),
            Skill("Mystic Veil",  "Lindungi ally dari 1 serangan",    "defense", 0,   C_CYAN,    "🌀"),
        ]

    def get_role_icon(self): return "🔮"

    def use_skill(self, skill_index, targets, allies):
        sk     = self._skills[skill_index]
        result = {"skill": sk.name, "log": [], "particles": []}

        if sk.skill_type in ("attack", "aoe"):
            tlist = targets[:1] if sk.skill_type == "attack" else targets
            for t in tlist:
                actual = t.take_damage(int(self._attack * sk.power))
                result["log"].append(f"{self._name} ✨ {t.name}: {actual} DMG")
                result["particles"].append((t, sk.color))

        elif sk.skill_type == "defense":
            result["log"].append(f"{self._name} bungkus ally dengan Mystic Veil!")
            result["particles"].append((self, sk.color))

        return result


# ── Healer ───────────────────────────────────────────────────────────────────
class Healer(Hero):
    """
    [INHERITANCE + POLYMORPHISM]
    Peran  : Support — menyembuhkan tim.
    Skills : Nature's Touch | Rain of Life (heal all) | Thorn Whip | Revitalize
    """

    def __init__(self, name="Bloom Sage"):
        super().__init__(name, max_hp=130, attack=22, defense=14,
                         speed=14, color=C_HEAL, role="Healer")
        self._skills = [
            Skill("Nature's Touch", "Pulihkan 50 HP ke 1 ally",           "heal",     50,  C_HEAL,   "💚"),
            Skill("Rain of Life",   "Pulihkan 25 HP ke semua ally",       "heal_all", 25,  C_GREEN,  "🌧️"),
            Skill("Thorn Whip",     "Serang 1 musuh dengan sulur",        "attack",   1.1, C_GREEN2, "🌿"),
            Skill("Revitalize",     "Pulihkan 80 HP ke ally HP terendah", "heal",     80,  C_GOLD,   "⭐"),
        ]

    def get_role_icon(self): return "💚"

    def use_skill(self, skill_index, targets, allies):
        sk     = self._skills[skill_index]
        result = {"skill": sk.name, "log": [], "particles": []}

        if sk.skill_type == "heal":
            # Revitalize memilih ally HP terendah
            ally = (min(allies, key=lambda a: a.hp)
                    if sk.name == "Revitalize"
                    else random.choice(allies))
            healed = ally.heal(int(sk.power))
            result["log"].append(f"{self._name} 💚 {ally.name}: +{healed} HP")
            result["particles"].append((ally, sk.color))

        elif sk.skill_type == "heal_all":
            for a in allies:
                healed = a.heal(int(sk.power))
                result["log"].append(f"{self._name} 🌧️ {a.name}: +{healed} HP")
                result["particles"].append((a, sk.color))

        elif sk.skill_type == "attack":
            for t in targets[:1]:
                actual = t.take_damage(int(self._attack * sk.power))
                result["log"].append(f"{self._name} → {t.name}: {actual} DMG")
                result["particles"].append((t, sk.color))

        return result


# ── Ranger ───────────────────────────────────────────────────────────────────
class Ranger(Hero):
    """
    [INHERITANCE + POLYMORPHISM]
    Peran  : Balanced — SPD tertinggi, damage konsisten.
    Skills : Seed Shot | Scatter Arrow (multi) | Camouflage | Eagle Strike
    """

    def __init__(self, name="Moss Hunter"):
        super().__init__(name, max_hp=145, attack=40, defense=12,
                         speed=18, color=C_GOLD, role="Ranger")
        self._skills = [
            Skill("Seed Shot",     "Tembak 1 musuh — cepat & akurat",    "attack",  1.3, C_GOLD,   "🏹"),
            Skill("Scatter Arrow", "Tembak 2 musuh acak",                "multi",   1.0, C_ORANGE, "🎯"),
            Skill("Camouflage",    "Hindari serangan berikutnya",         "defense", 0,   C_GREEN,  "🍃"),
            Skill("Eagle Strike",  "Tembak kritis ke 1 musuh",           "attack",  1.8, C_RED,    "🦅"),
        ]

    def get_role_icon(self): return "🏹"

    def use_skill(self, skill_index, targets, allies):
        sk     = self._skills[skill_index]
        result = {"skill": sk.name, "log": [], "particles": []}

        if sk.skill_type == "attack":
            for t in targets[:1]:
                actual = t.take_damage(int(self._attack * sk.power))
                result["log"].append(f"{self._name} 🏹 {t.name}: {actual} DMG")
                result["particles"].append((t, sk.color))

        elif sk.skill_type == "multi":
            chosen = random.sample(targets, min(2, len(targets)))
            for t in chosen:
                actual = t.take_damage(int(self._attack * sk.power))
                result["log"].append(f"{self._name} 🎯 {t.name}: {actual} DMG")
                result["particles"].append((t, sk.color))

        elif sk.skill_type == "defense":
            result["log"].append(f"{self._name} bersembunyi — serangan meleset!")
            result["particles"].append((self, sk.color))

        return result


# ════════════════════════════════════════════════════════════════════
#  [4] ENEMY — Inheritance dari Character
# ════════════════════════════════════════════════════════════════════

class Enemy(Character):
    """[INHERITANCE] Kelas musuh dasar. Menambahkan tier (level scaling)."""

    def __init__(self, name, max_hp, attack, defense, speed, color, tier=1):
        super().__init__(name, max_hp, attack, defense, speed, color)
        self._tier = tier

    @property
    def tier(self): return self._tier

    def get_description(self) -> str:
        return f"HP:{self._max_hp}  ATK:{self._attack}  DEF:{self._defense}"

    def get_role_icon(self) -> str:
        return "🌑"

    def ai_turn(self, heroes: list) -> dict:
        """[POLYMORPHISM] Logika AI berbeda di setiap subclass."""
        raise NotImplementedError


# ── Shadow ───────────────────────────────────────────────────────────────────
class Shadow(Enemy):
    """
    [INHERITANCE + POLYMORPHISM]
    AI: incar hero HP terendah; 30% gunakan Void Strike (damage tinggi).
    """

    def __init__(self, tier=1):
        mult = 1 + (tier - 1) * 0.3
        super().__init__(
            f"Shadow Lv{tier}",
            max_hp=int(80*mult), attack=int(28*mult),
            defense=int(5*mult), speed=20,
            color=C_PURPLE2, tier=tier,
        )
        self._skills = [
            Skill("Dark Slash",  "Serangan cepat ke 1 hero",  "attack", 1.2, C_PURPLE2, "🗡️"),
            Skill("Void Strike", "Serangan brutal ke 1 hero", "attack", 1.8, C_RED,     "💀"),
        ]

    def get_role_icon(self): return "🌑"

    def use_skill(self, skill_index, targets, allies):
        sk     = self._skills[skill_index]
        result = {"skill": sk.name, "log": [], "particles": []}
        for t in targets[:1]:
            actual = t.take_damage(int(self._attack * sk.power))
            result["log"].append(f"{self._name} ⚡ {t.name}: {actual} DMG")
            result["particles"].append((t, C_PURPLE2))
        return result

    def ai_turn(self, heroes):
        alive = [h for h in heroes if h.alive]
        if not alive:
            return {"log": [], "particles": []}
        target = min(alive, key=lambda h: h.hp)        # incar HP terendah
        sk_idx = 1 if random.random() < 0.3 else 0     # 30% Void Strike
        return self.use_skill(sk_idx, [target], [])


# ── DarkMage ─────────────────────────────────────────────────────────────────
class DarkMage(Enemy):
    """
    [INHERITANCE + POLYMORPHISM]
    AI: 40% Eclipse Blast (AoE semua hero), 60% Curse Bolt (1 hero acak).
    """

    def __init__(self, tier=1):
        mult = 1 + (tier - 1) * 0.3
        super().__init__(
            f"Dark Mage Lv{tier}",
            max_hp=int(70*mult), attack=int(38*mult),
            defense=int(8*mult), speed=15,
            color=C_RED2, tier=tier,
        )
        self._skills = [
            Skill("Curse Bolt",    "Sihir gelap ke 1 hero",   "attack", 1.3, C_RED,  "🔥"),
            Skill("Eclipse Blast", "Sihir AoE ke semua hero", "aoe",    0.7, C_RED2, "💣"),
        ]

    def get_role_icon(self): return "☄️"

    def use_skill(self, skill_index, targets, allies):
        sk     = self._skills[skill_index]
        result = {"skill": sk.name, "log": [], "particles": []}
        tlist  = targets if sk.skill_type == "aoe" else targets[:1]
        for t in tlist:
            actual = t.take_damage(int(self._attack * sk.power))
            result["log"].append(f"{self._name} ☄️ {t.name}: {actual} DMG")
            result["particles"].append((t, C_RED))
        return result

    def ai_turn(self, heroes):
        alive = [h for h in heroes if h.alive]
        if not alive:
            return {"log": [], "particles": []}
        if random.random() < 0.4:
            return self.use_skill(1, alive, [])          # AoE
        return self.use_skill(0, [random.choice(alive)], [])


# ════════════════════════════════════════════════════════════════════
#  [5] BATTLE ENGINE — Giliran, Log, Cek Menang
# ════════════════════════════════════════════════════════════════════

class BattleEngine:
    """
    Otak pertarungan.

    Tanggung jawab:
        - Menyimpan daftar hero & musuh
        - Mengelola log aksi (maks 8 baris)
        - Memproses giliran hero dan AI musuh
        - Menentukan pemenang
    """

    def __init__(self, heroes: list, enemies: list):
        self.heroes  = heroes
        self.enemies = enemies
        self.turn    = 0
        self.log: list[str] = []
        self.winner: str | None = None    # "hero" | "enemy"
        self._sort_turn_order()

    def _sort_turn_order(self):
        """Urutkan berdasarkan speed, lalu acak untuk variasi."""
        all_chars = self.heroes + self.enemies
        self.turn_order = sorted(all_chars, key=lambda c: -c.speed)
        random.shuffle(self.turn_order)

    # ── Helper ──────────────────────────────────────────────────────
    def alive_heroes(self)  -> list: return [h for h in self.heroes  if h.alive]
    def alive_enemies(self) -> list: return [e for e in self.enemies if e.alive]

    def add_log(self, msg: str):
        self.log.append(msg)
        if len(self.log) > 8:
            self.log.pop(0)

    def check_winner(self):
        if not self.alive_heroes():
            self.winner = "enemy"
        elif not self.alive_enemies():
            self.winner = "hero"

    # ── Giliran ─────────────────────────────────────────────────────
    def enemy_turn(self) -> list[dict]:
        """Semua musuh hidup melakukan aksi AI."""
        results = []
        for enemy in self.alive_enemies():
            res = enemy.ai_turn(self.alive_heroes())
            for msg in res["log"]:
                self.add_log(msg)
            results.append(res)
        self.check_winner()
        return results

    def hero_use_skill(self, hero, skill_idx: int, targets: list) -> dict:
        """Hero menggunakan skill, catat log, cek pemenang."""
        res = hero.use_skill(skill_idx, targets, self.alive_heroes())
        for msg in res["log"]:
            self.add_log(msg)
        self.check_winner()
        return res


# ════════════════════════════════════════════════════════════════════
#  [6] BATTLE SCREEN — Tampilan & Input Layar Pertempuran
# ════════════════════════════════════════════════════════════════════

class BattleScreen:
    """
    Layar pertempuran utama.

    Fase:
        player_turn → hero aktif pilih & gunakan skill
        anim        → animasi pasca-skill (timer countdown)
        enemy_turn  → semua musuh lakukan AI (langsung)
        result      → tampilkan hasil akhir
    """

    # Peta warna tombol per skill_type
    _SKILL_COLOR = {
        "attack":   C_RED2,
        "aoe":      C_PURPLE2,
        "multi":    C_ORANGE,
        "heal":     C_GREEN2,
        "heal_all": C_GREEN2,
        "defense":  C_BLUE,
    }

    def __init__(self, heroes: list):
        self.heroes  = heroes
        self.enemies = self._buat_musuh()
        self.engine  = BattleEngine(self.heroes, self.enemies)

        # HP bar untuk setiap karakter
        self.hp_bars_h = {h: HPBar(0, 0, 140, 14, h) for h in heroes}
        self.hp_bars_e = {e: HPBar(0, 0, 120, 12, e) for e in self.enemies}

        # State tampilan
        self.phase              = "player_turn"
        self.selected_hero_idx  = 0
        self.anim_timer         = 0
        self.turn_label         = ""
        self.tick               = 0

        # Rect layout kartu
        self.hero_rects:  list[pygame.Rect] = []
        self.enemy_rects: list[pygame.Rect] = []
        self.skill_btns:  list[Button]      = []

        self._bangun_layout()
        self._pilih_hero(0)

    # ── Setup ────────────────────────────────────────────────────────
    def _buat_musuh(self) -> list:
        pool  = [Shadow, DarkMage]
        count = random.randint(2, 3)
        return [random.choice(pool)(tier=1) for _ in range(count)]

    def _bangun_layout(self):
        """Hitung posisi kartu hero (bawah-kiri) dan musuh (atas-kanan)."""
        hw, hh, gap = 160, 110, 14
        for i in range(len(self.heroes)):
            self.hero_rects.append(
                pygame.Rect(30 + i * (hw + gap), SCREEN_H - hh - 14, hw, hh)
            )

        ew, eh = 150, 100
        ex = SCREEN_W - len(self.enemies) * (ew + gap) - 20
        for i in range(len(self.enemies)):
            self.enemy_rects.append(pygame.Rect(ex + i * (ew + gap), 14, ew, eh))

    def _pilih_hero(self, idx: int):
        """Ganti hero aktif dan bangun ulang tombol skill."""
        alive = self.engine.alive_heroes()
        if not alive:
            return
        self.selected_hero_idx = idx % len(alive)
        hero = alive[self.selected_hero_idx]

        self.skill_btns = []
        bw, bh = 190, 42
        sx = SCREEN_W // 2 - (2 * bw + 10) // 2
        for i, sk in enumerate(hero.skills):
            col = self._SKILL_COLOR.get(sk.skill_type, C_PANEL)
            row, col_pos = divmod(i, 2)
            self.skill_btns.append(Button(
                (sx + col_pos * (bw + 10), SCREEN_H - 240 + row * (bh + 8), bw, bh),
                f"{sk.icon} {sk.name}",
                col, lerp_color(col, C_WHITE, 0.2), F_SMALL,
            ))

    def _posisi_karakter(self, char) -> tuple:
        """Kembalikan koordinat tengah kartu karakter di layar."""
        for i, h in enumerate(self.heroes):
            if h is char and i < len(self.hero_rects):
                return self.hero_rects[i].center
        for i, e in enumerate(self.enemies):
            if e is char and i < len(self.enemy_rects):
                return self.enemy_rects[i].center
        return (SCREEN_W // 2, SCREEN_H // 2)

    # ── Update (dipanggil tiap frame) ───────────────────────────────
    def update(self, events) -> str:
        self.tick += 1
        mx, my = pygame.mouse.get_pos()

        # Update semua HP bar (animasi smooth)
        for bar in self.hp_bars_h.values(): bar.update()
        for bar in self.hp_bars_e.values(): bar.update()

        # Fase animasi — tunggu timer habis
        if self.phase == "anim":
            self.anim_timer -= 1
            if self.anim_timer <= 0:
                if self.turn_label == "player":
                    self.phase = "enemy_turn"
                    self._proses_giliran_musuh()
                else:
                    self.phase = "player_turn"
                    self._giliran_hero_berikutnya()

        # Fase hasil — klik untuk kembali ke menu
        if self.phase == "result":
            for e in events:
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN:
                    return "menu"
            return "battle"

        # Cek pemenang
        if self.engine.winner:
            self.phase = "result"
            return "battle"

        # Fase giliran hero — baca input
        if self.phase == "player_turn":
            alive = self.engine.alive_heroes()
            for btn in self.skill_btns:
                btn.check_hover((mx, my))

            for e in events:
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                # Tombol ◄ ► untuk ganti hero
                if e.type == pygame.KEYDOWN:
                    if e.key in (pygame.K_LEFT, pygame.K_a):
                        self._pilih_hero((self.selected_hero_idx - 1) % len(alive))
                    if e.key in (pygame.K_RIGHT, pygame.K_d):
                        self._pilih_hero((self.selected_hero_idx + 1) % len(alive))

                # Klik tombol skill
                for i, btn in enumerate(self.skill_btns):
                    if btn.is_clicked((mx, my), e):
                        self._hero_gunakan_skill(i)

                # Klik kartu hero untuk ganti aktif
                for i, r in enumerate(self.hero_rects):
                    if (i < len(alive)
                            and e.type == pygame.MOUSEBUTTONDOWN
                            and r.collidepoint(mx, my)):
                        self._pilih_hero(i)

        return "battle"

    # ── Aksi gameplay ───────────────────────────────────────────────
    def _hero_gunakan_skill(self, skill_idx: int):
        alive_heroes  = self.engine.alive_heroes()
        alive_enemies = self.engine.alive_enemies()
        if not alive_heroes or not alive_enemies:
            return

        hero = alive_heroes[self.selected_hero_idx]
        sk   = hero.skills[skill_idx]

        # Tentukan target berdasarkan tipe skill
        targets = (alive_heroes
                   if sk.skill_type in ("heal", "heal_all", "defense")
                   else alive_enemies)

        result = self.engine.hero_use_skill(hero, skill_idx, targets)

        # Spawn partikel di posisi target
        for char, col in result.get("particles", []):
            pos = self._posisi_karakter(char)
            spawn_particles(pos[0], pos[1], col, count=20)

        self.anim_timer  = 55
        self.turn_label  = "player"
        self.phase       = "anim"

    def _proses_giliran_musuh(self):
        results = self.engine.enemy_turn()
        for res in results:
            for char, col in res.get("particles", []):
                pos = self._posisi_karakter(char)
                spawn_particles(pos[0], pos[1], col, count=18)
        self.anim_timer = 55
        self.turn_label = "enemy"
        self.phase      = "anim"
        if self.engine.winner:
            self.phase = "result"

    def _giliran_hero_berikutnya(self):
        alive = self.engine.alive_heroes()
        if alive:
            self._pilih_hero(0)
        self.engine.turn += 1

    # ── Draw ────────────────────────────────────────────────────────
    def draw(self):
        screen.fill(C_BG)
        self._gambar_latar()
        self._gambar_musuh()
        self._gambar_hero()
        self._gambar_log()
        self._gambar_skill()
        self._gambar_info_giliran()
        update_particles(screen)
        if self.phase == "result":
            self._gambar_hasil()

    def _gambar_latar(self):
        # Grid tipis
        for x in range(0, SCREEN_W, 60):
            pygame.draw.line(screen, (15, 22, 35), (x, 0), (x, SCREEN_H))
        for y in range(0, SCREEN_H, 60):
            pygame.draw.line(screen, (15, 22, 35), (0, y), (SCREEN_W, y))
        # Glow eclipse di tengah
        glow_r    = 180 + int(math.sin(self.tick * 0.03) * 20)
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        for r in range(glow_r, 0, -20):
            a = int(8 * (r / glow_r))
            pygame.draw.circle(glow_surf, (80, 20, 100, a), (glow_r, glow_r), r)
        screen.blit(glow_surf, (SCREEN_W // 2 - glow_r, SCREEN_H // 2 - glow_r - 80))

    def _gambar_musuh(self):
        for enemy, rect in zip(self.enemies, self.enemy_rects):
            if not enemy.alive:
                s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                s.fill((10, 10, 10, 120))
                screen.blit(s, rect.topleft)
                draw_text_centered(screen, "💀 DEFEATED", F_TINY, C_GRAY,
                                   rect.centerx, rect.centery)
                continue
            draw_rounded_rect(screen, C_SHADOW_E, rect, 12, border=2, border_color=C_BORDER2)
            draw_text_centered(screen, enemy.get_role_icon(), F_BIG, enemy.color,
                               rect.centerx, rect.y + 22)
            draw_text_centered(screen, enemy.name, F_TINY, C_WHITE,
                               rect.centerx, rect.y + 52)
            bar = self.hp_bars_e[enemy]
            bar.x = rect.x + 8; bar.y = rect.y + 68
            bar.w = rect.w - 16; bar.h = 14
            bar.draw(screen)
            draw_text_centered(screen, f"ATK:{enemy.attack}  DEF:{enemy.defense}",
                               F_TINY, C_GRAY, rect.centerx, rect.y + 88)

    def _gambar_hero(self):
        alive_heroes = self.engine.alive_heroes()
        for i, (hero, rect) in enumerate(zip(self.heroes, self.hero_rects)):
            is_active = (i < len(alive_heroes)
                         and i == self.selected_hero_idx
                         and self.phase == "player_turn")

            if not hero.alive:
                s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                s.fill((10, 10, 10, 140))
                screen.blit(s, rect.topleft)
                draw_text_centered(screen, "💀", F_MED, C_GRAY,
                                   rect.centerx, rect.centery)
                continue

            # Kartu hero
            bg_col  = (15, 35, 20) if is_active else C_PANEL
            bdr_col = hero.color   if is_active else C_BORDER
            draw_rounded_rect(screen, bg_col, rect, 12,
                              border=3 if is_active else 2, border_color=bdr_col)

            # Glow kalau aktif
            if is_active:
                glow  = abs(math.sin(self.tick * 0.08))
                g_s   = pygame.Surface((rect.w + 20, rect.h + 20), pygame.SRCALPHA)
                pygame.draw.rect(g_s, (*hero.color, int(40 * glow)),
                                 (0, 0, rect.w + 20, rect.h + 20), border_radius=14)
                screen.blit(g_s, (rect.x - 10, rect.y - 10))
                draw_text_centered(screen, "▲ ACTIVE", F_TINY, C_GREEN,
                                   rect.centerx, rect.top - 12)

            draw_text_centered(screen, hero.get_role_icon(), F_MED, hero.color,
                               rect.centerx, rect.y + 18)
            draw_text_centered(screen, hero.name, F_TINY, C_WHITE,
                               rect.centerx, rect.y + 40)
            draw_text_centered(screen, hero.role, F_TINY, hero.color,
                               rect.centerx, rect.y + 56)
            bar = self.hp_bars_h[hero]
            bar.x = rect.x + 8; bar.y = rect.y + 72
            bar.w = rect.w - 16; bar.h = 14
            bar.draw(screen)
            draw_text_centered(screen, f"ATK:{hero.attack}  DEF:{hero.defense}",
                               F_TINY, C_GRAY, rect.centerx, rect.y + 93)

    def _gambar_log(self):
        lx, ly, lw, lh = SCREEN_W - 310, 130, 290, 200
        draw_rounded_rect(screen, C_PANEL, (lx, ly, lw, lh), 12,
                          border=1, border_color=C_BORDER)
        draw_text(screen, "📜 Battle Log", F_TINY, C_GOLD, lx + 10, ly + 8)
        recent = self.engine.log[-7:]
        for i, msg in enumerate(recent):
            col = C_WHITE if i == len(recent) - 1 else C_GRAY
            txt = F_TINY.render(msg[:40], True, col)
            screen.blit(txt, (lx + 8, ly + 28 + i * 22))

    def _gambar_skill(self):
        if self.phase != "player_turn":
            return
        alive = self.engine.alive_heroes()
        if not alive:
            return
        hero = alive[self.selected_hero_idx]

        draw_rounded_rect(screen, C_PANEL,
                          (SCREEN_W // 2 - 210, SCREEN_H - 255, 420, 135),
                          14, border=1, border_color=C_BORDER)
        draw_text_centered(screen, f"Skills — {hero.name}", F_SMALL, hero.color,
                           SCREEN_W // 2, SCREEN_H - 248)
        for btn in self.skill_btns:
            btn.draw(screen)
        draw_text_centered(screen,
                           "◄ ► atau klik hero  |  Klik skill untuk menyerang",
                           F_TINY, C_GRAY, SCREEN_W // 2, SCREEN_H - 115)

    def _gambar_info_giliran(self):
        label_map = {
            "player_turn": "🌿 GILIRAN HERO",
            "anim":        "⚡ ...",
            "enemy_turn":  "🌑 GILIRAN MUSUH",
            "result":      "SELESAI",
        }
        col = C_GREEN if self.phase == "player_turn" else C_RED
        draw_text_centered(screen,
                           f"Turn {self.engine.turn + 1}  |  {label_map.get(self.phase, '')}",
                           F_MED, col, SCREEN_W // 2, 12)
        draw_text_centered(screen, "— VS —", F_SMALL, C_GRAY,
                           SCREEN_W // 2, SCREEN_H // 2 - 30)

    def _gambar_hasil(self):
        # Overlay gelap
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        screen.blit(ov, (0, 0))

        won   = self.engine.winner == "hero"
        col   = C_GREEN if won else C_RED
        title = "🌿 MONSTERA MENANG!" if won else "🌑 ECLIPSE MENANG!"
        msg   = "Alam kembali bersinar!" if won else "Kegelapan menyelimuti dunia..."

        box = pygame.Rect(SCREEN_W // 2 - 260, SCREEN_H // 2 - 120, 520, 240)
        draw_rounded_rect(screen, C_DARK, box, 20, border=3, border_color=col)
        draw_text_centered(screen, title, F_BIG,   col,     SCREEN_W // 2, SCREEN_H // 2 - 70)
        draw_text_centered(screen, msg,   F_MED,   C_WHITE, SCREEN_W // 2, SCREEN_H // 2 - 20)
        draw_text_centered(screen, "Klik di mana saja untuk kembali ke menu",
                           F_SMALL, C_GRAY, SCREEN_W // 2, SCREEN_H // 2 + 40)

        # Efek partikel saat menang
        if won and self.tick % 4 == 0:
            spawn_particles(random.randint(100, SCREEN_W - 100),
                            SCREEN_H // 2, C_GREEN, count=5)
