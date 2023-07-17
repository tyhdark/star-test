# -*- coding: utf-8 -*-
import os
import time

import pytest
from loguru import logger

logger.add("logs/case_{time}.log", rotation="500MB")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_DIR = os.path.join(BASE_DIR, f'results/{time.strftime("%Y%m%d-%H%M%S")}')


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} Execution time {(end_time - start_time) / 60} min")
        return result

    return wrapper


@timer
def run_tests():
    pytest.main(['-s', '-m', 'P0', "checklist/", f'--alluredir={RESULT_DIR}', ])


if __name__ == '__main__':
    run_tests()
