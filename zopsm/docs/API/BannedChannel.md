# BannedChannel 

/banned-channels/{$channel_id}/subscribers
/banned-channels/{$channel_id}/subscribers/{$subscriber_id}

post
    ban `$subscriber_id` from channel `$channel_id`


delete
    unban `$subscriber_id` from channel `$channel_id`

put
    not allowed
    
get
    list banned subscribers of `$channel_id`
    
