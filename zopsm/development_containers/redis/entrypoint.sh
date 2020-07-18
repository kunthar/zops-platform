#!/usr/bin/env bash

if [[ "$REDIS_MODE" == master ]]; then
  echo "
  port 6379
  bind 0.0.0.0
  requirepass quoh
  " > /usr/local/etc/redis/redis.conf
  redis-server /usr/local/etc/redis/redis.conf
  echo "Redis Node started as Master."
else
  echo "
  port 6379
  bind 0.0.0.0
  masterauth quoh
  slaveof $REDIS_MASTER 6379
  " > /usr/local/etc/redis/redis.conf
  redis-server /usr/local/etc/redis/redis.conf
  echo "Redis Node started as Slave."
fi