# -*-  coding: utf-8 -*-

import websocket

def on_message(ws, message):
    print(message)

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8888/ws",
                                on_message=on_message,
                                header={'user':'sample3'})

    ws.run_forever()