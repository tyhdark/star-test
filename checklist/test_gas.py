# -*- coding: utf-8 -*-

import pytest
from loguru import logger

from cases import unitcases

logger.add("logs/case_{time}.log", rotation="500MB")


@pytest.mark.P1
class TestGas(object):
    test_region = unitcases.Region()
    test_del = unitcases.Delegate()
    test_kyc = unitcases.Kyc()
    test_bank = unitcases.Bank()
    test_fixed = unitcases.Fixed()
    base_cfg = test_bank.tx
    number = 5

    # 3.验证创建区域 gas_used 的变化信息
    def test_new_region_gas_used(self):
        for i in range(1, self.number):
            region_admin_info, region_id, region_name, gas_dict = self.test_region.test_new_region()
            logger.info(f'第{i}次 region_id:{region_id}, gas_dict: {gas_dict}')

    def test_new_kyc_gas_used(self):
        region_admin_info, region_id, region_name, _ = self.test_region.test_new_region()
        region_admin_addr = region_admin_info["address"]
        new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)

        for i in range(1, self.number):
            user_info, gas_dict = self.test_kyc.test_new_kyc(**new_kyc_data)
            logger.info(f'第{i}次 new_kyc:{user_info}, gas_dict: {gas_dict}')
