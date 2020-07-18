# -*-  coding: utf-8 -*-

from zopsm.workers.base_jobs import BaseWorkerJobs
from zopsm.lib.log_handler import zlogger
from datetime import datetime
from zopsm.lib.utility import generate_uuid
from zopsm.lib.settings import DATETIME_FORMAT
from zopsm.lib.settings import CACHE_ONLINE_SUBSCRIBERS
from zopsm.lib.settings import CACHE_IDLE_SUBSCRIBERS
from zopsm.lib.settings import CACHE_STATUS
from zopsm.lib.settings import CACHE_STATUS_EXPIRE
from zopsm.lib.settings import CACHE_CONTACTS
from zopsm.lib.sd_riak import RABBIT_HOOK_BUCKET_TYPE


class MessageWorkerJobs(BaseWorkerJobs):
    """
    Worker jobs related with messaging part.
    
    """

    def __setitem__(self, k, v):
        self.__dict__.update(zip(k, v))

    def get_message(self, **kwargs):
        """
        Gets message with given message_id.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - message_id (str)
                - subscriber_id (str)

        Returns:
            dict: message data

        """
        message = self.get_obj(kwargs['project_id'], 'message', kwargs['message_id'],
                               bucket_type=RABBIT_HOOK_BUCKET_TYPE)
        subscriber = self.get_obj(kwargs['project_id'], 'subscriber', kwargs['subscriber_id'])
        if not message.exists:
            zlogger.error(
                "Object Not Found. Subscriber:{sub_id} requested a message that does not exist. "
                "There is no such message with id:{msg_id}.".format(
                    sub_id=kwargs['subscriber_id'], msg_id=kwargs['message_id']
                )
            )
            return {"error": {"code": -32002, "message": "Object Not Found"}}
        elif not kwargs['subscriber_id'] in [message.data['sender'], message.data['receiver']] and \
                        message.data['channel'] not in subscriber.data['channels']:
            zlogger.error("Subscriber id doesn't have permission this operation. Praoject id:{}, "
                          "Message sender:{}, subscriber id:{}".format(kwargs['project_id'],
                                                                       message.data['sender'],
                                                                       kwargs['subscriber_id']))

            return {"error": {"code": -32004, "message": "Unauthorized Operation Error"}}
        return message.data

    def post_message(self, **kwargs):
        """
        Saves message with given data.

        Args:
            kwargs (dict):
                - project_id (str): project id
                - validated_message(dict):
                    * id (str): candidate id for message
                    * title (str): title of message
                    * body (str): body of message
                    * sentTime (str): formatted date string e.g. "2017-08-20T08:54:56.750Z00:00"
                    * receiver (str): "" or receiver_id
                    * channel (str): "prv_user1_user2" or channel_id
                    * sender (str): subscriber_id
                - trackable(bool): Shows that a non-blocking operation or not
                - tracking_id(str): Id to track the erroneous response of this operation

        Returns:

        """
        bucket = self.get_bucket(kwargs['project_id'], 'message',
                                 bucket_type=RABBIT_HOOK_BUCKET_TYPE)
        validated_message = kwargs.get('validated_message')
        validated_message.update(self.get_creation_info())
        message = bucket.get(validated_message.get('id'))
        if message.exists:
            message = bucket.new()
        message.data = validated_message
        message_creation_time_str = message.data["creation_time"]
        datetime_object = datetime.strptime(message_creation_time_str, DATETIME_FORMAT)
        formatted_time = format(datetime_object.timestamp(), '.7f')
        timestamp = int(self.last) - int("".join(str(formatted_time).split('.')))
        message.add_index('message_bin',
                          "{}_{}".format(kwargs['validated_message']['channel'], timestamp))
        message.store()
        zlogger.info(
            "Message is created. Project id:{}, message id:{}".format(
                kwargs['project_id'], message.key),
            extra={
                "project_id": kwargs['project_id'],
                "service": kwargs['service'],
                "purpose": "counter",
            })

        if validated_message['receiver']:
            event_message = "Direct message event is created. Project id: {}, Message id: {}," \
                            " Sender id: {}, Receiver id: {}".format(kwargs['project_id'],
                                                                     message.key,
                                                                     validated_message.get("channel"),
                                                                     validated_message.get("sender"))
            method_name = "direct_message_event"
        else:
            event_message = "Channel Message event is created.Project id: {}, Message id: {}," \
                            " Channel id: {}, Sender id: {}".format(kwargs['project_id'], message.key,
                                   validated_message.get("channel"),
                                   validated_message.get("sender"))
            method_name = "channel_message_event"
        zlogger.info(
            event_message,
            extra={
                "purpose": "event",
                "params": {
                    "channelId": validated_message.get("channel"),
                    "data": validated_message,
                },
                "method": method_name,
            }
        )

    def update_message(self, **kwargs):
        """
        Updates existing message with given data.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - message_id (str)
                - subscriber id (str)
                - validated_message (dict):
                    * title (str): message title
                    * body (str): message body max 1K string
                    * sentTime (str): formatted date string e.g. "2017-08-20T08:54:56.750Z00:00"

        Returns:
            
        """
        # TODO: validated message contents should be detailed.
        message = self.get_obj(kwargs['project_id'], 'message', kwargs['message_id'], bucket_type=RABBIT_HOOK_BUCKET_TYPE)
        if kwargs['subscriber_id'] != message.data['sender']:
            zlogger.error("Sender id is not equal to message sender. Project id:{}, Message "
                          "sender:{}, subscriber id:{}".format(kwargs['project_id'],
                                                               message.data['sender'],
                                                               kwargs['subscriber_id']))
            return {"error": {"code": -32004, "message": "Unauthorized Operation Error"}}
        kwargs['validated_message']['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        message.data.update(kwargs['validated_message'])
        message.store()
        zlogger.info("Message is updated. Project id:{}, message id:{}".format(
            kwargs['project_id'], kwargs['message_id']))

    def delete_message(self, **kwargs):
        """
        Deletes message with given id.
        
        Args:
            kwargs (dict)
                - project_id (str): project id
                - message_id (str)
                - subscriber_id (str)

        """
        message = self.get_obj(kwargs['project_id'], 'message', kwargs['message_id'],
                               bucket_type=RABBIT_HOOK_BUCKET_TYPE)

        if kwargs['subscriber_id'] != message.data['sender']:
            zlogger.error("Sender id is not equal to message sender. Project id:{}, Message "
                          "sender:{}, subscriber id:{}".format(kwargs['project_id'],
                                                               message.data['sender'],
                                                               kwargs['subscriber_id']))
            return {"error": {"code": -32004, "message": "Unauthorized Operation Error"}}

        message.delete()
        zlogger.info(
            "Message is deleted. Project id:{}, message id:{}".format(
                kwargs['project_id'], kwargs['message_id']),
            extra={
                "project_id": kwargs['project_id'],
                "service": kwargs['service'],
                "purpose": "counter",
            })

    def list_messages(self, **kwargs):
        """
        Messages are listed according to given pattern(private or channel message)
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - continuation (str):
                - page_size (int):
                _ channel (str): like 'prv_usr1_usr2' or channel_id

        Returns:
            dict: continuation, results:
                - continuation(str): continuation key
                - results(list): list of messages' data
            
        """
        project_id = kwargs['project_id']
        bucket = self.get_bucket(project_id, 'message', bucket_type=RABBIT_HOOK_BUCKET_TYPE)

        params = {'max_results': kwargs['page_size']}

        if 'continuation' in kwargs:
            params['continuation'] = kwargs['continuation']

        pattern = kwargs['channel']
        first, last = '{}_{}'.format(pattern, self.first), '{}_{}'.format(pattern, self.last)
        message_data = bucket.get_index('message_bin', first, last, **params)

        continuation, results = message_data.continuation, message_data.results
        return {"continuation": continuation,
                "results": [self.add_key_to_data(project_id, 'message', key, bucket_type=RABBIT_HOOK_BUCKET_TYPE) for key in results]}

    def ban_channel_by_subscriber(self, **kwargs):
        """
        Subscriber's channel ban.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - channel_id (str)
                - subscriber_id (str) 

        Returns:

        """
        channel = self.get_obj(kwargs['project_id'], 'channel', kwargs['channel_id'])
        subscriber = self.get_obj(kwargs['project_id'], 'subscriber', kwargs['subscriber_id'])

        subscriber.data['banned_channels'][kwargs['channel_id']] = ""

        if kwargs['channel_id'] in subscriber.data['channels'].keys():
            del subscriber.data['channels'][kwargs['channel_id']]
            del channel.data['subscribers'][kwargs['subscriber_id']]
            channel.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
            channel.store()

        subscriber.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        subscriber.store()

        self.bindings_operation('delete_binding', kwargs['subscriber_id'], kwargs['channel_id'])
        zlogger.info("Channel is banned by subscriber. Project id:{}, subscriber id:{}, "
                     "channel id:{}".format(kwargs['project_id'], kwargs['subscriber_id'],
                                            kwargs['channel_id']))

    def unban_channel_by_subscriber(self, **kwargs):
        """
        Subscriber's channel unban.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - channel_id (str)
                - subscriber_id (str)
    
        Returns:
    
        """
        subscriber = self.get_obj(kwargs['project_id'], 'subscriber', kwargs['subscriber_id'])

        if kwargs['channel_id'] not in subscriber.data['banned_channels']:
            zlogger.error(
                "Channel id doesn't exist in subscriber's banned channels. Project id:{}, "
                "subscriber id:{}, channel id:{}".format(kwargs['project_id'],
                                                         kwargs['subscriber_id'],
                                                         kwargs['channel_id']))
            return {"error":
                        {"code": -32006,
                         "message": "Channel id doesn't exist in subscriber's banned channels"}
                    }

        del subscriber.data['banned_channels'][kwargs['channel_id']]

        subscriber.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        subscriber.store()

        zlogger.info("Channel is unbanned by subscriber. Project id:{}, subscriber id:{}, "
                     "channel id:{}".format(kwargs['project_id'], kwargs['subscriber_id'],
                                            kwargs['channel_id']))

    def ban_subscriber_by_channel(self, **kwargs):
        """
        Channel's subscriber ban.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - channel_id (str)
                - subscriber_id (str)
    
        Returns:
    
        """
        channel = self.get_obj(kwargs['project_id'], 'channel', kwargs['channel_id'])
        subscriber = self.get_obj(kwargs['project_id'], 'subscriber', kwargs['subscriber_id'])

        channel.data['banned_subscribers'][kwargs['subscriber_id']] = ""

        if kwargs['channel_id'] in subscriber.data['channels'].keys():
            del subscriber.data['channels'][kwargs['channel_id']]
            del channel.data['subscribers'][kwargs['subscriber_id']]
            subscriber.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
            subscriber.store()
            self.bindings_operation('delete_binding', kwargs['subscriber_id'], kwargs['channel_id'])

        channel.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        channel.store()
        zlogger.info("Subscriber is banned by channel. Project id:{}, subscriber id:{}, "
                     "channel id:{}".format(kwargs['project_id'], kwargs['subscriber_id'],
                                            kwargs['channel_id']))

    def unban_subscriber_by_channel(self, **kwargs):
        """
        Channel's subscriber unban.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - channel_id (str)
                - subscriber_id (str)

        Returns:

        """
        channel = self.get_obj(kwargs['project_id'], 'channel', kwargs['channel_id'])
        if kwargs['subscriber_id'] not in channel.data['banned_subscribers']:
            zlogger.error(
                "Subscriber id doesn't exist in channel's banned subscribers. Project id:{}, "
                "subscriber id:{}, channel id:{}".format(kwargs['project_id'],
                                                         kwargs['subscriber_id'],
                                                         kwargs['channel_id']))
            return {"error":
                        {"code": -32006,
                         "message": "Subscriber id doesn't exist in channel's banned subscribers"}}

        del channel.data['banned_subscribers'][kwargs['subscriber_id']]
        channel.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        channel.store()
        zlogger.info("Subscriber is unbanned by channel. Project id:{}, subscriber id:{}, "
                     "channel id:{}".format(kwargs['project_id'], kwargs['subscriber_id'],
                                            kwargs['channel_id']))

    def ban_subscriber_by_subscriber(self, **kwargs):
        """
        Args:
            kwargs (dict):
                - project_id (str): project id
                - subscriber_id (str): subscriber who bans `subscriber_to_ban`
                - subscriber_to_ban (str): subscriber who is banned by `subscriber_id`

        Returns:
        
        """
        subs_to_ban_id = kwargs['subscriber_to_ban']

        subscriber = self.get_obj(kwargs['project_id'], 'subscriber', kwargs['subscriber_id'])
        subs_to_ban = self.get_obj(kwargs['project_id'], 'subscriber', subs_to_ban_id)

        subscriber.data['banned_subscribers'][kwargs['subscriber_to_ban']] = ""
        if subs_to_ban_id in subscriber.data['contacts']:

            del subscriber.data['contacts'][subs_to_ban_id]
            del subs_to_ban.data['contacts'][kwargs['subscriber_id']]
            subs_to_ban.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
            subs_to_ban.store()

        subscriber.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        subscriber.store()
        zlogger.info("Subscriber is banned by other subscriber. Project id:{}, banned subscriber "
                     "id:{}, is banned subscriber id:{}".format(kwargs['project_id'],
                                                                kwargs['subscriber_id'],
                                                                kwargs['subscriber_to_ban']))

    def unban_subscriber_by_subscriber(self, **kwargs):
        """
        A subscriber removes a ban of another.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - subscriber_id (str): subscriber id
                - subscriber_to_unban (str): subscriber id to unban

        Returns:

        """
        subscriber = self.get_obj(kwargs['project_id'], 'subscriber', kwargs['subscriber_id'])
        if kwargs['subscriber_to_unban'] not in subscriber.data['banned_subscribers']:
            zlogger.error(
                "Subscriber who will unban doesn't exist in subscriber's banned subscribers. "
                "Project id:{}, subscriber to unban:{}, subscriber id:{}".format(
                    kwargs['project_id'],
                    kwargs['subscriber_to_unban'],
                    kwargs['subscriber_id']))
            return {"error":
                        {"code": -32006,
                         "message": "Subscriber who will unban doesn't exist in subscriber's "
                                    "banned subscribers."}
                    }
        del subscriber.data['banned_subscribers'][kwargs['subscriber_to_unban']]
        subscriber.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        subscriber.store()
        zlogger.info("Subscriber is unbanned by other subscriber. Project id:{}, "
                     "unbanned subscriber id:{}, is unbanned subscriber id:{}".
                     format(kwargs['project_id'],
                            kwargs['subscriber_id'],
                            kwargs['subscriber_to_unban']))

    def delete_channel(self, **kwargs):
        """
        Channel deletion.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - channel_id (str): channel id to delete
    
        Returns:
            
        """
        channel = self.get_obj(kwargs['project_id'], 'channel', kwargs['channel_id'])

        for subs_id in channel.data['subscribers'].keys():
            subscriber = self.get_obj(kwargs['project_id'], 'subscriber', subs_id)
            del subscriber.data['channels'][kwargs['channel_id']]
            subscriber.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
            subscriber.store()
            self.bindings_operation('delete_binding', subs_id, kwargs['channel_id'])

        channel.delete()
        zlogger.info(
            "Channel is deleted. Project id:{}, channel id:{}".format(
                kwargs['project_id'], kwargs['channel_id']),
            extra={
                "project_id": kwargs['project_id'],
                "service": kwargs['service'],
                "purpose": "counter",
            })

    def update_channel(self, **kwargs):
        """
        Channel info's update.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - channel_id (str):
                - validated_channel (dict):
                    * name (str)
                    * description (str)
                    * type (str): 'public', 'private', 'invisible', 'public-announcement',
                    'private-announcement', 'invisible-announcement

        Returns:
    
        """
        channel = self.get_obj(kwargs['project_id'], 'channel', kwargs['channel_id'])
        validated_channel = kwargs.get('validated_channel')
        channel.data.update(validated_channel)
        channel.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        channel.store()

        zlogger.info("Channel is updated. Project id:{}, channel id:{}".format(kwargs['project_id'],
                                                                               kwargs[
                                                                                   'channel_id']))

    def list_channels(self, **kwargs):
        """
        Subscriber's channels listing according to channel type.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - channel_type (str): 'public', 'private', 'invisible', 'public-announcement',
                    'private-announcement', 'invisible-announcement' or 'all' if no params sent.
                - subscriber_id (str)
    
        Returns:
    
        """
        project_id = kwargs['project_id']
        subscriber = self.get_obj(kwargs['project_id'], 'subscriber', kwargs['subscriber_id'])
        channels = subscriber.data['channels']
        ch_type = kwargs['channel_type']
        if kwargs['channel_type'] == 'all':
            raw_result = [self.add_key_to_data(project_id, 'channel', key) for key in channels.keys()]
        else:
            raw_result = []
            for key in channels.keys():
                channel_data = self.add_key_to_data(project_id, 'channel', key)
                if channel_data['type'] == ch_type:
                    raw_result.append(channel_data)

        return raw_result if not raw_result else [
            {
                "id": r['id'],
                "name": r['name'],
                "type": r['type'],
                "description": r['description'],
                "creation_time": r['creation_time'],
                "last_update_time": r['last_update_time'],
                "is_deleted": r['is_deleted'],
                "is_active": r['is_active'],
            }
            for r in raw_result]

    def create_channel(self, **kwargs):
        """
        Channel creation.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - created_by (str): subscriber id of who creates the channel
                - validated_channel (dict):
                    * name (str): Channel name
                    * description (str): Optional channel description
                    * type (str): 'public', 'public-group', 'private-group', 'announcement', 'private'
                - channel_id (str): Riak id of the channel will be created.

        Returns:
    
        """
        bucket = self.get_bucket(kwargs['project_id'], 'channel')
        subscriber = self.get_obj(kwargs['project_id'], 'subscriber', kwargs['created_by'])

        data = kwargs['validated_channel']
        data['owner'] = {kwargs['created_by']: ""}
        data['managers'] = {kwargs['created_by']: ""}
        # list of invite ids for invitations that sent by channel in dict form
        data['invitees'] = {}
        # list of invite ids for join requests to channel in dict form
        data['join_requests'] = {}
        data['subscribers'] = {kwargs['created_by']: ""}
        data['banned_subscribers'] = {}
        data.update(self.get_creation_info())
        channel = bucket.get(kwargs['channel_id'])

        # if the sent channel id is already exists in riak
        if channel.exists:
            channel = bucket.new()

        channel.data = data
        subscriber.data['channels'][channel.key] = ""
        channel.usermeta = {
            "project_id": kwargs['project_id'],
            "service": kwargs['service'],
            "bucket_name": 'channel',
        }
        channel.store()
        subscriber.store()

        self.bindings_operation('create_binding', kwargs['created_by'], channel.key)
        zlogger.info(
            "Channel is created. Project id:{}, channel id:{}".format(
                kwargs['project_id'], channel.key),
            extra={
                "project_id": kwargs['project_id'],
                "service": kwargs['service'],
                "purpose": "counter"})

    def delete_contact(self, **kwargs):
        """
        Subscriber removes another subscriber from contacts.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - subscriber_id (str): subscriber id of user who makes the request
                - contact_id (str): subscriber id of contact to delete
    
        Returns:
    
        """
        subscriber = self.get_obj(kwargs['project_id'], 'subscriber', kwargs['subscriber_id'])
        contact = self.get_obj(kwargs['project_id'], 'subscriber', kwargs['contact_id'])

        if kwargs['contact_id'] in subscriber.data['contacts'] and kwargs['subscriber_id'] in \
                contact.data['contacts']:
            del subscriber.data['contacts'][kwargs['contact_id']]
            del contact.data['contacts'][kwargs['subscriber_id']]
        else:
            err_msg = "Subscriber:{} cannot delete subscriber:{} from contacts, because they are " \
                      "not contacts!".format(kwargs['subscriber_id'], kwargs['contact_id'])
            zlogger.error(err_msg)
            return {"error": {"code": -32006, "message": err_msg}}

        now = datetime.now().strftime(DATETIME_FORMAT)
        subscriber.data['last_update_time'] = now
        contact.data['last_update_time'] = now
        subscriber.store()
        contact.store()
        zlogger.info("Contact is deleted. Project id:{}, subscriber id:{}, contact id:{}".format(
            kwargs['project_id'], kwargs['subscriber_id'], kwargs['contact_id']))

    def accept_reject_contact_request(self, **kwargs):
        """
        Accepting or rejecting of contact request between two subscriber.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - invite_id (str): invite id of the contact request
                - approve (str): can be 'approved', 'rejected'
                - service (str): service id
                - subscriber_id (str): subscriber id of whom is expected to be invitee
    
        Returns:

        """
        approve = kwargs['approve']
        invite = self.get_obj(kwargs['project_id'], 'invite', kwargs['invite_id'])
        subscriber_id = invite.data['invitee']
        inviter_id = invite.data['inviter']

        # checks if replier of this contact request is invitee of it
        if subscriber_id == kwargs.get('subscriber_id'):
            subscriber = self.get_obj(kwargs['project_id'], 'subscriber', subscriber_id)
        else:
            err_msg = "Subscriber:{} is not allowed to reply this contact request:{}. Invitee:{} " \
                      "of contact request is different from subscriber.".format(
                kwargs['subscriber_id'], kwargs['invite_id'], subscriber_id)
            zlogger.error(err_msg)
            return {"error": {"code": -32006,
                              "message": err_msg}}

        now = datetime.now().strftime(DATETIME_FORMAT)
        inviter = self.get_obj(kwargs['project_id'], 'subscriber', inviter_id)

        if approve == 'approved':
            subscriber.data['contacts'][inviter_id] = ""
            inviter.data['contacts'][subscriber_id] = ""

        invite.delete()
        del subscriber.data['contact_requests_in'][kwargs['invite_id']]
        subscriber.data['last_update_time'] = now
        subscriber.store()

        del inviter.data['contact_requests_out'][kwargs['invite_id']]
        inviter.data['last_update_time'] = now
        inviter.store()

        zlogger.info("Contact request is evaluated. Project id:{}, inviter id:{}, invitee id:{}, "
                     "result:{}".format(kwargs['project_id'], inviter_id, subscriber_id, approve))

    def create_contact_request(self, **kwargs):
        """
        Creation of contact request between two subscribers.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - inviter (str): subscriber id of who made the contact request
                - invitee (str): subscriber id of whom wanted to be a contact with
                - message (str): textual request message to say hi
                - service (str): service: roc, push or sms
        Returns:

        """

        bucket = self.get_bucket(kwargs['project_id'], 'invite')
        kwargs.update(self.get_creation_info())

        invite = bucket.new(data=kwargs)
        invite.store()

        subscriber = self.get_obj(kwargs['project_id'], 'subscriber', kwargs['invitee'])
        inviter = self.get_obj(kwargs['project_id'], 'subscriber', kwargs['inviter'])

        ####
        # in case of there is already a contact request between invitee and inviter
        subs_invitations = []
        subs_invitations.extend(subscriber.data['contact_requests_in'].values())
        subs_invitations.extend(subscriber.data['contact_requests_out'].values())
        # in case of there is already a contact request between invitee and inviter
        for invtr in subs_invitations:
            if invtr == kwargs['inviter']:
                err_msg = "There already is a contact request exists between subscribers " \
                          "{inviter} and {invitee}".format(inviter=kwargs['inviter'],
                                                           invitee=kwargs['invitee'])
                zlogger.error(err_msg)
                return {"error": {"code": -32006,
                                  "message": err_msg}}

        inv_invitations = []
        inv_invitations.extend(inviter.data['contact_requests_in'].values())
        inv_invitations.extend(inviter.data['contact_requests_out'].values())
        for invte in inv_invitations:
            if invte == kwargs['invitee']:
                err_msg = "There already is a contact request exists between subscribers " \
                          "{inviter} and {invitee}".format(inviter=kwargs['inviter'],
                                                           invitee=kwargs['invitee'])
                zlogger.error(err_msg)
                return {"error": {"code": -32006,
                                  "message": err_msg}}
        ####

        if kwargs['inviter'] not in subscriber.data['banned_subscribers'] and \
                kwargs['invitee'] not in inviter.data['banned_subscribers']:
            # invitee's incoming contact requests updated with invitation id and inviter id
            subscriber.data['contact_requests_in'][invite.key] = kwargs['inviter']

            # inviter's sent contact requests updated with invitation id and invitee id
            inviter.data['contact_requests_out'][invite.key] = kwargs['invitee']

            now = datetime.now().strftime(DATETIME_FORMAT)
            subscriber.data['last_update_time'] = now
            inviter.data['last_update_time'] = now
            subscriber.store()
            inviter.store()
            zlogger.info("Contact request is created. Project id:{}, inviter id:{}, invitee id:{}".
                         format(kwargs['project_id'], kwargs['inviter'], kwargs['invitee']))
        elif kwargs['invitee'] in inviter.data['banned_subscribers']:
            err_msg = "Subscriber:{} is banned. In order to send a contact request ban of " \
                      "subscriber:{} must be removed!".format(kwargs['invitee'], kwargs['invitee'])
            zlogger.error(err_msg)
            return {"error": {"code": -32007,
                              "message": err_msg}}
        else:
            err_msg = "Subscriber:{} is not allowed to send contact request to subscriber:{}, ." \
                      "because subscriber:{} already banned subscriber:{}".format(
                kwargs['inviter'], kwargs['invitee'], kwargs['invitee'], kwargs['inviter'])
            zlogger.error(err_msg)
            return {"error": {"code": -32007,
                              "message": err_msg}}

    def list_requests(self, **kwargs):
        """
        Subscriber's requests listing according to request type.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - subscriber_id (str): subscriber id of who made the list request
                - request_type (str): 'channel', 'contact' or 'all'
                - invite_type (str): 'incoming' or 'sent'
                - service (str): service: roc, push or sms
    
        Returns:
            list(dict): list of invite objects
        """
        subscriber = self.get_obj(kwargs['project_id'], 'subscriber', kwargs['subscriber_id'])

        invites = {}
        if kwargs['request_type'] == 'channel':
            if kwargs['invite_type'] == 'incoming':
                invites = subscriber.data['channel_invites']
            elif kwargs['invite_type'] == 'sent':
                invites = subscriber.data['channel_join_requests']
        elif kwargs['request_type'] == 'contact':
            if kwargs['invite_type'] == 'incoming':
                invites = subscriber.data['contact_requests_in']
            elif kwargs['invite_type'] == 'sent':
                invites = subscriber.data['contact_requests_out']
        else:
            if kwargs['invite_type'] == 'incoming':
                invites = dict(**subscriber.data['channel_invites'],
                               **subscriber.data['contact_requests_in'])
            elif kwargs['invite_type'] == 'sent':
                invites = dict(**subscriber.data['channel_join_requests'],
                               **subscriber.data['contact_requests_out'])

        result = []
        for inv_id in invites.keys():
            invite = self.get_obj(kwargs['project_id'], 'invite', inv_id)
            invite.data['id'] = invite.key
            result.append(invite.data)

        return result

    def evaluate_accept_reject_invite(self, **kwargs):
        """

        Args:
            **kwargs (dict):
                - project_id (str): project id
                - invite_id (str): invite id
                - approve (str): can be 'approved', 'rejected'
                - service (str): service
                - subscriber_id (str): unique identifier of subscriber
        Returns:

        """
        subscriber_id = kwargs.get('subscriber_id')
        invite = self.get_obj(kwargs['project_id'], 'invite', kwargs['invite_id'])
        inviter_id = invite.data.get('inviter')
        channel_id = invite.data.get('channel')
        channel = self.get_obj(kwargs['project_id'], 'channel', channel_id)
        invitee_id = invite.data.get('invitee')

        if invite.data['approve'] == kwargs['approve']:
            err_msg = "Field 'approve' must be updated!"
            zlogger.error(err_msg)
            return {"error": {"code": -32006, "message": err_msg}}

        if not invitee_id or invitee_id == channel_id:
            # subscriber asks to join and channel must reply
            if subscriber_id not in channel.data['managers']:
                err_msg = "Subscriber:{} is not allowed to approve or reject this invite:{}!".format(
                    subscriber_id,
                    kwargs['invite_id']
                )
                zlogger.error(err_msg)
                return {"error": {"code": -32007, "message": err_msg}}
            else:
                self.accept_reject_invite_by_channel(invite, channel, **kwargs)
        elif all([invitee_id, inviter_id, channel_id]) and inviter_id in channel.data['managers']:
            # channel manager invites subscriber and subscriber must reply
            if subscriber_id != invitee_id:
                err_msg = "Subscriber:{} is not allowed to approve or reject this invite:{}!".format(
                    subscriber_id,
                    kwargs['invite_id']
                )
                zlogger.error(err_msg)
                return {"error": {"code": -32007, "message": err_msg}}
            else:
                self.accept_reject_invite_by_subscriber(invite, channel, **kwargs)

    def accept_reject_invite_by_subscriber(self, invite_obj, channel_obj, subscriber_id=None,
                                           from_by_channel=False, **kwargs):
        """
        
        Subscriber's request to participate in the channel is evaluated.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - invite_id (str): invite id
                - approve (str): can be 'approved', 'rejected'
                - service (str): service
            subscriber_id (str): unique identifier of subscriber
            invite_obj (obj): riak object of invite
            channel_obj (obj): riak object of channel
            from_by_channel (bool): indicates that method is called
                `from accept_reject_invite_by_channel` method. False by default.

        Returns:

        """
        approve = kwargs['approve']
        invite = invite_obj
        channel_id = invite.data['channel']
        subscriber_id = subscriber_id or invite.data['invitee']

        subscriber = self.get_obj(kwargs['project_id'], 'subscriber', subscriber_id)
        channel = channel_obj

        if approve == 'approved':
            subscriber.data['channels'][channel_id] = ""
            channel.data['subscribers'][subscriber_id] = ""
            self.bindings_operation('create_binding', subscriber_id, channel_id)

        if not from_by_channel:
            # removes the invite id from invites
            subscriber.data['channel_invites'].pop(kwargs['invite_id'], None)
            channel.data['invitees'].pop(kwargs['invite_id'], None)
        else:
            # removes the invite id from join requests
            subscriber.data['channel_join_requests'].pop(kwargs['invite_id'], None)
            channel.data['join_requests'].pop(kwargs['invite_id'], None)

        now = datetime.now().strftime(DATETIME_FORMAT)
        channel.data['last_update_time'] = now
        subscriber.data['last_update_time'] = now
        channel.store()
        subscriber.store()
        invite.delete()
        zlogger.info("Channel request is evaluated. Project id:{}, subscriber id:{}, channel id:{},"
                     "result:{}".format(kwargs['project_id'], subscriber_id, channel_id, approve))

    def accept_reject_invite_by_channel(self, invite_obj, channel_obj, **kwargs):
        """
        Channel invite evaluation by channel.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - invite_id (str): invite id
                - approve (str): can be 'approved', 'rejected'
                - service (str): service
                - subscriber_id (str): unique identifier of subscriber
            invite_obj (obj): riak object of invite
            channel_obj (obj): riak object of channel

        Returns:
                    inviter (user)
                    invitee (user)
                    channel (channel)
                    message (str)
                    approve (str, approved, rejected, not_evaluated)

    
        """

        kwargs['subscriber_id'] = invite_obj.data['inviter']
        self.accept_reject_invite_by_subscriber(invite_obj, channel_obj, from_by_channel=True,
                                                **kwargs)

    def get_invite(self, **kwargs):
        """
        Retrieves a single invite with given id.

        Args:
            **kwargs (dict):
                - project_id (str): project id
                - invite_id (str): invite id
                - service (str): service
                - subscriber_id (str): unique identifier of subscriber

        Returns:
            dict: invite object
        """
        invite_id = kwargs['invite_id']
        subscriber_id = kwargs['subscriber_id']
        invite = self.get_obj(kwargs['project_id'], 'invite', invite_id)
        channel_id = invite.data['channel']
        channel = self.get_obj(kwargs['project_id'], 'channel', channel_id)
        subscriber = self.get_obj(kwargs['project_id'], 'subscriber', subscriber_id)

        def validated():
            if invite_id in subscriber.data['channel_invites']:
                return True
            elif invite_id in subscriber.data['channel_join_requests']:
                return True
            if invite_id in channel.data['invitees'] and subscriber_id in channel.data['managers']:
                return True
            elif invite_id in channel.data['join_requests'] and subscriber_id in channel.data['managers']:
                return True
            return False

        if not validated():
            err_msg = "Subscriber id does not have permission for this operation. Project id:{}, " \
                      "subscriber id:{}, invite id:{}".format(kwargs['project_id'], subscriber_id, invite_id)
            zlogger.error(err_msg)
            return {"error": {"code": -32007, "message": err_msg}}
        invite.data['id'] = invite_id
        return invite.data

    def cancel_invite(self, **kwargs):
        """
        Cancels an invitation.
        Args:
            **kwargs (dict):
                - project_id (str): project id
                - invite_id (str): invite id
                - service (str): service
                - subscriber_id (str): unique identifier of subscriber
                - type (str): contact, or channel

        Returns:

        """
        invite_id = kwargs['invite_id']
        subscriber_id = kwargs['subscriber_id']
        invite = self.get_obj(kwargs['project_id'], 'invite', invite_id)

        inviter_id = invite.data['inviter']
        invitee_id = invite.data['invitee']

        if subscriber_id != inviter_id:
            err_msg = "Subscriber id does not have permission to cancel an invite. Project id:{}, "\
                      "subscriber id:{}, invite id:{}".format(kwargs['project_id'], subscriber_id,
                                                              invite_id)
            zlogger.error(err_msg)
            return {"error": {"code": -32007, "message": err_msg}}

        if invitee_id:
            invitee = self.get_obj(kwargs['project_id'], 'subscriber', invitee_id)

        inviter = self.get_obj(kwargs['project_id'], 'subscriber', inviter_id)
        now = datetime.now().strftime(DATETIME_FORMAT)

        if kwargs['type'] == "contact":
            zlogger.debug("TYPE CONTACT")
            invite.delete()
            if invite_id in inviter.data['contact_requests_out']:
                del inviter.data['contact_requests_out'][invite_id]
            if invite_id in invitee.data['contact_requests_in']:
                del invitee.data['contact_requests_in'][invite_id]
            inviter.data['last_update_time'] = now
            invitee.data['last_update_time'] = now
            inviter.store()
            invitee.store()
            zlogger.info(
                "Contact request canceled in project:{project_id} from subscriber:{inviter_id} to "
                "subscriber:{invitee_id}".format(
                    project_id=kwargs['project_id'],
                    inviter_id=inviter_id,
                    invitee_id=invitee_id
                )
            )
        else:
            channel_id = invite.data['channel']
            channel = self.get_obj(kwargs['project_id'], 'channel', channel_id)
            invite.delete()
            if invite_id in channel.data['invitees']:
                del channel.data['invitees'][invite_id]
            elif invite_id in channel.data['join_requests']:
                del channel.data['join_requests'][invite_id]
            if invite_id in inviter.data['channel_invites']:
                del inviter.data['channel_invites'][invite_id]
            elif invite_id in inviter.data['channel_join_requests']:
                del inviter.data['channel_join_requests'][invite_id]
            channel.data['last_update_time'] = now
            inviter.data['last_update_time'] = now
            channel.store()
            inviter.store()
            zlogger.info(
                "Channel request is cancelled. Project id:{}, subscriber id:{}, channel id:{}".format(
                    kwargs['project_id'], subscriber_id, channel_id))

    def create_invite_by_subscriber(self, **kwargs):
        """
        Invite creation by subscriber.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - inviter (str): inviter
                - channel (str): channel id
                - invite_message (str): invite message
                - service (str): service

        Returns:
    
        """
        channel = self.get_obj(kwargs['project_id'], 'channel', kwargs['channel'])
        subscriber = self.get_obj(kwargs['project_id'], 'subscriber', kwargs['inviter'])
        now = datetime.now().strftime(DATETIME_FORMAT)

        if channel.data['type'] != 'public' and channel.data['type'] != 'public-announcement':
            invite_id = kwargs['invite_id']
            bucket = self.get_bucket(kwargs['project_id'], 'invite')
            kwargs.update(self.get_creation_info())
            kwargs['invitee'] = ""
            kwargs['approve'] = "not-evaluated"

            invite = bucket.get(invite_id)
            if invite.exists:
                invite = bucket.new()
            invite.data = kwargs
            invite.store()

            subscriber.data['channel_join_requests'][invite.key] = ""
            subscriber.data['last_update_time'] = now
            subscriber.store()

            channel.data['join_requests'][invite.key] = ""
            channel.data['last_update_time'] = now
            channel.store()

            zlogger.info("Invitation is created by subscriber. Project id:{}, subscriber id:{}, "
                         "channel id:{}".format(kwargs['project_id'], kwargs['inviter'],
                                                kwargs['channel']))
        else:
            channel.data['subscribers'][kwargs['inviter']] = ""
            subscriber.data['channels'][kwargs['channel']] = ""

            channel.data['last_update_time'] = now
            subscriber.data['last_update_time'] = now

            channel.store()
            subscriber.store()

            self.bindings_operation('create_binding', kwargs['inviter'], kwargs['channel'])
            zlogger.info("Subscriber subscribed to channel. Project id:{}, subscriber id:{}, "
                         "channel id:{}".format(kwargs['project_id'], subscriber.key, channel.key))

    def create_invite_by_channel(self, **kwargs):
        """
        Invite creation by channel.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - inviter (str): inviter
                - invitee (str): invitee
                - channel (str): channel id
                - invite_message (str): invite message
                - service (str): service

        Returns:
                    
        """
        invite_id = kwargs['invite_id']
        kwargs['approve'] = "not-evaluated"
        bucket = self.get_bucket(kwargs['project_id'], 'invite')

        invite = bucket.get(invite_id)
        if invite.exists:
            invite_id = generate_uuid()
            invite = bucket.get(invite_id)
        kwargs.update(self.get_creation_info())
        invite.data = kwargs
        invite.store()

        subscriber = self.get_obj(kwargs['project_id'], 'subscriber', kwargs['invitee'])
        subscriber.data['channel_invites'][invite.key] = ""
        subscriber.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        subscriber.store()

        channel = self.get_obj(kwargs['project_id'], 'channel', kwargs['channel'])
        channel.data['invitees'][invite.key] = ""
        channel.data['last_update_time'] = datetime.now().strftime(DATETIME_FORMAT)
        channel.store()

        zlogger.info("Invitation is created by channel. Project id:{}, subscriber id:{}, "
                     "channel id:{}".format(kwargs['project_id'], kwargs['invitee'],
                                            kwargs['channel']))

    def list_invites_by_ids(self, **kwargs):
        """

        Args:
            **kwargs (dict):
                - project_id (str): project id
                - service (str): service
                - subscriber_id (str): unique identifier of subscriber
                - invites (list): list of invite ids to be listed in details

        Returns:

        """
        result = []
        invites = kwargs.pop('invites')
        for inv in invites:
            result.append(self.get_invite(invite_id=inv, **kwargs))
        return result

    def get_status(self, **kwargs):
        """
        Retrieves subscriber's and all his/her contacts status as list. First item in the list must
        be the subscriber's status.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - subscriber_id (str): subscriber id
                - service (str): service

        Returns:
            list : list of statuses of subscriber him/herself and his/her contacts
        """
        cache_online_subscribers = CACHE_ONLINE_SUBSCRIBERS.format(
            project_id=kwargs['project_id'],
            service=kwargs['service'],
        )
        cache_idle_subscribers = CACHE_IDLE_SUBSCRIBERS.format(
            project_id=kwargs['project_id'],
            service=kwargs['service'],
        )
        cache_status = CACHE_STATUS.format(
            project_id=kwargs['project_id'],
            service=kwargs['service'],
            subscriber_id=kwargs['subscriber_id'],
        )
        cache_contacts = CACHE_CONTACTS.format(
            project_id=kwargs['project_id'],
            service=kwargs['service'],
            subscriber_id=kwargs['subscriber_id'],
        )

        # retrieves subscriber's status from redis
        subscriber_status = self.cache.hgetall(cache_status)

        if not subscriber_status:
            # if not exists in redis retrieves the last status of subscriber from riak
            status = self.get_obj(kwargs['project_id'], 'status', kwargs['subscriber_id'])
            subscriber_status = status.data
            # makes it behavioral status online and set it to the redis
            subscriber_status['behavioral_status'] = 'online'
            now = datetime.now().strftime(DATETIME_FORMAT)
            subscriber_status['last_update_time'] = now
            subscriber_status['last_activity_time'] = now
            self.cache.hmset(cache_status, subscriber_status)
            self.cache.sadd(cache_online_subscribers, kwargs['subscriber_id'])
            self.cache.expire(cache_status, CACHE_STATUS_EXPIRE)
        subscriber_status['id'] = kwargs['subscriber_id']
        result = [subscriber_status]

        if not self.cache.exists(cache_contacts):
            subscriber = self.get_obj(kwargs['project_id'], 'subscriber', kwargs['subscriber_id'])
            self.cache.sadd(cache_contacts, list(subscriber.data['contacts']))

        cache_online_contacts = "Dyn:{}".format(generate_uuid())
        cache_idle_contacts = "Dyn:{}".format(generate_uuid())
        self.cache.sinterstore(cache_online_contacts, cache_online_subscribers, cache_contacts)
        self.cache.sinterstore(cache_idle_contacts, cache_idle_subscribers, cache_contacts)
        contacts = list(self.cache.sunion(cache_online_contacts, cache_idle_contacts))
        self.cache.delete(cache_online_contacts, cache_idle_contacts)
        for contact in contacts:
            contact = contact.decode()
            cache_status_contact = CACHE_STATUS.format(
                project_id=kwargs['project_id'],
                service=kwargs['service'],
                subscriber_id=contact,
            )
            contact_status = self.cache.hgetall(cache_status_contact)
            if contact_status:
                contact_status['id'] = contact
                result.append(contact_status)
        return result

    def set_status(self, **kwargs):
        """

        Args:
            kwargs (dict):
                - project_id (str): project id
                - subscriber_id (str): subscriber id
                - service (str): service
                - status_message (str):
                - behavioral_status (str): online, idle, offline
                - status_intentional (str): custom statuses
                - last_activity_time (str): client defined time

        Returns:

        """

        bucket = self.get_bucket(kwargs['project_id'], 'status')
        status = bucket.get(kwargs['subscriber_id'])
        behavioral_status = kwargs.pop('behavioral_status')
        kwargs.pop('trackable', None)
        kwargs.pop('tracking_id', None)

        status.data = kwargs
        status.store()
        zlogger.info("Status is set to subscriber. Project id:{}, subscriber id:{}".format(
            kwargs['project_id'], kwargs['subscriber_id']))
        self.status_notify_contacts(behavioral_status=behavioral_status, **kwargs)

    def status_notify_contacts(self, **kwargs):
        """

        Args:
            kwargs (dict):
                - project_id (str): project id
                - subscriber_id (str): subscriber id
                - service (str): service
                - status_message (str):
                - behavioral_status (str): online, idle, offline
                - status_intentional (str): custom statuses
                - last_activity_time (str): client defined time

        Returns:

        """
        contacts_key = CACHE_CONTACTS.format(
            project_id=kwargs['project_id'],
            service=kwargs['service'],
            subscriber_id=kwargs['subscriber_id']
        )
        online_subscribers_key = CACHE_ONLINE_SUBSCRIBERS.format(
            project_id=kwargs['project_id'],
            service=kwargs['service']
        )
        idle_subscribers_key = CACHE_IDLE_SUBSCRIBERS.format(
            project_id=kwargs['project_id'],
            service=kwargs['service']
        )

        online_contacts_key = "{}:onlines".format(contacts_key)
        idle_contacts_key = "{}:idles".format(contacts_key)
        contacts_to_notify_key = "{}:Notify".format(contacts_key)

        self.cache.sinterstore(online_contacts_key, contacts_key, online_subscribers_key)
        self.cache.sinterstore(idle_contacts_key, contacts_key, idle_subscribers_key)
        self.cache.sunionstore(contacts_to_notify_key, online_contacts_key, idle_contacts_key)

        self.cache.delete(online_contacts_key, idle_contacts_key)

        # This log actually triggers the computationally intensive delivery operation on the event
        # processor side.
        zlogger.info(
            "Online contacts of subscriber:{subscriber_id} calculated at "
            "key:{contacts_to_notify_key} and they will be notified.".format(
                subscriber_id=kwargs['subscriber_id'],
                contacts_to_notify_key=contacts_to_notify_key),
            extra={
                "purpose": "event",
                "params": {
                    "project_id": kwargs['project_id'],
                    "subscriber_id": kwargs['subscriber_id'],
                    "service": kwargs['service'],
                    "status_message": kwargs['status_message'],
                    "behavioral_status": kwargs['behavioral_status'],
                    "status_intentional": kwargs['status_intentional'],
                    "last_activity_time": kwargs['last_activity_time'],
                    "contacts_to_notify_key": contacts_to_notify_key,
                },
                "method": "status_notify_contacts",
            }
        )

    def unsubscribe_channel_by_subscriber(self, **kwargs):
        """
        Subscriber's channel unsubscription.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - channel_id (str): channel id of whose is a subject of unsubscription event
                - subscriber_id (str): subscriber id of whose is a subject of unsubscription event
                - service (str): service
        Returns:
    
        """
        channel = self.get_obj(kwargs['project_id'], 'channel', kwargs['channel_id'])
        subscriber = self.get_obj(kwargs['project_id'], 'subscriber', kwargs['subscriber_id'])

        if not kwargs['subscriber_id'] in channel.data['subscribers']:
            zlogger.error(
                "Subscriber doesn't exist in channel's subscribers. Project id:{}, channel id:{}, "
                "subscriber id:{}".format(kwargs['project_id'], kwargs['channel_id'],
                                          kwargs['subscriber_id']))
            return {"error": {"code": -32006,
                              "message": "Subscriber doesn't exist in channel's subscribers."}}

        if not kwargs['channel_id'] in subscriber.data['channels']:
            zlogger.error(
                "Channel doesn't exist in subscriber's channels. Project id:{}, channel id:{}, "
                "subscriber id:{}".format(kwargs['project_id'], kwargs['channel_id'],
                                          kwargs['subscriber_id']))
            return {"error": {"code": -32006,
                              "message": "Channel doesn't exist in subscriber's channels."}}

        del channel.data['subscribers'][kwargs['subscriber_id']]
        del subscriber.data['channels'][kwargs['channel_id']]

        now = datetime.now().strftime(DATETIME_FORMAT)
        subscriber.data['last_update_time'] = now
        channel.data['last_update_time'] = now
        subscriber.store()
        channel.store()

        self.bindings_operation('delete_binding', kwargs['subscriber_id'], kwargs['channel_id'])
        zlogger.info("Subscriber unsubscribed from channel. Project id:{}, subscriber id:{}, "
                     "channel id:{}".format(kwargs['project_id'], subscriber.key, channel.key))

    def unsubscribe_subscriber_by_channel(self, **kwargs):
        """
        Channel's subscriber unsubscription.
        
        Args:
            kwargs (dict):
                - project_id (str): project id
                - channel_id (str): channel id of whose is a subject of unsubscription event
                - subscriber_id (str): subscriber id of whose is a subject of unsubscription event
                - service (str): service
        Returns:

        """
        self.unsubscribe_channel_by_subscriber(**kwargs)

    def get_me(self, **kwargs):
        """
        Returns the subscribers personal information about itself such as contacts, channels etc.

        Args:
            **kwargs :
                - project_id (str): project id
                - subscriber_id (str): subscriber id of whose is a subject of subscription event
                - service (str): service

        Returns:
            dict : subscriber object

        """
        subscriber_id = kwargs['subscriber_id']

        bucket = self.get_bucket(kwargs['project_id'], 'subscriber')
        subscriber = bucket.get(subscriber_id)

        if not subscriber.exists:
            zlogger.info(
                "Subscriber is being created for project: {project_id} with given subscriber "
                "id: {subscriber_id}!".format(
                    project_id=kwargs['project_id'], subscriber_id=subscriber_id))
            self.create_subscriber(subscriber, subscriber_id, kwargs['project_id'],
                                   kwargs['service'])

        zlogger.info(
            "Subscriber is being retrieved for project: {project_id} with given subscriber "
            "id: {subscriber_id}!".format(
                project_id=kwargs['project_id'], subscriber_id=subscriber_id))

        subscriber.data.update({
            "id": kwargs['subscriber_id'],
            "contacts": subscriber.data['contacts'],
            "channels": subscriber.data['channels'],
            "banned_channels": list(subscriber.data['banned_channels'].keys()),
            "banned_subscribers": list(subscriber.data['banned_subscribers'].keys()),
            "channel_invites": list(subscriber.data['channel_invites'].keys()),
            "channel_join_requests": list(subscriber.data['channel_join_requests'].keys()),
            "contact_requests_in": list(subscriber.data['contact_requests_in'].keys()),
            "contact_requests_out": list(subscriber.data['contact_requests_out'].keys()),
        })
        return subscriber.data

    def create_subscriber(self, subscriber, subscriber_id, project_id, service):
        """
        Creates an initial subscriber with given id.

        Args:
            subscriber (obj): an empty riak object of subscriber with given id
            subscriber_id (str): subscriber id
            project_id(str):
            service(str):

        Returns:

        """
        subscriber.data = {
            "id": subscriber_id,
            "contacts": {},
            "channels": {},
            "banned_channels": {},
            "banned_subscribers": {},
            "last_status_message": "",
            "channel_invites": {},
            "channel_join_requests": {},
            "contact_requests_in": {},
            "contact_requests_out": {},
        }
        subscriber.data.update(self.get_creation_info())
        subscriber.usermeta = {
            "project_id": project_id,
            "service": service,
            "bucket_name": 'subscriber',
        }
        subscriber.store()

    def create_channel_as_admin(self, **kwargs):
        """
        Channel creation as admin user.

        Args:
            kwargs (dict):
                - project_id (str): project id
                - admin_id (str): admin id of who creates the channel
                - channel_parameters (dict):
                    * name (str): Channel name
                    * description (str): Optional channel description
                    * type (str): 'public', 'public-group', 'private-group', 'announcement', 'private'
                    * subscribers (list): List of channel subsciber ids
                    * managers (list): List of channel manager ids
                - channel_id (str): Riak id of the channel will be created.

        Returns:

        """
        data = kwargs['channel_parameters']

        valid_managers = {}
        for manager_id in data['managers']:
            try:
                subscriber_obj = self.get_obj(kwargs['project_id'], 'subscriber', manager_id)
                valid_managers[manager_id] = subscriber_obj
            except KeyError:
                zlogger.info(
                    "Subscriber does not exist in project. Project_id: {}, Admin_id: {}, Account id: {} "
                    "Invalid Subscriber Id: {}".format(kwargs['project_id'],
                                                       kwargs['admin_id'],
                                                       kwargs['account_id'],
                                                       manager_id))

        if not valid_managers:
            zlogger.error(
                "Channel creation error.Managers ids does not exist in project subscribers. "
                "Project_id: {}, Admin_id: {}, Account_id: {}".format(kwargs['project_id'],
                                                                      kwargs['admin_id'],
                                                                      kwargs['account_id']))
            return {"error": {"code": -32006, "message": "Manager ids invalid"}}

        valid_subscribers = {}

        for subscriber_id in data['subscribers']:
            try:
                subscriber_obj = self.get_obj(kwargs['project_id'], 'subscriber', subscriber_id)
                valid_subscribers[subscriber_id] = subscriber_obj
            except KeyError:
                zlogger.info(
                    "Subscriber does not exist in project. Project_id: {}, Admin_id: {}, Account id: {} "
                    "Invalid Subscriber Id: {}".format(kwargs['project_id'],
                                                       kwargs['admin_id'],
                                                       kwargs['account_id'],
                                                       subscriber_id))

        channel_bucket = self.get_bucket(kwargs['project_id'], 'channel')
        channel = channel_bucket.get(kwargs['channel_id'])

        # if the sent channel id is already exists in riak
        if channel.exists:
            channel = channel_bucket.new()

        data['managers'] = {}
        data['subscribers'] = {}
        for manager_id, manager_obj in valid_managers.items():
            data['managers'][manager_id] = ""
            data['subscribers'][manager_id] = ""
            manager_obj.data['channels'][channel.key] = ""

        for subscriber_id, subscriber_obj in valid_subscribers.items():
            data['subscribers'][subscriber_id] = ""
            subscriber_obj.data['channels'][channel.key] = ""

        # select first manager to become channel owner
        data['owner'] = {next(iter(valid_managers.keys())): ""}
        data['invitees'] = {}
        data['join_requests'] = {}
        data['banned_subscribers'] = {}
        data.update(self.get_creation_info())

        channel.data = data
        channel.usermeta = {
            "project_id": kwargs['project_id'],
            "service": kwargs['service'],
            "bucket_name": 'channel',
        }
        channel.store()
        self.bindings_operation('create_binding', data['owner'], channel.key)

        valid_subscribers.update(valid_managers)
        for subscriber_id, subscriber_obj in valid_subscribers.items():
            subscriber_obj.store()
            self.bindings_operation('create_binding', subscriber_id, channel.key)

        zlogger.info(
            "Channel is created as admin user. Project id:{}, channel id:{}".format(
                kwargs['project_id'], channel.key),
            extra={
                "project_id": kwargs['project_id'],
                "service": kwargs['service'],
                "purpose": "counter"})

    def update_channel_as_admin(self, **kwargs):
        """
        Channel update as admin user.

        Args:
            kwargs (dict):
                - project_id (str): project id
                - admin_id (str): admin id of who updates the channel
                - channel_parameters (dict):
                    * name (str): Channel name
                    * description (str): Optional channel description
                    * type (str): 'public', 'public-group', 'private-group', 'announcement', 'private'
                    * subscribers (list): List of channel subsciber ids
                    * managers (list): List of channel manager ids
                - channel_id (str): Riak id of the channel

        Returns:

        """
        data = kwargs['channel_parameters']

        channel = self.get_obj(kwargs['project_id'], 'channel', kwargs['channel_id'])
        channel_subscribers = channel.data["subscribers"]

        new_subscribers = data["subscribers"]

        channel_subs_set = set(channel_subscribers.keys())
        new_subs_set = set(new_subscribers)

        added_subscribers = list(new_subs_set - channel_subs_set)
        removed_subs = list(channel_subs_set - new_subs_set)

        new_valid_subscribers = {}
        valid_managers = {}

        for manager_id in data["managers"]:
            try:
                subscriber_obj = self.get_obj(kwargs['project_id'], 'subscriber', manager_id)
                valid_managers[manager_id] = subscriber_obj
            except KeyError:
                zlogger.info(
                    "Subscriber does not exist in project. Project_id: {}, Admin_id: {}, Account id: {} "
                    "Invalid Subscriber Id: {}".format(kwargs['project_id'],
                                                       kwargs['admin_id'],
                                                       kwargs['account_id'],
                                                       manager_id))

        if not valid_managers:
            zlogger.error(
                "Channel creation error.Managers ids does not exist in project subscribers. "
                "Project_id: {}, Admin_id: {}, Account_id: {}".format(kwargs['project_id'],
                                                                      kwargs['admin_id'],
                                                                      kwargs['account_id']))
            return {"error": {"code": -32006, "message": "Manager ids invalid"}}

        for subscriber_id in added_subscribers:
            try:
                subscriber_obj = self.get_obj(kwargs['project_id'], 'subscriber', subscriber_id)
                new_valid_subscribers[subscriber_id] = subscriber_obj
            except KeyError:
                zlogger.info(
                    "Subscriber does not exist in project. Project_id: {}, Admin_id: {}, Account id: {} "
                    "Invalid Subscriber Id: {}".format(kwargs['project_id'],
                                                       kwargs['admin_id'],
                                                       kwargs['account_id'],
                                                       subscriber_id))

        for subscriber_id in removed_subs:
            subscriber_obj = self.get_obj(kwargs['project_id'], 'subscriber', subscriber_id)
            del subscriber_obj.data['channels'][kwargs['channel_id']]
            del channel.data['subscribers'][subscriber_id]

            subscriber_obj.store()
            self.bindings_operation('delete_binding', subscriber_id, kwargs['channel_id'])

        new_valid_subscribers.update(valid_managers)
        for subscriber_id, subscriber_obj in new_valid_subscribers.items():
            channel.data["subscribers"][subscriber_id] = ""
            subscriber_obj.data["channels"][kwargs["channel_id"]] = ""
            subscriber_obj.store()
            self.bindings_operation('create_binding', subscriber_id, channel.key)

        for manager_id in valid_managers.keys():
            channel.data["managers"][manager_id] = ""

        if next(iter(channel.data["owner"].keys())) not in valid_managers.keys():
            # if channel owner is not in new channel managers
            # then first valid manager become channel owner
            del channel.data["owner"]
            channel.data["owner"] = {
                next(iter(valid_managers.keys())): ""
            }

        channel.data["name"] = data["name"]
        channel.data["description"] = data["description"]
        channel.data["type"] = data["type"]

        channel.store()

        zlogger.info(
            "Channel is updated by admin user. Project id:{}, channel id:{}, Admin id: {}".format(
                kwargs['project_id'], channel.key, kwargs['admin_id']),
            extra={
                "project_id": kwargs['project_id'],
                "service": kwargs['service'],
                "purpose": "counter"})

    def add_subscribers_to_channel_as_admin(self, **kwargs):
        """
        Add subscribers to channel as admin user

        Args:
            kwargs (dict):
                - project_id (str): project id
                - admin_id (str): admin id of who creates the channel
                - subscribers (list): List of subscriber ids
                - channel_id (str): Riak id of the channel
        Returns:
        """
        channel = self.get_obj(kwargs['project_id'], 'channel', kwargs['channel_id'])
        channel_subscribers = channel.data["subscribers"]

        new_subscribers = kwargs.get("subscribers")

        channel_subs_set = set(channel_subscribers.keys())
        new_subs_set = set(new_subscribers)

        added_subscribers = list(new_subs_set - channel_subs_set)

        valid_subscribers = {}
        for subscriber_id in added_subscribers:
            try:
                subscriber_obj = self.get_obj(kwargs['project_id'], 'subscriber', subscriber_id)
                valid_subscribers[subscriber_id] = subscriber_obj
            except KeyError:
                zlogger.info(
                    "Subscriber does not exist in project. Project_id: {}, Admin_id: {}, Account id: {} "
                    "Invalid Subscriber Id: {}".format(kwargs['project_id'],
                                                       kwargs['admin_id'],
                                                       kwargs['account_id'],
                                                       subscriber_id))

        for subscriber_id, subscriber_obj in valid_subscribers.items():
            channel.data["subscribers"][subscriber_id] = ""
            subscriber_obj.data["channels"][kwargs["channel_id"]] = ""
            subscriber_obj.store()
            self.bindings_operation('create_binding', subscriber_id, channel.key)

        channel.store()

        zlogger.info(
            "Subscriber list added to channel.Channel is updated by admin user. Project id:{}, channel id:{}, Admin id: {}".format(
                kwargs['project_id'], channel.key, kwargs['admin_id']),
            extra={
                "project_id": kwargs['project_id'],
                "service": kwargs['service'],
                "purpose": "counter"})

    def add_contact_to_subscriber_as_admin(self, **kwargs):
        """
        Add contact to subscriber as admin user

        Args:
            kwargs (dict):
                - project_id (str): project id
                - admin_id (str): admin id of who creates the channel
                - contact_parameters (dict):
                    * subscriber_id (str): User id of subscriber to be contact given contact list
                    * contactListToAdd (list): List of subscriber id to add
                - channel_id (str): Riak id of the channel

        Returns:

        """
        data = kwargs['contact_parameters']

        target_subscriber_id = data['subscriber_id']
        target_subscriber = self.get_obj(kwargs['project_id'], 'subscriber', target_subscriber_id)

        for subscriber_id in data["contact_list_to_add"]:
            try:
                now = datetime.now().strftime(DATETIME_FORMAT)
                subscriber_obj = self.get_obj(kwargs['project_id'], 'subscriber', subscriber_id)

                subscriber_obj.data['contacts'][target_subscriber_id] = ""
                target_subscriber.data['contacts'][subscriber_id] = ""

                subscriber_obj.data['last_update_time'] = now
                subscriber_obj.store()

                zlogger.info("{} subscriber become contact with {} subscriber. "
                             "Project id:{}".format(target_subscriber_id, subscriber_id,
                                                    kwargs['project_id'],))

            except KeyError:
                zlogger.info(
                    "Key error occured in add_contact_to_subscriber_as_admin method. "
                    "Subscriber does not exist in project. "
                    "Project_id: {}, Admin_id: {}, Account id: {} "
                    "Invalid Subscriber Id: {}".format(kwargs['project_id'],
                                                       kwargs['admin_id'],
                                                       kwargs['account_id'],
                                                       subscriber_id))

        now = datetime.now().strftime(DATETIME_FORMAT)
        target_subscriber.data['last_update_time'] = now
        target_subscriber.store()

    def update_channel_last_read_message(self, **kwargs):
        """
        Update subscriber channel last read message id

        Args:
            kwargs (dict):
                - project_id (str): project id
                - subscriber_id (str): subscriber id
                - service (str): service
                - channel_id (str): channel id


        Returns:
        """
        channel_id = kwargs['channel_id']
        subscriber_id = kwargs['subscriber_id']
        last_read_message_id = kwargs['lastReadMessageId']
        subscriber_obj = self.get_obj(kwargs['project_id'], 'subscriber', subscriber_id)
        if channel_id not in subscriber_obj.data["channels"]:
            err_msg = "Subscriber is not channel member. Project Id: {}, Subscriber Id: {}, " \
                      "Channel Id: {}".format(kwargs['project_id'], subscriber_id, channel_id)
            zlogger.error(err_msg)
            return {"error": {"code": -32002, "message": err_msg}}

        message_bucket = self.get_bucket(kwargs['project_id'], 'message',
                                         bucket_type=RABBIT_HOOK_BUCKET_TYPE)
        message = message_bucket.get(last_read_message_id)
        if not message.exists:
            err_msg = "Message object not found. Project Id: {}, Message Id: {}".format(kwargs['project_id'], last_read_message_id)
            zlogger.error(err_msg)
            return {"error": {"code": -32002, "message": err_msg}}
        elif message.data['channel'] != channel_id:
            err_msg = "Message not found in channel messages. Project Id: {}, " \
                      "Message Id: {}, Channel Id: {}".format(kwargs['project_id'],
                                                              channel_id, last_read_message_id)
            zlogger.error(err_msg)
            return {"error": {"code": -32002, "message": err_msg}}

        subscriber_obj.data["channels"][channel_id] = {
            "lastReadMessageId": last_read_message_id
        }
        subscriber_obj.store()
        zlogger.info("Last read channel message updated. Subscriber Id: {}, Channel Id: {}, "
                     "Project Id: {}".format(subscriber_id, channel_id, kwargs['project_id']))

    def get_unread_message_number(self, **kwargs):
        """
        get subscriber channel unread message number

        Args:
            kwargs (dict):
                - project_id (str): project id
                - subscriber_id (str): subscriber id
                - service (str): service
                - channel_id (str): channel id


        Returns:
        """
        channel_id = kwargs['channel_id']
        subscriber_id = kwargs['subscriber_id']
        project_id = kwargs['project_id']

        subscriber_obj = self.get_obj(project_id, 'subscriber', subscriber_id)
        if channel_id not in subscriber_obj.data["channels"]:
            err_msg = "Subscriber is not channel member. Project Id: {}, Subscriber Id: {}, " \
                      "Channel Id: {}".format(project_id, subscriber_id, channel_id)
            zlogger.error(err_msg)
            return {"error": {"code": -32002, "message": err_msg}}

        subscriber_channel_data = subscriber_obj.data["channels"][channel_id]

        if not subscriber_channel_data or (
                subscriber_channel_data is dict and not subscriber_channel_data.get("lastReadMessageId", None)):
            return {
                "number_of_unread_message": 0
            }

        last_read_message_id = subscriber_channel_data.get("lastReadMessageId")
        message_obj = self.get_obj(kwargs['project_id'], 'message', last_read_message_id,
                                   bucket_type=RABBIT_HOOK_BUCKET_TYPE)

        message_creation_time_str = message_obj.data["creation_time"]
        datetime_object = datetime.strptime(message_creation_time_str, DATETIME_FORMAT)
        message_timestamp = format(datetime_object.timestamp(), '.7f')
        message_index = int(self.last) - int("".join(str(message_timestamp).split('.')))

        bucket = self.get_bucket(project_id, 'message', bucket_type=RABBIT_HOOK_BUCKET_TYPE)

        message_index_format = '{}_{}'.format(channel_id, message_index - 1)
        first = '{}_{}'.format(channel_id, self.first)

        messages_data = bucket.get_index('message_bin', first, message_index_format,
                                         max_results=100)
        return {
            "number_of_unread_message": len(messages_data.results),
            "lastReadMessageId": last_read_message_id
        }

    def update_contact_last_read_message(self, **kwargs):
        """
        Update subscriber contact last read message id

        Args:
            kwargs (dict):
                - project_id (str): project id
                - subscriber_id (str): subscriber id
                - service (str): service
                - contact_id (str): contact id


        Returns:
        """
        contact_id = kwargs['contact_id']
        subscriber_id = kwargs['subscriber_id']
        last_read_message_id = kwargs['lastReadMessageId']
        subscriber_obj = self.get_obj(kwargs['project_id'], 'subscriber', subscriber_id)
        channel_id = kwargs['channel_id']
        if contact_id not in subscriber_obj.data["contacts"]:
            err_msg = "Subscriber is not contact with given subscriber. Project Id: {}, " \
                      "Subscriber Id: {}, Contact Id: {}".format(kwargs['project_id'],
                                                                 subscriber_id, contact_id)
            zlogger.error(err_msg)
            return {"error": {"code": -32002, "message": err_msg}}

        message_bucket = self.get_bucket(kwargs['project_id'], 'message',
                                         bucket_type=RABBIT_HOOK_BUCKET_TYPE)
        message = message_bucket.get(last_read_message_id)
        if not message.exists:
            err_msg = "Message object not found. Project Id: {}, " \
                      "Message Id: {}".format(kwargs['project_id'], last_read_message_id)
            zlogger.error(err_msg)
            return {"error": {"code": -32002, "message": err_msg}}
        elif message.data['channel'] != channel_id:
            err_msg = "Message not found in channel messages. Project Id: {}, " \
                      "Message Id: {}, Channel Id: {}".format(kwargs['project_id'],
                                                              channel_id, last_read_message_id)
            zlogger.error(err_msg)
            return {"error": {"code": -32002, "message": err_msg}}

        subscriber_obj.data["contacts"][contact_id] = {
            "lastReadMessageId": last_read_message_id
        }
        subscriber_obj.store()
        zlogger.info("Last read contact"
                     " message updated. Subscriber Id: {}, Channel Id: {}, "
                     "Project Id: {}, Message Id: {}".format(subscriber_id, channel_id,
                                                             kwargs['project_id'],
                                                             last_read_message_id))

    def get_unread_contact_message_number(self, **kwargs):
        """
        get subscriber contact unread message number

        Args:
            kwargs (dict):
                - project_id (str): project id
                - subscriber_id (str): subscriber id
                - service (str): service
                - contact_id (str): contact id
                - channel_id (str): channel id


        Returns:
        """
        contact_id = kwargs['contact_id']
        channel_id = kwargs['channel_id']
        subscriber_id = kwargs['subscriber_id']
        project_id = kwargs['project_id']

        subscriber_obj = self.get_obj(project_id, 'subscriber', subscriber_id)
        if contact_id not in subscriber_obj.data["contacts"]:
            err_msg = "Subscriber is not contact with given subscriber. Project Id: {}, " \
                      "Subscriber Id: {}, Contact Id: {}".format(kwargs['project_id'],
                                                                 subscriber_id, contact_id)
            zlogger.error(err_msg)
            return {"error": {"code": -32002, "message": err_msg}}

        subscriber_contact_data = subscriber_obj.data["contacts"][contact_id]

        if not subscriber_contact_data or (
                subscriber_contact_data is dict and not subscriber_contact_data.get("lastReadMessageId", None)):
            return {
                "number_of_unread_message": 0
            }

        last_read_message_id = subscriber_contact_data.get("lastReadMessageId", None)
        message_obj = self.get_obj(kwargs['project_id'], 'message', last_read_message_id,
                                   bucket_type=RABBIT_HOOK_BUCKET_TYPE)

        message_creation_time_str = message_obj.data["creation_time"]
        datetime_object = datetime.strptime(message_creation_time_str, DATETIME_FORMAT)
        message_timestamp = format(datetime_object.timestamp(), '.7f')
        message_index = int(self.last) - int("".join(str(message_timestamp).split('.')))

        bucket = self.get_bucket(project_id, 'message', bucket_type=RABBIT_HOOK_BUCKET_TYPE)

        message_index_format = '{}_{}'.format(channel_id, message_index - 1)
        first = '{}_{}'.format(channel_id, self.first)

        messages_data = bucket.get_index('message_bin', first, message_index_format,
                                         max_results=100)
        return {
            "number_of_unread_message": len(messages_data.results),
            "lastReadMessageId": last_read_message_id
        }

