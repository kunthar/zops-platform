# Cache Objects
Cache key strings must have been prefixed by tenant, account, project
and service identifiers, such as:

```
P:456:S:789
```

So, a user status key becomes following:

```
P:456:S:789:St:123456789
```


## User Status
It keeps status both behavioral and intentional data. It expires in 10
minutes. Absence of this key means the user is or has become offline.

| Name         | Description                                         |
|--------------|-----------------------------------------------------|
| PREFIX       | St                                                  |
| EXPIRE TIME  | 600 seconds                                         |
| KEY          | prefix + user_id, e.g.     St:123456789             |
| VALUE        | status and status message                           |
| EXAMPLE      | "St:123456789": {...}                               |

`Status` resource reads and writes this data. If it is not exist for a
user, it is set or updated whenever the user login and send message,
or change intentional status by client.


## Contact List
It keeps a list if contacts (friends and channels) of a user. Never
expires unless it is modified  or destroyed by service.

| Name         | Description                                                  |
|--------------|--------------------------------------------------------------|
| PREFIX       | C                                                            |
| EXPIRE TIME  | Never                                                        |
| KEY          | prefix + user_id, e.g. C:123456789                           |
| VALUE        | list of `u` or `c` prefixed ids of other users and channels. |
| EXAMPLE      | "C:123456789": ["u_1", "u_2", "u_3", "c_1",]                 |


Messaging App use this data to decide if sender is allowed to send
message to receiver. Also `Contact` REST responses read this data. If it
is not set for a user, it is set by reading `contacts` and `chanells`
field of `User` model.

## Channel
Channel informations should be cached when a subscriber ask for messages
of the channel.

### Channel General
Channel's non-data-structured attributes, such as name, description,
type and lastMessage are kept in a [Redis hash](https://redis.io/topics/data-types-intro#redis-hashes).
The structure in Redis will be the same with a python dict.

#### Properties
| Name          | Description                                                  |
|---------------|--------------------------------------------------------------|
| KEY_STRUCTURE | Ch:{channel_id}                                              |
| EXPIRE TIME   | 10800 seconds (3 hours)                                      |
| VALUE         | dict of channel general fields                               |

#### Example:
```python
{
    # ...
    "Ch:123456": {
        "name": "CHANNEL_NAME",
        "description": "CHANNEL_DESCRPTION",
        "type": "CHANNEL_TYPE",
        "lastMessage": "LAST_MESSAGE"
    }
    # ...
}
    
```

### Channel: Subscribers, Owners, Managers, BannedSubscribers
Properties are the same except key structure. Key structure must be
considered as the field name for each. For instance, while subscriibers'
key structure is *Channel:{channel_id}:Subscribers*, owners' key
structure must be *Channel:{channel_id}:Owners*.

#### Subscribers
It keeps ids of subscribers of channel in a [Redis set](https://redis.io/topics/data-types-intro#redis-sets).

##### Properties
| Name          | Description                                                  |
|---------------|--------------------------------------------------------------|
| KEY_STRUCTURE | Ch:{channel_id}:Sub                                          |
| EXPIRE TIME   | 10800 seconds (3 hours)                                      |
| VALUE         | set of subscriber ids                                        |

##### Examples:
```python
{
    # ...
    "Ch:123456:Sub": {"subscriberId4","subscriberId1","subscriberId3","subscriberId2"},
    "Ch:123456:Own": {"subscriberId1"},
    "Ch:123456:Man": {"subscriberId4","subscriberId1"},

    "Ch:123456:BanSub": {"subscriberId9","subscriberId10"},
    # ...    
}
```

#### Channel: JoinRequests, Invites

Keeps the invite ids of the subscribers' request to join to the channel
and channel's invites to subscribers
in a [Redis set](https://redis.io/topics/data-types-intro#redis-sets).

##### Properties
| Name          | Description                                                  |
|---------------|--------------------------------------------------------------|
| KEY_STRUCTURE | Channel:{channel_id}:JoinRequests                            |
| EXPIRE TIME   | 10800 seconds (3 hours)                                      |
| VALUE         | set of invite ids                                        |

##### Example:
```python
{
    # ...
    "Ch:123456:JR": {"inviteId1","inviteId2","inviteId12","inviteId3"},
    "Ch:123456:Inv": {"inviteId61","inviteId22"},
    # ...    
}
```

## Subscriber

### Subscriber: Contacts, Channels, BannedChannels, BannedSubscribers, Invites, JoinRequests

Keeps subscriber's structured fields.

#### Properties
| Name          | Description                                                  |
|---------------|--------------------------------------------------------------|
| KEY_STRUCTURE | Sub:{subscriber_id}:C                                        |
| EXPIRE TIME   | 10800 seconds (3 hours)                                      |
| VALUE         | set of ids                                                   |

#### Example:
```python
{
    # ...
    "Sub:123456:C": {"subscriberId1","subscriberId3","subscriberId2",},
    "Sub:123456:Ch": {"channel1","channel3","channel4","channel2",},
    "Sub:123456:BanCh": {"channel5","channel17","channel22","channel0",},
    "Sub:123456:BanSub": {"subscriberId12","subscriberId32","subscriberId22",},
    "Sub:123456:Inv": {"inviteId1","inviteId2","inviteId3",},
    "Sub:123456:JR": {"inviteId11","inviteId21","inviteId31",},
    # ...    
}
```


### Online Subscribers
Online subscribers of a service is cached under a key like following:

```
"P:456:S:789:OnSub": {"subscriberId1","subscriberId3","subscriberId2",}
```


## Refresh Token
Initially SaaS management generates a refresh token to allow user to generate
own token pairs. This initial token expires in 30 seconds. Users must ask
for new tokens within this short period.

```
"P:456:S:789:RefTok:{temp_token}": {"tenant:"123", "account":"007", "project":"456", "service":"push", "user":"user_id"}
```

## Access Token
Service Auth generates access tokens to allow user to consume resoures.
Tokens are valid for 3 hours. User must renew with refresh token.

```
"P:456:S:789:AccTok:{user_token}": {"tenant:"123", "account":"007", "project":"456", "service":"push", "user":"user_id"}
```

`service` key can be one of the 'push', 'roc' or 'sms'.


## Token Keys
Token keys map is an hashmap object to keep actual key of user token.

TokensKeys:{
    {token_1}: Projects:456:Services:789:RefreshTokens:{token_1},
    {token_2}: Projects:456:Services:789:AccessTokens:{token_2},
}



Google Server API Key
Google Project Number (Sender ID) 
APNS iOS Push Certificate
