import random
import os
from zopsm.lib.sd_consul import consul_client
from zopsm.lib.credis import ZRedis
from zopsm.lib.log_handler import zlogger
from zopsm.lib.sd_vault import vault
from zopsm.lib.settings import WORKING_ENVIRONMENT

redis_master = None
redis_slave = None
redis_db_pw = vault.read('db/redis_{}'.format(WORKING_ENVIRONMENT))['data']['pw']


def watch_redis(single=False):
    global redis_master, redis_slave
    cur_index = None
    while True:
        index, data = consul_client.catalog.service('redis', index=cur_index, wait='10m')
        if index != cur_index:
            cur_index = index
            redis_nodes = [node['ServiceAddress'] for node in data]
            zlogger.info(f"Redis Nodes are changed. New nodes are {redis_nodes}.")
            redis_master, redis_slave = find_redis_role(redis_nodes)
            if single:
                zlogger.info(f"Redis Master: {redis_master}")
                zlogger.info(f"Redis Slave: {redis_slave}")
                return redis_master, redis_slave


def find_redis_role(redis_nodes):
    roles = {'master': [], 'slave': []}
    for node in redis_nodes:
        try:
            cache = ZRedis(host=node)
            cache.execute('PING')
        except Exception as e:
            zlogger.error(str(e))
            # If failPassword should be provided because Redis Master expects that.
            cache = ZRedis(host=node,
                           password=redis_db_pw)

        execute_role = cache.execute('ROLE')
        role_of_node = execute_role[0].decode()
        roles[role_of_node].append(node)

    return roles.get('master')[0], random.choice(roles.get('slave' if roles['slave'] else 'master'))

