riak start
riak-admin bucket-type create zopsm_rabbit_hook '{"props":{"postcommit":[{"mod":"riak_rabbitmq","fun":"postcommit_send_amqp"}]}}'
riak-admin bucket-type activate zopsm_rabbit_hook
riak-admin bucket-type create zopsm_logs '{"props":{"backend":"leveldb"}}'
riak-admin bucket-type activate zopsm_logs
riak-admin bucket-type create zopsm '{"props":{"backend":"leveldb"}}'
riak-admin bucket-type activate zopsm