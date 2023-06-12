import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler('log.log', mode='a'))
logger.handlers[0].setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))