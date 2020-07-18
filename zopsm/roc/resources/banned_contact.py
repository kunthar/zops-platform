from falcon import HTTPMethodNotAllowed, HTTPBadRequest
from zopsm.lib.rest.fields import ZopsAlphaNumericStringField
from zopsm.lib.rest.serializers import ZopsBaseDBSerializer
from zopsm.lib.cache.subscriber_cache import SubscriberCache

from zopsm.lib.rest.custom import ZopsRetrieveUpdateDeleteApi
from zopsm.lib.rest.custom import ZopsContinuatedListCreateApi


class BannedContactSerializer(ZopsBaseDBSerializer):
    bannedContactId = ZopsAlphaNumericStringField("Id of subscriber to ban or unban",
                                                  source='banned_contact_id')


class BannedContact(ZopsRetrieveUpdateDeleteApi):
    """
    Allows to unban a subscriber.

    ### Code Examples:
    #### DELETE:
    ##### Request:
    ```bash
    #bash
    curl \\
         --request DELETE \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/banned-contacts/fd38771e2ae2453bbd890e7b9e507f01

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.delete("https://api_baseurl/v1/roc/banned-contacts/fd38771e2ae2453bbd890e7b9e507f01",
                                headers=header)
    ```

    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "trackingId": "17665ff4-63a7-4937-b63f-59e243775e8c"
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
    serializer = BannedContactSerializer()

    def __repr__(self):
        return "Unban Subscriber"

    def __str__(self):
        return self.__repr__()

    def check_delete_request(self, user, banned_contact_id):
        subscriber = SubscriberCache(user.get('project'), user.get('service'), user.get('user'),
                                     rpc_client=self.rpc_client).get_or_set()
        banned_subs = subscriber['banned_subscribers']

        if banned_contact_id not in banned_subs:
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid parameter(s).",
                description="Subscriber is not banned.")

    def delete(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        banned_contact_id = kwargs.get('subscriber_id')

        self.check_resource_id(banned_contact_id)
        self.check_delete_request(user, banned_contact_id)

        body = {
            "project_id": project_id,
            "subscriber_id": user_id,
            "subscriber_to_unban": banned_contact_id,
            "service": service
        }

        rpc_params = self.rpc_client.rpc_call("unban_subscriber_by_subscriber", body,
                                              blocking=False)
        return {"trackingId": rpc_params['tracking_id']}

    def retrieve(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def update(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class BannedContactList(ZopsContinuatedListCreateApi):
    """
    Allows to ban a subscriber.

    ### Code Examples:
    #### POST:
    ##### Request:
    ```bash

    curl \\
         --request POST \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         --data-binary "{                                                                       \\
                \"bannedContactId\": \"8c83b4fffec34449a29131d6b6ed1216\"  \\
         }" \\
         https://api_baseurl/v1/roc/banned-contacts

    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    payload = {
        "bannedContactId": "8c83b4fffec34449a29131d6b6ed1216",
    }

    req = requests.post("https://api_baseurl/v1/roc/banned-contacts",
                                headers=header, data=json.dumps(payload))

    ```

    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "bannedContactId": "8c83b4fffec34449a29131d6b6ed1216",
            "creationTime": null,
            "isActive": null,
            "isDeleted": null,
            "lastUpdateTime": null,
            "trackingId": "d3acf02f-40bf-4e82-ae81-86f2e14f26ba"
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
    serializer = BannedContactSerializer()

    def __repr__(self):
        return "Ban Subscriber"

    def __str__(self):
        return self.__repr__()

    def check_create_request(self, user, banned_contact_id):
        subscriber = SubscriberCache(user.get('project'), user.get('service'), user.get('user'),
                                     rpc_client=self.rpc_client).get_or_set()
        banned_subs = subscriber['banned_subscribers']

        if banned_contact_id in banned_subs:
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid parameter(s).",
                description="Subscriber already banned.")

    def create(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        banned_contact_id = validated.get('banned_contact_id')

        self.check_create_request(user, banned_contact_id)

        body = {
            "project_id": project_id,
            "subscriber_id": user_id,
            "subscriber_to_ban": banned_contact_id,
            "service": service
        }
        validated.update(
            self.rpc_client.rpc_call("ban_subscriber_by_subscriber", body, blocking=False))
        return validated

    def list(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

