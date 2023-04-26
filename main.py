# -*- coding: utf-8 -*-

import pytest
from loguru import logger

logger.add("logs/case_{time}.log", rotation="500MB")

if __name__ == '__main__':
    '''
    -q: 安静模式, 不输出环境信息
    -v: 丰富信息模式, 输出更详细的用例执行信息
    -s: 显示程序中的print/logging输出
    '''
    # '--clean-alluredir',
    pytest.main(['-s', "checklist/test_region_delegate.py", '--alluredir=./allure-results'])
