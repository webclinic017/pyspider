import logging


def logger():
    fmt = '%(asctime)s %(levelname)s %(name)s %(lineno)s %(message)s'
    logging.basicConfig(level=logging.DEBUG,
                        filename=str(__name__)+'.log',
                        format=fmt)
    logger = logging.getLogger(__name__)
    return logger
