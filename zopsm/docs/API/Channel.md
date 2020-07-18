# Channel 

Channels correspond chat rooms. Messages can be sent and recieved by its subscribers. There are 4 types of channels:

* __Public Group__:
  Any authenticated user can join public channels and can post and read any message without authorization. All
  subscribers are both consumer and producer at the same time.

  * __Private Group__:
  Only authorized users of public group channels can post and read messages. All subscribers are both consumer
  and producer at the same time.

  * __Invisible Private Group__:
  Invisible Private Group

  * __Public Announcement__:
  All authenticated users of announcement channels can read messages, since only one or some of them can post.

  * __Private Announcement__:
  All authorized users of announcement channels can read messages, since only one or some of them can post.

  * __Invisible Private Announcement__:
  Invisible Private Announcement

  * __Private Chat__:
  Private channels have only two subscribers who can post and read messages.


__Attributes__:

| attr              | description                                           |
| ----------------- | ------------------------------------------------------|
| name              | name of channel                                       |
| description       | a short description of channels                       |
| type              | type of channel described above                       |
| lastMessage       | last message sting text, sender, date                 |
| serviceId         | service                                               |
| subscribers       | list of channels' subscribers                         |
| owner             | subscriber who owns channel                           |
| managers          | subscribers who can manage channel                    |
| invites           | subscribers who can join channel                      |
| joinRequests      | the requests sent by candidate subscribers of channel |
| bannedSubscribers | subscribers who banned from channel                   |


__URLs:__
  * /channels?{params}
  * /channels/{id}

__Params:__

  * Required: `serviceId`

__Allowed Methods:__

  * GET:
    Retrieves list of channels paginated by 10 or retrieves a single channel by given id
    __filter params__: `type`
    __search params__: `name`, `description`

  * PUT:
    Update an existing channel by `name`, `description`, and `type`
    Public channels can be converted Public Group or Private Group.

  * DELETE:
    Delete an existing channel

  * POST:
    Create a new channel
