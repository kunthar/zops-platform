# ZetaOps GateWay

FROM basho/riak-kv:ubuntu-2.2.3
ADD riak-rabbitmq-commit-hooks/ /riak-rabbitmq-commit-hooks
RUN cp /riak-rabbitmq-commit-hooks/* /usr/lib/riak/lib/ -r