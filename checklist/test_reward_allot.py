# -*- coding: utf-8 -*-
import decimal
import time

import pytest

from case.bank.test_tx import TestBank
from case.staking.delegate.test_delegate import TestDelegate
from case.staking.kyc.test_kyc import TestKyc
from config import chain
from tools import handle_query, calculate
from x.tx import Tx


@pytest.mark.P0
class TestMint(object):
    tx = Tx()
    test_del = TestDelegate()
    test_kyc = TestKyc()
    test_bank = TestBank()
    handle_q = handle_query.HandleQuery()

    one_block_reward = handle_q.get_block_reward()

    def test_mint_allot(self):
        """
        验证mint 出块奖励分配
        1.分配至superadmin
        2.分配至region
        """

        # 获取当前区块高度
        start_block_height = self.handle_q.get_block()
        superadmin_balance_uc = int(self.handle_q.get_balance(chain.super_addr, chain.coin['uc'])["amount"])
        superadmin_balance_ug = int(self.handle_q.get_balance(chain.super_addr, chain.coin['ug'])["amount"])

        # 获取当前链上所有region
        all_region = self.handle_q.get_regin_list()
        region_amt = 0
        if all_region:
            all_region_total_as = sum([float(i['regionTotalAS']) for i in all_region["region"]])
            region_amt = self.one_block_reward * (all_region_total_as / chain.TOTAL_AS)
        superadmin_amt_c = self.one_block_reward - region_amt
        superadmin_amt_uc = calculate.to_usrc(superadmin_amt_c)
        superadmin_amt_ug = superadmin_amt_uc * 400

        time.sleep(10)
        end_block_height = self.handle_q.get_block()
        end_balance_uc = int(self.handle_q.get_balance(chain.super_addr, chain.coin['uc'])["amount"])
        end_balance_ug = int(self.handle_q.get_balance(chain.super_addr, chain.coin['ug'])["amount"])

        assert end_balance_uc - superadmin_balance_uc == (end_block_height - start_block_height) * superadmin_amt_uc
        assert end_balance_ug - superadmin_balance_ug == (end_block_height - start_block_height) * superadmin_amt_ug

    # TODO
    #  1.活期各类场景叠加 计算收益
    #         -.单独kyc收益
    #         -.正常活期委托
    #         -.周期活期委托 -> 质押有id 到期后提取 需确定只返回本金 + 利率算出来的金额 不包含活期收益
    #         -.永久活期委托
    #         -.主动提取收益(tx withdraw) 和 被动提取
    #  2.出块减产逻辑

    def test_kyc_reward(self, setup_create_region):
        """验证kyc的收益"""
        region_admin_addr, region_id, region_name, _ = setup_create_region
        region_amt_uc = calculate.to_usrc(self.one_block_reward * (chain.REGION_AS / chain.TOTAL_AS))

        new_kyc_data = dict(region_id=f"{region_id}", region_admin_addr=f"{region_admin_addr}")
        user_addr = self.test_kyc.test_new_kyc_user(new_kyc_data)

        delegate_info = self.handle_q.get_delegate(user_addr)['delegation']
        start_height = int(delegate_info['startHeight'])
        # kyc 收益计算
        region_info = self.handle_q.get_region(region_id)['region']
        region_c = calculate.to_usrc(region_info['regionTotalUAC'], False)

        kyc_amt_uc = decimal.Decimal(region_amt_uc) * (1 / region_c)
        delegate_info = self.handle_q.get_delegate(user_addr)['delegation']
        end_height = self.handle_q.get_block()

        x = (end_height - start_height) * kyc_amt_uc
        assert delegate_info['interestAmount'] == '{:.18f}'.format(x)

        pass
        # user_addr init balance 100 coin
        # send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr}", amount="100", fees="1")
        # self.test_bank.test_send(send_data)
