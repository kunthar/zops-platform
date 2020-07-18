from falcon import HTTPBadRequest, HTTPMethodNotAllowed
from zopsm.lib.rest.fields import ZopsStringField, ZopsAlphaNumericStringField
from zopsm.lib.rest.parameters import ZopsBooleanParam
from zopsm.lib.rest.serializers import ZopsBaseDBSerializer
from zopsm.roc.validators import invite_approve_validator

from zopsm.lib.rest.custom import ZopsRetrieveUpdateDeleteApi, \
    ZopsContinuatedListCreateApi

from zopsm.lib.cache.subscriber_cache import SubscriberCache


class ContactRequestSerializer(ZopsBaseDBSerializer):
    id = ZopsAlphaNumericStringField("Unique identifier of contact request", read_only=True)
    inviter = ZopsAlphaNumericStringField("User id of subscriber who sends the contact request",
                                          read_only=True)
    invitee = ZopsAlphaNumericStringField("User id of subscriber to be a contact")
    contactRequestMessage = ZopsStringField("Contact request message",
                                            source='message')
    approve = ZopsStringField("approved, rejected, not_evaluated",
                              validators=[invite_approve_validator], write_only=True)


class ContactRequest(ZopsRetrieveUpdateDeleteApi):
    """
    Allows to accept or reject a contact request with given id.

    ### Code Examples:
    #### PUT:
    Accepts or rejects a contact request.

    ##### Request:
    Accepts the contact request.
    ```bash

    curl \\
         --request PUT \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         --data-binary "{                                                                   \\
                \"invitee\": null,   \\
                \"contactRequestMessage\": null,   \\
                \"approve\": \"approved\"   \\
            }" \\
         https://api_baseurl/v1/roc/contact-requests/13b84fad901f4d0eae703069b21d3ef2
    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    payload = {
        "invitee": null,
        "contactRequestMessage": null,
        "approve": "approved",
    }

    req = requests.put("https://api_baseurl/v1/roc/contact-requests/13b84fad901f4d0eae703069b21d3ef2",
                                headers=header, data=json.dumps(payload))

    ```

    Rejects the contact request.
    ```bash

    curl \\
         --request PUT \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         --data-binary "{                                                                   \\
                \"invitee\": null,   \\
                \"contactRequestMessage\": null,   \\
                \"approve\": \"rejected\"   \\
            }" \\
         https://api_baseurl/v1/roc/contact-requests/13b84fad901f4d0eae703069b21d3ef2
    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    payload = {
        "invitee": null,
        "contactRequestMessage": null,
        "approve": "rejected",
    }

    req = requests.put("https://api_baseurl/v1/roc/contact-requests/13b84fad901f4d0eae703069b21d3ef2",
                                headers=header, data=json.dumps(payload))

    ```

    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "contactRequestMessage": null,
            "creationTime": null,
            "id": "13b84fad901f4d0eae703069b21d3ef2",
            "invitee": null,
            "inviter": null,
            "isActive": null,
            "isDeleted": null,
            "lastUpdateTime": null,
            "trackingId": "ceae507a-2641-4f57-9b1e-42e61ae2dd21"
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
    Cancels the contact request with given invite id.
    ##### Request:
    ```bash
    #bash
    curl \\
         --request DELETE \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/contact-requests/9c5295924ec84c329d963b971c175539

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.delete("https://api_baseurl/v1/roc/contact-requests/9c5295924ec84c329d963b971c175539",
                                headers=header)

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {},
        "meta": {
            "params": {
                "indent": 0
            }
        }
    }
    ```
    """

    serializer = ContactRequestSerializer()

    def __repr__(self):
        return "Contact Request Accept & Reject"

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def _check_update_request(validated):
        contact_user_id = validated.get('invitee')
        contact_request_message = validated.get('message')
        approve_new = validated.get('approve')

        if any([contact_user_id, contact_request_message, not approve_new]):
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid body "
                      "parameter(s).",
                description="Only approve can be updated.")
        elif approve_new == "not_evaluated":
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid body "
                      "parameter(s).",
                description="Approve must be one of approved or rejected!")
        return approve_new

    def update(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        invite_id = kwargs.get('invite_id')
        self.check_resource_id(invite_id)
        body = {
            "project_id": project_id,
            "invite_id": invite_id,
            "approve": self._check_update_request(validated),
            "service": service,
            "subscriber_id": user_id,
        }

        rpc_params = self.rpc_client.rpc_call("accept_reject_contact_request", body, blocking=False)
        return {
            "id": rpc_params['invite_id'],
            "tracking_id": rpc_params['tracking_id'],
        }

    def retrieve(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def delete(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        invite_id = kwargs.get('invite_id')

        self.check_resource_id(invite_id)

        body = {
            "project_id": project_id,
            "invite_id": invite_id,
            "service": service,
            "subscriber_id": user_id,
            "type": "contact",
        }

        self.rpc_client.rpc_call("cancel_invite", body, blocking=True)
        return {}


class ContactRequestList(ZopsContinuatedListCreateApi):
    """
    Allows to create and list contact requests.

    ### Code Examples:
    #### GET:
    Allows to list contact requests of a subscriber that send to or sent by other subscribers with
    the help of `inviter` parameter. If `inviter` send as true, it is retrieved the contact requests
    that are sent by subscriber him/herself. Contact requests that are sent by other subscribers to
    subscriber who makes the request are retrieved otherwise. `inviter` is `false` by default.

    ##### Request:
    ```bash
    #bash
    curl \\
         --request GET \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/contact-requests

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.get("https://api_baseurl/v1/roc/contact-requests",
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
        "content": [
                {
                    "id": "dabbe5bf65fd4d1fae81f10cb80f7c3f",
                    "creationTime": "2017-08-20T08:54:56.750Z00:00",
                    "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                    "isDeleted": false,
                    "isActive": true,
                    "inviter": "ac7dc65a30fa4239be34441bb0d79ede",
                    "invitee": "9d9ad8f1a7ff434b9ca624ee12d470e4",
                    "contactRequestMessage": "Please, add me to your contact list."
                },
                {
                    "id": "3b9d1e98118d490da2d3844315e3529e",
                    "creationTime": "2017-08-20T08:54:56.750Z00:00",
                    "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                    "isDeleted": false,
                    "isActive": true,
                    "inviter": "1a8113efcc2f48ba9969da5676be2ce1",
                    "invitee": "9d9ad8f1a7ff434b9ca624ee12d470e4",
                    "contactRequestMessage": "It would be great to be in your contact list."
                },
                {
                    "id": "a1d4d2ade8914b3c9a63403014dde426",
                    "creationTime": "2017-08-20T08:54:56.750Z00:00",
                    "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                    "isDeleted": false,
                    "isActive": true,
                    "inviter": "c6b72c100b274229910ba8e180df7826",
                    "invitee": "9d9ad8f1a7ff434b9ca624ee12d470e4",
                    "contactRequestMessage": "What if I told you that I wanted to be in your contacts."
                },

        ]
    }
    ```
    OR
    ##### Request:
    ```bash
    #bash
    curl \\
         --request GET \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/contact-requests?inviter=true

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.get("https://api_baseurl/v1/roc/contact-requests?inviter=true",
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
        "content": [
                {
                    "id": "3bdbad5efd74419787eb78d3cd9b4251",
                    "creationTime": "2017-08-20T08:54:56.750Z00:00",
                    "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                    "isDeleted": false,
                    "isActive": true,
                    "inviter": "9d9ad8f1a7ff434b9ca624ee12d470e4",
                    "invitee": "1dd024ccfbec4eeba93bb7d248be5e2f",
                    "contactRequestMessage": "Please, add me to your contact list."
                },
                {
                    "id": "044bfd806fd3445bb5b9f4e20bc6b37c",
                    "creationTime": "2017-08-20T08:54:56.750Z00:00",
                    "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                    "isDeleted": false,
                    "isActive": true,
                    "inviter": "9d9ad8f1a7ff434b9ca624ee12d470e4",
                    "invitee": "ac636a86b97c445ea34909531b433784",
                    "contactRequestMessage": "It would be great to be in your contact list."
                },
                {
                    "id": "275ed6c7df0b4820a3228255fc4318f4",
                    "creationTime": "2017-08-20T08:54:56.750Z00:00",
                    "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                    "isDeleted": false,
                    "isActive": true,
                    "inviter": "9d9ad8f1a7ff434b9ca624ee12d470e4",
                    "invitee": "9528fb426ab148a7af16e1bed0f43fe3",
                    "contactRequestMessage": "What if I told you that I wanted to be in your contacts."
                },

        ]
    }
    ```

    #### POST:

    Creates contact request with given body.

    ##### Request:
    ```bash
    curl \\
         --request POST \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         --data-binary "{                                                                       \\
                \"invitee\": \"c1f091f2c8fb4199af2fa622a6a465a1\",   \\
                \"contactRequestMessage\": \"Hi there! It would be great to keep in touch with you from now on till the end.\",   \\
                \"approve\": \"not_evaluated\",   \\
         }" \\
         https://api_baseurl/v1/roc/contact-requests

    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    payload = {
        "invitee": "c1f091f2c8fb4199af2fa622a6a465a1",
        "contactRequestMessage": "Hi there! It would be great to keep in touch with you from now on till the end.",
        "approve": "not_evaluated",
    }


    req = requests.post("https://api_baseurl/v1/roc/contact-requests",
                                headers=header, data=json.dumps(payload))

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "contactRequestMessage": "Hi there! It would be great to keep in touch with you from now on till the end.",
            "creationTime": null,
            "id": null,
            "invitee": "c1f091f2c8fb4199af2fa622a6a465a1",
            "inviter": "fec33ce8ddd24718b8052ca553551351",
            "isActive": null,
            "isDeleted": null,
            "lastUpdateTime": null,
            "trackingId": "71e69d4f-24ad-4ee0-8bc3-7e9bd7472247"
        },
        "meta": {
            "params": {
                "indent": 0,
                "inviter": false
            }
        }
    }

    ```

    > Warning
    >
    > Error response of this request, if any, will be delivered via WebSocket connection with
    > `trackingId` obtained from the response.


    """

    serializer = ContactRequestSerializer()

    def __repr__(self):
        return "Contact Request Create & List"

    def __str__(self):
        return self.__repr__()

    inviter = ZopsBooleanParam("Asks for contact requests which are sent to current user by "
                               "default. if it is True, then it will ask for contact requests "
                               "which are sent by current user.", default="False")

    def check_create_request(self, user, contact_id):
        subscriber = SubscriberCache(user.get('project'), user.get('service'), user.get('user'),
                                     rpc_client=self.rpc_client).get_or_set()
        contacts = subscriber['contacts']
        subscriber_id = user.get('user')
        if not contact_id:
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request with missing body parameter(s).",
                description="Contact id cannot be null.")
        elif contact_id in contacts:
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request with invalid body parameter(s).",
                description="Invitee:{contact_id} is already in contacts of "
                            "subscriber:{subscriber_id}".format(contact_id=contact_id,
                                                                subscriber_id=subscriber_id)
            )

    def create(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')

        contact_id = validated.get('invitee')
        request_message = validated.get('message')

        self.check_create_request(user, contact_id)

        body = {
            "project_id": project_id,
            "inviter": user_id,
            "invitee": contact_id,
            "message": request_message,
            "service": service,
        }

        return self.rpc_client.rpc_call("create_contact_request", body, blocking=False)

    def _list(self, params, meta, **kwargs):
        return [self.serializer.to_representation(obj) for obj in self.list(params, meta, **kwargs)]

    def list(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        inviter = params.get('inviter')

        body = {
            "project_id": project_id,
            "subscriber_id": user_id,
            "request_type": "contact",
            "invite_type": "sent" if inviter else "incoming",
            "service": service,
        }

        return self.rpc_client.rpc_call("list_requests", body)

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

