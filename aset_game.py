"""
aset_game.py — Asset & Animation Manager untuk Monstera Eclipse.

Sistem ini mendukung DUA mode per karakter:
  1. Sprite sheet  : satu PNG berisi banyak frame (kolom = frame, baris = state)
  2. Fallback icon : emoji/teks jika file PNG tidak ditemukan

Format sprite sheet yang dipakai:
  - Setiap baris = 1 state: 0=idle, 1=run, 2=attack, 3=hurt, 4=die
  - Setiap kolom = 1 frame

State index:
  IDLE    = 0
  RUN     = 1
  ATTACK  = 2
  HURT    = 3
  DIE     = 4
"""

import pygame
import os

# ── State constants ───────────────────────────────────────────────────────────
ANIM_IDLE   = 0
ANIM_RUN    = 1
ANIM_ATTACK = 2
ANIM_HURT   = 3
ANIM_DIE    = 4

# ── Per-key config: (sheet_filename, frame_w, frame_h, frames_per_row, n_states, fps_per_state)
SPRITE_CONFIG = {
    #  key             filename                 fw   fh  cols states spf
    "warrior":    ("warrior_sheet.png",          96,  96,  15,   5,   5),
    "mage":       ("mage_sheet.png",             96,  96,  15,   5,   5),
    "healer":     ("healer_sheet.png",           96,  96,  15,   5,   5),
    "ranger":     ("ranger_sheet.png",           96,  96,  15,   5,   5),
    "shadow":     ("shadow_sheet.png",           96,  96,   8,   4,   4),
    "dark_mage":  ("dark_mage_sheet.png",        96,  96,   8,   4,   4),
    "boss_eclipse":("boss_eclipse_sheet.png",   120, 120,   8,   5,   6),
}

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "assets", "images", "characters")


class SpriteSheet:
    """Memuat satu sprite sheet dan menyediakan akses per frame."""
    def __init__(self, path, frame_w, frame_h, cols, n_states):
        self.frame_w  = frame_w
        self.frame_h  = frame_h
        self.cols     = cols
        self.n_states = n_states
        self._sheet   = pygame.image.load(path).convert_alpha()
        self.frames = []
        for row in range(n_states):
            row_frames = []
            for col in range(cols):
                rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
                surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                surf.blit(self._sheet, (0, 0), rect)
                row_frames.append(surf)
            self.frames.append(row_frames)

    def get_frame(self, state: int, frame_idx: int) -> pygame.Surface:
        state     = min(state, self.n_states - 1)
        frame_idx = frame_idx % self.cols
        return self.frames[state][frame_idx]


class CharacterAnimator:
    """
    Mengelola animasi satu karakter.
    """
    def __init__(self, sheet: SpriteSheet, spf: int = 6):
        self.sheet         = sheet
        self.spf           = spf
        self.state         = ANIM_IDLE
        self.frame_idx     = 0
        self.tick          = 0
        self._queued_state = None
        self._one_shot     = False

    def set_state(self, state: int, one_shot: bool = False):
        if self.state == state and not one_shot:
            return
        self.state     = state
        self.frame_idx = 0
        self.tick      = 0
        self._one_shot = one_shot
        if one_shot:
            self._queued_state = ANIM_IDLE

    def update(self):
        self.tick += 1
        if self.tick >= self.spf:
            self.tick = 0
            self.frame_idx += 1
            if self.frame_idx >= self.sheet.cols:
                self.frame_idx = 0
                if self._one_shot and self._queued_state is not None:
                    self.state     = self._queued_state
                    self._one_shot = False

    def get_surface(self, size=None, flip=False) -> pygame.Surface:
        surf = self.sheet.get_frame(self.state, self.frame_idx)
        if flip:
            surf = pygame.transform.flip(surf, True, False)
        if size and size != (self.sheet.frame_w, self.sheet.frame_h):
            surf = pygame.transform.scale(surf, size)
        return surf

    def is_done(self) -> bool:
        return self._one_shot is False and self._queued_state is None


class AssetManager:
    """
    Singleton manager: load semua sprite sheet saat init.
    """
    def __init__(self):
        self._sheets:    dict[str, SpriteSheet]       = {}
        self._animators: dict[int, CharacterAnimator] = {}
        self._bg:        pygame.Surface | None        = None
        self._menu_bg:   pygame.Surface | None        = None
        self._initialized = False

    def init(self):
        """Panggil setelah pygame.init() dan display dibuat."""
        if self._initialized:
            return
        self._initialized = True

        for key, (fname, fw, fh, cols, n_states, spf) in SPRITE_CONFIG.items():
            path = os.path.join(IMAGES_DIR, fname)
            if os.path.isfile(path):
                try:
                    self._sheets[key] = SpriteSheet(path, fw, fh, cols, n_states)
                    print(f"[AssetManager] Loaded sheet: {key}")
                except Exception as e:
                    print(f"[AssetManager] Failed to load {key}: {e}")
            else:
                print(f"[AssetManager] Sheet not found (fallback): {path}")

        # Load battle background
        bg_path = os.path.join(BASE_DIR, "assets", "images", "backgrounds", "battle_bg.png")
        if os.path.isfile(bg_path):
            try:
                from config import SCREEN_W, SCREEN_H
                raw = pygame.image.load(bg_path).convert()
                self._bg = pygame.transform.scale(raw, (SCREEN_W, SCREEN_H))
                print("[AssetManager] Loaded battle background.")
            except Exception as e:
                print(f"[AssetManager] Failed to load battle_bg: {e}")

        # Load menu background
        menu_path = os.path.join(BASE_DIR, "assets", "images", "backgrounds", "menu_bg.png")
        if os.path.isfile(menu_path):
            try:
                from config import SCREEN_W, SCREEN_H
                raw = pygame.image.load(menu_path).convert()
                self._menu_bg = pygame.transform.scale(raw, (SCREEN_W, SCREEN_H))
                print("[AssetManager] Loaded menu background.")
            except Exception as e:
                print(f"[AssetManager] Failed to load menu_bg: {e}")

    def get_animator(self, char_obj, key: str) -> CharacterAnimator | None:
        char_id = id(char_obj)
        if char_id not in self._animators:
            if key not in self._sheets:
                return None
            cfg = SPRITE_CONFIG[key]
            spf = cfg[5]
            self._animators[char_id] = CharacterAnimator(self._sheets[key], spf)
        return self._animators.get(char_id)

    def remove_animator(self, char_obj):
        self._animators.pop(id(char_obj), None)

    def update_all(self):
        for anim in self._animators.values():
            anim.update()

    def draw_sprite(self, surf, key, center, size=(96, 96), flip=False):
        if key not in self._sheets:
            return False
        sheet = self._sheets[key]
        frame = sheet.get_frame(ANIM_IDLE, 0)
        if size:
            frame = pygame.transform.scale(frame, size)
        if flip:
            frame = pygame.transform.flip(frame, True, False)
        x = center[0] - frame.get_width()  // 2
        y = center[1] - frame.get_height() // 2
        surf.blit(frame, (x, y))
        return True

    def get_background(self) -> pygame.Surface | None:
        return self._bg

    def get_menu_background(self) -> pygame.Surface | None:
        return self._menu_bg

    def has_sheet(self, key: str) -> bool:
        return key in self._sheets


# Global singleton
asset_manager = AssetManager()
