from classes.Player import Player
from classes.Deck import Deck
from classes.Card import Card
from functions.supply_functions import reset_supply
from functions.abilities_functions import activate_ability_v2


# Should Game just inherit all the 'battle_functions' methods and 'play_functions' methods that don't belong elsewhere?

class Game:

    def __init__(self, id):
        self.id = id
        self.players = [Player("Player 1"), Player("Player 2")]
        self.supply = Deck()
        self.round = 0
        self.reset_game()
        self.ready = False
        self.phase = 0 # Game has 4 phases: 1 - Strategy, 2 - Battle, 3 - Buy, 4 - Wrap-up [5 - game over]
        self.part = 1 # strategy has 2 parts: 1 - Show hand, 2 - Show cards played before battle.
        # Battle has 4 parts: 1 - battle 1, 2 - battle 2, 3 - battle 3, 4 - overall resolution
        self.subpart = 1 # Just for battle phase (1 - run battle, 2 - reaction activated)
        self.reaction_activated = [False, False]
        self.reaction_str = ["", ""]
        self.players_ready = [False, False] # p1 [0] and p2 [1] : False - not ready for next round. True = Ready for next round.
        self.game_text = ""
        self.action = ""
        self.player_action_idx = 0 # Which player needs to take the action.
        self.log_text = ["", ""]
        self.prompt = ["", ""]
        self.game_state = "in_play" #Game states: in_play, game_over; add more as is necessary
        self.game_reset = [False, False]
        self.supply_coin = 0
        #self.current_phase = "blank"
                
    def set_player_names(self, player1, player2):
        self.players[0].name = player1
        self.players[1].name = player2

    def set_reset(self, p):
        """
        Assign game_reset[player] = True - Indicating This player is ready to 'return to main menu' or 'reset' the game
        """
        self.game_reset[p] = True
        
    def check_reset_state(self):
        """Returns True if both players have requested a reset
        """
        return self.game_reset[0] and self.game_reset[1]

    def reset_game(self):
        reset_supply(self.supply)
        self.players[0].setup_deck()
        self.players[1].setup_deck()

    def update_game(self, p, data):
        print(f"Game updating for {p} at {self.phase} {self.part}")
        print(f"Game data: {data}")
        if self.phase == 1 and self.part == 1:
            [self.players[p].cards_played.append(Card(x)) for x in data[2:]]
            self.players[p].hand.remove_cards(self.players[p].cards_played)
            self.players[p].set_log_text("\n".join([f"{card.rank}_{card.value}" for card in self.players[p].cards_played]))
            self.players[p].set_prompt("")

        elif self.phase == 2 and self.reaction_activated[p]: # If the player is the one who had a reaction activated, process it.
            self.process_reaction(p, data)
            self.players[0].set_prompt("")
            self.players[1].set_prompt("")
            # process reaction...

        elif self.phase == 3 and self.part == 1:
            if p == self.supply_coin:
                if data[2] == "SKIP":
                    self.players[p].set_log_text("No card was chosen\n from supply\n")
                    self.players[p].set_prompt("")
                else:
                    bought_card = Card(data[2])
                    self.players[p].change_money(-1 * bought_card.cost)
                    self.players[p].discard.add_cards(bought_card)
                    self.supply.remove_card(bought_card)
                    self.players[p].set_log_text(f"{self.players[p].name} gained\n  a {bought_card.rank}\n from the supply.\n")
                    self.players[p].set_prompt("")                
                
        elif self.phase == 3 and self.part == 2:
            if p != self.supply_coin:
                if data[2] == "SKIP":
                    self.players[p].set_log_text("No card was chosen\n from supply\n")
                    self.players[p].set_prompt("")
                else:
                    bought_card = Card(data[2])
                    self.players[p].change_money(-1 * bought_card.cost)
                    self.players[p].discard.add_cards(bought_card)
                    self.supply.remove_card(bought_card)
                    self.players[p].set_log_text(f"{self.players[p].name} gained\n  a {bought_card.rank}\n from the supply.\n")
                    self.players[p].set_prompt("")                          
            
        print(f"Game updated for player: {p}")



    def play(self, p, data):
        print("Game is being played")
        print(f"{self.players_ready[0]} and {self.players_ready[1]}")
        try:
            if self.players_ready[0] and self.players_ready[1]:
                # For whatever phase it is, complete steps and move on to the next one.
                if self.phase == 1:
                    if self.part == 1:
                        self.players[0].draw_hand()
                        self.players[1].draw_hand()
                    elif self.part == 2:
                        pass
                        #[self.players[p].cards_played.append(Card(x)) for x in data[1:3]]
                        #self.players[p].hand.remove_cards(self.players[p].cards_played)
                        #self.players[p].set_log_text("\n".join([f"{card.rank}_{card.value}" for card in self.players[p].cards_played]))
                        #self.players[p].set_prompt("")
                                    
                elif self.phase == 2:
                    if self.part <= 3:
                        if self.subpart == 1:
                            self.run_battle(self.part - 1)
                            if self.reaction_activated[0] or self.reaction_activated[1]:
                                self.activate_reaction(p) # If either activate a reaction
                            else:
                                self.next_part_or_phase() # Skip subpart 2 - When neither are True.

                        if self.subpart == 2:
                            # data[1] = card choice, "reaction_str" - indicated reaction type
                            # Reset reaction details
                            self.reaction_str = ["", ""]
                            self.reaction_activated = [False, False]
                            #self.process_reaction(p, data) # needs something
                            # ask client to for response (which then asks user for response) [additional phase/part/subpart]
                            # add_action_details(win, game, player_idx)
                            # Use data to do something based on reaction
                    if self.part == 4:
                        self.resolve_battle()

                elif self.phase == 3:
                    
                    if self.part == 1:
                        self.players[self.supply_coin].set_prompt(f"You have {self.players[self.supply_coin].money} coins.\n Select a card to Buy up to that value.\n")
                        self.players[(self.supply_coin - 1)*-1].set_prompt(f"You have {self.players[(self.supply_coin - 1)*-1].money} coins.\n Please wait for your opponent to make their selection.\n")
                        
                    elif self.part == 2:
                        self.players[(self.supply_coin - 1) *-1].set_prompt(f"You have {self.players[(self.supply_coin - 1)*-1].money} coins.\n Select a card to Buy up to that value.\n")
                        self.players[self.supply_coin].set_prompt(f"You have selected your Buy.\nPlease wait for your opponent to make their selection.\n")

                elif self.phase == 4:
                    self.end_round()
                    self.players[0].set_log_text("New Round")
                    self.players[1].set_log_text("New Round")

        except Exception as e:
            print("We've caught a gameplay exception.")
            print(e)

            # Next round, require new 'ready' returns
            

    def activate_reaction(self, p):
        if self.reaction_str[p] == "guard":
            self.activate_guard(p)
        elif self.reaction_str[p] == "lich":
            pass
        else:
            pass

    def process_reaction(self, p, data):
        if self.reaction_str[p] == "guard":
            self.process_guard(p, data)
        elif self.reaction_str[p] == "lich":
            pass
        else:
            pass

    def activate_guard(self, p):
        self.players[p].set_prompt("Select a card in hand to trash.\n")
        self.players[(p-1) * -1].set_prompt("Waiting for other player to react...")

    def process_guard(self, p, data):
        try:
            selected_card = Card(data[2])

            if selected_card.rank == "SKIP":
                self.players[p].set_log_text("No card was trashed\n")
                self.players[(p-1) * -1].set_log_text("Other player did\n not trash a card\n")
            else:
                self.players[p].hand.remove_cards([selected_card])
                self.players[p].set_log_text(f"{self.players[p].name} trashed \na {selected_card.rank}\n from their hand.\n")
                self.players[(p-1) * -1].set_log_text(f"{self.players[p].name} \ntrashed a {selected_card.rank}\n from their hand.\n")

        except:
            print("process_guard problem occured", data)

    def activate_lich(self, p):
        self.players[p].set_prompt("Select a card from supply up to value 5.\n")
        self.players[(p-1) * -1].set_prompt("Waiting for other player to react...")

    def process_lich(self, p, data):
        try:
            selected_card = Card(data[2])

            if selected_card.rank == "SKIP":
                self.players[p].set_log_text("No card was trashed\nYou kept the Lich.")
                self.players[(p-1) * -1].set_log_text("Other player did\n not trash a card\n")
                self.player[p].discard.add_cards(Card("Lich")) # Re-add Lich to discard pile. If there become a trash search - this will cause problems
            else:
                self.players[p].discard.add_cards(selected_card)
                self.supply.remove_card(selected_card)
                self.players[p].set_log_text(f"{self.players[p].name} gained \na {selected_card.rank}\n from the supply.\n")
                self.players[(p-1) * -1].set_log_text(f"{self.players[p].name} \n gained a {selected_card.rank}\n from the supply.\n")

        except:
            print("process_guard problem occured", data)


    def set_ready(self, p):
        self.players_ready[p] = True
        
    def set_game_state(self, game_state):
        self.game_state = game_state

    def set_game_over(self):
        """
        Change Log to 'GAME OVER'.     
        """
        self.players[0].set_log_text("GAME OVER")
        self.players[1].set_log_text("GAME OVER")
        self.phase = 5
        self.part = 1
        
    def announce_winner(self):
        """
        Change Prompt to indicate whether player has won or lost.   
        """
        winner = self.get_winner()
        if winner == 0:
            self.players[0].set_prompt("Winner! You have won!")
            self.players[1].set_prompt("Defeat! You have lost!")
        elif winner == 1:
            self.players[1].set_prompt("Winner! You have won!")
            self.players[0].set_prompt("Defeat! You have lost!")
        else:
            self.players[0].set_prompt("Draw! Game has ended in a tie...")
            self.players[1].set_prompt("Draw! Game has ended in a tie...")
            
        
    def get_winner(self):
        """
        Return 0 or 1 or 9 as to which player has dealt the final blow. If 9 - it's a draw, both players are dead.
        """
        winner = -1
        if self.players[0].check_health() == "game_over" and self.players[1].check_health() == "game_over":
            winner = 9
        elif self.players[0].check_health() == "game_over":
            winner = 1
        elif self.players[1].check_health() == "game_over":
            winner = 0
        else:
            print("************** Game Over without Winner *************")
        return winner

    def end_round(self):
        """
        This occurs before wrap-up phase.
        """
        self.players[0].discard_hand()
        self.players[1].discard_hand()
        self.players[0].discard_cards_played()
        self.players[1].discard_cards_played()
        self.players[0].end_round_reset()
        self.players[1].end_round_reset()

    def setup_new_round(self):
        """
        This occurs once wrap up phase of previous round is complete, settting up the next round.
        """
        self.round += 1
        print(f"ROUND {self.round} BEGINS")
        self.phase = 1
        self.part = 1
    # also draw new hand

    def set_log_text(self, player_idx, text):
        self.players[player_idx].set_log_text(text)

    def set_prompt(self, player_idx, text):
        self.players[player_idx].set_prompt(text)

    def run_battle(self, battle_number):
        """
        Resolve the outcome of an individual battle in battle arena.
        battle_number = 0 1 or 2
        Returns nothing, but changes action, game_text, player_action_idx sometimes
        """
        p1card = self.players[0].cards_played[battle_number]
        p2card = self.players[1].cards_played[battle_number]
        print(f"{self.players[0].name} plays a {p1card}")
        print(f"{self.players[1].name} plays a {p2card}")
        log_text = ""
        log_text += f"{self.players[0].name} plays\n a {p1card}\n\n"
        log_text += f"{self.players[1].name} plays\n a {p2card}\n\n"
        
        if p1card > p2card:
            # p1 is winner
            self.player_action_idx = 1
            self.players[0].change_money(1)
            log_text += f"{self.players[0].name} gains\n 1 coin\n\n"
            text_output, action = activate_ability_v2(p2card, self.players[1], self.players[0], self.supply)
        elif p1card < p2card:
            # p2 is winner
            self.player_action_idx = 0
            self.players[1].change_money(1)
            log_text += f"{self.players[1].name} gains\n 1 coin\n\n"
            text_output, action = activate_ability_v2(p1card, self.players[0], self.players[1], self.supply)
        else:
            # draw
            text_output, action = ("A draw\n no ability\n was activated.\n", "")
        
        # print text_output to display
        log_text += text_output
        self.players[0].set_log_text(log_text)
        self.players[1].set_log_text(log_text)
        self.game_text = text_output
        self.action = action
        if action == "":
            self.reaction_activated = [False, False]
            self.reaction_str = ["", ""]
        else:
            if p1card > p2card:
                self.reaction_activated[1] = True
                self.reaction_str[1] = action
            else:
                self.reaction_activated[0] = True
                self.reaction_str[0] = action

    def resolve_battle(self):
        self.players[0].get_damage()
        self.players[1].get_damage()
        p1damage = self.players[0].damage
        p2damage = self.players[1].damage

        text = f"{self.players[0].name} has\n {p1damage} attack power.\n {self.players[1].name} has\n {p2damage} attack power.\n\n"
        if p1damage > p2damage:
            self.players[1].change_health(p2damage - p1damage)# makes it negative
            text += f"{self.players[1].name} takes \n{p1damage - p2damage} damage.\n\n"
            text += f"{self.players[1].name} has \n{self.players[1].health} HP remaining.\n"
            self.supply_coin = 0
        elif p1damage < p2damage:
            self.players[0].change_health(p1damage - p2damage) # makes it negative
            text += f"{self.players[0].name} takes \n{p2damage - p1damage} damage.\n\n"
            text += f"{self.players[0].name} has \n{self.players[0].health} HP remaining.\n"
            self.supply_coin = 1
        else:
            text += f"A draw\n no damage is done.\n"

        self.players[0].damage = 0
        self.players[1].damage = 0
        
        self.players[0].set_log_text(text)
        self.players[1].set_log_text(text)

        self.players[0].add_new_additional_cards()
        self.players[1].add_new_additional_cards()
        
        self.players[0].trash_cards_to_trash()
        self.players[1].trash_cards_to_trash()


    def check_players_health(self):
        if self.players[0].check_health() == "game_over" or self.players[1].check_health() == "game_over":
            return "game_over"

    def both_players_ready(self):
        return self.players_ready[0] and self.players_ready[1]

    def next_part_or_phase(self):
        if self.phase == 0:
            self.phase = 1

        elif self.phase == 1:
            if self.part == 1:
                self.part = 2
            elif self.part == 2:
                self.part = 3
            elif self.part == 3:
                self.part = 1
                self.phase = 2

        elif self.phase == 2:
            if self.part <= 3:
                if self.subpart == 1:
                    self.subpart = 2
                elif self.subpart == 2:
                    self.part += 1
                    self.subpart = 1
            else:
                self.part = 1
                self.phase = 3

        elif self.phase == 3:
            if self.part == 1:
                self.part = 2
            elif self.part == 2:
                self.part = 3
            elif self.part == 3:
                self.part = 1
                self.phase = 4

        elif self.phase == 4:
            self.part = 1
            self.phase = 1

    def get_player(self, player_index):
        """
        :param p: [0, 1]
        :return: Move - could be a selection      
        """
        return self.players[player_index]
# Need to define get_choice method in player object - Or perhaps this can be split into 3 different 'choices' methods for points throughout the game.
# Need to define 'made choice' in player object
    def connected(self):
        return self.ready

 
