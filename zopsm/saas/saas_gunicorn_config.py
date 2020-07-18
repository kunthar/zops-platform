from zopsm.lib import sd_redis
from zopsm.lib import sd_rabbit
from zopsm.lib import sd_postgres
import os

bind = "0.0.0.0:10000"
loglevel = os.getenv("LOG_LEVEL", "debug")
workers = 3
proc_name = 'saas'
raw_env = [f'REDIS_HOST={sd_redis.watch_redis(single=True)[0]}',
           f'RABBIT_NODES={sd_rabbit.watch_rabbit(single=True)}',
           'REDIS_PORT=6379',
           f'DB_USER={sd_postgres.postgres_user}',
           f'DB_PASSWORD={sd_postgres.postgres_pw}']
