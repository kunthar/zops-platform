# # -*-  coding: utf-8 -*-

from zopsm.lib.settings import DATETIME_FORMAT
from zopsm.lib.settings import VIRTUAL_HOST
from zopsm.lib import sd_riak
from zopsm.lib import sd_rabbit
from pika import ConnectionParameters, SelectConnection
from threading import Thread
from datetime import datetime
import time
import json


class LogProcessor(object):
    def __init__(self, queue_name, exchange, bind_list):
        self.connection = None
        self.channel = None
        self.queue_name = queue_name
        self.bind_list = bind_list
        self.exchange = exchange

    def connect(self, host=None):
        """
        Connection with Rabbit.

        """
        if not host:
            _, host = list(json.loads(sd_rabbit.rabbit_nodes).items())[0]

        return SelectConnection(ConnectionParameters(host=host,
                                                     port=5672,
                                                     virtual_host=VIRTUAL_HOST,
                                                     credentials=sd_rabbit.rabbit_credential),
                                on_open_callback=self.on_connected,
                                on_close_callback=self.on_closed)

    def on_connected(self, connection):
        """
        AMQP connection callback.
        Creates input channel.

        Args:
            connection: AMQP connection

        """
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        """
        Input channel creation callback, exchange declaring.

        """
        self.channel = channel

        self.log_declare()

        self.channel.basic_consume(self.on_log_message,
                                   queue=self.queue_name,
                                   no_ack=True)

    def log_declare(self):
        """
        Exchange and queue are declared and routing keys are binded to queue.

        """
        self.channel.exchange_declare(exchange=self.exchange,
                                      type='topic',
                                      durable=True)

        self.channel.queue_declare(callback=None,
                                   queue=self.queue_name)

        for bind_key in self.bind_list:
            self.channel.queue_bind(callback=None,
                                    exchange=self.exchange,
                                    queue=self.queue_name,
                                    routing_key=bind_key)

    def on_closed(self, connection, _, __):
        """
        Moves listeners from close node's queue manager to queue's new master node.

        """
        client = sd_rabbit.get_suitable_client(json.loads(sd_rabbit.rabbit_nodes))
        new_master_node = client.get_queue(vhost=VIRTUAL_HOST, name=self.queue_name)['node']
        new_master_host = json.loads(sd_rabbit.rabbit_nodes)[new_master_node]
        self.connection = self.connect(host=new_master_host)
        self.connection.ioloop.start()

    def on_log_message(self, ch, method, properties, body):
        """
        Gets log messages from rabbit.
        
        """
        # print(" [x] %r:%r" % (method.routing_key, body))
        self.write_to_db(body)

    def write_to_db(self, body):
        """
        Log messages are saved to db with indexes.
        
        """
        # log_bucket.get_index('level_name_bin', startkey='INFO').results

        data = json.loads(body)
        store_data = {'msg': data['msg'],
                      'level_name': data['levelname'],
                      'host': data['host']
                      }

        obj = sd_riak.log_bucket.new(data=store_data)
        obj.add_index('host_bin', data['host'])
        obj.add_index('level_name_bin', data['levelname'])
        # Example time out: '2017-08-20T08:54:56.750Z00:00'
        obj.add_index('time_bin', datetime.now().strftime(DATETIME_FORMAT))
        obj.add_index('function_name_bin', data['funcName'])
        obj.store()

    def run(self):
        """
        Rabbit and riak watchers and log processor are run.
        
        """
        t1 = Thread(target=sd_rabbit.watch_rabbit)
        t2 = Thread(target=sd_riak.watch_riak)
        t1.start()
        t2.start()

        while not getattr(sd_rabbit, 'rabbit_nodes') or not getattr(sd_riak, 'log_bucket'):
            time.sleep(0.01)

        self.connection = self.connect()
        self.connection.ioloop.start()


