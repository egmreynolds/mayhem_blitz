# Contains functions to recieve requests and send responses to a client
# Although I have solved the websockets problems, in the future more may arise and
# Because the game is turn-based, we can avoid the complexities that come with websockets 
# and instead use an API (fastAPI). Also good practice for building an API.
# Although maybe I still need websockets... learning...
from game import Game
import asyncio
from pydantic import BaseModel
from fastapi import FastAPI, BackgroundTasks, WebSocket

app = FastAPI()

GAMES = {}
PLAYERS_LOGGED_IN:str = []
PLAYERS_IN_QUEUE:str = []
PLAYERS_IN_GAME:str = []
GAMES_ABOUT_TO_START = {} # Dictionary keys: player_id, values = Game_id
USERS = {}

# There are players in game
# Players in queue
# and players who just left the queue but dont have their game_id yet -> games_about_to_start
background_tasks = BackgroundTasks()

## On Start Up ##
@app.on_event("startup")
async def startup_event():
    # Run the matchmake function as a background task on startup
    asyncio.create_task(matchmake())

## Matchmaking ##
async def matchmake():
    """
    Sets up Matchmaking. When 2 players in queue - set up a game between them
    Add players in queue to players in game.
    """
    while True:
        await asyncio.sleep(2)  # Adjust the sleep duration as needed
        print(f"Number of Players in Queue: {len(PLAYERS_IN_QUEUE)}")
        if len(PLAYERS_IN_QUEUE) >= 2:
            player1 = PLAYERS_IN_QUEUE.pop(0)
            #PLAYERS_IN_GAME.append(player1)
            player2 = PLAYERS_IN_QUEUE.pop(0)            
            #PLAYERS_IN_GAME.append(player2)
            
            # Start a new game with player1 and player2
            start_game(player1, player2)
            #background_tasks.add_task(start_game, player1, player2)
            
def start_game(player1: str, player2: str):
    """
    Sets up a new game for player1 and player2
    Adds game to GAMES
    Players will retrieve their new game when they call 'get_game' next...
    """
    game_id = hash(f"{player1}{player2}")
    print(game_id)
    GAMES_ABOUT_TO_START[player1] = [game_id, 0]
    GAMES_ABOUT_TO_START[player2] = [game_id, 1]
    game = Game(game_id)
    game.set_player_names(player1, player2)
    #game.phase = 1
    GAMES[game_id] = game
    
# Run Matchmaking:::
## Lobby ##
class User(BaseModel):
    user_id: str


@app.get("/lobby/state/{user_id}")
async def get_lobby(user_id: str):
    """
    Return Lobby state
    Lobby would include User, a few summary stats, a waiting for game state
    """
    print("get lobby function")
    return {"type" : "lobby", "user_id" : user_id}

@app.post("/lobby/add_player_to_queue")
async def add_player_to_queue(user: User):
    """
    Adds a player to the queue for their next game    
    """
    if user.user_id not in PLAYERS_IN_QUEUE and user.user_id not in PLAYERS_IN_GAME:
        PLAYERS_IN_QUEUE.append(user.user_id)
    return {"type" : "In queue", "user_id" : user.user_id}

@app.get("/lobby/get_number_of_players_in_queue")
async def get_number_of_players_in_queue():
    """
    Return the number of players in the QUEUE
    """
    return {"player_count" : len(PLAYERS_IN_QUEUE)}

@app.get("/lobby/get_number_of_players_in_game")
async def get_number_of_players_in_game():
    """
    Return the number of players in GAME
    """
    return {"player_count" : len(PLAYERS_IN_GAME)}

@app.get("/lobby/statistics/{user_id}")
async def get_stats(user_id: str):
    """
    Return Statistics for User
    """
    return {"statistics" : user_id}

## Games ##

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
    
def create_game_out(game: Game, player_idx: int):
    """
    Function to create the Pydantic model representing the Game for the Player.
    This can then be passed via json by the API to the client.
    Minimises information passed, avoids player getting info that should be private.
    game is a Game object
    player_idx is an int, either 0 or 1
    """
    game_out = GameOut(
        game_id = game.id,
        game_state = [game.phase, game.part, game.subpart],
        supply = list(set([card.rank for card in game.supply.all_cards])), # Gross
        supply_coin = game.supply_coin,
        
        health = [game.players[0].health, game.players[1].health],
        money = [game.players[0].money, game.players[1].money],
        reaction_activated = game.reaction_activated,
        reaction_str = game.reaction_str,
        cards_played = [[i.rank for i in game.players[0].cards_played],[i.rank for i in game.players[1].cards_played]],
        additional_cards_in_play = [[i.rank for i in game.players[0].additional_cards_in_play], 
                                     [i.rank for i in game.players[1].additional_cards_in_play]],
        
        player_idx = player_idx,
        hand = [i.rank for i in game.players[player_idx].hand.all_cards],
        log_text = game.players[player_idx].log_text,
        prompt = game.players[player_idx].prompt,
        deck_size = game.players[player_idx].deck.get_deck_size(),
        discard_size = game.players[player_idx].discard.get_deck_size()        
    )
    return game_out
    

class UpdateDetails(BaseModel):
    game_id: int
    user_id: str
    details: list


@app.post("/games/update_game/")
async def update_game(update_details: UpdateDetails):
    """
    Processes input made by player
    Returns updated game state 
    """
    game_id = update_details.game_id
    user_id = update_details.user_id
    details = update_details.details
    player_idx = details[0] # should be 0 or 1

    print(f"Details: {details}")  
    if details[1] == "get":
        return {"type": "game_state", "message" : "get_return"}
    elif details[1] == "reset":
        if game_id in GAMES.keys():
            GAMES[game_id].set_reset(player_idx)
            print("*** reset game ****")
            return {"type" : "game_state", "message" : "return_to_lobby"}
        else:
            return {"type": "game_state", "message" : "unexpected reset request"}
    elif details[1] == "ready": 
        if game_id in GAMES.keys():
            if user_id in [i.name for i in GAMES[game_id].players]:
                if not GAMES[game_id].players_ready[player_idx]:   
                    GAMES[game_id].update_game(player_idx, details)    
                GAMES[game_id].set_ready(player_idx)
                if GAMES[game_id].players_ready == [True, True]:
                    GAMES[game_id].next_part_or_phase()
                    GAMES[game_id].play(player_idx, details)
                    GAMES[game_id].players_ready = [False, False]                
                
                return {"type" : "game_state", "message" : "game updated successfully"}
            else: # Spectator Mode - Needs work.
                return {"type" :"game_state", "message" : "spectator mode not implemented"}
        else:
            return {"type" :"game_state", "message" : "game doesn't exist"}
    return {"type": "game_state", "message" : "details were not valid."}    
    

@app.get("/games/")
async def get_game(game_id: int, user_id: str):
    """
    Returns the current game state for this game of interest
    Additions: Check user is in the game, if game isn't open to spectators.
    """   
    print(f"UserId: {user_id}")
    print(f"GameId: {game_id}")
    if user_id in GAMES_ABOUT_TO_START.keys():
        print(f"Game: {GAMES_ABOUT_TO_START[user_id]}")
        print(f"Player0: {GAMES[GAMES_ABOUT_TO_START[user_id][0]].players[0]}")
    else:
        print()        
   
    if game_id in GAMES.keys():
        if GAMES[game_id].players[0].name == user_id:
            return {"game" : create_game_out(GAMES[game_id], 0)}
        elif GAMES[game_id].players[1].name == user_id:
            return {"game" : create_game_out(GAMES[game_id], 1)}
        else:
            ## Spectator Mode - to set up
            return {"game" : None, "message" : "Spectator Mode"}
    else:
        if user_id in PLAYERS_IN_QUEUE:
            return {"game" : None, "message" : "In Queue"}
        elif user_id in GAMES_ABOUT_TO_START.keys():
            if GAMES[GAMES_ABOUT_TO_START[user_id][0]].players[0].name == user_id:
                msg = {"game" : create_game_out(GAMES[GAMES_ABOUT_TO_START[user_id][0]], 0)}
            elif GAMES[GAMES_ABOUT_TO_START[user_id][0]].players[1].name == user_id:
                msg = {"game" : create_game_out(GAMES[GAMES_ABOUT_TO_START[user_id][0]], 1)}
            del GAMES_ABOUT_TO_START[user_id]
            PLAYERS_IN_GAME.append(user_id)
            return msg
        else:
            
            return {"game" : None, "message" : "This game doesn't exist or user/game combo isn't valid..."}

## Login ##

class LoginDetails(BaseModel):
    user_id: str
    user_pwrd: int
        
class RegisterDetails(BaseModel):
    user_id: str
    user_pwrd: int
    user_email: str
        
@app.get("/login/test")
def connect():
    """
    Simply aims to test the connection, done at client startup
    """        
    #background_tasks = BackgroundTasks()
    background_tasks.add_task(matchmake)
    return {"connect_status": True} 

@app.post("/login/connect")
async def connect_to_lobby(login_details: LoginDetails):
    """
    Takes input of username/password
    Checks with server to see if connection is valid
    Returns Lobby
    """  
    if login_details.user_id in USERS.keys():
        if login_details.user_pwrd == USERS[login_details.user_id]["password"]:
            if login_details.user_id in PLAYERS_LOGGED_IN:
                return {"login_status" : "failed", "message" : "Failed, You are already logged in..."}
            else:
                return {"login_status": "success", "message" : "Correct, you are logged in."}
        else:
            return {"login_status": "failed", "message" : "Incorrect, username and password do not match"}
    else:
        return {"login_status": "failed", "message" : "Incorrect, username and password do not match, try registering."}

@app.post("/login/register")
async def register(register_details: RegisterDetails):
    """
    Takes input - username, password, email_address
    # Need to remind user that this is completely unsecure    
    # Need to add checks that user_id or user_email aren't already in the database
    """
    #if user_id and user_email not in database
    if register_details.user_id not in USERS.keys():
        USERS[register_details.user_id] = {"password" : register_details.user_pwrd, "email" : register_details.user_email}
        return {"register_status" : "success", "message" : "Your account was successfully registered."}
    else:
        return {"register_status" : "failed", "message" : "Your username is already taken."}