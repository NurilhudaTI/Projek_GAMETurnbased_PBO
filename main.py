"""Main game loop — Monstera Eclipse dengan sistem level bertahap."""

import pygame
import sys
from config import *
from game import (
    MenuScreen, SettingsScreen, PartySelectScreen,
    BattleScreen, LevelUpScreen, GameClearScreen,
    LevelSystem, particles
)


def main():
    pygame.init()
    pygame.mixer.init()

    clock     = pygame.time.Clock()
    music_on  = True
    state     = "menu"

    # Objek screen aktif
    menu_screen   = MenuScreen()
    battle_screen = None
    settings_screen = None
    party_screen  = None
    levelup_screen  = None
    gameclear_screen = None

    # State global yang bertahan antar battle
    heroes       = []
    level_system = LevelSystem()   # ← satu instance sepanjang run game

    # ── BGM ──────────────────────────────────────────────────────────────────
    try:
        pygame.mixer.music.load("assets/sounds/music/battle_theme.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except Exception:
        pass  # tidak ada file musik — tetap jalan

    # ── MAIN LOOP ─────────────────────────────────────────────────────────────
    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # ── MENU ──────────────────────────────────────────────────────────
        if state == "menu":
            # Reset level system setiap kali kembali ke menu
            level_system = LevelSystem()
            heroes = []
            particles.clear()

            result = menu_screen.update(events)
            menu_screen.draw()
            if result == "select_party":
                party_screen = PartySelectScreen()
                state = "select_party"
            elif result == "settings":
                settings_screen = SettingsScreen(music_on)
                state = "settings"

        # ── SETTINGS ──────────────────────────────────────────────────────
        elif state == "settings":
            result, music_on = settings_screen.update(events)
            settings_screen.draw()
            if music_on:
                pygame.mixer.music.set_volume(0.5)
            else:
                pygame.mixer.music.set_volume(0)
            if result == "menu":
                state = "menu"

        # ── PARTY SELECT ──────────────────────────────────────────────────
        elif state == "select_party":
            result, data = party_screen.update(events)
            party_screen.draw()
            if result == "menu":
                state = "menu"
            elif result == "battle":
                heroes = data
                level_system = LevelSystem()          # level mulai dari 1
                battle_screen = BattleScreen(heroes, level_system)
                state = "battle"

        # ── BATTLE ────────────────────────────────────────────────────────
        elif state == "battle":
            result = battle_screen.update(events)
            battle_screen.draw()

            if result == "hero_win":
                # Hero menang satu level → terapkan heal reward
                heal_log = []
                pct = level_system.heal_percent
                for hero in heroes:
                    if hero.alive:
                        amount = int(hero.max_hp * pct)
                        healed = hero.heal(amount)
                        heal_log.append(f"{hero.name} pulih {healed} HP")

                # Naikkan level
                level_system.advance()

                if level_system.is_game_cleared:
                    # Semua 12 level selesai → game clear screen
                    gameclear_screen = GameClearScreen()
                    state = "game_clear"
                else:
                    # Tampilkan layar level up
                    levelup_screen = LevelUpScreen(level_system, heroes, heal_log)
                    state = "level_up"

            elif result == "menu":
                # Hero kalah → balik ke menu
                state = "menu"

        # ── LEVEL UP (transisi) ───────────────────────────────────────────
        elif state == "level_up":
            result = levelup_screen.update(events)
            levelup_screen.draw()

            if result == "battle_next":
                # Mulai battle berikutnya dengan hero yang sama (HP sudah di-heal)
                battle_screen = BattleScreen(heroes, level_system)
                state = "battle"
            elif result == "menu":
                state = "menu"

        # ── GAME CLEAR ────────────────────────────────────────────────────
        elif state == "game_clear":
            result = gameclear_screen.update(events)
            gameclear_screen.draw()
            if result == "menu":
                state = "menu"

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()