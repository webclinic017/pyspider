import logging

fmt='%(asctime)s %(levelname)s %(name)s %(lineno)s %(message)s'
logging.basicConfig(level=logging.DEBUG,filename='blue_ox.log',format=fmt)
logger=logging.getLogger(__name__)
logger.debug('where is my axe')
