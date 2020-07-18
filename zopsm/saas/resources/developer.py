# -*- coding: utf-8 -*-

from falcon.errors import HTTPMethodNotAllowed
from graceful.fields import StringField
from graceful.resources.generic import RetrieveUpdateDeleteAPI, ListCreateAPI
from zopsm.saas.auth import require_roles
from zopsm.saas.models import ERoles
from zopsm.saas.validators import email_validator
from zopsm.saas.resources.saas_base import SaasBase
from zopsm.saas.utility import remove_user_tokens
from zopsm.saas.utility import add_user_token
from zopsm.lib.rest.serializers import ZopsBaseSerializer
from zopsm.saas.utility import encode_jwt_token, create_auth_token_payload
from zopsm.saas.utility import data_hashing


class UserSerializer(ZopsBaseSerializer):
    id = StringField("ID", read_only=True)
    token = StringField("Access token", read_only=True)
    email = StringField("Email for user.Max length 70 Character", validators=[email_validator])
    password = StringField("Password for user.Max length 128 Character", write_only=True)
    role = StringField("Role of user.", read_only=True)
    firstName = StringField("Name of user.Max length 32 Character", source='first_name')
    lastName = StringField("Last Name of user.Max length 32 Character", source='last_name')


class UserSingleSerializer(ZopsBaseSerializer):
    email = StringField("Email for user.Max length 70 Character", validators=[email_validator])
    password = StringField("Password for user.Max length 128 Character", write_only=True)
    role = StringField("Role of user.", read_only=True)
    firstName = StringField("Name of user.Max length 32 Character", source='first_name')
    lastName = StringField("Last Name of user.Max length 32 Character", source='last_name')
    token = StringField("Access token.", read_only=True)


class DeveloperResource(SaasBase, ListCreateAPI):
    """
        Allows to list and create developer

        ### Code Examples:

        #### POST:
        Create a new user with developer role
        #### Request:

        ```bash
            #bash
            curl \\
                 --request POST                                                          \\
                 --header "Content-Type: application/json"                               \\
                 --header "AUTHORIZATION: 0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"   \\
                 --body "{                                                             \\
                         \"email\": \"zops_test_eneoooeeN@example.com\",               \\
                         \"password\": \"123\",                                        \\
                         \"firstName\": \"emre\",                                      \\
                         \"lastName\": \"dönmesz\"                                     \\
                 }" \\
                 https://api_baseurl/api/v1/developers
        ```

        ```python
            #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1MTA4MTkyNTQsImlhdCI6MTUxMDIxNDQ1NCwic3ViIjoiOTBjNGNjOGIxMWFiNDlhNThlY2I0Yjc5OWZhYTg5NzkiLCJyb2wiOjIsInRlbmFudF9pZCI6bnVsbCwiYWNjb3VudF9pZCI6ImYyMDBiYWNjZGVkNDQxM2E4MWY5YTM4MTA2M2M0MzVjIn0.0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w\"
                      }

            body = {
                    "email": "zops_test_eneoooeeN@example.com",
                    "password": "123",
                    "firstName": "emre",
                    "lastName": "dönmezs"
                    }

            req = requests.post("https://api_baseurl/api/v1/developers",
                                            header=header, data=json.dumps(body))
        ```

        #### Response:
        201 Accepted:

        ```json
            {
            "meta": {
                    "params": {
                                "indent": 0
                                }
                    },
            "content": {
                        "id": "3a033bb9d86443c4a82a98a575c6a461",
                        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1MTA4MTkyNTQsImlhdCI6MTUxMDIxNDQ1NCwic3ViIjoiM2EwMzNiYjlkODY0NDNjNGE4MmE5OGE1NzVjNmE0NjEiLCJyb2wiOjIsInRlbmFudF9pZCI6bnVsbCwiYWNjb3VudF9pZCI6ImYyMDBiYWNjZGVkNDQxM2E4MWY5YTM4MTA2M2M0MzVjIn0.pExlQUMQ8YNyLfUdYf7rmldGI79KQcIz8nwX1NcFC5o",
                        "email": "zops_test_eoNeeoeNnn@example.com",
                        "role": "developer",
                        "firstName": "emre",
                        "lastName": "dönmez"
                        }
            }
        ```

        #### Possible Errors
        - __Conflict__
        - __Unauthorized__


        #### GET
        Retrieve account developers.
        #### Request:

        ```bash
            #bash
            curl \\
                 --request GET                                                          \\
                 --header "Content-Type: application/json"                              \\
                 --header "AUTHORIZATION: 0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"  \\
                 https://api_baseurl/api/v1/developers
        ```

        ```python
            #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"
                      }
            req = requests.get("https://api_baseurl/api/v1/developers",
                                            header=header)
        ```

        #### Response:
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
                         "id": "fc236ae7e97f4afbb638f2f3075eee1c",
                         "email": "zops_test_NnNNnoneoo@example.com",
                         "firstName": "emre",
                         "lastName": "dönmez"
                         "role": "developer",
                         "token": null,

                         },
                        {
                         "id": "b0cbdd61cff843fdaf5a8c62cbbe460e",
                         "email": "zops_test_oNNnNneoeN@example.com",
                         "firstName": "emre2",
                         "lastName": "dönmez2"
                         "role": "developer",
                         "token": null,
                         },
                        {
                         "id": "d31703ec133246f8ab6ee62176aa16f1",
                         "email": "zops_test_oNNenNoo@example.com",
                         "firstName": "emre3",
                         "lastName": "dönmez3"
                         "role": "developer",
                         "token": null,
                         }
                       ]
            }
        ```
        """
    serializer = UserSerializer()
    role = ERoles.developer

    def __repr__(self):
        return "Developer User Create & List"

    def resource_name(self):
        return "DeveloperResource"

    def _list(self, params, meta, **kwargs):
        result = []
        for obj in self.list(params, meta, **kwargs):
            obj.role = obj.role.name
            result.append(self.serializer.to_representation(obj))
        return result

    @require_roles(roles=[ERoles.admin])
    def list(self, params, meta, **kwargs):
        return self.db.list_user_by_role(account_id=kwargs['token']['account_id'], role=self.role)

    @require_roles(roles=[ERoles.admin])
    def create(self, params, meta, **kwargs):
        user = self.db.create_user(validated=kwargs['validated'], jwt_token=kwargs['token'], role=self.role)
        token_payload = create_auth_token_payload(user.id, role=user.role, account_id=user.account_id)
        token = encode_jwt_token(token_payload)

        add_user_token(user.id, token)

        return {
            "token": token,
            "role": user.role.name,
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        }

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class DeveloperSingleResource(SaasBase, RetrieveUpdateDeleteAPI):
    """
        Allows to get and update developer with id.

        ### Code Examples

        #### GET:
        Retrieve developer user with id.
        #### Request:

        ```bash
            #bash
            curl \\
                 --request GET                                                          \\
                 --header "Content-Type: application/json"                              \\
                 --header "AUTHORIZATION: 0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"  \\
                 https://api_baseurl/api/v1/developers/{developer_id}
        ```

        ```python
            #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"
                      }
            req = requests.get("https://api_baseurl/api/v1/developers/{developer_id}",
                                            header=header)
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
                "email": "zops_test_oenNeNen@example.com",
                "role": "developer",
                "firstName": "ahmet",
                "lastName": "mehmet"
              }
            }
        ```


        #### PUT:
        Update developer user with id.
        #### Request:

        ```bash
            #bash
            curl \\
                 --request PUT                                                              \\
                 --header "Content-Type: application/json"                                  \\
                 --header "AUTHORIZATION: 0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"      \\
                 --body "{                                                             \\
                         \"email\": \"zops_test_eneoooeeN@example.com\",               \\
                         \"password\": \"123\",                                        \\
                         \"firstName\": \"mehmet\",                                    \\
                         \"lastName\": \"ahmet\"                                       \\
                 }" \\
                 https://api_baseurl/api/v1/developers/{developer_id}
        ```

        ```python
            #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"
                      }
            body = {
                    "email": "zops_test_eneoooeeN@example.com",
                    "password": "123",
                    "firstName": "mehmet",
                    "lastName": "ahmet"
                    }
            req = requests.post("https://api_baseurl/api/v1/developers/{developer_id}",
                                            header=header, data=json.dumps(body))
        ```

        ##### Response:
        202 Accepted.
        ```json{
              "meta": {
                "params": {
                  "indent": 0
                }
              },
              "content": {
                "email": "zops_test_nNnoeeee@example.com",
                "role": "developers",
                "firstName": "mehmet",
                "lastName": "ahmet"
              }
            }
        ```

        #### Possible Error
        - __Conflict_
        - __Bad Request__
    """
    serializer = UserSingleSerializer()
    role = ERoles.developer

    def __repr__(self):
        return "Developer User Retrieve & Update & Delete"

    def resource_name(self):
        return "DeveloperSingleResource"

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def retrieve(self, params, meta, **kwargs):
        user = self.db.get_user(user_id=kwargs['developer_id'], account_id=kwargs['token']['account_id'])

        return {
            "role": user.role.name,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def update(self, params, meta, **kwargs):
        kwargs['validated']['password'] = data_hashing(kwargs['validated']['password'])
        updated_user = self.db.update_user(user_id=kwargs['developer_id'], validated=kwargs['validated'],
                                           account_id=kwargs['token']['account_id'])

        return {
            "email": updated_user.email,
            "role": updated_user.role.name,
            "first_name": updated_user.first_name,
            "last_name": updated_user.last_name,
        }

    @require_roles(roles=[ERoles.admin])
    def delete(self, params, meta, **kwargs):
        self.db.delete_user(kwargs['developer_id'], kwargs['token']['account_id'])
        remove_user_tokens(kwargs['developer_id'])
