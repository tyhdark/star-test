# -*- coding: utf-8 -*-
import pytest
from loguru import logger

from case.bank.test_tx import TestBank
from case.staking.fixed.test_fixed import TestFixed
from case.staking.kyc.test_kyc import TestKyc
from case.staking.region.test_region import TestRegion
from config import chain
from tools import handle_query, calculate


@pytest.mark.P0
class TestSendCoin(object):
    test_region = TestRegion()
    test_fixed = TestFixed()
    test_kyc = TestKyc()
    test_bank = TestBank()
    handle_q = handle_query.HandleQuery()

    def test_ag_to_ac(self):
        """测试ag兑换ac"""
        logger.info("TestSendCoin/test_ag_to_ac")
        region_admin_addr, region_id = self.test_region.test_create_region()

        new_kyc_data = dict(region_id=f"{region_id}", region_admin_addr=f"{region_admin_addr}")
        user_addr = self.test_kyc.test_new_kyc_user(new_kyc_data)

        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr}", amount="500", fees="1")
        self.test_bank.test_send(send_data)
        # 计算定期收益 0.06 * 1 / 12 * (200 * 1000000) * 400 = 400000000usrg  区金库:1100000000usrg
        region_info = self.handle_q.get_region(region_id)
        region_fixed_addr = region_info['region']['baseAccountAddr']
        fixed_usrc_balance = self.handle_q.get_balance(region_fixed_addr, 'usrc')
        fixed_usrg_balance = self.handle_q.get_balance(region_fixed_addr, 'usrg')
        logger.info(f"fixed_usrc_balance:{fixed_usrc_balance}, fixed_usrg_balance:{fixed_usrg_balance}")

        fixed_data = dict(amount="200", period=f"{chain.period[1]}", from_addr=f"{user_addr}", fees=2, gas=400000)
        self.test_fixed.test_fixed(fixed_data)

        # 验证用户余额
        user_balance = self.handle_q.get_balance(user_addr, 'usrc')
        assert user_balance['amount'] == str(calculate.subtraction(500, 200, 2))

        # 验证区金库信息
        region_info = self.handle_q.get_region(region_id)
        region_fixed_addr = region_info['region']['fixedDepositAccountAddr']
        fixed_addr_balance = self.handle_q.get_balance(region_fixed_addr, 'usrc')
        assert fixed_addr_balance['amount'] == str(calculate.to_usrc(200))

        # 查用户定期信息
        user_fixed_info = self.handle_q.get_fixed_deposit_by_addr(user_addr, chain.fixed_type[0])
        fixed_list = user_fixed_info['FixedDeposit']
        fixed_info = [i for i in fixed_list if i['account'] == user_addr][0]
        _fixed_id = fixed_info['id']
        _fixed_end_height = fixed_info['end_height']
        user1_fixed_info = [i for i in fixed_list if i['account'] == user_addr][0]
        assert str(calculate.to_usrc(200)) == user1_fixed_info['amount']

        # 需要wait-block
        logger.info(f'{"到期赎回质押":*^50s}')
        calculate.wait_block_for_height(height=_fixed_end_height)
        u_fees = calculate.to_usrc(2)

        fixed_data = dict(deposit_id=f'{_fixed_id}', from_addr=f"{user_addr}", fees=2, gas=400000)
        self.test_fixed.test_fixed_withdraw(fixed_data)
        logger.info(f'{"无定期质押,返回质押本金+定期收益":*^50s}')
        resp_user_usrc = self.handle_q.get_balance(user_addr, 'usrc')
        assert resp_user_usrc['amount'] == str(int(user_balance['amount']) + calculate.to_usrc(200) - u_fees)
        resp_user_usrg = self.handle_q.get_balance(user_addr, 'usrg')
        assert resp_user_usrg['amount'] == str(calculate.to_usrc(400))

        # ag to ac
        uag_balance = resp_user_usrg['amount']
        ag = calculate.to_usrc(uag_balance, False)
        ag_data = dict(ag_amount=f"{ag}", from_addr=f"{user_addr}", fees=1)
        self.test_kyc.tx.Staking.ag_to_ac(**ag_data)
        u_fees = calculate.to_usrc(1)
        to_uac = calculate.ag_to_ac(uag_balance)
        # check balances
        resp2_user_usrc = self.handle_q.get_balance(user_addr, 'usrc')
        assert resp2_user_usrc['amount'] == str(int(resp_user_usrc['amount']) - u_fees + to_uac)
