import pygame
import sys
import random
import math
import os

pygame.init()
pygame.mixer.init()

SCREEN_W, SCREEN_H = 1100, 700
FPS = 60

C_BG = (8, 12, 20)
C_DARK = (14, 22, 38)
C_PANEL = (18, 30, 50)
C_PANEL2 = (22, 38, 62)
C_BORDER = (40, 80, 60)
C_BORDER2 = (80, 40, 80)
C_GREEN = (60, 200, 100)
C_GREEN2 = (30, 140, 70)
C_PURPLE = (160, 60, 220)
C_PURPLE2 = (100, 30, 160)
C_GOLD = (220, 180, 60)
C_ORANGE = (230, 120, 40)
C_RED = (220, 60, 60)
C_RED2 = (160, 30, 30)
C_BLUE = (60, 140, 220)
C_CYAN = (60, 210, 200)
C_WHITE = (230, 235, 245)
C_GRAY = (100, 110, 130)
C_GRAY2 = (60, 70, 90)
C_HEAL = (60, 220, 140)
C_SHADOW_E = (30, 10, 50)

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption(" Monstera Eclipse ")
clock = pygame.time.Clock()
