# -*-  coding: utf-8 -*-

import websocket

def on_message(ws, message):
    print(message)

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://35.198.112.97:9000/ws",
                                on_message=on_message,
                                header={'token':'testUser1'})

    ws.run_forever()