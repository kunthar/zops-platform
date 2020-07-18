from falcon import HTTPMethodNotAllowed
from zopsm.lib.rest.fields import ZopsStringField
from zopsm.lib.rest.fields import ZopsDatetimeField
from zopsm.lib.rest.fields import ZopsAlphaNumericStringField
from zopsm.lib.rest.serializers import ZopsBaseDBSerializer
from zopsm.roc.validators import behavioral_status_validator
from zopsm.lib.cache.status_cache import StatusCache
from zopsm.lib.cache.subscriber_cache import SubscriberCache

from zopsm.lib.rest.custom import ZopsContinuatedListCreateApi


class StatusSerializer(ZopsBaseDBSerializer):
    subscriberId = ZopsAlphaNumericStringField("Unique identifier of subscriber whose status being "
                                               "retrieved", read_only=True, source='subscriber_id')
    lastActivityTime = ZopsDatetimeField("Time that subscriber last status update sent",
                                         source='last_activity_time')
    statusMessage = ZopsStringField("Status message, user defined status description "
                                    "e.g. **I am busy right now**", source='status_message')
    behavioralStatus = ZopsStringField("Status defines the subscriber is `online`, `idle`, or "
                                       "`offline`.", source='behavioral_status',
                                       validators=[behavioral_status_validator])
    statusIntentional = ZopsStringField(
        "Intentional status defined by subscriber itself. e.g. Busy", source='status_intentional')


class Status(ZopsContinuatedListCreateApi):
    """
    Allows to post subscriber's status and list its own status within statuses of its online
    contacts. If there is no information returned about a contact, it means that it is offline at
    that moment.

    > Warning
    >
    > Subscriber's own status is located in the first index in the response array.

    ### Code Examples:
    #### GET:
    ##### Request:
    ```bash
    #bash
    curl \\
         --request GET \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/status

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.get("https://api_baseurl/v1/roc/status",
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
                "subscriberId": "2daed34089a1497f8da46a38310329c0",
                "creationTime": "2017-08-20T08:54:56.750Z00:00",
                "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                "isDeleted": false,
                "isActive": true,
                "lastActivityTime": "2017-08-20T08:54:56.750Z00:00",
                "statusMessage": "Veni Vidi Vici",
                "behavioralStatus": "online",
                "statusIntentional": null,
            },
            {
                "subscriberId": "25e8b60b7636426a8f28f7a89d92df3a",
                "creationTime": "2017-08-20T08:54:56.750Z00:00",
                "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                "isDeleted": false,
                "isActive": true,
                "lastActivityTime": "2017-08-20T08:54:56.750Z00:00",
                "statusMessage": "Hey there I am using zopsm!",
                "behavioralStatus": "idle",
                "statusIntentional": "busy",
            },
            {
                "subscriberId": "c1e9f488d42b46f28d77c01714271c73",
                "creationTime": "2017-08-20T08:54:56.750Z00:00",
                "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                "isDeleted": false,
                "isActive": true,
                "lastActivityTime": "2017-08-20T08:54:56.750Z00:00",
                "statusMessage": "No pain no gain",
                "behavioralStatus": "online",
                "statusIntentional": null,
            },
            {
                "subscriberId": "eab2dbf529bc438bb27702c18a21844d",
                "creationTime": "2017-08-20T08:54:56.750Z00:00",
                "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                "isDeleted": false,
                "isActive": true,
                "lastActivityTime": "2017-08-20T08:54:56.750Z00:00",
                "statusMessage": "Remember, remember 5th of November",
                "behavioralStatus": "online",
                "statusIntentional": null,
            }
        ]
    }
    ```

    #### POST:
    Creates or updates a subscriber's status.
    ##### Request:
    ```bash
    curl \\
         --request POST \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         --data-binary "{                                                                       \\
                \"statusMessage\": \"Looking for a rainbow!\",   \\
                \"behavioralStatus\": \"online\",   \\
                \"statusIntentional\": null,   \\
                \"lastActivityTime\": \"2017-08-20T08:54:56.750Z00:00\"   \\
         }" \\
         https://api_baseurl/v1/roc/status

    ```


    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    payload = {
        "statusMessage": "Looking for a rainbow!",
        "behavioralStatus": "online",
        "statusIntentional": null,
        "lastActivityTime": "2017-08-20T08:54:56.750Z00:00",
    }


    req = requests.post("https://api_baseurl/v1/roc/status",
                                headers=header, data=json.dumps(payload))

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "behavioralStatus": "online",
            "creationTime": "2018-01-24T08:00:19.663036Z00:00",
            "isActive": true,
            "isDeleted": false,
            "lastActivityTime": "2017-08-20T08:54:56.750Z00:00",
            "lastUpdateTime": "2018-01-24T08:00:19.663036Z00:00",
            "statusIntentional": null,
            "statusMessage": "Looking for a rainbow!",
            "subscriberId": "ff82e16c2c7b4b1c82bb29cc70df5ce0",
            "trackingId": "0800c8ba-da12-4808-8c53-6f89ebe27d05"
        },
        "meta": {
            "params": {
                "indent": 0
            }
        }
    }

    ```

    ### Status Delivery

    Subscribers are responsible for sending their statuses within a 5 minutes period.
    If a significant change occured in subscriber's status, such as a change in the
    `behavioral status`, `intentional status`, or `status message`, online contacts
    of that subscriber must be notified. This notification sent via the **WebSocket**
    connection in following format:

    ```json
    {
        "type": "status_delivery",
        "data": {
            "subscriberId": "2daed34089a1497f8da46a38310329c0",
            "lastActivityTime": "2017-08-20T08:54:56.750Z00:00",
            "statusMessage": "Veni Vidi Vici",
            "behavioralStatus": "online",
            "statusIntentional": null,
        }
    }
    ```

    > This is the general form of messages coming through the WebSocket.

    **`type`**: Indicates the reason of occurrence for that message. Possible values are
    `status_delivery`, `channel_update`, `invite_actions`, and `message_delivery`.

    **`data`**: Up to date value of the status of subscriber.

    Erroneous form of the message is as follows:

    ```json
    {
        "type": "error",
        "trackingId": "EVENT_TRACKING_ID",
        "data": {
            "title": "TITLE",
            "description": "DESCRIPTION",
            "code": 400
        }
    }
    ```

    """

    serializer = StatusSerializer()

    def __repr__(self):
        return "Sending and Retrieving Status"

    def __str__(self):
        return self.__repr__()

    def _list(self, params, meta, **kwargs):
        return [self.serializer.to_representation(obj) for obj in self.list(params, meta, **kwargs)]

    def list(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')

        body = {
            "project_id": project_id,
            "subscriber_id": user_id,
            "service": service,
        }

        subscriber = SubscriberCache(project_id, service, user_id,
                                     rpc_client=self.rpc_client).get_or_set()

        contacts = subscriber['contacts']
        status = StatusCache(project_id, service, user_id, rpc_client=self.rpc_client).get()
        status_list = [status]

        for contact in contacts:
            contact_status = StatusCache(project_id, service, contact,
                                         rpc_client=self.rpc_client).get(body)

            # todo: For now status information only can be given for online subscribers.

            if contact_status:
                status_list.append(contact_status)

        # todo: Future improvement, offline subscriber's statuses can also be retrieved.
        # status_list.extend(self.rpc_client.rpc_call("get_status", body))
        return status_list

    def create(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')

        body = {
            "project_id": project_id,
            "subscriber_id": user_id,
            "service": service,
        }
        body.update(validated)

        status, worth_to_write_and_notify = StatusCache(project_id, service, user_id,
                                                        rpc_client=self.rpc_client).set(body)
        if worth_to_write_and_notify:
            status.update(self.rpc_client.rpc_call("set_status", body, blocking=False))

        return status

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


