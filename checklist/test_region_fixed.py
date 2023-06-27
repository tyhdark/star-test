# -*- coding: utf-8 -*-
import pytest
from loguru import logger

from cases import package
from config import chain
from tools import handle_query, calculate


@pytest.mark.P0
class TestRegionFixed(object):
    test_region = package.RegionPackage()
    test_del = package.DelegatePackage()
    test_kyc = package.KycPackage()
    test_bank = package.BankPackage()
    test_fixed = package.FixedPackage()
    handle_q = handle_query.HandleQuery()

    def test_region_fixed(self):
        """测试新创建区域并定期质押"""
        logger.info("TestRegionFixed/test_region_fixed")
        region_admin_addr, region_id, _ = self.test_region.test_create_region()

        new_kyc_data = dict(region_id=f"{region_id}", region_admin_addr=f"{region_admin_addr}")
        user_addr = self.test_kyc.test_new_kyc_user(new_kyc_data)

        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr}", amount="100", fees="1")
        self.test_bank.test_send(send_data)
        # 计算定期收益 0.06 * 1 / 12 * (10 * 1000000) * 400 = 20000000usrg  1100000000
        region_info = self.handle_q.get_region(region_id)
        region_fixed_addr = region_info['region']['baseAccountAddr']
        fixed_usrc_balance = self.handle_q.get_balance(region_fixed_addr, chain.coin['uc'])
        fixed_usrg_balance = self.handle_q.get_balance(region_fixed_addr, chain.coin['ug'])
        logger.info(f"fixed_usrc_balance:{fixed_usrc_balance}, fixed_usrg_balance:{fixed_usrg_balance}")

        fixed_data = dict(amount="10", period=f"{chain.period[1]}", from_addr=f"{user_addr}", fees="1", gas=200000)
        self.test_fixed.test_create_fixed_deposit(fixed_data)

        # 验证用户余额
        user_balance = self.handle_q.get_balance(user_addr, chain.coin['uc'])
        assert user_balance['amount'] == str(calculate.subtraction(100, 10, 1))

        # 验证区金库信息
        region_info = self.handle_q.get_region(region_id)
        region_fixed_addr = region_info['region']['fixedDepositAccountAddr']
        fixed_addr_balance = self.handle_q.get_balance(region_fixed_addr, chain.coin['uc'])
        assert fixed_addr_balance['amount'] == str(calculate.to_usrc(10))

        # 查用户定期信息
        user_fixed_info = self.handle_q.get_fixed_deposit_by_addr(user_addr, chain.fixed_type[0])
        fixed_list = user_fixed_info['FixedDeposit']
        user1_fixed_info = [i for i in fixed_list if i['account'] == user_addr][0]
        assert str(calculate.to_usrc(10)) == user1_fixed_info['amount']
        return region_admin_addr, region_id, user_addr

    def test_region_more_fixed(self):
        """测试新创建区域多用户定期质押"""
        logger.info("TestRegionFixed/test_region_more_fixed")
        region_admin_addr, region_id, _ = self.test_region.test_create_region()

        new_kyc_data = dict(region_id=f"{region_id}", region_admin_addr=f"{region_admin_addr}")
        user_addr1 = self.test_kyc.test_new_kyc_user(new_kyc_data)
        user_addr2 = self.test_kyc.test_new_kyc_user(new_kyc_data)

        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr1}", amount="100", fees="1")
        self.test_bank.test_send(send_data)
        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr2}", amount="100", fees="1")
        self.test_bank.test_send(send_data)
        # 计算定期收益 0.06 * 1 / 12 * (10 * 1000000) * 400 = 20000000usrg  1100000000
        region_info = self.handle_q.get_region(region_id)
        region_fixed_addr = region_info['region']['baseAccountAddr']
        fixed_usrc_balance = self.handle_q.get_balance(region_fixed_addr, chain.coin['uc'])
        fixed_usrg_balance = self.handle_q.get_balance(region_fixed_addr, chain.coin['ug'])
        logger.info(f"fixed_usrc_balance:{fixed_usrc_balance}, fixed_usrg_balance:{fixed_usrg_balance}")

        fixed_data = dict(amount="10", period=f"{chain.period[1]}", from_addr=f"{user_addr1}", fees=2, gas=400000)
        self.test_fixed.test_create_fixed_deposit(fixed_data)
        fixed_data = dict(amount="10", period=f"{chain.period[1]}", from_addr=f"{user_addr2}", fees=2, gas=400000)
        self.test_fixed.test_create_fixed_deposit(fixed_data)

        # 验证用户余额
        user_balance1 = self.handle_q.get_balance(user_addr1, chain.coin['uc'])
        assert user_balance1['amount'] == str(calculate.subtraction(100, 10, 2))
        user_balance2 = self.handle_q.get_balance(user_addr2, chain.coin['uc'])
        assert user_balance2['amount'] == str(calculate.subtraction(100, 10, 2))

        # 验证区金库信息
        region_info = self.handle_q.get_region(region_id)
        region_fixed_addr = region_info['region']['fixedDepositAccountAddr']
        fixed_addr_balance = self.handle_q.get_balance(region_fixed_addr, chain.coin['uc'])
        assert fixed_addr_balance['amount'] == str(calculate.to_usrc(10 * 2))

        # 查用户定期信息
        user_fixed_info = self.handle_q.get_fixed_deposit_by_addr(user_addr1, chain.fixed_type[0])
        fixed_list = user_fixed_info['FixedDeposit']
        user1_fixed_info = [i for i in fixed_list if i['account'] == user_addr1][0]
        user1_fixed_id = user1_fixed_info['id']
        assert str(calculate.to_usrc(10)) == user1_fixed_info['amount']
        user_fixed_info = self.handle_q.get_fixed_deposit_by_addr(user_addr2, chain.fixed_type[0])
        fixed_list = user_fixed_info['FixedDeposit']
        user2_fixed_info = [i for i in fixed_list if i['account'] == user_addr2][0]
        user2_fixed_id = user2_fixed_info['id']
        user2_fixed_end_height = user2_fixed_info['end_height']
        assert str(calculate.to_usrc(10)) == user2_fixed_info['amount']
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
        user1_balance_uc = self.handle_q.get_balance(user_addr1, chain.coin['uc'])
        user2_balance_uc = self.handle_q.get_balance(user_addr2, chain.coin['uc'])

        logger.info(f'{"- user1 未到期赎回质押":*^50s}')
        fixed_data = dict(deposit_id=f'{user1_fixed_id}', from_addr=f"{user_addr1}", fees=2, gas=400000)
        self.test_fixed.test_withdraw_fixed_deposit(fixed_data)

        logger.info(f'{"+ expect: user1 无定期质押,返回质押本金":*^50s}')
        u_fees = calculate.to_usrc(2)
        resp_balance1 = self.handle_q.get_balance(user_addr1, chain.coin['uc'])
        assert resp_balance1['amount'] == str(int(user1_balance_uc['amount']) + calculate.to_usrc(10) - u_fees)

        # 验证区金库信息
        region_info = self.handle_q.get_region(region_id)
        region_fixed_addr = region_info['region']['fixedDepositAccountAddr']
        fixed_addr_balance = self.handle_q.get_balance(region_fixed_addr, chain.coin['uc'])
        assert fixed_addr_balance['amount'] == str(calculate.to_usrc(10))

        # 查用户定期信息
        user_fixed_info = self.handle_q.get_fixed_deposit_by_addr(user_addr1, chain.fixed_type[0])
        fixed_list = user_fixed_info['FixedDeposit']
        assert len(fixed_list) == 0

        # user-2 如何判断其到期，需要wait-block
        logger.info(f'{"- user2 到期赎回质押":*^50s}')
        calculate.wait_block_for_height(height=user2_fixed_end_height)

        fixed_data = dict(deposit_id=f'{user2_fixed_id}', from_addr=f"{user_addr2}", fees=2, gas=400000)
        self.test_fixed.test_withdraw_fixed_deposit(fixed_data)
        logger.info(f'{"+ expect: user2 无定期质押,返回质押本金+定期收益":*^50s}')
        resp_user2_usrc = self.handle_q.get_balance(user_addr2, chain.coin['uc'])
        assert resp_user2_usrc['amount'] == str(int(user2_balance_uc['amount']) + calculate.to_usrc(10) - u_fees)
        resp_user2_usrg = self.handle_q.get_balance(user_addr2, chain.coin['ug'])
        assert resp_user2_usrg['amount'] == str(calculate.to_usrc(20))
