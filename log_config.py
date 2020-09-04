import logging
import logging.handlers

# create logger
def logger(filename):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(lineno)s %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    # fmt = '%(asctime)s %(levelname)s %(filename)s %(lineno)s %(message)s'

    # fh=logging.FileHandler('test.log')
    # fh.setLevel(logging.DEBUG)
    # fh.setFormatter(formatter)
    # logger.addHandler(fh)

    handler = logging.handlers.RotatingFileHandler(
                filename+'.log', maxBytes=1024*1024)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger

# 'application' code
if __name__ == "__main__":

    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')