import pygame
import random
import math

pygame.init()
pygame.mixer.init()


# ┌─────────────────────────────────────────────────────┐
# │  [1] KONSTANTA LAYAR & FPS                          │
# └─────────────────────────────────────────────────────┘

SCREEN_W, SCREEN_H = 1100, 700
FPS = 60

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("🌿 Monstera Eclipse 🌑")
clock = pygame.time.Clock()


# ┌─────────────────────────────────────────────────────┐
# │  [2] PALET WARNA                                    │
# └─────────────────────────────────────────────────────┘

# Background & panel
C_BG      = (8,   12,  20)
C_DARK    = (14,  22,  38)
C_PANEL   = (18,  30,  50)
C_PANEL2  = (22,  38,  62)

# Border
C_BORDER  = (40,  80,  60)
C_BORDER2 = (80,  40,  80)

# Warna tema hero
C_GREEN   = (60,  200, 100)   # Warrior
C_GREEN2  = (30,  140,  70)
C_PURPLE  = (160,  60, 220)   # Mage
C_PURPLE2 = (100,  30, 160)
C_GOLD    = (220, 180,  60)   # Ranger
C_ORANGE  = (230, 120,  40)
C_HEAL    = (60,  220, 140)   # Healer

# Warna aksi
C_RED     = (220,  60,  60)   # Damage / musuh
C_RED2    = (160,  30,  30)
C_BLUE    = (60,  140, 220)   # Defense
C_CYAN    = (60,  210, 200)   # Shield / buff

# Teks & UI
C_WHITE   = (230, 235, 245)
C_GRAY    = (100, 110, 130)
C_GRAY2   = (60,   70,  90)

# Musuh
C_SHADOW_E = (30,  10,  50)


# ┌─────────────────────────────────────────────────────┐
# │  [3] FONT                                           │
# └─────────────────────────────────────────────────────┘

def _load_font(size, bold=False):
    try:
        return pygame.font.SysFont("segoeui", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)

F_TITLE = _load_font(64, bold=True)   # judul layar
F_BIG   = _load_font(36, bold=True)   # tombol besar
F_MED   = _load_font(24, bold=True)   # label sedang
F_SMALL = _load_font(18)              # teks biasa
F_TINY  = _load_font(14)              # teks kecil / stat


# ┌─────────────────────────────────────────────────────┐
# │  [4] FUNGSI UTILITAS GAMBAR                         │
# └─────────────────────────────────────────────────────┘

def draw_rounded_rect(surf, color, rect, radius=12, border=0, border_color=None):
    """Gambar rect dengan sudut membulat, opsional border berwarna."""
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)


def draw_text_centered(surf, text, font, color, cx, cy):
    """Render teks di tengah koordinat (cx, cy)."""
    s = font.render(text, True, color)
    surf.blit(s, (cx - s.get_width() // 2, cy - s.get_height() // 2))


def draw_text(surf, text, font, color, x, y):
    """Render teks di koordinat kiri-atas (x, y)."""
    s = font.render(text, True, color)
    surf.blit(s, (x, y))


def lerp_color(c1, c2, t):
    """Interpolasi linier antara dua warna. t = 0.0 → c1, t = 1.0 → c2."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


# ┌─────────────────────────────────────────────────────┐
# │  [5] SISTEM PARTIKEL                                │
# └─────────────────────────────────────────────────────┘

class Particle:
    """
    Satu partikel visual — muncul saat serangan / heal.
    Bergerak, memudar, lalu hilang ketika life habis.
    """
    def __init__(self, x, y, color, vx=None, vy=None, life=None, size=None):
        self.x        = x
        self.y        = y
        self.color    = color
        self.vx       = vx   if vx   is not None else random.uniform(-2, 2)
        self.vy       = vy   if vy   is not None else random.uniform(-3, -0.5)
        self.life     = life if life is not None else random.randint(30, 70)
        self.max_life = self.life
        self.size     = size if size is not None else random.randint(2, 5)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.05        # gravitasi ringan
        self.life -= 1

    def draw(self, surf):
        alpha = self.life / self.max_life
        r  = int(self.color[0] * alpha)
        g  = int(self.color[1] * alpha)
        b  = int(self.color[2] * alpha)
        sz = max(1, int(self.size * alpha))
        pygame.draw.circle(surf, (r, g, b), (int(self.x), int(self.y)), sz)


# List global — diakses oleh game.py dan main.py
particles: list = []


def spawn_particles(x, y, color, count=15, spread=20):
    """Tambah sejumlah partikel di sekitar (x, y)."""
    for _ in range(count):
        px = x + random.randint(-spread, spread)
        py = y + random.randint(-spread, spread)
        particles.append(Particle(px, py, color))


def update_particles(surf):
    """Update + gambar semua partikel; buang yang sudah mati."""
    for p in particles[:]:
        p.update()
        p.draw(surf)
        if p.life <= 0:
            particles.remove(p)


# ┌─────────────────────────────────────────────────────┐
# │  [6] KOMPONEN UI — Button & HPBar                   │
# └─────────────────────────────────────────────────────┘

class Button:
    """
    Tombol klik dengan efek hover.

    Params:
        rect        : (x, y, w, h)
        text        : label yang ditampilkan
        color       : warna normal
        hover_color : warna saat kursor di atasnya
        font        : pygame.Font (default F_MED)
        text_color  : warna teks
        radius      : kelengkungan sudut
    """

    def __init__(self, rect, text, color, hover_color,
                 font=None, text_color=None, radius=10):
        self.rect        = pygame.Rect(rect)
        self.text        = text
        self.color       = color
        self.hover_color = hover_color
        self.font        = font       or F_MED
        self.text_color  = text_color or C_WHITE
        self.radius      = radius
        self.hovered     = False

    def draw(self, surf):
        col        = self.hover_color if self.hovered else self.color
        border_col = C_GREEN if self.hovered else C_BORDER
        draw_rounded_rect(surf, col, self.rect, self.radius,
                          border=2, border_color=border_col)
        draw_text_centered(surf, self.text, self.font, self.text_color,
                           self.rect.centerx, self.rect.centery)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos, event) -> bool:
        return (event.type == pygame.MOUSEBUTTONDOWN
                and self.rect.collidepoint(pos))


class HPBar:
    """
    Bar HP animasi smooth (lerp) dengan warna dinamis.

    Warna:
        > 60%  → hijau
        30-60% → emas
        < 30%  → merah
    """

    def __init__(self, x, y, w, h, char):
        self.x    = x
        self.y    = y
        self.w    = w
        self.h    = h
        self.char = char
        self._display_hp = float(char.hp)

    def update(self):
        """Gerakkan display HP perlahan mendekati HP aktual."""
        self._display_hp += (self.char.hp - self._display_hp) * 0.12

    def draw(self, surf):
        ratio = max(0.0, self._display_hp / self.char.max_hp)

        # Latar
        draw_rounded_rect(surf, C_GRAY2, (self.x, self.y, self.w, self.h), 4)

        # Isi bar
        col = C_GREEN if ratio > 0.6 else (C_GOLD if ratio > 0.3 else C_RED)
        fill_w = int(self.w * ratio)
        if fill_w > 0:
            draw_rounded_rect(surf, col, (self.x, self.y, fill_w, self.h), 4)

        # Border tipis
        pygame.draw.rect(surf, C_BORDER,
                         (self.x, self.y, self.w, self.h), 1, border_radius=4)

        # Teks HP
        hp_text = F_TINY.render(
            f"{int(self._display_hp)}/{self.char.max_hp}", True, C_WHITE
        )
        surf.blit(hp_text, (
            self.x + self.w // 2 - hp_text.get_width()  // 2,
            self.y + self.h // 2 - hp_text.get_height() // 2,
        ))
