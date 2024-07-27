import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(service_name):
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
    if not os.path.exists('logs'):
        os.makedirs('logs')

    log_file = os.path.join(log_dir, f'{service_name}.log')

    logger = logging.getLogger(service_name)
    logger.setLevel(logging.DEBUG)

    c_handler = logging.StreamHandler()
    f_handler = RotatingFileHandler(f'logs/{service_name}.log', maxBytes=10485760, backupCount=5)
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.DEBUG)

    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)
    f_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)


    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger
