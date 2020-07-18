import falcon

from graceful.serializers import BaseSerializer
from graceful.fields import IntField, RawField
from graceful.parameters import StringParam
from graceful.resources.generic import (
    RetrieveAPI,
    PaginatedListAPI,
    PaginatedListCreateAPI,
)

api = application = falcon.API()

from zopsm.lib.rest.authentication import zops_authorization_required

# lets pretend that this is our backend storage
CATS_STORAGE = [
    {"id": 0, "name": "kitty", "breed": "saimese"},
    {"id": 1, "name": "lucie", "breed": "maine coon"},
    {"id": 2, "name": "molly", "breed": "sphynx"},
]


# this is how we represent cats in our API
class CatSerializer(BaseSerializer):
    id = IntField("cat identification number", read_only=True)
    name = RawField("cat name")
    breed = RawField("official breed name")

@zops_authorization_required
class Cat(RetrieveAPI):
    """
    Single cat identified by its id
    """
    serializer = CatSerializer()

    def get_cat(self, cat_id):
        try:
            return [
                cat for cat in CATS_STORAGE if cat['id'] == int(cat_id)
            ][0]
        except IndexError:
            raise falcon.HTTPNotFound

    def retrieve(self, params, meta, **kwargs):
        cat_id = kwargs['cat_id']
        return self.get_cat(cat_id)

@zops_authorization_required
class CatList(PaginatedListCreateAPI):

    def allowed_methods(self):
        """Return list of allowed HTTP methods on this resource.

        This is only for purpose of making resource description.

        Returns:
            list: list of allowed HTTP method names (uppercase)

        """
        alloweds = []

        map = {
            "GET": ["retrieve", "list"],
            "POST": ["create"],
            "PUT": ["update"],
            "PATCH": ["create_bulk"],
            "DELETE": ["delete"],
            "HEAD": ["on_head"],
            "OPTIONS": ["on_options"]}

        for method in map.keys():
            attr_list = [getattr(self, m, False) for m in map[method]]
            if any(attr_list):
                for attr in attr_list:
                    if attr and attr.__doc__ != "Not Implemented":
                        alloweds.append(method)
        return alloweds



    """
    Get a unique message identified by `message_id`.

    > Warning
    >
    > This resource is available only version 1. Please be sure the body is empty. You can not
    > send extra parameters like, `title`, `body`, `receiver`, etc.

    Message response is a json string containing message details, such as:
    ```json
        {
            "title": "Hello World!",
            "body": "This message is sent by someone who you might know or maybe not!",
            "id": "FH4DJ90HF1USD9879SIPXAZ"
        }
    ```

    > Warning
    >
    > Response always contains `id`, `title` and `body` and optionally `receiver`, `sender`.
    > Do not send `sender` while using API version 2.0.
    >
    > See here new paragraph starts.

    Warning ends and regular API explanation goes on here. Message is any


    ### Code Examples:
    ```bash

        curl \\
             --request POST \\
             --header "Content-Type: application/json; charset=utf-8" \\
             --header "Authorization: Basic a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102" \\
             --data-binary "{\"project_id\": \"b4392fdb-b6cd-4f3c-82f3-dacf0b3d6432\", \\
                            \"body\": {\"tr\": \"Hello World\"}, \\
                            \"message_tag\": [\"receieved\"]}" \\
             https://zopsm.io/api/v1/message

    ```


    ```python
        import requests
        import json

        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Basic a42069f7b356f2e9189a88d1a4c7fa647b223cd8c81580b673c3ae37f7e4e102"}

        payload = {"project_id": "b4392fdb-b6cd-4f3c-82f3-dacf0b3d6432",
                   "message_tag": ["receieved"],
                   "body": {"tr": "Hello World!"}}

        req = requests.post("https://zopsm.io/api/v1/messages",
                                    headers=header, data=json.dumps(payload))

        print(req.status_code, req.reason)
    ```

    ### Possible Errors
    Alognside with generic ones, endpoint can respond with costum errors below:

    - __Message Not Found__: Probably you try to get a deleted or non-existent message.
    - __Illegal Operand__: Please check definition of sets, they must be declared as shown in fields table.

    """

    serializer = CatSerializer()

    breed = StringParam("set this param to filter cats by breed")

    def list(self, params, meta, **kwargs):
        if 'breed' in params:
            filtered = [
                cat for cat in CATS_STORAGE
                if cat['breed'] == params['breed']
            ]
            return filtered
        else:
            return CATS_STORAGE


    def create(self, params, meta, **kwargs):
        """Not Implemented"""
        pass

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        pass


endpoints = {
    "/v1/cats/{cat_id}": Cat(),
    "/v1/cats/": CatList()
}

for uri, endpoint in endpoints.items():
    api.add_route(uri, endpoint)


# this is how we represent cats in our API
class URLSerializer(BaseSerializer):
    url = RawField("url", read_only=True)


class ResourceListResource(PaginatedListAPI):
    serializer = URLSerializer()

    def list(self, params, meta, **kwargs):
        return [{"url": url} for url, _ in endpoints.items()]


api.add_route("/", ResourceListResource())
