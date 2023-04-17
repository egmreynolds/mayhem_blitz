"""
Abilities:
    Reduce damage done by x
    ### Heal x
    ### Add a 'curse' to winners deck
    ### Trash a card from your hand
    Add a card to deck of value x
    ### Inflict x damage to opponent
    ### Trash the card that lost (for high value cards that shouldn't lose)
    Trash a card from hand and add a card with value of 1 higher than it
    ### Trash the card that lost and 'upgrade' it
    ### Cause opponent to draw less cards next turn (or owner to draw more?)
    ###This card stays on the battlefield, adding it's strength to the next battle? (e.g. Skeleton stays and adds one) 
    ## Card staying on battlefield for rest of game
    ## Get 1 coin for losing

    'Draw' powers - probably only useful when there's more than one type of card with that value.
    # Should powers activate before or after damage done?
"""

from classes.Card import Card


def activate_ability(card, owner, opponent, supply):
    if card.rank == "Curse" or card.rank == "King":
        return
    
    print(f"Ability Activated: {card}")
    # Each card has an ability
    # Do I need if/else statements to find the ability that matches cardname? Not so bad for now, but with >20 abilities it would be.
    if card.rank == "Guard":
        trash_card_from_hand(owner)       
    elif card.rank == "Priest":
        add_card_from_supply(opponent, supply, Card("Curse"))
    elif card.rank == "Baron":
        inflict_damage(opponent, 1)
        owner.change_money(1)
    elif card.rank == "Handmaid":
        heal(owner, 3)
    elif card.rank == "Prince":
        trash_card_from_play(owner, card)    
    elif card.rank == "Lich":
        trash_card_from_play(owner, card)
        owner.select_from_supply(supply, card.value + 1)
    elif card.rank == "Slime":
        opponent.change_number_of_cards_to_draw(-1)
    elif card.rank == "Orc":
        owner.change_number_of_cards_to_draw(1)
    elif card.rank == "Goblin":
        pass
    elif card.rank == "Warlord":
        pass
    elif card.rank == "Skeleton":
        owner.add_to_additional_cards_in_play(card) # Need further help if the card is to stay for the rest of the game

def activate_ability_v2(card, owner, opponent, supply):
    """
    V2 = returns text_output and action - strings for display to activate.
    """
    if card.rank in ["Curse", "King", "Goblin", "Warlord", "Soldier"]: # cards with no ability
        return (f"{card.rank} lost,\n nothing happens...\n", "")
    
    print(f"Ability Activated: {card}")
    # Each card has an ability
    # Do I need if/else statements to find the ability that matches cardname? Not so bad for now, but with >20 abilities it would be.
    if card.rank == "Guard":
        #trash_card_from_hand(owner) -  actions needing choices are now done elsewhere
        return (f"{owner.name} can\n trash a card\n from their hand.\n\n", "guard")  
    elif card.rank == "Priest":
        add_card_from_supply(opponent, supply, Card("Curse"))
        return (f"A Curse\n was added to {opponent.name}'s\n discard pile.\n\n", "")
    elif card.rank == "Baron":
        inflict_damage(opponent, 1)
        owner.change_money(1)
        return (f"{opponent.name} took\n 1 damage.\n {owner.name} gained\n 1 coin.\n\n", "")
    elif card.rank == "Handmaid":
        heal(owner, 3)
        return (f"{owner.name} healed\n 3 HP.\n\n", "")
    elif card.rank == "Prince":
        trash_card_from_play(owner, card)    
        return (f"{owner.name}'s {card.rank}\n was trashed.\n\n", "")
    elif card.rank == "Lich":
        trash_card_from_play(owner, card)
        #owner.select_from_supply(supply, card.value + 1) - actions needing choices are now done elsewhere
        return (f"{owner.name} trashed\n their {card.rank} and\n selected a new card\n from supply.\n\n", "lich")
    elif card.rank == "Slime":
        opponent.change_number_of_cards_to_draw(-1)
        return (f"{opponent.name} will\n draw 1 less card\n next round.\n\n", "")
    elif card.rank == "Orc":
        owner.change_number_of_cards_to_draw(1)
        return (f"{owner.name} will\n draw 1 more card\n next round.\n\n", "")
    elif card.rank == "Skeleton":
        owner.add_to_additional_cards_in_play(card) # this is still done here as it's not a choice, display update will be required? 
        return (f"{owner.name}'s {card.rank}\n will remain\n on the battlefield.\n\n", "")
    elif card.rank == "Matyr":
        owner.set_multiplier(2)
        return (f"{owner.name}'s damage\n will be doubled\n this round.\n\n")


def heal(player, heal = 3):
    player.change_health(heal)  
    print(f"{player.name} healed {heal} HP.")
    
def trash_card_from_play(player, card):
    """
    Trash the card that lost the battle.
    """
    player.cards_played.remove(card)   
    print(f"{player.name}'s {card} was trashed.")
    
def trash_card_from_hand(player):
    """
    Choose card in hand that hasn't been played.
    Remove it permanently from the game.   
    Return it's value.
    """
    player.get_cards_to_trash(num = 1)    

def add_card_from_supply(player, supply, card):
    """
    If supply contains card, add it to discard pile of player
    """
    if card in supply.all_cards:
        supply.remove_card(card)
        player.discard.add_cards(card)
        print(f"A {card} has been added to {player.name}'s discard pile")
    else:
        print(f"No {card}'s remain in the supply and cannot be added to {player.name}'s discard pile")

def inflict_damage(player, damage = 1):
    player.change_health(-1 * damage)
    print(f"{player.name} was hit by spikes and lost {damage} HP")    
        



