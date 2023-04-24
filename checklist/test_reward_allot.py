# -*- coding: utf-8 -*-
import time

import pytest

from config import chain
from tools import handle_query, calculate
from x.query import Query
from x.tx import Tx


@pytest.mark.P0
class TestMint(object):
    tx = Tx()
    q = Query()
    handle_q = handle_query.HandleQuery()

    def test_mint_allot(self):
        """
        验证mint 出块奖励分配
        1.分配至superadmin
        2.分配至region
        """
        one_block_reward = self.handle_q.get_block_reward()

        # 获取当前区块高度
        start_block_height = self.handle_q.get_block()
        superadmin_balance_uc = int(self.handle_q.get_balance(chain.super_addr, chain.coin['uc'])["amount"])
        superadmin_balance_ug = int(self.handle_q.get_balance(chain.super_addr, chain.coin['ug'])["amount"])

        # 获取当前链上所有region
        all_region = self.handle_q.get_regin_list()
        region_amt = 0
        if all_region:
            all_region_total_as = sum([float(i['regionTotalAS']) for i in all_region["region"]])
            region_amt = one_block_reward * (all_region_total_as / chain.TOTAL_AS)
        superadmin_amt_c = one_block_reward - region_amt
        superadmin_amt_uc = calculate.to_usrc(superadmin_amt_c)
        superadmin_amt_ug = superadmin_amt_uc * 400

        time.sleep(10)
        end_block_height = self.handle_q.get_block()
        end_balance_uc = int(self.handle_q.get_balance(chain.super_addr, chain.coin['uc'])["amount"])
        end_balance_ug = int(self.handle_q.get_balance(chain.super_addr, chain.coin['ug'])["amount"])

        assert end_balance_uc - superadmin_balance_uc == (end_block_height - start_block_height) * superadmin_amt_uc
        assert end_balance_ug - superadmin_balance_ug == (end_block_height - start_block_height) * superadmin_amt_ug
