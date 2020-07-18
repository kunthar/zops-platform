from falcon import HTTPMethodNotAllowed, HTTP_ACCEPTED
from zopsm.lib.rest.serializers import ZopsBaseDBSerializer

from zopsm.lib.rest.custom import ZopsRetrieveUpdateDeleteApi

class ContactSerializer(ZopsBaseDBSerializer):
    pass


class Contact(ZopsRetrieveUpdateDeleteApi):
    """
    Allows to remove a contact from contact list.

    #### DELETE:
    Removes the contact with given id from contact list.
    ##### Request:
    ```bash
    #bash
    curl \\
         --request DELETE \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --header "Authorization: Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6" \\
         https://api_baseurl/v1/roc/contacts/c06d227d7f36477db80d76c3a5d643d4

    ```

    ```python
    # python
    import requests

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    req = requests.delete("https://api_baseurl/v1/roc/contacts/c06d227d7f36477db80d76c3a5d643d4",
                                headers=header)

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "content": {
            "trackingId": "178c700a-f01f-4db8-93d8-8060e51f38ff"
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

    ### Possible Errors
    - __Bad Request__: Probably it was made a request with invalid resource id.
    - __Object Not Found__: Probably you try to get, update or delete a non-existent resource.
    - __Method Not Allowed__: Probably it was made a request except DELETE or OPTIONS.

    """

    serializer = ContactSerializer()

    def __repr__(self):
        return "Contact Delete"

    def __str__(self):
        return self.__repr__()

    def delete(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        user_id = user.get('user')
        project_id = user.get('project')
        service = user.get('service')
        contact_id = kwargs.get('subscriber_id')

        self.check_resource_id(contact_id)
        body = {
            "project_id": project_id,
            "subscriber_id": user_id,
            "contact_id": contact_id,
            "service": service,
        }
        rpc_params = self.rpc_client.rpc_call("delete_contact", body, blocking=False)
        return {"trackingId": rpc_params['tracking_id']}

    def retrieve(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def update(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


