from time import sleep
from wargame_subpackage.classes.Card import Card
from wargame_subpackage.classes.Deck import Deck
from wargame_subpackage.classes.Player import Player
from wargame_subpackage.functions.supply_functions import reset_supply
from wargame_subpackage.functions.battle_functions import run_battle, run_battle_version2

def play_game():
    p1 = Player("P1")
    p1.setup_deck()
    p2 = Player("P2")
    p2.setup_deck()
    supply = Deck()
    reset_supply(supply)
    round = 0

    while True:
        round += 1
        print(f"\nRound {round} begins.\n")
        p1.draw_hand()
        p1.get_play_order()
        p1.print_cards_played()

        p2.draw_hand()
        p2.get_play_order()
        p2.print_cards_played()
        print()
        if run_battle_version2(p1, p2, supply) == "game_over":
            print("End")
            break

        p1.purchase_phase(supply)
        p2.purchase_phase(supply)
        p1.discard_hand()
        p1.discard_cards_played()
        p2.discard_hand()
        p2.discard_cards_played()
        p1.end_round_reset()
        p2.end_round_reset()

        sleep(3)


if __name__ == '__main__':
    play_game()
