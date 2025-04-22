#!/usr/bin/env python

# WS server example

import asyncio
import websockets

async def hello(websocket, path):
    msg = await websocket.recv()
    print("RECVD Len", len(msg), "\n", msg)
    await websocket.send("RECVD Length %d" %len(msg))

start_server = websockets.serve(hello, "localhost", 8765, max_size = None)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
