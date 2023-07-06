# -*- coding: utf-8 -*-
import pytest
from loguru import logger

from cases import unitcases
from tools.compute import Compute, WaitBlock
from tools.parse_response import HttpResponse


@pytest.mark.P0
class TestRegionFixed(object):
    test_region = unitcases.Region()
    test_del = unitcases.Delegate()
    test_kyc = unitcases.Kyc()
    test_bank = unitcases.Bank()
    test_fixed = unitcases.Fixed()
    base_cfg = test_bank.tx

    def test_region_fixed(self, setup_create_region):
        """测试新创建区域并定期质押"""
        logger.info("TestRegionFixed/test_region_fixed")
        region_admin_info, region_id, region_name = setup_create_region
        region_admin_addr = region_admin_info['address']

        new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
        user_info = self.test_kyc.test_new_kyc_user(**new_kyc_data)
        user_addr = user_info['address']

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
        self.test_bank.test_send(**send_data)

        region_info = HttpResponse.get_region(region_id)
        region_base_addr = region_info['region']['baseAccountAddr']
        base_uac_balance = HttpResponse.get_balance_unit(region_base_addr, self.base_cfg.coin['uc'])
        base_uag_balance = HttpResponse.get_balance_unit(region_base_addr, self.base_cfg.coin['ug'])
        logger.info(f"base_uac_balance:{base_uac_balance}, base_uag_balance:{base_uag_balance}")

        fixed_data = dict(amount=10, period=self.base_cfg.period[1], from_addr=user_addr)
        self.test_fixed.test_create_fixed_deposit(**fixed_data)

        # 验证用户余额
        user_balance = HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])
        assert int(user_balance['amount']) == Compute.to_u(100 - 10 - self.base_cfg.fees)

        # 验证区金库信息
        region_fixed_addr = region_info['region']['fixedDepositAccountAddr']
        fixed_uac_balance = HttpResponse.get_balance_unit(region_fixed_addr, self.base_cfg.coin['uc'])
        assert int(fixed_uac_balance['amount']) == Compute.to_u(10)

        # 查用户定期信息
        user_fixed_info = HttpResponse.get_fixed_deposit_by_addr(user_addr, self.base_cfg.fixed_type['all'])
        fixed_list = user_fixed_info['FixedDeposit']
        user1_fixed_info = [i for i in fixed_list if i['account'] == user_addr][0]
        assert int(user1_fixed_info['amount']) == Compute.to_u(10)
        return region_admin_addr, region_id, user_addr

    def test_region_more_fixed(self):
        """测试新创建区域多用户定期质押"""
        logger.info("TestRegionFixed/test_region_more_fixed")
        region_admin_info, region_id, region_name = self.test_region.test_create_region()
        region_admin_addr = region_admin_info['address']

        new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
        user_info1 = self.test_kyc.test_new_kyc_user(**new_kyc_data)
        user_info2 = self.test_kyc.test_new_kyc_user(**new_kyc_data)
        user_addr1, user_addr2 = user_info1['address'], user_info2['address']

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr1, amount=100)
        self.test_bank.test_send(**send_data)
        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr2, amount=100)
        self.test_bank.test_send(**send_data)

        region_info = HttpResponse.get_region(region_id)
        region_base_addr = region_info['region']['baseAccountAddr']
        base_uac_balance = HttpResponse.get_balance_unit(region_base_addr, self.base_cfg.coin['uc'])
        base_uag_balance = HttpResponse.get_balance_unit(region_base_addr, self.base_cfg.coin['ug'])
        logger.info(f"base_uac_balance:{base_uac_balance}, base_uag_balance:{base_uag_balance}")

        fixed_data = dict(amount=10, period=self.base_cfg.period[1], from_addr=user_addr1)
        self.test_fixed.test_create_fixed_deposit(**fixed_data)
        fixed_data = dict(amount=10, period=self.base_cfg.period[1], from_addr=user_addr2)
        self.test_fixed.test_create_fixed_deposit(**fixed_data)

        # 验证用户余额
        user_balance1 = HttpResponse.get_balance_unit(user_addr1, self.base_cfg.coin['uc'])
        user_balance2 = HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])
        assert user_balance1['amount'] == user_balance2['amount'] == str(Compute.to_u(100 - 10 - self.base_cfg.fees))

        # 验证区金库信息
        region_info = HttpResponse.get_region(region_id)
        region_fixed_addr = region_info['region']['fixedDepositAccountAddr']
        fixed_addr_balance = HttpResponse.get_balance_unit(region_fixed_addr, self.base_cfg.coin['uc'])
        assert fixed_addr_balance['amount'] == str(Compute.to_u(10 * 2))

        # 查用户定期信息
        user_fixed_info = HttpResponse.get_fixed_deposit_by_addr(user_addr1, self.base_cfg.fixed_type['all'])
        fixed_list = user_fixed_info['FixedDeposit']
        user1_fixed_info = [i for i in fixed_list if i['account'] == user_addr1][0]
        user1_fixed_id = user1_fixed_info['id']
        assert str(Compute.to_u(10)) == user1_fixed_info['amount']
        user_fixed_info = HttpResponse.get_fixed_deposit_by_addr(user_addr2, self.base_cfg.fixed_type['all'])
        fixed_list = user_fixed_info['FixedDeposit']
        user2_fixed_info = [i for i in fixed_list if i['account'] == user_addr2][0]
        user2_fixed_id = user2_fixed_info['id']
        user2_fixed_end_height = user2_fixed_info['end_height']
        assert str(Compute.to_u(10)) == user2_fixed_info['amount']
        logger.info(f"fixed_info:{region_admin_addr}, {region_id}, {user_addr1}, "
                    f"{user_addr2}, {user1_fixed_id}, {user2_fixed_id}, {user2_fixed_end_height}")
        return region_admin_addr, region_id, user_addr1, user_addr2, user1_fixed_id, user2_fixed_id, user2_fixed_end_height

    def test_region_more_fixed_withdraw(self):
        """
        测试新创建区域多用户定期质押
        @Desc:
            - user1 未到期赎回质押
            + expect: user1 无定期质押,返回质押本金

            - user2 到期赎回质押
            + expect: user2 无定期质押,返回质押本金+定期收益
        """
        logger.info("TestRegionFixed/test_region_more_fixed_withdraw")
        region_admin_addr, region_id, user_addr1, user_addr2, user1_fixed_id, user2_fixed_id, user2_fixed_end_height = self.test_region_more_fixed()
        user1_balance_uc = HttpResponse.get_balance_unit(user_addr1, self.base_cfg.coin['uc'])
        user2_balance_uc = HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])

        logger.info(f'{"- user1 未到期赎回质押":*^50s}')
        fixed_data = dict(deposit_id=user1_fixed_id, from_addr=user_addr1)
        self.test_fixed.test_withdraw_fixed_deposit(**fixed_data)

        logger.info(f'{"+ expect: user1 无定期质押,返回质押本金":*^50s}')
        u_fees = Compute.to_u(self.base_cfg.fees)
        resp_balance1 = HttpResponse.get_balance_unit(user_addr1, self.base_cfg.coin['uc'])
        assert int(resp_balance1['amount']) == int(user1_balance_uc['amount']) + Compute.to_u(10) - u_fees

        # 验证区金库信息
        region_info = HttpResponse.get_region(region_id)
        region_fixed_addr = region_info['region']['fixedDepositAccountAddr']
        fixed_addr_balance = HttpResponse.get_balance_unit(region_fixed_addr, self.base_cfg.coin['uc'])
        assert int(fixed_addr_balance['amount']) == Compute.to_u(10)

        # 查用户定期信息
        user_fixed_info = HttpResponse.get_fixed_deposit_by_addr(user_addr1, self.base_cfg.fixed_type['all'])
        fixed_list = user_fixed_info['FixedDeposit']
        assert len(fixed_list) == 0

        # user-2 需要wait-block等待到期
        logger.info(f'{"- user2 到期赎回质押":*^50s}')
        WaitBlock.wait_block_for_height(height=user2_fixed_end_height)

        fixed_data = dict(deposit_id=user2_fixed_id, from_addr=user_addr2)
        self.test_fixed.test_withdraw_fixed_deposit(**fixed_data)
        logger.info(f'{"+ expect: user2 无定期质押,返回质押本金+定期收益":*^50s}')
        resp_user2_uac = HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])
        assert int(resp_user2_uac['amount']) == int(user2_balance_uc['amount']) + Compute.to_u(10) - u_fees
        resp_user2_uag = HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['ug'])

        # 计算定期收益 0.06 * 1 / 12 * (10 * 1000000) * 400 = 20000000ug  20g
        interest_ac = Compute.interest(amount=10, period=1, rate=self.base_cfg.annual_rate[1])
        interest_ag = Compute.ag_to_ac(interest_ac, reverse=True)
        assert int(resp_user2_uag['amount']) == Compute.to_u(interest_ag)
