from graceful.fields import StringField
from graceful.resources.generic import RetrieveUpdateDeleteAPI
from zopsm.saas.auth import require_roles
from zopsm.saas.models import ERoles
from zopsm.saas.validators import phone_validator
from zopsm.saas.resources.saas_base import SaasBase
from zopsm.saas.utility import remove_user_tokens
from zopsm.saas.utility import delete_consumers_tokens
from zopsm.lib.rest.serializers import ZopsBaseSerializer


class AccountSerializer(ZopsBaseSerializer):
    organizationName = StringField("Organization Name.Max Organization Name length 100 Character",
                                   source='organization_name')
    address = StringField("Address. Max Address length 200 Character")
    phone = StringField("Phone Number, length must be 11 character.", validators=[phone_validator])
    email = StringField("Email for Account.Max Email length 70 Character")


class AccountResource(SaasBase, RetrieveUpdateDeleteAPI):
    """
    Account get, update and delete resource

    ### Code Example:

    #### PUT:
    Update account field
    ### Request:

    ```bash
        #bash
        curl \\
             --request PUT                                                          \\
             --header "Content-Type: application/json"                              \\
             --header "AUTHORIZATION: sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"   \\
                 --body "{                                                              \\
                  \"organizationName\": \"Updated Example Organization\",               \\
                  \"address\": \"Updated_Example Address, A Street No 5.\",             \\
                  \"phone\": \"12345670001\",                                           \\
                  \"email\": \"Updated_zops_test_eneoooeeN@example.com\"                \\
             }"                                                                         \\
             https://api_baseurl/api/v1/account
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
                    "organizationName": "Updated_Example Organization",
                    "address": "Updated_Example Address, A Street No 5.",
                    "phone": "12345678901",
                    "email": "Updated_zops_test_eneoooeeN@example.com"
            }

        req = requests.put("https://api_baseurl/api/v1/account",
                                        header=header, data=json.dumps(body))
    ```

    #### Response:
    202 Accepted.
    ```json
        {
        "meta":{
                "params": {
                        "indent": 0
                        }
               },
        "content": {
                     "organizationName": "Updated_Example Organization",
                     "address": "Updated_Example Address, A Street No 5.",
                     "phone": "12345670001",
                     "email": "Updated_zops_test_eneoooeeN@example.com",
                     }
        }
    ```
    #### Possible Errors
    - __Conflict__: Email address already used


    #### DELETE
    Delete account (all connected field deleted (users, services, consumers, projects)
    ### Request:

    ```bash
        #bash
        curl \\
             --request DELETE                                                       \\
             --header "Content-Type: application/json"                              \\
             --header "AUTHORIZATION: 0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"  \\
             https://api_baseurl/api/v1/account
    ```

    ```python
        #python
        import requests
        import json
            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"
                      }
        req = requests.delete("https://api_baseurl/api/v1/account",
                                        header=header)
    ```
    #### Response:
    202 Accepted.

    #### GET
    Get account information
    ### Request:

    ```bash
        #bash
        curl \\
             --request GET                                                          \\
             --header "Content-Type: application/json"                              \\
             --header "AUTHORIZATION: 0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"  \\
             https://api_baseurl/api/v1/account
    ```

    ```python
        #python
        import requests
        import json
            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"
                      }
        req = requests.get("https://api_baseurl/api/v1/account",
                                        header=header)
    ```
    #### Response:
    200 Accepted.
    ```json
        {
        "meta":{
                "params": {
                        "indent": 0
                        }
               },
        "content": {
                     "organizationName": "Example Organization",
                     "address": "Example Address, A Street No 5.",
                     "phone": "12345670001",
                     "email": "zops_test_eneoooeeN@example.com",
                     }
        }
    ```


    """

    serializer = AccountSerializer()

    def __repr__(self):
        return "Account Get & Update & Delete"

    def resource_name(self):
        return "AccountResource"

    @require_roles(roles=[ERoles.admin])
    def update(self, params, meta, **kwargs):
        account = self.db.update_account(kwargs['token']['account_id'], kwargs['validated'])
        return account

    @require_roles(roles=[ERoles.admin])
    def delete(self, params, meta, **kwargs):
        account = self.db.get_account(kwargs['token']['account_id'])

        for project in account.projects:
            for service in project.services:
                delete_consumers_tokens(project.id, service.service_catalog_code)

        for user in account.managers:
            remove_user_tokens(user.id)

        self.db.delete_account(kwargs['token']['account_id'])

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def retrieve(self, params, meta, **kwargs):
        return self.db.get_account(kwargs['token']['account_id'])
