from datetime import datetime
from zopsm.lib.log_handler import zlogger
from zopsm.lib.cache.cache import Cache

from zopsm.lib.settings import CACHE_SUBSCRIBER_EXPIRE
from zopsm.lib.settings import CACHE_SUBSCRIBERS
from zopsm.lib.settings import CACHE_CONTACTS
from zopsm.lib.settings import CACHE_SUBSCRIBER_CHANNELS
from zopsm.lib.settings import CACHE_SUBSCRIBER_BANNED_CHANNELS
from zopsm.lib.settings import CACHE_SUBSCRIBER_BANNED_SUBSCRIBERS
from zopsm.lib.settings import CACHE_SUBSCRIBER_CHANNEL_INVITES
from zopsm.lib.settings import CACHE_SUBSCRIBER_CHANNEL_JOIN_REQUESTS
from zopsm.lib.settings import CACHE_SUBSCRIBER_CONTACT_REQUESTS_IN
from zopsm.lib.settings import CACHE_SUBSCRIBER_CONTACT_REQUESTS_OUT
from zopsm.lib.settings import CACHE_SUBSCRIBER_CHANNELS_DATA, CACHE_SUBSCRIBER_CONTACTS_DATA


class SubscriberCache(Cache):
    """
    Cache object for subscriber

    subscriber.data = {
        "id": subscriber_id,
        "last_status_message": "",

        "contacts": {},

        "channels": {},

        "banned_channels": {},
        "banned_subscribers": {},

        "channel_invites": {},
        "channel_join_requests": {},
        "contact_requests_in": {},
        "contact_requests_out": {},
    }

        id
        contacts
        channels
        bannedChannels -> source='banned_channels'
        bannedSubscribers -> source='banned_subscribers'
        lastStatusMessage -> source='last_status_message'

        channelInvites -> source='channel_invites'
        channelJoinRequests -> source='channel_join_requests'

        contactRequestsIn -> source='contact_requests_in'
        contactRequestsOut ->  source='contact_requests_out'

    """
    def __init__(self, project, service, subscriber, rpc_client=None):
        super().__init__(project, service, subscriber, "subscriber", rpc_client)
        self.expire = CACHE_SUBSCRIBER_EXPIRE
        self.cache_keys = {
            "subscriber": CACHE_SUBSCRIBERS.format(
                project_id=self.project,
                service=self.service,
                subscriber_id=self.object_id),
            "contacts": CACHE_CONTACTS.format(
                project_id=self.project,
                service=self.service,
                subscriber_id=self.object_id),
            "channels": CACHE_SUBSCRIBER_CHANNELS.format(
                project_id=self.project,
                service=self.service,
                subscriber_id=self.object_id),
            "banned_channels": CACHE_SUBSCRIBER_BANNED_CHANNELS.format(
                project_id=self.project,
                service=self.service,
                subscriber_id=self.object_id),
            "banned_subscribers": CACHE_SUBSCRIBER_BANNED_SUBSCRIBERS.format(
                project_id=self.project,
                service=self.service,
                subscriber_id=self.object_id),
            "channel_invites": CACHE_SUBSCRIBER_CHANNEL_INVITES.format(
                project_id=self.project,
                service=self.service,
                subscriber_id=self.object_id),
            "channel_join_requests": CACHE_SUBSCRIBER_CHANNEL_JOIN_REQUESTS.format(
                project_id=self.project,
                service=self.service,
                subscriber_id=self.object_id),
            "contact_requests_in": CACHE_SUBSCRIBER_CONTACT_REQUESTS_IN.format(
                project_id=self.project,
                service=self.service,
                subscriber_id=self.object_id),
            "contact_requests_out": CACHE_SUBSCRIBER_CONTACT_REQUESTS_OUT.format(
                project_id=self.project,
                service=self.service,
                subscriber_id=self.object_id),
        }

    def get(self, default=None):
        """

        Args:
            default: the default return value if subscriber does not exist in cache

        Returns:
            dict: subscriber object dict as follows:

                .. code-block:: python
                    subscriber = {
                        "id": "16effc7b7be64ce295464a1370a9a2db",
                        "creation_time": "2017-08-20T08:54:56.750Z00:00",
                        "last_update_time": "2017-08-20T08:54:56.750Z00:00",
                        "is_deleted": false,
                        "is_active": true,
                        "contacts": [
                            "203bce7b3f004d049bbbe06d49597727",
                            "d6b81ac5747249c79a09381ee9e25c0f",
                            "b607a35af40140dfb346e75e0b5f1e82"
                        ],
                        "channels": {
                            "f6bed083fc1d45758fb884f2c90a62f9": {
                                "lastReadMessageId": s1c81ac5747249c79a09381ee9e25c0b
                            },
                            "ca3ed083fc1d45758fb884f2c90a62f9": {
                                "lastReadMessageId": y1z12ad6747240c79a09381ee9e25c0b
                            }
                        },
                        "banned_channels": [
                            "cb0481040ff847368981a2628dfccd04"
                        ],
                        "banned_subscribers": [
                            "9ef946edb1584b0c98edef00cbb0a835"
                        ],
                        "last_status_message": "Hello world!",
                        "channelInvites": [
                            "2380d95edd294b7aa3970f97673cf6c3"
                        ],
                        "channel_join_requests": [
                            "379bba7e26ec4c39bff8c0f2a79462f8"
                        ],
                        "contact_requests_in": [
                            "b8c24273419d4cd4bd0768fe34385bf7"
                        ],
                        "contact_requests_out": [
                            "6d09ce39de754e08a47ba681aec685ae"
                        ]
                    }
        """
        if not self.cache.exists(self.cache_keys['subscriber']):
            return default

        # todo Evolve to the pipelined version of this code when it is implemented.
        subscriber = {}

        # Read subscriber object's id, last_status_message and db default fields as bytes
        # Converts them to strings. Some of the db default fields are booleans, they are converted
        # to booleans in here.
        subscriber_obj_byte = self.cache.hgetall(self.cache_keys['subscriber'])
        for k, v in subscriber_obj_byte.items():
            if k.decode() in ['is_deleted', 'is_active']:
                if v.decode() == '1':
                    value = True
                else:
                    value = False
            else:
                value = v.decode()
            subscriber.update(**{k.decode(): value})

        # read contacts of subscriber
        subscriber['contacts'] = {}
        subs_contact = self.cache.smembers(self.cache_keys['contacts'])
        for contact_id in subs_contact:
            decoded_contact_id = contact_id.decode()
            subscriber["contacts"][decoded_contact_id] = {}
            contact_cache_data_key = CACHE_SUBSCRIBER_CONTACTS_DATA.format(
                project_id=self.project,
                service=self.service,
                subscriber_id=self.object_id,
                contact_id=decoded_contact_id
            )
            contact_data = self.cache.hgetall(contact_cache_data_key)

            for key, value in contact_data.items():
                subscriber['contacts'][decoded_contact_id][key.decode()] = value.decode()

        # read channels of subscriber
        subscriber['channels'] = {}

        subs_channels = self.cache.smembers(self.cache_keys['channels'])
        for channel_id in subs_channels:
            decoded_channel_id = channel_id.decode()
            subscriber["channels"][decoded_channel_id] = {}
            channel_cache_data_key = CACHE_SUBSCRIBER_CHANNELS_DATA.format(
                project_id=self.project,
                service=self.service,
                subscriber_id=self.object_id,
                channel_id=decoded_channel_id
            )
            channel_data = self.cache.hgetall(channel_cache_data_key)

            for key, value in channel_data.items():
                subscriber['channels'][decoded_channel_id][key.decode()] = value.decode()

        # read banned channels of subscriber
        subscriber['banned_channels'] = self.set_to_list(
            self.cache.smembers(self.cache_keys['banned_channels']))

        # read banned subscribers of subscriber
        subscriber['banned_subscribers'] = self.set_to_list(
            self.cache.smembers(self.cache_keys['banned_subscribers']))

        # read channel invites of subscriber
        subscriber['channel_invites'] = self.set_to_list(
            self.cache.smembers(self.cache_keys['channel_invites']))

        # read channel join requests of subscriber
        subscriber['channel_join_requests'] = self.set_to_list(
            self.cache.smembers(self.cache_keys['channel_join_requests']))

        # read incoming contact requests of subscriber
        subscriber['contact_requests_in'] = self.set_to_list(
            self.cache.smembers(self.cache_keys['contact_requests_in']))

        # read sent contact requests of subscriber
        subscriber['contact_requests_out'] = self.set_to_list(
            self.cache.smembers(self.cache_keys['contact_requests_out']))

        # set expire time for all keys of subscriber
        for v in self.cache_keys.values():
            self.cache.expire(v, self.expire)

        return subscriber

    def set(self, data):
        """
        Args:
            data(dict): riak object data form of subscriber object

        Returns:
            dict: subscriber object dict as in the same form of the get method's docs.
        """
        # todo Evolve to the pipelined version of this code when it is implemented.
        self.delete()

        subscriber_obj = {
            "id": self.object_id,
            "last_status_message": data['last_status_message'],
            "creation_time": data['creation_time'],
            "last_update_time": data['last_update_time'],
            "is_deleted": data['is_deleted'],
            "is_active": data['is_active'],
        }

        # store subscriber object to redis as a hash map with string fields of it
        self.cache.hmset(self.cache_keys['subscriber'], subscriber_obj)
        self.cache.expire(self.cache_keys['subscriber'], self.expire)

        for k, v in self.cache_keys.items():
            if k not in ('subscriber', 'channels', 'contacts'):
                subscriber_obj[k] = [value for value in data[k].keys()] if data[k] else []
                try:
                    if subscriber_obj[k]:
                        self.cache.sadd(v, *subscriber_obj[k])
                except ValueError as e:
                    zlogger.warning(
                        "An error occured while trying to add set:{v} to a value:{list_to_add}: "
                        "{err}".format(v=v, list_to_add=subscriber_obj[k], err=e))
                self.cache.expire(v, self.expire)
            elif k == 'channels':
                subscriber_obj['channels'] = data[k]
                if data[k]:
                    self.cache.sadd(v, *data[k].keys())
                    self.cache.expire(v, self.expire)
                for channel_id, channel_data in data[k].items():
                    channel_cache_data_key = CACHE_SUBSCRIBER_CHANNELS_DATA.format(
                        project_id=self.project,
                        service=self.service,
                        subscriber_id=self.object_id,
                        channel_id=channel_id
                    )
                    if channel_data:
                        for key, value in channel_data.items():
                            self.cache.hset(channel_cache_data_key, key, value)
                        self.cache.expire(channel_cache_data_key, self.expire)
            elif k == 'contacts':
                subscriber_obj['contacts'] = data[k]
                if data[k]:
                    self.cache.sadd(v, *data[k].keys())
                    self.cache.expire(v, self.expire)
                for channel_id, channel_data in data[k].items():
                    contact_cache_data_key = CACHE_SUBSCRIBER_CONTACTS_DATA.format(
                        project_id=self.project,
                        service=self.service,
                        subscriber_id=self.object_id,
                        contact_id=channel_id
                    )
                    if channel_data:
                        for key, value in channel_data.items():
                            self.cache.hset(contact_cache_data_key, key, value)
                        self.cache.expire(contact_cache_data_key, self.expire)

        return subscriber_obj

    def delete(self):
        # todo Evolve to the pipelined version of this code when it is implemented.
        channel_ids = self.cache.smembers(self.cache_keys["channels"])
        for channel_id in channel_ids:
            channel_cache_data_key = CACHE_SUBSCRIBER_CHANNELS_DATA.format(
                project_id=self.project,
                service=self.service,
                subscriber_id=self.object_id,
                channel_id=channel_id.decode()
            )
            self.cache.delete(channel_cache_data_key)

        contact_ids = self.cache.smembers(self.cache_keys["contacts"])
        for contact_id in contact_ids:
            contact_cache_data_key = CACHE_SUBSCRIBER_CONTACTS_DATA.format(
                project_id=self.project,
                service=self.service,
                subscriber_id=self.object_id,
                contact_id=contact_id.decode()
            )
            self.cache.delete(contact_cache_data_key)

        for key in self.cache_keys.values():
            self.cache.delete(key)
