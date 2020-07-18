import os
import json
import logging
from pyrabbit2 import api
from zopsm.lib.sd_consul import consul_client
from zopsm.lib.sd_vault import vault
from pika import PlainCredentials
from zopsm.lib.settings import WORKING_ENVIRONMENT

rabbit_nodes = {}

rabbit_user = vault.read('db/rabbitmq_{}'.format(WORKING_ENVIRONMENT))['data']['username']
rabbit_pw = vault.read('db/rabbitmq_{}'.format(WORKING_ENVIRONMENT))['data']['password']
rabbit_credential = PlainCredentials(rabbit_user, rabbit_pw)


def watch_rabbit(single=False):
    cur_index = None
    while True:
        index, data = consul_client.catalog.service(service='rabbitmq', index=cur_index)
        if index != cur_index:
            cur_index = index
            global rabbit_nodes
            rabbit_nodes = {}
            for node in data:
                rabbit_nodes["rabbit@{}".format(node["Node"])] = node["ServiceAddress"]
            logging.info("RABBIT_NODES: {}\n".format(rabbit_nodes))
            rabbit_nodes = json.dumps(rabbit_nodes)
            if single:
                return rabbit_nodes


def get_suitable_client(rabbit_nodes=None):
    node_name, host = list(rabbit_nodes.items())[0]
    return api.Client(api_url='{}:15672'.format(host),
                      user=rabbit_user,
                      passwd=rabbit_pw)
