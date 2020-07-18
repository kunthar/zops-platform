from falcon import HTTPBadRequest
from falcon import HTTPMethodNotAllowed

from zopsm.lib.rest.fields import ZopsAlphaNumericStringField
from zopsm.lib.rest.fields import ZopsStringField
from zopsm.lib.rest.fields import ZopsListOfAlphaNumericStringsField
from zopsm.lib.rest.serializers import ZopsBaseDBSerializer
from zopsm.lib.cache.channel_cache import ChannelCache
from zopsm.lib.rest.custom import ZopsContinuatedListCreateApi
from zopsm.lib.rest.custom import ZopsRetrieveUpdateDeleteApi
from zopsm.lib.utility import generate_uuid

from zopsm.roc.validators import subscribers_length_validator
from zopsm.roc.validators import manager_length_validator
from zopsm.roc.validators import channel_type_validator


class AdminChannelSerializer(ZopsBaseDBSerializer):
    id = ZopsAlphaNumericStringField("Unique identifier of channels", read_only=True)
    name = ZopsStringField("Name of channel")
    description = ZopsStringField("Short description of channel")
    channelType = ZopsStringField(
        "Type of channel e.g. `public`, `private`, `invisible`, `public-announcement`, "
        "`private-announcement`, and `invisible-announcement`",
        validators=[channel_type_validator], source="type")
    subscribers = ZopsListOfAlphaNumericStringsField("List of subscribers of channel")
    managers = ZopsListOfAlphaNumericStringsField("Subscriber(s) who can manage channel",
                                                  validators=[manager_length_validator])


class AdminChannelSubscriberSerializer(ZopsBaseDBSerializer):
    subscribers = ZopsListOfAlphaNumericStringsField("Subscribers to be added to the channel",
                                                     validators=[subscribers_length_validator])


class AdminChannelCreateResource(ZopsContinuatedListCreateApi):
    serializer = AdminChannelSerializer()

    def __repr__(self):
        return "Admin Channel List & Create"

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def _check_create_params(validated):
        success = [
            validated.get('name'),
            validated.get('type'),
        ]
        if not all(success):
            raise HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid body "
                      "parameter(s).",
                description="Channel must include all of 'name', and 'type'")
        return validated

    def create(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project_id')
        admin_id = user.get('admin_id')
        account_id = user.get('account_id')
        validated = kwargs.get("validated")

        channel_id = generate_uuid()
        self._check_create_params(validated)
        body = {
            "project_id": project_id,
            "account_id": account_id,
            "admin_id": admin_id,
            "service": "roc",
            "channel_id": channel_id,
            "channel_parameters": validated
        }

        rpc_params = self.rpc_client.rpc_call("create_channel_as_admin", body, blocking=False)
        return {
            "id": channel_id,
            "name": body['channel_parameters']['name'],
            "description": body['channel_parameters']['description'],
            "type": body['channel_parameters']['type'],
            "tracking_id": rpc_params['tracking_id'],
        }

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class AdminChannelResource(ZopsRetrieveUpdateDeleteApi):
    serializer = AdminChannelSerializer()

    def __repr__(self):
        return "Admin Channel Update & Delete & Retrieve"

    def __str__(self):
        return self.__repr__()

    def check_channel_existence(self, user, channel_id):
        channel = ChannelCache(user.get('project_id'), 'roc', channel_id,
                               rpc_client=self.rpc_client).get_or_set()
        if not channel:
            raise HTTPBadRequest(
                title="Bad Request. Channel:{channel} cannot be retrieved.".format(
                    channel=channel_id),
                description="Bad Request. Channel cannot be retrieved".format(channel_id))

    def update(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project_id')
        admin_id = user.get('admin_id')
        account_id = user.get('account_id')

        validated = kwargs.get("validated")
        channel_id = kwargs.get('channel_id')

        self.check_channel_existence(user, channel_id)

        body = {
            "project_id": project_id,
            "account_id": account_id,
            "admin_id": admin_id,
            "service": "roc",
            "channel_id": channel_id,
            "channel_parameters": validated
        }

        rpc_params = self.rpc_client.rpc_call("update_channel_as_admin", body, blocking=False)
        rpc_params.update(validated)
        rpc_params['id'] = channel_id
        return rpc_params

    def delete(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def retrieve(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class AdminChannelSubscribersCreateResource(ZopsContinuatedListCreateApi):
    serializer = AdminChannelSubscriberSerializer()

    def __repr__(self):
        return "Add Subscribers To Channel as Admin User"

    def __str__(self):
        return self.__repr__()

    def create(self, params, meta, **kwargs):
        user = kwargs.get('context').get('user')  # user dict
        project_id = user.get('project_id')
        admin_id = user.get('admin_id')
        account_id = user.get('account_id')
        validated = kwargs.get("validated")

        channel_id = kwargs.get('channel_id')
        subscribers = validated.get("subscribers")

        body = {
            "project_id": project_id,
            "account_id": account_id,
            "admin_id": admin_id,
            "service": "roc",
            "channel_id": channel_id,
            "subscribers": subscribers
        }

        rpc_params = self.rpc_client.rpc_call("add_subscribers_to_channel_as_admin", body,
                                              blocking=False)
        return {
            "subscribers": subscribers,
            "tracking_id": rpc_params['tracking_id'],
        }

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())
