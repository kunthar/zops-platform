//ubuntu@riak-03:~$ vault write sys/policy/testing policy=@testing.hcl
//Success! Data written to: sys/policy/testing
//ubuntu@riak-03:~$ vault token-create -period=10000h  -policy=testing
//Key                  Value
//---                  -----
//token                be81a5f9-e89a-de2e-34ae-c9bd0767f0b5
//token_accessor       3998ffe5-7884-633c-3991-0ef3751f5acd
//token_duration       10000h
//token_renewable      true
//token_policies       ["default" "testing"]
//identity_policies    []
//policies             ["default" "testing"]

path "testing/*" {
  capabilities = ["read", "create", "delete", "update"]
}

path "db/redis_testing" {
  capabilities = ["read"]
}

path "db/rabbitmq_testing" {
  capabilities = ["read"]
}

path "db/postgres_testing" {
  capabilities = ["read"]
}