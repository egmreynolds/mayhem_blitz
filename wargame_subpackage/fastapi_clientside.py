# Client functions interacting with FastAPI
#
import time
import pygame
import requests
from pydantic import BaseModel
from client import select_cards_to_play
from redraw_functions_fastapi_refactored import redrawWindow, make_card_display, redraw_mainmenu, redraw_loginscreen, redraw_lobbyscreen, redraw_mainmenu_fastapi, select_from_supply,  request_reaction_response, request_gameover_response
from classes.Card import Card # Remove, for test only
 
#
# Login
# new_client - menu_screen()
# When 'connect' clicked -> send connect_to_lobby request
api_url = 'http://127.0.0.1:8000/'

display_width, display_height = (800, 800)
win = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Client")

class GameOut(BaseModel):
    """
    This Model represents the Game Object with all information that can be sent to the client.
    """
    # Game stuff:
    game_id: int
    game_state: list[int] #phase, part, subpart
    supply: list[str] # Distinct cards in supply
    supply_coin: int #0 or 1 depending on whose first up/could be bit
    
    # Both players:
    health: list[int] #player0, player1
    money: list[int] #player0, player1
    reaction_activated: list[bool]
    reaction_str: list[str]
    cards_played: list[list[str]] # player0 cards, player1 cards (2 x 3)
    additional_cards_in_play: list[list[str]] # similar to cards_played, but 2 x ??? (normally 0)
    
    # Just this player:
    player_idx: int
    hand: list[str]
    log_text: str
    prompt: str
    deck_size: int
    discard_size: int    
    
def initial_connection():
    """
    Called at Client Start Up - Confirms if a connection can be made to the API
    """
    try:
        response = requests.get(f"{api_url}login/test")
        if response.json()["connect_status"]:
            print("Connected!")
            return True
        else:
            return False
    except Exception as e:
        print("Failed to Connect to Server")
        print(e)
        # ADD DISPLAY FEATURE TO INFORM USER 'Connection failed, try restarting the client or check the server status at www.status.com'
        return False

def login_to_server():
    """
    Called when user clicks 'login' in menu_screen
    Sends login request to API
    """
    # Display Login Screen - username - textbox, password - textbox, 'login' button
    # While loop waiting for login to be clicked and updating text-boxes as buttons or keys are pressed or QUIT
    # If 'login' button pressed -> do this:
    not_logged_in = True
    while not_logged_in:
        username, password = redraw_loginscreen(win) # function from redraw_functions
        password = hash(password)
        response = requests.post(f"{api_url}login/connect", json={"user_id": username, "user_pwrd": password})
        response = response.json()
        if response['login_status'] == "success":
            print(response['message'])
            not_logged_in = False
        # Go to Lobby
            return (True, username)
        else:
            print("Didn't log in...")
            print(response['message'])
            
            # Should be a function 'add login failed to win'
            font = pygame.font.SysFont("arial", 30)
            text_title = font.render(response['message'], 1, (154, 36, 21))    
            win.blit(text_title, (250, 400))
            pygame.display.update()  
            time.sleep(5)   
      
def register_to_server():
    """
    Called when user clicks 'register' in menu_screen
    Sends register request to API
    """
    not_registered = True
    while not_registered:
        username, password, user_email = redraw_loginscreen(win, register = True) # function from redraw_functions
        password = hash(password)
        response = requests.post(f"{api_url}login/register", json={"user_id": username, "user_pwrd": password, "user_email" : user_email})
        response = response.json()
        print(f"Register response: {response}")
        if response['register_status'] == "success":
            print(response['message'])
            not_registered = False
        # Go back to main screen:
            return
        else:
            print("Didn't register...")
            print(response['message'])
            
            # Should be a function 'add register failed to win'
            font = pygame.font.SysFont("arial", 30)
            text_title = font.render(response['message'], 1, (154, 36, 21))    
            win.blit(text_title, (250, 400))
            pygame.display.update()  
            time.sleep(0.5)   
  
def main_menu():
    
    # Try to connect to Server
    if not initial_connection():
        print("Client closing in 30 seconds...")
        time.sleep(30)
        pygame.quit()
        exit()
        
    # Else:
    # Wait for Login or Register input
    logged_in = False
    waiting_in_menu = True
    while waiting_in_menu:
        redraw_mainmenu_fastapi(win)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting_in_menu = False
                pygame.quit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if 250 <= pos[0] <= 550 and 250 <= pos[1] <= 450:
                    logged_in, user_id = login_to_server()
                elif 250 <= pos[0] <= 550 and 500 <= pos[1] <= 700:
                    register_to_server()
                if logged_in:
                    waiting_in_menu = False                       
                
    response = requests.get(f"{api_url}lobby/state/{user_id}")
    response = response.json()
    print(response)
    if response["type"] == "lobby":   
        redraw_lobbyscreen(win)     
        # Display Lobby - including some stats AND 'PLAY' and 'Statistics' buttons
    else:
        # Error, lobby unavailable?? ....
        print("Error: Response isn't lobby but you've moved past the login screen...")
    
    # Wait for input
    while True:
        redraw_lobbyscreen(win) 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting_in_menu = False
                pygame.quit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if 250 <= pos[0] <= 550 and 250 <= pos[1] <= 450:
                    response = requests.post(f"{api_url}lobby/add_player_to_queue",  json={"user_id": user_id})
                    setup_game(user_id)
                    break
                # if Pos == "Statistics":
                #get_statistics() # stats aren't available yet
        
def setup_game(user_id):
    #print(response)
    game_id = 0
    waiting_for_game = True
    while waiting_for_game:
        response = requests.get(f"{api_url}games/", params = {"game_id" : game_id, "user_id" : user_id})
        response = response.json()
        print(response)
        if response["game"]:
            print("Game is about to begin.")
            game_id = response["game"]["game_id"]
            player_idx = response["game"]["player_idx"]
            game_out = response["game"]
            play_game(game_id, user_id, player_idx)
        else:
            time.sleep(3)
            print(response["message"])
            #display - waitingforgame - and message
    
        
def play_game(game_id :int, user_id: str, player_idx: int):
    """
    Plays game until it is over.
    Args: game_id, user_id    
    """
    response = requests.get(f"{api_url}games/", params = {"game_id" : game_id, "user_id" : user_id})    
    print(response.json())
    print(response.json()["game"])
    
    game = GameOut.model_validate(response.json()["game"])
    
    run = True
    details  = [player_idx, "ready"]
    response = requests.post(f"{api_url}games/update_game/", json = {"game_id" : game_id, "user_id": user_id, "details": details} )
    print(response.json())
    
    redrawWindow(win, game, player_idx, reset = True)

    while run: 
        details = [player_idx, "get"]
        time.sleep(2)
        response = requests.get(f"{api_url}games/", params = {"game_id" : game_id, "user_id" : user_id})
        game_new = GameOut.model_validate(response.json()["game"])
        #print(game_new)
        print(f"{game.game_state}")
        print(f"{game_new.game_state}")
        if f"{game.game_state}" != f"{game_new.game_state}":
            game = game_new
            details = update_game_clientside(game_new, player_idx) #without the whole current_phase vs new_phase thing  
            print(response.json())
        #if msg[1] == "reset":
        #    run  = False
        response = requests.post(f"{api_url}games/update_game/", json = {"game_id" : game_id, "user_id": user_id, "details": details} )
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()      
    
    
def update_game_clientside(game, player_idx):
    #global new_phase
    #global current_phase
    msg = []
    #current_phase = "blank"
    print("Begin new_phase")
    #new_phase = False
    if game.game_state[0] == 1 and game.game_state[1] == 1:
        clickable_objects = make_card_display([Card(name) for name in game.hand], "hand", "clickable")
        redrawWindow(win, game, player_idx)   ### draw deck, discard, action, hand, log
        print("Possibly stuck c")
        cards_selected = select_cards_to_play(game, player_idx, clickable_objects)
        print("Possibly stuck d")
        pygame.time.delay(1000)
        print(f"Cards selected: {cards_selected}")
        msg = [player_idx, "ready"]
        print("Possibly stuck e")
        msg.extend(cards_selected)
        print(f"New message is: {msg}")

    elif game.game_state[0] == 1 and game.game_state[1] == 2:
        print("Phase 12")
        redrawWindow(win, game, player_idx) ## draw hand, action, log, player_battlezone.
        pygame.time.delay(1000)
        msg = [player_idx, "ready"]

    elif game.game_state[0] == 1 and game.game_state[1] == 3:
        print("Phase 13")
        redrawWindow(win, game, player_idx)
        pygame.time.delay(1000) # wait two seconds
        msg = [player_idx, "ready"]## action, log, opponent_battlezone

    elif game.game_state[0] == 2 and game.game_state[1] < 4:
        print(f"Phase {game.game_state[0]}{game.game_state[1]}{game.game_state[2]}")
        # if you win or draw change players_ready to True.
        # else resolve action then be ready
        redrawWindow(win, game, player_idx) # battlezone (opponent, player and whole)
        msg = [player_idx, "ready"]
        #redrawWindow(win, game, player_idx, f"2{game.part}") # action/log, stats
        pygame.time.delay(1000)
        if game.reaction_activated[player_idx]:
            #redrawWindow(win, game, player_idx, f"2{game.part}")
            card_rank = request_reaction_response(win, game, player_idx, game.reaction_str[player_idx])
            msg = [player_idx, "ready", card_rank]
        else:
            pass

    elif game.game_state[0] == 2 and game.game_state[1] == 4:
        print("Phase 24")
        redrawWindow(win, game, player_idx)
        pygame.time.delay(1000)
        msg = [player_idx, "ready"]

    elif game.game_state[0] == 3 and game.game_state[1] == 1: ## Big screen update
        print("Phase 31")
        redrawWindow(win, game, player_idx)
        if game.supply_coin == player_idx:
            selected_card = select_from_supply(game, player_idx, game.money[player_idx])
            msg = [player_idx, "ready", selected_card]
        else:
            msg = [player_idx, "ready"]

    elif game.game_state[0] == 3 and game.game_state[1] == 2:
        print("Phase 32")
        redrawWindow(win, game, player_idx)
        if game.supply_coin != player_idx:
            selected_card = select_from_supply(game, player_idx, game.money[player_idx])
            msg = [player_idx, "ready", selected_card]
        else:
            msg = [player_idx, "ready"]

    elif game.game_state[0] == 3 and game.game_state[1] == 3:
        print("Phase 33")
        redrawWindow(win, game, player_idx)
        pygame.time.delay(1000)
        msg = [player_idx, "ready"]#, selected_card]
        redrawWindow(win, game, player_idx,  reset = True)
        pygame.time.delay(1000)

    elif game.game_state[0] == 4 and game.game_state[1] == 1:
        print("Phase 41")
        redrawWindow(win, game, player_idx) ## Whole window
        pygame.time.delay(1000)
        msg = [player_idx, "ready"]
        
    elif game.game_state[0] == 5 and game.game_state[1] == 1:
        print("Phase 51 - GameOver")
        redrawWindow(win, game, player_idx)
        pygame.time.delay(1000)
        print("Requesting game over response....")
        if request_gameover_response(win, game, player_idx) == "game_over":
            msg = [player_idx, "reset"] # Change to 'main menu' eventually
        else:
            print("**** game over response fail **** ")
            
        print(f"game over response: {msg}")
            
    return msg   
     
    
    
def add_to_queue(user_id):
    response = requests.post(f"{api_url}lobby/add_player_to_queue",  json={"user_id": user_id})

def get_statistics():
    pass
    
main_menu()
 #
    # loop
    # Get summary stats -> # players in queue, # players in game, player details to display
    # wait for next input -> add to queue or statistics
    # if add to queue -> get_queue state until you're no longer there
    # if statistics -> go to stats page until 'go_back' is clicked.
    #
    # When no longer in queue:
    # Loop -> get_game()
    # Wait for valid input from Player -> every second either get_game() or update_game()
    # 
    
    



#### Order:
# We are going to first try without Websockets - and instead use consistent API calls
# Open Client/Browser -> Main Menu
# Connect to Server (set up websocket)
# If player clicks LOGIN -> Get User / Pass or Register
# If form is submitted: -> Sent to API
# If response is success -> Continue to Lobby
# Else -> Do not continue -> ask for it again [LOOP]
# -> Display Lobby
# If player clicks 'start' -> add to queue
# Loop -> get_game -> if game exists -> play
# -> wait for response
# Loop through game, if you get valid clicks -> send request, continue to process 'get'.
# If 'game_over' and click -> return to lobby -> loops back to lobby start.