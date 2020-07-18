from falcon import HTTPMethodNotAllowed
from zopsm.lib.rest.fields import ZopsStringField
from zopsm.lib.rest.serializers import ZopsBaseDBSerializer
from zopsm.push.validators import device_type_validator
from zopsm.lib.utility import generate_uuid
from zopsm.lib.rest.custom import ZopsRetrieveUpdateDeleteApi, ZopsContinuatedListCreateApi


class ClientSerializer(ZopsBaseDBSerializer):
    clientId = ZopsStringField("Unique identifier of a client", source='id', read_only=True)
    token = ZopsStringField(
        "Token obtained from client's notification service such as APNs, FCM etc.", write_only=True)
    appVersion = ZopsStringField("Version of client application", source='app_version')
    deviceType = ZopsStringField("Device type of client(android or ios for now).",
                                 source='device_type', validators=[device_type_validator])
    language = ZopsStringField("Language of client")
    country = ZopsStringField("Country")
    osVersion = ZopsStringField("Operating System Version", source='os_version')


class Client(ZopsRetrieveUpdateDeleteApi):
    """
    Allows retrive, update and delete clients. Each client application must
    register itself to the push notification server of its own platform and obtain a token after
    registration or whenever token changes.

    Client application is responsible for sending this token to provider when it is obtained.
    On each delivery of the token, the client must pass some information to make itself
    classifiable by giving some information to provider about itself.

    ### Code Examples:
    #### GET:
    Retrieves the client with given id.
    ##### Request:
    ```bash
    #bash
    curl \\
         --request GET \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
         https://api_baseurl/v1/push/clients/6d6d5b975d104eb198009596f3f59453

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

    req = requests.get("https://api_baseurl/v1/push/clients/6d6d5b975d104eb198009596f3f59453",
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
            "clientId": "6d6d5b975d104eb198009596f3f59453",
            "token": "1cef7469f72d445dad43f3c275e4323f",
            "appVersion": "1.0.0",
            "deviceType": "android",
            "language": "English",
            "country": "Turkey",
            "osVersion": "4.4.2",
            "creationTime": "2017-08-20T08:54:56.750Z00:00",
            "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
            "isDeleted": false,
            "isActive": true,
        }
    }
    ```

    #### PUT:
    Updates a client with given id.

    ##### Request:
    ```bash

    curl \\
         --request PUT \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
         --data-binary "{                                                                   \\
                \"token\": \"1cef7469f72d445dad43f3c275e4323f\",                            \\
                \"appVersion\": \"1.0.0\",                                                  \\
                \"deviceType\": \"android\",                                                \\
                \"language\": \"English\",                                                  \\
                \"country\": \"Turkey\",                                                    \\
                \"osVersion\": \"4.4.2\"                                                    \\
            }" \\
         https://api_baseurl/v1/push/clients/6d6d5b975d104eb198009596f3f59453
    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

    payload = {
        "token": "1cef7469f72d445dad43f3c275e4323f",
        "appVersion": "1.0.0",
        "deviceType": "android",
        "language": "English",
        "country": "Turkey",
        "osVersion": "4.4.2"
    }

    req = requests.put("https://api_baseurl/v1/push/clients/6d6d5b975d104eb198009596f3f59453",
                                headers=header, data=json.dumps(payload))

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "appVersion": "1.0.0",
            "clientId": "6d6d5b975d104eb198009596f3f59453",
            "country": "Turkey",
            "creationTime": null,
            "deviceType": "android",
            "isActive": null,
            "isDeleted": null,
            "language": "English",
            "lastUpdateTime": null,
            "osVersion": "4.4.2",
            "trackingId": "b56d09ad-b48f-4661-8693-769a813b7e43"
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
    Deletes the client with given id.
    ##### Request:
    ```bash
    #bash
    curl \\
         --request DELETE \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
         https://api_baseurl/v1/push/clients/6d6d5b975d104eb198009596f3f59453

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

    req = requests.delete("https://api_baseurl/v1/push/clients/6d6d5b975d104eb198009596f3f59453",
                                headers=header)

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "trackingId": "a8990c86-be58-4f79-9c9b-c71ff27353c4"
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

    """

    serializer = ClientSerializer()

    def __repr__(self):
        return "Client Retrieve & Update & Delete"

    def __str__(self):
        return self.__repr__()

    def retrieve(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        client_id = kwargs.get('client_id')
        body = {
            "client_id": client_id,
            "target_id": user_id,
            "project_id": project_id,
            "service": service
        }
        return self.rpc_client.rpc_call("get_client", body)

    def update(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        validated = kwargs.get('validated')
        client_id = kwargs.get('client_id')
        body = {
            "client_id": client_id,
            "target_id": user_id,
            "validated_client": validated,
            "project_id": project_id,
            "service": service
        }

        rpc_params = self.rpc_client.rpc_call("update_client", body, blocking=False)
        return {
            "id": rpc_params['client_id'],
            "tracking_id": rpc_params['tracking_id'],
            "app_version": rpc_params['validated_client']['app_version'],
            "device_type": rpc_params['validated_client']['device_type'],
            "language": rpc_params['validated_client']['language'],
            "country": rpc_params['validated_client']['country'],
            "os_version": rpc_params['validated_client']['os_version'],
        }

    def delete(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        client_id = kwargs.get('client_id')
        self.check_resource_id(client_id)
        body = {
            "client_id": client_id,
            "target_id": user_id,
            "project_id": project_id,
            "service": service
        }
        rpc_params = self.rpc_client.rpc_call("delete_client", body, blocking=False)
        return {"trackingId": rpc_params['tracking_id']}


class ClientList(ZopsContinuatedListCreateApi):
    """
    Allows to list and create clients by user.

    ### Code Examples:
    #### GET:
    Lists the clients by user.
    ##### Request:
    ```bash
    #bash
    curl \\
         --request GET \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
         https://api_baseurl/v1/push/clients
    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

    req = requests.get("https://api_baseurl/v1/push/clients",
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
        "content": [
            {
                "clientId": "6d6d5b975d104eb198009596f3f59453",
                "token": "1cef7469f72d445dad43f3c275e4323f",
                "appVersion": "1.0.0",
                "deviceType": "android",
                "language": "English",
                "country": "Turkey",
                "osVersion": "4.4.2",
                "creationTime": "2017-08-20T08:54:56.750Z00:00",
                "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                "isDeleted": false,
                "isActive": true,
            }
        ]
    }
    ```

    #### POST:
    Register a new client.

    ##### Request:
    ```bash

    curl \\
         --request POST \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
         --data-binary "{                                                                   \\
                \"token\": \"1cef7469f72d445dad43f3c275e4323f\",                            \\
                \"appVersion\": \"1.0.0\",                                                  \\
                \"deviceType\": \"android\",                                                \\
                \"language\": \"English\",                                                  \\
                \"country\": \"Turkey\",                                                    \\
                \"osVersion\": \"4.4.2\"                                                    \\

         }" \\
         https://api_baseurl/v1/push/clients

    ```


    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

    payload = {
        "token": "1cef7469f72d445dad43f3c275e4323f",
        "appVersion": "1.0.0",
        "deviceType": "android",
        "language": "English",
        "country": "Turkey",
        "osVersion": "4.4.2"
    }

    req = requests.post("https://api_baseurl/v1/push/clients",
                                headers=header, data=json.dumps(payload))

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "appVersion": "1.0.0",
            "clientId": "4fcb4b8ddd4845e1b4518991893300be",
            "country": "Turkey",
            "creationTime": null,
            "deviceType": "android",
            "isActive": null,
            "isDeleted": null,
            "language": "English",
            "lastUpdateTime": null,
            "osVersion": "4.4.2",
            "trackingId": "57b057b9-abc7-4864-9454-a2cf8735c088"
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

    serializer = ClientSerializer()

    def __repr__(self):
        return "Client Create & List"

    def __str__(self):
        return self.__repr__()

    def _list(self, params, meta, **kwargs):
        return [
                self.serializer.to_representation(obj)
                for obj in self.list(params, meta, **kwargs)
            ]

    def list(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get("user")
        project_id = user.get('project')
        service = user.get('service')
        body = {
            "target_id": user_id,
            "project_id": project_id,
            "service": service
        }
        return self.rpc_client.rpc_call("list_clients", body)

    def create(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        validated = kwargs.get('validated')
        client_id = generate_uuid()
        body = {
            "target_id": user_id,
            "validated_client": validated,
            "project_id": project_id,
            "service": service,
            "client_id": client_id
        }
        rpc_params = self.rpc_client.rpc_call("create_client", body, blocking=False)

        return {
            "id": client_id,
            "tracking_id": rpc_params['tracking_id'],
            "app_version": rpc_params['validated_client']['app_version'],
            "device_type": rpc_params['validated_client']['device_type'],
            "language": rpc_params['validated_client']['language'],
            "country": rpc_params['validated_client']['country'],
            "os_version": rpc_params['validated_client']['os_version'],
        }

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

