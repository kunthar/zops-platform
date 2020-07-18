from falcon import HTTPMethodNotAllowed, HTTPBadRequest
from graceful.fields import IntField

from zopsm.lib.rest.fields import ZopsAlphaNumericStringField, \
    ZopsListOfAlphaNumericStringsField, ZopsStringField, ZopsJsonObjectField
from zopsm.lib.rest.serializers import ZopsBaseDBSerializer
from zopsm.lib.rest.custom import ZopsRetrieveUpdateDeleteApi
from zopsm.lib.cache.subscriber_cache import SubscriberCache
from zopsm.roc.utils.common import generate_private_message_channel_name


class MeSerializer(ZopsBaseDBSerializer):
    id = ZopsAlphaNumericStringField("Unique identifier of the subscriber itself", read_only=True)
    contacts = ZopsListOfAlphaNumericStringsField("List of contacts of subscriber", read_only=True)
    channels = ZopsJsonObjectField("List of channels of subscriber", read_only=True)
    bannedChannels = ZopsListOfAlphaNumericStringsField("List of channels banned by subscriber",
                                                        read_only=True, source='banned_channels')
    bannedSubscribers = ZopsListOfAlphaNumericStringsField("List of subscribers banned by "
                                                           "subscriber", read_only=True,
                                                           source='banned_subscribers')
    lastStatusMessage = ZopsStringField("Last status message of subscriber", read_only=True,
                                        source='last_status_message')

    channelInvites = ZopsListOfAlphaNumericStringsField("List of channel invitations of subscriber",
                                                 read_only=True, source='channel_invites')
    channelJoinRequests = ZopsListOfAlphaNumericStringsField(
        "List of channel join requests of subscriber",
        read_only=True,
        source='channel_join_requests'
    )
    contactRequestsIn = ZopsListOfAlphaNumericStringsField(
        "List of contact requests to subscriber", read_only=True, source='contact_requests_in')
    contactRequestsOut = ZopsListOfAlphaNumericStringsField(
        "List of contact requests from subscriber", read_only=True, source='contact_requests_out')


class MeLastReadMessageSerializer(ZopsBaseDBSerializer):
    lastReadMessageId = ZopsAlphaNumericStringField("Unique identifier of the message")
    numberOfUnreadMessage = IntField("Number of unread message", source="number_of_unread_message",
                                     read_only=True)


class Me(ZopsRetrieveUpdateDeleteApi):
    """
    Allows to retrieve subscriber's own data such as contacts, channels etc.

    ### Code Examples:
    #### GET:
    ##### Request:
    ```bash
    #bash
    curl \\
         --request GET \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/me

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.get("https://api_baseurl/v1/roc/me",
                                headers=header)

    ```
    ##### Response:
    Response for initial subscriber.
    200 OK.
    ```json
    {
        "meta": {
            "params": {
                "indent": 0
            }
        },
        "content": {
            "id": "16effc7b7be64ce295464a1370a9a2db",
            "creationTime": "2017-08-20T08:54:56.750Z00:00",
            "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
            "isDeleted": false,
            "isActive": true,
            "contacts": [
                "203bce7b3f004d049bbbe06d49597727",
                "d6b81ac5747249c79a09381ee9e25c0f",
                "b607a35af40140dfb346e75e0b5f1e82"
            ],
            "channels": [
                "f6bed083fc1d45758fb884f2c90a62f9",
                "c9ec833cebe04243bdfbf7105c85d6c8",
                "f9f4a8a45dab4766b954c59d456c58a3"
            ],
            "bannedChannels": [
                "cb0481040ff847368981a2628dfccd04"
            ],
            "bannedSubscribers": [
                "9ef946edb1584b0c98edef00cbb0a835"
            ],
            "lastStatusMessage": "Hello world!",
            "channelInvites": [
                "2380d95edd294b7aa3970f97673cf6c3"
            ],
            "channelJoinRequests": [
                "379bba7e26ec4c39bff8c0f2a79462f8"
            ],
            "contactRequestsIn": [
                "b8c24273419d4cd4bd0768fe34385bf7"
            ],
            "contactRequestsOut": [
                "6d09ce39de754e08a47ba681aec685ae"
            ]
        }
    }
    ```

    """

    serializer = MeSerializer()

    def __repr__(self):
        return "Subscriber Retrieval"

    def __str__(self):
        return self.__repr__()

    def retrieve(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        body = {
            "project_id": project_id,
            "subscriber_id": user_id,
            "service": service
        }

        subscriber = SubscriberCache(
            user.get('project'),
            user.get('service'),
            user.get('user'),
            rpc_client=self.rpc_client).get()

        return subscriber or self.rpc_client.rpc_call("get_me", body)

    def delete(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def update(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class MeChannel(ZopsRetrieveUpdateDeleteApi):

    serializer = MeLastReadMessageSerializer()

    def __repr__(self):
        return "Update subscriber channel last read message"

    def update(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        channel_id = kwargs.get('channel_id')

        body = {
            "project_id": project_id,
            "subscriber_id": user_id,
            "service": service,
            "channel_id": channel_id,
            "lastReadMessageId": validated.get("lastReadMessageId")
        }
        subscriber_cache = SubscriberCache(user.get('project'), user.get('service'), user.get('user'),
                                     rpc_client=self.rpc_client)
        subscriber_data = subscriber_cache.get()
        if channel_id not in subscriber_data["channels"]:
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid body "
                      "parameter(s).",
                description="User is not channel member:'{}'".format(channel_id))
        rpc_params = self.rpc_client.rpc_call("update_channel_last_read_message", body,
                                              blocking=False)
        subscriber_cache.delete()
        return {
            "tracking_id": rpc_params.get('tracking_id'),
            "lastReadMessageId": validated.get("lastReadMessageId")
        }

    def retrieve(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        channel_id = kwargs.get('channel_id')
        body = {
            "project_id": project_id,
            "subscriber_id": user_id,
            "service": service,
            "channel_id": channel_id
        }
        return self.rpc_client.rpc_call("get_unread_message_number", body)

    def delete(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class MeContact(ZopsRetrieveUpdateDeleteApi):

    serializer = MeLastReadMessageSerializer()

    def __repr__(self):
        return "Update & Retrieve subscriber contact last read message"

    def update(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        contact_id = kwargs.get('contact_id')
        channel_id = generate_private_message_channel_name(user_id, contact_id)

        body = {
            "project_id": project_id,
            "subscriber_id": user_id,
            "service": service,
            "contact_id": contact_id,
            "lastReadMessageId": validated.get("lastReadMessageId"),
            "channel_id": channel_id
        }
        subscriber_cache = SubscriberCache(user.get('project'), user.get('service'), user.get('user'),
                                           rpc_client=self.rpc_client)
        subscriber_data = subscriber_cache.get()
        if contact_id not in subscriber_data["contacts"]:
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid body "
                      "parameter(s).",
                description="User is not contact with given subscriber:'{}'".format(contact_id))
        rpc_params = self.rpc_client.rpc_call("update_contact_last_read_message", body,
                                              blocking=False)
        subscriber_cache.delete()
        return {
            "tracking_id": rpc_params.get('tracking_id'),
            "lastReadMessageId": validated.get("lastReadMessageId")
        }

    def retrieve(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        contact_id = kwargs.get('contact_id')
        channel_id = generate_private_message_channel_name(user_id, contact_id)

        body = {
            "project_id": project_id,
            "subscriber_id": user_id,
            "service": service,
            "contact_id": contact_id,
            "channel_id": channel_id
        }

        return self.rpc_client.rpc_call("get_unread_contact_message_number", body)



