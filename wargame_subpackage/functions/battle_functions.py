from time import sleep
from .abilities_functions import activate_ability

def get_winner(p1card, p2card):
    if p1card > p2card:
        return ("P1","P2")
    elif p1card < p2card:
        return ("P2", "P1")
    else:
        return ("Draw", "Draw")
    
def get_difference(p1card, p2card):
    return abs(p1card.value - p2card.value)

def reduce_losers_health(loser, x):
    loser.change_health(-1 * x)

def run_battle(p1, p2, supply):
    # Battle
    # get p1 card and p2 card\
    for i in range(3):
        print(f"Battle {i+1}")
        
        p1card = p1.cards_played[i]
        p2card = p2.cards_played[i]
        print(f"{p1.name} plays a {p1.cards_played[i]}")
        print(f"{p2.name} plays a {p2.cards_played[i]}")

        winner, loser = get_winner(p1card, p2card)
        diff = get_difference(p1card, p2card)
        if loser == "P1":
            reduce_losers_health(p1, diff)
            p2.change_money(diff)
            print(f"{p1.name} loses {diff} hp.\n")
            activate_ability(p1card, p1, p2, supply)
                        
        elif loser == "P2":
            reduce_losers_health(p2, diff)
            p1.change_money(diff)
            print(f"{p2.name} loses {diff} hp.\n")
            activate_ability(p2card, p2, p1, supply)
        else:
            print("A draw, no damage.\n")
        
        p1.print_health_status()
        p2.print_health_status()
        print()
        if p1.check_health() == "game_over" or p2.check_health() == "game_over":
            return "game_over"
        
        sleep(1)

def run_battle_version2(p1, p2, supply):
    """
    Version 2
    Damage = Overall difference in values
    Resolve 3 abilities, then resolve overall damage.
    Money = 1 coin per victory (e.g. up to 3 coins available per round)
    """
    # Battle
    # get p1 card and p2 card\
    for i in range(3):
        print(f"Battle {i+1}")
        
        p1card = p1.cards_played[i]
        p2card = p2.cards_played[i]
        print(f"{p1.name} plays a {p1.cards_played[i]}")
        print(f"{p2.name} plays a {p2.cards_played[i]}")

        winner, loser = get_winner(p1card, p2card)
        #diff = get_difference(p1card, p2card)
        if loser == "P1":
            p2.change_money(1)
            activate_ability(p1card, p1, p2, supply)                        
        elif loser == "P2":
            p1.change_money(1)
            activate_ability(p2card, p2, p1, supply)
        else:
            print("A draw, no ability was activated.\n")
        
        print()

        if p1.check_health() == "game_over" or p2.check_health() == "game_over":
            return "game_over"
        
        sleep(1)

    p1.get_damage()
    p2.get_damage()
    print(f"{p1.name} has {p1.damage} attack power, {p2.name} has {p2.damage} attack power.")
    if p1.damage > p2.damage:
        p2.change_health(p2.damage - p1.damage)
        print(f"{p1.name} does {p1.damage - p2.damage} damage to {p2.name}.")
        print(f"{p2.name} has {p2.health} HP remaining.")
    elif p2.damage > p1.damage:
        p1.change_health(p1.damage - p2.damage)
        print(f"{p2.name} does {p2.damage - p1.damage} damage to {p1.name}.")
        print(f"{p1.name} has {p1.health} HP remaining.")
    else:
        print("A draw, no damage is done.")

    print()

    # Reset damage after the battle for next round
    p1.damage = 0
    p2.damage = 0

