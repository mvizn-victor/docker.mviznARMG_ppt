#!/usr/bin/env python

# WS client example

from websocket import create_connection
uri = "ws://localhost:8765"
msg = "bleh bleh"

ws = create_connection(uri)
print("Sending 'Hello, World'...")
ws.send("Hello, World")
print("Sent")
print("Receiving...")
result =  ws.recv()
print("Received '%s'" % result)
ws.close()
