# -*-  coding: utf-8 -*-

import os
import json
import time
from threading import Thread

from pika import ConnectionParameters
from pika.adapters.tornado_connection import TornadoConnection

from zopsm.lib.log_handler import zlogger
from zopsm.lib import sd_rabbit, sd_redis
from zopsm.lib.settings import VIRTUAL_HOST
from zopsm.lib.settings import CACHE_TOKENS_KEYS, CACHE_SUBSCRIBER_CHANNELS
from zopsm.lib.credis import ZRedis
from zopsm.lib.sd_redis import redis_db_pw


class QueueManager(object):
    def __init__(self):

        self.connection = None
        self.channel = None
        self._connected = False

        self.event_listeners = {}
        self.connections = {}
        self.cache = None
        self.run()

    def run(self):
        t1 = Thread(target=sd_redis.watch_redis)
        t1.start()
        while not getattr(sd_redis, 'redis_master'):
            time.sleep(0.01)

        self.cache = ZRedis(host=sd_redis.redis_master,
                            password=redis_db_pw,
                            db=os.getenv('REDIS_DB'))
        self.connect()

    def connect(self, host=None):
        """
        Connection with Rabbit.

        """
        if self._connected:
            zlogger.info('PikaClient: Already connecting to RabbitMQ')
            return

        if not host:
            _, host = list(json.loads(sd_rabbit.rabbit_nodes).items())[0]
        zlogger.info('PikaClient: Connecting to RabbitMQ in Queue Manager')
        param = ConnectionParameters(
            host=host,
            port=5672,
            virtual_host=VIRTUAL_HOST,
            credentials=sd_rabbit.rabbit_credential
        )
        self.connection = TornadoConnection(param,
                                            on_open_callback=self.on_connected)

        self.connection.add_on_close_callback(self.on_closed)

        self._connected = True
        zlogger.info("Connection is successful: host:{}".format(host))

    def on_connected(self, connection):
        """
        AMQP connection callback.
        Creates input channel.

        Args:
            connection: AMQP connection

        """
        zlogger.info('PikaClient: connected to RabbitMQ')
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        """
        Input channel creation callback, exchange declaring.

        """
        zlogger.info('PikaClient: Channel open, Declaring exchange')
        self.channel = channel
        self.channel.exchange_declare(exchange='messages',
                                      type='topic',
                                      durable=True)

    def on_message(self, channel, method, header, body):
        """
        When message is received, prepare notifier list.
        
        """
        user_id = method.consumer_tag
        notify_list = self.event_listeners[user_id]
        self.notify_listeners(body, notify_list)

    def listen_messages(self, queue_name, user_id):
        """
        Listen rabbit messages.
        
        """
        self.channel.basic_consume(consumer_callback=self.on_message,
                                   queue=queue_name,
                                   consumer_tag=user_id,
                                   no_ack=True)

    def notify_listeners(self, message, notify_list):
        """
        Write message to notifier list.
        
        """
        for listener in notify_list:
            listener.write_message(message)

    def add_event_listener(self, listener, user_info):
        """
        Add listener to user set. If queue creation is new, 
        
        """
        user_id = user_info.get("user")
        if not self.event_listeners.get(user_id):
            queue_name = self.get_queue_name(user_id)
            self.channel.queue_declare(queue=queue_name, auto_delete=True, callback=None)
            self.event_listeners.setdefault(user_id, []).append(listener)
            self.input_queue_bind(queue_name, user_info)
            self.listen_messages(queue_name, user_id)
            self.cache.sadd('QueueList:{}'.format(user_id), queue_name)

        else:
            self.event_listeners[user_id].append(listener)
        zlogger.info(
            "New websocket connection is added for user which has user_id:{}".format(user_id))

    def remove_event_listener(self, listener, user_id):
        """
        Remove listener from listener list.
        
        """
        try:
            if self.event_listeners.get(user_id):
                self.event_listeners[user_id].remove(listener)
                if not self.event_listeners[user_id]:
                    self.channel.queue_delete(queue=self.get_queue_name(user_id))
                    del self.event_listeners[user_id]

        except Exception as exc:
            zlogger.error("An error occurred on remove_event_listener method inside QueueManager. "
                          "User Id: {}, Exception: {}".format(user_id, exc))

    def input_queue_bind(self, queue, user_info):
        """
        Input queue   declaration callback.
        Input Queue/Exchange binding done here

        Args:
            queue: input queue
            user_info: user information dict include project, service and user ids

        """
        bind_list = self.get_bind_list(user_info)

        for route_key in bind_list:
            self.channel.queue_bind(callback=None,
                                    exchange='messages',
                                    queue=queue,
                                    routing_key=route_key)

    def get_bind_list(self, user_info):
        """
        Args:
            user_info: user information dict include project, service and user ids
        """
        user_id = user_info.get("user")
        project_id = user_info.get("project")
        service = user_info.get("service")

        bind_list = [user_id]

        # 'CACHE_SUBSCRIBER_CHANNELS' key is Channels list of a user
        subs_channels_key = CACHE_SUBSCRIBER_CHANNELS.format(
            project_id=project_id,
            service=service,
            subscriber_id=user_id
        )

        channels = self.cache.smembers(subs_channels_key)
        channels = [channel_id.decode() for channel_id in channels]

        bind_list.extend(channels)
        return bind_list

    def on_closed(self, connection, _, __):
        """
        Moves listeners from close node's queue manager to queue's new master node.
        
        """
        self._connected = False

    @staticmethod
    def get_queue_name(user_id):
        """
        Gets queue name according to user id.
        
        """
        return "{}_{}".format(user_id, os.getpid())
