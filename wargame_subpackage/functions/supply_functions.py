from classes.Hand import Hand 
from classes.Card import Card
    
def create_supply_hand(supply):
    """
    Create a 'hand' reflecting purchase options from supply
    """
    supply_hand = Hand()
    [supply_hand.add_card(card) for card in set(supply.all_cards)]
    return supply_hand

def reset_supply(supply):
      for rank in Card.ranks[:-1]:
            for i in range(5):
                supply.add_cards(Card(rank))
    