# -*- coding: utf-8 -*-
"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2023/3/6 16:28
@Version :  V1.0
@Desc    :  None
"""
import time

import pytest
from loguru import logger

from case.staking.kyc.test_kyc import TestKyc
from config import chain
from x.query import Query
from x.tx import Tx

logger.add("logs/case_{time}.log", rotation="500MB")


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
        region_info = self.tx.staking.create_region(region_name=region_name, region_id=region_id,
                                                    region_total_as=1000000, region_delegators_limit=200,
                                                    region_income_rate=0.5, from_addr=region_admin_addr,
                                                    region_totalStakeAllow=1000000, region_userMaxDelegateAC=100000,
                                                    region_userMinDelegateAC=1, fees=1)
        logger.info(f"create_region_info: {region_info}")

        tx_resp = self.q.tx.query_tx(region_info['txhash'])
        time.sleep(4)
        assert tx_resp['code'] == 0
        logger.info(f"region_admin_addr:{region_admin_addr}, region_id:{region_id}, region_name:{region_name}")
        return region_admin_addr, region_id

    @pytest.mark.parametrize("data", [
        dict(region_id="bfdf8d44bc9211ed83a91e620a42e349", from_addr="sil1quqx4dqd3e7qsv9wnufnqdkgmuks5xxn8qzag8",
             fees="1", region_income_rate="0.1")])
    def test_update_region(self, data):
        tx_resp = self.tx.staking.update_region(data["region_id"], data["from_addr"], data["fees"],
                                                region_income_rate=data["region_income_rate"])
        time.sleep(4)
        assert tx_resp.get("code") == 0
        logger.info(f"Updated region tx_resp:{tx_resp}")
