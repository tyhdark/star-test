# -*- coding: utf-8 -*-
import math

from x.query import HttpQuery, Query
from loguru import logger

import time


class Mint(object):
    # hq = HttpQuery()
    # q = Query()
    # _block_reward = int(math.ceil((50 * 10 ** 8) / ((365 * 24 * 60 * 60) / 5)))  # 单次出块奖励793mec固定，
    @staticmethod
    # 查询所有用户的收益
    def calculate_all_user_reward():
        to_u = 10 ** 6
        all_amount = 20000000000 * to_u
        block_reward = int(math.ceil((50 * 10 ** 8) / ((365 * 24 * 60 * 60) / 5)))  # 单次出块收益
        # 第一步，先查所有用户的活期委托
        bonded_pool_addr = Query.Account.auth_account(pool_name="bonded_tokens_pool")
        all_user_delegate_balance = HttpQuery.Bank.query_balances(addr=bonded_pool_addr)  # 全网所有用户的委托

        # KYC用户的数量
        kyc_number = HttpQuery.Staking.kyc()['pagination']['total']
        kyc_amount = int(kyc_number) * to_u
        all_delegate_balance = all_user_delegate_balance + kyc_amount
        # 所有委托收益= 793*10**6 *（用户所有委托 / 200亿mec*10**6 ）
        all_delegate_reward = (block_reward * to_u) * (all_delegate_balance / all_amount)
        logger.info(f"all_delegate_reward={all_delegate_reward}")
        return all_delegate_reward

    @staticmethod
    # 查询国库应得的收益
    def calculate_treasury_reward():
        #  国库的收益的收益等于793-全网用户获得的收益
        # 查询国库开始金额
        # 国库单次出块的收益等去全网节点的收益减去用户的收益
        block_reward = (int(math.ceil((50 * 10 ** 8) / ((365 * 24 * 60 * 60) / 5)))) * (10 ** 6)
        treasury_reward = int(block_reward - Mint.calculate_all_user_reward())
        logger.info(f"treasury_reward={treasury_reward}")
        return treasury_reward

    @staticmethod
    def _treasury_reward_test():
        # 查询国库开始金额
        treasury_balance_start = HttpQuery.Bank.query_balances(addr=Query.Account.auth_account())

        # 等出一个块
        time.sleep(5)
        # 查询国库结束余额
        treasury_balance_end = HttpQuery.Bank.query_balances(addr=Query.Account.auth_account())
        treasury_reward = treasury_balance_end - treasury_balance_start
        # 国库单次出块的收益等去全网节点的收益减去用户的收益
        logger.info(f"treasury_reward={treasury_reward}")
        return treasury_reward


if __name__ == '__main__':
    m = Mint()
    # m.calculate_all_user_reward()
    # print(m._block_reward)

    over = m.treasury_reward_test() - m.calculate_treasury_reward()
    print(over)
