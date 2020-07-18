from zopsm.lib.log_handler import zlogger

from zopsm.lib.settings import CACHE_CHANNELS
from zopsm.lib.settings import CACHE_CHANNEL_EXPIRE
from zopsm.lib.settings import CACHE_CHANNEL_MANAGERS
from zopsm.lib.settings import CACHE_CHANNEL_BANNED_SUBSCRIBERS
from zopsm.lib.settings import CACHE_CHANNEL_INVITEES
from zopsm.lib.settings import CACHE_CHANNEL_JOIN_REQUESTS
from zopsm.lib.settings import CACHE_CHANNEL_SUBSCRIBERS
from zopsm.lib.settings import CACHE_CHANNEL_OWNERS
from zopsm.lib.cache.cache import Cache


class ChannelCache(Cache):
    """
    Cache object for Channel.
    """

    def __init__(self, project, service, channel, rpc_client=None):
        super().__init__(project, service, channel, "channel", rpc_client)
        self.expire = CACHE_CHANNEL_EXPIRE
        self.cache_keys = {
            "channel": CACHE_CHANNELS.format(
                project_id=self.project,
                service=self.service,
                channel_id=self.object_id),
            "banned_subscribers": CACHE_CHANNEL_BANNED_SUBSCRIBERS.format(
                project_id=self.project,
                service=self.service,
                channel_id=self.object_id),
            "invitees": CACHE_CHANNEL_INVITEES.format(
                project_id=self.project,
                service=self.service,
                channel_id=self.object_id),
            "join_requests": CACHE_CHANNEL_JOIN_REQUESTS.format(
                project_id=self.project,
                service=self.service,
                channel_id=self.object_id),
            "owner": CACHE_CHANNEL_OWNERS.format(
                project_id=self.project,
                service=self.service,
                channel_id=self.object_id),
            "managers": CACHE_CHANNEL_MANAGERS.format(
                project_id=self.project,
                service=self.service,
                channel_id=self.object_id),
            "subscribers": CACHE_CHANNEL_SUBSCRIBERS.format(
                project_id=self.project,
                service=self.service,
                channel_id=self.object_id),
        }

    def get(self, default=None):
        """

        Args:
            default(object): the default return value if channel does not exist in cache

        Returns:
            dict: channel object dict in following form

            .. code-block:: python
                channel = {
                    "id": "3c44c47cf9bf47948d10733ccb6448c9",
                    "creationTime": "2017-08-20T08:54:56.750Z00:00",
                    "lastUpdateTime": "2017-08-20T08:54:56.750Z00:00",
                    "isDeleted": False,
                    "isActive": True,
                    "name": "CENG-101 Introduction to Programming",
                    "description": "Channel for the announcements of class CENG-101",
                    "type": "public-announcement",
                    "subscribers": [
                        "3338423fefdf44029586679981d92ffd",
                        "31a80814cd274828bfabae9a712411b3",
                        "7f4db9a8070a4f4884839b8dbc2ef774"
                    ],
                    "lastMessage": {
                        "text": "",
                        "sender": "bb1c30ab18aa43359e4cf420876f7d23",
                        "date": "2017-08-20T08:54:56.750Z00:00"
                    },
                    "owners": [
                        "bb1c30ab18aa43359e4cf420876f7d23"
                    ],
                    "managers": [
                        "bb1c30ab18aa43359e4cf420876f7d23",
                        "d0bbe44040314b8aa2cf4356fa851d1a",
                        "bf845d32818741c38575345d9d7e1f28"
                    ],
                    "invitees": [],
                    "joinRequests": [],
                    "bannedSubscribers": []
                }
        """
        if not self.cache.exists(self.cache_keys['channel']):
            return default

        # todo Evolve to the pipelined version of this code when it is implemented.
        channel = {}
        channel_obj_byte = self.cache.hgetall(self.cache_keys['channel'])
        for k, v in channel_obj_byte.items():
            if k.decode() in ['is_deleted', 'is_active']:
                if v.decode() == '1':
                    value = True
                else:
                    value = False
            else:
                value = v.decode()
            channel.update(**{k.decode(): value})

        # read channel's banned subscribers
        channel['banned_subscribers'] = self.set_to_list(
            self.cache.smembers(self.cache_keys['banned_subscribers']))

        # read channel's invitees
        channel['invitees'] = self.set_to_list(self.cache.smembers(self.cache_keys['invitees']))

        # read channel's join requests
        channel['join_requests'] = self.set_to_list(
            self.cache.smembers(self.cache_keys['join_requests']))

        # read channel's owners
        channel['owner'] = self.set_to_list(self.cache.smembers(self.cache_keys['owner']))

        # read channel's managers
        channel['managers'] = self.set_to_list(self.cache.smembers(self.cache_keys['managers']))

        # read channel's subscribers
        channel['subscribers'] = self.set_to_list(self.cache.smembers(self.cache_keys['subscribers']))

        for v in self.cache_keys.values():
            self.cache.expire(v, self.expire)

        return channel

    def set(self, data):
        """
        Args:
            data(dict): riak object data form of channel object

        Returns:
            dict: channel object dict as in the same form of the get method's docs.
        """
        # todo Evolve to the pipelined version of this code when it is implemented.
        self.delete()
        channel_obj = {
            "id": self.object_id,
            "name": data['name'],
            "description": data['description'],
            "type": data['type'],
            "creation_time": data['creation_time'],
            "last_update_time": data['last_update_time'],
            "is_deleted": data['is_deleted'],
            "is_active": data['is_active'],
        }

        # store channel object to redis as a hash map with string fields of it
        self.cache.hmset(self.cache_keys['channel'], channel_obj)
        self.cache.expire(self.cache_keys['channel'], self.expire)

        for k, v in self.cache_keys.items():
            if k != 'channel':
                channel_obj[k] = [value for value in data[k].keys()] if data[k] else []
                try:
                    if channel_obj[k]:
                        self.cache.sadd(v, *channel_obj[k])
                except ValueError as e:
                    zlogger.warning(
                        "An error occured while trying to add set:{v} to a value:{list_to_add}: "
                        "{err}".format(v=v, list_to_add=channel_obj[k], err=e))
                self.cache.expire(v, self.expire)

        return channel_obj

    def delete(self):
        # todo Evolve to the pipelined version of this code when it is implemented.
        for key in self.cache_keys.values():
            self.cache.delete(key)
