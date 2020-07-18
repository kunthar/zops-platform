from falcon import HTTPMethodNotAllowed, HTTPBadRequest
from zopsm.lib.rest.fields import ZopsStringField, ZopsAlphaNumericStringField
from zopsm.lib.rest.serializers import ZopsBaseDBSerializer
from zopsm.lib.cache.channel_cache import ChannelCache
from zopsm.roc.validators import invite_approve_validator
from zopsm.lib.rest.parameters import ZopsAlphaNumericStringParam
from zopsm.lib.utility import generate_uuid

from zopsm.lib.rest.custom import ZopsRetrieveUpdateDeleteApi
from zopsm.lib.rest.custom import ZopsContinuatedListCreateApi


class InviteSerializer(ZopsBaseDBSerializer):
    id = ZopsAlphaNumericStringField("Unique identifier of invites", read_only=True)
    inviter = ZopsAlphaNumericStringField("Subscriber id of who send invitation", read_only=True)
    invitee = ZopsAlphaNumericStringField("Subscriber id of whose intended to be sent invitation")
    channel = ZopsAlphaNumericStringField("Channel to which subscriber is invited or made join "
                                          "request")
    inviteMessage = ZopsStringField("Invitation message", source="invite_message")
    approve = ZopsStringField("approved, rejected, not_evaluated",
                              validators=[invite_approve_validator])


class Invite(ZopsRetrieveUpdateDeleteApi):
    """
    Allows to retrieve and approve/reject channel invitations sent by channel managers or join
    requests to channel sent by candidate subscribers.

    > Warning
    >
    > Invitations will be deleted after they replied. Only the ones having `approve` as
    > `not_evaluated` are stored.

    ### Code Examples:
    #### GET:
    Retrieves the invite with given id.
    ##### Request:
    ```bash
    #bash
    curl \\
         --request GET \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/invites/a95f72cca07a4c1485dd220f0eea47b5

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.get("https://api_baseurl/v1/roc/invites/a95f72cca07a4c1485dd220f0eea47b5",
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
            "id": "a95f72cca07a4c1485dd220f0eea47b5",
            "creationTime": "2017-08-20T08:54:56.750Z00:00",
            "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
            "isDeleted": false,
            "isActive": true,
            "inviter": "fac95326b984405a973586358ffbc89f",
            "invitee": "b8188c7a56404630b69d8b04d2052b25",
            "channel": "e0803dce6e4c4e4a95b6021b85d4feb3",
            "inviteMessage": "Hi there!",
            "approve": "not_evaluated",
        }
    }
    ```

    #### PUT:
    ##### Request:
    Approved by subscriber:
    ```bash

    curl \\
         --request PUT \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         --data-binary "{                                                                   \\
                \"invitee\": null,   \\
                \"channel\": null,   \\
                \"inviteMessage\": null,   \\
                \"approve\": \"approved\",   \\
            }" \\
         https://api_baseurl/v1/roc/invites/bf5e5bd22e6b43e587f80b1906cc001c
    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    payload = {
        "invitee": null,
        "channel": null,
        "inviteMessage": null,
        "approve": "approved",
    }

    req = requests.put("https://api_baseurl/v1/roc/invites/bf5e5bd22e6b43e587f80b1906cc001c",
                                headers=header, data=json.dumps(payload))

    ```

    Rejected by channel manager:
    ```bash

    curl \\
         --request PUT \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         --data-binary "{                                                                   \\
                \"invitee\": null,   \\
                \"channel\": null,   \\
                \"inviteMessage\": null,   \\
                \"approve\": \"rejected\",   \\
            }" \\
         https://api_baseurl/v1/roc/invites/8148e7f765244df8916887a28d681972
    ```

    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    payload = {
        "invitee": null,
        "channel": null,
        "inviteMessage": null,
        "approve": "rejected",
    }

    req = requests.put("https://api_baseurl/v1/roc/invites/8148e7f765244df8916887a28d681972",
                                headers=header, data=json.dumps(payload))

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "approve": null,
            "channel": null,
            "creationTime": null,
            "id": "8148e7f765244df8916887a28d681972",
            "inviteMessage": null,
            "invitee": null,
            "inviter": null,
            "isActive": null,
            "isDeleted": null,
            "lastUpdateTime": null,
            "trackingId": "6b1d54cd-d141-4c9f-8ab2-c0c7d816db25"
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
    Cancels the invitation with given id.
    ##### Request:
    ```bash
    #bash
    curl \\
         --request DELETE \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/invites/0bfc91abb33e47bc9a682c2d3db5e11f

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.delete("https://api_baseurl/v1/roc/invites/0bfc91abb33e47bc9a682c2d3db5e11f",
                                headers=header)

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "meta": {
            "params": {
                "indent": 0
            }
        },
        "content": {}
    }
    ```

    """

    serializer = InviteSerializer()

    def __repr__(self):
        return "Invitation Accept & Reject & Cancel"

    def __str__(self):
        return self.__repr__()


    @staticmethod
    def check_update_request(validated):
        invitee = validated.get('invitee')
        channel = validated.get('channel')
        invite_message = validated.get('invite_message')
        approve = validated.get('approve')

        if any([invitee, channel, invite_message, not approve]):
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid body "
                      "parameter(s).",
                description="Only approve can be updated.")

    def update(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        invite_id = kwargs.get('invite_id')

        self.check_resource_id(invite_id)
        self.check_update_request(validated)

        body = {
            "project_id": project_id,
            "invite_id": invite_id,
            "approve": validated['approve'],
            "service": service,
            "subscriber_id": user_id,
        }

        rpc_params = self.rpc_client.rpc_call("evaluate_accept_reject_invite", body, blocking=False)
        return {
            "id": invite_id,
            "tracking_id": rpc_params['tracking_id'],
        }

    def retrieve(self, params, meta, **kwargs):
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
        }

        return self.rpc_client.rpc_call("get_invite", body)

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
            "type": "channel"
        }

        self.rpc_client.rpc_call("cancel_invite", body, blocking=True)


class InviteList(ZopsContinuatedListCreateApi):
    """
    Allows to create and list invites. Lists invites with given invites param.

    ### Code Examples:
    #### POST:
    Creates a new invite as a join request to a channel. Response include invite id.
    ##### Request:
    ```bash

    curl \\
         --request POST \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         --data-binary "{                                                                       \\
                \"invitee\": null,   \\
                \"channel\": \"d33796c820a1451c8d9a3502ba0297cc\",   \\
                \"inviteMessage\": \"I want to join this channel\",   \\
                \"approve\": null,   \\
         }" \\
         https://api_baseurl/v1/roc/invites

    ```


    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    payload = {
        "invitee": null,
        "channel": "d33796c820a1451c8d9a3502ba0297cc",
        "inviteMessage": "I want to join this channel",
        "approve": null,
    }


    req = requests.post("https://api_baseurl/v1/roc/invites",
                                headers=header, data=json.dumps(payload))

    ```

    Or creates a new invite as a channel invitation to a subscriber from channel's manager.

    ```bash
    curl \\
         --request POST \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         --data-binary "{                                                                       \\
                \"invitee\": \"5c0bdb34a19c4ee796400b8fea465600\",   \\
                \"channel\": \"0505f8e83f6042b1997c88313195cd9e\",   \\
                \"inviteMessage\": \"I want you to join our channel\",   \\
                \"approve\": null,   \\
         }" \\
         https://api_baseurl/v1/roc/invites

    ```


    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    payload = {
        "invitee": "5c0bdb34a19c4ee796400b8fea465600",
        "channel": "0505f8e83f6042b1997c88313195cd9e",
        "inviteMessage": "I want you to join our channel",
        "approve": null,
    }


    req = requests.post("https://api_baseurl/v1/roc/invites",
                                headers=header, data=json.dumps(payload))

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "approve": "not_evaluated",
            "channel": "0505f8e83f6042b1997c88313195cd9e",
            "creationTime": null,
            "id": "f102b329ca914fb9bfe311197584a027",
            "inviteMessage": "I want you to join our channel",
            "invitee": "5c0bdb34a19c4ee796400b8fea465600",
            "inviter": "7dbe31022135471aac20678e92fab726",
            "isActive": null,
            "isDeleted": null,
            "lastUpdateTime": null,
            "trackingId": "6441a6e1-dc89-4d6f-9aa2-f0f29c3e9577"
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


    #### GET:
    Lists the invites with given invite param.

    > Warning
    >
    > `invite` param is required and it can have multiple values.

    ##### Request:
    ```bash
    #bash
    curl \\
         --request GET \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/invites?invite=dc12ae5552cc4a6a810b33734bdee8d0&invite=3a8a04fd291740c297306bbe7d115b9a&invite=561cea02af2245bc9b2d001a6c3cf3db

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.get("https://api_baseurl/v1/roc/invites?invite=dc12ae5552cc4a6a810b33734bdee8d0&invite=3a8a04fd291740c297306bbe7d115b9a&invite=561cea02af2245bc9b2d001a6c3cf3db",
                                headers=header)

    ```
    ##### Response:
    200 OK.
    ```json
    {
        "meta": {
            "params": {
                "indent": 0,
            }
        },
        "content": [
            {
                "id": "dc12ae5552cc4a6a810b33734bdee8d0",
                "creationTime": "2017-08-20T08:54:56.750Z00:00",
                "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                "isDeleted": false,
                "isActive": true,
                "inviter": "76e40e3bdf6e41b29a9ed3a911a1ca34",
                "invitee": "dd0ccedf70944653ab513dec95af5b61",
                "channel": "ace58356ee474686a88b82f091b780de",
                "inviteMessage": "Hi there!",
                "approve": "not_evaluated",
            },
            {
                "id": "3a8a04fd291740c297306bbe7d115b9a",
                "creationTime": "2017-08-20T08:54:56.750Z00:00",
                "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                "isDeleted": false,
                "isActive": true,
                "inviter": "7364c4695dcc4d509055768820c7b876",
                "invitee": null,
                "channel": "8f7e1d5e80284bbda7f58c000fbb58fe",
                "inviteMessage": "Hello there!",
                "approve": "not_evaluated",
            },
            {
                "id": "561cea02af2245bc9b2d001a6c3cf3db",
                "creationTime": "2017-08-20T08:54:56.750Z00:00",
                "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                "isDeleted": false,
                "isActive": true,
                "inviter": "2a792e305ab94f978031251d40d8565b",
                "invitee": null,
                "channel": "1b9d31fbebb7454c803e71eab3aa529c",
                "inviteMessage": "Is there anybody out there!",
                "approve": "not_evaluated",
            }
        ]
    }
    ```

    """

    serializer = InviteSerializer()

    def __repr__(self):
        return "Invitation Create"

    def __str__(self):
        return self.__repr__()

    invite = ZopsAlphaNumericStringParam("Invite ids to be listed in details", many=True)

    def check_create_request(self, user, channel_id, subscriber_id):
        user_id = user.get('user')
        channel = ChannelCache(user.get('project'), user.get('service'), channel_id,
                               rpc_client=self.rpc_client).get_or_set()
        subscribers = channel['subscribers']
        managers = channel['managers']
        if all([subscriber_id, channel_id]) and user_id not in managers:
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid body "
                      "parameter(s).",
                description="User:{} is not allowed to invite to channel:{}".format(user_id,
                                                                                    channel_id))
        elif channel_id and not subscriber_id and user_id in subscribers:
            raise HTTPBadRequest(
                    title="Bad Request. Client sent a request which includes invalid body "
                          "parameter(s).",
                    description="Already subscribed to channel.")
        elif not channel_id:
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request with missing body parameter(s).",
                description="Asking or sending invitation to join must include channel id as body "
                            "parameter. If it is an invitation subscriber id is also required, it "
                            "must be null otherwise.")
        elif all([subscriber_id, channel_id]):
            return "channel-manager"
        elif channel_id and not subscriber_id:
            return "subscriber"

    def create(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')

        channel_id = validated.get('channel')
        invitee = validated.get('invitee')
        actor = self.check_create_request(user, channel_id, invitee)
        invite_id = generate_uuid()

        body = {
            "project_id": project_id,
            "inviter": user_id,
            "channel": channel_id,
            "invite_message": validated.get('invite_message'),
            "service": service,
            "invite_id": invite_id
        }

        rpc_params = {}
        if actor == "channel-manager":
            body['invitee'] = invitee
            rpc_params = self.rpc_client.rpc_call("create_invite_by_channel", body, blocking=False)
        elif actor == "subscriber":
            rpc_params = self.rpc_client.rpc_call("create_invite_by_subscriber", body,
                                                  blocking=False)
        return {
            "id": rpc_params.get('invite_id'),
            "inviter": rpc_params.get('inviter'),
            "invitee": invitee,
            "channel": channel_id,
            "invite_message": rpc_params.get('invite_message'),
            "approve": "not_evaluated",
            "tracking_id": rpc_params.get('tracking_id'),
        }

    def _list(self, params, meta, **kwargs):
        return [self.serializer.to_representation(obj) for obj in self.list(params, meta, **kwargs)]

    def list(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        invites = params.get('invite')

        body = {
            "project_id": project_id,
            "service": service,
            "subscriber_id": user_id,
            "invites": invites,
        }

        return self.rpc_client.rpc_call("list_invites_by_ids", body)

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())
