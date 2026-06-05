import pygame
import sys
import random
import math
import os

pygame.init()
pygame.mixer.init()

# CONSTANTS
SCREEN_W, SCREEN_H = 1100, 700
FPS = 60

# Color Palette — Premium Dark Fantasy
C_BG        = (10,  8,  18)       # Deep void black
C_DARK      = (16, 14,  32)
C_PANEL     = (20, 18,  42)       # Dark panel
C_PANEL2    = (28, 24,  56)       # Lighter panel
C_BORDER    = (80, 160, 100)      # Green border
C_BORDER2   = (140, 60, 200)      # Purple border
C_GREEN     = (80,  220, 120)     # Bright green
C_GREEN2    = (40,  160,  80)     # Mid green
C_PURPLE    = (180,  80, 240)     # Bright purple
C_PURPLE2   = (120,  40, 180)     # Mid purple
C_GOLD      = (255, 200,  70)     # Bright gold
C_GOLD2     = (180, 140,  40)     # Dark gold
C_ORANGE    = (255, 140,  50)     # Orange
C_RED       = (240,  70,  70)     # Bright red
C_RED2      = (180,  35,  35)     # Dark red
C_BLUE      = (70,  160, 255)     # Bright blue
C_CYAN      = (80,  230, 220)     # Bright cyan
C_WHITE     = (240, 245, 255)     # Bright white
C_GRAY      = (120, 130, 150)     # Mid gray
C_GRAY2     = (55,   60,  80)     # Dark gray
C_HEAL      = (80,  240, 160)     # Heal green
C_SHADOW_E  = (30,  10,  50)
C_ACCENT    = (255, 180,  50)     # Warm accent / highlight
C_GLASS     = (30,  26,  60)      # Glass panel bg

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Monstera Eclipse")
clock = pygame.time.Clock()

# FONTS
def load_font(size, bold=False):
    try:
        return pygame.font.SysFont("segoeui", size, bold=bold)
    except:
        return pygame.font.Font(None, size)

F_TITLE  = load_font(64, bold=True)
F_BIG    = load_font(36, bold=True)
F_MED    = load_font(24, bold=True)
F_SMALL  = load_font(18)
F_TINY   = load_font(14)

# UTILITY
def draw_rounded_rect(surf, color, rect, radius=12, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)

def draw_text_centered(surf, text, font, color, cx, cy):
    s = font.render(text, True, color)
    surf.blit(s, (cx - s.get_width()//2, cy - s.get_height()//2))

def draw_text(surf, text, font, color, x, y):
    s = font.render(text, True, color)
    surf.blit(s, (x, y))

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

