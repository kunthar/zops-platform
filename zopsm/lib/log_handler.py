from zopsm.lib import sd_rabbit
from zopsm.lib.settings import VIRTUAL_HOST
from zopsm.lib.settings import WORKING_ENVIRONMENT
from python_logging_rabbitmq import RabbitMQHandlerOneWay
import logging
import os
import json
import sys


class ZRabbitMQHandlerOneWay(RabbitMQHandlerOneWay):
    def __init__(self, host='localhost', port=5672, connection_params=None,
                 username=None, password=None):
        super().__init__(
            host=host,
            port=port,
            connection_params=connection_params,
            routing_key_format="{name}.{level}.{purpose}",  # purpose: [general, counter, event]
            username=username,
            password=password)

    def emit(self, record):
        try:
            routing_key = self.routing_key_format.format(
                name=record.name,
                level=record.levelname,
                purpose=record.purpose if hasattr(record, 'purpose') else "general"
            )
            self.queue.put((record, routing_key))
        except Exception:
            self.channel, self.connection = None, None
            self.handleError(record)


try:
    nodes = os.environ['RABBIT_NODES']
    rabbit_nodes = json.loads(nodes)
except KeyError:
    rabbit_nodes = json.loads(sd_rabbit.watch_rabbit(single=True))


rabbit_host = list(rabbit_nodes.items())[0][1]
if os.getenv("LOG_LEVEL", "debug") == "debug":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
else:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

zlogger = logging.getLogger('{}_logger'.format(WORKING_ENVIRONMENT))

zlogger.addHandler(ZRabbitMQHandlerOneWay(host=rabbit_host,
                                         port=5672,
                                         connection_params={'virtual_host': VIRTUAL_HOST},
                                         username=sd_rabbit.rabbit_user,
                                         password=sd_rabbit.rabbit_pw
                                         ))
if os.getenv("LOG_LEVEL", "debug") == "debug":
    zlogger.setLevel(logging.DEBUG)
else:
    zlogger.setLevel(logging.INFO)
