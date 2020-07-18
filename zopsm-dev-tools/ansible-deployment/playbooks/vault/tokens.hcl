//ubuntu@riak-03:~$ vault token-create -period=10000h  -policy=tokens
//Key                  Value
//---                  -----
//token                4d4e5c2d-3272-30fd-c658-640b2b978cc6
//token_accessor       fc56c872-6bab-19db-370f-5cacaeada54d
//token_duration       10000h
//token_renewable      true
//token_policies       ["default" "tokens"]
//identity_policies    []
//policies             ["default" "tokens"]

//vault write sys/policy/tokens policy=@zopsm.hcl
path "tokens/*" {
  capabilities = ["read", "create", "delete", "update"]
}

path "db/redis_zopsm" {
  capabilities = ["read"]
}

path "db/rabbitmq_zopsm" {
  capabilities = ["read"]
}

path "db/postgres_zopsm" {
  capabilities = ["read"]
}