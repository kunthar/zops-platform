import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
saas_logger = logging.getLogger('saas_logger')

console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

saas_logger.addHandler(console_handler)


