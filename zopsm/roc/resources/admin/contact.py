from falcon import HTTPBadRequest, HTTPMethodNotAllowed
from zopsm.lib.rest.fields import ZopsStringField, ZopsAlphaNumericStringField
from zopsm.lib.rest.fields import ZopsListOfAlphaNumericStringsField
from zopsm.lib.rest.serializers import ZopsBaseDBSerializer
from zopsm.roc.validators import subscribers_length_validator

from zopsm.lib.rest.custom import ZopsRetrieveUpdateDeleteApi, \
    ZopsContinuatedListCreateApi


class ContactSerializer(ZopsBaseDBSerializer):
    subscriber_id = ZopsAlphaNumericStringField("User id of subscriber to be contact given "
                                                "contact list")
    contactListToAdd = ZopsListOfAlphaNumericStringsField(
        "Subscriber id list to add to given subscriber's contact list",
        validators=[subscribers_length_validator], source="contact_list_to_add")


class AdminContactResource(ZopsContinuatedListCreateApi):
    serializer = ContactSerializer()

    def __repr__(self):
        return "Admin Contact Create Resource"

    def __str__(self):
        return self.__repr__()

    def create(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project_id')
        admin_id = user.get('admin_id')
        account_id = user.get('account_id')
        validated = kwargs.get("validated")

        body = {
            "project_id": project_id,
            "account_id": account_id,
            "admin_id": admin_id,
            "service": "roc",
            "contact_parameters": validated
        }

        rpc_params = self.rpc_client.rpc_call("add_contact_to_subscriber_as_admin", body, blocking=False)
        return {
            "subscriber_id": validated["subscriber_id"],
            "tracking_id": rpc_params['tracking_id'],
        }

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())
