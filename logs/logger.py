import logging

logging.basicConfig(
    format='%(asctime)s | %(levelname)-8s | %(message)s' ,
    level=logging.DEBUG,
    filename='logs/logs.txt'
)

logger = logging.getLogger('logger')