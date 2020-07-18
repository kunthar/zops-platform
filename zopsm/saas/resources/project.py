# -*- coding: utf-8 -*-
from falcon.errors import HTTPMethodNotAllowed, HTTPBadRequest
from graceful.fields import StringField, IntField
from graceful.resources.generic import ListCreateAPI, RetrieveUpdateDeleteAPI, RetrieveUpdateAPI
from zopsm.saas.auth import require_roles
from zopsm.saas.models import Project, ERoles
from zopsm.saas.models import Account
from zopsm.saas.resources.saas_base import SaasBase
from zopsm.lib.sd_vault import vault
from zopsm.lib.settings import VAULT_PUSH_APNS_PATH, VAULT_PUSH_FCM_PATH
from zopsm.lib.settings import ACCOUNT_LIMIT
from zopsm.lib.rest.http_errors import HTTPPaymentRequired
from zopsm.lib.rest.serializers import ZopsBaseSerializer
from zopsm.lib.rest.fields import ZopsListOfStringsField
from zopsm.saas.utility import del_project_services_admin_token, add_project_services_admin_token, generate_user_token
from zopsm.saas.utility import encode_jwt_token, set_project_services_admin_token, get_project_services_admin_token


class ProjectResourceSerializer(ZopsBaseSerializer):
    name = StringField("Project name.Max length 70 Character")
    description = StringField("Project description.Max length 200 Character")
    id = StringField("ID", read_only=True)
    userLimit = IntField("User limit of service.", read_only=True, source='user_limit')
    userUsed = IntField("User used of service.", read_only=True, source='user_used')
    services = ZopsListOfStringsField("Project's active services", read_only=True)


class ProjectSecretSerializer(ZopsBaseSerializer):
    fcmApiKeys = StringField("Fcm API Key", source='fcm_api_key')
    fcmProjectNumber = StringField("Fcm Project Number", source='fcm_project_number')
    apnsCert = StringField("Apns Cert", source='apns_cert')
    id = StringField("ID", read_only=True)


class ProjectServicesAdminTokenSerializer(ZopsBaseSerializer):
    projectServicesAdminToken = StringField("Project Services Admin Token",
                                            source='project_services_admin_token', read_only=True)


class ProjectResource(SaasBase, ListCreateAPI):
    """
    Allows to create and list project

    ####### Code Example:

    #### POST:
      Create a new project
     ### Request:

       ```bash
           #bash
              curl \\
                    --request POST                                                                   \\
                    --header "Content-Type: application/json"                                        \\
                    --header "AUTHORIZATION : sdkjfhskjfk32kjh42kj2h342kh34h2k3h4kkhjsdhjkhwr"       \\
                    --body "{                                                   \\
                              \"name\": \"Aka Project\",                        \\
                              \"description\": \"Super top secret project!\"    \\
                            }"                                                  \\
                     https://api_baseurl/api/v1/projects
       ```

       ```python
           #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "sdkjfhskjfk32kjh42kj2h342kh34h2k3h4kkhjsdhjkhwr"
                      }

            body = {
                    "name": "Aka Project",
                    "description": "Super top secret project!"
                    }

            req = requests.post("https://api_baseurl/api/v1/projects",
                                            header=header, data=json.dumps(body))
       ```
     ### Response:
      201 Created.
      ```json
            {
              "meta": {
                "params": {
                  "indent": 0
                }
              },
              "content": {
                "name": "Aka Project",
                "description": "Super top secret project!",
                "id": "1aa36f61f9c14156a900921abb04af56",
                "userLimit": null,
                "userUsed": null
              }
            }
      ```


    #### GET:
      List projects
     ### Request:

       ```bash
           #bash
              curl \\
                    --request GET                                                               \\
                    --header "Content-Type: application/json"                                   \\
                    --header "AUTHORIZATION: sdkjfhskjfk32kjh42kj2h342kh34h2k3h4kkhjsdhjkhwr"   \\
                     https://api_baseurl/api/v1/projects
       ```

       ```python
           #python
            import requests
            import json

                header = {
                            "Content-Type": "application/json",
                            "AUTHORIZATION": "sdkjfhskjfk32kjh42kj2h342kh34h2k3h4kkhjsdhjkhwr"
                          }

            req = requests.get("https://api_baseurl/api/v1/projects",
                                            header=header)
       ```

     ### Response:
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
              "name": "Aka Project",
              "description": "Super top secret project!",
              "id": "1aa36f61f9c14156a900921abb04af56",
              "userLimit": 10,
              "userUsed": 0
            },
            {
              "name": "Zetaops Project",
              "description": "secret project!",
              "id": "asdasd1aa36f61f9c14156a900921abb04af56",
              "userLimit": 10,
              "userUsed": 0
            }
          ]
        }

      ```
    """
    serializer = ProjectResourceSerializer()

    def __repr__(self):
        return "Project Create & List"

    def resource_name(self):
        return "ProjectResource"

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def list(self, params, meta, **kwargs):
        result = []
        projects = self.db.filter(model=Project, account_id=kwargs['token']['account_id'])

        for obj in projects:
            result.append({"name": obj.name,
                           "id": obj.id,
                           "description": obj.description,
                           "user_limit": obj.user_limit,
                           "user_used": obj.user_used})
        return result

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def create(self, params, meta, **kwargs):
        validated = kwargs['validated']
        account = self.db.get_account(kwargs['token']['account_id'])

        if not account.project_limit > account.project_used:
            raise HTTPPaymentRequired(description="Please check your account's project limit")

        user_limit = ACCOUNT_LIMIT['user_limit']
        project = Project(name=validated['name'], description=validated['description'],
                          account_id=kwargs['token']['account_id'], user_limit=user_limit)
        account.project_used = Account.project_used + 1
        self.db.session.add(project)
        return project

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class ProjectSingleResource(SaasBase, RetrieveUpdateDeleteAPI):
    """
    Allows to update and retrieve project with project id

    ####### Code Example:

    #### PUT:
      Update project with project id
     ### Request:

       ```bash
           #bash
              curl \\
                    --request PUT                                                                       \\
                    --header "Content-Type: application/json"                                           \\
                    --header "AUTHORIZATION": sdkjfhskjfk32kjh42kj2h342kh34h2k3h4kkhjsdhjkhwr"          \\
                    --body "{                                                         \\
                                \"name\": \"Aka Project!..\",                         \\
                                \"description\": \"Super top secret project!\",       \\
                            }"                                                        \\
                     https://api_baseurl/api/v1/projects/{projectId}

       ```

       ```python
           #python
            import requests
            import json

                header = {
                            "Content-Type": "application/json",
                            "AUTHORIZATION": "sdkjfhskjfk32kjh42kj2h342kh34h2k3h4kkhjsdhjkhwr"
                          }
                body = {
                        "name": "Aka Project!..",
                        "description": "Super top secret project!"
                        }

            req = requests.put("https://api_baseurl/api/v1/projects/{projectId}",
                                            header=header, data=json.dumps(body))
       ```
     ### Response:
      202 Accepted.
      ```json
        {
          "meta": {
            "params": {
              "indent": 0
            }
          },
          "content": {
            "name": "Aka Project!..",
            "description": "Super top secret project!",
            "id": "1aa36f61f9c14156a900921abb04af56",
            "userLimit": 10,
            "userUsed": 0
          }
        }
      ```

    #### GET:
      Retrieve project with id
     ### Request:

       ```bash
           #bash
              curl \\
                    --request GET                                                                       \\
                    --header "Content-Type: application/json"                                           \\
                    --header "AUTHORIZATION": Token sdkjfhskjfk32kjh42kj2h342kh34h2k3h4kkhjsdhjkhwr"    \\
                     https://api_baseurl/api/v1/projects/{projectId}
       ```

       ```python
           #python
            import requests
            import json

                header = {
                            "Content-Type": "application/json",
                            "AUTHORIZATION": "sdkjfhskjfk32kjh42kj2h342kh34h2k3h4kkhjsdhjkhwr"
                          }

            req = requests.get("https://api_baseurl/api/v1/projects/{projectId}",
                                            header=header)
       ```
     ### Response:
      200 OK.
      ```json
            {
              "meta": {
                "params": {
                  "indent": 0
                }
              },
              "content": {
                "name": "Aka Project",
                "description": "Super top secret project!",
                "id": "1aa36f61f9c14156a900921abb04af56",
                "services": ["roc", "push"]
                "userLimit": 10,
                "userUsed": 0
              }
            }
      ```
      ## Possible Error
       - __Not Found___

    """
    serializer = ProjectResourceSerializer()

    def __repr__(self):
        return "Project Retrieve & Update"

    def resource_name(self):
        return "ProjectSingleResource"

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def retrieve(self, params, meta, **kwargs):
        project = self.db.get_project_by_id(kwargs['project_id'], kwargs['token']['account_id'])
        project_services = [service.service_catalog_code for service in project.services]
        return {
            "name": project.name,
            "description": project.description,
            "id": project.id,
            "user_limit": project.user_limit,
            "user_used": project.user_used,
            "services": project_services
        }

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def update(self, params, meta, **kwargs):
        project = self.db.get_project_by_id(kwargs['project_id'], kwargs['token']['account_id'])
        project.name = kwargs['validated']['name']
        project.description = kwargs['validated']['description']
        return project

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def delete(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class ProjectSecretResource(SaasBase, RetrieveUpdateAPI):
    """
    Project Google Server API Key, Google Project Number, Apns IOS Push Certification Resource. You can get and update using this resource.

        ### Code Examples

        #### GET:
        Get Google Server API Key, Google Project Number, Apns IOS Push Certification
        #### Request:

        ```bash
            #bash
            curl \\
                 --request GET                                                          \\
                 --header "Content-Type: application/json"                              \\
                 --header "AUTHORIZATION: 0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"  \\
                 https://api_baseurl/api/v1/projects/{project_id}/api
        ```

        ```python
            #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"
                      }
            req = requests.get("https://api_baseurl/api/v1/projects/{project_id}/api",
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
                "fcmApiKeys": "asdasdasdas123123",
                "fcmProjectNumber": "12312312qweqweq213",
                "apnsCert": "Yga25vd2xlZGdlLCBleGNlZWRzIHRoZSBzaG9ydCB2ZWhlbWVuY2Ugb2YgYW55IGNhcm5hbCBwbGVhc3VyZS4=",
                "id": "c3c0a4864a054b6da3c642588c594fc3"
              }
            }
        ```


        #### PUT:
        Update Google Server API Key, Google Project Number, Apns IOS Push Certification
        #### Request:

        ```bash
            #bash
            curl \\
                 --request PUT                                                              \\
                 --header "Content-Type: application/json"                                  \\
                 --header "AUTHORIZATION: 0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"      \\
                 --body "{                                                                                  \\
                        \"fcmApiKeys\": \"asdasdasdas123123\",                                              \\
                        \"fcmProjectNumber\": \"12312312qweqweq213\",                                       \\
                        \"apnsCert\": \"ZWRzIHRoZSBzaG9ydCB2ZWhlbWVuY2Ugb2YgYW55IGNhcm5hbCBwbGVhc3VyZS4=\"  \\
                 }" \\
                 https://api_baseurl/api/v1/projects/{project_id}/api
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
                    "fcmApiKeys": "asdasdasdas123123",
                    "fcmProjectNumber": "12312312qweqweq213",
                    "apnsCert": "asd2342j3423942342343VyZS4="
                    }
            req = requests.put("https://api_baseurl/api/v1/projects/{project_id}/api",
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
                "fcmApiKeys": "asdasdasdas123123",
                "fcmProjectNumber": "12312312qweqweq213",
                "apnsCert": "HRoZSBzaG9ydCB2ZWhlbWVuY2Ugb2YgYW55IGNhcm5hbCBwbGVhc3VyZS4=",
                "id": "c3c0a4864a054b6da3c642588c594fc3"
              }
            }
        ```
        #### Possible Error
        - __Bad Request__
    """

    serializer = ProjectSecretSerializer()

    def __repr__(self):
        return "Google Server API Key, Google Project Number, Apns IOS Push Certification Retrieve & Update"

    def resource_name(self):
        return "ProjectSecretResource"

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def retrieve(self, params, meta, **kwargs):
        project_id = kwargs['project_id']

        apns_path = VAULT_PUSH_APNS_PATH.format(project_id=project_id)
        apns_cert = vault.read(path=apns_path)['data']['cert_file']

        fcm_path = VAULT_PUSH_FCM_PATH.format(project_id=project_id)
        fcm_api_key = vault.read(path=fcm_path)['data']['api_key']
        fcm_project_number = vault.read(path=fcm_path)['data']['project_number']

        return {
            "fcm_api_key": fcm_api_key,
            "fcm_project_number": fcm_project_number,
            "apns_cert": apns_cert,
            "id": project_id
        }

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def update(self, params, meta, **kwargs):
        project_id = kwargs['project_id']
        validated = kwargs['validated']
        project = self.db.get_project(project_id=project_id,
                                      account_id=kwargs['token']['account_id'])

        project.fcm_api_key = validated['fcm_api_key']
        project.fcm_project_number = validated['fcm_project_number']
        project.apns_cert = validated['apns_cert'].encode()

        apns_path = VAULT_PUSH_APNS_PATH.format(project_id=project_id)
        vault.write(path=apns_path, cert_file=validated['apns_cert'])

        fcm_path = VAULT_PUSH_FCM_PATH.format(project_id=project_id)
        vault.write(path=fcm_path, api_key=validated['fcm_api_key'],
                    project_number=validated['fcm_project_number'])

        return {
            "fcm_api_key": project.fcm_api_key,
            "fcm_project_number": project.fcm_project_number,
            "apns_cert": project.apns_cert,
            "id": project_id
        }


class ProjectServicesAdminTokenResource(SaasBase, RetrieveUpdateAPI):
    serializer = ProjectServicesAdminTokenSerializer()

    def __repr__(self):
        return "Project Services Admin Token Resource"

    def resource_name(self):
        return "ProjectServicesAdminTokenResource"

    @require_roles(roles=[ERoles.admin])
    def retrieve(self, params, meta, **kwargs):
        project_id = kwargs['project_id']
        account_id = kwargs['token']['account_id']
        admin_id = kwargs['token']['sub']

        project = self.db.get_project(project_id=project_id, account_id=account_id)

        if not project:
            raise HTTPBadRequest(description="Project not found")

        token_payload = {'admin_id': admin_id,
                         'account_id': account_id,
                         'project_id': project_id}

        old_token = get_project_services_admin_token(project_id)
        if old_token:
            del_project_services_admin_token(old_token)

        token = generate_user_token()
        set_project_services_admin_token(project_id, token)
        add_project_services_admin_token(token, token_payload)

        return {
            "project_services_admin_token": token
        }
