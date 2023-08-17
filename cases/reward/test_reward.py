# -*- coding: utf-8 -*-
# 测试收益： 非KYC用户活期收益、KYC活期收益、KYC定期收益
import time

import pytest
import yaml

from tools.compute import Compute
from tools.rewards import Reward
from x.tx import Tx
from cases import unitcases
from loguru import logger
from x.query import Query, HttpQuery


class TestDelegateReward:
    def test_no_kyc_reward(self):
        user_addr = "me1ex3k095qcl2acc02zjj5kczu42j6yxhqjf4rwk"
        amount = "50"
        block = 3
        #
        # 用户发起委托
        Tx.Staking.delegate(from_addr=user_addr, amount=amount)
        # 查询用户余额
        start_balances = HttpQuery.Bank.query_balances(addr=user_addr)
        # 经历一个块高
        time.sleep(block * 5)
        # 查询用户的活期委托 拿到块高
        start_height = (HttpQuery.Staking.delegation(addr=user_addr))['startHeight']
        # 用户提取收益
        # result = Tx.Staking.withdraw_rewards(from_addr=user_addr)
        result = Tx.Staking.undelegate_nokyc(from_addr=user_addr, amount=float(amount))
        # logger.info(f"result={result['txhash']}")
        end_height = int((Query.Tx.query_tx(tx_hash=result['txhash']))['height'])
        # 查询用户结束余额
        end_balance = HttpQuery.Bank.query_balances(addr=user_addr)
        # 手动拿到收益值
        reward = Reward.reward_nokyc(stake=float(amount), start_height=start_height, end_height=end_height)
        logger.info(f"reward={reward}")
        assert end_balance == int(start_balances + reward - 100)
        pass

    def test_delegation(self):
        user_addr = "me1cscx53xnedldg2wrzhgq9y7yeauvcwlvt2rh34"
        delegation = HttpQuery.Staking.delegation(addr=user_addr)
        print(f"delegation={type(delegation['startHeight'])}")
        pass

    def test_kyc_reward(self):
        user_addr = "me12437lurmk23cl0a6wvyp7tukjpt6x3jcr5v9jn"
        amount = "50"
        block = 3
        #
        # 用户发起委托
        Tx.Staking.delegate(from_addr=user_addr, amount=float(amount))
        # 查询用户余额

        # 经历一个块高
        time.sleep(block * 5)
        start_balances = HttpQuery.Bank.query_balances(addr=user_addr)
        # 查询用户的活期委托 拿到块高
        start_height = (HttpQuery.Staking.delegation(addr=user_addr))['startHeight']
        # 用户提取收益
        result = Tx.Staking.undelegate_kyc(from_addr=user_addr, amount=float(amount))
        # logger.info(f"result={result['txhash']}")
        end_height = int((Query.Tx.query_tx(tx_hash=result['txhash']))['height'])
        # 查询用户结束余额
        end_balance = HttpQuery.Bank.query_balances(addr=user_addr)
        logger.info(f"end_balance={end_balance}")
        # 手动拿到收益值
        reward = Reward.reward_kyc(stake=float(amount), start_height=start_height, end_height=end_height)
        logger.info(f"reward={reward}")
        assert end_balance == int(start_balances + Compute.to_u(number=float(amount)) + reward - 100)
        # assert 1==1


