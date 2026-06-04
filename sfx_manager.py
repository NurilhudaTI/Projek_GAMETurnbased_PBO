"""
sfx_manager.py — Sound Effects Manager untuk Monstera Eclipse.
Load semua SFX satu kali, play kapanpun dibutuhkan.
"""

import pygame
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SFX_DIR  = os.path.join(BASE_DIR, "assets", "sounds", "sfx")

class SFXManager:
    def __init__(self):
        self._sounds = {}
        self._initialized = False
        self.enabled = True

    def init(self):
        if self._initialized:
            return
        self._initialized = True
        pygame.mixer.set_num_channels(16)

        files = {
            # Hero attacks
            "warrior_attack":  "warrior_attack.wav",
            "warrior_aoe":     "warrior_skill_aoe.wav",
            "warrior_heavy":   "warrior_skill_heavy.wav",
            "mage_attack":     "mage_attack.wav",
            "mage_burst":      "mage_skill_burst.wav",
            "mage_aoe":        "mage_skill_aoe.wav",
            "healer_attack":   "healer_attack.wav",
            "healer_heal":     "healer_heal.wav",
            "healer_revive":   "healer_skill_revive.wav",
            # Enemy attacks
            "demon_attack":    "demon_attack.wav",
            "demon_skill":     "demon_skill.wav",
            "golem_attack":    "golem_attack.wav",
            "golem_aoe":       "golem_skill_aoe.wav",
            "boss_attack":     "boss_attack.wav",
            "boss_aoe":        "boss_skill_aoe.wav",
            "boss_armor":      "boss_skill_armor.wav",
            "boss_multi":      "boss_skill_multi.wav",
            # Hit reactions
            "hit_physical":    "hit_physical.wav",
            "hit_magic":       "hit_magic.wav",
            "hit_heavy":       "hit_heavy.wav",
            # UI
            "ui_hover":        "ui_hover.wav",
            "ui_confirm":      "ui_confirm.wav",
            "ui_select":       "ui_select.wav",
            "ui_cancel":       "ui_cancel.wav",
            "ui_start":        "ui_start.wav",
            # Events
            "victory":         "victory.wav",
            "defeat":          "defeat.wav",
            "level_start":     "level_start.wav",
            "level_up":        "level_up.wav",
        }

        for key, fname in files.items():
            path = os.path.join(SFX_DIR, fname)
            if os.path.isfile(path):
                try:
                    snd = pygame.mixer.Sound(path)
                    snd.set_volume(0.55)
                    self._sounds[key] = snd
                except Exception as e:
                    print(f"[SFX] Failed {key}: {e}")

        print(f"[SFX] Loaded {len(self._sounds)} sounds.")

    def play(self, key: str, volume: float = None):
        if not self.enabled:
            return
        snd = self._sounds.get(key)
        if snd:
            if volume is not None:
                snd.set_volume(volume)
            snd.play()

    def play_attack(self, char):
        """Otomatis pilih SFX berdasarkan tipe karakter."""
        from game import Warrior, Mage, Healer, Shadow, DarkMage, BossEclipse
        if isinstance(char, Warrior):
            self.play("warrior_attack")
        elif isinstance(char, Mage):
            self.play("mage_attack")
        elif isinstance(char, Healer):
            self.play("healer_attack")
        elif isinstance(char, BossEclipse):
            self.play("boss_attack")
        elif isinstance(char, DarkMage):
            self.play("golem_attack")
        elif isinstance(char, Shadow):
            self.play("demon_attack")

    def play_skill(self, char, skill_type: str):
        """Pilih SFX skill berdasarkan karakter + tipe skill."""
        from game import Warrior, Mage, Healer, Shadow, DarkMage, BossEclipse
        if isinstance(char, Warrior):
            self.play("warrior_aoe" if skill_type == "aoe" else "warrior_heavy")
        elif isinstance(char, Mage):
            self.play("mage_aoe" if skill_type == "aoe" else "mage_burst")
        elif isinstance(char, Healer):
            self.play("healer_revive" if skill_type == "heal" else "healer_heal")
        elif isinstance(char, BossEclipse):
            if skill_type == "aoe":    self.play("boss_aoe")
            elif skill_type == "buff": self.play("boss_armor")
            elif skill_type == "multi":self.play("boss_multi")
            else:                      self.play("boss_attack")
        elif isinstance(char, DarkMage):
            self.play("golem_aoe" if skill_type == "aoe" else "golem_attack")
        elif isinstance(char, Shadow):
            self.play("demon_skill")

    def play_hit(self, attacker):
        """SFX saat kena hit — based on attacker type."""
        from game import Warrior, BossEclipse, DarkMage
        if isinstance(attacker, BossEclipse):
            self.play("hit_heavy")
        elif isinstance(attacker, (Warrior, DarkMage)):
            self.play("hit_physical")
        else:
            self.play("hit_magic")


# Global singleton
sfx = SFXManager()
