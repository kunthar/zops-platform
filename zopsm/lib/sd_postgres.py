import os
from zopsm.lib.sd_consul import consul_client
from zopsm.lib.sd_vault import vault
from zopsm.lib.log_handler import zlogger
from zopsm.lib.settings import WORKING_ENVIRONMENT

postgres_nodes = {}
postgres_master_ip = None

postgres_user = vault.read('db/postgres_{}'.format(WORKING_ENVIRONMENT))['data']['username']
postgres_pw = vault.read('db/postgres_{}'.format(WORKING_ENVIRONMENT))['data']['password']


def watch_postgres(single=False):
    cur_index = None
    while True:
        index, data = consul_client.catalog.service('postgresql', index=cur_index, wait='10m')
        if index != cur_index:
            cur_index = index
            global postgres_nodes
            postgres_nodes = data[0]['ServiceAddress']
            zlogger.info(f"Postgresql Nodes are changed. New nodes are {postgres_nodes}.")
            if single:
                return postgres_nodes


def postgres_master(single=False):
    global postgres_master_ip
    cur_index = None
    while True:
        index, data = consul_client.kv.get('service/zopsmpa/leader', index=cur_index)
        if index != cur_index:
            cur_index = index
            postgres = watch_postgres(single=True)
            master_node_name = data["Value"]
            postgres_master_ip = postgres[master_node_name.decode()]
            if single:
                return postgres_master_ip
