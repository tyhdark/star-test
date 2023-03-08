# -*- coding: utf-8 -*-
from loguru import logger

from case.bank.test_tx import TestBank
from case.staking.delegate.test_delegate import TestDelegate
from case.staking.kyc.test_kyc import TestKyc
from case.staking.region.test_region import TestRegion
from config import chain
from tools import calculate, handle_query

logger.add("logs/case_{time}.log", rotation="500MB")


class TestRegionDelegate(object):
    test_region = TestRegion()
    test_del = TestDelegate()
    test_kyc = TestKyc()
    test_bank = TestBank()
    handle_q = handle_query.HandleQuery()

    def test_region_delegate(self):
        """测试新创建区域并质押"""
        region_admin_addr, region_id = self.test_region.test_create_region()

        new_kyc_data = dict(region_id=f"{region_id}", region_admin_addr=f"{region_admin_addr}")
        user_addr = self.test_kyc.test_new_kyc_user(new_kyc_data)

        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr}", amount="100", fees="1")
        self.test_bank.test_send(send_data)

        del_data = dict(region_id=f"{region_id}", region_user_addr=f"{user_addr}", del_amt="10", fees="1")
        self.test_del.test_delegate(del_data)

        # 验证用户余额
        user_balance = self.handle_q.get_balance(user_addr, 'usrc')
        assert user_balance['amount'] == str(calculate.subtraction(100, 10, 1))

        # 验证区信息
        region_info = self.handle_q.get_region(region_id)
        assert region_info['commission']['currentDemandTotalUAC'] == str(calculate.add([10, 1]))
        assert user_addr in region_info['delegators']['delegators']

        return region_admin_addr, region_id, user_addr

    def test_region_more_delegate(self):
        """多用户质押"""
        region_admin_addr, region_id, user_addr1 = self.test_region_delegate()
        logger.info(f'{"setup test_region_delegate finish":*^50s}')

        new_kyc_data = dict(region_id=f"{region_id}", region_admin_addr=f"{region_admin_addr}")
        user_addr2 = self.test_kyc.test_new_kyc_user(new_kyc_data)

        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr2}", amount="100", fees="1")
        self.test_bank.test_send(send_data)

        del_data = dict(region_id=f"{region_id}", region_user_addr=f"{user_addr2}", del_amt="10", fees="1")
        self.test_del.test_delegate(del_data)

        user_balance = self.handle_q.get_balance(user_addr2, 'usrc')
        assert user_balance['amount'] == str(calculate.subtraction(100, 10, 1))

        region_info = self.handle_q.get_region(region_id)
        assert region_info['commission']['currentDemandTotalUAC'] == str(calculate.add([10, 1, 10, 1]))
        assert user_addr1 and user_addr2 in region_info['delegators']['delegators']
