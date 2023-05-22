'''
Author: Abel
Date: 2022-12-09 16:25:26
LastEditTime: 2023-05-22 10:45:51
'''
'''
Author: Abel icyheart1214@163.com
Date: 2022-07-07 13:53:16
LastEditors: Please set LastEditors
LastEditTime: 2022-12-08 17:00:38
Description: 
Copyright (c) 2022 by Abel icyheart1214@163.com, All Rights Reserved.
'''
from sys import stdout
from loguru import logger
from loguru._logger import Logger

class MyLogger:
    __instance = None
    def __new__(cls, level: str='TRACE'):
        if not cls.__instance:
            '''初始化logger'''
            logger.remove()
            logger.level(name='INFO', color='<fg #62bf91><bold>')
            fmt = (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>「{extra[ps]}」 {message}</level>"
            )
            logger.add(stdout, level=level, format=fmt)
            logger.add('logs/LOG_{time: %Y-%m-%d}.log', format=fmt, backtrace=True, enqueue=True, level='TRACE', rotation="00:00", retention=10)  # 每天一个日志文件，保留 10 天
            cls.__instance = logger.bind(ps='CheckIn')
        return cls.__instance
