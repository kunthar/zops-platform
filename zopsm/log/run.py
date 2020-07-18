from zopsm.log.log_processor import LogProcessor
from zopsm.lib.settings import WORKING_ENVIRONMENT


BIND_LIST = ['{}_logger.INFO.general'.format(WORKING_ENVIRONMENT),
             '{}_logger.ERROR.general'.format(WORKING_ENVIRONMENT),
             '{}_logger.DEBUG.general'.format(WORKING_ENVIRONMENT),
             '{}_logger.WARNING.general'.format(WORKING_ENVIRONMENT)]
EXCHANGE_NAME = 'log'
QUEUE_NAME = 'log_queue'

log_processor = LogProcessor(QUEUE_NAME, EXCHANGE_NAME, BIND_LIST)
log_processor.run()

