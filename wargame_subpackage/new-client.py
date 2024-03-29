import asyncio
import websockets
import pygame
import pickle
from client import redrawWindow, make_card_display, request_reaction_response, select_from_supply, select_cards_to_play, request_gameover_response
import time

display_width, display_height = (800, 800)
win = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Client")
current_phase = "blank"
new_phase = False

async def test():
    async with websockets.connect('ws://localhost:8000') as websocket:
        await websocket.send("1")

        # get all messages (not only with `update`)
        async for message in websocket:
            print(message)

async def receive_moves(game, websocket):
    try:
        print("Receiving Moves")
        event = await websocket.recv()
        event = pickle.loads(event)
        game = event["game"]
        player_idx = event["player"]
        print(f"Player ID : {player_idx}")
        msg = update_game_client(game, player_idx)
    except Exception as e:
        print("Error in Receive Moves")
        print(e)
    finally:
        return msg    

async def send_moves(msg, websocket):
    try:
        print("Sending Moves")
        event = {
            "type": "play",
            "data" : msg
        }                   
        await websocket.send(pickle.dumps(event))        
    except:
        print("Error in Sending Moves")


async def new_main():
    print("Starting new main")
    run = True
    clock = pygame.time.Clock()
    #n = Network()
    #async with websockets.connect('ws://localhost:8000') as websocket:
    #websocket = await websockets.connect('ws://<insert_AWS_ip>:8080')
    websocket = await websockets.connect('ws://localhost:8080')
    event = {"type" : "init", "message" : "hello"}
    await websocket.send(pickle.dumps(event))
    print("Sent TEST Event")
    event = await websocket.recv()
    print("You are player: ", event)
    print("You are player: ", pickle.loads(event))
    game_data = pickle.loads(event)
    game = game_data["game"]
    player_idx = game_data["player"]
    print("123")
    #async for message in websocket:
    #        print(message)

    waiting_for_game = False
    while waiting_for_game:
        print("now im waiting")
        next_message =  await websocket.recv()
        print("message recieved")
        print(next_message)
        async for message in websocket:
            print(message)
            print(pickle.loads(message))
            game = pickle.loads(message)
            try:
                if game.ready:
                    waiting_for_game = False
                    print("We are ready to go!")
            except:
                print("Not ready yet...")
            
    print("about to receive game object first")   
    #await websocket.send("test123") 
    #testx =  await websocket.recv()
    #game = pickle.loads(testx)
    print("received")
    print(game)   
    redrawWindow(win, game, player_idx, "41", reset = True)
    #n.send_to_server([player_idx, "ready"])
    msg = [player_idx, "ready"]
    #current_phase = "blank"
    
    # try using while run loop, and receive moves and send moves functions 
    #async for message in websocket:
    while run: 
        print("test")
        clock.tick(60)
        time.sleep(1)
        try:
            await send_moves(msg, websocket)
            msg = await receive_moves(game, websocket)
            #print(f"sending message: {msg}")
            #await websocket.send(pickle.dumps(msg))
            #game = await pickle.loads(websocket.recv())
            #print(f"receiving message: {game}") # it receives the game, but then never sends another message... so it's getting stuck somewhere
            #msg = [player_idx, "get"]
        except Exception as e:
            run = False
            print("Couldn't get game, sorry.")
            print(e)
            #break        
        #msg = update_game(win, game, player_idx)
                        # Listen for any events (card clicks)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                        
        
def update_game_client(game, player_idx):
    global new_phase
    global current_phase
    #current_phase = "blank"
    msg = [player_idx, "get"]
    game_phase = f"{game.phase}{game.part}{game.subpart}"
    if current_phase != game_phase:
        print(f"new_phase: current = {current_phase} -> new_phase = {game_phase}")
        current_phase = game_phase
        new_phase = True

    if new_phase:
        print("Begin new_phase")
        new_phase = False
        if game.phase == 1 and game.part == 1:
            clickable_objects = make_card_display(game.get_player(player_idx).hand.all_cards, "hand", "clickable")
            redrawWindow(win, game, player_idx, "11")   ### draw deck, discard, action, hand, log
            print("Possibly stuck c")
            cards_selected = select_cards_to_play(game, player_idx, clickable_objects)
            print("Possibly stuck d")
            pygame.time.delay(1000)
            print(f"Cards selected: {cards_selected}")
            msg = [player_idx, "ready"]
            print("Possibly stuck e")
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
            
        elif game.phase == 5 and game.part == 1:
            print("Phase 51 - GameOver")
            redrawWindow(win, game, player_idx, "41")
            pygame.time.delay(1000)
            print("Requesting game over response....")
            if request_gameover_response(win, game, player_idx) == "game_over":
                msg = [player_idx, "reset"] # Change to 'main menu' eventually
            else:
                print("**** game over response fail **** ")
                
            print(f"game over response: {msg}")
            
    return msg



asyncio.get_event_loop().run_until_complete(new_main())