from falcon import HTTPBadRequest
from falcon import HTTPForbidden
from falcon import HTTPMethodNotAllowed
from zopsm.lib.rest.fields import ZopsAlphaNumericStringField
from zopsm.lib.rest.fields import ZopsStringField
from zopsm.lib.rest.fields import ZopsListOfAlphaNumericStringsField
from zopsm.lib.rest.fields import ZopsJsonObjectField
from zopsm.lib.rest.parameters import ZopsStringParam
from zopsm.lib.rest.serializers import ZopsBaseDBSerializer
from zopsm.roc.validators import channel_type_validator
from zopsm.lib.rest.custom import ZopsRetrieveUpdateDeleteApi
from zopsm.lib.rest.custom import ZopsContinuatedListCreateApi

from zopsm.lib.cache.channel_cache import ChannelCache

from zopsm.lib.utility import generate_uuid


class ChannelSerializer(ZopsBaseDBSerializer):
    id = ZopsAlphaNumericStringField("Unique identifier of channels", read_only=True)
    name = ZopsStringField("Name of channel")
    description = ZopsStringField("Short description of channel")
    channelType = ZopsStringField(
        "Type of channel e.g. `public`, `private`, `invisible`, `public-announcement`, "
        "`private-announcement`, and `invisible-announcement`",
        validators=[channel_type_validator], source="type")
    subscribers = ZopsListOfAlphaNumericStringsField("List of subscribers of channel",
                                                     read_only=True)
    lastMessage = ZopsJsonObjectField("Last message string text, sender, date", read_only=True,
                                      source="last_message")
    owners = ZopsListOfAlphaNumericStringsField("Subscriber(s) who owns channel", read_only=True,
                                                source="owner")
    managers = ZopsListOfAlphaNumericStringsField("Subscriber(s) who can manage channel",
                                                  read_only=True)
    invitees = ZopsListOfAlphaNumericStringsField("Subscribers who are invited to join to channel",
                                                  read_only=True)
    joinRequests = ZopsListOfAlphaNumericStringsField(
        "The requests sent by candidate subscribers of channel", read_only=True,
        source="join_requests")
    bannedSubscribers = ZopsListOfAlphaNumericStringsField(
        "Subscribers who are banned from channel", read_only=True, source='banned_subscribers')


class Channel(ZopsRetrieveUpdateDeleteApi):
    """
    Allows to retrieve, update and delete channel.

    ### Code Examples:
    #### GET:
    Retrieves a single channel for subscriber, channel manager and outsider with fields that they
    are allowed to see.
    ##### Request:
    ```bash
    #bash
    curl \\
         --request GET \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/channels/3c44c47cf9bf47948d10733ccb6448c9

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.get("https://api_baseurl/v1/roc/channels/3c44c47cf9bf47948d10733ccb6448c9",
                                headers=header)

    ```
    ##### Response:
    200 OK.

    While a channel subscribers will see following,
    ```json
    {
        "meta": {
            "params": {
                "indent": 0
            }
        },
        "content": {
            "id": "3c44c47cf9bf47948d10733ccb6448c9",
            "creationTime": "2017-08-20T08:54:56.750Z00:00",
            "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
            "isDeleted": false,
            "isActive": true,
            "name": "CENG-101 Introduction to Programming",
            "description": "Channel for the announcements of class CENG-101",
            "channelType": "public-announcement",
            "subscribers": [
                "3338423fefdf44029586679981d92ffd",
                "31a80814cd274828bfabae9a712411b3",
                "7f4db9a8070a4f4884839b8dbc2ef774"
            ],
            "lastMessage": {
                "text": "",
                "sender": "bb1c30ab18aa43359e4cf420876f7d23",
                "date": "2017-08-20T08:54:56.750Z00:00"
            },
            "owners": [
                "bb1c30ab18aa43359e4cf420876f7d23"
            ],
            "managers": [
                "bb1c30ab18aa43359e4cf420876f7d23",
                "d0bbe44040314b8aa2cf4356fa851d1a",
                "bf845d32818741c38575345d9d7e1f28"
            ],
            "invitees": null,
            "joinRequests": null,
            "bannedSubscribers": null
        }
    }
    ```

    channel manager will see:
    ```json
    {
        "meta": {
            "params": {
                "indent": 0
            }
        },
        "content": {
            "id": "3c44c47cf9bf47948d10733ccb6448c9",
            "creationTime": "2017-08-20T08:54:56.750Z00:00",
            "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
            "isDeleted": false,
            "isActive": true,
            "name": "CENG-101 Introduction to Programming",
            "description": "Channel for the announcements of class CENG-101",
            "channelType": "public-announcement",
            "subscribers": [
                "3338423fefdf44029586679981d92ffd",
                "31a80814cd274828bfabae9a712411b3",
                "7f4db9a8070a4f4884839b8dbc2ef774"
            ],
            "lastMessage": {
                "text": "",
                "sender": "bb1c30ab18aa43359e4cf420876f7d23",
                "date": "2017-08-20T08:54:56.750Z00:00"
            },
            "owners": [
                "bb1c30ab18aa43359e4cf420876f7d23"
            ],
            "managers": [
                "bb1c30ab18aa43359e4cf420876f7d23",
                "d0bbe44040314b8aa2cf4356fa851d1a",
                "bf845d32818741c38575345d9d7e1f28"
            ],
            "invitees": [
                "4d75adf7eaaf41b18e5c0b540e2e417f"
            ],
            "joinRequests": [
                "749d91c6c03f4b2894551edf68f8f778"
            ],
            "bannedSubscribers": [
                "dc67845710ef447897f389dbde47cd63"
            ]
        }
    }
    ```

    and an outsider will see:
    ```json
    {
        "meta": {
            "params": {
                "indent": 0
            }
        },
        "content": {
            "id": "3c44c47cf9bf47948d10733ccb6448c9",
            "creationTime": "2017-08-20T08:54:56.750Z00:00",
            "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
            "isDeleted": false,
            "isActive": true,
            "name": "CENG-101 Introduction to Programming",
            "description": "Channel for the announcements of class CENG-101",
            "channelType": "public-announcement",
            "subscribers": null,
            "lastMessage": null,
            "owners": null,
            "managers": null,
            "invitees": null,
            "joinRequests": null,
            "bannedSubscribers": null
        }
    }
    ```

    #### DELETE:
    Deletes the channel with given id.

    > Warning
    >
    > Only owners of the channel can delete the channel.

    ##### Request:
    ```bash
    #bash
    curl \\
         --request DELETE \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/channels/3c44c47cf9bf47948d10733ccb6448c9

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.delete("https://api_baseurl/v1/roc/channels/3c44c47cf9bf47948d10733ccb6448c9",
                                headers=header)

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "trackingId": "46bc42ae-586f-43c0-a002-c001737923cb"
        },
        "meta": {
            "params": {
                "indent": 0
            }
        }
    }
    ```

    > Warning
    >
    > Error response of this request, if any, will be delivered via WebSocket connection with
    > `trackingId` obtained from the response.


    #### PUT:
    Updates a channel with given id.

    > Warning
    >
    > Only managers of the channel can update the channel.

    ##### Request:
    ```bash

    curl \\
         --request PUT \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         --data-binary "{                                                                   \\
                \"name\": \"CENG-103 Discrete Structures\",   \\
                \"description\": \"Channel for the announcements of class CENG-103\",   \\
                \"channelType\": \"public-announcement\",   \\
            }" \\
         https://api_baseurl/v1/roc/channels/3c44c47cf9bf47948d10733ccb6448c9
    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    payload = {
        "name": "CENG-103 Discrete Structures",
        "description": "Channel for the announcements of class CENG-103",
        "channelType": "public-announcement",
    }

    req = requests.put("https://api_baseurl/v1/roc/channels/3c44c47cf9bf47948d10733ccb6448c9",
                                headers=header, data=json.dumps(payload))

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "bannedSubscribers": null,
            "channelType": "public-announcement",
            "creationTime": null,
            "description": "Channel for the announcements of class CENG-103",
            "id": "3c44c47cf9bf47948d10733ccb6448c9",
            "invitees": null,
            "isActive": null,
            "isDeleted": null,
            "joinRequests": null,
            "lastMessage": null,
            "lastUpdateTime": null,
            "managers": null,
            "name": "CENG-103 Discrete Structures",
            "owners": null,
            "subscribers": null,
            "trackingId": "7840abaa-8607-4fe0-bd94-a5642791250d"
        },
        "meta": {
            "params": {
                "indent": 0
            }
        }
    }
    ```
    > Warning
    >
    > Error response of this request, if any, will be delivered via WebSocket connection with
    > `trackingId` obtained from the response.



    ### Possible Errors
    - __Bad Request__: Probably it was made a request with invalid resource id.
    - __Object Not Found__: Probably you try to get, update or delete a non-existent resource.
    - __Forbidden__: Probably it was made a request that is not allowed for the role who send it.

    """
    serializer = ChannelSerializer()

    def __repr__(self):
        return "Channel Update & Delete & Retrieve"

    def __str__(self):
        return self.__repr__()

    def check_retrieve(self, user, channel_id):
        """
        Determines if given `user_id` is a manager of given `channel_id`, just a subscriber, or
        an outsider for the channel.

        Considering the role of subscriber who makes the retrieval of the channel, decides the which
        part of channel must be shown in the response.

        Args:
            user (dict): user dict obtained by the authentication
            channel_id (str): unique identifier of channel

        Returns:
            dict: Returns a channel object representation as dict

        Raises:
            HTTPBadRequest
        """
        user_id = user.get('user')
        channel = ChannelCache(user.get('project'), user.get('service'), channel_id,
                               rpc_client=self.rpc_client).get_or_set()
        if not channel:
            raise HTTPBadRequest(
                title="Bad Request. Channel:{channel} cannot be retrieved.".format(
                    channel=channel_id),
                description="User:{} not allowed to retrieve the information of channel:{}".format(
                    user_id, channel_id))

        managers = channel['managers']
        subscribers = channel['subscribers']
        is_public_channel = channel['type'] == "public" or channel['type'] == "public-announcement"

        if 'banned_subscribers' in channel:
            if user_id in channel['banned_subscribers']:
                raise HTTPForbidden(
                    title="Forbidden",
                    description="User:{} not allowed to retrieve the information of channel:{}".format(
                        user_id, channel_id))

        if is_public_channel:
            if user_id in managers:
                return channel
            else:
                subs_fields = ['name', 'type', 'description', 'subscribers', 'owner', 'managers',
                               'creation_time', 'last_update_time', 'is_deleted', 'is_active']
                return {field: channel[field] for field in subs_fields if field in channel}

        else:
            if user_id in managers:
                return channel
            elif user_id in subscribers:
                subs_fields = ['name', 'type', 'description', 'subscribers', 'owner', 'managers',
                               'creation_time', 'last_update_time', 'is_deleted', 'is_active']
                return {field: channel[field] for field in subs_fields if field in channel}
            else:
                outside_fields = ['name', 'type', 'description', 'creation_time', 'last_update_time',
                                  'is_deleted', 'is_active']
                return {field: channel[field] for field in outside_fields if field in channel}

    def retrieve(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        channel_id = kwargs.get('channel_id')
        self.check_resource_id(channel_id)

        return self.check_retrieve(user, channel_id)

    def check_delete(self, user, channel_id):
        user_id = user.get('user')
        channel = ChannelCache(user.get('project'), user.get('service'), channel_id, rpc_client=self.rpc_client).get_or_set()
        if user_id not in channel['owner']:
            raise HTTPForbidden(
                title="Forbidden.",
                description="Only owners can delete a channel!".format(
                    user_id, channel_id))

    def delete(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project')
        service = user.get('service')
        channel_id = kwargs.get('channel_id')
        self.check_resource_id(channel_id)
        self.check_delete(user, channel_id)
        body = {
            "project_id": project_id,
            "channel_id": channel_id,
            "service": service,
        }
        rpc_params = self.rpc_client.rpc_call("delete_channel", body, blocking=False)
        return {"trackingId": rpc_params['tracking_id']}

    def check_update(self, user, channel_id):
        user_id = user.get('user')
        channel = ChannelCache(user.get('project'), user.get('service'), channel_id,
                               rpc_client=self.rpc_client).get_or_set()
        if user_id not in channel['managers']:
            raise HTTPForbidden(
                title="Forbidden.",
                description="Only managers can update a channel!".format(
                    user_id, channel_id))

    def update(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project')
        service = user.get('service')
        channel_id = kwargs.get('channel_id')

        self.check_resource_id(channel_id)
        self.check_update(user, channel_id)
        body = {
            "project_id": project_id,
            "channel_id": channel_id,
            "service": service,
            "validated_channel": validated
        }
        rpc_params = self.rpc_client.rpc_call("update_channel", body, blocking=False)
        rpc_params.update(rpc_params['validated_channel'])
        rpc_params['id'] = channel_id
        return rpc_params


class ChannelList(ZopsContinuatedListCreateApi):
    """
    Allows to list and create channels.

    Channels correspond chat rooms. Messages can be sent and recieved by its subscribers. There are 6 types of channels:

    * __Public Group__:
    Any authenticated user can join public channels and can post and read any message without authorization. All
    subscribers are both consumer and producer at the same time.

    * __Private Group__:
    Only authorized users of public group channels can post and read messages. All subscribers are both consumer
    and producer at the same time.

    * __Invisible Private Group__:
    Invisible Private Group

    * __Public Announcement__:
    All authenticated users of announcement channels can read messages, since only one or some of them can post.

    * __Private Announcement__:
    All authorized users of announcement channels can read messages, since only one or some of them can post.

    * __Invisible Private Announcement__:
    Invisible Private Announcement

    ### Code Examples:
    #### GET:
    Lists the channels of subscriber by the `channelType` param. If it is not passed a `channelType` param, it
    will be listed all channels of subscriber by default.
    ##### Request:
    ```bash
    #bash
    curl \\
         --request GET \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/channels

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.get("https://api_baseurl/v1/roc/channels",
                                headers=header)

    ```
    ##### Response:
    200 OK.
    ```json
    {
        "meta": {
            "params": {
                "indent": 0,
                "page_size": 2
            }
        },

        "content": [
            {
                "id": "3c44c47cf9bf47948d10733ccb6448c9",
                "creationTime": "2017-08-20T08:54:56.750Z00:00",
                "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                "isDeleted": false,
                "isActive": true,
                "name": "CENG-101 Introduction to Programming",
                "description": "Channel for the announcements of class CENG-101",
                "channelType": "public-announcement",
                "subscribers": null,
                "lastMessage": null,
                "owners": null,
                "managers": null,
                "invitees": null,
                "joinRequests": null,
                "bannedSubscribers": null
            },
            {
                "id": "537e2cb33a0144289aef56c2ffb5273c",
                "creationTime": "2017-08-20T08:54:56.750Z00:00",
                "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                "isDeleted": false,
                "isActive": true,
                "name": "Welcome",
                "description": "Welcoming group for newbies",
                "channelType": "public",
                "subscribers": null,
                "lastMessage": null,
                "owners": null,
                "managers": null,
                "invitees": null,
                "joinRequests": null,
                "bannedSubscribers": null
            }
        ]
    }
    ```

    #### POST:
    Creates a new channel.
    ##### Request:
    ```bash

    curl \\
         --request POST \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         --data-binary "{                                                                   \\
                \"name\": \"CENG-103 Discrete Structures\",   \\
                \"description\": \"Channel for the announcements of class CENG-103\",   \\
                \"channelType\": \"public-announcement\",   \\
            }" \\
         https://api_baseurl/v1/roc/channels
    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    payload = {
        "name": "CENG-103 Discrete Structures",
        "description": "Channel for the announcements of class CENG-103",
        "channelType": "public-announcement",
    }

    req = requests.post("https://api_baseurl/v1/roc/channels",
                                headers=header, data=json.dumps(payload))

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "bannedSubscribers": [],
            "channelType": "public-announcement",
            "creationTime": null,
            "description": "Channel for the announcements of class CENG-103",
            "id": "2104f5f74d7844a399edc572c4efe42c",
            "invitees": [],
            "isActive": null,
            "isDeleted": null,
            "joinRequests": null,
            "lastMessage": null,
            "lastUpdateTime": null,
            "managers": [
                "34ce1c1b70154196ae8ca1598431ab98"
            ],
            "name": "CENG-103 Discrete Structures",
            "owners": [
                "34ce1c1b70154196ae8ca1598431ab98"
            ],
            "subscribers": [
                "34ce1c1b70154196ae8ca1598431ab98"
            ],
            "trackingId": "4a15ebee-cb73-4a3d-b501-0eca905bf7bf"
        },
        "meta": {
            "params": {
                "channelType": "all",
                "indent": 0
            }
        }
    }
    ```
    > Warning
    >
    > Error response of this request, if any, will be delivered via WebSocket connection with
    > `trackingId` obtained from the response.

    ### Possible Errors
    - __Bad Request__: Probably it was made a request with invalid resource id.
    - __Object Not Found__: Probably you try to get, update or delete a non-existent resource.


    """

    serializer = ChannelSerializer()

    def __repr__(self):
        return "Channel List & Create"

    def __str__(self):
        return self.__repr__()

    channelType = ZopsStringParam("Type of channel e.g. `public`, `private`, `invisible`, "
                           "`public-announcement`, `private-announcement`, and "
                           "`invisible-announcement`", validators=[channel_type_validator],
                           default='all')

    @staticmethod
    def _check_create_params(validated):
        success = [
            validated.get('name'),
            validated.get('type'),
        ]
        if not all(success):
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid body "
                      "parameter(s).",
                description="Channel must include all of 'name', and 'type'")
        return validated

    def _list(self, params, meta, **kwargs):
        return [self.serializer.to_representation(obj) for obj in self.list(params, meta, **kwargs)]

    def list(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        channel_type = params.get('channelType')

        body = {
            "project_id": project_id,
            "channel_type": channel_type,
            "subscriber_id": user_id,
            "service": service,
        }

        return self.rpc_client.rpc_call("list_channels", body)

    def create(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')

        channel_id = generate_uuid()

        self._check_create_params(validated)
        body = {
            "project_id": project_id,
            "created_by": user_id,
            "validated_channel": self._check_create_params(validated),
            "service": service,
            "channel_id": channel_id,
        }
        rpc_params = self.rpc_client.rpc_call("create_channel", body, blocking=False)
        return {
            "id": channel_id,
            "name": body['validated_channel']['name'],
            "description": body['validated_channel']['description'],
            "type": body['validated_channel']['type'],
            "banned_subscribers": [],
            "invitees": [],
            "joinRequests": [],
            "owner": [user_id],
            "managers": [user_id],
            "subscribers": [user_id],
            "tracking_id": rpc_params['tracking_id'],
        }

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())
