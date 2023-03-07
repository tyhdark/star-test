# -*- coding: utf-8 -*-
import time

import pytest
from loguru import logger

from case.keys.test_keys import TestKeys
from config import chain
from tools import handle_name
from x.query import Query
from x.tx import Tx


class TestKyc:
    tx = Tx()
    q = Query()
    test_keys = TestKeys()

    @pytest.mark.parametrize("data", [dict(region_id="bfdf8d44bc9211ed83a91e620a42e349",
                                           region_admin_addr="sil1quqx4dqd3e7qsv9wnufnqdkgmuks5xxn8qzag8")])
    def test_new_kyc_user(self, data):
        # 新创建区 需要等待一个块高才能认证KYC，即区金库要有余额
        region_id, region_admin_addr = data['region_id'], data['region_admin_addr']
        user_addr = self.test_keys.test_add()
        logger.info(f"user_addr : {user_addr}")
        tx_info = self.tx.staking.new_kyc(addr=user_addr, region_id=region_id, role=chain.role[1],
                                          from_addr=region_admin_addr, fees=1, from_super=False)
        logger.info(f"{region_id} 认证kyc: {tx_info}")
        time.sleep(2)
        resp = self.q.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0
        return user_addr

    def test_new_kyc_admin(self):
        region_id, region_name = handle_name.create_region_id_and_name()
        logger.info(f"new region_id: {region_id}, region_name:{region_name}")
        # 添加用户
        region_admin_addr = self.test_keys.test_add()
        logger.info(f"region_admin_addr: {region_admin_addr}")

        # 超管认证区域管理员为KYC-admin
        tx_info = self.tx.staking.new_kyc(addr=region_admin_addr, region_id=region_id, role=chain.role[0],
                                          from_addr=chain.super_addr, fees=1, from_super=True)
        logger.info(f"region_admin_addr kyc info: {tx_info}")

        resp = self.q.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0
        return region_admin_addr, region_id, region_name
