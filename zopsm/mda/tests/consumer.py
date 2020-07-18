# -*-  coding: utf-8 -*-

import websocket

def on_message(ws, message):
    print("asfasdfasd")
    print(message)

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8888/ws",
                                on_message=on_message,
                                header={'token':'testUser5'})

    ws.run_forever()