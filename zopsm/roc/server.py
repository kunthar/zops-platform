import falcon
import consul
import os
from graceful.authentication import Token
from zopsm.lib.rest.authentication import ZopsKeyValueUserStorage
from zopsm.lib.rest.response_logger import ResponseLoggerMiddleware
from zopsm.roc.resources.banned_channel import BannedChannel, BannedChannelList
from zopsm.roc.resources.banned_contact import BannedContact, BannedContactList
from zopsm.roc.resources.channel import Channel, ChannelList
from zopsm.roc.resources.contact import Contact
from zopsm.roc.resources.contact_request import ContactRequest, ContactRequestList
from zopsm.roc.resources.invite import Invite, InviteList
from zopsm.roc.resources.status import Status
from zopsm.roc.resources.subscriber import Subscriber
from zopsm.roc.resources.message import Message, MessageList
from zopsm.roc.resources.me import Me, MeContact, MeChannel
from zopsm.roc.resources.admin.channel import AdminChannelCreateResource
from zopsm.roc.resources.admin.channel import AdminChannelSubscribersCreateResource
from zopsm.roc.resources.admin.channel import AdminChannelResource
from zopsm.roc.resources.admin.contact import AdminContactResource
from zopsm.lib.sd_consul import consul_client, EnvironmentVariableNotFound
from zopsm.lib.rest.resource import ResourceListResource, Ping
from zopsm.lib.settings import WORKING_ENVIRONMENT


container_name = os.getenv('CONTAINER_NAME', 'gw')
container_port = int(os.getenv('CONTAINER_PORT', 8888))

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
        name='gw',
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
    "/v1/roc/messages/{message_id}": Message(),
    "/v1/roc/messages/": MessageList(),

    # Channel
    "/v1/roc/channels/{channel_id}": Channel(),
    "/v1/roc/channels/": ChannelList(),

    # Subscriber
    "/v1/roc/channels/{channel_id}/subscribers/{subscriber_id}": Subscriber(),

    # BannedChannel
    "/v1/roc/banned-channels/channels/{channel_id}/subscribers/{subscriber_id}":
        BannedChannel(),
    "/v1/roc/banned-channels": BannedChannelList(),

    # Invite
    "/v1/roc/invites/{invite_id}": Invite(),
    "/v1/roc/invites": InviteList(),

    # Contact
    "/v1/roc/contacts/{subscriber_id}": Contact(),

    # ContactRequest
    "/v1/roc/contact-requests/{invite_id}": ContactRequest(),
    "/v1/roc/contact-requests": ContactRequestList(),

    # BannedContact
    "/v1/roc/banned-contacts/{subscriber_id}": BannedContact(),
    "/v1/roc/banned-contacts": BannedContactList(),

    # Status
    "/v1/roc/status": Status(),

    # Me
    "/v1/roc/me": Me(),
    "/v1/roc/me/channels/{channel_id}": MeChannel(),
    "/v1/roc/me/contacts/{contact_id}": MeContact(),

    # Ping
    "/v1/ping": Ping(),

}

roc_admin_endpoints = {
    "/v1/roc/admin/create-channel": AdminChannelCreateResource(),
    "/v1/roc/admin/channels/{channel_id}": AdminChannelResource(),
    "/v1/roc/admin/channels/{channel_id}/subscribers": AdminChannelSubscribersCreateResource(),
    "/v1/roc/admin/contact": AdminContactResource(),
}


for uri, endpoint in endpoints.items():
    app.add_route(uri, endpoint)


for uri, endpoint in roc_admin_endpoints.items():
    app.add_route(uri, endpoint)

app.add_route("/", ResourceListResource(endpoints))
