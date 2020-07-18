# -*- coding: utf-8 -*-

from falcon.errors import HTTPMethodNotAllowed
from falcon.errors import HTTPConflict, HTTPBadRequest, HTTPNotFound
from graceful.fields import StringField
from graceful.resources.generic import ListCreateAPI, RetrieveUpdateDeleteAPI
from zopsm.saas.auth import require_roles
from zopsm.saas.models import ERoles, Consumer, Project, ProjectConsumer, Service
from zopsm.lib.rest.http_errors import HTTPPaymentRequired
from zopsm.lib.rest.serializers import ZopsBaseSerializer
from zopsm.saas.resources.saas_base import SaasBase
from zopsm.saas.utility import generate_token
from zopsm.saas.utility import add_consumer_token, remove_consumer_token


class ConsumerSerializer(ZopsBaseSerializer):
    id = StringField("ID of consumer.", read_only=True)


class ProjectConsumerSerializer(ZopsBaseSerializer):
    consumerId = StringField("List of consumer_id's", source='consumer_id')


class ConsumerTokenSerializer(ZopsBaseSerializer):
    consumerId = StringField("Consumer ID", source='consumer_id')
    projectId = StringField("Project ID", source='project_id')
    serviceCatalogCode = StringField("Service Code", source='service_catalog_code')
    token = StringField("Refresh Token", read_only=True)


class ConsumerResource(SaasBase, ListCreateAPI):
    """
    Allows to create and list consumer

    ####### Code Example:

    #### POST:
      Creates a new consumer, returns consumer id
     ### Request:

       ```bash
           #bash
            curl \\
                 --request POST                                                    \\
                 --header "Content-Type: application/json"                         \\
                 --header "AUTHORIZATION: CI6ImYyMDBiYWNjZGVkNDQxM2E4MiX5I1qH83w"  \\
                 --body "{}"                                                       \\
                 https://api_baseurl/api/v1/consumers

       ```

       ```python
           #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "CI6ImYyMDBiYWNjZGVkNDQxM2E4MiX5I1qH83w"
                      }

            body = {}
            req = requests.post("https://api_baseurl/api/v1/consumers",
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
                "id": "f074d1b87c774ddfa685b224567b803d"
              }
            }
      ```

    #### GET:
      List consumers
     ### Request:
       ```bash
           #bash
            curl \\
                 --request GET                                                                  \\
                 --header "Content-Type: application/json"                                      \\
                 --header "AUTHORIZATION: sdfjskdjhsrk3hfksejhfksefhskefhskeh12123kjhkasdhaıs"  \\
                 https://api_baseurl/api/v1/consumers
       ```
       ```python
           #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "sdfjskdjhsrk3hfksejhfksefhskefhskeh12123kjhkasdhaıs"
                      }
            req = requests.get("https://api_baseurl/api/v1/consumers",
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
                  "id": "f074d1b87c774ddfa685b224567b803d"
                },
                {
                  "id": "1fcedd8e7ac345e8ba60db07ae4fb59a"
                },
                {
                  "id": "5af03d9fa2ed4f12950717f4d32bd679"
                }
              ]
            }
      ```
    """
    serializer = ConsumerSerializer()

    def __repr__(self):
        return "Consumer Create & List"

    def resource_name(self):
        return "ConsumerResource"

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def create(self, params, meta, **kwargs):
        consumer = Consumer(account_id=kwargs['token']['account_id'])
        self.db.session.add(consumer)
        return consumer

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def list(self, params, meta, **kwargs):
        return self.db.filter(model=Consumer, account_id=kwargs['token']['account_id'])

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class ProjectConsumerCreateResource(SaasBase, ListCreateAPI):
    """

    Allows to create attachment with project to consumer

    ####### Code Example:

    #### POST:
      Create a project consumer
     ### Request:

       ```bash
           #bash
            curl \\
                 --request POST                                                                 \\
                 --header "Content-Type: application/json"                                      \\
                 --header "AUTHORIZATION: sdfjskdjhsrk3hfksejhfksefhskefhskeh12123kjhkasdhaıs"  \\
                 --body "{                                                            \\
                            \"consumerId\": \"f074d1b87c774ddfa685b224567b803d\"      \\
                         }"                                                           \\
                 https://api_baseurl/api/v1/projects/{project_id}/consumers
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
                       "consumerId": "f074d1b87c774ddfa685b224567b803d"
                    }
            req = requests.post("https://api_baseurl/api/v1/projects/{project_id}/consumers",
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
                "consumerId": "f074d1b87c774ddfa685b224567b803d"
              }
            }

      ```
    """

    def __repr__(self):
        return "Project Consumer Create"

    def resource_name(self):
        return "ProjectConsumerCreateResource"

    serializer = ProjectConsumerSerializer()

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def create(self, params, meta, **kwargs):
        kwargs['consumer_id'] = kwargs['validated']['consumer_id']
        project = self.db.get(Project, _id=kwargs['project_id'])

        if not project:
            raise (
                HTTPNotFound(description="There is no such project  !")
            )
        if not project.is_user_limit_available():
            raise HTTPPaymentRequired(description="Please check your project user limit")
        consumer_exist = self.db.exists(model=Consumer, _id=kwargs['consumer_id'],
                                        account_id=kwargs['token']['account_id'])
        if not consumer_exist:
            raise (
                HTTPNotFound(description="There is  no such consumer !")
            )
        attached_consumer = self.db.get_attached_consumer(kwargs['consumer_id'], kwargs['project_id'])
        if attached_consumer:
            raise (
                HTTPConflict(description="These consumer already attached this project")
            )

        project.user_used = Project.user_used + 1
        project_consumer = ProjectConsumer(consumer_id=kwargs['consumer_id'], project_id=kwargs['project_id'])
        self.db.session.add(project_consumer)
        return {"consumer_id": kwargs['consumer_id']}

    def list(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class ProjectConsumerDeleteResource(SaasBase, RetrieveUpdateDeleteAPI):

    """

    Allows to delete attachment (between project and consumer)

    ####### Code Example:

    #### DELETE:
      Delete project consumer
     ### Request:

       ```bash
           #bash
            curl \\
                 --request DELETE                                                               \\
                 --header "Content-Type: application/json"                                      \\
                 --header "AUTHORIZATION: sdfjskdjhsrk3hfksejhfksefhskefhskeh12123kjhkasdhaıs"  \\
                 https://api_baseurl/api/v1/projects/$project_id/consumers/$consumer_id
       ```

       ```python
           #python
            import requests
            import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "sdfjskdjhsrk3hfksejhfksefhskefhskeh12123kjhkasdhaıs"
                      }
            req = requests.delete("https://api_baseurl/api/v1/projects/$project_id/consumers/{consumer_id}",
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

    def __repr__(self):
        return "Project Consumer Delete"

    def resource_name(self):
        return "ProjectConsumerDeleteResource"

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def delete(self, params, meta, **kwargs):
        project = self.db.get(Project, _id=kwargs['project_id'])

        if not project:
            raise HTTPNotFound(
                description="There is no such project  !")

        consumer_exist = self.db.exists(model=Consumer, _id=kwargs['consumer_id'],
                                        account_id=kwargs['token']['account_id'])
        if not consumer_exist:
            raise HTTPNotFound(
                description="There is no such consumer !")

        attached_consumer = self.db.get_attached_consumer(kwargs['consumer_id'], kwargs['project_id'])
        if not attached_consumer:
            raise HTTPNotFound(
                description="There is no such attachment")

        self.db.session.delete(attached_consumer)
        project.user_used = Project.user_used - 1

    def retrieve(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def update(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class ProjectConsumerBulkResource(SaasBase, RetrieveUpdateDeleteAPI):
    serializer = ProjectConsumerSerializer()

    def __repr__(self):
        return "ProjectConsumerBulkResource"

    def resource_name(self):
        return "ProjectConsumerBulkResource"

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def update(self, params, meta, **kwargs):
        # consumers = kwargs['validated']['consumer_id']
        # # todo : Bulk attaching consumers.
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def delete(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def retrieve(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class ConsumerTokenCreate(SaasBase, ListCreateAPI):

    """
    Allows to create consumer token

    ### Code Example:
    #### POST:
    #### Request:

    ```bash
        #bash
        curl \\
             --request POST                                                                 \\
             --header "Content-Type: application/json"                                      \\
             --header "AUTHORIZATION: sdfjskdjhsrk3hfksejhfksefhskefhskeh12123kjhkasdhaıs"  \\
             --body "{                                                      \\
                        \"consumerId\":\"$consumer1_id\",                   \\
                        \"projectId\":\"$project_id\",                      \\
                        \"serviceCatalogCode\":\"$service_catalog_code\"    \\
                    }"                                                      \\
             https://api_baseurl/api/v1/consumer-tokens

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
                       "consumerId":"$consumer1_id",
                       "projectId":"$project_id",
                       "serviceCatalogCode":"$service_catalog_code"
                    }
            req = requests.post("https://api_baseurl/api/v1/consumer-tokens,
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
                "consumerId": null,
                "projectId": null,
                "serviceCatalogCode": null,
                "token": "5b72837976e9e81409962c38ad07495c1b4884f7729381ebcaacf41f1c9452a7"
              }
            }

    ```

    """

    def __repr__(self):
        return "Consumer Token Create"

    def resource_name(self):
        return "ConsumerTokenCreate"

    serializer = ConsumerTokenSerializer()

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def create(self, params, meta, **kwargs):
        consumer_id = kwargs['validated']['consumer_id']
        service_catalog_code = kwargs['validated']['service_catalog_code']
        project_id = kwargs['validated']['project_id']
        account_id = kwargs['token']['account_id']

        service = self.db.get(model=Service,
                              account_id=account_id,
                              project_id=project_id,
                              service_catalog_code=service_catalog_code
                              )

        if not service:
            raise HTTPBadRequest(
                description="Please check your service parameters! "
                            "There is no service identified with your parameters.")
        elif not self.db.get_attached_consumer(consumer_id=consumer_id, project_id=project_id):
            raise HTTPBadRequest(
                description="There is no such consumer attached to specified project."
                            "Please check your parameters or try to attach consumer first!")
        elif not service.is_item_limit_available():
            raise HTTPPaymentRequired(description="Please check your service message limit")
        else:
            token = generate_token()
            add_consumer_token(account_id,
                               project_id,
                               service_catalog_code,
                               consumer_id,
                               token)

            return {"token": token}

    def list(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class ConsumerTokenDelete(SaasBase, RetrieveUpdateDeleteAPI):
    """
    Allows to delete consumer token

    ### Code Example:

    #### DELETE:
    #### Request:

    ```bash
        #bash
        curl \\
             --request DELETE                                                               \\
             --header \"Content-Type: application/json\"                                    \\
             --header \"AUTHORIZATION: sdfjskdjhsrk3hfksejhfksefhskefhskeh12123kjhkasdhaıs" \\
             https://api_baseurl/api/v1/consumer-tokens/{consumer_token}/projects/{project_id}/services/{service_catalog_code}

    ```

    ```python
        #python
        import requests
        import json

            header = {
                        "Content-Type": "application/json",
                        "AUTHORIZATION": "sdfjskdjhsrk3hfksejhfksefhskefhskeh12123kjhkasdhaıs"
                      }
            req = requests.delete("https://api_baseurl/api/v1/consumer-tokens/{consumer_token}/projects/{project_id}/services/{service_cagalog_code},
                                header=header, data=json.dumps(body))

    ```

    ### Response:
    201 Created.
    ```json

    ```

    """
    def __repr__(self):
        return "Consumer Token Delete"

    def resource_name(self):
        return "ConsumerTokenDelete"

    @require_roles(roles=[ERoles.admin, ERoles.developer])
    def delete(self, params, meta, **kwargs):
        remove_consumer_token(kwargs['project_id'], kwargs['service_catalog_code'], kwargs['token_id'])

    def update(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def retrieve(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())
