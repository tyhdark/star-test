# -*- coding: utf-8 -*-
import os
import time

import pytest
from loguru import logger

logger.add("logs/case_{time}.log", rotation="500MB")

if __name__ == '__main__':
    start_time = time.time()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pytest.main(['-s', '-m', 'P0', "checklist/", f'--alluredir={BASE_DIR}/allure-results', ])
    elapsed_time = (time.time() - start_time) / 60  # 计算时间差
    logger.info(f"Elapsed time: {elapsed_time} min")
