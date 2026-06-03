import pygame
import sys
import random
import math

from config import (
    screen, clock, FPS,
    SCREEN_W, SCREEN_H,
    C_BG, C_DARK, C_PANEL, C_PANEL2, C_BORDER,
    C_GREEN, C_GREEN2, C_PURPLE, C_GOLD, C_CYAN,
    C_RED, C_RED2, C_HEAL,
    C_WHITE, C_GRAY, C_GRAY2,
    F_TITLE, F_BIG, F_MED, F_SMALL, F_TINY,
    draw_rounded_rect, draw_text_centered, lerp_color,
    Button,
)
from game import (
    Warrior, Mage, Healer, Ranger,
    BattleScreen,
)


# ════════════════════════════════════════════════════════════════════
#  [1] MENU SCREEN
# ════════════════════════════════════════════════════════════════════

class MenuScreen:

    def __init__(self):
        self.tick = 0
        self.buttons = [
            Button((SCREEN_W // 2 - 130, 330, 260, 52), "START GAME", C_GREEN2, C_GREEN, F_BIG),
            Button((SCREEN_W // 2 - 130, 400, 260, 52), "SETTINGS", C_PANEL2, C_PANEL, F_BIG),
            Button((SCREEN_W // 2 - 130, 470, 260, 52), "EXIT", C_RED2, C_RED, F_BIG),
        ]
        self.orbs = [
            (
                random.randint(50, SCREEN_W - 50),
                random.randint(50, SCREEN_H - 50),
                random.uniform(0, math.pi * 2),
                random.uniform(0.5, 2),
                random.choice([C_GREEN, C_PURPLE, C_GOLD, C_CYAN]),
            )
            for _ in range(18)
        ]

    def update(self, events) -> str:
        self.tick += 1
        mx, my = pygame.mouse.get_pos()
        for b in self.buttons:
            b.check_hover((mx, my))
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
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
            orb = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(orb, (*col, 60), (10, 10), 10)
            screen.blit(orb, (int(x) - 10, int(y) - 10))
        glow = abs(math.sin(self.tick * 0.04))
        draw_text_centered(screen, "MONSTERA", F_TITLE,
                           lerp_color(C_GREEN, C_CYAN, glow), SCREEN_W // 2, 170)
        draw_text_centered(screen, "ECLIPSE", F_TITLE,
                           lerp_color(C_PURPLE, C_RED, glow), SCREEN_W // 2, 240)
        draw_text_centered(screen, "⚔️ Turn-Based RPG ⚔️",
                           F_SMALL, C_GRAY, SCREEN_W // 2, 295)
        for b in self.buttons:
            b.draw(screen)
        draw_text_centered(screen, "© Monstera Eclipse Team",
                           F_TINY, C_GRAY2, SCREEN_W // 2, SCREEN_H - 20)

class SettingsScreen:

    def __init__(self, music_on: bool):
        self.music_on  = music_on
        self.back_btn  = Button((30, 30, 120, 40), "← Back",
                                C_PANEL2, C_PANEL, F_SMALL)
        self.music_btn = Button(
            (SCREEN_W // 2 - 130, 280, 260, 52),
            "🔊 Music: ON" if music_on else "🔇 Music: OFF",
            C_GREEN2 if music_on else C_GRAY2, C_GREEN, F_MED,
        )

    def update(self, events) -> tuple:
        mx, my = pygame.mouse.get_pos()
        self.back_btn.check_hover((mx, my))
        self.music_btn.check_hover((mx, my))
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if self.back_btn.is_clicked((mx, my), e):
                return "menu", self.music_on
            if self.music_btn.is_clicked((mx, my), e):
                self.music_on       = not self.music_on
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
        draw_text_centered(screen, "Controls: Mouse + Click to play",
                           F_SMALL, C_GRAY, SCREEN_W // 2, 370)
        self.back_btn.draw(screen)


class PartySelectScreen:

    HERO_CLASSES = [Warrior, Mage,             Healer,         Ranger]
    HERO_NAMES   = ["Verdant Knight", "Flora Sorceress", "Bloom Sage", "Moss Hunter"]
    HERO_ROLES   = ["Warrior ⚔️",    "Mage 🔮",         "Healer 💚",  "Ranger 🏹"]
    HERO_ICONS   = ["⚔️",            "🔮",               "💚",         "🏹"]
    HERO_COLORS  = [C_GREEN,          C_PURPLE,           C_HEAL,       C_GOLD]
    HERO_DESCS   = [
        ["HP: 180 (Tinggi)",  "ATK: 35 | DEF: 20", "SPD: 12 — Tank",      "AoE & Shield"],
        ["HP: 110 (Rendah)",  "ATK: 55 | DEF: 8",  "SPD: 16 — Burst DMG", "Sihir tinggi"],
        ["HP: 130 (Medium)",  "ATK: 22 | DEF: 14", "SPD: 14 — Support",   "Heal & serang"],
        ["HP: 145 (Medium)",  "ATK: 40 | DEF: 12", "SPD: 18 — Tercepat",  "Multi-target"],
    ]

    def __init__(self):
        self.selected: set = set()
        self.hovered = -1
        self.start_btn = Button((SCREEN_W // 2 - 140, SCREEN_H - 70, 280, 48),
                                 "⚔️  START BATTLE", C_GREEN2, C_GREEN, F_BIG)
        self.back_btn  = Button((30, 30, 120, 40), "← Back", C_PANEL2, C_PANEL, F_SMALL)
        cw, ch  = 220, 280
        gap     = 24
        total_w = 4 * cw + 3 * gap
        sx      = (SCREEN_W - total_w) // 2
        self.card_rects = [
            pygame.Rect(sx + i * (cw + gap), 130, cw, ch) for i in range(4)
        ]

    def update(self, events) -> tuple:
        mx, my = pygame.mouse.get_pos()
        self.start_btn.check_hover((mx, my))
        self.back_btn.check_hover((mx, my))
        self.hovered = -1
        for i, r in enumerate(self.card_rects):
            if r.collidepoint(mx, my):
                self.hovered = i
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if self.back_btn.is_clicked((mx, my), e):
                return "menu", []
            if e.type == pygame.MOUSEBUTTONDOWN:
                for i, r in enumerate(self.card_rects):
                    if r.collidepoint(mx, my):
                        if i in self.selected:
                            self.selected.discard(i)
                        elif len(self.selected) < 3:
                            self.selected.add(i)
            if self.start_btn.is_clicked((mx, my), e) and self.selected:
                heroes = [self.HERO_CLASSES[i]() for i in sorted(self.selected)]
                return "battle", heroes
        return "select_party", []

    def draw(self):
        screen.fill(C_BG)
        draw_text_centered(screen, "🌿 PILIH PARTY HERO (maks 3)",
                           F_BIG, C_WHITE, SCREEN_W // 2, 55)
        draw_text_centered(screen, f"Dipilih: {len(self.selected)}/3",
                           F_MED, C_GREEN if self.selected else C_GRAY,
                           SCREEN_W // 2, 95)
        for i, r in enumerate(self.card_rects):
            sel = i in self.selected
            hov = i == self.hovered
            bg         = (20, 55, 35) if sel else C_PANEL2
            border_col = self.HERO_COLORS[i] if sel else (C_WHITE if hov else C_BORDER)
            draw_rounded_rect(screen, bg, r, 16,
                              border=3 if sel else 2, border_color=border_col)
            cx = r.centerx
            icon_surf = F_TITLE.render(self.HERO_ICONS[i], True, self.HERO_COLORS[i])
            screen.blit(icon_surf, (cx - icon_surf.get_width() // 2, r.y + 12))
            draw_text_centered(screen, self.HERO_ROLES[i],
                               F_MED, self.HERO_COLORS[i], cx, r.y + 90)
            draw_text_centered(screen, self.HERO_NAMES[i],
                               F_SMALL, C_WHITE, cx, r.y + 118)
            for j, desc in enumerate(self.HERO_DESCS[i]):
                draw_text_centered(screen, desc, F_TINY, C_GRAY, cx, r.y + 146 + j * 22)
            if sel:
                draw_text_centered(screen, "✔ DIPILIH", F_SMALL, C_GREEN, cx, r.bottom - 22)
        if self.selected:
            self.start_btn.draw(screen)
        else:
            draw_rounded_rect(screen, C_GRAY2,
                              (SCREEN_W // 2 - 140, SCREEN_H - 70, 280, 48), 10)
            draw_text_centered(screen, "Pilih minimal 1 hero",
                               F_MED, C_GRAY, SCREEN_W // 2, SCREEN_H - 46)
        self.back_btn.draw(screen)


def main():

    state        = "menu"
    music_on     = False
    menu_scr     = MenuScreen()
    settings_scr = None
    party_scr    = None
    battle_scr   = None

    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        if state == "menu":
            next_state = menu_scr.update(events)
            menu_scr.draw()
            if next_state != "menu":
                if next_state == "select_party":
                    party_scr = PartySelectScreen()
                elif next_state == "settings":
                    settings_scr = SettingsScreen(music_on)
                state = next_state

        elif state == "settings":
            next_state, music_on = settings_scr.update(events)
            settings_scr.draw()
            if next_state == "menu":
                menu_scr = MenuScreen()
                state    = "menu"

        elif state == "select_party":
            next_state, data = party_scr.update(events)
            party_scr.draw()
            if next_state == "menu":
                menu_scr = MenuScreen()
                state    = "menu"
            elif next_state == "battle":
                battle_scr = BattleScreen(data)
                state      = "battle"

        elif state == "battle":
            next_state = battle_scr.update(events)
            battle_scr.draw()
            if next_state == "menu":
                menu_scr = MenuScreen()
                state    = "menu"

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
