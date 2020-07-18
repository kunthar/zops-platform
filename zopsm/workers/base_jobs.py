# # -*-  coding: utf-8 -*-

from zopsm.lib.sd_riak import DEFAULT_BUCKET_TYPE
from zopsm.lib.settings import DATETIME_FORMAT
from zopsm.lib.log_handler import zlogger
from zopsm.lib.sexp_parser import SEXPParser
from pyrabbit2.http import HTTPError
from zopsm.lib.credis import ZRedis
from datetime import datetime
import hashlib
import json
import os


class BaseWorkerJobs(object):
    """
    Base worker jobs
    
    """

    # Note: Unresolved attribute references(riak_pb, cache etc.) are provided from extended
    # classes(MessageWorkerJobs, PushWorkerJobs)
    def __init__(self):
        self.first = "{0:0>20}".format("")
        self.last = "{0:9>20}".format("")

    def ping(self, **kwargs):
        return "PONG" if self.riak_pb.ping() else ""

    def get_obj(self, project_id, bucket_name, obj_id, bucket_type=DEFAULT_BUCKET_TYPE):
        """
        Gets obj from riak.

        Args:
            - project_id(str): project id
            - bucket_name (str): bucket name
            - obj_id (str): riak object key 

        Returns:
            - obj (obj): riak obj

        """
        bucket = self.get_bucket(project_id, bucket_name, bucket_type)
        obj = bucket.get(obj_id)

        if not obj.exists:
            zlogger.error("Object not found. Bucket name:{}, id:{}".format(bucket.name, obj_id))
            raise KeyError("Object Not Found, bucket:{}, key:{}".format(bucket.name, obj_id))

        return obj

    def get_obj_data(self, **kwargs):
        """
        Gets obj data from riak and delivers it to as RPC response.

        Args:
            **kwargs(dict):
                - project_id(str): project id to determine the bucket
                - bucket_name(str): bucket name
                - object_id(str): id of object whose data will be retrieved
        Returns:

        """

        obj = self.get_obj(project_id=kwargs['project_id'], bucket_name=kwargs['bucket_name'],
                           obj_id=kwargs['object_id'])

        return obj.data

    def add_key_to_data(self, project_id, bucket_name, key, bucket_type=DEFAULT_BUCKET_TYPE):
        """
        Adds obj's key to obj's data as 'id' key and returns.
        
        Args:
            - project_id(str): project id
            - bucket_name (str): bucket name
            - key (str): riak object key 

        Returns:
            - data (dict): obj's data with obj's key
        
        """
        data = self.get_obj(project_id, bucket_name, key, bucket_type).data
        data.update({'id': key})
        return data

    def get_bucket(self, project_id, bucket_name, bucket_type=DEFAULT_BUCKET_TYPE):
        """
        Adds project id to given bucket name.
        
        Ex: project_id: '12345'
            bucket_name = 'message'
            new_bucket_name = '12345_message'
            
        Args:
            - project_id(str): project id
            - bucket_name (str): bucket name

        Returns:
            - bucket name (dict): bucket name is created with project id.
        
        """
        bucket_name = "{}_{}".format(project_id, bucket_name)
        return self.riak_pb.bucket_type(bucket_type).bucket(bucket_name)

    def get_creation_info(self):
        """
        Finds currently time and is returned with other fields for new created object's data.
        
        """
        now = datetime.now().strftime(DATETIME_FORMAT)
        return {'creation_time': now,
                'last_update_time': now,
                'is_deleted': False,
                'is_active': True}

    @staticmethod
    def add_target_and_client_push_tag(tag, obj, **kwargs):
        """
        Adds a single tag to target or client's push tags and adds index.
        Operations according to tag_type (key, key-value, multi) and value_type(str, int, float)

        If value_type == float:
            convert to 2f pattern. ex: 24.2343432423 --> 24.23

        Float values are indexed by multiplying with 100 for acting like integers.

        Args:
            tag(obj): tag object
            obj(obj): target or client object
            **kwargs (dict): project_id, client_id, key, value
                - project_id: project_id
                - client_id: client which will be tagged with this tag
                - name: name of tag
                - value: value of tag for client or target

        """
        if "push_tags" not in obj.data:
            obj.data['push_tags'] = {}

        if tag.data['tag_type'] == 'key':
            obj.data['push_tags'][kwargs['name']] = ""
            obj.add_index('{}_tag_bin'.format(kwargs['name']), kwargs['project_id'])
            tag.data['possible_values'][kwargs['project_id']] = ""
            tag.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
            tag.store()
        else:
            if tag.data['tag_type'] == 'multi':
                obj.data['push_tags'].setdefault(kwargs['name'], {})[kwargs['value']] = ""
            else:
                obj.data['push_tags'][kwargs['name']] = kwargs['value']

            if tag.data['value_type'] == 'float':
                kwargs['value'] = round(float(kwargs['value']), 2)

            if tag.data['value_type'] == 'str':
                obj.add_index('{}_tag_bin'.format(kwargs['name']), kwargs['value'])

            else:
                val = kwargs['value'] if tag.data['value_type'] == 'int' else kwargs['value'] * 100
                obj.add_index('{}_tag_int'.format(kwargs['name']), int(val))

            key = kwargs['value'] * 100 if tag.data['value_type'] == 'float' else kwargs['value']
            tag.data['possible_values'][key] = ""
            tag.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
            tag.store()

        obj.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        obj.store()

    @staticmethod
    def delete_target_and_client_tag(tag, obj, **kwargs):
        """
        Removes a single tag from target or client's push tags and removes existing index.

        Args:
            tag(obj): tag object
            obj(obj): target or client object
            **kwargs (dict): project_id, client_id, key, value
                - project_id: project_id
                - name: name of tag
                - value: value of tag for client or target

        Returns:

        """
        end_index = 'bin' if tag.data['value_type'] == 'str' else 'int'
        tag_index_pattern = "{}_tag_{}".format(tag.data['name'], end_index)

        if tag.data['tag_type'] == 'multi' and kwargs['value']:
            del obj.data['push_tags'][kwargs['name']][kwargs['value']]
            if tag.data['value_type'] == 'float':
                kwargs['value'] = round(float(kwargs['value']), 2)
                kwargs['value'] = int(kwargs['value'] * 100)
            if tag.data['value_type'] == 'int':
                kwargs['value'] = int(kwargs['value'])
            obj.remove_index(tag_index_pattern, kwargs['value'])

        else:
            del obj.data['push_tags'][kwargs['name']]
            obj.remove_index(tag_index_pattern)

        obj.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        obj.store()

    def calculate_sets(self, residents, case, single_case_type, project_id):
        """
        Evaluates given sets according to relation, key type. Sets' all items are evaluated one by 
        one. Value({"key": "birth_year", "relation": "()", "value": "["1980","2010"]", "intention": 
        "target"})'s hash is used as redis key. If value's calculated results exist in cache, taken 
        from cache otherwise calculated and set to cache with hash key.

        Args:
            residents (dict):
                residents = {
                    "sets": {
                        "c": {"key": "birth_year", "relation": "()", "value": "["1980","2010"]",
                         "intention": "target"},
                        "d": {"key": "device", "relation": "=", "value": "apple", "intention": "client"},
                    },
            case (str): shows residents' intentions variety. If all of them are target or client,
                        case is 'single', both are exists, case is 'mix'.

            single_case_type(str): if case is single, shows it's target or client otherwise None.

            **kwargs (dict): project_id
                - project_id: project_id

        Returns:
            list: client ids

        """
        # target and client buckets are prepared
        buckets = {'target': self.get_bucket(project_id, 'target'),
                   'client': self.get_bucket(project_id, 'client')}

        redis_key_map = {}
        for key, val in residents['sets'].items():
            ids = []
            # for each value of sets (ex: {"key": "device", "relation": "=", "value": "apple",
            # "intention": "client"}) hash is taken.
            hash = hashlib.sha1(json.dumps(val).encode()).hexdigest()
            cache_key = "CalculateSet:{}:{}".format(project_id, hash)

            # If prepared result exists in this value, it is taken and continue for this value.
            if self.cache.exists(cache_key):
                redis_key_map[key] = cache_key
                continue

            # If not exist in cache. start, end key and type are found. For this example value(
            # {"key": "device", "relation": "=", "value": "apple", "intention": "client"}), these
            # values should be 'blue', None and bin(tag value type)
            (start, end), type = self.find_start_and_end_key(project_id, val)
            tag_index = "{}_tag_{}".format(val['key'], type)
            stream = buckets[val['intention']].stream_index(tag_index, start, end)

            for keys in stream:
                ids.extend(keys)

            if case == 'mix' and val['intention'] == 'target':
                ids = self.get_targets_client_ids(project_id, ids)

            if ids:
                self.cache.sadd(cache_key, *ids)
                self.cache.expire(cache_key, 3 * 60 * 60)
            redis_key_map[key] = cache_key

        sexp = SEXPParser(residents["sets"], residents["expression"], redis_key_map, self.cache)
        stack = sexp.expression_stack
        final_cache_key = sexp.evaluate_stack(stack[:])

        final_ids = []
        for member in self.cache.smembers(final_cache_key):
            member = member.decode()
            final_ids.append(member)

        if case == 'single' and single_case_type == 'target':
            final_ids = self.get_targets_client_ids(project_id, final_ids)

        return final_ids

    def get_targets_client_ids(self, project_id, target_ids):
        """
        Finds client ids of given target ids list. 

        Args:
            project_id (str): project id
            ids (list): target ids list

        Returns:
            list: client ids

        """
        client_ids = []
        for id in target_ids:
            try:
                target_obj = self.get_obj(project_id, 'target', id)
                client_ids.extend(target_obj.data['clients'].keys())
            except KeyError:
                zlogger.error("Invalid target id. Key error occured in get_targets_client_ids "
                              "method.Project id: {}, target_id: {}".format(project_id, id))
        return client_ids

    def group_by_device_type(self, client_ids, project_id):
        """
        Groups devices(tokens) according to device type.

        Args:
            client_ids (list): client ids list
            project_id (str): project id

        Returns:
            dict: grouped tokens by device type
                  example = {'ios': ['easd3323dasdsa', 'asdlasnld32ajsd'],
                             'android': ['dsamdlsad2934d', '234324k423n423k']}  

        """
        device_tokens = {}
        for client_id in client_ids:
            client = self.get_obj(project_id, 'client', client_id)
            device_tokens.setdefault(client.data['device_type'], []).append(client.data['token'])
        return device_tokens

    def find_start_and_end_key(self, project_id, val):
        """
        According to operation type, finds startkey and endkey to use in 2i index. For example, 
        "=" operation is used equality like color=blue. startkey should be blue and endkey should 
        be None. On the other hand, "()" operation refers to range like 1980<birth year<2005, min 
        and max values are came in val and set. For "<" and ">" operation, one value is given and 
        other value is found from tag's possible values. For example, if people who are less than 
        30 is wanted, end key is assigned to 30 and minimum value is found from tag's possible 
        values, let's say if it's 12, for this scenario, returns (12,30) tuple.

        Args:
            **kwargs (dict): project_id, val
                - project_id(str): project_id
                - val(dict): segment's residents' sets

        Returns:
            tuple: (startkey, endkey)

        """
        obj = self.get_obj(project_id, 'tag', "{}_{}".format(project_id, val['key']))
        pos_val = obj.data['possible_values'].keys()

        operations = {
            "=": (val['value'], None),
            "<": (min(pos_val), val['value']),
            ">": (val['value'], max(pos_val)),
            "()": tuple(val['value'])
        }

        return operations[val['relation']], 'bin' if obj.data['value_type'] == 'str' else 'int'

    def get_queues(self, subscriber_id):
        """
        Get subscriber's queues from cache and checks change, if any change about subscriber's 
        queues, cache record is deleted and updated queue info is set to cache.

        Args:
            - subscriber_id (str): Subscriber id

        Returns:
            - active_queues (list): User's active queues list

        """
        is_change = False
        active_queues = []

        cache_key = 'QueueList:{}'.format(subscriber_id)
        queues = self.cache.smembers(cache_key)

        for queue in queues:
            try:
                self.rabbit_cl.get_queue('zopsm', queue.decode())
                active_queues.append(queue.decode())
            except HTTPError as exc:
                zlogger.error("An error occurred: {}".format(exc))
                is_change = True

        if is_change:
            self.cache.delete(cache_key)
            self.cache.sadd(cache_key, *active_queues)

        return active_queues

    def bindings_operation(self, operation, subscriber_id, route_key):
        """
        According to given operation(create binding or delete binding), new bindings are created or 
        existing bindings are removed.

        Args:
            - operation (str): 'create_binding' or 'delete_binding'
            - subscriber_id (str): riak subscriber object key 

        Returns:

        """
        queues = self.get_queues(subscriber_id)
        for queue in queues:
            try:
                getattr(self.rabbit_cl, operation)('zopsm', 'messages', queue, route_key)
            except HTTPError as exc:
                zlogger.error("An error occur on bindings_operation method inside BaseWorkerJobs. "
                              "Exc: {}".format(exc))

    def update_instances(self, riak_pb, rabbit_cl, redis_master):
        """
        Updated riak, rabbit and redis clients are set to wanted instance(PushWorker or 
        MessagingWorker)
        
        Args:
            kwargs (dict):
                - riak_pb(obj): riak client obj
                - rabbit_cl (obj): rabbit_ client obj
                - redis_master (str): redis master ip address


        """
        from zopsm.lib.sd_redis import redis_db_pw

        cache = ZRedis(host=redis_master,
                       password=redis_db_pw,
                       db=os.getenv('REDIS_DB'))

        self['riak_pb', 'rabbit_cl', 'cache'] = [riak_pb, rabbit_cl, cache]
