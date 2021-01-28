import datetime
import logging
import os
import logging.handlers


def get_logger(file_name, log_dir='D:\\logs'):
    logger = logging.getLogger(file_name)
    if not file_name.endswith('.log'):
        file_name = file_name + ':' + str(datetime.date.today()) + '.log'
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s %(filename)s %(lineno)s %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    log_file = os.path.join(log_dir, file_name)
    handler = logging.handlers.RotatingFileHandler(log_file,
                                                   maxBytes=1024 * 1024)
    handler.setFormatter(formatter)
    handler.setLevel(logging.ERROR)
    logger.addHandler(handler)
    return logger


async def get_async_logger():
    pass
