from .Card import Card
from .Hand import Hand
from .Deck import Deck
from ..functions.response_functions import request_response
from ..functions.supply_functions import create_supply_hand

class Player():
    max_health = 15

    def __init__(self, name):
        self.hand = Hand()
        self.handsize = 0
        self.deck = Deck()
        self.discard = Deck()
        self.playorder = []
        self.cards_played = []
        self.health = 15
        self.name = name
        self.money = 0
        self.number_of_cards_to_draw = 5
        self.additional_cards_in_play = []
        self.damage = 0
        
    def discard_hand(self):
        # Move hand to discard pile, reset cards played etc.
        self.discard.add_cards(self.hand.discard_hand())
        
    def discard_cards_played(self):
        self.discard.add_cards(self.cards_played)
        self.cards_played = []
    
    def end_round_reset(self):
        self.handsize = 0
        self.playorder = []       
        
    def get_play_order(self):
        print(f"{self.name}, this is your hand.")
        print(self.hand)
        question = "Which cards would you like to play? "
        self.playorder = request_response(question, num = 3, upper_bound = len(self.hand.all_cards) - 1, blank_ok = False)
        self.cards_played = [self.hand.all_cards[i] for i in self.playorder]
        self.hand.remove_cards(self.cards_played)
        self.add_extras()
   
    def get_cards_to_trash(self, num = 1):
        self.trash_card()
        
    def print_cards_played(self):
        print(", ".join([f"{card}" for card in self.cards_played]))

    def add_to_additional_cards_in_play(self, card):
        self.additional_cards_in_play.append(card)

    def add_extras(self):
        self.cards_played.extend(self.additional_cards_in_play)
        self.additional_cards_in_play = []

    def get_damage(self):
        for card in self.cards_played:
            self.damage += card.value
        
    def change_money(self, amount):
        self.money += amount

    def change_number_of_cards_to_draw(self, amount):
        self.number_of_cards_to_draw += amount
        
    def change_health(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
        if self.health <= 0:
            self.health = 0
            
    def check_health(self):
        if self.health <= 0:
            print(f"Game over! {self.name} loses.")
            return "game_over"
            
    def print_health_status(self):
        print(f"{self.name} has {self.health} hp remaining.")
        
    def print_money_status(self):
        print(f"{self.name} has {self.money} gold remaining")
        
    def setup_deck(self):
        """
        Setup a deck with six 1's and three 2's and one 3. [Goblin, Soldier, Captain = generic]
        """
        cards = [Card("Guard"), Card("Goblin"), Card("Goblin"), Card("Goblin"), Card("Goblin"), Card("Goblin"), Card("Soldier"), Card("Soldier"), Card("Captain"), Card("Priest")]
        self.deck.add_cards(cards)
        self.deck.shuffle()
        
    def draw_hand(self):
        """
        Draw a hand of x(number_of_cards_to_draw) cards from deck
        """
        cards_drawn = 0
        for i in range(self.number_of_cards_to_draw):
            if self.deck.is_empty():
                # shuffle discard pile into deck
                self.deck.add_cards(self.discard.all_cards)
                self.discard = Deck()
                self.deck.shuffle()

            try:
                self.hand.add_card(self.deck.draw_card())
                self.handsize += 1
                cards_drawn += 1
            except IndexError:
                print("Deck and Discard piles are empty!")
                break
            except:
                print("Unknown error when drawing cards into hand")
                break

        print(f"{self.name} drew {cards_drawn} cards.")  
        self.number_of_cards_to_draw = 5  
        
    def trash_card(self):
        # if hand is empty : nothing to trash
        # else: question = "Which card would you like to trash? " Upper - handsize, num = 1, blankok = true.
        if self.hand.is_empty():
            print("Empty hand. Nothing to trash.")
            return        
        
        print(f"{self.name}, this is your hand.")
        print(self.hand)
        question = "Which card would you like to trash? "
        choice = request_response(question, num = 1, upper_bound = len(self.hand.all_cards) - 1, blank_ok = True)
        if choice == []:
            print(f"{self.name} chose not to trash a card.")
        else:
            trash_card = self.hand.all_cards[choice[0]]
            print(f"{self.name} chose to trash a {trash_card}")
            self.hand.remove_cards([trash_card])           

        
    def purchase_phase(self, supply):
        self.print_money_status()
        supply.display_supply()
        supply_hand = create_supply_hand(supply)
        while True:
            question = "What card(s) would you like to purchase? "
            choice = request_response(question, num = 1, upper_bound = len(supply_hand.all_cards) - 1, blank_ok = True)
            # If a card is not chosen
            if choice == []:
                print(f"{self.name} chose not to buy a card.")
                break
            # If card is affordable
            chosen_card = supply_hand.all_cards[choice[0]]
            if chosen_card.value <= self.money:
                self.discard.add_cards(chosen_card)  
                supply.remove_card(chosen_card)
                print(f"{self.name} purchased a {chosen_card} for {chosen_card.value}")
                self.change_money(-1 * chosen_card.value)
                self.print_money_status()
                break
            else:
                print("You cannot afford this card, please choose another.")
                self.print_money_status()

        print()
        # add card, remove from supply
        # What if money didn't reset
        #self.money = 0
    def select_from_supply(self, supply, value):
        print(f"Select a card up to value: {value}")
        supply.display_supply()
        supply_hand = create_supply_hand(supply)
        while True:
            question = "What card would you like to take? "
            choice = request_response(question, num = 1, upper_bound = len(supply_hand.all_cards) - 1, blank_ok = False)
            # If card is affordable
            chosen_card = supply_hand.all_cards[choice[0]]
            if chosen_card.value <= value:
                self.discard.add_cards(chosen_card)  
                supply.remove_card(chosen_card)
                print(f"{self.name} selected a {chosen_card} for {chosen_card.value}")
                break
            else:
                print("You cannot afford this card, please choose another.")
                print(f"You have ${value}.")