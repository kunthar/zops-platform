import time
import json
import ssl
from zopsm.lib import sd_rabbit
from threading import Thread
from zopsm.counter.counter_processor import CounterProcessor
from urllib.request import Request, urlopen
from urllib.error import URLError
from queue import Queue
from zopsm.saas.log_handler import saas_logger
from zopsm.lib.settings import WORKING_ENVIRONMENT

CHAT_CHANNEL_ENDPOINT = 'https://talk.zetaops.io/hooks/u9xk65o667dydkk3sg58tyyhne' 
SAAS_NOTIFIER_ENDPOINT = '/api/v1/log-notifier/'
BIND_LIST = ['{}_logger.ERROR.general'.format(WORKING_ENVIRONMENT)]
# BIND_LIST = ['{}_logger.ERROR.general'.format(WORKING_ENVIRONMENT),
#              '{}_logger.WARNING.general'.format(WORKING_ENVIRONMENT)]
EXCHANGE_NAME = 'log'
QUEUE_NAME = 'notifier_queue'
TIME_LIMIT = 10
MESSAGE_LIMIT = 100
insecure_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # to bypass ssl validation errors


class LogNotifier(CounterProcessor):
    def __init__(self, queue_name, exchange, bind_list):
        """
        saas_time: saas time to send data to saas
        saas_counter: message counter to sending data to saas
        consul_index: consul data index
        saas_nodes: saas nodes getting from consul
        data: want to send data to saas

        data format:{
                        "project_id_1__service_code__service_event": value1,
                        "project_id_2__service_code__service_event": value2
                    }


        :param queue_name: notifier queue name
        :param exchange: log exchange
        :param bind_list: notifier bind list
        """
        super().__init__(queue_name, exchange, bind_list)
        self.saas_counter = 0
        self.data = []
        self.saas_time = time.time()
        self.data_queue = Queue()
        self.consul_index, self.saas_nodes = self.get_saas_nodes()

    def on_log_message(self, ch, method, properties, body):
        """
        Gets log messages from rabbit.
        If body funcName in actions then we prepare message to write the data_queue

        """
        body = json.loads(body)
        message = {"level_name": body['levelname'],
                   "function_name": body['funcName'],
                   "path_name": body['pathname'],
                   "line_number": body['lineno'],
                   "message": body['msg']}
        self.data_queue.put(message)

    def add_data(self):
        """
        we consume messages in data_queue.
        if saas time_limit or message_limit exceed then we call the send to saas function

        """
        while True:
            while not self.data_queue.empty():
                message = self.data_queue.get()

                self.data.append(message)
                self.saas_counter += 1

                if self.saas_counter >= MESSAGE_LIMIT:
                    if WORKING_ENVIRONMENT == "zopsm":
                        self.send_to_chat_channel(self.data)
                    self.send_to_saas()
            else:
                time.sleep(1)

            if time.time() - self.saas_time > TIME_LIMIT:
                if self.data:
                    if WORKING_ENVIRONMENT == "zopsm":
                        self.send_to_chat_channel(self.data)
                    self.send_to_saas()
                else:
                    self.saas_time = time.time()

    def send_to_saas(self):
        """
        We try to send data to saas.
        If error occur all saas node then we call saas node function to get new saas node and we retry to send data to saas
        and start_time
        """
        data = {"notifierData": self.data}
        data = json.dumps(data).encode('utf8')
        self.saas_counter = 0
        self.saas_time = time.time()

        if self.saas_nodes:
            for index in range(len(self.saas_nodes)):
                url = "http://{}{}".format(self.saas_nodes[index], SAAS_NOTIFIER_ENDPOINT)
                req = Request(url=url, data=data, headers={"Content-Type": "application/json"})
                try:
                    urlopen(req)
                except URLError as e:
                    if index == len(self.saas_nodes) - 1:
                        new_consul_index, self.saas_nodes = self.get_saas_nodes()
                        if new_consul_index != self.consul_index:
                            self.consul_index = new_consul_index
                            self.send_to_saas()
                else:
                    self.data = []
                    break
        else:
            self.consul_index, self.saas_nodes = self.get_saas_nodes()

    def send_to_chat_channel(self, body):
        """
        we try to send data to chat channel
        :param body:
        :return:
        """
        data_format = "```json\n{}\n```".format(json.dumps(body, indent=4))
        data = {"text": data_format}
        data = json.dumps(data).encode('utf8')
        url = CHAT_CHANNEL_ENDPOINT
        req = Request(url=url, data=data, headers={"Content-Type": "application/json"})
        try:
            urlopen(req, context=insecure_context)
        except URLError as e:
            saas_logger.error(e)

    def run(self):
        t1 = Thread(target=sd_rabbit.watch_rabbit)
        t2 = Thread(target=self.add_data)
        t1.start()
        t2.start()
        while not hasattr(sd_rabbit, 'rabbit_nodes'):
            time.sleep(0.01)
        self.connection = self.connect()
        self.connection.ioloop.start()


log_notifier = LogNotifier(QUEUE_NAME, EXCHANGE_NAME, BIND_LIST)
log_notifier.run()

