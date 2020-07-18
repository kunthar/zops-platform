from falcon import HTTPBadRequest, HTTPMethodNotAllowed
from zopsm.lib.rest.fields import ZopsAlphaNumericStringField
from zopsm.lib.rest.serializers import ZopsBaseDBSerializer
from zopsm.lib.cache.channel_cache import ChannelCache

from zopsm.lib.rest.custom import ZopsRetrieveUpdateDeleteApi, \
    ZopsContinuatedListCreateApi


class BannedChannelSerializer(ZopsBaseDBSerializer):
    channel = ZopsAlphaNumericStringField("Id of channel which is subject to ban/unban operation",
                                          write_only=True)
    subscriber = ZopsAlphaNumericStringField("Id of subscriber who is subject to ban/unban "
                                             "operation", write_only=True)


class BannedChannel(ZopsRetrieveUpdateDeleteApi):
    """
    Allows to unban a channel as a subscriber or unban a subscriber for channel as a channel
    manager.

    ### Code Examples:
    #### DELETE:
    In order to remove the ban of channel, it must be send a DELETE request to
    `https://api_baseurl/v1/roc/banned-channels/channels/{channel_id}/subscribers/{subscriber_id}`
    where `channel_id` is id of the channel to remove its ban and `subscriber_id` is id of the
    subscriber who wanted to remove the ban of a channel.

    > Warning
    >
    > `subscriber_id` must be of its own subscriber id of whose the one sending the request

    ##### Request:
    ```bash
    #bash
    curl \\
         --request DELETE \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/banned-channels/channels/138b38f2da994adb846464eb39b5b198/subscribers/8c83b4fffec34449a29131d6b6ed1216

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.delete("https://api_baseurl/v1/roc/banned-channels/channels/138b38f2da994adb846464eb39b5b198/subscribers/8c83b4fffec34449a29131d6b6ed1216",
                                headers=header)

    ```

    In order to remove the ban of a subscriber from a channel, it must be send a DELETE request to
    `https://api_baseurl/v1/roc/banned-channels/channels/{channel_id}/subscribers/{subscriber_id}`
    where `channel_id` is id of the channel and `subscriber_id` is id of the subscriber whose ban
    is wanted to remove.

    > Warning
    >
    > The one who sends the request must be a manager to unban a subscriber.

    ##### Request:
    ```bash
    #bash
    curl \\
         --request DELETE \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/banned-channels/channels/138b38f2da994adb846464eb39b5b198/subscribers/4bea5295de3c407d95c34ced9d67e546

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.delete("https://api_baseurl/v1/roc/banned-channels/channels/138b38f2da994adb846464eb39b5b198/subscribers/4bea5295de3c407d95c34ced9d67e546",
                                headers=header)

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "trackingId": "3deecb81-1de6-4434-baf1-51f91198188d"
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

    """
    # /banned-channels/{channel_id}/subscribers/{subscriber_id}
    serializer = BannedChannelSerializer()

    def __repr__(self):
        return "Unsubscribe From Channel"

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def _check_delete_request(user_id, channel_managers, subscriber_id):
        if not (user_id in channel_managers or user_id == subscriber_id):
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid parameter(s).",
                description="User not allowed to unsubscribe.")
        elif user_id in channel_managers:
            return "channel-manager"
        elif user_id == subscriber_id:
            return "subscriber"

    def delete(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        channel_id = kwargs.get('channel_id')
        subscriber_id = kwargs.get('subscriber_id')

        self.check_resource_id(channel_id)
        self.check_resource_id(subscriber_id)

        channel = ChannelCache(project_id, service, channel_id,
                               rpc_client=self.rpc_client).get_or_set()
        managers = channel['managers']
        unban_actor = self._check_delete_request(user_id, managers, subscriber_id)

        body = {
            "project_id": project_id,
            "channel_id": channel_id,
            "subscriber_id": subscriber_id,
            "service": service
        }

        rpc_params = {}
        if unban_actor == "channel-manager":
            rpc_params = self.rpc_client.rpc_call("unban_subscriber_by_channel", body,
                                                  blocking=False)
        elif unban_actor == "subscriber":
            rpc_params = self.rpc_client.rpc_call("unban_channel_by_subscriber", body,
                                                  blocking=False)
        tracking_id = rpc_params.get('tracking_id')
        # Delete methods responses does not checked by the serializer.
        return {"trackingId": tracking_id}

    def update(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def retrieve(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class BannedChannelList(ZopsContinuatedListCreateApi):
    """
    Allows to ban a channel as a subscriber or ban a subscriber for channel as a channel manager.

    ### Code Examples:
    #### POST:
    In order to ban a channel as a subscriber, it must be send a POST request to
    `https://api_baseurl/v1/roc/banned-channels` as in the following request.

    ##### Request:
    ```bash

    curl \\
         --request POST \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         --data-binary "{                                                                       \\
                \"channel\": \"138b38f2da994adb846464eb39b5b198\",  \\
                \"subscriber\": \"8c83b4fffec34449a29131d6b6ed1216\"  \\
         }" \\
         https://api_baseurl/v1/roc/banned-channels

    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    payload = {
        "channel": "138b38f2da994adb846464eb39b5b198",
        "subscriber": "8c83b4fffec34449a29131d6b6ed1216",
    }

    req = requests.post("https://api_baseurl/v1/roc/banned-channels",
                                headers=header, data=json.dumps(payload))

    ```

    In order to ban a subscriber for a channel as a channel manager, it must be send a POST request
    to `https://api_baseurl/v1/roc/banned-channels` as in the following request.

    ##### Request:
    ```bash

    curl \\
         --request POST \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         --data-binary "{                                                                       \\
                \"channel\": \"138b38f2da994adb846464eb39b5b198\",  \\
                \"subscriber\": \"4bea5295de3c407d95c34ced9d67e546\"  \\
         }" \\
         https://api_baseurl/v1/roc/banned-channels

    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    payload = {
        "channel": "138b38f2da994adb846464eb39b5b198",
        "subscriber": "4bea5295de3c407d95c34ced9d67e546",
    }

    req = requests.post("https://api_baseurl/v1/roc/banned-channels",
                                headers=header, data=json.dumps(payload))

    ```

    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "creationTime": null,
            "isActive": null,
            "isDeleted": null,
            "lastUpdateTime": null,
            "trackingId": "92728f72-8bed-4374-a3aa-87f0215b0472"
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

    """

    serializer = BannedChannelSerializer()

    def __repr__(self):
        return "Ban Channel-Subscriber"

    def __str__(self):
        return self.__repr__()

    def check_create_request(self, user, channel_id, subscriber_id):
        user_id = user.get('user')
        if channel_id:
            channel = ChannelCache(user.get('project'), user.get('service'), channel_id,
                                   rpc_client=self.rpc_client).get_or_set()
            managers = channel['managers']
            subscribers = channel['subscribers']

        if all([channel_id, subscriber_id]) and user_id not in managers:
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid body "
                      "parameter(s).",
                description="User:{} not allowed to ban a subscriber from this channel:{}. "
                            "'subscriber' must be sent as null to ban a channel which is user "
                            "in".format(user_id, channel_id))
        elif channel_id and not subscriber_id and user_id not in subscribers:
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid body "
                      "parameter(s).",
                description="User:{} not allowed the ban this channel:{}. "
                            "To ban a channel is required to be a subscriber of "
                            "it.".format(user_id, channel_id))
        elif not any([channel_id, subscriber_id]):
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid body "
                      "parameter(s).",
                description="In order to ban a channel it must be sent channel's id and null as "
                            "subscriber's id. To ban a subscriber for a channel requires both "
                            "channel and subscriber.")
        elif all([channel_id, subscriber_id]):
            return "channel-manager"
        elif channel_id and not subscriber_id:
            return "subscriber"

    def create(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        channel_id = validated.get('channel')
        subscriber_id = validated.get('subscriber')

        ban_actor = self.check_create_request(user, channel_id, subscriber_id)

        body = {
            "project_id": project_id,
            "channel_id": channel_id,
            "subscriber_id": subscriber_id,
            "service": service
        }

        if ban_actor == "channel-manager":
            return self.rpc_client.rpc_call("ban_subscriber_by_channel", body, blocking=False)
        elif ban_actor == "subscriber":
            channel = ChannelCache(user.get('project'), user.get('service'), channel_id,
                                   rpc_client=self.rpc_client).get_or_set()
            body['subscriber_id'] = user_id
            owners = channel['owner']
            if user_id in owners:
                raise HTTPBadRequest(
                    title="Bad Request.",
                    description="Channel owner cannot ban a channel, but it is allowed to delete "
                                "it.")
            return self.rpc_client.rpc_call("ban_channel_by_subscriber", body, blocking=False)

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def list(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())
