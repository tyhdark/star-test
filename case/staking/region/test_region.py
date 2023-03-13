# -*- coding: utf-8 -*-
import time

import pytest
from loguru import logger

from case.staking.kyc.test_kyc import TestKyc
from config import chain
from x.query import Query
from x.tx import Tx


@pytest.mark.P1
class TestRegion:
    tx = Tx()
    q = Query()
    test_kyc = TestKyc()

    def test_create_region(self):
        region_admin_addr, region_id, region_name = self.test_kyc.test_new_kyc_admin()
        time.sleep(5)
        # 使用SuperAdmin给区管理转账
        send_tx_info = self.tx.bank.send_tx(from_addr=chain.super_addr, to_addr=region_admin_addr, amount=100,
                                            fees=1, from_super=True)
        logger.info(f"send_tx_info: {send_tx_info}")

        # 创建区域
        time.sleep(5)
        # as总量:200 00000
        region_info = self.tx.staking.create_region(region_name=region_name, region_id=region_id,
                                                    total_as=100000, delegators_limit=200,
                                                    fee_rate=0.5, from_addr=region_admin_addr,
                                                    totalStakeAllow=100000, userMaxDelegateAC=100000,
                                                    userMinDelegateAC=1, fees=2, gas=400000)
        logger.info(f"create_region_info: {region_info}")
        tx_resp = self.q.tx.query_tx(region_info['txhash'])
        assert tx_resp['code'] == 0
        # 等待块高 确保区域内有足够钱用于new-kyc 25ac * 1 / 200 = 0.125ac = 125000usrc 8个块 = 1000000usrc
        logger.info(f"Make sure there is enough money in the area to spend new-kyc")
        time.sleep((5 * 8) * 2)
        region_info = dict(region_admin_addr=region_admin_addr, region_id=region_id, region_name=region_name)
        logger.info(f"{region_info}")
        # 动态修改测试数据,测试数据管理可优化方案: 存储至db 或者 将动态数据回写至文件
        # region_id_list = [i["region_id"] for i in test_data.Region.region_list]
        # test_data.Region.region_list.append(region_info) if region_id not in region_id_list else "region_id is exist"
        return region_admin_addr, region_id

    # @pytest.mark.parametrize("data", test_data.Region.update_region)
    def test_update_region(self, data):
        tx_resp = self.tx.staking.update_region(**data)
        time.sleep(5)
        assert tx_resp.get("code") == 0
        logger.info(f"Updated region tx_resp:{tx_resp}")
