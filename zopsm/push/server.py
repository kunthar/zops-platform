import falcon
import consul
import os
from graceful.authentication import Token
from zopsm.lib.rest.response_logger import ResponseLoggerMiddleware
from zopsm.lib.rest.authentication import ZopsKeyValueUserStorage
from zopsm.push.resources.client import Client, ClientList
from zopsm.push.resources.message import Message, MessageList
from zopsm.push.resources.acknowledgement import Acknowledgement
from zopsm.push.resources.segment import Segment, SegmentList
from zopsm.push.resources.tag.tag import Tag, TagList
from zopsm.push.resources.tag.user_tag import UserTag, UserTagList
from zopsm.push.resources.tag.client_tag import ClientTag, ClientTagList
from zopsm.lib.settings import WORKING_ENVIRONMENT
from zopsm.lib.sd_consul import consul_client, EnvironmentVariableNotFound
from zopsm.lib.rest.resource import ResourceListResource, Ping

container_name = os.getenv('CONTAINER_NAME', 'push')
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
        name='push',
        service_id=f'{container_name}',
        address=f'{host_ipv4}',
        port=int(container_port),
        check=check)

auth_storage = ZopsKeyValueUserStorage()

app = application = falcon.API(
    middleware=[
        Token(auth_storage),
        ResponseLoggerMiddleware(),
    ]
)

endpoints = {
    # Client
    "/v1/push/clients/{client_id}": Client(),
    "/v1/push/clients": ClientList(),

    # Message
    "/v1/push/messages/{message_id}": Message(),
    "/v1/push/messages": MessageList(),

    # Acknowledgement
    "/v1/push/acknowledgements": Acknowledgement(),

    # Segment
    "/v1/push/segments": SegmentList(),
    "/v1/push/segments/{segment_id}": Segment(),

    # Tags
    "/v1/push/tags": TagList(),
    "/v1/push/tags/{tag_key}": Tag(),
    "/v1/push/tags/user": UserTagList(),
    "/v1/push/tags/user/{user_id}": UserTag(),
    "/v1/push/tags/client": ClientTagList(),
    "/v1/push/tags/client/{client_id}": ClientTag(),

    # Ping
    "/v1/ping": Ping(),
}

for uri, endpoint in endpoints.items():
    app.add_route(uri, endpoint)

app.add_route("/", ResourceListResource(endpoints))
