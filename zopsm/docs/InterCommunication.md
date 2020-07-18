# Inter communication between microservices

## Microservices
 
### Gateways

This service is responsible to meet users' REST requests. It checks message structure 
and try to validate to accept request. Also check request token if it is same with claimer or not. Service
responses back `202 Accepted` if there is nothing wrong with mentioned controls.

Along with `202 Accepted`, service insert a new job to rabbitmq `inter_comm` exchange with related routing key.

| URL        | routing key   | message                 |
|------------|---------------|-------------------------|
|



### Message Transfer Agents


### Message Delivery Agents


## RPC Communication between Gateways and MTAs

Workers consumes its own rabbitmq queue which is called `rpc_queue_worker_name` and bound to `inter_comm` exchange
with binding keys refering the name(s) of the dedicated jobs of that worker, eg. `get_message`, `subscribe_user`. etc..


```

                   `inter_comm`

    REST                / \  get_message    ______________________________                   WORKER
    GATEWAYS  -------  /   \ ~~~~~~~~~~~~~~~                                               responsible to 
      \                \   / ~~~~~~~~~~~~~~~    rpc_queue_worker_name     ---------------  get message and
       \               \ /  subscribe_user ______________________________                  user subscription
        \                                                                                        /
         \                                                                                      /
          \  ---------------------                                                             /
           \-     callback_queue  ------------------------------------------------------------/
             ---------------------

```


RPC calls must contain followings in a json string:

* `job` string to point method name
* `params` dict including parameters for `job`'s method. Parameters must be nested if necessary. Do NOT flat them.

## Examples:

RPC call for `get_message`:

```json
  {
    "jsonrpc": "2.0",
    "method": "get_message",
    "params": {
      "message_id": "X9J0UI76GBWQTF"
    },
    "id": "eyJhIjozLCJiIjo0fQ"
  }

```

A success response for `get_message`:
```json
    {
      "jsonrpc": "2.0",
      "result": {"sender": "user_1", "receiver":"user_2", "body": "merhaba"},
      "id": "eyJhIjozLCJiIjo0fQ"
    }
```

A fail response for `get_message`:
```json
    {
      "jsonrpc": "2.0",
      "error": {
                "code": -32602, 
                "message": "Invalid params"
                },
      "id": "eyJhIjozLCJiIjo0fQ"
    }
```

Python Code which gets message:


```python

    import JSONRPCInvalidParams

    def do_job_get_message(**params):
        error = None
        try:
            message_id = params.get('message_id')
            mb = riak_pb.bucket_type('rabbit_hook').bucket('message')
            message = mb.get(message_id)
        except KeyError:
            error = JSONRPCInvalidParams
        
        return rpc_response(result=message, error=error)

    def rpc_response(result, error=None, jsonrpc="2.0", id=None):
        response = {
            "jsonrpc": "2.0"
        }
        if id:
            response['id'] = id
        
        if error:
            response['error'] = error
        else:
            response['result'] = result
        
        return json.dumps(response)
```
