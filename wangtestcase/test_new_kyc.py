# -*- coding: utf-8 -*-
# import decimal
# import math
# import time

import pytest

# from loguru import logger

# from config import chain
# from tools import calculate, handle_query


@pytest.mark.P0
class TestNewKyc():

    def setup_class(self):
        print("============这是执行测试前执行的方法，类级别setup===========")

    def test_new_add_user001(self):
        print("---test_new_add_user001----")
        """测试NEWKYC能不能成功"""
        assert 2 - 1 == 1

    def test_new_add_user002(self):
        print("---test_new_add_user001----")
        assert 1 + 1 == 2

    def teardown(self):
        print("=============这是执行测试后执行的方法，方法级别的teardown==========")


if __name__ == '__main__':
    pytest.main(['pytest-v test_new_kyc.py --log-level=debug --log-file=./log --alluredir=../report/wangtest --clean-alluredir'
])
