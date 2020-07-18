# Subscriber

Entities who can send/receive messages to/from channels of other subscribers
or groups.

__Attributes__:

| attr               | attr                                          |
| ------------------ | ----------------------------------------------|
| consumer           | id of accounts's consumer on SaaS management  |
| contacts           | list of subscribers                           |
| channels           | list of channels                              |
| bannedChannels     | list of channels                              |
| bannedSubscribers  | list of subscribers                           |
| lastStatusMessage  | last status message                           |
| invites            | list of invitations of subscriber             |
| joinRequests       | list of join requests of subscriber           |
| serviceId          | service                                       |



__URLs:__
  * /channels/{channel_id}/subscribers
  * /channels/{channel_id}/subscribers/{id}
  * /subscribers/{id}

__Params:__

  * Required: `serviceId`

__Allowed Methods:__

  * GET:
    Retrieves list of subscribers of `channel_id` paginated by 10 or retrieves a single subscriber by given id

  * PUT:
    Update an existing subscriber by `contacts`, `channels`, and `banned_channels`

  * DELETE:
    Unsubscribe `id` from `channel_id`

  * POST:
    Subscribe `id` to `channel_id`

