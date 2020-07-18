from zopsm.lib.rest.fields import ZopsStringField, ZopsAlphaNumericStringField, \
    ZopsJsonObjectField
from zopsm.lib.rest.serializers import ZopsBaseDBSerializer
from zopsm.lib.rest.parameters import ZopsIntegerParam, ZopsStringParam
from zopsm.push.validators import residents_validator
from zopsm.lib.utility import generate_uuid

from zopsm.lib.rest.custom import ZopsRetrieveUpdateDeleteApi, ZopsContinuatedListCreateApi


class SegmentSerializer(ZopsBaseDBSerializer):
    segmentId = ZopsAlphaNumericStringField("Unique identifier of the segment", source='id',
                                            read_only=True)
    name = ZopsStringField("Name of the segment.")
    residents = ZopsJsonObjectField("Object representation of the expressions which define the "
                                    "target audience of the push message",
                                    validators=[residents_validator])


class Segment(ZopsRetrieveUpdateDeleteApi):
    """
    Allows to retrieve, update and delete a segment.

    ### Code Examples:
    #### GET:
    Retrieves the segment with given id.
    ##### Request:
    ```bash
        #bash
        curl \\
             --request GET \\
             --header "Content-Type: application/json; charset=utf-8" \\
             --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
             https://api_baseurl/v1/push/segments/ecbf6155b4dd4703960fbdd2a882ea29

    ```

    ```python
        # python
        import requests

        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

        req = requests.get("https://api_baseurl/v1/push/segments/ecbf6155b4dd4703960fbdd2a882ea29",
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
                "segmentId": "ecbf6155b4dd4703960fbdd2a882ea29",
                "name": "Students Greater Than 15 y.o. and Has Blue Eyes",
                "residents": {
                    "sets": {
                        "a": {"key": "age", "relation": ">", "value": "15", "intention": "target"},
                        "b": {"key": "eye-color", "relation": "=", "value": "blue", "intention": "target"}
                    },
                    "expression": "a n b"
                },
                "creationTime": "2017-08-20T08:54:56.750Z00:00",
                "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                "isDeleted": false,
                "isActive": true
            }
        }
    ```

    #### PUT:
    Updates a segment with given body.

    ##### Request:
    ```bash

    curl \\
         --request PUT \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
         --data-binary "{ \\
                            \"name\": \"Students Greater Than 15 y.o. or Has Blue Eyes\", \\
                            \"residents\": {\\
                                \"sets\": {\\
                                    \"a\": {\"key\": \"age\", \"relation\": \">\", \"value\": \"15\", \"intention\": \"target\"}, \\
                                    \"b\": {\"key\": \"eye-color\", \"relation\": \"=\", \"value\": \"blue\", \"intention\": \"target\"}, \\
                                }", \\
                                \"expression\": \"a U b\"
                            }", \\
                        }" \\
         https://api_baseurl/v1/push/segments/ecbf6155b4dd4703960fbdd2a882ea29
    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

    payload = {
        "name": "Students Greater Than 15 y.o. or Has Blue Eyes",
        "residents": {
            "sets": {
                "a": {"key": "age", "relation": ">", "value": "15", "intention": "target"},
                "b": {"key": "eye-color", "relation": "=", "value": "blue", "intention": "target"}
            },
            "expression": "a U b"
        }
    }

    req = requests.put("https://api_baseurl/v1/push/segments/ecbf6155b4dd4703960fbdd2a882ea29",
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
            "name": "Students Greater Than 15 y.o. or Has Blue Eyes",
            "residents": {
                "expression": "a U b",
                "sets": {
                    "a": {
                        "intention": "target",
                        "key": "age",
                        "relation": ">",
                        "value": "15"
                    },
                    "b": {
                        "intention": "target",
                        "key": "eye-color",
                        "relation": "=",
                        "value": "blue"
                    }
                }
            },
            "segmentId": "ecbf6155b4dd4703960fbdd2a882ea29",
            "trackingId": "dbbf5d77-e049-48a8-add2-5b0aaa496d02"
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
    Deletes the segment with given id.
    ##### Request:
    ```bash
        #bash
        curl \\
             --request DELETE \\
             --header "Content-Type: application/json; charset=utf-8" \\
             --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
             https://api_baseurl/v1/push/segments/ecbf6155b4dd4703960fbdd2a882ea29

    ```

    ```python
        # python
        import requests

        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

        req = requests.delete("https://api_baseurl/v1/push/segments/ecbf6155b4dd4703960fbdd2a882ea29",
                                    headers=header)

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "trackingId": "fb212c61-8b87-4e5a-a642-9db9e2bd7efd"
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
    - __Object Not Found__: Probably you try to get or delete a non-existent tag.
    - __Conflict__: Probably you try to delete a tag which is included in a segment or segments.


    """

    serializer = SegmentSerializer()

    def __repr__(self):
        return "Segment Retrieve & Update & Delete"

    def __str__(self):
        return self.__repr__()

    def retrieve(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project')
        service = user.get('service')
        segment_id = kwargs.get('segment_id')
        self.check_resource_id(segment_id)
        body = {
            "project_id": project_id,
            "segment_id": segment_id,
            "service": service
        }
        return self.rpc_client.rpc_call("get_push_segment", body)

    def update(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project')
        service = user.get('service')
        segment_id = kwargs.get('segment_id')
        self.check_resource_id(segment_id)
        body = dict(project_id=project_id, **validated, segment_id=segment_id, service=service)
        rpc_params = self.rpc_client.rpc_call("update_push_segment", body, blocking=False)
        rpc_params['id'] = segment_id
        return rpc_params

    def delete(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project')
        service = user.get('service')
        segment_id = kwargs.get('segment_id')
        self.check_resource_id(segment_id)
        body = {
            "project_id": project_id,
            "segment_id": segment_id,
            "service": service
        }
        rpc_params = self.rpc_client.rpc_call("delete_push_segment", body, blocking=False)
        return {"trackingId": rpc_params['tracking_id']}


class SegmentList(ZopsContinuatedListCreateApi):
    """
    Allows to create and list segments.

    ### Creating Segments
    Segments can be interpreted as recipients that are grouped by a certain expression. `residents`
    field of a `segment` includes the `sets` and `expression` attributes.

    ```json
    "residents": {
        "sets": {
            "a": {"key": "color", "relation": "=", "value": "blue", "intention": "target"},
            "b": {"key": "age", "relation": "<", "value": "55", "intention": "target"},
            "c": {"key": "birth_year", "relation": "()", "value": "["1980","2010"]",
            "intention": "target"},
            "d": {"key": "device", "relation": "=", "value": "apple", "intention": "client"},
        },
        "expression": "(a U b) - (c n d)"
    }
    ```
    Each set item in the `sets` attribute of the `residents` field has a common interpretation.
        - Key of set item is the name of the set that will be used in the `expression`
        - `key` attribute of the set item represents the tag name whose will be applied a filter on
        - `relation` attribute of the set item represents the relation which will be applied on tag.
        It can be '=', '<', '>', '()', with meanings equals, less than, greater than and in range
        respectively.
        - `value` attribute of the set item represents the value which will be passed to the filter
        relation. It will always be string or consist of strings, and with respect to the type,
        casting is performed at the behind of the scene. If relation is a range operation, value
        must be a list of two items represents the initial and final elements of range.
        - `intention` indicates the type of tag which will be applied a filter on whether it is a
        user tag (`target`), or it is a client tag (`client`).

    `expression` attribute defines the relation of sets by using 'U', 'n' and '-' set operators.
        - The union symbol `U` returns the union of the input sets.
        - The intersection symbol `n` returns the intersection of the input sets.
        - The difference symbol `-` returns the difference of the input sets with given order. It
        means that "a - b" is NOT equal to "b - a".

    > Warning
    >
    > Parentheses are crucial if more than one operator exists. Following is not a valid usage even
    > if it is mathematically correct: "a n b n c". It must be something like "(a n b) n c" or
    > "a n (b n c)".


    > Warning
    >
    > It is not allowed that if a given set is not used in the expression, or an expression includes
    > a set name and it is not in the given sets.

    ### Code Examples:
    #### POST:
    Creates a segment with given body.

    ##### Request:
    ```bash

    curl \\
         --request POST \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
         --data-binary "{ \\
                            \"name\": \"Students Greater Than 15 y.o. and Has Blue Eyes\", \\
                            \"residents\": {\\
                                \"sets\": {\\
                                    \"a\": {\"key\": \"age\", \"relation\": \">\", \"value\": \"15\", \"intention\": \"target\"}, \\
                                    \"b\": {\"key\": \"eye-color\", \"relation\": \"=\", \"value\": \"blue\", \"intention\": \"target\"}, \\
                                }", \\
                                \"expression\": \"a n b\"
                            }", \\
                        }" \\
         https://api_baseurl/v1/push/segments
    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

    payload = {
        "name": "Students Greater Than 15 y.o. and Has Blue Eyes",
        "residents": {
            "sets": {
                "a": {"key": "age", "relation": ">", "value": "15", "intention": "target"},
                "b": {"key": "eye-color", "relation": "=", "value": "blue", "intention": "target"}
            },
            "expression": "a n b"
        }
    }

    req = requests.post("https://api_baseurl/v1/push/segments",
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
            "name": "Students Greater Than 15 y.o. and Has Blue Eyes",
            "residents": {
                "expression": "a n b",
                "sets": {
                    "a": {
                        "intention": "target",
                        "key": "age",
                        "relation": ">",
                        "value": "15"
                    },
                    "b": {
                        "intention": "target",
                        "key": "eye-color",
                        "relation": "=",
                        "value": "blue"
                    }
                }
            },
            "segmentId": "ecbf6155b4dd4703960fbdd2a882ea29",
            "trackingId": "dbbf5d77-e049-48a8-add2-5b0aaa496d02"
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


    #### PATCH:
    Creates segments with given list of segments.

    ##### Request:
    ```bash

    curl \\
         --request PATCH \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
         --data-binary "[ \\
                            { \\
                                \"name\": \"Students Greater Than 15 y.o. and Has Blue Eyes\", \\
                                \"residents\": {\\
                                    \"sets\": {\\
                                        \"a\": {\"key\": \"age\", \"relation\": \">\", \"value\": \"15\", \"intention\": \"target\"}, \\
                                        \"b\": {\"key\": \"eye-color\", \"relation\": \"=\", \"value\": \"blue\", \"intention\": \"target\"}, \\
                                    }", \\
                                    \"expression\": \"a n b\"
                                }", \\
                            }, \\
                            { \\
                                \"name\": \"Having Android Device or Reading Sabah\", \\
                                \"residents\": {\\
                                    \"sets\": {\\
                                        \"a\": {\"key\": \"newspaper\", \"relation\": \"=\", \"value\": \"Sabah\", \"intention\": \"target\"}, \\
                                        \"b\": {\"key\": \"device\", \"relation\": \"=\", \"value\": \"android\", \"intention\": \"client\"}, \\
                                    }", \\
                                    \"expression\": \"a U b\"
                                }", \\
                            } \\
                        ]" \\
         https://api_baseurl/v1/push/segments
    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

    payload = [
                {
                    "name": "Having Android Device or Reading Sabah",
                    "residents": {
                        "sets": {
                            "a": {"key": "newspaper", "relation": "=", "value": "Sabah", "intention": "target"},
                            "b": {"key": "device", "relation": "=", "value": "android", "intention": "client"}
                        },
                        "expression": "a U b"
                    }
                },
                {
                    "name": "Students Greater Than 15 y.o. and Has Blue Eyes",
                    "residents": {
                        "sets": {
                            "a": {"key": "age", "relation": ">", "value": "15", "intention": "target"},
                            "b": {"key": "eye-color", "relation": "=", "value": "blue", "intention": "target"}
                        },
                        "expression": "a n b"
                    }
                }
        ]

    req = requests.post("https://api_baseurl/v1/push/segments",
                                headers=header, data=json.dumps(payload))

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": [
            {
                "creationTime": null,
                "isActive": null,
                "isDeleted": null,
                "lastUpdateTime": null,
                "name": "Having Android Device or Reading Sabah",
                "residents": {
                    "sets": {
                        "a": {
                            "key": "newspaper",
                            "relation": "=",
                            "value": "Sabah",
                            "intention": "target"
                        },
                        "b": {
                            "key": "device",
                            "relation": "=",
                            "value": "android",
                            "intention": "client"
                        }
                    },
                    "expression": "a U b"
                },
                "segmentId": "4b40c6cd5113462e9bbf0b0421fbc412",
                "trackingId": "24cd0545-b60f-4e67-80ba-283b1d277413"
            },
            {
                "creationTime": null,
                "isActive": null,
                "isDeleted": null,
                "lastUpdateTime": null,
                "name": "Students Greater Than 15 y.o. and Has Blue Eyes",
                "residents": {
                    "sets": {
                        "a": {
                            "key": "age",
                            "relation": ">",
                            "value": "15",
                            "intention": "target"
                        },
                        "b": {
                            "key": "eye-color",
                            "relation": "=",
                            "value": "blue",
                            "intention": "target"
                        }
                    },
                    "expression": "a n b"
                },
                "segmentId": "ecbf6155b4dd4703960fbdd2a882ea29",
                "trackingId": "dbbf5d77-e049-48a8-add2-5b0aaa496d02"
            }
        ],
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



    #### GET:
    Lists segments by pageSize and continuation params.
    ##### Request:
    ```bash
        #bash
        curl \\
             --request GET \\
             --header "Content-Type: application/json; charset=utf-8" \\
             --header "Authorization: Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
             https://api_baseurl/v1/push/segments?page_size=2

    ```

    ```python
        # python
        import requests

        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Token a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

        req = requests.get("https://api_baseurl/v1/push/segments?page_size=2",
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
                        "segmentId": "91a323236a58455e8d0a3b44eb752a99",
                        "name": "Having Android Device or Reading Sabah",
                        "residents": {
                            "sets": {
                                "a": {"key": "newspaper", "relation": "=", "value": "Sabah", "intention": "target"},
                                "b": {"key": "device", "relation": "=", "value": "android", "intention": "client"}
                            },
                            "expression": "a U b"
                        },
                        "creationTime": "2017-08-20T08:54:56.750Z00:00",
                        "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                        "isDeleted": false,
                        "isActive": true
                    },
                    {
                        "segmentId": "9368ce8a03d44505b5792c28deb586b4",
                        "name": "Students Greater Than 15 y.o. and Has Blue Eyes",
                        "residents": {
                            "sets": {
                                "a": {"key": "age", "relation": ">", "value": "15", "intention": "target"},
                                "b": {"key": "eye-color", "relation": "=", "value": "blue", "intention": "target"}
                            },
                            "expression": "a n b"
                        },
                        "creationTime": "2017-08-20T08:54:56.750Z00:00",
                        "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                        "isDeleted": false,
                        "isActive": true
                    }
                ],
                "continuation": "1cd6c8c224aa40f4b6f66ed0c69d370b"
            }
        }
    ```
    > Warning
    >
    > The next page can be obtained via requesting to
    > `https://api_baseurl/v1/push/segments?page_size=2&continuation=1cd6c8c224aa40f4b6f66ed0c69d370b`

    """

    serializer = SegmentSerializer()

    page_size = ZopsIntegerParam(
        details="Specifies number of result entries in single response",
        default='10'
    )

    continuation = ZopsStringParam(
        details="Key for retrieval of the next page if exists. It can only be obtained at the "
                "response of a list call."
    )

    def __repr__(self):
        return "Segment Create & Create Bulk & List"

    def __str__(self):
        return self.__repr__()

    def create(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project')
        service = user.get('service')
        segment_id = generate_uuid()
        body = dict(project_id=project_id, **validated, service=service, segment_id=segment_id)

        rpc_params = self.rpc_client.rpc_call("create_push_segment", body, blocking=False)
        rpc_params['id'] = segment_id
        return rpc_params

    def list(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project')
        service = user.get('service')
        page_size = params.get('page_size')
        continuation = params.get('continuation', None)

        body = dict(project_id=project_id, page_size=page_size, service=service)

        if continuation:
            body['continuation'] = continuation

        response = self.rpc_client.rpc_call("list_push_segments", body)
        return {
            "continuation": response['continuation'],
            "result": response['results']
        }
