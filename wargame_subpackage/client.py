#from network import Network
import pygame
import pickle
from display import UpdatedDisplayItem, ClickableDisplayItem
from game import Game
from classes.Card import Card # Remove, for test only
from redraw_functions import redrawWindow, make_card_display, make_supply_display, redraw_supply
from network import Network
import time

pygame.font.init()
## LOTS OF STATS, there might be a better place.
display_width, display_height = (800, 800)


card_width, card_height = (80, 120)
sep = 20

battlezone_width, battlezone_height = (360, 380)
player_battlezone_width, player_battlezone_height = (320, 160)
stat_width, stat_height = (50, 50)
hand_width, hand_height = (520, 160)
log_width, log_height = (150, 380)
log_font_size = 20
action_width, action_height = (360, 120)
action_font_size = 30
red_border_size = 5

supply_width, supply_height = (620, 380 + hand_height + sep)

battlezone_x, battlezone_y = ((display_width - battlezone_width) / 2, 20)
opponent_battlezone_x, opponent_battlezone_y = (battlezone_x + sep, battlezone_y + sep)
player_battlezone_x, player_battlezone_y = (opponent_battlezone_x, opponent_battlezone_y + player_battlezone_height + sep)
opponent_hp_x, opponent_hp_y = (battlezone_x + battlezone_width + sep, opponent_battlezone_y)
opponent_money_x, opponent_money_y = (opponent_hp_x + stat_width + sep, opponent_hp_y)
player_hp_x, player_hp_y = (opponent_hp_x, player_battlezone_y + player_battlezone_height - stat_height)
player_money_x, player_money_y = (player_hp_x + stat_width + sep, player_hp_y)

opponent_battlecards_start_x, opponent_battlecards_start_y = (opponent_battlezone_x + sep, opponent_battlezone_y + sep)
player_battlecards_start_x, player_battlecards_start_y = (player_battlezone_x + sep, player_battlezone_y + sep)

hand_x, hand_y = ((display_width - hand_width) / 2, battlezone_y + battlezone_height + sep)
hand_cards_x, hand_cards_y = (hand_x + sep, hand_y + sep)

log_x, log_y = (20, 20)
action_x, action_y = (battlezone_x, hand_y + hand_height + sep)
deck_x, deck_y = (action_x + action_width + sep/2, action_y)
discard_x, discard_y = (deck_x + card_width + sep/2, deck_y)

supply_x, supply_y = (log_x + log_width + sep, log_y)
supply_cards_x, supply_cards_y = (supply_x + sep, supply_y + sep)


win = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Client")


def request_reaction_response(win, game, player_idx, reaction):
    response = ""
    if reaction == "guard":
        redraw_guard_reaction(win, game, player_idx)
        response = request_guard_reaction(game, player_idx)

    elif reaction == "lich":
        redraw_lich_reaction(win, game, player_idx)
        response = request_lich_reaction(game, player_idx)

    else:
        pass

    return response


def redraw_guard_reaction(win, game, player_idx):
    redrawWindow(win, game, player_idx, "11", with_skip = True)

def request_guard_reaction(game, player_idx):
    clickables = make_card_display(game.players[player_idx].hand.all_cards, "hand", "clickable")
    clickables.append(ClickableDisplayItem("SKIP", hand_cards_x + (card_width + sep) * len(clickables), hand_cards_y, card_width, card_height, (255, 255, 255), Card("SKIP")))
    selected_card = ""
    break_loop = False
    while not(break_loop):
        for event in pygame.event.get():
            if break_loop: break
            if event.type == pygame.QUIT:
                break_loop = True
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for obj in clickables:  # Cycle through cards, if it's clicked and hasn't been added yet, add to cards_played
                    if obj.click(pos):
                        print(obj.card)
                        selected_card = obj.card.rank
                        break_loop = True
                        break

    return selected_card

def redraw_lich_reaction(win, game, player_idx):
    redrawWindow(win, game, player_idx, "31")

def request_lich_reaction(game, player_idx):
    return select_from_supply(game, player_idx, 5)

def select_from_supply(game, player_idx, max_money):
    """
    Take input from user when selecting from supply.
    """
    clickable_items = make_supply_display(game, "clickable")
    selected_card = ""
    break_loop = False
    while True:
        if break_loop:
            break
        for event in pygame.event.get():
            if break_loop:
                break

            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for obj in clickable_items:
                    if obj.click(pos):
                        if obj.card.value <= max_money:
                            selected_card = obj.card.rank
                            break_loop = True
                            break
                        else:
                            pass

    return selected_card

def select_cards_to_play(game, player_idx, clickable_objects):
    selected_cards = []
    break_loop = False
    while not(break_loop):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break_loop = True
                pygame.quit()
            if break_loop: break

            if event.type == pygame.MOUSEBUTTONDOWN:
                for obj in clickable_objects:  # Cycle through cards, if it's clicked and hasn't been added yet, add to cards_played
                    if obj.click(pygame.mouse.get_pos()) and not(obj.clicked):
                        print(obj.card)
                        selected_cards.append(obj.card.rank)
                        obj.was_clicked()
                        if len(selected_cards) == 3: # Don't accept any more, remove cards_played from hand, progress to next part
                            break_loop = True # break outer loop as a new phase is occuring
                            break # break this inner loop

    return selected_cards


def main():
    print("Starting main")
    run = True
    clock = pygame.time.Clock()
    n = Network()

    print(n.getP())
    player_idx = int(n.getP())
    print("You are player: ", player_idx)

    waiting_for_game = True
    while waiting_for_game:
        try:
            game = n.receive()
            if game.ready:
                waiting_for_game = False
                print("We are ready to go!")
        except:
            print("Not ready yet...")


    redrawWindow(win, game, player_idx, "41", reset = True)
    #n.send_to_server([player_idx, "ready"])
    msg = [player_idx, "ready"]
    current_phase = "blank"
    while run:
        clock.tick(60)
        time.sleep(1)
        try:
            print(f"sending message: {msg}")
            #msg = [player_idx, "get"]
            n.send_to_server(msg)
            game = n.receive()
            print(f"receiving message: {game}") # it receives the game, but then never sends another message... so it's getting stuck somewhere
            msg = [player_idx, "get"]
        except:
            run = False
            print("Couldn't get game, sorry.")
            break

        game_phase = f"{game.phase}{game.part}{game.subpart}"
        if current_phase != game_phase:
            current_phase = game_phase
            new_phase = True

        if new_phase:
            new_phase = False
            if game.phase == 1 and game.part == 1:
                clickable_objects = make_card_display(game.get_player(player_idx).hand.all_cards, "hand", "clickable")
                redrawWindow(win, game, player_idx, "11")   ### draw deck, discard, action, hand, log
                cards_selected = select_cards_to_play(game, player_idx, clickable_objects)
                pygame.time.delay(1000)
                print(f"Cards selected: {cards_selected}")
                msg = [player_idx, "ready"]
                msg.extend(cards_selected)
                print(f"New message is: {msg}")

            elif game.phase == 1 and game.part == 2:
                print("Phase 12")
                redrawWindow(win, game, player_idx, "12") ## draw hand, action, log, player_battlezone.
                pygame.time.delay(1000)
                msg = [player_idx, "ready"]

            elif game.phase == 1 and game.part == 3:
                print("Phase 13")
                redrawWindow(win, game, player_idx, "13")
                pygame.time.delay(1000) # wait two seconds
                msg = [player_idx, "ready"]## action, log, opponent_battlezone

            elif game.phase == 2 and game.part < 4:
                print(f"Phase {game.phase}{game.part}{game.subpart}")
                # if you win or draw change players_ready to True.
                # else resolve action then be ready
                redrawWindow(win, game, player_idx, f"2{game.part}") # battlezone (opponent, player and whole)
                msg = [player_idx, "ready"]
                #redrawWindow(win, game, player_idx, f"2{game.part}") # action/log, stats
                pygame.time.delay(1000)
                if game.reaction_activated[player_idx]:
                    #redrawWindow(win, game, player_idx, f"2{game.part}")
                    card_rank = request_reaction_response(win, game, player_idx, game.reaction_str[player_idx])
                    msg = [player_idx, "ready", card_rank]
                else:
                    pass


            elif game.phase == 2 and game.part == 4:
                print("Phase 24")
                redrawWindow(win, game, player_idx, "24")
                pygame.time.delay(1000)
                msg = [player_idx, "ready"]

            elif game.phase == 3 and game.part == 1: ## Big screen update
                print("Phase 31")
                redrawWindow(win, game, player_idx, "31")
                selected_card = select_from_supply(game, player_idx, game.players[player_idx].money)
                msg = [player_idx, "ready", selected_card]

            elif game.phase == 3 and game.part == 2:
                print("Phase 32")
                redrawWindow(win, game, player_idx, "31")
                pygame.time.delay(1000)
                #selected_card = select_from_supply(game, player_idx, game.players[player_idx].money)
                msg = [player_idx, "ready"]#, selected_card]
                redrawWindow(win, game, player_idx, "41", reset = True)
                pygame.time.delay(1000)

            elif game.phase == 4 and game.part == 1:
                print("Phase 41")
                redrawWindow(win, game, player_idx, "41") ## Whole window
                pygame.time.delay(1000)
                msg = [player_idx, "ready"]

            # Listen for any events (card clicks)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()


def menu_screen():
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        win.fill((128, 128, 128))

        font = pygame.font.SysFont("arial", 60)
        text = font.render("Click to Play!", 1, (255, 0, 0))
        win.blit(text, (200, 200))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False

    main()



menu_screen()
