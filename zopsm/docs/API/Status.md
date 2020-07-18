# Status

When subscriber retrieves the status of itself and its contacts, if
status does not exist in redis, it is read from riak, status_behavioral
updated as online, status is written to redis with a 5 min expire time.
If status is not updated until its expire time is up, it is written to riak.

When a subscriber requested the status itself, it also requests a status
list including its own status as first element and its contacts'
statuses as the rest of the list except first element.



__Attributes__:

| attr                  | description                                                                 |
| --------------------- | --------------------------------------------------------------------------  |
| last_activity_time    | timestamp of any user activity (log_in, send_message, open return back app) |
| status_message        | user defined status message. "do not disturb"                               |
| behavioral_status     | online, idle, offline                                                       |
| status_intentional    | str (Max 999)                                                               |


User status can be designated by

- usage of client applications, behavioral
- explicitly declared by users, intentional

Intentional status is managed by client applications. Platform carries
that information between nodes. Intentional status must be specified by
client applications on every `Status` request.
 

__Behavioral Status__: 

* Online
When user logs in, the status marked as online. If the last activity
user inactivity period (e.) until the value which is to mark
user inactive, expires.

* Idle
* Offline


__Intentional Status__:
* 1: Available (Default)
* 2: Busy
* n: User defined strings


| Behavioral         | Intentional    | Result            |
|--------------------|----------------|-------------------|
| Online             | Available      | Available         |
| Online             | Busy           | Busy              |
| Online             | User defined   | User defined      |
| Idle               | Available      | Available         |
| Idle               | Available      | Available         |
| Idle               | Available      | Available         |
| Offline            |       *        | Offline           |


