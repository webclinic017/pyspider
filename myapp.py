from log_config import logger
import mylib
logger=logger('myapp')

def main():
    logger.debug('Started')
    mylib.do_something(logger)
    logger.info('Finished')
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')

if __name__ == '__main__':
    main()