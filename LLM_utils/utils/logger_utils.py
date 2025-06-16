import os
import logging


def create_logger(name):
    # 获取环境变量中的日志级别
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

    # 将字符串的日志级别转换为 logging 模块中对应的级别
    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')


    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(numeric_level)
    formatter = logging.Formatter('%(asctime)s ｜ %(name)s ｜ %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger
