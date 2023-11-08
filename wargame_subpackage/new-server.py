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
            # Play the move.
            if data[1] == "reset":
                game.reset_game()
            elif data[1] == "ready":
                print("Game is ready...")
                if data[1] == "ready" and f"{game.phase}{game.part}" in ["11", "21", "22", "23", "31"] and not(game.players_ready[data[0]]):
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
    
        if game.check_players_health() == "game_over":
            print("GAME OVER!")
            game.set_game_over()
            #game.end_game()
            
        event = {
            "type": "play",
            "player": player,
            "game" : game
        }      
        print(f"reply occuring for {player}")
        print(f"Game: {game}")          
        # Send a "play" event to update the UI.        
        await websocket.send(pickle.dumps(event))
  


async def threaded_client(conn, p, gameId):
    print("Threaded client reached: ", p)
    print(gameId)
    #print(games[gameId])
    game = JOIN[gameId][0]
    global idCount
    try:        
        await conn.send(pickle.dumps(p))
        print("p has been sent")
    except:
        print("Failed to player id")
        print(p)
    reply = ""

    #while not(games[gameId].ready):
    while not game.ready:
        print(f"Game not ready yet: {p}")
        #await conn.send(pickle.dumps(games[gameId]))
        await conn.send(pickle.dumps(game))
        time.sleep(5)

    print("------------ Game is ready! ---------")
    #await conn.send(pickle.dumps(games[gameId]))
    await conn.send(pickle.dumps(game))

    while True:
        try:
            data = pickle.loads(await conn.recv())
            print(data)
            print("passed start of try loop")
            if gameId in games: # Check game still exists
                game = games[gameId]
                print(f"{p} : {game.players_ready}")
                print(f'{game.phase} : {game.part} : {game.subpart}')
                if game.check_players_health() == "game_over":
                    print("GAME OVER!")
                    game.set_game_over()
                    #game.end_game()
                    continue
                if not data:
                    break
                else:
                    # data is always an array with first element ("reset", "ready", "not-ready") or "get"
                    # check if reset, get, or move - Do something with the game
                    # e.g. draw hand, or assemble battle field, or run battles
                    # reply will be the game object
                    # Then client will take game object and redraw diplay or ask for input.
                    if data[1] == "reset":
                        game.reset_game()
                    elif data[1] == "ready":
                        if data[1] == "ready" and f"{game.phase}{game.part}" in ["11", "21", "22", "23", "31"] and not(game.players_ready[data[0]]):
                            game.update_game(data[0], data)
                        game.set_ready(data[0]) # set that player as ready
                        if game.players_ready == [True, True]:
                            print(f"--- This is the data: {data} ----------------")
                            game.next_part_or_phase()
                            game.play(data[0], data)
                            game.players_ready = [False, False]
                        #print("set ready")
                        # Play any possible actions for game, change ready back to False for each player, then reply with game state.
                        #print("played game")

                    reply = pickle.dumps(game)
                    print(f"reply occuring for {p}")
                    print # why does it never reply to 0
                    await conn.send(reply)
                    print(f"Game ID: {gameId}")
                    print(f"Games: {games}")
            else:
                print("Ok game isn't in games apparently")
                print(games)
                print(gameId)
                break
        except Exception as e:
            print("It's breaking")
            print(e)
            break

    print("Lost Connection")
    try:
        del games[gameId]
        print("Closing Game... ", gameId)
    except:
        pass
    idCount -= 1
    await conn.close()

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
    EVENTS["init"] == "Game Started"
    EVENTS["gameId"] = gameId

    join_key = 0
    JOIN[join_key] = game, connected

    try:
        # Send the secret access token to the browser of the first player,
        # where it'll be used for building a "join" link.
        event = {
            "type": "init",
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
    try:
        # Send the first move, in case the first player already played it.
        # await replay(websocket, game)
        # Receive and process moves from the second player.
        
        event = {
            "type": "init",
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
    

    if EVENTS["init"] == "Game Started":
        EVENTS["init"] == "No game available."
        await join(websocket, EVENTS["gameId"])
    else:
        EVENTS["init"] = "Game Started"
        await start(websocket)

   # if "join" in event:
    #    join(websocket, event["join"])
    #else:
        # First player starts a new game.
     #   await start(websocket)

"""
# create handler for each connection
async def handler(websocket, path):

    message = await websocket.recv()
    event = pickle.loads(message)
    print(f"Data recieved: {event['type']}")
    print(f"Data recieved: {event['message']}")
    idCount = int(event["message"])
    #await websocket.send("asdasdasd")
    #await websocket.send("asdasdasd")
    #await websocket.send("asdasdasd")
    #await websocket.send("asdasdasd")
    
    p = 0
    gameId = (idCount - 1)//2

    print(f"Game ID: {gameId}")
    if gameId not in JOIN: # new game required
        #games[gameId] = Game(gameId)
        game = Game(gameId)
        print("Creating a new game...")
        connected = {websocket}
        JOIN[gameId] = [game, connected]
        try:
            player = await threaded_client(websocket, p, gameId)
            t = threading.Thread(asyncio.run_until_complete(asyncio.wait(player)))
            t.start() # Start new game at each new connection
        finally:
            del JOIN[gameId] 
        
    else: # game is ready to be played
        game, connected = JOIN[gameId]
        game.ready = True
        connected.add(websocket)
        p = 1
        try:
            player = await threaded_client(websocket, p, gameId)
            t = threading.Thread(asyncio.run_until_complete(asyncio.wait(player)))
            t.start()
        finally:
            connected.remove(websocket)

"""

EVENTS = {'init' : "no game", 'gameId' :-9}
JOIN = {}

start_server = websockets.serve(handler, "localhost", 8000)

asyncio.get_event_loop().run_until_complete(start_server)

asyncio.get_event_loop().run_forever()