from falcon import HTTPMethodNotAllowed
from zopsm.lib.rest.custom import ZopsContinuatedListCreateApi
from zopsm.lib.rest.serializers import ZopsBaseDBSerializer
from zopsm.lib.rest.fields import ZopsAlphaNumericStringField


class AcknowledgementSerializer(ZopsBaseDBSerializer):
    clientId = ZopsAlphaNumericStringField(
        "Unique identifier of the client which sends the acknowledgement", source="client_id")
    messageId = ZopsAlphaNumericStringField(
        "Unique identifier of the push message which acknowledgement sends for",
        source="message_id")


class Acknowledgement(ZopsContinuatedListCreateApi):
    """
    Clients use to notify provider about that it received the message.

    #### POST:
    ##### Request:
    ```bash

    curl \\
         --request POST \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
         --data-binary "{                                                                       \\
                \"clientId\": \"6d6d5b975d104eb198009596f3f59453\",                             \\
                \"messageId\": \"a1c89b20aede4eda8438d84cc9bd5056\"                             \\
         }" \\
         https://api_baseurl/v1/push/acknowledgements

    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

    payload = {
        "clientId": "6d6d5b975d104eb198009596f3f59453",
        "messageId": "a1c89b20aede4eda8438d84cc9bd5056"
    }

    req = requests.post("https://api_baseurl/v1/push/acknowledgements",
                                headers=header, data=json.dumps(payload))

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "clientId": "6d6d5b975d104eb198009596f3f59453",
            "creationTime": null,
            "isActive": null,
            "isDeleted": null,
            "lastUpdateTime": null,
            "messageId": "a1c89b20aede4eda8438d84cc9bd5056",
            "trackingId": "f056c58f-1373-4ecd-a0e3-37f9ecba05ee"
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

    serializer = AcknowledgementSerializer()

    def __repr__(self):
        return "Acknowledgement Create"

    def __str__(self):
        return self.__repr__()

    def create(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        body = dict(target_id=user_id, **validated, project_id=project_id, service=service)
        return self.rpc_client.rpc_call("post_push_acknowledgement", body, blocking=False)

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def list(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


