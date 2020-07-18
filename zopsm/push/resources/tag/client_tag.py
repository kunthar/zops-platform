from falcon import HTTPInvalidParam, HTTPMethodNotAllowed
from zopsm.lib.rest.fields import ZopsStringField, ZopsJsonObjectField
from zopsm.lib.rest.serializers import ZopsBaseDBSerializer
from zopsm.lib.rest.parameters import ZopsStringParam, ZopsAlphaNumericStringParam

from zopsm.lib.rest.custom import ZopsRetrieveUpdateDeleteApi, ZopsContinuatedListCreateApi


class ClientTagSerializer(ZopsBaseDBSerializer):
    clientId = ZopsStringField(
        "Unique identifier of the client which is desired to be tagged with given key and its value",
        source='client_id', write_only=True)
    key = ZopsStringField("Unique name of the tag in the set of tags of client")
    valueWrite = ZopsStringField(
        "Value of the tag which is specified with name `key`. It can be diversified "
        "by the type of the tag. If its type is `key`, value to write must be `null`. "
        "If its type is `key-value`, value can vary by the `valueType`. "
        "It can be a string, an integer and a float. If its type is `multi`, "
        "just as in the `key-value`, it can consist of strings, integers or "
        "floats, but mixed types are not supported. So, for instance, a tag "
        "that have `multi` as `tagType` and `str` as `valueType` can only "
        "include strings as values of itself.", write_only=True, source='value_write')

    valueRead = ZopsJsonObjectField(
        "Value of the tag which is specified with name `key`. Previously written values can be read"
        " from this field. For `tagType`s `key`, `key-value` and `multi`, `valueRead` can be an "
        "empty array, an array including only one value and an array including more than one values"
        " respectively.", read_only=True, source='value_read'
    )


class ClientTag(ZopsRetrieveUpdateDeleteApi):
    """
    Allows to retrieve and delete a specified tag with a given tag name(key).

    In order to get or delete the tag specified with a key, client must have been tagged with it
    before.

    ### Code Examples:
    #### GET:
    Retrieves the information about tag of a client with a given client id and tag name.
    ##### Request:
    ```bash
    #bash
    curl \\
         --request GET \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
         https://api_baseurl/v1/push/tags/client/ae3a086dff3c4f1fa0e861ed0630b695?tagKey=newspaper
    ```
    ```python
    # python
    import requests
    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}
    req = requests.get("https://api_baseurl/v1/push/tags/client/ae3a086dff3c4f1fa0e861ed0630b695?tagKey=newspaper",
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
            "key": "newspaper",
            "valueRead": ["Daily News", "New York Times"],
            "creationTime": "2017-08-20T08:54:56.750Z00:00",
            "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
            "isDeleted": false,
            "isActive": true
        }
    }
    ```
    #### DELETE:
    Deletes;
        - all tags of client with given id if no parameter given
        - a particular tag of client and its all values with given `tagKey` if only `tagKey`
        parameter given
        - a particular value of a particular tag with given `tagKey` and `tagValue` parameters, if
        its `tagType` is `multi`.
    ##### Request:
    ```bash
        #bash
        curl \\
             --request DELETE \\
             --header "Content-Type: application/json; charset=utf-8" \\
             --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
             https://api_baseurl/v1/push/tags/client/ae3a086dff3c4f1fa0e861ed0630b695
        #deletes all tags of user
    ```
    ```python
        # python
        import requests
        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}
        req = requests.delete("https://api_baseurl/v1/push/tags/client/ae3a086dff3c4f1fa0e861ed0630b695",
                                    headers=header)
        #deletes all tags of user
    ```
    ```bash
        #bash
        curl \\
             --request DELETE \\
             --header "Content-Type: application/json; charset=utf-8" \\
             --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
             https://api_baseurl/v1/push/tags/client/ae3a086dff3c4f1fa0e861ed0630b695?tagKey=newspaper
        #deletes newspaper tag and its values
    ```
    ```python
        # python
        import requests
        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}
        req = requests.delete("https://api_baseurl/v1/push/tags/client/ae3a086dff3c4f1fa0e861ed0630b695?tagKey=newspaper",
                                    headers=header)
        #deletes newspaper tag and its values
    ```
    ```bash
        #bash
        curl \\
             --request DELETE \\
             --header "Content-Type: application/json; charset=utf-8" \\
             --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
             https://api_baseurl/v1/push/tags/client/ae3a086dff3c4f1fa0e861ed0630b695?tagKey=newspaper&tagValue=Daily News
        #deletes Daily News of newspaper tag
    ```
    ```python
        # python
        import requests
        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}
        req = requests.delete("https://api_baseurl/v1/push/tags/client/ae3a086dff3c4f1fa0e861ed0630b695?tagKey=newspaper&tagValue=Daily News",
                                    headers=header)
        #deletes Daily News of newspaper tag
    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "trackingId": "d1b6d24f-d96b-4a26-9dc6-1e51c92572d4"
        },
        "meta": {
            "params": {
                "indent": 0,
                "tagKey": "newspaper",
                "tagValue": "Daily News"
            }
        }
    }

    ```

    > Warning
    >
    > Error response of this request, if any, will be delivered via WebSocket connection with
    > `trackingId` obtained from the response.


    ### Possible Errors
    - __Object Not Found__: Probably you try to get or delete a non-existent user or its tag.
    - __Invalid Param__: Probably it was not passed tagKey as param.
    
    """

    serializer = ClientTagSerializer()

    def __repr__(self):
        return "Client Tag Retrieve & Update & Delete"

    def __str__(self):
        return self.__repr__()

    tagKey = ZopsStringParam("Unique name of the tag in the set of tags of client. Represents the "
                             "tag that desired to operate on")

    tagValue = ZopsStringParam("Value of tag desired to delete")

    def retrieve(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project')
        service = user.get('service')

        tag_key = params.get("tagKey")
        tag_client = kwargs.get("client_id")  # who is object of the request

        if not tag_key:
            raise HTTPInvalidParam("It cannot be empty to retrieve a single tag.", "tagKey")

        body = {
            "project_id": project_id,
            "client_id": tag_client,
            "name": tag_key,
            "service": service
        }

        return self.rpc_client.rpc_call("get_push_client_tag", body)

    def update(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def delete(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project')
        service = user.get('service')

        tag_key = params.get("tagKey")
        tag_value = params.get("tagValue")
        tag_client = kwargs.get("client_id")

        body = {
            "project_id": project_id,
            "client_id": tag_client,
            "service": service
        }

        if not tag_key:
            rpc_params = self.rpc_client.rpc_call("delete_all_push_client_tags", body,
                                                  blocking=False)
        else:
            body['name'] = tag_key
            body['value'] = tag_value
            rpc_params = self.rpc_client.rpc_call("delete_push_client_tag", body, blocking=False)
        return {"trackingId": rpc_params['tracking_id']}


class ClientTagList(ZopsContinuatedListCreateApi):
    """
    Allows to add tags to client and list existing tags of client.

    ### Code Examples:
    #### GET:
    Lists all the tags of client with given `clientParam` without pagination.
    ##### Request:
    ```bash
    #bash
    curl \\
         --request GET \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
         https://api_baseurl/v1/push/tags/client?clientParam=ae3a086dff3c4f1fa0e861ed0630b695

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

    req = requests.get("https://api_baseurl/v1/push/tags/client?clientParam=ae3a086dff3c4f1fa0e861ed0630b695",
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
                "key": "android",
                "valueRead": [],
                "creationTime": "2017-08-20T08:54:56.750Z00:00",
                "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                "isDeleted": false,
                "isActive": true
            },
            {
                "key": "eye-color",
                "valueRead": ["blue"],
                "creationTime": "2017-08-20T08:54:56.750Z00:00",
                "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                "isDeleted": false,
                "isActive": true
            },
            {
                "key": "newspaper",
                "valueRead": ["Daily News", "New York Times"],
                "creationTime": "2017-08-20T08:54:56.750Z00:00",
                "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                "isDeleted": false,
                "isActive": true
            }
        ]
    }
    ```

    #### POST:
    Adds a tag to the client.

    > Warning
    >
    > Tags must be created before adding to the user.

    ##### Request:
    ```bash

    curl \\
         --request POST \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
         --data-binary "{\"clientId\": \"ae3a086dff3c4f1fa0e861ed0630b695\", \\
                        \"key\": \"newspaper\", \\
                        \"valueWrite\": \"Sabah\"}" \\
         https://api_baseurl/v1/push/tags/client
    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

    payload = {"clientId": "ae3a086dff3c4f1fa0e861ed0630b695",
               "key": "newspaper",
               "valueWrite": "Sabah"}

    req = requests.post("https://api_baseurl/v1/push/tags/client",
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
            "key": "newspaper",
            "lastUpdateTime": null,
            "trackingId": "807fbb48-e044-469b-99c8-980c407cd2e5",
            "valueRead": null
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
    - __Invalid Param__: Probably it was not passed tagKey as param.

    """

    serializer = ClientTagSerializer()

    def __repr__(self):
        return "Client Tag Add & List"

    def __str__(self):
        return self.__repr__()

    clientParam = ZopsAlphaNumericStringParam("client id for whom the tags will be listed")

    def _list(self, params, meta, **kwargs):
        return [
            self.serializer.to_representation(obj)
            for obj in self.list(params, meta, **kwargs)
            ]

    def list(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project')
        service = user.get('service')

        client_param = params.get("clientParam")

        if not client_param:
            raise HTTPInvalidParam("It cannot be empty to get a list of tags.", "clientParam")

        body = {
            "project_id": project_id,
            "client_id": client_param,
            "service": service
        }

        return self.rpc_client.rpc_call("get_list_push_client_tags", body)

    def create(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project')
        service = user.get('service')

        body = dict(
            project_id=project_id,
            client_id=validated.get('client_id'),
            name=validated.get('key'),
            value=validated.get('value_write'),
            service=service
        )

        rpc_params = self.rpc_client.rpc_call("add_push_client_tag", body, blocking=False)
        return {
            "key": rpc_params['name'],
            "tracking_id": rpc_params['tracking_id'],
        }

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

