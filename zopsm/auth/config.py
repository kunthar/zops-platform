from zopsm.lib import sd_redis
from zopsm.lib import sd_rabbit
import os

bind = "0.0.0.0:8000"
loglevel = os.getenv("LOG_LEVEL", "debug")
workers = 3
proc_name = 'auth'
raw_env = [f'REDIS_MASTER={sd_redis.watch_redis(single=True)[0]}', f'RABBIT_NODES={sd_rabbit.watch_rabbit(single=True)}']
