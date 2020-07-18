import consul
import os
from zopsm.lib.settings import WORKING_ENVIRONMENT
from zopsm.lib.sd_consul import consul_client, EnvironmentVariableNotFound

container_name = os.getenv('CONTAINER_NAME', 'sms')
container_port = int(os.getenv('CONTAINER_PORT', 9500))

host_ipv4 = os.getenv('DOCKER_HOST_IPV4')
if host_ipv4 is None:
    raise EnvironmentVariableNotFound('DOCKER_HOST_IPV4 should not be empty.')

if WORKING_ENVIRONMENT in ["zopsm", "develop"]:
    # Consul service and check registration
    check = consul.Check.http(
        url=f'http://{host_ipv4}:{container_port}/v1/ping',
        timeout='1s',
        interval='10s',
        deregister='2m')
    consul_client.agent.service.register(
        name='sms',
        service_id=f'{container_name}',
        address=f'{host_ipv4}',
        port=int(container_port),
        check=check)
