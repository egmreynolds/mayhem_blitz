import asyncio

import websockets
import socket
from _thread import *
from game import Game
import pickle
import threading
import time

games = {}
idCount = 0

### PROBLEM: It seems to get messed up with Who is Who: e.g. Data received from 1: [0, 'get']
## PROBLEM: Also stuck on 'get' instead of progresssing to next step.
async def play(websocket, game, player, connected):
    """
    Receive and process moves from a player.
    """
    print(f"PLAY {player}")
    async for message in websocket:
        print("evaluating message on server")
        # Parse a "play" event from the UI.
        event = pickle.loads(message)
        assert event["type"] == "play"
        data = event["data"]  
        print(f"Data received from {player}: {data}")  
        try:
            # Play the move            
            if data[1] == "reset":
                # Return to start() or join() 
                game.set_reset(data[0])
                if game.check_reset_state():
                    print()
                    print("**** RESET GAME *****")
                    print()
                    return
                else:
                    return      
            elif data[1] == "ready":
                print("Game is ready...")
                if data[1] == "ready" and f"{game.phase}{game.part}" in ["11", "21", "22", "23", "31", "32"] and not(game.players_ready[data[0]]):
                    print("step1")
                    game.update_game(data[0], data)
                game.set_ready(data[0]) # set that player as ready
                if game.players_ready == [True, True]:
                    print(f"--- This is the data: {data} ----------------")
                    game.next_part_or_phase()
                    game.play(data[0], data)
                    game.players_ready = [False, False]
                    
                    
                            # why does it never reply to 0
            #await conn.send(reply)
            #print(f"Game ID: {gameId}")
                    
        except RuntimeError as exc:
            # Send an "error" event if the move was illegal.
            await error(websocket, str(exc))
            continue
        
        print(f"gameID: {game.id}")
    
        event = {
            "type": "play",
            "player": player,
            "game" : game
        }  
            
        if game.check_players_health() == "game_over":
            print("GAME OVER!")
            game.end_round()
            game.set_game_over()
            game.announce_winner()
            game.set_game_state("game_over")
            event["type"] = "end"
            event["game"] = game
                    
        print(f"reply occuring for {player}")
        print(f"Game: {game}")          
        # Send a "play" event to update the UI.        
        await websocket.send(pickle.dumps(event))
  
# 
async def start(websocket):
    print("START")
    global EVENTS
    global JOIN
    # Initialize a game, the set of WebSocket connections
    # receiving moves from this game, and access token.
    gameId = 0
    game = Game(gameId)
    connected = {websocket}
    #EVENTS["init"] = "Game Started"
    EVENTS["gameId"] = gameId

    join_key = 0
    JOIN[join_key] = game, connected
    
    event = {
            "type" : "wait",
            "player" : 0,
            "game" : game
        }
       
    while EVENTS["init"] != "No game available.":
        await websocket.send(pickle.dumps(event))
        print(EVENTS["init"])
        print("waiting for game")
        event = await websocket.recv()
        event = pickle.loads(event)  
        time.sleep(0.5)

    try:
        # Send the secret access token to the browser of the first player,
        # where it'll be used for building a "join" link.
        event = {
            "type": "play",
            "join": join_key,
            "player" : 0,
            "game": game
        }
        await websocket.send(pickle.dumps(event))

        # Temporary - for testing.
        print("first player started game", id(game))
        #async for message in websocket:
        #    print("first player sent", message)
        # Receive and process moves from the first player.
        #await threaded_client(websocket, game, 0, connected)
        await play(websocket, game, 0, connected)
        print("Testing await works")
        #t = threading.Thread(asyncio.run_until_complete(asyncio.wait(player)))
        print("Testing wait player")
        #t.start() # Start new game at each new connection

    finally:
        del JOIN[join_key]      
        
async def error(websocket, message):
    """
    Send an error message.
    """
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(pickle.dumps(event))  
        
async def join(websocket, join_key):
    """
    Handle a connection from the second player: join an existing game.
    """
    print('JOIN')
    # Find the Connect Four game.
    try:
        game, connected = JOIN[join_key]
    except KeyError:
        await error(websocket, "Game not found.")
        return
   # Register to receive moves from this game.
    connected.add(websocket)
    time.sleep(0.5)
    try:
        # Send the first move, in case the first player already played it.
        # await replay(websocket, game)
        # Receive and process moves from the second player.
        
        event = {
            "type": "play",
            "join": join_key,
            "player" : 1,
            "game": game
        }
        await websocket.send(pickle.dumps(event))
        await play(websocket, game, 1, connected)
    finally:
        connected.remove(websocket)

async def handler(websocket):
    # Receive and parse the "init" event from the UI.
    print("1")
    message = await websocket.recv()
    event = pickle.loads(message)
    print(event)
    assert event["type"] == "init"
    print(f"EVENTS: {EVENTS['init']}")
    
    event = {
        "type" : "login",
    }
    await websocket.send(pickle.dumps(event))
    
    # Wait for login credentials
    event = await websocket.recv()
    event = pickle.loads(event)
    
    assert event["type"] == "login"
    if event["username"] == "guest":
        if event["password"] == "guest123":
            event = {
                "type" : "lobby"                
            }
            await websocket.send(pickle.dumps(event))
        else:
            print("Password failed")
            return
    else:
        print("Username failed")
        return
    
    # Wait for game request - if it already exists -> join(), if it doesn't start()
    event = await websocket.recv()
    event = pickle.loads(event)
    
    assert event["type"] == "request_game"
    if event["type"] == "request_game":    
        if EVENTS["init"] == "Game Started":
            EVENTS["init"] = "No game available."
            await join(websocket, EVENTS["gameId"])
        else:
            EVENTS["init"] = "Game Started"
            await start(websocket)

   # if "join" in event:
    #    join(websocket, event["join"])
    #else:
        # First player starts a new game.
     #   await start(websocket)

EVENTS = {'init' : "no game", 'gameId' :-9}
JOIN = {}

#start_server = websockets.serve(handler, "localhost", 8000)
start_server = websockets.serve(handler, "localhost", 8080, ping_timeout = 120)

asyncio.get_event_loop().run_until_complete(start_server)

asyncio.get_event_loop().run_forever()