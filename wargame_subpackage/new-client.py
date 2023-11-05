import asyncio
import websockets

async def test():
    async with websockets.connect('ws://localhost:8000') as websocket:
        await websocket.send("1")

        # get all messages (not only with `update`)
        async for message in websocket:
            print(message)

asyncio.get_event_loop().run_until_complete(test())