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

