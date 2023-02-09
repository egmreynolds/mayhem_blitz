class Hand:
    def __init__(self):
        self.size = 0
        self.all_cards = []
        
    def add_card(self, card):
        self.all_cards.append(card)
        self.size += 1
        
    def play_card(self, card):
        if card in self.all_cards:
            self.all_cards.remove(card)
            return card
        else:
            print(f"{card} isn't in hand...")
            
    def discard_hand(self):
        discarded_cards = self.all_cards
        self.all_cards = []
        self.size = 0
        return discarded_cards
    
    def remove_cards(self, cards):
        for card in cards:
            if card in self.all_cards:
                self.all_cards.remove(card)
            else:
                print(f"{card} isn't in hand...")        
    
    def is_empty(self):
        return self.all_cards == []
    
    def __str__(self):
        if len(self.all_cards) == 0:
            return "Hand is empty."        
        
        return ", ".join([f"{card}" for card in self.all_cards])