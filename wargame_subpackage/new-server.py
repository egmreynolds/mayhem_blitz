import asyncio

import websockets
import socket
from _thread import *
from game import Game
import pickle
import threading

games = {}
idCount = 0

async def threaded_client(conn, p, gameId):
    print("Threaded client reached: ", p)
    print(gameId)
    print(games[gameId])
    global idCount
    try:
      await conn.send(pickle.dumps(p))
    except:
        print("Failed to player id")
        print(p)
    reply = ""

    while not(games[gameId].ready):
        print(f"Game not ready yet: {p}")

    print("------------ Game is ready! ---------")
    await conn.send(pickle.dumps(games[gameId]))

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

# create handler for each connection

async def handler(websocket, path):

    idCount = int(await websocket.recv())

    print(f"Data recieved: {idCount}")

    await websocket.send("asdasdasd")
    await websocket.send("asdasdasd")
    await websocket.send("asdasdasd")
    await websocket.send("asdasdasd")


    p = 0
    gameId = (idCount - 1)//2

    print(f"Game ID: {gameId}")
    if idCount % 2 == 1: # new game required
        games[gameId] = Game(gameId)
        print("Creating a new game...")
    else: # game is ready to be played
        games[gameId].ready = True
        p = 1

    player = await threaded_client(websocket, p, gameId)
    t = threading.Thread(asyncio.run_until_complete(asyncio.wait(player)))
    t.start() # Start new game at each new connection



start_server = websockets.serve(handler, "localhost", 8000)



asyncio.get_event_loop().run_until_complete(start_server)

asyncio.get_event_loop().run_forever()