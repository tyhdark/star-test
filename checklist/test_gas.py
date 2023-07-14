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

    # 3.验证创建区域 gas_used 的变化信息
    def test_new_region_gas_used(self):
        for i in range(1, 100):
            region_admin_info, region_id, region_name, gas_dict = self.test_region.test_new_region()
            logger.info(
                f'第{i}次 区域id:{region_id}, gas_used: {gas_dict["gas_used"]}, gas_wanted: {gas_dict["gas_wanted"]}')
