import datetime
import logging
import logging.handlers
import os
import sys
import time


def get_logger(name):
    if sys.platform == "win32":
        base_dir = "D:\\logs\\pyspider"
    else:
        base_dir = "/data/logs/pyspider"
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    logger = logging.getLogger(name)
    file_name = str(datetime.date.today()) + ".log"
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(filename)s %(lineno)s %(message)s"
    )
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    log_path = os.path.join(base_dir, name)
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log_file_path = os.path.join(log_path, file_name)
    handler = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=1024 * 1024)
    dir_list = [os.path.join(log_path, file) for file in os.listdir(log_path)]
    for log in dir_list:
        create_time = int(os.path.getctime(log))
        if int(time.time()) - create_time >= 3600 * 24 * 3:
            os.remove(log)
    handler.setFormatter(formatter)
    handler.setLevel(logging.ERROR)
    logger.addHandler(handler)
    return logger


async def get_async_logger():
    pass
