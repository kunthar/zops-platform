import os
from zopsm.lib.credis import ZRedis
from zopsm.lib import sd_redis
from zopsm.lib.log_handler import zlogger

if os.getenv('REDIS_MASTER'):
    master = os.getenv('REDIS_MASTER')
else:
    sd_redis.watch_redis(single=True)
    master = sd_redis.redis_master

cache = ZRedis(host=master,
               password=sd_redis.redis_db_pw,
               db=os.getenv('REDIS_DB'))

zlogger.info(f"Connected to redis node: {master}")


class Cache(object):
    """
    Base cache object to implement specific cache object for each use case.

    """

    def __init__(self, project, service, object_id, bucket_name, rpc_client):
        self.cache = cache
        self.project = project
        self.service = service
        self.object_id = object_id
        self.bucket_name = bucket_name
        self.rpc_client = rpc_client

    def get(self, default=None):
        raise NotImplemented()

    def set(self, data):
        raise NotImplemented()

    def get_or_set(self, data=None):
        """
        Retrieves data of targeted object from cache if exists in it.
        Otherwise sets the given `data` to cache if any.
        If no `data` passed, it retrieves the data of channel from db via rpc.

        Args:
            data(dict): targeted object dict
        Returns:
            dict: targeted object dict
        """
        return self.get() or self.set(data=data or self.rpc())

    def delete(self):
        raise NotImplemented()

    def rpc(self):
        """
        Makes an rpc call to get raw data of object.

        Args:
            bucket_name(str):
            project_id(str):
            object_id(str):
            service(str):
        Returns:
            dict: returns riak_object.data for given object.
        """
        if not (self.bucket_name or self.project or self.object_id or self.service):
            zlogger.info("Invalid value for bucket_name, project_id, object_id or service.")
            raise ValueError("Invalid value for bucket_name, project_id, object_id or service.")
        params = {
            "bucket_name": self.bucket_name,
            "project_id": self.project,
            "object_id": self.object_id,
            "service": self.service,
        }
        return self.rpc_client.rpc_call("get_obj_data", params)

    def set_to_list(self, redis_set):
        return [a.decode() for a in list(redis_set)] if redis_set else []
