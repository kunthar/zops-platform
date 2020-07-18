#!/usr/bin/env python3
import json
import pika
import uuid
from zopsm.lib import sd_rabbit
from zopsm.lib.log_handler import zlogger
from zopsm.lib.settings import VIRTUAL_HOST

sd_rabbit.watch_rabbit(single=True)
rabbit_nodes = json.loads(sd_rabbit.rabbit_nodes)

rabbit_node_name = list(rabbit_nodes)[0]
rabbit_node_ip = rabbit_nodes[rabbit_node_name]


class Pinger(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbit_node_ip,
                                      virtual_host=VIRTUAL_HOST,
                                      credentials=sd_rabbit.rabbit_credential))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        self.message_properties = {
            "jsonrpc": "2.0",
            "method": "ping",
            "params": {"service": "roc"},
            "id": self.corr_id
        }
        self.channel.basic_publish(exchange='inter_comm',
                                   routing_key='get_message',
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=json.dumps(self.message_properties, ensure_ascii=False))
        zlogger.info("Send PING message to Riak.")
        while self.response is None:
            self.connection.process_data_events()
        return self.response


pinger = Pinger()

response = pinger.call()
response = json.loads(response.decode())
zlogger.info("Got {} from Ping Method".format(response))
if response['result'] == "PONG":
    exit(0)
else:
    exit(1)
