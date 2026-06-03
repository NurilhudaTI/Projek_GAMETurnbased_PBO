import pygame
import sys

from config import FPS, clock
from game import MenuScreen, SettingsScreen, PartySelectScreen, BattleScreen

def main():
    state      = "menu"
    music_on   = False
    menu_scr   = MenuScreen()
    settings_scr = None
    party_scr  = None
    battle_scr = None

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
                state = "menu"

        elif state == "select_party":
            next_state, data = party_scr.update(events)
            party_scr.draw()
            if next_state == "menu":
                menu_scr = MenuScreen()
                state = "menu"
            elif next_state == "battle":
                battle_scr = BattleScreen(data)
                state = "battle"

        elif state == "battle":
            next_state = battle_scr.update(events)
            battle_scr.draw()
            if next_state == "menu":
                menu_scr = MenuScreen()
                state = "menu"

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()