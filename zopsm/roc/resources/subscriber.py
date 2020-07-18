from falcon import HTTPMethodNotAllowed, HTTPBadRequest
from zopsm.lib.rest.serializers import ZopsBaseDBSerializer
from zopsm.lib.cache.channel_cache import ChannelCache
from zopsm.lib.rest.custom import ZopsRetrieveUpdateDeleteApi


class SubscriberSerializer(ZopsBaseDBSerializer):
    pass


class Subscriber(ZopsRetrieveUpdateDeleteApi):
    """
    Allows to unsubscribe from a channel or a subscriber from a channel.

    ### Code Examples:

    #### DELETE:
    ##### Request:
    ```bash
    #bash
    curl \\
         --request DELETE \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/channels/836db9d5d69c4a17bec612eb0111084d/subscribers/2269e3925561494cb927d4ceb7d43e5f

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.delete("https://api_baseurl/v1/roc/channels/836db9d5d69c4a17bec612eb0111084d/subscribers/2269e3925561494cb927d4ceb7d43e5f",
                                headers=header)

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "trackingId": "710044e9-c35e-4298-b880-78df8a49a2ef"
        },
        "meta": {
            "params": {
                "indent": 0
            }
        }
    }

    ```

    ### Possible Errors:
    - __Bad Request__: Probably it was made a request with invalid resource id.
    - __Object Not Found__: Probably you try to get, update or delete a non-existent resource.


    """

    serializer = SubscriberSerializer()

    def __repr__(self):
        return "Unsubscribe From a Channel or Unsubscribe a Subscriber From a Channel"

    def __str__(self):
        return self.__repr__()


    @staticmethod
    def _check_delete_request(user_id, channel_managers, subscriber_id):
        if not (user_id in channel_managers or user_id == subscriber_id):
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid parameter(s).",
                description="User not allowed to unsubscribe.")
        elif user_id in channel_managers:
            return "channel-manager"
        elif user_id == subscriber_id:
            return "subscriber"

    def delete(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')

        channel_id = kwargs.get('channel_id')
        subscriber_id = kwargs.get('subscriber_id')

        self.check_resource_id(channel_id)
        self.check_resource_id(subscriber_id)

        channel = ChannelCache(project_id, service, channel_id, self.rpc_client).get_or_set()
        managers = channel['managers']

        unsubscription_actor = self._check_delete_request(user_id, managers, subscriber_id)

        body = {
            "project_id": project_id,
            "service": service,
            "channel_id": channel_id,
            "subscriber_id": subscriber_id,
        }
        if unsubscription_actor == "channel-manager":
            rpc_params = self.rpc_client.rpc_call("unsubscribe_subscriber_by_channel", body,
                                                  blocking=False)
        else:
            rpc_params = self.rpc_client.rpc_call("unsubscribe_channel_by_subscriber", body,
                                                  blocking=False)
        return {"trackingId": rpc_params.get('tracking_id')}

    def retrieve(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def update(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())
