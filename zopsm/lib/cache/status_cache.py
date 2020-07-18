from zopsm.lib.settings import CACHE_ONLINE_SUBSCRIBERS
from zopsm.lib.settings import CACHE_IDLE_SUBSCRIBERS
from zopsm.lib.settings import CACHE_STATUS_EXPIRE
from zopsm.lib.settings import CACHE_STATUS

from zopsm.lib.cache.cache import Cache
from zopsm.lib.settings import DATETIME_FORMAT
from datetime import datetime


class StatusCache(Cache):
    """
    Cache object for Channel.
    """

    def __init__(self, project, service, status, rpc_client=None):
        super().__init__(project, service, status, "status", rpc_client)
        self.expire = CACHE_STATUS_EXPIRE
        self.online_subscribers = CACHE_ONLINE_SUBSCRIBERS.format(
                project_id=self.project,
                service=self.service,
            )
        self.idle_subscribers = CACHE_IDLE_SUBSCRIBERS.format(
                project_id=self.project,
                service=self.service,
            )

        self.status = CACHE_STATUS.format(
                project_id=self.project,
                service=self.service,
                subscriber_id=self.object_id,
            )

    def get(self, default=None):
        """

        Args:
            default(object): the default return value if status does not exist in cache

        Returns:
            dict: status object dict in following form

            .. code-block:: python
                status = {
                    "subscriber_id": "2daed34089a1497f8da46a38310329c0",
                    "creation_time": "2017-08-20T08:54:56.750Z00:00",
                    "last_update_time": "2017-08-20T08:54:56.750Z00:00",
                    "is_deleted": false,
                    "is_active": true,
                    "last_activity_time": "2017-08-20T08:54:56.750Z00:00",
                    "status_message": "Veni Vidi Vici",
                    "behavioral_status": "online",
                    "status_intentional": null,
                },
        """
        # todo Evolve to the pipelined version of this code when it is implemented.
        status = {}

        # todo: When redis keyspace notifications will be available, it will be activated.
        # if not self.cache.exists(self.status):
            # status['behavioral_status'] = "offline"
            # status.update(self.rpc())
            # return status

        status_obj_byte = self.cache.hgetall(self.status)
        for k, v in status_obj_byte.items():
            if k.decode() in ['is_deleted', 'is_active']:
                if v.decode() == '1':
                    value = True
                else:
                    value = False
            else:
                value = v.decode()
            status[k.decode()] = value
        return status

    def set(self, data):
        """
        Args:
            data(dict): riak object data form of status object
                - subscriber_id
                - last_activity_time
                - status_message
                - behavioral_status
                - status_intentional

        Returns:
            tuple(dict, bool, bool): status object dict as in the same form of the get method's docs,
                either True if the status is worth to write into riak and notify user's contacts or False otherwise.
        """
        # todo Evolve to the pipelined version of this code when it is implemented.
        worth_to_write_and_notify = True
        now = datetime.now().strftime(DATETIME_FORMAT)
        data.update(
            {
                "creation_time": now,
                "last_update_time": now,
                "is_deleted": False,
                "is_active": True,
            }
        )
        prev_status = {}
        prev_status_obj_byte = self.cache.hgetall(self.status)
        for k, v in prev_status_obj_byte.items():
            if k.decode() in ['is_deleted', 'is_active']:
                if v.decode() == '1':
                    value = True
                else:
                    value = False
            else:
                value = v.decode()
            prev_status[k.decode()] = value

        self.cache.delete(self.status)

        if data['behavioral_status'] != "offline":
            self.cache.hmset(self.status, data)
            if data['behavioral_status'] == "online":
                self.cache.sadd(self.online_subscribers, data['subscriber_id'])
                self.cache.srem(self.idle_subscribers, data['subscriber_id'])
            else:
                self.cache.sadd(self.idle_subscribers, data['subscriber_id'])
                self.cache.srem(self.online_subscribers, data['subscriber_id'])

            sm = data['status_message'] != prev_status.get('status_message')
            si = data['status_intentional'] != prev_status.get('status_intentional')
            bs = data['behavioral_status'] != prev_status.get('behavioral_status')
            worth_to_write_and_notify = sm or si or bs

        return data, worth_to_write_and_notify
