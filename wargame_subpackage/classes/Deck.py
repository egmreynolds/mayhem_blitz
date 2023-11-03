import random 

class Deck:
    def __init__(self):
        self.all_cards = []
        
    def add_cards(self, cards):
        if type(cards) == type([]):
            self.all_cards.extend(cards)
        else:  
            self.all_cards.append(cards)
    
    def remove_card(self, card):
        if card in self.all_cards:
            self.all_cards.remove(card)
        else:
            print(f"{card} isn't in deck...")
            
    def shuffle(self):
        random.shuffle(self.all_cards)
    
    def draw_card(self):
        return self.all_cards.pop(0) 
    
    def is_empty(self):
        return self.all_cards == []    

    def get_deck_size(self):
        return len(self.all_cards)

    
    def display_supply(self):
        """
        Print out supply
        Bugfix: Should be in order of value.
        """
        print("Supply")
        [print(f"{card} : Available cards: {self.all_cards.count(card)}") for card in set(self.all_cards)]        
    
    def __str__(self):
        if len(self.all_cards) == 0:
            return "Deck is empty."
        return ", ".join([f"{card}" for card in self.all_cards])
        