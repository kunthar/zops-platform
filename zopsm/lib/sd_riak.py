import os
import riak
from zopsm.lib.sd_consul import consul_client
from riak.riak_object import RiakObject
from zopsm.lib.cache.channel_cache import ChannelCache
from zopsm.lib.cache.subscriber_cache import SubscriberCache
from riak.resolver import last_written_resolver
from zopsm.lib.log_handler import zlogger
from zopsm.lib.settings import WORKING_ENVIRONMENT

riak_pb = None
log_bucket = None

DEFAULT_BUCKET_TYPE = os.environ.get('MTA_RIAK_DEFAULT_BUCKET_TYPE', 'zopsm')
RABBIT_HOOK_BUCKET_TYPE = os.environ.get('MTA_RIAK_RABBIT_HOOK_BUCKET_TYPE', 'zopsm_rabbit_hook')

BUCKET_CACHE_MAP = {
    'channel': ChannelCache,
    'subscriber': SubscriberCache,
}


class ZRiakObject(RiakObject):
    """
    Riak Object wrapper for storing data to redis in each store to riak.
    """

    def get_cache_obj(self):
        return BUCKET_CACHE_MAP[self.usermeta.get('bucket_name')](
                self.usermeta.get('project_id'), self.usermeta.get('service'), self.key)

    def store(self, without_cache=False, **kwargs):
        """
        Stores objects by calling super().store() to riak.

        If the bucket is in the `BUCKET_CACHE_MAP` and `without_cache` is not explicitly passed as
        True, it also stores to the cache, does nothing otherwise.

        Args:

            without_cache (bool): Must be set explicitly as True if current object is not intended
            to be stored in cache although it usually does

            **kwargs (dict): riak object's store method's kwargs
        """
        super().store(**kwargs)
        # todo There should be a background job to store data to redis in the future

        # usermeta must alrady be updated with these properties at creation of the object
        if self.usermeta.get('bucket_name', None) in BUCKET_CACHE_MAP and not without_cache:
            cache_obj = self.get_cache_obj()
            cache_obj.set(self.data)

        return self

    def delete(self, **kwargs):
        """
        Deletes objects by calling super().delete() from riak.
        If the bucket is in the `BUCKET_CACHE_MAP`, it also deletes from the cache.
        Args:
            **kwargs:
        Returns:
        """
        if self.usermeta.get('bucket_name', None) in BUCKET_CACHE_MAP:
            cache_obj = self.get_cache_obj()
            cache_obj.delete()
        return super().delete(**kwargs)


riak.RiakObject = ZRiakObject


def watch_riak():
    cur_index = None
    global riak_pb
    global log_bucket
    while True:
        index, data = consul_client.catalog.service('riak', index=cur_index, wait='10m')
        if index != cur_index:
            cur_index = index
            RIAK_POOL = [
                {'host': node['ServiceAddress'],
                 'pb_port': 8087,
                 'http_port': 8098} for node in data]

            zlogger.info(f"Riak Pool Nodes are changed. New nodes are {RIAK_POOL}.")
            riak_pb = riak.RiakClient(nodes=RIAK_POOL)
            riak_pb.resolver = last_written_resolver
            log_bucket = riak_pb.bucket_type('{}_logs'.format(WORKING_ENVIRONMENT)).bucket(
                                                       '{}_log'.format(WORKING_ENVIRONMENT))

