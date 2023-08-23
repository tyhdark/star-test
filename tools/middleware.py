# -*- coding: utf-8 -*-
import functools
import time

from loguru import logger


def retry_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        RETRY_NUMBER = 5
        result = func(*args, **kwargs)
        if result is None:
            while True:
                RETRY_NUMBER -= 1
                logger.debug("retry_decorator")
                time.sleep(1)
                result = func(*args, **kwargs)
                if result is not None:
                    break
                if RETRY_NUMBER <= 0:
                    break
        return result.get('delegation')

    return wrapper


def read_large_file(file_path):
    with open(file_path) as f:
        for line in f:
            yield line.strip()


if __name__ == '__main__':
    for l in read_large_file("../checklist/logs/case_2023-07-14_10-28-51_642887.log"):
        if ", gas_used:" in l:
            print(l)
