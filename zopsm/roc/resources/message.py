from falcon import HTTPBadRequest, HTTPMethodNotAllowed, HTTPForbidden

from zopsm.lib.rest.fields import ZopsStringField, ZopsDatetimeField, ZopsAlphaNumericStringField

from zopsm.lib.rest.parameters import ZopsDateParam, ZopsAlphaNumericStringParam, \
    ZopsIntegerParam, ZopsStringParam

from zopsm.lib.rest.serializers import ZopsBaseDBSerializer
from zopsm.roc.utils.common import generate_private_message_channel_name
from zopsm.lib.cache.subscriber_cache import SubscriberCache
from zopsm.lib.cache.channel_cache import ChannelCache
from zopsm.lib.rest.custom import ZopsRetrieveUpdateDeleteApi, ZopsContinuatedListCreateApi
from zopsm.lib.utility import generate_uuid


class MessageSerializer(ZopsBaseDBSerializer):
    id = ZopsAlphaNumericStringField("Unique identifier of message", read_only=True)
    title = ZopsStringField("Generally null, it can be used rarely in more complex scenarios")
    body = ZopsStringField("Message content, max 1K string.")
    sender = ZopsAlphaNumericStringField("Subscriber id of message sender", read_only=True)
    receiver = ZopsAlphaNumericStringField("Subscriber id of message receiver")
    # e.g 2017-08-20T08:54:56.750Z00:00
    sentTime = ZopsDatetimeField("Time of client device")
    channel = ZopsAlphaNumericStringField("Channel id of which channel the message is sent to.")


class Message(ZopsRetrieveUpdateDeleteApi):
    """
    Allows to retrieve, update and delete single message.

    ### Code Examples:
    #### GET:
    Retrieves the message with given id.
    ##### Request:
    ```bash
    #bash
    curl \\
         --request GET \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/messages/ce65e1d6bac04be2a84d8d12cd846566

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.get("https://api_baseurl/v1/roc/messages/ce65e1d6bac04be2a84d8d12cd846566",
                                headers=header)

    ```
    ##### Response:
    200 OK.
    > Warning
    >
    > Following response is the result of retrieval of a single private chat message.
    > In private messages, there is a hypothetical channel for indexing purposes. It does not represent
    > a channel for real.

    ```json
    {
        "meta": {
            "params": {
                "indent": 0
            }
        },
        "content": {
            "id": "ce65e1d6bac04be2a84d8d12cd846566",
            "creationTime": "2017-08-20T08:54:56.750Z00:00",
            "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
            "isDeleted": false,
            "isActive": true,
            "title": "Hi",
            "body": "Hello World",
            "sender": "4f4acbd1bec04a2180380559bf0c8f3c",
            "receiver": "37e5f8d14c72431e8a9952d4817529e5",
            "sentTime": "2017-08-20T08:54:56.750Z00:00",
            "channel": "prv_37e5f8d14c72431e8a9952d4817529e5_4f4acbd1bec04a2180380559bf0c8f3c",
            "trackingId": null
        }
    }
    ```

    #### PUT:
    Updates a message with given body except receiver and channel fields. These fields cannot be
    updated and while sending an update body, it must be passed `null`.

    ##### Request:
    ```bash

    curl \\
         --request PUT \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         --data-binary "{                                                                   \\
                \"title\": \"Hi\",                                                          \\
                \"body\": null,                                                             \\
                \"receiver\": \"37e5f8d14c72431e8a9952d4817529e5\",                         \\
                \"sentTime\": \"2017-08-20T08:54:56.750Z00:00\",                            \\
                \"channel\": null                                                           \\
            }" \\
         https://api_baseurl/v1/roc/messages/ce65e1d6bac04be2a84d8d12cd846566
    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    payload = {
        "title": "Hi",
        "body": "Hello World",
        "receiver": None,
        "sentTime": "2017-08-20T08:54:56.750Z00:00",
        "channel": None,
    }

    req = requests.put("https://api_baseurl/v1/roc/messages/ce65e1d6bac04be2a84d8d12cd846566",
                                headers=header, data=json.dumps(payload))

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "body": "Hello World",
            "channel": null,
            "creationTime": null,
            "id": "ce65e1d6bac04be2a84d8d12cd846566",
            "isActive": null,
            "isDeleted": null,
            "lastUpdateTime": null,
            "receiver": null,
            "sender": "87568f8d735d47b28db719e156654e1a",
            "sentTime": "2017-08-20T08:54:56.750Z00:00",
            "title": "Hi",
            "trackingId": "443f0e7f-2f6c-4332-9dc8-48f3f479b4c2"
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

    #### DELETE:
    Deletes the message with given id.
    ##### Request:
    ```bash
    #bash
    curl \\
         --request DELETE \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/messages/ce65e1d6bac04be2a84d8d12cd846566

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.delete("https://api_baseurl/v1/roc/messages/ce65e1d6bac04be2a84d8d12cd846566",
                                headers=header)

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "id": "ce65e1d6bac04be2a84d8d12cd846566",
            "trackingId": "f4268c85-2111-49ef-a7a0-34f876d4652f"
        },
        "meta": {
            "params": {
                "indent": 0
            }
        }
    }
    ```

    ### Possible Errors
    - __Bad Request__: Probably it was made a request with invalid resource id.
    - __Object Not Found__: Probably you try to get, update or delete a non-existent resource.

    """
    serializer = MessageSerializer()

    def __repr__(self):
        return "Message Retrieve & Update & Delete"

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def _check_update_params(validated):
        receiver = validated.pop('receiver')
        channel = validated.pop('channel')
        if receiver or channel:
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid body "
                      "parameter(s).",
                description="It is not allowed to update the source which message has been "
                            "delivered to.")
        return validated

    def retrieve(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        msg_id = kwargs.get('message_id')
        service = user.get('service')
        self.check_resource_id(msg_id)
        body = {
            "message_id": msg_id,
            "project_id": project_id,
            "subscriber_id": user_id,
            "service": service
        }
        return self.rpc_client.rpc_call("get_message", body)

    def update(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        msg_id = kwargs.get('message_id')
        self.check_resource_id(msg_id)
        body = {
            "project_id": project_id,
            "message_id": msg_id,
            "subscriber_id": user_id,
            "validated_message": self._check_update_params(validated),
            "service": service,
        }

        rpc_params = self.rpc_client.rpc_call("update_message", body, blocking=False)
        return {
            "id": msg_id,
            "title": rpc_params['validated_message']['title'],
            "body": rpc_params['validated_message']['body'],
            "sender": user_id,
            "sentTime": rpc_params['validated_message']['sentTime'],
            "tracking_id": rpc_params['tracking_id'],
        }

    def delete(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        msg_id = kwargs.get('message_id')
        service = user.get('service')
        self.check_resource_id(msg_id)
        body = {
            "project_id": project_id,
            "message_id": msg_id,
            "subscriber_id": user_id,
            "service": service,
        }
        rpc_params = self.rpc_client.rpc_call("delete_message", body, blocking=False)

        return {"trackingId": rpc_params['tracking_id'], "id": msg_id}


class MessageList(ZopsContinuatedListCreateApi):
    """
    Allows to post a new message and list messages of subscriber by filters `subscriber`,
    `channel`, or `sentTime`.

    ### Code Examples:
    #### GET:
    Lists the messages by the `pageSize`, `continuation`, `subscriber`, `channel` and `sentTime`
    params.
    ##### Request:
    ```bash
    #bash
    curl \\
         --request GET \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/messages?page_size=2&channel=905f9cbf874f4111b740d520b4779899

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.get("https://api_baseurl/v1/roc/messages?page_size=2&channel=905f9cbf874f4111b740d520b4779899",
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
        "content": {
            "result": [
                {
                    "id": "ce65e1d6bac04be2a84d8d12cd846566",
                    "creationTime": "2017-08-20T08:54:56.750Z00:00",
                    "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                    "isDeleted": false,
                    "isActive": true,
                    "title": "Hi",
                    "body": "Hello World",
                    "sender": "4f4acbd1bec04a2180380559bf0c8f3c",
                    "receiver": null,
                    "sentTime": "2017-08-20T08:54:56.750Z00:00",
                    "channel": "905f9cbf874f4111b740d520b4779899"
                },
                {
                    "id": "13d86a6b6bd94af1ad4434fd39508911",
                    "creationTime": "2017-08-20T08:54:56.750Z00:00",
                    "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                    "isDeleted": false,
                    "isActive": true,
                    "title": "Hi",
                    "body": "Hello Work",
                    "sender": "cdfde3cd56b740f79f77d4558e0acca3",
                    "receiver": null,
                    "sentTime": "2017-08-20T08:54:56.750Z00:00",
                    "channel": "905f9cbf874f4111b740d520b4779899"
                }
            ],
            "continuation": "73893447ba5040d6a068a71f88ea38e5"
        }
    }
    ```
    OR
    ##### Request:
    ```bash
    #bash
    curl \\
         --request GET \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/messages?page_size=2&subscriber=4f4acbd1bec04a2180380559bf0c8f3c

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.get("https://api_baseurl/v1/roc/messages?page_size=2&subscriber=4f4acbd1bec04a2180380559bf0c8f3c",
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
        "content": {
            "result": [
                {
                    "id": "4bd5f1ea0d9049e79260c2cf514f8d43",
                    "creationTime": "2017-08-20T08:54:56.750Z00:00",
                    "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                    "isDeleted": false,
                    "isActive": true,
                    "title": "Hi",
                    "body": "Hello World",
                    "sender": "4f4acbd1bec04a2180380559bf0c8f3c",
                    "receiver": "cdfde3cd56b740f79f77d4558e0acca3",
                    "sentTime": "2017-08-20T08:54:56.750Z00:00",
                    "channel": "prv_4f4acbd1bec04a2180380559bf0c8f3c_cdfde3cd56b740f79f77d4558e0acca3"
                },
                {
                    "id": "b3dd269943544eda9a62b3da63aade57",
                    "creationTime": "2017-08-20T08:54:56.750Z00:00",
                    "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                    "isDeleted": false,
                    "isActive": true,
                    "title": "Hi",
                    "body": "Hello Work",
                    "sender": "cdfde3cd56b740f79f77d4558e0acca3",
                    "receiver": "4f4acbd1bec04a2180380559bf0c8f3c",
                    "sentTime": "2017-08-20T08:54:56.750Z00:00",
                    "channel": "prv_4f4acbd1bec04a2180380559bf0c8f3c_cdfde3cd56b740f79f77d4558e0acca3"
                }
            ],
            "continuation": "ed9d29bc4adb4fae84e5b0a3bf02b33d"
        }
    }
    ```
    > Warning
    >
    > The next pages can be obtained via requesting to
    > `https://api_baseurl/v1/roc/messages?page_size=2&channel=905f9cbf874f4111b740d520b4779899&continuation=73893447ba5040d6a068a71f88ea38e5` or
    > `https://api_baseurl/v1/roc/messages?page_size=2&subscriber=4f4acbd1bec04a2180380559bf0c8f3c&continuation=ed9d29bc4adb4fae84e5b0a3bf02b33d`.

    #### POST:
    Creates and posts a new message.
    ##### Request:
    Message to a receiver.
    ```bash

    curl \\
         --request POST \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         --data-binary "{                                                                       \\
                \"title\": \"Hi\",  \\
                \"body\": \"Hello World\",  \\
                \"receiver\": \"cdfde3cd56b740f79f77d4558e0acca3\",  \\
                \"sentTime\": \"2017-08-20T08:54:56.750Z00:00\",  \\
                \"channel\": null  \\
         }" \\
         https://api_baseurl/v1/roc/messages

    ```


    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    payload = {
        "title": "Hi",
        "body": "Hello World",
        "receiver": "cdfde3cd56b740f79f77d4558e0acca3",
        "sentTime": "2017-08-20T08:54:56.750Z00:00",
        "channel": null,
    }


    req = requests.post("https://api_baseurl/v1/roc/messages",
                                headers=header, data=json.dumps(payload))

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "body": "Hello World",
            "channel": null,
            "creationTime": null,
            "id": "b9b5a482a2644e34bc709f39f04dcf25",
            "isActive": null,
            "isDeleted": null,
            "lastUpdateTime": null,
            "receiver": "cdfde3cd56b740f79f77d4558e0acca3",
            "sender": "76e17243ce27436aba21588b92746cf1",
            "sentTime": "2017-08-20T08:54:56.750Z00:00",
            "title": "Hi",
            "trackingId": "b145b784-c566-496b-ac75-e30840d2503b"
        },
        "meta": {
            "params": {
                "indent": 0,
                "page_size": 10
            }
        }
    }

    ```
    OR

    ##### Request:
    Message to a channel.
    ```bash

    curl \\
         --request POST \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         --data-binary "{                                                                       \\
                \"title\": \"Hi\",  \\
                \"body\": \"Hello World\",  \\
                \"receiver\": null,  \\
                \"sentTime\": \"2017-08-20T08:54:56.750Z00:00\",  \\
                \"channel\": "1cb9684922874c6fbf32afcce8532fa1"  \\
         }" \\
         https://api_baseurl/v1/roc/messages

    ```


    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    payload = {
        "title": "Hi",
        "body": "Hello World",
        "receiver": null,
        "sentTime": "2017-08-20T08:54:56.750Z00:00",
        "channel": "1cb9684922874c6fbf32afcce8532fa1",
    }


    req = requests.post("https://api_baseurl/v1/roc/messages",
                                headers=header, data=json.dumps(payload))

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "body": "Hello World",
            "channel": "1cb9684922874c6fbf32afcce8532fa1",
            "creationTime": null,
            "id": "5560aaa87830428399ce5f7f3586ad99",
            "isActive": null,
            "isDeleted": null,
            "lastUpdateTime": null,
            "receiver": "",
            "sender": "437e40b0e6db4a57a248d0b599099203",
            "sentTime": "2017-08-20T08:54:56.750Z00:00",
            "title": "Hi",
            "trackingId": "2c7ad866-fe97-43f3-b07b-e772c10c8a12"
        },
        "meta": {
            "params": {
                "indent": 0,
                "page_size": 10
            }
        }
    }
    ```

    > Warning
    >
    > Error response of this request, if any, will be delivered via WebSocket connection with
    > `trackingId` obtained from the response.

    """

    serializer = MessageSerializer()

    def __repr__(self):
        return "Message Create & List"

    def __str__(self):
        return self.__repr__()

    subscriber = ZopsAlphaNumericStringParam(
        "Id of subscriber whose messages are listed between the subscriber makes request")
    channel = ZopsAlphaNumericStringParam("Channel id of desired message(s)")
    sentTime = ZopsDateParam("Sent time filter parameter")

    page_size = ZopsIntegerParam(
        details="Specifies number of result entries in single response",
        default='10'
    )

    continuation = ZopsStringParam(
        details="Key for retrieval of the next page if exists. It can only be obtained at the "
                "response of a list call."
    )


    @staticmethod
    def _check_list_params(user_id, channels_of_user, contacts_of_user, params):
        """
        Getting the specified list of messages requires some parameters, which
        are sender, receiver, channel and sentTime.

        They are expected to be sent by a logic, except the sentTime which always can be sent.

        |------------|---------|--------|
        | subscriber | channel | RESULT |
        |------------|---------|--------|
        |    0       |   0     |   0    |
        |------------|---------|--------|
        |    0       |   1     |   X    |
        |------------|---------|--------|
        |    1       |   0     |   X    |
        |------------|---------|--------|
        |    1       |   1     |   0    |
        |------------|---------|--------|

        0s under the subscriber and channel params represent the absence of them.
        1s represents the existence.

        0s under the RESULT column represents "400 Bad Request"
        Xs indicates that the existence of the parameters is valid, but it cannot be said that the
        request is completely valid. For example; only channel id exists in requests parameters,
        but the user who send this request is not allowed to see the messages of that channel. These
        cases also handled in the `failures` list below.

        Args:
            user_id (str): subscriber id of user obtained by his/her token
            channels_of_user:
            contacts_of_user:
            params:

        Returns:

        """
        body = {}
        subscriber_id = params.pop('subscriber', False)
        channel_id = params.pop('channel', False)
        sent_time = params.pop('sentTime', False)
        continuation = params.pop('continuation', False)

        counter = 0
        for a in [subscriber_id, channel_id]:
            if not a:
                counter += 1

        if counter == 1:
            if channel_id and channel_id not in channels_of_user:
                raise HTTPBadRequest(
                    title="Bad Request. Client sent a request which includes invalid parameter(s).",
                    description="User not in this channel:'{}'".format(channel_id))
            elif subscriber_id and (subscriber_id == user_id or subscriber_id not in contacts_of_user):
                raise HTTPBadRequest(
                    title="Bad Request. Client sent a request which includes invalid parameter(s).",
                    description="User is not allowed to send/receive messages "
                                "to/from subscriber:'{}'".format(subscriber_id))
            elif channel_id:
                body['channel'] = channel_id
            else:
                body['channel'] = generate_private_message_channel_name(user_id, subscriber_id)
        else:
            if not (subscriber_id or channel_id):
                raise HTTPBadRequest(
                    title="Bad Request. Client sent a request which does not include required "
                          "parameter(s).",
                    description="One of the parameters from 'subscriber, channel' must be "
                                "included in the request.")

            if subscriber_id and channel_id:
                raise HTTPBadRequest(
                    title="Bad Request. Client sent a request which includes invalid parameter(s).",
                    description="This resource accepts one parameter at a time for 'subscriber', "
                                "and 'channel'. Client sent subscriber:{0} "
                                "and channel:{1}.".format(subscriber_id, channel_id))
        if sent_time:
            body['sent_time'] = sent_time

        if continuation:
            body['continuation'] = continuation

        return {**body, **params}

    def _check_create_params(self, user_id, channels_of_user, contacts_of_user, validated,
                             project_id, service):
        """
        Checks the body parameters of the POST request if they are valid.
            - If it is a legal request
            - If it is a private chat message
            - If it is a channel chat message
        Args:
            user_id (str): subscriber id of the user obtained by his/her token
            channels_of_user (list): list of channels which subscriber in
            contacts_of_user (list): list of contacts which subscriber has
            validated (dict): dict of body parameters including title, body, receiver, sentTime,
channel
        Returns:
            dict
        """
        # validated becomes a dict with keys [title, body, receiver, sentTime, channel]
        receiver_id = validated.pop("receiver")
        channel_id = validated.pop("channel")
        # validated becomes a dict with keys [title, body, sentTime]
        if bool(receiver_id) != bool(channel_id):
            if receiver_id and (receiver_id == user_id or receiver_id not in contacts_of_user):
                raise HTTPBadRequest(
                    title="Bad Request. Client sent a request which includes invalid body "
                          "parameter(s).",
                    description="User is not allowed to send messages "
                                "to receiver:'{}'".format(receiver_id))
            elif channel_id and channel_id not in channels_of_user:
                raise HTTPBadRequest(
                    title="Bad Request. Client sent a request which includes invalid body "
                          "parameter(s).",
                    description="User is not allowed to send messages "
                                "to channel:'{}'".format(channel_id))
            elif receiver_id:
                # validated becomes a dict with keys [title, body, sentTime]
                validated['receiver'] = receiver_id
                validated['channel'] = generate_private_message_channel_name(user_id, receiver_id)
                # validated becomes a dict with keys [title, body, sentTime, receiver, channel]
            elif channel_id:
                channel = ChannelCache(project_id, service, channel_id,
                                       rpc_client=self.rpc_client).get_or_set()
                if channel['type'] in ('public-announcement',
                                       'private-announcement',
                                       'invisible-announcement') and user_id not in channel['managers']:
                    raise HTTPForbidden(
                        title="Forbidden",
                        description="Only managers can sent message to {} channel".format(
                            channel['type']))

                # validated becomes a dict with keys [title, body, sentTime]
                validated['receiver'] = ""
                validated['channel'] = channel_id
                # validated becomes a dict with keys [title, body, sentTime, receiver, channel]
        else:
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid body "
                      "parameter(s).",
                description="A message must include only one of receiver or channel. It can have "
                            "neither both nor none. If one is present, the other must be 'null'.")
        # validated becomes a dict with keys [title, body, sentTime, receiver, channel]
        validated['sender'] = user_id
        # validated becomes a dict with keys [title, body, sentTime, receiver, channel, sender]
        return validated

    def list(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.pop("user")
        project_id = user.pop('project')
        service = user.pop('service')
        subscriber = SubscriberCache(project_id, service, user_id,
                                     rpc_client=self.rpc_client).get_or_set()
        contacts_of_user = subscriber['contacts']
        channels_of_user = subscriber['channels']

        body = dict(
            project_id=project_id,
            service=service,
            **self._check_list_params(user_id, channels_of_user, contacts_of_user, params),
            **user)
        response = self.rpc_client.rpc_call("list_messages", body)
        return {
            "continuation": response['continuation'],
            "result": response['results']
        }

    def create(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        subscriber = SubscriberCache(user.get('project'), user.get('service'), user.get('user'),
                                     rpc_client=self.rpc_client).get_or_set()
        contacts_of_user = subscriber['contacts']
        channels_of_user = subscriber['channels']
        channel = validated['channel']

        validated_message = self._check_create_params(user_id, channels_of_user, contacts_of_user,
                                                      validated, project_id, service)
        validated_message['id'] = generate_uuid()

        body = {
            "project_id": project_id,
            "service": service,
            # validated message becomes a dict with keys
            # [id, title, body, sentTime, receiver, channel, sender]
            "validated_message": validated_message,
        }

        rpc_params = self.rpc_client.rpc_call("post_message", body, blocking=False)
        return {
            "id": rpc_params['validated_message']['id'],
            "title": rpc_params['validated_message']['title'],
            "body": rpc_params['validated_message']['body'],
            "sender": rpc_params['validated_message']['sender'],
            "receiver": validated['receiver'],
            "sentTime": rpc_params['validated_message']['sentTime'],
            "channel": channel,
            "tracking_id": rpc_params['tracking_id'],
        }

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

