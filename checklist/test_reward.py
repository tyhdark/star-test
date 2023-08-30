# -*- coding: utf-8 -*-
import time

import pytest
from loguru import logger

from cases import unitcases
from tools.compute import Compute
from tools.parse_response import HttpResponse
from tools.rewards import Reward


# TODO
#  2.出块减产逻辑 - 5年后才减产,临时版本的项目生命周期预计不到5年,用例优先级不高


@pytest.mark.file_829
class TestReward(object):
    test_region = unitcases.Region()
    test_del = unitcases.Delegate()
    test_kyc = unitcases.Kyc()
    test_bank = unitcases.Bank()
    base_cfg = test_bank.tx

    # 默认单块收益
    block_reward_uc = Compute.to_u(base_cfg.init_mint_ac)
    # 默认一个区域收益/块
    region_reward_uc = block_reward_uc * (base_cfg.region_as / base_cfg.total_as)
    # kyc赠送的ac
    kyc_give_amt_uc = Compute.to_u(1)
    # as兑换ac比例是400,单个kyc用户赠送1代币/块收益
    kyc_reward_uc = region_reward_uc * (kyc_give_amt_uc / Compute.to_u((base_cfg.region_as * 400)))

    # @pytest.mark.skip
    # def test_kyc_reward(self, setup_create_region_and_kyc_user):
    #     """单独kyc收益"""
    #     region_admin_addr, region_id, region_name, user_addr = setup_create_region_and_kyc_user
    #     # kyc计算收益开始高度
    #     delegate_info = HttpResponse.get_delegate(user_addr)
    #     start_height = int(delegate_info['startHeight'])
    #
    #     time.sleep(20)
    #
    #     delegate_info = HttpResponse.get_delegate(user_addr)
    #     end_height = HttpResponse.get_current_block()
    #
    #     x = float((end_height - start_height) * self.kyc_reward_uc)
    #     assert float(delegate_info['interestAmount']) == x, f"test_kyc_reward failed"

    @pytest.mark.test_0829
    def test_tx_kyc_withdraw(self, creat_one_kyc):
        """
        主动提取收益(tx withdraw)，KYC用户发起活期委托，计算收益
        """
        # new kyc
        user_addr, start_balances = creat_one_kyc

        # 发起活期委托
        del_data = dict(from_addr=user_addr, amount=80)

        self.test_del.test_delegate(**del_data)
        # 查看KYC开始快高，
        del_start_height = int(HttpResponse.get_delegate_for_http(user_addr=user_addr)['startHeight'])
        # 查询开始快高
        logger.info(f"del_start_height = {del_start_height}")

        # 等待快高
        time.sleep(10)
        # 提取收益
        withdraw_result = self.test_del.test_withdraw(**dict(from_addr=user_addr))
        # logger.info(f"withdraw_result=: {withdraw_result}")
        del_end_height = int((HttpResponse.hq.Tx.query_tx(tx_hash=withdraw_result['txhash']))['height'])
        end_balances = HttpResponse.get_balance_unit(user_addr=user_addr)
        logger.info(f"balances_balances = {end_balances}")
        # 断言
        # 计算收益
        reward = Reward.reward_kyc(stake=80, end_height=del_end_height, start_height=del_start_height)
        assert end_balances == start_balances - Compute.to_u(number=80) + reward - 100 - 100

        # assert user_addr_balance_uc == Compute.to_u(1000000 - (20000 * 2) - (self.base_cfg.fees * 3)) + int(reward)
        # assert user_addr_balance_ug == int(reward)

    @pytest.mark.test_0829
    def test_tx_no_kyc_withdraw(self, creat_one_nokyc):
        """
        主动提取收益(tx withdraw)，非KYC用户发起活期委托，计算收益
        """

        user_addr, start_balances = creat_one_nokyc
        # 发起活期委托
        del_data = dict(from_addr=user_addr, amount=80)
        self.test_del.test_delegate(**del_data)
        # 查看KYC开始快高，
        del_start_height = int(HttpResponse.get_delegate_for_http(user_addr=user_addr)['startHeight'])
        # 查询开始快高
        logger.info(f"del_start_height = {del_start_height}")
        # 等待快高
        time.sleep(10)
        # 提取收益
        withdraw_result = self.test_del.test_withdraw(**dict(from_addr=user_addr))
        # logger.info(f"withdraw_result=: {withdraw_result}")
        del_end_height = int((HttpResponse.hq.Tx.query_tx(tx_hash=withdraw_result['txhash']))['height'])
        end_balances = HttpResponse.get_balance_unit(user_addr=user_addr)
        logger.info(f"balances_balances = {end_balances}")
        # 断言
        # 计算收益
        reward = Reward.reward_nokyc(stake=80, end_height=del_end_height, start_height=del_start_height)
        assert end_balances == start_balances - Compute.to_u(number=80) + reward - 100 - 100

        # assert user_addr_balance_uc == Compute.to_u(1000000 - (20000 * 2) - (self.base_cfg.fees * 3)) + int(reward)
        # assert user_addr_balance_ug == int(reward)
