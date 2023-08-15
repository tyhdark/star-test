# -*- coding: utf-8 -*-
import inspect
import time

import pytest
from loguru import logger

from cases import unitcases
from tools.name import UserInfo, RegionInfo, ValidatorInfo
from tools.parse_response import HttpResponse
from x.query import Query, HttpQuery
from x.tx import Tx


# 单元测试delegate模块

# class Base:
#     tx = Tx()
#     hq = HttpQuery()
#     q = Query()


@pytest.mark.skip
class TestDelegate(object):
    test_region = unitcases.Region()
    test_del = unitcases.Delegate()
    test_kyc = unitcases.Kyc()
    test_key = unitcases.Keys()
    test_bank = unitcases.Bank()
    test_validator = unitcases.Validator()
    base_cfg = test_bank.tx
    user_addr = None

    def test_newkey_unkyc_delegate(self):
        """新创建的用户，没有kyc，没有余额时进行活期委托"""
        logger.info("TestDelegate/test_newkey_unkyc_delegate")
        user_info = self.test_key.test_add()
        user_addr = user_info['address']
        # 查询当前用户是不是没有余额
        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == 0
