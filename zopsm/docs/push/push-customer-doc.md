# API Reference (Draft v0.2)

## Resources 

### Client

Client resource represents client-application pair in the system. Each client application must 
register itself to the push notification server of its own platform and obtain a token after 
registration or whenever token changes. 

Client application is responsible for sending this token to provider when it is obtained. 
On each delivery of the token, the client must pass some information to make itself classifiable by 
giving provider some information about itself.
 
#### Attributes:

| attr         | description                                           |
| ------------ | ------------------------------------------------------|
| clientId     | unique identifier of clients                          |
| token        | token obtained from client's notification service     | 
| language     | client's language                                     |
| appVersion   | version of client application                         |
| deviceType   | device type of application runs on                    |
| email        | email                                                 |
| country      | country                                               |
| osVersion    | os version                                            |


#### URLs:
  * /push/clients
  * /push/clients/{client_id}

#### Allowed Methods:
| Resource URI                 | Method | Description                              |
|------------------------------|--------|------------------------------------------|
| /v1/push/clients             | POST   | Register a device to the provider        |
| /v1/push/clients             | GET    | Get list of devices                      |
| /v1/push/clients/{client_id} | PUT    | Updates a device's information           |
| /v1/push/clients/{client_id} | GET    | Single get operation                     |
| /v1/push/clients/{client_id} | DELETE | Delete operation to unsubscribe a client |

### Message

#### Attributes:

| attr        | description                                           |
| ----------- | ------------------------------------------------------|
| id          | unique identifier of messages                         |
| sender      | sender of the message                                 |
| title       | title of message                                      |
| body        | body of message                                       |
| type        | automated, scheduled, ordinary                        |
| language    | language                                              |
| icon        | icon                                                  |
| image       | image                                                 |
| badge       | badge                                                 |
| segment     | segments of the message                               |

Additional attributes will be added to take required actions with respect to `type`.

#### URLs:
  * /push/messages
  * /push/messages/{message_id}

#### Allowed Methods:
| Resource URI                   | Method | Description                                                        |
|--------------------------------|--------|--------------------------------------------------------------------|
| /v1/push/messages              | POST   | Posts a push message                                               |
| /v1/push/messages              | GET    | Gets a list of push messages                                       |
| /v1/push/messages/{message_id} | GET    | Get a single push message                                          |
| /v1/push/messages/{message_id} | DELETE | Delete a single push message if its type is automated or scheduled |
| /v1/push/messages/{message_id} | PUT    | Update a single push message if its type is automated or scheduled |

### Acknowledgement

Clients use to notify provider about that it received the message.
 
#### Attributes:

| attr        | description                                           |
| ----------- | ------------------------------------------------------|
| message_id  | unique identifier of messages                         |
| client_id   | unique identifier of client                           |

#### URLs:
  * /push/messages/acknowledgement

#### Allowed Methods:
| Resource URI                       | Method | Description                                         |
|------------------------------------|--------|-----------------------------------------------------|
| /v1/push/messages/acknowledgements | POST   | Acknowledgement about delivery of message to client |


### Segment

Segments are user or client groups created by adding filters.
 
#### Attributes: 

| attr        | description                                                       |
| ----------- | ------------------------------------------------------------------|
| id          | unique identifier of segments                                     |
| name        | name of the segment                                               |
| residents   | residents is an object that defines the filters of these segments |

#### URLs:
  * /push/segments
  * /push/segments/{segment_id}
 
#### Allowed Methods:
| Resource URI                   | Method | Description              |
|--------------------------------|--------|--------------------------|
| /v1/push/segments              | POST   | Creates a segment        |
| /v1/push/segments              | GET    | Returns list of segments |
| /v1/push/segments              | PATCH  | Creates segments         |
| /v1/push/segments/{segment_id} | GET    | Returns a single segment |
| /v1/push/segments/{segment_id} | PUT    | Updates a given segment  |
| /v1/push/segments/{segment_id} | DELETE | Removes a given segment  |



#### Sending Filters:

Each filter can be thought as sets of users/clients. So, set operations can be applied on filters.
Following is a list of operators which can be applied to filters:
- intersection 
- union 
- difference 

##### Residents Object

If only one operator will be applied on the return values of the given expressions, following can 
be sent.

```json
{
    "residents": {
        "operator": "intersection",
        "expressions": [
          {
            "key": "level", 
            "relation": "=", 
            "value": "10"
          }, 
          {
            "key": "amount_spent", 
            "relation": ">", 
            "value": "0"
          }
        ]
    }
}
```
Residents in the above json represents the intersection of two sets
1. Set of users/clients having tag `level` with value "10", and
2. Set of users/clients having tag `amount_spent` with value greater than 0

Following schema is also valid:

```json
{
    "residents": {
        "operator": "intersection",
        "first": {
            "key": "level", 
            "relation": "=", 
            "value": "10"
        }, 
        "second": {
            "key": "amount_spent", 
            "relation": ">", 
            "value": "0"
        }
    }
}
```
> `difference` operator can only be used as in the schema above.


If more complicated logic is required like nested expressions:

```json

{
    "residents": {
        "operator": "union",
        "first": {
          "key": "level", 
          "relation": "=", 
          "value": "10"
        },
        "second": {
          "operator": "difference",
          "first": {
              "key": "age", 
              "relation": "in", 
              "value": [15, 25]
          }, 
          "second": {
              "key": "amount_spent", 
              "relation": ">", 
              "value": "0"
          }
        }
    }
}
```
Residents in the above json represents the union of two sets
1. Set of users/clients having tag `level` with value "10", and
2. Difference set of sets having tag `age` within range [15, 25] and `amount_spent` value 
with greater than 0

### Tags

Tags are customer defined fields for users/clients. 

#### User Tags 

Tags that are related to user, and consequently all clients of the user.

##### URLs:
  * /push/tags/user
  * /push/tags/user/{user_id}
 
##### Allowed Methods:
| Resource URI                 | Method | Description                                                                                                      |
|------------------------------|--------|------------------------------------------------------------------------------------------------------------------|
| /v1/push/tags/user           | POST   | Tags a user with given id and given tag in the body                                                              |
| /v1/push/tags/user           | GET    | Gets all tags of the user specified with param `user`                                                            |
| /v1/push/tags/user/{user_id} | GET    | Gets a single tag of user with given user_id, and a parameter `tagKey`                                           |
| /v1/push/tags/user/{user_id} | DELETE | Deletes all tags of user with given user_id if not passed a parameter `tagKey`, removes specified key otherwise  |
| /v1/push/tags/user/{user_id} | PUT    | Updates a single tag of user with given user_id, if key not exists in tags of user it does nothing               |



##### `POST /tags/user`

Tag a user.

* `Content-Type`: `"application/json"`
* `Accept`: `"application/json"`

Include the `userId`, `key` and `value` text in the body:

```json
{
  "userId": "USER_ID",
  "key": "client-type",
  "value": "android",
  "type": "str"
}
```

###### Example response

* `Status`: `202`
* `Content-Type`: `"application/json"`

```json
{
  "userId": "USER_ID",
  "key": "client-type",
  "value": "android",
  "type": "str"
}
```


#### Client Tags 

Tags that are related to user, and consequently all clients of the user.

##### URLs:
  * /push/tags/client
  * /push/tags/client/{client_id}
 
##### Allowed Methods:
| Resource URI                     | Method | Description                                                                                                          |
|----------------------------------|--------|----------------------------------------------------------------------------------------------------------------------|
| /v1/push/tags/client             | POST   | Tags a client with given id and given tag in the body                                                                |
| /v1/push/tags/client             | GET    | Gets all tags of the client specified with param `client`                                                            |
| /v1/push/tags/client/{client_id} | GET    | Gets a single tag of client with given `client_id`, and a parameter `tagKey`                                         |
| /v1/push/tags/client/{client_id} | DELETE | Deletes all tags of client with given `client_id if not passed a parameter `tagKey`, removes specified key otherwise |
| /v1/push/tags/client/{client_id} | PUT    | Updates a single tag of client with given `client_id`, if key does not exist in tags of user it does nothing         |

##### `POST /tags/client`

Tag a client.

* `Content-Type`: `"application/json"`
* `Accept`: `"application/json"`

Include the `clientId`, `key` and `value` text in the body:

```json
{
  "clientId": "CLIENT_ID",
  "key": "client-type",
  "value": "android",
  "type": "str"
}
```

###### Example response

* `Status`: `202`
* `Content-Type`: `"application/json"`

```json
{
  "clientId": "CLIENT_ID",
  "key": "client-type",
  "value": "android",
  "type": "str"
}
```




| Resource URI                       | Method  | Description                                           | Params   |
|------------------------------------|---------|-------------------------------------------------------|----------|
| /v1/push/clients                   | POST    | Register a device to the provider                     |          |
| /v1/push/clients                   | PATCH   | Register devices to the provider                      |          |
| /v1/push/clients                   | GET     | Get list of devices                                   |          |
| /v1/push/clients/{client_id}       | PUT     | Updates a device's information                        |          |
| /v1/push/clients/{client_id}       | GET     | Single get operation                                  |          |
| /v1/push/messages                  | POST    | Posts a push message                                  |          |
| /v1/push/messages                  | GET     | Gets a list of push messages                          |          |
| /v1/push/messages/{message_id}     | GET     | Get a single push message                             |          |
| /v1/push/messages/acknowledgements | POST    | Acknowledgement about delivery of message to client   |          |
| /v1/push/segments                  | POST    | Creates a segment                                     |          |
| /v1/push/segments                  | GET     | Returns list of segments                              |          | 
| /v1/push/segments                  | PATCH   | Creates a segments                                    |          |
| /v1/push/segments/{segment_id}     | GET     | Returns a single segment                              |          | 
| /v1/push/segments/{segment_id}     | PUT     | Updates a given segment                               |          |
| /v1/push/segments/{segment_id}     | DELETE  | Removes a given segment                               |          |
| /v1/push/tags/user                 | POST    | Tags a user with given id and given tag in the body   |          |
| /v1/push/tags/user/{user_id}       | GET     | Gets tags of user with given user_id                  |          |
| /v1/push/tags/user/{user_id}       | DELETE  | Deletes tags of user with given user_id               | `tag_id` |
| /v1/push/tags/client               | POST    | Tags a client with given id and given tag in the body |          |
| /v1/push/tags/client/{client_id}   | GET     | Gets tags of client with given client_id              |          |
| /v1/push/tags/client/{client_id}   | DELETE  | Deletes tags of client with given client_id           | `tag_id` |


