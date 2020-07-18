# -*-  coding: utf-8 -*-
import os
import json
from datetime import timedelta

import consul
from tornado import websocket, web
from tornado.ioloop import IOLoop

from zopsm.mda.queue_manager import QueueManager
from zopsm.lib.credis import ZRedis
from zopsm.lib.sd_consul import consul_client, EnvironmentVariableNotFound
from zopsm.lib.log_handler import zlogger
from zopsm.lib.settings import WORKING_ENVIRONMENT
from zopsm.lib.settings import CACHE_TOKENS_KEYS

connections = {}

container_name = os.getenv('CONTAINER_NAME', 'mda')
container_port = int(os.getenv('CONTAINER_PORT', 9000))

host_ipv4 = os.getenv('DOCKER_HOST_IPV4')
if host_ipv4 is None:
    raise EnvironmentVariableNotFound('DOCKER_HOST_IPV4 should not be empty.')

rabbit_nodes = json.loads(os.getenv('RABBIT_NODES'))
# master = os.getenv('REDIS_HOST')
slave = os.getenv('REDIS_SLAVE')

cache = ZRedis(host=slave,
               db=os.getenv('REDIS_DB'))

if WORKING_ENVIRONMENT in ["zopsm", "develop"]:
    # Consul service and check registration
    check = consul.Check.http(
        url=f'http://{host_ipv4}:{container_port}/ping',
        timeout='1s',
        interval='10s',
        deregister='2m')
    consul_client.agent.service.register(
        name='mda',
        service_id=f'{container_name}',
        address=f'{host_ipv4}',
        port=int(container_port),
        check=check)


class MyWebSocketHandler(websocket.WebSocketHandler):
    """
    Web socket handler for open and close events.

    """

    def check_origin(self, origin):
        return True

    def get_user_info_and_token(self, token):
        """
        According to coming token, finds user info and token ttl  from cache.

        """
        token_key = cache.hmget(CACHE_TOKENS_KEYS, token)[0]
        if not token_key:
            zlogger.error("Unathorized error for token value:{}".format(token if token else "-"))
            raise web.HTTPError(status_code=401,
                                log_message='Unauthorized error')
        token_ttl = cache.ttl(token_key.decode())

        stored_value = cache.hgetall(token_key)
        user = {}
        if stored_value:
            for k, v in stored_value.items():
                user[k.decode()] = v.decode()

        return user, token_ttl

    def check_validity(self, user_info, request_user_id, token_ttl):
        """
        Checks that token and user_id aren't invalid.

        """
        user_id = user_info.get("user")
        if not user_id or not token_ttl > 60:
            zlogger.error("Unathorized error for value:{}".format(user_id))
            raise web.HTTPError(status_code=401,
                                log_message='Unauthorized error')
            # self.close(code=401, reason="Unauthorized error.")

        elif user_id != request_user_id:
            zlogger.error("Unauthorized error. user_id inside Request parameter({}) and "
                          "token(User id: {}) does not match.".format(request_user_id, user_id))
            raise web.HTTPError(status_code=401,
                                log_message='Unauthorized error')
            # self.close(code=401, reason="Unauthorized error.")

    def open(self, request_user_id, token):
        """
        To do when a new ws connection.

        """
        try:
            user_info, token_ttl = self.get_user_info_and_token(token)

            self.check_validity(user_info, request_user_id, token_ttl)

            IOLoop.current().add_timeout(deadline=timedelta(seconds=token_ttl),
                                         callback=self.token_timeout)
            queue_manager.add_event_listener(self, user_info)
        except Exception as exc:
            zlogger.error("An error occurred on open method inside MyWebSocketHandler. "
                          "Exc: {}".format(exc))
            self.close()

    def on_close(self):
        """
        To do when a ws connection close.

        """

        try:
            user_id = self.path_kwargs.get("request_user_id", None)
            if user_id:
                queue_manager.remove_event_listener(self, user_id)
        except Exception as exc:
            zlogger.error("An error occurred on close method inside MyWebSocketHandler. "
                          "Exc: {}".format(exc))

    def token_timeout(self):
        self.close()


class Ping(web.RequestHandler):
    def get(self):
        self.write('pong')


queue_manager = QueueManager()

application = web.Application([
    (r'/ws/subscribers/(?P<request_user_id>\w+)/token/(?P<token>.*)', MyWebSocketHandler),
    (r'/ping', Ping)
])
