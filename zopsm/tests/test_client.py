import websocket
from concurrent.futures import ThreadPoolExecutor
from zopsm.lib.credis import ZRedis
import json


NUMBER_OF_THREADS = 5  # For online users

pool = ThreadPoolExecutor(NUMBER_OF_THREADS)

cache = ZRedis()


def assertions_5(counter):
    """

    Args:
        counter (dict): redis test counter dict

    Returns:

    """
    assert counter["testChannel3"] == 1


def assertions_6(counter):
    """

    Args:
        counter (dict): redis test counter dict

    Returns:

    """
    assert counter["testChannel3"] == 1


def assertions_7(counter):
    """

    Args:
        counter (dict): redis test counter dict

    Returns:

    """
    assert counter["testChannel3"] == 1


def assertions_8(counter):
    """

    Args:
        counter (dict): redis test counter dict

    Returns:

    """
    assert counter["testUser0"] == 1
    assert counter["testChannel3"] == 1


def assertions_9(counter):
    """

    Args:
        counter (dict): redis test counter dict

    Returns:

    """
    assert counter["testChannel3"] == 1


def remove_counters():
    cache.delete(*[
        "TestCounters:testUser5",
        "TestCounters:testUser6",
        "TestCounters:testUser7",
        "TestCounters:testUser8",
        "TestCounters:testUser9"
    ])


assertions = {
    "testUser5": assertions_5,
    "testUser6": assertions_6,
    "testUser7": assertions_7,
    "testUser8": assertions_8,
    "testUser9": assertions_9,
}


def on_message(ws, message):
    message = json.loads(message)
    token = ws.header.get("token")
    sender = message.get("sender")
    channel = message.get("channel")
    receiver = message.get("receiver")
    body = message.get("body")
    if body != "Start assertions":
        if receiver and channel:
            cache.hincrby("TestCounters:{}".format(token), sender)
        else:
            cache.hincrby("TestCounters:{}".format(token), channel)
    else:
        ws.close()
    print(message)


def on_close(ws):
    token = ws.header.get("token")
    counters = cache.hgetall("TestCounters:{}".format(token))
    count_dict = {}
    for k, v in counters.items():
        count_dict[k.decode()] = int(v.decode())
    assertions[token](count_dict)
    remove_counters()


def wake_client_up(token):
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8888/ws",
                                on_message=on_message,
                                on_close=on_close,
                                header={'token': token})
    ws.run_forever()


if __name__ == "__main__":
    remove_counters()
    for i in range(NUMBER_OF_THREADS):
        future = pool.submit(wake_client_up("testUser{}".format(i+5)))
