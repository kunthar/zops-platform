# Client 

Client is an application coded in mobile or web. Client application reflects all abilities of zopsm platform.

__Authentication__:


__Authorization__:


__Messages__:


__Presence__:






__Attributes__:

| attr               | description                            |
| ------------------ | -------------------------------------- |
| message_title      | generally null, can be used rarely in more complex scenarios|
| message_body       | message content, max 1K string.                       |
| sender             | subscriber id of message sender         |
| receiver           | subscriber id of message receiver        |
| sent_time          | time of client device, UTC with TZ data        |
| channel            | channel_id of which channel the message is sent to.      |
| service_id         | service                                |



List messages or get one exact message identified by `key`

__URLs:__
  * /messages
  * /message/{key}

__Params:__

  * Required:

  * Optional
  key=[alphanumeric]
  example: /message/JIO7A02J1IY

__Allowed Methods:__

  * GET:
    Retrieves list of messages of {user_id} paginated by 10

  * PUT:
    Update an existing message

  * DELETE:
    Delete an existing message

  * POST:
    Add a new message





    /contacts/{user_id}/{contact}


    - Contact List
      - Contacts
        - Name
        - Icon
        - Last Message Text
        - Last Message Time
        - Last Message Sender Name if group

    - Get Channel
      - Name
      - Icon Url
      - Last Messsage Time
      - Messages
        - Message one
          - Sender
          - Icon Url
          - Text
          - Time
          -

    Messaging

    Management SAAS OP

    Tenant
    Chat User
    Chat Channel
    Developers

    Tekil Kullanicilari
