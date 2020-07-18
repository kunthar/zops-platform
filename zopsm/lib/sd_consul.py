from consul import Consul
from functools import reduce
import os

class EnvironmentVariableNotFound(Exception):
    """

    """
# what if consul_host = [], IndexError... ?
consul_host = os.getenv('CONSUL_HOST')
if consul_host is None:
    raise EnvironmentVariableNotFound('CONSUL_HOST should not be empty.')

consul_client = Consul(host=consul_host, port=8500, scheme='http')
consul_members = consul_client.agent.members()

def consul_role(acc, val):
    """
    :param acc: Accumulator to list addresses
    :param val: list item
    :return: list of consul servers
    """
    try:
        if val['Tags']['role'] == 'consul':
            acc.append(val['Addr'])
        return acc
    except AttributeError:
        pass

only_consul_servers = reduce(consul_role, consul_members, [])