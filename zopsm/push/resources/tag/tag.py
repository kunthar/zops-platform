from falcon import HTTPConflict, HTTPMethodNotAllowed
from zopsm.lib.rest.fields import ZopsStringField, ZopsAlphaNumericStringField
from zopsm.lib.rest.serializers import ZopsBaseDBSerializer
from zopsm.lib.rest.parameters import ZopsStringParam, ZopsIntegerParam
from zopsm.lib.rest.custom import ZopsRetrieveUpdateDeleteApi, ZopsContinuatedListCreateApi
from zopsm.push.validators import tag_type_validator, tag_value_type_validator


class TagSerializer(ZopsBaseDBSerializer):
    name = ZopsAlphaNumericStringField("Alphanumeric key of tag")
    tagType = ZopsStringField("Type of tag indicating the tag is in type key, key-value or multi",
                              validators=[tag_type_validator], source="tag_type")
    valueType = ZopsStringField("Type of value of tag which can be int, str or float",
                                validators=[tag_value_type_validator], source="value_type")


class Tag(ZopsRetrieveUpdateDeleteApi):
    """
    Tag can be considered as a label for targets and clients.

    In order to compartmentalize the recipients of a push message, each candidate recipient must be
    tagged with a certain key. This key can have a value, multiple values or not. These can be
    categorized under the `tagType` field as:

    __key__: it represents the tags that do not have values. Basically, these are the groups that
    have members. If you add this type of tag to a target or a client, it means that target or
    client who is intended to be tagged with this type of tag will be a member of a set which the
    ones that have this tag.
    ```json
        {
            "name": "male",
            "tagType": "key",
            "valueType": null
        }
    ```
    __key-value__: it represents the tags that do have a single value.
    ```json
        {
            "name": "eye-color",
            "tagType": "key-value",
            "valueType": "str"
        }
    ```
    __multi__: it represents the tags that do have more than one value.
    ```json
        {
            "name": "newspaper",
            "tagType": "multi",
            "valueType": "str"
        }
    ```

    Values of tags can be in three forms: `int`, `str`, and `float`. The only specification about
    `valueType` is that float type values must be in form of `%.2f`. It means that there can only be
     two digits after the point.

    > Warning
    >
    > If `valueType` of a tag is `float`, it must be in form of `%.2f`. It means that there can only
    > be two digits after the point.

    ### Code Examples:
    #### GET:
    Retrieves the information about tag with given id.
    ##### Request:
    ```bash
        #bash
        curl \\
             --request GET \\
             --header "Content-Type: application/json; charset=utf-8" \\
             --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
             https://api_baseurl/v1/push/tags/newspaper

    ```

    ```python
        # python
        import requests

        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

        req = requests.get("https://api_baseurl/v1/push/tags/newspaper",
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
                "name": "newspaper",
                "tagType": "multi",
                "valueType": "str",
                "creationTime": "2017-08-20T08:54:56.750Z00:00",
                "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                "isDeleted": false
            }
        }
    ```
    #### DELETE:
    Deletes the tag with given id if there is no segments including it.
    ##### Request:
    ```bash
        #bash
        curl \\
             --request DELETE \\
             --header "Content-Type: application/json; charset=utf-8" \\
             --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
             https://api_baseurl/v1/push/tags/newspaper

    ```

    ```python
        # python
        import requests

        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

        req = requests.delete("https://api_baseurl/v1/push/tags/newspaper",
                                    headers=header)

    ```
    ##### Response:

    202 Accepted.
    ```json
    {
        "content": {
            "trackingId": "edb6a2e4-a6a1-4dd8-af5c-d69999f84754"
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

    409 Conflict.
    ```json
        {
            "title": "Conflict",
            "description": "It is not allowed to delete the tag TAG_NAME, while following segments are including it:[LIST_OF_SEGMENTS]."
        }
    ```


    ### Possible Errors
    - __Object Not Found__: Probably you try to get or delete a non-existent tag.
    - __Conflict__: Probably you try to delete a tag which is included in a segment or segments.


    """

    serializer = TagSerializer()

    def __repr__(self):
        return "Tag Retrieve & Delete"

    def __str__(self):
        return self.__repr__()

    def retrieve(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project')
        service = user.get('service')

        tag_key = kwargs.get("tag_key")

        self.check_resource_id(tag_key)

        body = {
            "project_id": project_id,
            "tag_name": tag_key,
            "service": service
        }

        return self.rpc_client.rpc_call("get_push_tag", body)

    def delete(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project')
        service = user.get('service')

        tag_key = kwargs.get("tag_key")

        self.check_resource_id(tag_key)

        body = {
            "project_id": project_id,
            "tag_name": tag_key,
            "service": service
        }

        response = self.rpc_client.rpc_call("check_tag_deletion_suitability", body)

        if not response['suitable']:
            raise HTTPConflict(
                title="Conflict",
                description="It is not allowed to delete the tag {}, while following segments are "
                            "including it:{}.".format(tag_key, response['results']))
        rpc_params = self.rpc_client.rpc_call("delete_push_tag", body, blocking=False)
        return {"trackingId": rpc_params['tracking_id']}

    def update(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class TagList(ZopsContinuatedListCreateApi):
    """
    TagList resource supports retrieval of list of tags and creating a new tag.

    __Listing all push tags__:

    Listing all push tags performed by paginating by a given `page_size` and `continuation`
    parameters with the request.

    `page_size` indicates the number of tags will be given as response of a single request. It is an
    integer and 0 by default.

    `continuation` is a string that will be given in the body of the response of the initial request
    to obtain the list. So, the result size of the first response will exactly be as many as
    `page_size`. In order to retrieve the next page with given `page_size`, the request must include
    `continuation` which is already sent in previous response as a parameter. There is no default
    value for continuation. If it is not specified explicitly in the request, it will always give
    the first page.

    ### Code Examples:
    #### GET:
    Lists the tags by the pageSize and continuation params.
    ##### Request:
    ```bash
        #bash
        curl \\
             --request GET \\
             --header "Content-Type: application/json; charset=utf-8" \\
             --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
             https://api_baseurl/v1/push/tags?page_size=2

    ```

    ```python
        # python
        import requests

        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

        req = requests.get("https://api_baseurl/v1/push/tags?page_size=2",
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
                        "name": "newspaper",
                        "tagType": "multi",
                        "valueType": "str",
                        "creationTime": "2017-08-20T08:54:56.750Z00:00",
                        "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                        "isDeleted": false
                    },
                    {
                        "name": "color",
                        "tagType": "key-value",
                        "valueType": "str",
                        "creationTime": "2017-08-20T08:54:56.750Z00:00",
                        "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                        "isDeleted": false
                    }
                ],
                "continuation": "1cd6c8c224aa40f4b6f66ed0c69d370b"
            }
        }
    ```
    > Warning
    >
    > The next page can be obtained via requesting to
    > `https://api_baseurl/v1/push/tags?page_size=2&continuation=1cd6c8c224aa40f4b6f66ed0c69d370b`

    #### POST:
    Creates a new tag with given body.
    ##### Request:
    ```bash

        curl \\
             --request POST \\
             --header "Content-Type: application/json; charset=utf-8" \\
             --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
             --data-binary "{\"name\": \"newspaper\", \\
                            \"tagType\": \"multi\", \\
                            \"valueType\": \"str\"}" \\
             https://api_baseurl/v1/push/tags

    ```


    ```python
        import requests
        import json

        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

        payload = {"name": "newspaper",
                   "tagType": "multi",
                   "valueType": "str"}

        req = requests.post("https://api_baseurl/v1/push/tags",
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
            "name": "newspaper",
            "tagType": "multi",
            "trackingId": "6ba45488-5995-45d2-b51b-39a04efb524e",
            "valueType": "str"
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

    serializer = TagSerializer()

    def __repr__(self):
        return "Tag Create & List"

    def __str__(self):
        return self.__repr__()

    page_size = ZopsIntegerParam(
        details="Specifies number of result entries in single response",
        default='10'
    )

    continuation = ZopsStringParam(
        details="Key for retrieval of the next page if exists. It can only be obtained at the "
                "response of a list call."
    )

    def list(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project')
        service = user.get('service')

        page_size = params.get('page_size')
        continuation = params.get('continuation', None)

        body = {
            "project_id": project_id,
            "page_size": page_size,
            "service": service
        }

        if continuation:
            body['continuation'] = continuation

        response = self.rpc_client.rpc_call("list_push_tags", body)
        return {
            "continuation": response['continuation'],
            "result": response['results']
        }

    def create(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project')
        service = user.get('service')
        validated = kwargs.get('validated')

        body = dict(project_id=project_id, service=service, **validated)

        return self.rpc_client.rpc_call("create_push_tag", body, blocking=False)

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())




