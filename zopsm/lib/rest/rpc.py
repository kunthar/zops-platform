import json
import uuid
import pika
import threading
from time import sleep
from pika.exceptions import ConnectionClosed
import time
from falcon.errors import HTTPNotFound, HTTPUnauthorized, HTTPMissingParam, HTTPInvalidParam
from falcon.errors import HTTPBadRequest, HTTPConflict, HTTPForbidden
from falcon.errors import HTTPInternalServerError
from falcon.errors import HTTPError
from falcon.errors import status

# wait for WORKER_TIMEOUT second to get result of rpc call
# otherwise raise HTTPGatewayTimeout
WORKER_TIMEOUT = 10


class HTTPGatewayTimeout(HTTPError):
    def __init__(self, title=None, description=None, **kwargs):
        super(HTTPGatewayTimeout, self).__init__(status.HTTP_504, title=title,
                                                 description=description, **kwargs)


class UnKnownException(Exception):
    pass


"""
RPC Errors:
-32700	Parse error	Invalid JSON was received by the server. An error occurred on the server while parsing the JSON text.
-32600	Invalid Request	The JSON sent is not a valid Request object.
-32601	Method not found	The method does not exist / is not available.
-32602	Invalid params	Invalid method parameter(s).
-32603	Internal error	Internal JSON-RPC error.
-32000 to -32099	Server error	Reserved for implementation-defined server-errors.
"""

RPC_ERROR = {
    -32700: HTTPInternalServerError,
    -32600: HTTPInternalServerError,
    -32601: HTTPInternalServerError,
    -32602: HTTPInternalServerError,
    -32603: HTTPInternalServerError,
    -32001: HTTPInternalServerError,
    -32002: HTTPNotFound,
    -32003: HTTPGatewayTimeout,
    -32004: HTTPUnauthorized,
    -32005: HTTPConflict,
    -32006: HTTPBadRequest,
    -32007: HTTPForbidden,
    -32008: HTTPMissingParam,
    -32009: HTTPInvalidParam,
}


class RpcClient(object):
    internal_lock = threading.Lock()

    def __init__(self,
                 exchange="inter_comm",
                 connection_params=None,
                 rabbitmq_user="guest",
                 rabbitmq_pass="guest",
                 ):

        self.connection_params = connection_params if connection_params else  {
            "host": "localhost",
            "port": 5672,
        }

        self.credentials = pika.PlainCredentials(rabbitmq_user,
                                                 rabbitmq_pass)

        self.exchange = exchange
        self.exchange_declared = False
        self.connection = None
        self.channel = None

        self.open_connection()
        thread = threading.Thread(target=self._process_data_events)
        thread.setDaemon(True)
        thread.start()

    def _process_data_events(self):
        """
        In order to come over the "ERROR:pika.adapters.base_connection:Socket Error on fd 34: 104"
        adapted from:
            https://github.com/pika/pika/issues/439
            https://github.com/pika/pika/issues/439#issuecomment-36452519
            https://github.com/eandersson/python-rabbitmq-examples/blob/master/Flask-examples/pika_async_rpc_example.py
        """
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

        while True:
            with self.internal_lock:
                self.connection.process_data_events()
            sleep(0.05)

    def open_connection(self):
        """
        Connect to RabbitMQ.
        """

        if not self.connection or self.connection.is_closed:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(**self.connection_params,
                                                                                credentials=self.credentials))

        if not self.channel or self.channel.is_closed:
            self.channel = self.connection.channel()

        if not self.exchange_declared:
            self.channel.exchange_declare(exchange=self.exchange, exchange_type='topic', durable=True,
                                          auto_delete=False)
            self.exchange_declared = True

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

    def close_connection(self):
        """
        Close active connection.
        """

        if self.channel:
            self.channel.close()

        if self.connection:
            self.connection.close()

        self.connection, self.channel = None, None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)

    def rpc_call(self, method, params, blocking=True, time_limit=WORKER_TIMEOUT):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        params['trackable'] = not blocking

        self.message_properties = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.corr_id
        }

        try:
            if not self.connection or self.connection.is_closed or not self.channel or self.channel.is_closed:
                with self.internal_lock:
                    self.open_connection()

            with self.internal_lock:
                self.channel.basic_publish(
                    exchange=self.exchange,
                    routing_key='post_message',
                    properties=pika.BasicProperties(
                        reply_to=self.callback_queue,
                        correlation_id=self.corr_id,),
                    body=json.dumps(self.message_properties, ensure_ascii=False))

        except ConnectionClosed:
            with self.internal_lock:
                self.close_connection()
                self.open_connection()
            return self.rpc_call(method, params, blocking=blocking, time_limit=time_limit)

        except Exception as e:
            self.response = {"error": {"code": -32603, "message": "Can not connect AMQP or another error occured!"}, }
            self.close_connection()

        if not blocking and self.response is None:
            # todo check every response of non-blocking rpc to return the tracking id
            # indicates that the erroneous response of event can be tracked with this id via ws
            params['tracking_id'] = self.corr_id
            return params  # "Job is queued"

        deadline = time.time() + time_limit

        while self.response is None:
            time_limit = deadline - time.time()
            if time_limit <= 0:
                self.response = {"error": {"code": -32003, "message": "Worker timeout"}, }

        if "result" in self.response:
            return self.response['result']

        if "error" in self.response:
            error, msg = RPC_ERROR.get(self.response['error']['code'],
                                       UnKnownException), self.response['error']['message']
            raise error(description=msg)


