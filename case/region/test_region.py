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

from config import chain
from tools import handle_name
from x.query import Query
from x.tx import Tx

logger.add("logs/case_{time}.log", rotation="500MB")


@pytest.mark.P1
class TestRegion:
    tx = Tx()
    q = Query()

    def test_create_region(self):
        region_id, region_name = handle_name.create_region_id_and_name()

        # 添加用户
        user_name = handle_name.create_username()
        user_info = self.tx.keys.add(user_name)
        logger.info(f"新增用户信息: {user_info}")
        region_admin_addr = user_info[0][0]['address']
        time.sleep(3)
        balances_info = self.q.bank.query_balances(region_admin_addr)
        logger.info(f"账户余额信息: {balances_info}")

        # 区管理员 认证kyc
        kyc_info = self.tx.staking.new_kyc(addr=region_admin_addr, region_id=region_id, role=chain.role[0],
                                           from_addr=chain.super_addr, fees=1)
        logger.info(f"认证kyc 为管理员信息: {kyc_info}")

        time.sleep(5)
        # 使用SuperAdmin给区管理转账
        send_tx_info = self.tx.bank.send_tx(from_addr=chain.super_addr, to_addr=region_admin_addr, amount=100,
                                            fees=1, from_super=True)
        logger.info(f"转账信息: {send_tx_info}")

        # 创建区域
        time.sleep(5)
        region_info = self.tx.staking.create_region(region_name=region_name, region_id=region_id,
                                                    region_total_as=1000000, region_delegators_limit=200,
                                                    region_income_rate=0.5, from_addr=region_admin_addr,
                                                    region_totalStakeAllow=1000000, region_userMaxDelegateAC=100000,
                                                    region_userMinDelegateAC=1, fees=1)
        logger.info(f"创建区信息: {region_info}")

        tx_resp = self.q.tx.query_tx(region_info['txhash'])
        time.sleep(4)
        assert tx_resp['code'] == 0
        logger.info(f"区管理员地址: {region_admin_addr}, 区ID: {region_id}")

        return region_admin_addr, region_id
