import os
from zopsm.lib.credis import ZRedis
from zopsm.lib.sd_redis import redis_db_pw

slave = os.getenv('REDIS_SLAVE')

cache = ZRedis(host=slave,
               db=os.getenv('REDIS_DB'))



def build_pika_message(job, params):
    return {
        "job": job,
        "params": params
    }


def generate_private_message_channel_name(sender, receiver):
    ids = sorted([sender, receiver])
    return "prv_{}_{}".format(ids[0], ids[1])
