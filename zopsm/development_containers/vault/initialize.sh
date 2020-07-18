#!/bin/sh
/bin/vault mount -path=tokens kv
/bin/vault mount -path=db kv

/bin/vault write db/redis_${WORKING_ENVIRONMENT} pw=quoh

/bin/vault write db/rabbitmq_${WORKING_ENVIRONMENT} username=zopsm password=chauj5DuX

/bin/vault write db/postgres_${WORKING_ENVIRONMENT} username=zopsm password=ipoo3a