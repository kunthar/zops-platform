# -*- coding: utf-8 -*-

from falcon.errors import HTTPMethodNotAllowed
from graceful.fields import StringField, IntField
from graceful.resources.generic import ListCreateAPI, RetrieveUpdateDeleteAPI
from zopsm.saas.auth import require_roles
from zopsm.saas.models import ERoles, Service, ServiceCatalog, ServiceEvent
from zopsm.saas.validators import is_service_code
from zopsm.saas.resources.saas_base import SaasBase
from zopsm.lib.rest.fields import ZopsJsonObjectField
from zopsm.lib.settings import ACCOUNT_LIMIT
from zopsm.saas.utility import delete_consumers_tokens
from zopsm.lib.rest.serializers import ZopsBaseSerializer


class ServiceCatalogSerializer(ZopsBaseSerializer):
    name = StringField("Service Catalog name")
    description = StringField("Service Catalog description")
    codeName = StringField("Code name of the service.", source='code_name')


class ServiceSerializer(ZopsBaseSerializer):
    id = StringField("ID", read_only=True)
    itemLimit = IntField("Item limit of service.", read_only=True, source='item_limit')
    itemUsed = IntField("Item used of service.", read_only=True, source='item_used')
    name = StringField("Service name.Max length 70 Character")
    description = StringField("Service description.Max length 200 Character")
    serviceCatalogCode = StringField("Code name of the service.", validators=[is_service_code],
                                     source="service_catalog_code")


class ServiceEventSerializer(ZopsBaseSerializer):
    serviceData = ZopsJsonObjectField("Service data", write_only=True, source='service_data')


class ServiceResource(SaasBase, ListCreateAPI):
    """
    Allows to create attachment between service and project

    ### Code Example:

    ##### POST:
    ### Request:

        ```bash
            #bash
            curl \\
                 --request POST                                                                 \\
                 --header "Content-Type: application/json"                                      \\
                 --header "AUTHORIZATION: sdfjskdjhsrk3hfksejhfksefhskefhskeh12123kjhkasdhaıs"  \\
                 --body "{                                                              \\
                                \"serviceCatalogCode\":\"roc\",                         \\
                                \"name\":\"message\",                                   \\
                                \"description\":\"fff\"                                 \\
                        }"                                                              \\
                 https://api_baseurl/api/v1/projects/{project_id}/services
        ```

        ```python
            #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "sdfjskdjhsrk3hfksejhfksefhskefhskeh12123kjhkasdhaıs"
                      }
            body = {
                        "codeName":"roc",
                        "name":"message",
                        "description":"fff"
                    }
            req = requests.post("https://api_baseurl/api/v1/projects/{project_id}/services",
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
                    "id": "316589e74d52490e93a88fdf21c6f2ad",
                    "itemLimit": 0,
                    "name": "message",
                    "description": "fff",
                    "serviceCatalogCode": "roc"
                  }
                }
        ```

    """
    serializer = ServiceSerializer()

    def __repr__(self):
        return "Service Create"

    def resource_name(self):
        return "ServiceResource"

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def create(self, params, meta, **kwargs):
        validated = kwargs['validated']
        message_limit = ACCOUNT_LIMIT["message_limit"][validated['service_catalog_code']]

        service = Service(name=validated['name'],
                          description=validated['description'],
                          project_id=kwargs['project_id'],
                          service_catalog_code=validated['service_catalog_code'],
                          account_id=kwargs['token']['account_id'],
                          item_limit=message_limit)
        self.db.session.add(service)

        return service

    def list(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class ServiceSingleResource(SaasBase, RetrieveUpdateDeleteAPI):
    """
    Allows to delete attachment between project and service

    ### Code Example:

    #### GET:
      Retrieve service with project_id and service_catalog_code
     ### Request:

       ```bash
           #bash
              curl \\
                    --request GET                                                                       \\
                    --header "Content-Type: application/json"                                           \\
                    --header "AUTHORIZATION": Token sdkjfhskjfk32kjh42kj2h342kh34h2k3h4kkhjsdhjkhwr"    \\
                    https://api_baseurl/api/v1/projects/{project_id}/services/{service_catalog_code}
       ```

       ```python
           #python
            import requests
            import json

                header = {
                            "Content-Type": "application/json",
                            "AUTHORIZATION": "sdkjfhskjfk32kjh42kj2h342kh34h2k3h4kkhjsdhjkhwr"
                          }

            req = requests.get("https://api_baseurl/api/v1/projects/{project_id}/services/{service_catalog_code}",
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
                "id": "316589e74d52490e93a88fdf21c6f2ad",
                "itemLimit": 100,
                "itemUsed": 10,
                "name": "message",
                "description": "fff",
                "serviceCatalogCode": "roc"
              }
            }
      ```
      ## Possible Error
       - __Not Found___

    ##### DELETE:
    ### Request:

        ```bash
            #bash
            curl \\
                 --request DELETE                                                               \\
                 --header "Content-Type: application/json"                                      \\
                 --header "AUTHORIZATION: sdfjskdjhsrk3hfksejhfksefhskefhskeh12123kjhkasdhaıs"  \\
                 https://api_baseurl/api/v1/projects/{project_id}/services/{service_catalog_code}
        ```

        ```python
            #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "sdfjskdjhsrk3hfksejhfksefhskefhskeh12123kjhkasdhaıs"
                      }
            req = requests.delete("https://api_baseurl/api/v1/projects/{project_id}/services/{service_catalog_code}",
                                            header=header)
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
                  "content": null
                }
        ```

    """
    serializer = ServiceSerializer()

    def __repr__(self):
        return "Service Delete"

    def resource_name(self):
        return "ServiceSingleResource"

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def delete(self, params, meta, **kwargs):
        # todo: delete service or service "is_deleted" field true ???
        service = self.db.get_service_of_project(service_catalog_code=kwargs['service_catalog_code'],
                                                 project_id=kwargs['project_id'],
                                                 account_id=kwargs['token']['account_id'])
        self.db.session.delete(service)
        delete_consumers_tokens(kwargs['project_id'], kwargs['service_catalog_code'])

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def retrieve(self, params, meta, **kwargs):
        return self.db.get_service_of_project(service_catalog_code=kwargs['service_catalog_code'],
                                              project_id=kwargs['project_id'], account_id=kwargs['token']['account_id'])

    def update(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class ServiceCatalogResource(SaasBase, ListCreateAPI):
    """
    Allows to create and list service catalog

    ### Code Example:

    ##### POST:
    Create service catalog item (You Must be Root)
    ### Request:

        ```bash
            #bash
            curl \\
                 --request POST                                                                 \\
                 --header "Content-Type: application/json"                                      \\
                 --header "AUTHORIZATION: sdfjskdjhsrk3hfksejhfksefhskefhskeh12123kjhkasdhaıs"  \\
                 --body "{                                                              \\
                                \"codeName\":\"roc\",                                   \\
                                \"name\":\"Real Time Online Chat\",                     \\
                                \"description\":\"Real Time Online Chat is funny!\"     \\
                        }"                                                              \\
                 https://api_baseurl/api/v1/services
        ```

        ```python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "sdfjskdjhsrk3hfksejhfksefhskefhskeh12123kjhkasdhaıs"
                      }
            body = {
                        "codeName":"roc",
                        "name":"Real Time Online Chat",
                        "description":"Real Time Online Chat is funny!"
                    }
            req = requests.post("https://api_baseurl/api/v1/services",
                                            header=header, data=json.dumps(body))
        ```

    ### Response:
        201 Accepted.
        ```json
            {
                "codeName":"roc",
                "name":"Real Time Online Chat",
                "description":"Real Time Online Chat is funny!"
            }
        ```


    ##### GET:
    Get all service catalogs
    ### Request:
        ```bash
            #bash
            curl \\
                 --request GET                                                                  \\
                 --header "Content-Type: application/json"                                      \\
                 --header "AUTHORIZATION: sdfjskdjhsrk3hfksejhfksefhskefhskeh12123kjhkasdhaıs"  \\
                 https://api_baseurl/api/v1/services
        ```

        ```python
            #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "sdfjskdjhsrk3hfksejhfksefhskefhskeh12123kjhkasdhaıs"
                        }
            req = requests.get("https://api_baseurl/api/v1/services",
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
                      "name": "Real Time Online Chat",
                      "description": "Real Time Online Chat is funny!",
                      "codeName": "roc"
                    }
                  ]
                }

        ```

    """
    serializer = ServiceCatalogSerializer()

    def __repr__(self):
        return "Service Catalog Create and List"

    def resource_name(self):
        return "ServiceCatalogResource"

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def list(self, params, meta, **kwargs):
        return self.db.filter(model=ServiceCatalog)

    @require_roles(roles=[ERoles.manager])  # todo: must be root on production
    def create(self, params, meta, **kwargs):
        validated = kwargs['validated']
        service_catalog = ServiceCatalog(code_name=validated['code_name'], name=validated['name'],
                                         description=validated['description'])
        self.db.session.add(service_catalog)
        return service_catalog

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class ServiceEventResource(SaasBase, ListCreateAPI):

    allow_in_public_doc = False

    serializer = ServiceEventSerializer()

    def __repr__(self):
        return "Service Event Resource"

    def resource_name(self):
        return "ServiceEventResource"

    def create(self, params, meta, **kwargs):
        validated = kwargs['validated']
        data = validated['service_data']

        service_item_used_event = ["post_message", "post_push_message"]

        for key, value in data.items():
            """
            message format = "project_id__service_code__service_event" --->  "2398472938udsa987__roc__create_channel"
            message[0]:project_id           --> 2398472938udsa987
            message[1]:service_catalog_code --> roc
            message[2]:service_event        --> create_channel
            """
            message = key.split('__')
            service = self.db.get_service(message[0], message[1])
            service_event = ServiceEvent(name=message[2], service_id=service.id, amount=value)
            if message[2] in service_item_used_event:
                service.item_used = Service.item_used + value
            self.db.session.add(service_event)
        return {}

    def list(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

