import os
import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets", "extracted")

# Mapping role/karakter ke file aset.
# Catatan: Knight berasal dari Knight.rar. Jika sudah diekstrak manual ke assets/extracted/Knight,
# loader akan memakai KnightIdle_strip.png. Kalau belum, loader memakai Frost Guardian sebagai fallback
# agar game tetap bisa berjalan.
SPRITE_PATHS = {
    "warrior": [
        os.path.join(ASSET_DIR, "Knight", "noBKG_KnightIdle_strip.png"),
        os.path.join(ASSET_DIR, "Knight", "KnightIdle_strip.png"),
        os.path.join(ASSET_DIR, "Frost_Guardian_FREE_v1.0", "PNG files", "idle", "idle_1.png"),
    ],
    "mage": [
        os.path.join(ASSET_DIR, "Little Mage", "Idle", "Idle1.png"),
        os.path.join(ASSET_DIR, "Little Mage", "ALL Spritesheet.png"),
    ],
    "healer": [
        os.path.join(ASSET_DIR, "Tiny RPG Character Asset Pack v1.03 -Free Soldier&Orc", "Characters(100x100)", "Soldier", "Soldier with shadows", "Soldier-Idle.png"),
        os.path.join(ASSET_DIR, "Tiny RPG Character Asset Pack v1.03 -Free Soldier&Orc", "Characters(100x100)", "Soldier", "Soldier", "Soldier-Idle.png"),
    ],
    "ranger": [
        os.path.join(ASSET_DIR, "ranger", "idle.png"),
    ],
    "shadow": [
        os.path.join(ASSET_DIR, "Flying Demon 2D Pixel Art", "Sprites", "with_outline", "IDLE.png"),
        os.path.join(ASSET_DIR, "Flying Demon 2D Pixel Art", "Sprites", "without_outline", "IDLE.png"),
    ],
    "dark_mage": [
        os.path.join(ASSET_DIR, "mino_v1.1_free", "animations", "idle", "idle_1.png"),
        os.path.join(ASSET_DIR, "Frost_Guardian_FREE_v1.0", "PNG files", "idle", "idle_1.png"),
    ],
}


def _first_existing(paths):
    for path in paths:
        if os.path.exists(path):
            return path
    return None


class AssetManager:
    def __init__(self):
        self._cache = {}

    def _crop_first_frame(self, image):
        """Ambil frame pertama jika file berupa spritesheet strip horizontal."""
        w, h = image.get_size()
        if w > h * 2:
            # Banyak spritesheet berbentuk beberapa frame sejajar horizontal.
            # Ambil frame pertama dengan ukuran tinggi x tinggi.
            frame_w = h
            rect = pygame.Rect(0, 0, min(frame_w, w), h)
            cropped = pygame.Surface(rect.size, pygame.SRCALPHA)
            cropped.blit(image, (0, 0), rect)
            return cropped
        return image

    def load_sprite(self, key, size=(74, 74), flip=False):
        cache_key = (key, size, flip)
        if cache_key in self._cache:
            return self._cache[cache_key]

        path = _first_existing(SPRITE_PATHS.get(key, []))
        if not path:
            self._cache[cache_key] = None
            return None

        try:
            image = pygame.image.load(path).convert_alpha()
            image = self._crop_first_frame(image)
            image = pygame.transform.smoothscale(image, size)
            if flip:
                image = pygame.transform.flip(image, True, False)
            self._cache[cache_key] = image
            return image
        except Exception:
            self._cache[cache_key] = None
            return None

    def draw_sprite(self, surface, key, center, size=(74, 74), flip=False):
        sprite = self.load_sprite(key, size, flip)
        if sprite:
            rect = sprite.get_rect(center=center)
            surface.blit(sprite, rect)
            return True
        return False


asset_manager = AssetManager()
