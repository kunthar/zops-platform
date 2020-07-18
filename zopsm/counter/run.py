from zopsm.counter.counter_processor import CounterProcessor
from zopsm.lib.settings import WORKING_ENVIRONMENT


BIND_LIST = ['{}_logger.INFO.counter'.format(WORKING_ENVIRONMENT)]
EXCHANGE_NAME = 'log'
QUEUE_NAME = 'counter_queue'

counter_processor = CounterProcessor(QUEUE_NAME, EXCHANGE_NAME, BIND_LIST)
counter_processor.run()
