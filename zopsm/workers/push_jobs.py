# -*-  coding: utf-8 -*-

from zopsm.lib.settings import DATETIME_FORMAT
from zopsm.lib.log_handler import zlogger
from zopsm.workers.base_jobs import BaseWorkerJobs
from zopsm.workers.unified_push_sender import send_push_message
from datetime import datetime
from zopsm.lib.utility import generate_uuid
import time


class PushWorkerJobs(BaseWorkerJobs):
    """
    Worker jobs related with push messaging part.

    """

    def __setitem__(self, k, v):
        self.__dict__.update(zip(k, v))

    def post_push_acknowledgement(self, **kwargs):
        """
        Each client sends an acknowledgement message when they receive a push message.
        This acknowledgement must be saved to DeliveryInfo bucket.
    
        Args:
            **kwargs (dict): project_id, target_id, client_id, message_id:
                - project_id: project_id
                - target_id: alphanumeric string, represents the target of the push message
                - client_id: string, represents the target's device-application pair
                - message_id: alphanumeric string, represents the push message
    
        """
        client_bucket = self.get_bucket(kwargs['project_id'], 'client')
        message_bucket = self.get_bucket(kwargs['project_id'], 'push_message')

        client = client_bucket.get(kwargs['client_id'])
        message = message_bucket.get(kwargs['message_id'])

        if client.exists and message.exists:
            bucket = self.get_bucket(kwargs['project_id'], 'delivery_info')
            kwargs.update(self.get_creation_info())
            bucket.new(data=kwargs).store()
            zlogger.info("New delivery info record is created. Project id:{}, client id:{}".format(
                kwargs['project_id'], kwargs['client_id'])
            )

    def get_client(self, **kwargs):
        """
        Returns the client info as dict including clientId, token, appVersion, deviceType, language,
        country, osVersion, creationTime, lastUpdateTime, isDeleted, isActive.
    
        Args:
            **kwargs (dict): project_id, target_id, client_id:
                - project_id: project_id
                - target_id: id of user who wants to get the client information, possibly user 
                - client_id: id of the client whose information is desired
                of the client
    
        Returns:
            dict : client data
        """
        client = self.get_obj(kwargs['project_id'], 'client', kwargs['client_id'])

        if client.data['target_id'] != kwargs['target_id']:
            zlogger.error("Target id is not equal to wanted client's target. Project id:{}, Target "
                          "id:{}, client id:{}".format(kwargs['project_id'], kwargs['target_id'],
                                                       kwargs['client_id']))
            return {"error": {"code": -32004, "message": "Unauthorized Operation Error"}}

        return client.data

    def update_client(self, **kwargs):
        """
        Updates the client info with given values.
    
        Args:
            **kwargs (dict): project_id, client_id, target_id, validated_client:
                - project_id: project_id
                - client_id: id of client which is desired to be updated
                - target_id: id of user who wants to update the client information, possibly user
                 of the client
                - validated_client: dict of updated client information including clientId, token,
                 appVersion, deviceType, language, country, osVersion.
        Returns:
    
        """
        client = self.get_obj(kwargs['project_id'], 'client', kwargs['client_id'])

        if client.data['target_id'] != kwargs['target_id']:
            zlogger.error("Target id is not equal to wanted client's target. Project id:{}, Target "
                          "id:{}, client id:{}".format(kwargs['project_id'], kwargs['target_id'],
                                                       kwargs['client_id']))
            return {"error": {"code": -32004, "message": "Unauthorized Operation Error"}}

        client.data.update(kwargs['validated_client'])
        client.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        client.store()
        zlogger.info("Client data is updated. Project id:{}, "
                     "client id:{}".format(kwargs['project_id'], kwargs['client_id']))

    def delete_client(self, **kwargs):
        """
        Deletes the client with given id.
    
        Args:
            **kwargs (dict): project_id, client_id, target_id:
                - project_id: project_id
                - client_id: id of client which is desired to be deleted
                - target_id: id of user who wants to delete the client, possibly user of the client
    
        Returns:
    
        """
        client = self.get_obj(kwargs['project_id'], 'client', kwargs['client_id'])

        if client.data['target_id'] != kwargs['target_id']:
            zlogger.error("Target id is not equal to wanted client's target. Project id:{}, Target "
                          "id:{}, client id:{}".format(kwargs['project_id'], kwargs['target_id'],
                                                       kwargs['client_id']))
            return {"error": {"code": -32004, "message": "Unauthorized Operation Error"}}

        target = self.get_obj(kwargs['project_id'], 'target', client.data['target_id'])

        if kwargs['client_id'] not in target.data['clients']:
            zlogger.error("Client id doesn't exist in target's clients. Project id:{},"
                          "target id:{}, client id:{}".format(kwargs['project_id'],
                                                              kwargs['target_id'],
                                                              kwargs['client_id']))
            return {"error": {"code": -32006, "message": "Client id doesn't exist in target"}}

        del target.data['clients'][kwargs['client_id']]

        target.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        target.store()
        client.delete()
        zlogger.info("Client is deleted. Project id:{}, client id:{}".format(kwargs['project_id'],
                                                                             kwargs['client_id']))

    def list_clients(self, **kwargs):
        """
        Lists the clients of user with given target_id.
    
        Args:
            **kwargs (dict): project_id, target_id
                - project_id: project_id
                - target_id: id of target who wants to list his/her own clients
        Returns:
            (list) : list of client dicts, each including clientId, token, appVersion, deviceType,
            language, country, osVersion, creationTime, lastUpdateTime, isDeleted, isActive.
        """
        target = self.get_obj(kwargs['project_id'], 'target', kwargs['target_id'])
        clients = target.data['clients'].keys()

        return [self.add_key_to_data(kwargs['project_id'], 'client', cl_id) for cl_id in clients]

    def create_client(self, **kwargs):
        """
        Creates a new client with given target_id and validated_client.
    
        Args:
            **kwargs: project_id, target_id, validated_client
                - project_id: project_id
                - target_id: id of target who owns client
                - validated_client: dict of client information including clientId, token,
                appVersion, deviceType, language, country, osVersion.
    
        Returns:
        """
        # TODO: device_type's validity should be controlled before this method.
        client_bucket = self.get_bucket(kwargs['project_id'], 'client')
        target_bucket = self.get_bucket(kwargs['project_id'], 'target')

        kwargs['validated_client']['target_id'] = kwargs['target_id']
        kwargs['validated_client']['id'] = kwargs['client_id']
        kwargs['validated_client'].update(self.get_creation_info())
        client = client_bucket.get(kwargs['client_id'])

        if client.exists:
            # todo: let client know the new client id
            kwargs['validated_client']['id'] = generate_uuid()
            client = client_bucket.get(kwargs['validated_client']['id'])

        client.data = kwargs['validated_client']
        target = target_bucket.get(kwargs['target_id'])

        client.store()
        zlogger.info("Client is created. Project id:{}, target id:{}, client id:{}".format(
            kwargs['project_id'], kwargs['target_id'], client.key))

        if target.exists:
            target.data['clients'][client.key] = ""
            zlogger.info("Client: {} is added into Target Object . Project id:{}, target id:{}".format(
                client.key, kwargs['project_id'],  target.key))
        else:
            target.data = {'clients': {client.key: ""}}
            zlogger.info("Target is created and Client: {} is added. Project id:{}, target id:{}".format(
                client.key, kwargs['project_id'],  target.key))

        target.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        target.store()

    def get_push_message(self, **kwargs):
        """
        Retrieves a single message with given message_id to target with given target_id.
    
        *User must be allowed to see the message. So, user must be the sender of the message.
    
        Args:
            **kwargs (dict): project_id, target_id, message_id
                - project_id:
                - target_id:
                - message_id:
    
        Returns:
            dict : message dict including id, creationTime, lastUpdateTime, isDeleted, isActive,
            sender, title, body, type, language, icon, image, badge, audience
        """
        message = self.get_obj(kwargs['project_id'], 'push_message', kwargs['message_id'])
        if message.data['target_id'] != kwargs['target_id']:
            zlogger.error("Message's sender is not equal to target. Project id:{}, target id:{}, "
                          "message id:{}".format(kwargs['project_id'], kwargs['target_id'],
                                                 kwargs['message_id']))
            return {"error": {"code": -32004, "message": "Unauthorized Operation Error"}}
        return message.data

    def update_push_message(self, **kwargs):
        """
        Updates a message with given id.
    
        Args:
            **kwargs (dict): project_id, message_id, validated_message, target_id
                - project_id: project_id
                - message_id:
                - validated_message: dict of validated message including title, body, type,
                language, icon, image, badge.
                - target_id:
        Returns:
    
        """
        message = self.get_obj(kwargs['project_id'], 'push_message', kwargs['message_id'])
        if message.data['target_id'] != kwargs['target_id']:
            zlogger.error("Message's sender is not equal to target. Project id:{}, target id:{}, "
                          "message id:{}".format(kwargs['project_id'], kwargs['target_id'],
                                                 kwargs['message_id']))
            return {"error": {"code": -32004, "message": "Unauthorized Operation Error"}}
        #todo:if message type is 'ordinary' , message doesnot updated
        if message.data['audience']:
            if not kwargs['validated_message']['audience']:
                zlogger.error("Message audience field can not be null. Project id:{}, target id:{}, "
                              "message id:{}".format(kwargs['project_id'], kwargs['target_id'],
                                                     kwargs['message_id']))
                return {"error": {"code": -32006, "message": "Message audience field can not be null"}}
            else:
                kwargs['validated_message']['consumers'] = {}

        elif message.data['consumers']:
            if not kwargs['validated_message']['consumers']:
                zlogger.error("Message consumers field can not be null. Project id:{}, target id:{}, "
                              "message id:{}".format(kwargs['project_id'], kwargs['target_id'],
                                                     kwargs['message_id']))
                return {"error": {"code": -32006, "message": "Message consumers field can not be null"}}

        message.data.update(kwargs['validated_message'])
        message.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        message.store()
        zlogger.info("Message is updated. Project id:{}, message id:{}".format(
            kwargs['project_id'], kwargs['message_id']))

    def delete_push_message(self, **kwargs):
        """
        Deletes a message with given id if its type is scheduled or automated.
    
        Args:
            **kwargs (dict): project_id, message_id, target_id
                - project_id:
                - message_id:
                - target_id:
        Returns:
    
        """
        message = self.get_obj(kwargs['project_id'], 'push_message', kwargs['message_id'])
        if message.data['target_id'] != kwargs['target_id']:
            zlogger.error("Message's sender is not equal to target. Project id:{}, target id:{}, "
                          "message id:{}".format(kwargs['project_id'], kwargs['target_id'],
                                                 kwargs['message_id']))
            return {"error": {"code": -32004, "message": "Unauthorized Operation Error"}}
        message.delete()
        zlogger.info("Message is deleted. Project id:{}, message id:{}".format(
            kwargs['project_id'], kwargs['message_id']))

    def list_push_messages(self, **kwargs):
        """
        Lists push messages with given target_id, page and page_size parameter. Returns the list of
        messages.
    
        Args:
            **kwargs (dict): target_id, page_size, page
                - target_id
                - project_id:
                - page_size: number of messages must be sent in a single page
                - continuation(optional): continuation id
        Returns:
            (dict): continuation, results:
                - continuation(str or None):
    
        """
        target_id, project_id, buck_name = kwargs['target_id'], kwargs['project_id'], 'push_message'
        bucket = self.get_bucket(project_id, buck_name)

        params = {'max_results': kwargs['page_size']}
        if 'continuation' in kwargs:
            params['continuation'] = kwargs['continuation']

        first, last = '{}_{}'.format(target_id, self.first), '{}_{}'.format(target_id, self.last)
        message_data = bucket.get_index('push_message_bin', first, last, **params)

        continuation, results = message_data.continuation, message_data.results
        return {"continuation": continuation,
                "results": [self.add_key_to_data(project_id, buck_name, key) for key in results]}

    def post_push_message(self, **kwargs):
        """
        Creates a push message with given segment id.
    
        Segment id check must be performed. If it is OK, then segment's resident set must be
        retrieved and push operation performed according to the message's type.
    
        `audience` is a segment id, it is retrieved from db. its `residents` field in following
        form:
            residents = {
                "sets": {
                    "a": {"key": "color", "relation": "=", "value": "blue", "intention": "target"},
                    "b": {"key": "age", "relation": "<", "value": "55", "intention": "target"},
                    "c": {"key": "birth_year", "relation": "()", "value": "["1980","2010"]", 
                    "intention": "target"},
                    "d": {"key": "device", "relation": "=", "value": "apple", "intention": "client"},
                },
                "expression": "(a U b) - (c n d)"
            }
    
        Sets must be obtained from riak concurrently. For each set in the given residents object,
        there must be a worker that parses the given set definition, gets keys from riak by using
        2i, put it to the redis and map its set_key to the redis key.
        Examples:
             set: "a": {"key": "level", "relation": "=", "value": "10"}
             2i query: level_int, 10
             redis_key: Project:Example123:a
             redis_key_map: {"a": "Project:Example123:a"}
    
        Main worker sends redis keys of sets to sub-workers, so that they can put them to redis with
        expected keys.
    
        Main worker subscribes a redis pub/sub channel after sending jobs to the sub-workers. Each
        worker that finishes its job publishes a message to redis channel. Main worker counts the
        messages that are published to the channel and when it reach to the number of sets, starts
        the evaluation of the expression.
    
        For the evaluation of the expression a SEXPParser instance must be obtained.
            sexp = SEXPParser(residents["sets"], residents["expression"], redis_key_map, redis_instance)
            `sexp.expression_stack` gives the parsed expression stack
            evaluated_set_redis_key = sexp.evaluate_stack()  # this is the final redis key
            then, evaluate_stack method must be called to evaluate the stack.
        Args:
            **kwargs: project_id, target_id, validated_message
                - project_id
                - validated_message: dict of validated message including title, body, type,
                language, icon, image, badge, audience.
                - target_id: sender of the message
    
        Returns:
    
        """
        if kwargs['validated_message']['audience']:
            kwargs['validated_message']["consumers"] = []
            segment_id = kwargs['validated_message']['audience']
            segment = self.get_obj(kwargs['project_id'], 'segment', segment_id)
            residents = segment.data['residents']

            intentions = [val['intention'] for val in residents['sets'].values()]

            case = 'single' if len(set(intentions)) == 1 else 'mix'
            single_case_type = set(intentions).pop() if case == 'single' else None

            client_ids = self.calculate_sets(residents, case, single_case_type, kwargs['project_id'])
        else:
            consumers = kwargs['validated_message']['consumers']
            client_ids = self.get_targets_client_ids(kwargs['project_id'], consumers)

        bucket = self.get_bucket(kwargs['project_id'], 'push_message')
        message = bucket.get(kwargs['message_id'])

        if message.exists:
            kwargs['validated_message']['id'] = generate_uuid()
            message = bucket.get(kwargs['validated_message']['id'])

        kwargs['validated_message']['target_id'] = kwargs['target_id']
        message.data = kwargs['validated_message']

        formatted_time = format(time.time(), '.7f')
        timestamp = int(self.last) - int("".join(str(formatted_time).split('.')))
        message.add_index('push_message_bin', "{}_{}".format(kwargs['target_id'], timestamp))
        message.data.update(self.get_creation_info())
        message.store()

        self.send_push_message(kwargs['project_id'], kwargs['service'], client_ids, kwargs['validated_message'], message.key)

    def send_push_message(self, project_id, service, client_ids, validated_message, message_id):
        device_tokens = self.group_by_device_type(client_ids, project_id)
        for device_type, tokens in device_tokens.items():
            send_push_message(device_type, tokens, validated_message, project_id)
            zlogger.info(
                "Send Push Message. Project id:{}, message id:{}".format(
                    project_id, message_id),
                extra={
                    "project_id": project_id,
                    "service": service,
                    "purpose": "counter",
                })

    def get_push_segment(self, **kwargs):
        """
        Retrieves a push segment with given id.
    
        Args:
            **kwargs (dict): project_id, segment_id
                - project_id: project_id
                - segment_id: unique identifier of segment
    
        Returns:
            dict: segment object including segment_id, name, residents
    
        """
        segment = self.get_obj(kwargs['project_id'], 'segment', kwargs['segment_id'])
        return segment.data

    def update_push_segment(self, **kwargs):
        """
        Updates a push segment with given id.
    
        Args:
            **kwargs (dict): project_id, segment_id, name, residents
                - project_id: proejct_id
                - segment_id: unique identifier of segment
                - name (str): name of segment
                - residents (dict): object of expressions which represent the audience set of
                segment
    
        Returns:
    
        """
        segment = self.get_obj(kwargs['project_id'], 'segment', kwargs['segment_id'])
        segment.data.update({'name': kwargs['name'],
                             'residents': kwargs['residents']})
        segment.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        segment.store()
        zlogger.info("Segment is updated. Project id:{}, segment id:{}".format(
            kwargs['project_id'], kwargs['segment_id']))

    def delete_push_segment(self, **kwargs):
        """
        Deletes a push segment with given id.
    
        Args:
            **kwargs (dict): project_id, segment_id
                - project_id: project_id
                - segment_id: unique identifier of segment
    
        Returns:
    
        """
        segment = self.get_obj(kwargs['project_id'], 'segment', kwargs['segment_id'])
        segment.delete()
        zlogger.info("Segment is deleted. Project id:{}, segment id:{}".format(
            kwargs['project_id'], kwargs['segment_id']))

    def create_push_segment(self, project_id=None, **kwargs):
        """
        Creates a push segment with given args.
    
        Args:
            **kwargs (dict): project_id, name, residents
                - project_id: project_id
                - name (str): name of segment
                - residents (dict): object of expressions which represent the audience set of
                segment
        Returns:
    
        """
        project_id = project_id or kwargs['project_id']
        bucket = self.get_bucket(project_id, 'segment')
        segment = bucket.get(kwargs['segment_id'])

        if segment.exists:
            # todo: let client know the new segment id
            kwargs['segment_id'] = generate_uuid()
            segment = bucket.get(kwargs['segment_id'])

        segment.data = {'name': kwargs['name'], 'residents': kwargs['residents'], 'id': kwargs['segment_id']}
        segment.add_index('segment_bin', project_id)

        for val in kwargs['residents']['sets'].values():
            segment.add_index('tag_seg_bin', val['key'])

        segment.data.update(self.get_creation_info())
        segment.store()
        zlogger.info("New segment is created. Project id:{}, segment id:{}".format(
            project_id, segment.key))

    def list_push_segments(self, **kwargs):
        """
        Lists segments of target with given id.
    
        Args:
            **kwargs (dict): project_id, continuation, page_size
                - project_id: project_id
                - page_size: number of records in a single page
                - continuation: continuation key for take next page.
    
        Returns:
            list: list of segments
        """
        project_id = kwargs['project_id']
        bucket = self.get_bucket(project_id, 'segment')

        params = {'max_results': kwargs['page_size']}
        if 'continuation' in kwargs:
            params['continuation'] = kwargs['continuation']

        segment_data = bucket.get_index('segment_bin', kwargs['project_id'], **params)

        continuation, results = segment_data.continuation, segment_data.results
        return {"continuation": continuation,
                "results": [self.add_key_to_data(project_id, 'segment', key) for key in results]}

    def create_push_tag(self, **kwargs):
        """
        Creates a single tag with given id.
    
        Args:
            **kwargs (dict): project_id, name, tag_type, value_type
                - project_id: project id
                - name: name of tag
                - tag_type: tag type
                - value_type: value type
    
        Returns:
        """
        bucket = self.get_bucket(kwargs['project_id'], 'tag')

        tag_key = "{}_{}".format(kwargs['project_id'], kwargs['name'])
        if bucket.get(tag_key).exists:
            zlogger.error(" Tag to be saved is already exists. Project id:{}, tag name:{}".format(
                kwargs['project_id'], kwargs['name']))
            return {"error": {"code": -32005, "message": "Invalid value, tag is already exists."}}

        kwargs['possible_values'] = {}
        kwargs.update(self.get_creation_info())
        obj = bucket.new(data=kwargs)
        obj.add_index('tag_bin', kwargs['project_id'])
        obj.key = tag_key
        obj.store()
        zlogger.info("New push tag is created. Project id:{}, tag name:{}".format(
            kwargs['project_id'], kwargs['name']))

    def list_push_tags(self, **kwargs):
        """
        Lists all push tags according to given project id.
        Args:
            **kwargs (dict): project_id, target_id
                - project_id: project id
                - page_size: page size
                - continuation: (optional)
    
        Returns:
        """
        project_id = kwargs['project_id']
        bucket = self.get_bucket(project_id, 'tag')

        params = {'max_results': kwargs['page_size']}
        if 'continuation' in kwargs:
            params['continuation'] = kwargs['continuation']

        push_tags = bucket.get_index("tag_bin", project_id, **params)
        continuation, results = push_tags.continuation, push_tags.results
        return {"continuation": continuation,
                "results": [self.add_key_to_data(project_id, 'tag', key) for key in results]}

    def get_push_tag(self, **kwargs):
        """
        Gets a single push tag according to given tag_id and project_id.
    
        Args:
            **kwargs (dict): project_id, name
                - project_id: project id
                - name: name of tag
        Returns:
        """
        tag_key = "{}_{}".format(kwargs['project_id'], kwargs['tag_name'])
        tag = self.get_obj(kwargs['project_id'], 'tag', tag_key)
        del tag.data['possible_values']
        return tag.data

    def delete_push_tag(self, **kwargs):
        """
        Gets a single push tag according to given tag_id.
    
        Args:
            **kwargs (dict): project_id, name
                - project_id: project id
                - name: name of tag
    
        Returns:
        """
        project_id = kwargs['project_id']
        tag_name = kwargs['tag_name']
        tag = self.get_obj(kwargs['project_id'], 'tag', "{}_{}".format(project_id, tag_name))

        end_index = 'bin' if tag.data['value_type'] in ['str', None] else 'int'
        tag_index_pattern = "{}_{}_tag_{}".format(kwargs['project_id'], tag_name, end_index)
        if len(tag.data['possible_values'].keys()) != 0:
            min_val = min(tag.data['possible_values'].keys())
            max_val = max(tag.data['possible_values'].keys())

            tar_bucket = self.get_bucket(project_id, 'target')
            cl_bucket = self.get_bucket(project_id, 'client')

            tar_stream = tar_bucket.stream_index(tag_index_pattern, min_val, max_val)
            cl_stream = cl_bucket.stream_index(tag_index_pattern, min_val, max_val)

            for keys in tar_stream:
                for target_id in keys:
                    self.delete_push_target_tag(**{'target_id': target_id,
                                                   'name': tag_name})
            for keys in cl_stream:
                for client_id in keys:
                    self.delete_push_client_tag(**{'client_id': client_id,
                                                   'name': tag_name})

        tag.delete()
        zlogger.info("New push tag is deleted. Project id:{}, tag name:{}".format(
            kwargs['project_id'], kwargs['name']))

    def check_tag_deletion_suitability(self, **kwargs):
        """
        Checks single tag deletion suitability. Is tag used in any segment?
    
        Args:
            **kwargs (dict): project_id, name
                - project_id: project id
                - name: name of tag
    
        Returns:
            dict():suitable, results
                - suitable(bool): suitable or not
                - results(list): if not suitable, segment ids list where tag is used in.
        """
        bucket = self.get_bucket(kwargs['project_id'], 'segment')
        results = bucket.get_index("tag_seg_bin", kwargs['tag_name']).results
        return {'suitable': not bool(results), 'results': results}

    def get_push_target_tag(self, **kwargs):
        """
        Retrieves a single target tag with given id.
    
        Args:
            **kwargs (dict): project_id, target_id, name
                - project_id: project id
                - target_id: target who is tagged with this tag
                - name: name of tag
    
        Returns:
            dict: target tag or error message
        """
        project_id, tag_name = kwargs['project_id'], kwargs['name']
        target = self.get_obj(project_id, 'target', kwargs['target_id'])

        if tag_name not in target.data['push_tags']:
            zlogger.error("Tag is doesn't exist in target's tags. Project id:{},"
                          "target id:{}, tag name:{}".format(project_id,
                                                             kwargs['target_id'],
                                                             tag_name))
            return {"error": {"code": -32006,
                              "message": "Related tag couldn't be found in user's push tags."}}

        tag = self.get_obj(project_id, 'tag', "{}_{}".format(project_id, tag_name))
        tag_type, val = (tag.data['tag_type'], target.data['push_tags'][tag_name])
        value = [] if tag_type == 'key' else [val] if tag_type == 'key-value' else list(val.keys())

        return {'key': tag_name, 'value_read': value}

    def delete_all_push_target_tags(self, **kwargs):
        """
        Deletes all tags of target with given id.
    
        Args:
            **kwargs (dict): project_id, target_id
                - project_id: project id
                - target_id: target who is tagged with these tags
        Returns:
    
        """
        target = self.get_obj(kwargs['project_id'], 'target', kwargs['target_id'])
        target.data['push_tags'] = {}
        target.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        target.indexes = {}
        target.store()
        zlogger.info("Target's all tags are deleted. Project id:{}, target id:{}".format(
            kwargs['project_id'], kwargs['target_id']))

    def delete_push_target_tag(self, **kwargs):
        """
        Deletes a specified tag with `name` of target with given id.
    
        Args:
           **kwargs (dict): project_id, target_id, name, value
                - project_id: project id
                - target_id: target who is tagged with this tag
                - name: tag name to delete
                - value: tag_value to delete
    
        Returns:
    
        """
        project_id = kwargs['project_id']
        tag = self.get_obj(project_id, 'tag', "{}_{}".format(project_id, kwargs['name']))
        target = self.get_obj(project_id, 'target', kwargs['target_id'])

        self.delete_target_and_client_tag(tag, target, **kwargs)
        zlogger.info("Target's tag is deleted. Project id:{}, target id:{}, tag name:{}".format(
            kwargs['project_id'], kwargs['target_id'], kwargs['name']))

    def add_push_target_tag(self, **kwargs):
        """
        Adds a tag to target with given id.
    
        Args:
            **kwargs (dict): project_id, target_id, name, value
                - project_id: project id
                - target_id: target who will be tagged with this tag
                - name: name of tag
                - value: value of tag for target('name')
    
        Returns:
    
        """
        tag_key = "{}_{}".format(kwargs['project_id'], kwargs['name'])
        tag = self.get_obj(kwargs['project_id'], 'tag', tag_key)
        target = self.get_obj(kwargs['project_id'], 'target', kwargs['target_id'])

        self.add_target_and_client_push_tag(tag, target, **kwargs)
        zlogger.info("New tag is added to target. Project id:{}, target id:{}, tag name:{}".format(
            kwargs['project_id'], kwargs['target_id'], kwargs['name']))

    def get_list_push_target_tags(self, **kwargs):
        """
        Lists all tags of a target with given id.
    
        Args:
            **kwargs (dict): project_id, target_id
                - project_id: project_id
                - target_id: target whose tags are being listed
    
        Returns:
    
            list: list of dicts(key, value)
                key(str): tag name
                value(list): 
    
        """
        target = self.get_obj(kwargs['project_id'], 'target', kwargs['target_id'])
        results = []
        for k, v in target.data['push_tags'].items():
            results.append(
                {'key': k,
                 'value_read': list(v.keys()) if isinstance(v, dict) else [v] if v else []})

        return results

    def get_push_client_tag(self, **kwargs):
        """
        Retrieves a single client tag with given id.
    
        Args:
            **kwargs (dict): project_id, client_id, key
                - project_id: project_id
                - client_id: client which is tagged with this tag
                - name: name of tag
    
        Returns:
            dict: client tag
        """
        client = self.get_obj(kwargs['project_id'], 'client', kwargs['client_id'])

        if kwargs['name'] not in client.data['push_tags']:
            zlogger.error("Tag is doesn't exist in client's tags. Project id:{}, client id:{}, "
                          "tag name:{}".format(kwargs['project_id'], kwargs['client_id'],
                                               kwargs['name']))
            return {"error": {"code": -32006,
                              "message": "Related tag couldn't be found in client's push tags."}}

        tag = self.get_obj(kwargs['project_id'], 'tag',
                           "{}_{}".format(kwargs['project_id'], kwargs['name']))
        tag_type, val = (tag.data['tag_type'], client.data['push_tags'][kwargs['name']])
        value = [] if tag_type == 'key' else [val] if tag_type == 'key-value' else list(val.keys())

        return {'key': kwargs['name'], 'value_read': value}

    def delete_all_push_client_tags(self, **kwargs):
        """
        Deletes all tags of client with given id.
    
        Args:
            **kwargs (dict): project_id, client_id
                - project_id: project_id            
                - client_id: client which is tagged with these tags
    
        Returns:
    
        """
        client = self.get_obj(kwargs['project_id'], 'client', kwargs['client_id'])
        client.data['push_tags'] = {}
        client.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        client.indexes = {}
        client.store()
        zlogger.info("Client's all tags are deleted. Project id:{}, client id:{}".format(
            kwargs['project_id'], kwargs['client_id']))

    def delete_push_client_tag(self, **kwargs):
        """
        Deletes a specified tag with `key` of client with given id.
    
        Args:
           **kwargs (dict): project_id, client_id, name, value
                - project_id: project_id
                - client_id: client which is tagged with this tag
                - name: name of tag
                - value: value of tag
    
        Returns:
    
        """
        project_id = kwargs['project_id']
        tag = self.get_obj(kwargs['project_id'], 'tag', "{}_{}".format(project_id, kwargs['name']))
        client = self.get_obj(kwargs['project_id'], 'client', kwargs['client_id'])

        self.delete_target_and_client_tag(tag, client, **kwargs)
        zlogger.info("Client's tag is deleted. Project id:{}, client id:{}, tag name:{}".format(
            kwargs['project_id'], kwargs['client_id'], kwargs['name']))

    def get_list_push_client_tags(self, **kwargs):
        """
        Lists all tags of a client with given id.
    
        Args:
            **kwargs (dict): project_id, client_id
                - project_id: project_id
                - client_id: client whose tags are being listed
    
        Returns:
            list: list of dicts(key, value)
    
        """
        client = self.get_obj(kwargs['project_id'], 'client', kwargs['client_id'])

        results = []
        for k, v in client.data['push_tags'].items():
            results.append(
                {'key': k,
                 'value_read': list(v.keys()) if isinstance(v, dict) else [v] if v else []})

        return results

    def add_push_client_tag(self, **kwargs):
        """
        Adds a tag to client with given id.
    
        Args:
            **kwargs (dict): project_id, client_id, name, value
                - project_id: project_id
                - client_id: client which will be tagged with this tag
                - name: name of tag
                - value: value of tag for client(`client_id`)
    
        Returns:
    
        """
        client = self.get_obj(kwargs['project_id'], 'client', kwargs['client_id'])
        tag = self.get_obj(kwargs['project_id'], 'tag',
                           "{}_{}".format(kwargs['project_id'], kwargs['name']))

        self.add_target_and_client_push_tag(tag, client, **kwargs)
        zlogger.info("New tag is added to client. Project id:{}, client id:{}, tag name:{}".format(
            kwargs['project_id'], kwargs['client_id'], kwargs['name']))
