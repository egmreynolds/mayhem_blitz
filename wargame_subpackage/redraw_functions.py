import pygame
from display import UpdatedDisplayItem, ClickableDisplayItem, InputBox
from classes.Card import Card # Remove, for test only

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

additional_cards_width, additional_cards_height = (20, 30)

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

opponent_additional_cards_start_x, opponent_additional_cards_start_y = (battlezone_x - 10, opponent_battlezone_y)
player_additional_cards_start_x, player_additional_cards_start_y = (opponent_additional_cards_start_x, player_battlezone_y)

hand_x, hand_y = ((display_width - hand_width) / 2, battlezone_y + battlezone_height + sep)
hand_cards_x, hand_cards_y = (hand_x + sep, hand_y + sep)

log_x, log_y = (20, 20)
action_x, action_y = (battlezone_x, hand_y + hand_height + sep)
deck_x, deck_y = (action_x + action_width + sep/2, action_y)
discard_x, discard_y = (deck_x + card_width + sep/2, deck_y)

supply_x, supply_y = (log_x + log_width + sep, log_y)
supply_cards_x, supply_cards_y = (supply_x + sep, supply_y + sep)

def redrawWindow(win, game, player_idx, phase, reset = False, with_skip = False):
    if reset:
        win.fill((128, 128, 128))
        pygame.display.update()

    if phase == "11":
        redraw_hand(win, game, player_idx, with_skip = with_skip)
        redraw_decks(win, game, player_idx)
        redraw_textboxes(win, game, player_idx)

    elif phase == "12":
        redraw_battlefield(win, game, player_idx)
        redraw_hand(win, game, player_idx)
        redraw_textboxes(win, game, player_idx)

    elif phase == "13":
        redraw_battlefield(win, game, player_idx)
        redraw_textboxes(win, game, player_idx)

    elif phase in ["21", "22", "23", "24"]:
        redraw_battlefield(win, game, player_idx)
        redraw_stats(win, game, player_idx)
        redraw_hand(win, game, player_idx)
        redraw_textboxes(win, game, player_idx)        

    elif phase == "31":
        redraw_supply(win, game, player_idx)
        redraw_textboxes(win, game, player_idx)
    
    elif phase == "41": # reset to main game and ready for next round.
        redraw_battlefield(win, game, player_idx)
        redraw_hand(win, game, player_idx)
        redraw_decks(win, game, player_idx)
        redraw_stats(win, game, player_idx)
        redraw_textboxes(win, game, player_idx)
    
    elif phase == "51":
        redraw_battlefield(win, game, player_idx)
        redraw_gameover(win, game, player_idx)
        redraw_stats(win, game, player_idx)
        redraw_textboxes(win, game, player_idx)


def redraw_stats(win, game, player_idx):
    """
    Redraw HP and Money stats for both players.
    """
    opp_idx = (player_idx - 1) * -1
    player_hp_display = UpdatedDisplayItem(f"HP\n {game.players[player_idx].health}", player_hp_x, player_hp_y, stat_width, stat_height, (255, 0, 0))
    player_money_display = UpdatedDisplayItem(f"Money\n$ {game.players[player_idx].money}", player_money_x, player_money_y, stat_width, stat_height, (0, 128, 128))
    opp_hp_display = UpdatedDisplayItem(f"HP\n {game.players[opp_idx].health}", opponent_hp_x, opponent_hp_y, stat_width, stat_height, (255, 0, 0))
    opp_money_display = UpdatedDisplayItem(f"Money\n$ {game.players[opp_idx].money}", opponent_money_x, opponent_money_y, stat_width, stat_height, (0, 128, 128))
    items = [player_hp_display, player_money_display, opp_hp_display, opp_money_display]
    for item in items:
        item.draw(win)

    pygame.display.update()

def redraw_hand(win, game, player_idx, with_skip = False):
    """
    Redraw players hand. Optional = with SKIP
    """
    hand_background = UpdatedDisplayItem("", hand_x, hand_y, hand_width, hand_height, (100, 100, 100))
    hand_background.draw(win)
    hand = game.players[player_idx].hand.all_cards
    items = make_card_display(hand, "hand", "unclickable")
    if with_skip:
        n = len(items)
        items.append(UpdatedDisplayItem("SKIP", hand_cards_x + (card_width + sep) * n, hand_cards_y, card_width, card_height, (255, 255, 255)))

    for item in items:
        item.draw(win)

    pygame.display.update()
    
def redraw_gameover(win, game, player_idx):
    """
    Redraw 'RETURN TO MAIN MENU' box in Hand position
    """
    hand_background = UpdatedDisplayItem("", hand_x, hand_y, hand_width, hand_height, (100, 100, 100))
    item = UpdatedDisplayItem("RETURN TO MAIN MENU", hand_cards_x + (card_width + sep), hand_cards_y, card_width * 4, card_height, (255, 255, 255))
    item.draw(win)
    pygame.display.update()
    
def redraw_textboxes(win, game, player_idx):
    """
    Redraw log and action text boxes. # Add p1_log, p2_log, p1_prompt, p2_prompt to game.
    """
    log_display = UpdatedDisplayItem(game.players[player_idx].log_text, log_x, log_y, log_width, log_height, (200, 200, 200), pos = True)
    action_display = UpdatedDisplayItem(game.players[player_idx].prompt, action_x, action_y, action_width, action_height, (255, 255, 255))
    items = [log_display, action_display]
    for item in items:
        item.draw(win)

    pygame.display.update()

def redraw_battlefield(win, game, player_idx):
    """
    Redraw entire battlefield. # Use game.phase, game.part (if 11 just do player, 12 just do player, otherwise both AND if 21 red box battle 1, 22 for battle 2, 23 for battle 3)
    """
    battlezone_display = UpdatedDisplayItem("", battlezone_x, battlezone_y, battlezone_width, battlezone_height, (200, 200, 200))
    player_battlezone_display = UpdatedDisplayItem("", player_battlezone_x, player_battlezone_y, player_battlezone_width, player_battlezone_height, (220,220, 220))
    opp_battlezone_display = UpdatedDisplayItem("", opponent_battlezone_x, opponent_battlezone_y, player_battlezone_width, player_battlezone_height, (220, 220, 220))
    items = [battlezone_display, player_battlezone_display, opp_battlezone_display]
    if f"{game.phase}{game.part}" == "11":
        pass
    elif f"{game.phase}{game.part}" == "12":
        items.extend(make_card_display(game.players[player_idx].cards_played, "player battlezone", "unclicklable"))
    else:
        items.extend(make_card_display(game.players[player_idx].cards_played, "player battlezone", "unclicklable"))
        items.extend(make_card_display(game.players[(player_idx - 1) * -1].cards_played, "opponent battlezone", "unclicklable"))

    for item in items:
        item.draw(win)

    if f"{game.phase}{game.part}" == "21":
        pygame.draw.rect(win, (255, 0, 0), (opponent_battlecards_start_x - red_border_size, opponent_battlecards_start_y - red_border_size, card_width + red_border_size * 2, 2 * (card_height + sep + red_border_size) + sep), red_border_size)
    elif  f"{game.phase}{game.part}" == "22":
        pygame.draw.rect(win, (255, 0, 0), (opponent_battlecards_start_x - red_border_size + card_width + sep, opponent_battlecards_start_y - red_border_size, card_width + red_border_size * 2, 2 * (card_height + sep + red_border_size) + sep), red_border_size)
    elif  f"{game.phase}{game.part}" == "23":
        pygame.draw.rect(win, (255, 0, 0), (opponent_battlecards_start_x - red_border_size + (card_width + sep) * 2, opponent_battlecards_start_y - red_border_size, card_width + red_border_size * 2, 2 * (card_height + sep + red_border_size) + sep), red_border_size)

    # Draw additional cards if they exist
    additional_items = []
    if game.players[player_idx].additional_cards_in_play: # True if anything in additional_cards_in_play
        additional_items.extend(make_additional_cards_display(game.players[player_idx].additional_cards_in_play, "player"))
    if game.players[(player_idx - 1) * -1].additional_cards_in_play: # True if anything in additional_cards_in_play
        additional_items.extend(make_additional_cards_display(game.players[(player_idx - 1) * -1].additional_cards_in_play, "opponent"))

    for item in additional_items:
        item.draw(win)

    pygame.display.update()

def redraw_decks(win, game, player_idx):
    """
    Redraw deck and discard pile for player_idx
    """
    player_deck_display = UpdatedDisplayItem(f"Deck\n {game.players[player_idx].deck.get_deck_size()}", deck_x, deck_y, card_width, card_height, (0, 255, 0))
    player_discard_display = UpdatedDisplayItem(f"Discard\n {game.players[player_idx].discard.get_deck_size()}", discard_x, discard_y, card_width, card_height, (255, 0, 0))
    items = [player_deck_display, player_discard_display]
    for item in items:
        item.draw(win)

    pygame.display.update()

def redraw_supply(win, game, player_idx):
    """
    Draw supply -  6 items to a row. With log/action text boxes
    """
    win.fill((128, 128, 128))
    redraw_textboxes(win, game, player_idx)
    items = [UpdatedDisplayItem("", supply_x, supply_y, supply_width, supply_height, (240, 240, 240))]
    items.extend(make_supply_display(game, "unclickable"))
    for item in items:
        item.draw(win)

    pygame.display.update()
    #text_action_message = f"Select a card costing up to ${money}."
    #draw_main_text(text_action_message, (110, 110))

def make_additional_cards_display(cards, position):
    """
    Return a list of updated display items for additional cards in play.
    cards = list of cards
    position = {"player", "opponent"}    
    """
    if position == "player":
        x, y, width, height = (player_additional_cards_start_x, player_additional_cards_start_y, additional_cards_width, additional_cards_height)
    elif position == "opponent":
        x, y, width, height = (opponent_additional_cards_start_x, opponent_additional_cards_start_y, additional_cards_width, additional_cards_height)

    display_items = []
    for i in range(len(cards)):
        display_items.append(UpdatedDisplayItem(f"{cards[i].rank[0]} {cards[i].value}", x, y + (height + 10) * i, width, height, (0, 0, 255)))

    return display_items


def make_card_display(cards, position, type):
    """
    Return a list of Updated- or Clickable- DisplayItems based on a list of cards.
    cards = list of cards
    position = {"player battlezone", "hand", "opponent battlezone"}
    type = {"unclickable", "clickable"}
    """
    if position == "hand":
        x, y, width, height = (hand_cards_x, hand_cards_y, card_width, card_height)
    elif position == "player battlezone": # battle
        x, y, width, height = (player_battlecards_start_x, player_battlecards_start_y, card_width, card_height)
    elif position == "opponent battlezone": # opponents battle arena 
        x, y, width, height = (opponent_battlecards_start_x, opponent_battlecards_start_y, card_width, card_height)
    elif position == "add_cards_player": # needs work
        x, y, width, height = (550, 200, 80, 120, 10)
    else:
        x, y, width, height = (550, 20, 80, 120, 10)
    
    if len(cards) == 0:
        return []
    
    display_items = []
    for i in range(len(cards)):
        if type == "unclickable":
            display_items.append(UpdatedDisplayItem(f"{cards[i].rank} \n{cards[i].value} ", (x + (width+sep)*i), y, width, height, (0, 0, 255)))
        else:
            display_items.append(ClickableDisplayItem(f"{cards[i].rank} \n{cards[i].value} ", (x + (width+sep)*i), y, width, height, (0, 0, 255), cards[i]))
    
    return display_items
    

def make_supply_display(game, type):
    """
    Return either a clickable or unclickable (type) list of cards for the supply [ always include a SKIP card ]
    Up to 20 objects
    """
    cards = game.supply.all_cards
    unique_cards = list(set(cards))
    n_cards = len(unique_cards)
    display_items = []
    row = 0
    col = 0
    for i in range(n_cards):
        if type == "unclickable":
            display_items.append(UpdatedDisplayItem(f"{unique_cards[i].rank} \n{unique_cards[i].value} \nC:{unique_cards[i].cost}", (supply_cards_x + (card_width + sep)*col), (supply_cards_y + (card_height + sep)*row), card_width, card_height, (0, 0, 255)))
        else:
            display_items.append(ClickableDisplayItem(f"{unique_cards[i].rank} \n{unique_cards[i].value} \nC:{unique_cards[i].cost} ", (supply_cards_x + (card_width + sep)*col), (supply_cards_y + (card_height + sep)*row), card_width, card_height, (0, 0, 255), unique_cards[i]))
        
        col += 1
        if (i+1) % 6 == 0:
            row += 1
            col = 0

    display_items.append(ClickableDisplayItem("SKIP", (supply_cards_x + (card_width + sep)*col), (supply_cards_y + (card_height + sep)*row), card_width, card_height, (0, 0, 255), Card("SKIP")))

    return display_items

def redraw_mainmenu(win):
    """
    Draw main menu screen - First Window User sees in Client.
    Simply Game Title and Connect Button.
    """
    win.fill((21, 139, 154))
    font = pygame.font.SysFont("arial", 60)
    text_title = font.render("Mayhem Blitz", 1, (154, 36, 21))    
    win.blit(text_title, (250, 100))
    item = UpdatedDisplayItem("", 250, 250, 300, 200, (154, 69, 21))
    item.draw(win)
    text_connect = font.render("Connect!", 1, (154, 36, 21)) 
    win.blit(text_connect, (300, 300))
    pygame.display.update()
    
def redraw_loginscreen(win):
    """
    Draw Username and Password boxes, display them and request input.
    """      
    username, password = ["", ""]
    win.fill((21, 139, 154))
    font = pygame.font.SysFont("arial", 60)
    font_subtext = pygame.font.SysFont("arial", 30)
    text_title = font.render("Mayhem Blitz", 1, (154, 36, 21))    
    win.blit(text_title, (250, 100))
    text_username = font_subtext.render("Username", 1, (255, 255, 255))
    text_password = font_subtext.render("Password", 1, (255, 255, 255))
    username_item = InputBox(250, 250, 300, 50, username)
    password_item = InputBox(250, 350, 300, 50, password)
    input_boxes = [username_item, password_item]
    win.blit(text_username, (250,220))
    #username_item.draw(win)
    win.blit(text_password, (250,320))
    enter_item = UpdatedDisplayItem("Enter", 350, 450, 100, 60, (154, 69, 21))
    enter_item.draw(win)
    # Create ENTER ClickableItem: display.
    #password_item.draw(win)
    pygame.display.update()
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                pygame.quit()
            for box in input_boxes:
                box.handle_event(event)
                
            # if event hits ENTER: return username, password
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()        
                if 350 <= pos[0] <= 350 + 100 and 450 <= pos[1] <= 450 + 60:
                    done = True
                    username = input_boxes[0].text
                    password = input_boxes[1].text
                    break

        for box in input_boxes:
            box.draw(win)
                                    
        pygame.display.update()    
         
    return (username, password)   

def redraw_lobbyscreen(win, wait = False):
    """
    Draw Lobby - includes title, games played, players online
    Include a button 'Start Game' which will add player to 'looking for game' or 'start game'
    If wait == True: Add waiting for opponent... text, remove clickable button.
    """     
    win.fill((21, 139, 154))
    font = pygame.font.SysFont("arial", 60)
    text_title = font.render("Mayhem Blitz", 1, (154, 36, 21))    
    win.blit(text_title, (250, 100))
    if wait:
        item = UpdatedDisplayItem("Waiting for opponent...", 250, 250, 300, 200, (154, 69, 21))
        item.draw(win)
    else:
        item = UpdatedDisplayItem("Start Game", 250, 250, 300, 200, (154, 69, 21))
        item.draw(win)

    pygame.display.update()