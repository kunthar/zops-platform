from graceful.resources.generic import RetrieveAPI
from graceful.fields import StringField
from zopsm.lib.rest.serializers import ZopsBaseSerializer
from zopsm.saas.auth import require_roles
from zopsm.saas.models import ERoles
from zopsm.saas.resources.saas_base import SaasBase


class UserSerializer(ZopsBaseSerializer):
    id = StringField("ID", read_only=True)
    email = StringField("Email for user.Max length 70 Character", read_only=True)
    role = StringField("Role of user.", read_only=True)
    firstName = StringField("Name of user.Max length 32 Character", source='first_name', read_only=True)
    lastName = StringField("Last Name of user.Max length 32 Character", source='last_name', read_only=True)


class MeResource(SaasBase, RetrieveAPI):
    """
    Allow to get user information

        ### Code Examples
        #### GET:
        Retrieve user information with token.
        #### Request:
        ```bash
            #bash
            curl \\
                 --request GET                                                          \\
                 --header "Content-Type: application/json"                              \\
                 --header "AUTHORIZATION: 0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"  \\
                 https://api_baseurl/api/v1/me
        ```

        ```python
            #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"
                      }
            req = requests.get("https://api_baseurl/api/v1/me",
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
                "role": "admin",
                "id": 123123123123,
                "firstName": "ahmet",
                "lastName": "mehmet"
              }
            }
        ```
    """

    serializer = UserSerializer()

    def __repr__(self):
        return "Get User Information"

    def resource_name(self):
        return "MeResource"

    @require_roles(roles=[ERoles.manager, ERoles.admin, ERoles.developer, ERoles.billing])
    def retrieve(self, params, meta, **kwargs):
        user_id = kwargs['token']['sub']
        account_id = kwargs['token']['account_id']

        user = self.db.get_user(user_id, account_id)

        return {
            "id": user_id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.name
        }
