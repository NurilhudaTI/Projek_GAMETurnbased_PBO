# 🌿 Monstera Eclipse - Turn-Based Battle Game

## 📋 Deskripsi Project

**Monstera Eclipse** adalah permainan turn-based RPG battle system yang dikembangkan menggunakan **Python** dan **Pygame**. Game ini menampilkan sistem pertempuran taktis di mana pemain memilih tim hero dari 3 kelas berbeda untuk melawan wave musuh yang semakin sulit. 

Setiap karakter memiliki mekanik unik dengan skill-skill khusus, animasi sprite yang dinamis, dan sistem level progression dengan 12 tingkat kesulitan. Game ini menggabungkan konsep game design profesional dengan implementasi Object-Oriented Programming yang solid.

---

## 👥 Anggota Kelompok

| Nama | Peran |
|------|-------|
| **M. Ikliluddin Al Wafi** | Lead Developer |
| **Kevin Ahmadinejad** | Game Mechanics & Balance |
| **Valentinus Satrio Dewwanto** | UI/UX & Asset Management |
| **Moch Nuril Huda** | SFX & Audio System |

---

## ⭐ Fitur Utama

### 1. **Sistem Hero Beragam**
- **Warrior** (Verdant Knight) - Penyerang fisik dengan defense tinggi
  - Skill: Vine Slash, Root Shield, Thorn Burst, Earth Smash
- **Mage** (Flora Sorceress) - Damage output tinggi dengan AoE attack
  - Skill: Petal Storm, Spore Cloud, Arcane Bloom, Mystic Veil
- **Healer** (Bloom Sage) - Support dan recovery hero
  - Skill: Nature's Touch, Rain of Life, Thorn Whip, Revitalize
- **Ranger** (Swift Scout) - Balanced attacker dengan cepat
  - Skill: Pierce Shot, Multi-Shot, Evasive Stance, Rapid Fire

### 2. **Sistem Musuh Progresif**
- **Shadow** - Musuh ringan dengan kecepatan tinggi
- **Dark Mage** - Penyerang magic dengan AoE
- **Boss Eclipse** - Boss tier dengan multiple phase dan special abilities

### 3. **Sistem Level & Progresso**
- **12 Level Progression** dengan 4 tier kesulitan (Hijau, Redup, Gelap, Eclipse)
- Difficulty stars yang meningkat seiring level
- Dynamic enemy pool yang berbeda per tier
- Post-win healing dengan persentase menurun seiring level naik

### 4. **Animasi & Visual**
- Sprite sheet animation system untuk semua karakter
- Particle effects untuk damage/skill visual feedback
- Background dinamis untuk battle dan menu
- Smooth sprite transition & state management

### 5. **Sistem Audio**
- Background music untuk menu dan battle
- Sound effects untuk setiap skill dan aksi
- Character-specific attack sounds
- UI feedback sounds

### 6. **UI Interaktif**
- Menu screen dengan multiple options
- Party selection screen dengan preview karakter
- Settings panel untuk kontrol musik
- Battle log untuk melihat history action
- Level up screen dengan healing recap
- Game clear screen untuk victory feedback

---

## 🚀 Cara Menjalankan Project

### Prasyarat
```bash
Python 3.8+
Pygame 2.0+
```

### Instalasi Dependencies
```bash
pip install pygame
```

### Struktur Folder yang Dibutuhkan
```
monstera-eclipse/
├── assets/
│   ├── images/
│   │   ├── characters/
│   │   │   ├── warrior_sheet.png
│   │   │   ├── mage_sheet.png
│   │   │   ├── healer_sheet.png
│   │   │   ├── ranger_sheet.png
│   │   │   ├── shadow_sheet.png
│   │   │   ├── dark_mage_sheet.png
│   │   │   └── boss_eclipse_sheet.png
│   │   └── backgrounds/
│   │       ├── menu_bg.png
│   │       └── battle_bg.png
│   └── sounds/
│       ├── music/
│       │   ├── menu_theme.mp3
│       │   └── battle_theme.mp3
│       └── sfx/
│           ├── warrior_attack.wav
│           ├── mage_attack.wav
│           └── [SFX files lainnya...]
├── main.py
├── game.py
├── config.py
├── aset_game.py
├── sfx_manager.py
└── README.md
```

### Menjalankan Game
```bash
python main.py
```

---

## 🏗️ Penjelasan Implementasi OOP

### 1. **Abstraksi (Abstraction) - Base Class `Character`**

Semua karakter dalam game mewarisi dari class abstrak `Character` yang mendefinisikan interface umum:

```python
class Character:
    def __init__(self, name, max_hp, attack, defense, speed, color):
        self._name = name
        self._hp = max_hp
        self._max_hp = max_hp
        # ... properties lainnya
    
    def take_damage(self, raw_dmg: int) -> int:
        """Hitung damage dengan mempertimbangkan defense"""
        actual = max(1, raw_dmg - self._defense)
        self._hp = max(0, self._hp - actual)
        return actual
    
    def use_skill(self, skill_index, targets, allies):
        """Method abstrak yang diimplementasikan di subclass"""
        raise NotImplementedError
```

**Manfaat:**
- Menghilangkan code duplication
- Memastikan setiap karakter memiliki interface yang konsisten
- Mudah menambah karakter baru

---

### 2. **Inheritance (Pewarisan)**

#### Hero Class Hierarchy
```
        Character (Base)
            |
        Hero (Abstract Hero)
         /  |  \  \
        /   |   \   \
    Warrior Mage Healer Ranger
```

#### Enemy Class Hierarchy
```
        Character (Base)
            |
        Enemy (Base Enemy)
         /   |   \
        /    |    \
    Shadow DarkMage BossEclipse
```

**Contoh Implementasi:**
```python
class Hero(Character):
    def __init__(self, name, max_hp, attack, defense, speed, color, role):
        super().__init__(name, max_hp, attack, defense, speed, color)
        self._role = role
    
    @property
    def role(self):
        return self._role

class Warrior(Hero):
    def __init__(self, name="Verdant Knight"):
        super().__init__(name, max_hp=180, attack=35, defense=20,
                         speed=12, color=C_GREEN, role="Warrior")
        self._skills = [
            Skill("Vine Slash", "Serangan fisik kuat ke 1 musuh", "attack", 1.4, C_GREEN, "[ATK]"),
            # ... skill lainnya
        ]
    
    def use_skill(self, skill_index, targets, allies):
        # Implementasi spesifik Warrior
```

**Manfaat Inheritance:**
- Setiap hero memiliki stat dan skill unik
- Method `use_skill` di-override untuk behavior spesifik
- Polymorphism memungkinkan handling semua hero dengan cara yang sama

---

### 3. **Polymorphism (Polimorfisme)**

```python
# Di battle loop, semua karakter ditangani dengan cara yang sama
for character in action_queue:
    # Character bisa Warrior, Mage, Healer, Shadow, DarkMage, atau BossEclipse
    result = character.use_skill(skill_index, targets, allies)
    
    # Tapi behavior berbeda untuk setiap tipe!
    # Warrior: Single target + AoE support
    # Mage: High damage magical attacks
    # Healer: Healing + support abilities
```

**Method Polymorphic:**
- `use_skill()` - berbeda untuk setiap karakter
- `take_damage()` - sama untuk semua (inherited)
- `heal()` - sama untuk semua (inherited)

---

### 4. **Encapsulation (Enkapsulasi)**

Semua property karakter dilindungi dengan underscore (`_property`) dan diakses via property decorators:

```python
class Character:
    def __init__(self, name, max_hp, ...):
        self._name = name
        self._hp = max_hp
        self._attack = attack
        # ...
    
    @property
    def name(self):
        return self._name
    
    @property
    def hp(self):
        return self._hp
    
    @property
    def attack(self):
        return self._attack
```

**Manfaat:**
- Data tidak bisa dimodifikasi langsung dari luar (kontrol akses)
- Logic validasi bisa ditambahkan di setter jika diperlukan
- Interface yang clean dan predictable

---

### 5. **Composition (Komposisi)**

#### Skill System
```python
class Skill:
    def __init__(self, name, description, skill_type, power, color, icon):
        self.name = name
        self.description = description
        self.skill_type = skill_type
        self.power = power
        self.color = color
        self.icon = icon

class Hero(Character):
    def __init__(self, ...):
        super().__init__(...)
        self._skills = []  # Composition: Hero HAS-A list of Skills
```

#### Asset & Animation System
```python
class SpriteSheet:
    """Manages character animation frames"""

class CharacterAnimator:
    """Manages animation state"""
    def __init__(self, sheet: SpriteSheet, spf: int = 6):
        self.sheet = sheet  # Composition

class AssetManager:
    def __init__(self):
        self._sheets: dict[str, SpriteSheet] = {}        # Has-A SpriteSheet
        self._animators: dict[int, CharacterAnimator] = {}  # Has-A Animators
```

**Manfaat Composition:**
- Reusable components (Skill dapat digunakan oleh berbagai Hero)
- Flexible architecture
- Mudah di-test dan di-maintain

---

### 6. **Dependency Injection**

```python
class BattleScreen:
    def __init__(self, heroes: list, level_system: LevelSystem):
        self.heroes = heroes
        self.level_system = level_system
        # Dependencies di-inject melalui constructor
```

**Manfaat:**
- Loose coupling antar class
- Mudah untuk testing dan mocking
- Flexibility dalam runtime

---

### 7. **Singleton Pattern**

```python
# sfx_manager.py
class SFXManager:
    def __init__(self):
        self._sounds = {}
        self._initialized = False

sfx = SFXManager()  # Global singleton instance

# aset_game.py
class AssetManager:
    def __init__(self):
        self._sheets = {}

asset_manager = AssetManager()  # Global singleton instance
```

**Penggunaan:**
```python
# Di mana saja dalam project
from sfx_manager import sfx
from aset_game import asset_manager

sfx.play("warrior_attack")
asset_manager.init()
```

**Manfaat:**
- Memastikan hanya satu instance dari manager yang ada
- Akses global tanpa parameter passing
- Konsistensi state di seluruh aplikasi

---

## 📊 Class Diagram Relationship

```
┌─────────────────────────────────────────────────────────────┐
│                    Character (Abstract)                      │
│  ─────────────────────────────────────────────────────────  │
│  - _name, _hp, _max_hp, _attack, _defense, _speed, _color  │
│  + take_damage(dmg) → actual_damage                         │
│  + heal(amount) → healed_amount                             │
│  + use_skill(index, targets, allies) → result (Abstract)   │
└────────────────┬──────────────────────────────────────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
 ┌────▼──────┐         ┌───▼────┐
 │    Hero   │         │ Enemy  │
 │           │         │        │
 └────┬──────┘         └───┬────┘
      │                    │
   ┌──┼──┬──┐          ┌───┼────┬──────────┐
   │  │  │  │          │   │    │          │
┌─▼─┐│  │  │      ┌───▼──┐│┌──▼────┐ ┌──▼───────┐
│War││Ma│He│Ran   │Shado││Dark   │Boss
│rio││ge│al││      │ow   ││Mage   │Eclipse
└───┘│  │  │      └─────┘└───────┘ └────────┘
   │  │  │
   └─────┘

Has-A Relationships:
─────────────────────
Hero ────────> Skill (composition)
CharacterAnimator ──> SpriteSheet (composition)
BattleScreen ──> Hero[] (dependency)
BattleScreen ──> Enemy[] (dependency)
BattleScreen ──> LevelSystem (dependency)
```

---

## 🎮 Game Flow Diagram

```
┌─────────────────┐
│  MenuScreen     │
│  - Play Game    │──┐
│  - Settings     │  │
│  - Quit         │  │
└────────┬────────┘  │
         │           │
         │      ┌────▼─────────────┐
         │      │SettingsScreen    │
         │      │ - Toggle Music    │
         │      │ - Back to Menu    │
         │      └───────┬──────────┘
         │              │
         └──────────────┘
                 │
         ┌───────▼──────────┐
         │ PartySelectScreen │
         │ - Choose 3 Heroes │
         │ - Preview Stats   │
         │ - Start Battle    │
         └────────┬──────────┘
                  │
         ┌────────▼──────────┐
         │  BattleScreen     │
         │ - Turn-based      │
         │ - Skill Selection │
         │ - Damage Calc     │
         │ - Win/Lose Check  │
         └────────┬──────────┘
                  │
          ┌───────┴────────┐
          │ Hero Win?      │
          └──┬──────────┬──┘
             │          │
          YES│          │NO
             │          └─────────────┐
             │                        │
         ┌───▼────────────┐  ┌───────▼─────┐
         │ LevelUpScreen  │  │GameOverScreen│
         │ - Heal Reward  │  │ - Return Menu│
         │ - Next Level?  │  └──────────────┘
         └───┬────────────┘
             │
         ┌───▼──────────┐
         │Final Level?  │
         └──┬────────┬──┘
            │        │
         YES│        │NO
            │        └─┬─────────────┐
            │          │ (Battle Next)
            │          └──────────────┘
            │
      ┌─────▼────────────┐
      │GameClearScreen   │
      │ - Victory Banner │
      │ - Return Menu    │
      └──────────────────┘
```

---

## 🎨 Fitur Teknis

### Animasi & Rendering
- **SpriteSheet Parsing**: Membaca frame dari sprite sheet berdasarkan posisi
- **Frame-based Animation**: Update frame setiap N ticks
- **Alpha Blending**: Particle effects dengan fade out
- **Sprite Transformation**: Flip horizontal dan scale

### Game Logic
- **Turn-based System**: Queue action berdasarkan speed
- **Damage Calculation**: `actual_dmg = max(1, raw_dmg - defense)`
- **Healing System**: `healed = min(amount, max_hp - current_hp)`
- **Level Progression**: Scaling musuh & reward berdasarkan tier

### State Management
- **LevelSystem**: Menyimpan state progression game
- **Character State**: Alive/dead, current HP, status effects
- **Animation State**: Current animation state, frame index, tick counter

---

## 📁 File Structure & Responsibilities

| File | Fungsi |
|------|--------|
| `main.py` | Entry point - main game loop & state management |
| `config.py` | Global constants - colors, fonts, screen settings |
| `game.py` | Game logic - Character classes, Battle screen, UI screens |
| `aset_game.py` | Asset management - Sprite loading, animation system |
| `sfx_manager.py` | Sound management - SFX & music playback |

---

## 🖼️ Screenshot & Tampilan

### 1. Menu Screen
```
┌──────────────────────────────────────────────┐
│                                              │
│           🌿 MONSTERA ECLIPSE 🌿            │
│                                              │
│          ╔════════════════════════╗          │
│          ║   [Play Game]          ║          │
│          ║   [Settings]           ║          │
│          ║   [Quit]               ║          │
│          ╚════════════════════════╝          │
│                                              │
└──────────────────────────────────────────────┘
```

### 2. Party Select Screen
```
┌──────────────────────────────────────────────┐
│         SELECT YOUR PARTY (Choose 3)         │
│                                              │
│  ┌────────────┐  ┌────────────┐             │
│  │  [Warrior] │  │  [Mage]    │             │
│  │ ATK: 35    │  │ ATK: 55    │             │
│  │ DEF: 20    │  │ DEF: 8     │             │
│  │ SPD: 12    │  │ SPD: 16    │             │
│  └────────────┘  └────────────┘             │
│                                              │
│  ┌────────────┐  ┌────────────┐             │
│  │ [Healer]   │  │ [Ranger]   │             │
│  │ ATK: 22    │  │ ATK: 42    │             │
│  │ DEF: 14    │  │ DEF: 12    │             │
│  │ SPD: 14    │  │ SPD: 18    │             │
│  └────────────┘  └────────────┘             │
│                                              │
│  Selected: Warrior, Mage, Healer            │
│  [← Back]                    [Start Battle] │
└──────────────────────────────────────────────┘
```

### 3. Battle Screen (In-Combat)
```
┌──────────────────────────────────────────────┐
│  LEVEL 1 - Hijau ★★★★☆ - Enemies: 2        │
├──────────────────────────────────────────────┤
│                                              │
│   HEROES                    ENEMIES          │
│  ┌─────────────┐    ┌─────────────────┐    │
│  │ Warrior     │    │ Shadow         │    │
│  │ HP: ████████│50  │ HP: ███░░░░    │18  │
│  │ [SKL1][SKL2]│    │ Shadow         │    │
│  │ [SKL3][SKL4]│    │ HP: ███░░░░    │18  │
│  └─────────────┘    └─────────────────┘    │
│  ┌─────────────┐                            │
│  │ Mage        │                            │
│  │ HP: ████░░░░│30  BATTLE LOG:             │
│  │ [SKL1][SKL2]│    > Warrior used          │
│  │ [SKL3][SKL4]│      Vine Slash!           │
│  └─────────────┘    > Shadow took 24 DMG   │
│  ┌─────────────┐    > Shadow attacked!     │
│  │ Healer      │    > Warrior took 15 DMG  │
│  │ HP: ████░░░░│40  > Mage's turn...      │
│  │ [SKL1][SKL2]│                           │
│  │ [SKL3][SKL4]│                           │
│  └─────────────┘                           │
│                                              │
│  [AUTO]                    [END TURN]       │
└──────────────────────────────────────────────┘
```

### 4. Level Up Screen
```
┌──────────────────────────────────────────────┐
│          VICTORY! LEVEL 1 COMPLETE           │
├──────────────────────────────────────────────┤
│                                              │
│  HEALING REWARDS:                           │
│  ✓ Warrior pulih 72 HP (40%)                │
│  ✓ Mage pulih 44 HP (40%)                   │
│  ✓ Healer pulih 52 HP (40%)                 │
│                                              │
│  NEXT LEVEL: Redup ★★★★★                    │
│  Enemies: 3                                  │
│  Difficulty: Moderate                        │
│                                              │
│  Current Tier: Hijau → Redup                │
│                                              │
│               [NEXT BATTLE]                 │
│                 [QUIT GAME]                 │
│                                              │
└──────────────────────────────────────────────┘
```

### 5. Game Clear Screen
```
┌──────────────────────────────────────────────┐
│                                              │
│         🏆 GAME COMPLETE! 🏆                │
│                                              │
│    Congratulations! All 12 Levels Clear!    │
│                                              │
│  Final Party:                               │
│  • Warrior  - HP: 180/180                   │
│  • Mage     - HP: 110/110                   │
│  • Healer   - HP: 130/130                   │
│                                              │
│  Total Score: [CALCULATED]                  │
│                                              │
│              [RETURN TO MENU]               │
│                                              │
└──────────────────────────────────────────────┘
```

---

## 🔧 Teknologi yang Digunakan

- **Language**: Python 3.8+
- **Game Engine**: Pygame 2.0+
- **Graphics**: Sprite sheets + Pygame drawing
- **Audio**: Pygame mixer (MP3/WAV)
- **Architecture**: Object-Oriented Programming (OOP)

---

## 💡 Design Patterns Digunakan

| Pattern | Lokasi | Fungsi |
|---------|--------|--------|
| **Singleton** | `sfx_manager.py`, `aset_game.py` | Memastikan hanya satu instance manager |
| **Factory** | `LevelSystem.generate_enemies()` | Membuat enemy berdasarkan tier |
| **Observer** | `BattleScreen.update()` | Memantau state character |
| **State** | `CharacterAnimator` | Manage animation state |
| **Template Method** | `Character.take_damage()` | Define algoritma umum |
| **Composition** | `Hero._skills`, `AssetManager._sheets` | Flexible object composition |

---

## 🎯 Kesimpulan

Monstera Eclipse mendemonstrasikan implementasi OOP yang solid dengan:

✅ **Clear Inheritance Hierarchy** - Hero & Enemy classes  
✅ **Polymorphism** - Different skill implementations  
✅ **Encapsulation** - Protected properties & public interfaces  
✅ **Composition** - Skills, Animators, SpriteSheets  
✅ **Abstraction** - Abstract base Character class  
✅ **Design Patterns** - Singleton, Factory, State  
✅ **SOLID Principles** - Single Responsibility, Open/Closed  

Game ini dapat diperluas dengan mudah untuk menambah hero baru, musuh baru, skill baru, atau fitur gameplay tanpa merusak existing code.

---

**Happy Playing! 🌿🎮✨**
