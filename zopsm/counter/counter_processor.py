# # -*-  coding: utf-8 -*-

import time
import json
from zopsm.lib import sd_rabbit
from zopsm.lib import sd_riak
from threading import Thread
from zopsm.lib.sd_consul import consul_client
from zopsm.log.log_processor import LogProcessor
from urllib.request import Request, urlopen
from urllib.error import URLError
from queue import Queue
from zopsm.lib.settings import DATETIME_FORMAT
from datetime import datetime

SAAS_SERVICE_EVENT_ENDPOINT = '/api/v1/service-event/'
TIME_LIMIT = 10
MESSAGE_LIMIT = 100
RIAK_TIME_LIMIT = 600
RIAK_MESSAGE_LIMIT = 10000


class CounterProcessor(LogProcessor):
    def __init__(self, queue_name, exchange, bind_list):
        """
        riak_time: riak time to writing data to riak
        riak_counter: message counter to writing data to riak
        saas_time: saas time to send data to saas
        saas_counter: message counter to sending data to saas
        consul_index: consul data index
        saas_nodes: saas nodes getting from consul
        data: want to send data to saas

        data format:{
                        "project_id_1__service_code__service_event": value1,
                        "project_id_2__service_code__service_event": value2
                    }


        :param queue_name: counter queue name
        :param exchange: log exchange
        :param bind_list: counter bind list
        """
        super().__init__(queue_name, exchange, bind_list)
        self.saas_counter = 0
        self.data = {}
        self.saas_time = time.time()
        self.riak_time = time.time()
        self.riak_counter = 0
        self.data_queue = Queue()
        self.consul_index, self.saas_nodes = self.get_saas_nodes()

    def on_log_message(self, ch, method, properties, body):
        """
        Gets log messages from rabbit.
        If body funcName in actions then we prepare message to write the data_queue

        message format = "project_id__service_code__service_event" --->  "2398472938udsa987__roc__create_channel"

        """
        # print(" [x] %r:%r" % (method.routing_key, body))
        body = json.loads(body)
        message = "{}__{}__{}".format(body['project_id'], body['service'], body['funcName'])
        self.data_queue.put(message)

    def add_data(self):
        """
        we consume messages in data_queue.
        if saas time_limit or message_limit exceed then we call the send to saas function

        """
        while True:
            while not self.data_queue.empty():
                message = self.data_queue.get()
                value = self.data.get(message, 0)
                self.data[message] = value + 1
                self.saas_counter += 1

                if self.saas_counter >= MESSAGE_LIMIT:
                    self.send_to_saas()
            else:
                time.sleep(0.02)

            if time.time() - self.saas_time > TIME_LIMIT:
                self.send_to_saas()

    def send_to_saas(self):
        """
        We try to send data to saas.
        If error occur all saas node then we call saas node function to get new saas node and we reset the saas_counter
        and start_time
        if we don't send to data to saas and riak time out(600 second or 10000 message) then call the write_to_db
        function for writing data to riak
        """
        data = {"serviceData": self.data}
        data = json.dumps(data).encode('utf8')
        current_time = time.time()
        self.riak_counter += self.saas_counter
        self.saas_counter = 0
        self.saas_time = current_time

        if self.saas_nodes:
            for index in range(len(self.saas_nodes)):
                url = "http://{}{}".format(self.saas_nodes[index], SAAS_SERVICE_EVENT_ENDPOINT)
                req = Request(url=url, data=data, headers={"Content-Type": "application/json"})
                try:
                    urlopen(req)
                except URLError:
                    if index == len(self.saas_nodes) - 1:
                        new_consul_index, self.saas_nodes = self.get_saas_nodes()
                        if new_consul_index != self.consul_index:
                            self.consul_index = new_consul_index
                            self.send_to_saas()
                else:
                    self.riak_time = current_time
                    self.riak_counter = 0
                    self.data = {}
                    break
        else:
            self.consul_index, self.saas_nodes = self.get_saas_nodes()

        if self.riak_counter > RIAK_MESSAGE_LIMIT or current_time - self.riak_time > RIAK_TIME_LIMIT:
            self.write_to_db()
            self.riak_time = current_time
            self.riak_counter = 0
            self.data = {}

    def write_to_db(self, body=None):
        """
        if we don't send to data to saas and riak time out(600 second or 10000 message) then we write the data to riak
        log bucket with counter_bin(True) and time_bin(2017-08-20T08:54:56.750Z00:00) index
        """
        riak_object = sd_riak.log_bucket.new(data=self.data)
        riak_object.add_index("counter_bin", True)
        # Example time out: '2017-08-20T08:54:56.750Z00:00'
        riak_object.add_index("time_bin", datetime.now().strftime(DATETIME_FORMAT))
        riak_object.store()

    @staticmethod
    def get_saas_nodes():
        """
        we want to saas nodes from consul
        index: consul data index(if data changed then index value changed otherwise value remains the same)
        data: saas nodes --> ['127.0.0.1:8000','127.0.0.2:8000'
        """
        index, data = consul_client.catalog.service(service='saas', index=None)
        return index, ["{}:{}".format(node["ServiceAddress"], node['ServicePort']) for node in data]

    def run(self):
        """
        Rabbit and riak watchers and log processor are run.

        """
        t1 = Thread(target=sd_rabbit.watch_rabbit)
        t2 = Thread(target=sd_riak.watch_riak)
        t3 = Thread(target=self.add_data)
        t1.start()
        t2.start()
        t3.start()
        while not hasattr(sd_rabbit, 'rabbit_nodes') and not hasattr(sd_riak, 'log_bucket'):
            time.sleep(0.01)
        self.connection = self.connect()
        self.connection.ioloop.start()

