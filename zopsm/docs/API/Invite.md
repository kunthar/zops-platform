# Invite

__Attributes__:

| attr             | description                                           |
| -----------------| ------------------------------------------------------|
| subcscriber      | invited subscriber                                    |
| channel          | channel to which subscriber is invited                |
| invite_message   | invitation message                                    |
| approve          | approved, rejected, not_evaluated                     |
| serviceId        | service                                               |

__URLs:__
  * /invites
  * /invite/{id}


__Allowed Methods:__

  * PUT:
    - Update `approve` by invitee or channel owner (invite / requests)

  * POST:
    Create a new invitation
    
    

