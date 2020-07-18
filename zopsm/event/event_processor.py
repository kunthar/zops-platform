import os
import time
import json
from threading import Thread

from zopsm.lib import sd_rabbit
from zopsm.lib import sd_redis
from zopsm.log.log_processor import LogProcessor
from zopsm.lib.log_handler import zlogger
from zopsm.lib.settings import WORKING_ENVIRONMENT
from zopsm.lib.credis import ZRedis
from zopsm.lib.sd_redis import redis_db_pw

EVENT_BIND_LIST = ['{}_logger.INFO.event'.format(WORKING_ENVIRONMENT)]
EVENT_EXCHANGE = 'log'
EVENT_QUEUE = 'event_queue'


class EventProcessor(LogProcessor):
    def on_log_message(self, ch, method, properties, body):
        """
        Gets log messages from rabbit.

        Args:
            ch: Channel
            method: Method
            properties: Props
            body(dict): Body
                - params(dict): kwargs for methods
                - method(str): methods name

        Returns:
            None
        """

        try:
            body = json.loads(body)
            method_name = body.get('method', None)
            event_worker_method = getattr(self, method_name) if method_name else None
            if event_worker_method is not None:
                event_worker_method(**body['params'])
        except Exception as exc:
            zlogger.error("An error occurred on_log_message method inside EventProcessor."
                          "Exception: {}, ".format(exc))

    def run(self):
        """
        Rabbit and riak watchers and log processor are run.

        """
        t1 = Thread(target=sd_rabbit.watch_rabbit)
        t2 = Thread(target=sd_redis.watch_redis)
        t1.start()
        t2.start()
        while not hasattr(sd_rabbit, 'rabbit_nodes') and not hasattr(sd_redis, 'redis_master'):
            time.sleep(0.01)

        self.cache = ZRedis(host=sd_redis.redis_master,
                            password=redis_db_pw,
                            db=os.getenv('REDIS_DB'))
        self.connection = self.connect()
        self.connection.ioloop.start()

    def status_notify_contacts(self, **kwargs):
        """
        Method to notify online contacts about a subscriber's status update.
        Args:
            **kwargs(dict):
                - project_id(str):
                - service(str):
                - subscriber_id(str):
                - status_message(str):
                - behavioral_status(str):
                - status_intentional(str):
                - last_activity_time(str):
                - contacts_to_notify_key(str):

        Returns:

        """
        exchange = "messages"
        contacts_to_notify_key = kwargs['contacts_to_notify_key']
        contacts_to_notify = self.cache.smembers(contacts_to_notify_key)
        message = {
            "type": "status_delivery",
            "subscriberId": kwargs['subscriber_id'],
            "lastActivityTime": kwargs['last_activity_time'],
            "statusMessage": kwargs['status_message'],
            "behavioralStatus": kwargs['behavioral_status'],
            "statusIntentional": kwargs['status_intentional'],
        }

        for contact in contacts_to_notify:
            self.channel.basic_publish(
                exchange,
                contact.decode(),
                json.dumps(message, ensure_ascii=False))

        self.cache.delete(contacts_to_notify_key)

    def fails_non_blocking_jobs(self, **kwargs):
        """

        Args:
            **kwargs(dict):
                - trackingId(str): unique identifier matches with the triggered event
                - data(dict):
                    - title(str): title of the error
                    - description(str): "Event has failed."
                    - code(int): 500
                - usr_id(str): id of the target or subscriber to notify

        Returns:

        """
        exchange = "messages"
        message = {
            "type": "error",
            "trackingId": kwargs['trackingId'],
            "data": kwargs['data']
        }

        self.channel.basic_publish(
            exchange,
            kwargs['usr_id'],
            json.dumps(message, ensure_ascii=False))

    def channel_message_event(self, **kwargs):
        """

        Args:
            **kwargs(dict):
                - channelId(str): roc channel id
                - data(dict):
                    - title(str): title of the message
                    - body(str): message body
                    - sentTime(str): string representation of sent time
                    - creation_time(str): string representation of creation time(riak object)
                    - last_update_time(str): string representation of last update time(riak object)
                    - sender(str): id of the sender user

        Returns:

        """
        exchange = "messages"
        message = {
            "type": "channel_message",
            "messageId": kwargs['data'].get("id", None),
            "channelId": kwargs['channelId'],
            "title": kwargs['data'].get("title", None),
            "body": kwargs['data'].get("body", None),
            "sentTime": kwargs['data'].get("sentTime", None),
            "sender": kwargs['data'].get("sender", None),
        }

        self.channel.basic_publish(
            exchange,
            kwargs['channelId'],
            json.dumps(message, ensure_ascii=False))

    def direct_message_event(self, **kwargs):
        """

        Args:
            **kwargs(dict):
                - channelId(str): roc channel id
                - data(dict):
                    - title(str): title of the message
                    - body(str): message body
                    - sentTime(str): string representation of sent time
                    - creation_time(str): string representation of creation time(riak object)
                    - last_update_time(str): string representation of last update time(riak object)
                    - sender(str): id of the sender user

        Returns:

        """
        exchange = "messages"
        message = {
            "type": "direct_message",
            "messageId": kwargs['data'].get("id", None),
            "title": kwargs['data'].get("title", None),
            "body": kwargs['data'].get("body", None),
            "sentTime": kwargs['data'].get("sentTime", None),
            "sender": kwargs['data'].get("sender", None),
        }

        self.channel.basic_publish(
            exchange,
            kwargs['data']['receiver'],
            json.dumps(message, ensure_ascii=False))


event_processor = EventProcessor(EVENT_QUEUE, EVENT_EXCHANGE, EVENT_BIND_LIST)
event_processor.run()
