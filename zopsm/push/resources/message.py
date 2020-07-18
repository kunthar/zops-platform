from falcon import HTTPMethodNotAllowed, HTTPBadRequest
from zopsm.lib.rest.fields import ZopsStringField, ZopsDatetimeField, ZopsAlphaNumericStringField, \
    ZopsListOfStringsField, ZopsJsonObjectField
from zopsm.lib.rest.serializers import ZopsBaseDBSerializer

from zopsm.lib.rest.custom import ZopsRetrieveUpdateDeleteApi, \
    ZopsContinuatedListCreateApi
from zopsm.lib.rest.parameters import ZopsStringParam, ZopsIntegerParam
from zopsm.lib.utility import generate_uuid
from zopsm.push.validators import list_of_consumer_validator


class MessageSerializer(ZopsBaseDBSerializer):
    messageId = ZopsAlphaNumericStringField("Unique identifier of the push message", read_only=True, source='id')
    sender = ZopsAlphaNumericStringField("Sender of the message", read_only=True, source="target_id")
    title = ZopsStringField("Title of the push message. Optional.")
    body = ZopsStringField("Body of the push message.")
    type = ZopsAlphaNumericStringField(
        "Type of the push message. It can be automated, scheduled, ordinary")
    language = ZopsStringField("Language")
    icon = ZopsStringField("Icon url")
    image = ZopsStringField("Image url")
    badge = ZopsStringField("Badge of your app icon.")
    consumers = ZopsListOfStringsField("List of consumers", validators=[list_of_consumer_validator])
    audience = ZopsAlphaNumericStringField(
        "Id of a previously created segment to send push message")
    #todo: if message type ordinary scheduletime must be null
    scheduleTime = ZopsDatetimeField(
        "Time of message will be pushed if message type is scheduled, else it must be null.",
        source="schedule_time")
    extra = ZopsJsonObjectField("Extra data for Apple Devices")


class Message(ZopsRetrieveUpdateDeleteApi):
    """
    Allows to retrieve, update and delete push messages.

    ### Code Examples:
    #### GET:
    Retrieves the message with given id.
    ##### Request:
    ```bash
        #bash
        curl \\
             --request GET \\
             --header "Content-Type: application/json; charset=utf-8" \\
             --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
             https://api_baseurl/v1/push/messages/a1c89b20aede4eda8438d84cc9bd5056

    ```

    ```python
        # python
        import requests

        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

        req = requests.get("https://api_baseurl/v1/push/messages/a1c89b20aede4eda8438d84cc9bd5056",
                                    headers=header)

    ```
    ##### Response:
    200 OK.
    ```json
        {
            "meta": {
                "params": {
                    "indent": 0
                }
            },
            "content": {
                "id": "a1c89b20aede4eda8438d84cc9bd5056",
                "creationTime": "2017-08-20T08:54:56.750Z00:00",
                "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                "isDeleted": false,
                "isActive": true,
                "sender": "002b139c705d4db7802e42416ec16ea9",
                "title": "Hi",
                "body": "Hello World",
                "type": "ordinary",
                "language": "English",
                "icon": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
                "image": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
                "badge": "null",
                "consumers": [],
                "audience": "6483ff9c6c064e1c982a976904447875",
                "scheduleTime": "null",
                "extra": "null"
            }
        }
    ```
    OR
    ```json
        {
            "meta": {
                "params": {
                    "indent": 0
                }
            },
            "content": {
                "id": "a1c89b20aede4eda8438d84cc9bd5056",
                "creationTime": "2017-08-20T08:54:56.750Z00:00",
                "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                "isDeleted": false,
                "isActive": true,
                "sender": "002b139c705d4db7802e42416ec16ea9",
                "title": "Hi",
                "body": "Hello World",
                "type": "scheduled",
                "language": "English",
                "icon": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
                "image": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
                "badge": "null",
                "consumers": [],
                "audience": "6483ff9c6c064e1c982a976904447875",
                "scheduleTime": "2017-08-20T08:54:56.750Z00:00",
                "extra": "null"
            }
        }
    ```

    #### PUT:
    Updates a message if message type is not `ordinary`. `ordinary` messages can not be updated in
    that it processed immediately.

    ##### Request:
    ```bash

    curl \\
         --request PUT \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
         --data-binary "{                                                                   \\
                \"title\": \"Hi\",                                                          \\
                \"body\": \"Hello World\",                                                  \\
                \"type\": \"scheduled\",                                                    \\
                \"language\": \"English\",                                                  \\
                \"icon\": \"https://avatars0.githubusercontent.com/u/10046644?s=200&v=4\",  \\
                \"image\": \"https://avatars0.githubusercontent.com/u/10046644?s=200&v=4\", \\
                \"badge\": \"null\",                                                        \\
                \"consumers\": \"[]\",                                                      \\
                \"audience\": \"6483ff9c6c064e1c982a976904447875\",                         \\
                \"scheduleTime\": \"2017-08-20T08:54:56.750Z00:00\",                        \\
                \"extra\": \"null\"                                                         \\
            }" \\
         https://api_baseurl/v1/push/messages/a1c89b20aede4eda8438d84cc9bd5056
    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

    payload = {
        "title": "Hi",
        "body": "Hello World",
        "type": "scheduled",
        "language": "English",
        "icon": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
        "image": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
        "badge": None,
        "consumers": [],
        "audience": "6483ff9c6c064e1c982a976904447875",
        "scheduleTime": "2017-08-20T08:54:56.750Z00:00",
        "extra": "null"
    }

    req = requests.put("https://api_baseurl/v1/push/messages/a1c89b20aede4eda8438d84cc9bd5056",
                                headers=header, data=json.dumps(payload))

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "audience": "6483ff9c6c064e1c982a976904447875",
            "badge": null,
            "body": "Hello World",
            "creationTime": null,
            "icon": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
            "image": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
            "isActive": null,
            "isDeleted": null,
            "language": "English",
            "lastUpdateTime": null,
            "messageId": "a1c89b20aede4eda8438d84cc9bd5056",
            "scheduleTime": "2017-08-20T08:54:56.750Z00:00",
            "sender": "6c47f245954b4252ab3d098e4eecf637",
            "title": "Hi",
            "trackingId": "80696627-a76c-4b9e-b879-ba77e7e791ce",
            "type": "scheduled",
            "extra": "null"
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
             --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
             https://api_baseurl/v1/push/messages/a1c89b20aede4eda8438d84cc9bd5056

    ```

    ```python
        # python
        import requests

        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

        req = requests.delete("https://api_baseurl/v1/push/messages/a1c89b20aede4eda8438d84cc9bd5056",
                                    headers=header)

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "trackingId": "3ed021a5-f7bc-446e-9d47-bb3c540c746f"
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
    - __Object Not Found__: Probably you try to get or delete a non-existent resource.

    """

    serializer = MessageSerializer()

    def __repr__(self):
        return "Message Retrieve & Update & Delete"

    def __str__(self):
        return self.__repr__()

    def retrieve(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        msg_id = kwargs.get('message_id')

        self.check_resource_id(msg_id)

        body = {
            "message_id": msg_id,
            "target_id": user_id,
            "project_id": project_id,
            "service": service
        }

        return self.rpc_client.rpc_call("get_push_message", body)

    def update(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        validated = kwargs.get("validated")
        msg_id = kwargs.get('message_id')
        if validated['audience'] and validated['consumers']:
            raise HTTPBadRequest(description="Audience and consumers field can not be filled at the same time")
        elif not validated['audience'] and not validated['consumers']:
            raise HTTPBadRequest(description="Audience or consumers field must be filled")
        self.check_resource_id(msg_id)
        body = {
            "project_id": project_id,
            "message_id": msg_id,
            "validated_message": validated,
            "target_id": user_id,
            "service": service
        }

        rpc_params = self.rpc_client.rpc_call("update_push_message", body, blocking=False)
        return {
            "id": msg_id,
            "target_id": rpc_params['target_id'],
            "tracking_id": rpc_params['tracking_id'],
            "title": rpc_params['validated_message']['title'],
            "body": rpc_params['validated_message']['body'],
            "type": rpc_params['validated_message']['type'],
            "language": rpc_params['validated_message']['language'],
            "icon": rpc_params['validated_message']['icon'],
            "image": rpc_params['validated_message']['image'],
            "badge": rpc_params['validated_message']['badge'],
            "consumers": rpc_params['validated_message']['consumers'],
            "audience": rpc_params['validated_message']['audience'],
            "schedule_time": rpc_params['validated_message']['schedule_time'],
            "extra": rpc_params['validated_message']['extra'],
        }

    def delete(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        msg_id = kwargs.get('message_id')
        self.check_resource_id(msg_id)
        body = {
            "message_id": msg_id,
            "target_id": user_id,
            "project_id": project_id,
            "service": service
        }
        rpc_params = self.rpc_client.rpc_call("delete_push_message", body, blocking=False)
        return {"trackingId": rpc_params['tracking_id']}


class MessageList(ZopsContinuatedListCreateApi):
    """
    Allows to Post and List push messages.

    ### Code Examples:
    #### GET:
    Lists the push messages by the pageSize and continuation params.
    ##### Request:
    ```bash
        #bash
        curl \\
             --request GET \\
             --header "Content-Type: application/json; charset=utf-8" \\
             --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
             https://api_baseurl/v1/push/messages?page_size=2

    ```

    ```python
        # python
        import requests

        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

        req = requests.get("https://api_baseurl/v1/push/messages?page_size=2",
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
                        "id": "a1c89b20aede4eda8438d84cc9bd5056",
                        "creationTime": "2017-08-20T08:54:56.750Z00:00",
                        "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                        "isDeleted": false,
                        "isActive": true,
                        "sender": "002b139c705d4db7802e42416ec16ea9",
                        "title": "Hi",
                        "body": "Hello World",
                        "type": "ordinary",
                        "language": "English",
                        "icon": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
                        "image": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
                        "badge": "null",
                        "consumers": [],
                        "audience": "6483ff9c6c064e1c982a976904447875",
                        "scheduleTime": "null",
                        "extra": "null"
                    },
                    {
                        "id": "83cb4810fd5049c4bc15ca82f00b6965",
                        "creationTime": "2017-08-20T08:54:56.750Z00:00",
                        "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                        "isDeleted": false,
                        "isActive": true,
                        "sender": "002b139c705d4db7802e42416ec16ea9",
                        "title": "Hi",
                        "body": "Hello World",
                        "type": "scheduled",
                        "language": "English",
                        "icon": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
                        "image": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
                        "badge": "null",
                        "consumers": [123hk234y23234],
                        "audience": null,
                        "scheduleTime": "2017-08-20T08:54:56.750Z00:00",
                        "extra": "null"
                    }
                ],
                "continuation": "1cd6c8c224aa40f4b6f66ed0c69d370b"
            }
        }
    ```
    > Warning
    >
    > The next page can be obtained via requesting to
    > `https://api_baseurl/v1/push/messages?page_size=2&continuation=1cd6c8c224aa40f4b6f66ed0c69d370b`

    #### POST:
    Creates a new message post it to audience(consumers field must be empty list) according to its type whether
    immediately or at scheduleTime.
    Create a new message post it to consumer list(audience field must be null) according to its type whether immediately
    or scheduleTime
    ##### Request:
    ```bash

        curl \\
             --request POST \\
             --header "Content-Type: application/json; charset=utf-8" \\
             --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
             --data-binary "{                                                                       \\
                        \"title\": \"Hi\",                                                          \\
                        \"body\": \"Hello World\",                                                  \\
                        \"type\": \"ordinary\",                                                     \\
                        \"language\": \"English\",                                                  \\
                        \"icon\": \"https://avatars0.githubusercontent.com/u/10046644?s=200&v=4\",  \\
                        \"image\": \"https://avatars0.githubusercontent.com/u/10046644?s=200&v=4\", \\
                        \"badge\": \"null\",                                                        \\
                        \"audience\": \"6483ff9c6c064e1c982a976904447875\",                         \\
                        \"scheduleTime\": \"null\",                                                 \\
                        \"extra\": \"null\"                                                         \\

             }" \\
             https://api_baseurl/v1/push/messages

    ```


    ```python
        import requests
        import json

        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

        payload = {
            "title": "Hi",
            "body": "Hello World",
            "type": "scheduled",
            "language": "English",
            "icon": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
            "image": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
            "badge": None,
            "audience": "6483ff9c6c064e1c982a976904447875",
            "scheduleTime": "2017-08-20T08:54:56.750Z00:00",
            "extra": "null"
        }

        req = requests.post("https://api_baseurl/v1/push/messages",
                                    headers=header, data=json.dumps(payload))

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "audience": "6483ff9c6c064e1c982a976904447875",
            "badge": "null",
            "body": "Hello World",
            "creationTime": null,
            "icon": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
            "image": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
            "isActive": null,
            "isDeleted": null,
            "language": "English",
            "lastUpdateTime": null,
            "messageId": "2587d91a9d584fae9e38dbf92933639b",
            "scheduleTime": "2017-08-20T08:54:56.750Z00:00",
            "sender": "8cb5963a1e0f4cbdbe9a300b2657d3f8",
            "title": "Hi",
            "trackingId": "73cd70a9-21df-4e91-bbbf-ba59d17deb4d",
            "type": "scheduled",
            "extra": "null"
        },
        "meta": {
            "params": {
                "indent": 0,
                "page_size": 10
            }
        }
    }

    ```bash

        curl \\
             --request POST \\
             --header "Content-Type: application/json; charset=utf-8" \\
             --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
             --data-binary "{                                                                       \\
                        \"title\": \"Hi\",                                                          \\
                        \"body\": \"Hello World\",                                                  \\
                        \"type\": \"ordinary\",                                                     \\
                        \"language\": \"English\",                                                  \\
                        \"icon\": \"https://avatars0.githubusercontent.com/u/10046644?s=200&v=4\",  \\
                        \"image\": \"https://avatars0.githubusercontent.com/u/10046644?s=200&v=4\", \\
                        \"badge\": \"null\",                                                        \\
                        \"consumers": \"[\"sdfhk23jh42lk34h"\, \"sjhfsdkfjhsdkf\"]\",               \\
                        \"audience\": \"null\",                                                     \\
                        \"scheduleTime\": \"null\"                                                  \\
                        \"extra\": \"null\"                                                         \\

             }" \\
             https://api_baseurl/v1/push/messages

    ```


    ```python
        import requests
        import json

        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

        payload = {
            "title": "Hi",
            "body": "Hello World",
            "type": "scheduled",
            "language": "English",
            "icon": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
            "image": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
            "badge": None,
            "consumer": ["sdfhk23jh42lk34h", "sakjhdaksjdhk21321"],
            "audience": null,
            "scheduleTime": "2017-08-20T08:54:56.750Z00:00",
            "extra": "null"
        }

        req = requests.post("https://api_baseurl/v1/push/messages",
                                    headers=header, data=json.dumps(payload))

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "consumer": ["sdfhk23jh42lk34h", "sakjhdaksjdhk21321"],
            "audience": null,
            "badge": "null",
            "body": "Hello World",
            "creationTime": null,
            "icon": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
            "image": "https://avatars0.githubusercontent.com/u/10046644?s=200&v=4",
            "isActive": null,
            "isDeleted": null,
            "language": "English",
            "lastUpdateTime": null,
            "messageId": "2587d91a9d584fae9e38dbf92933639b",
            "scheduleTime": "2017-08-20T08:54:56.750Z00:00",
            "sender": "8cb5963a1e0f4cbdbe9a300b2657d3f8",
            "title": "Hi",
            "trackingId": "73cd70a9-21df-4e91-bbbf-ba59d17deb4d",
            "type": "scheduled",
            "extra": "null"
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

    page_size = ZopsIntegerParam(
        details="Specifies number of result entries in single response",
        default='10'
    )

    continuation = ZopsStringParam(
        details="Key for retrieval of the next page if exists. It can only be obtained at the "
                "response of a list call."
    )

    def __repr__(self):
        return "Message Post & List"

    def __str__(self):
        return self.__repr__()

    def list(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get("user")
        project_id = user.get('project')
        service = user.get('service')
        page_size = params.get("page_size")
        continuation = params.get('continuation', None)
        body = {
            "target_id": user_id,
            "project_id": project_id,
            "page_size": page_size,
            "service": service
        }
        if continuation:
            body['continuation'] = continuation

        response = self.rpc_client.rpc_call("list_push_messages", body)
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
        message_id = generate_uuid()
        if not validated['audience'] and not validated['consumers']:
            raise HTTPBadRequest(description="Audience or consumers field must be filled")
        elif validated['audience'] and validated['consumers']:
            raise HTTPBadRequest(description="Audience and consumers field can not be filled at the same time")

        body = dict(
            target_id=user_id,
            validated_message=validated,
            project_id=project_id,
            service=service,
            message_id=message_id
        )

        rpc_params = self.rpc_client.rpc_call("post_push_message", body, blocking=False)
        return {
            "id": message_id,
            "target_id": rpc_params['target_id'],
            "tracking_id": rpc_params['tracking_id'],
            "title": rpc_params['validated_message']['title'],
            "body": rpc_params['validated_message']['body'],
            "type": rpc_params['validated_message']['type'],
            "language": rpc_params['validated_message']['language'],
            "icon": rpc_params['validated_message']['icon'],
            "image": rpc_params['validated_message']['image'],
            "badge": rpc_params['validated_message']['badge'],
            "audience": rpc_params['validated_message']['audience'],
            "schedule_time": rpc_params['validated_message']['schedule_time'],
            "extra": rpc_params['validated_message']['extra'],
            "consumers": rpc_params['validated_message']['consumers']
        }

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

