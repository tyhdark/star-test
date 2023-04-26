# -*- coding: utf-8 -*-
import time

import pytest
from loguru import logger

from case import package
from config import chain
from tools import handle_query, calculate


@pytest.mark.P0
class TestMint(object):
    test_region = package.RegionPackage()
    test_del = package.DelegatePackage()
    test_kyc = package.KycPackage()
    test_bank = package.BankPackage()
    handle_q = handle_query.HandleQuery()

    one_block_reward = handle_q.get_block_reward()
    region_amt_uc = calculate.to_usrc(one_block_reward * (chain.REGION_AS / chain.TOTAL_AS))

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
    #         -.永久活期委托 + 1kyc
    #         -.周期活期委托 -> 质押有id 到期后提取 需确定只返回本金 + 利率算出来的金额 不包含活期收益   x + 10收益+1kyc
    #                      -> 到期之后 根据利率算钱的那部分结束了，不提取的话 那质押的本金还享受活期收益

    #         -.主动提取收益(tx withdraw) 和 被动提取
    #  2.出块减产逻辑

    def test_kyc_reward(self, setup_create_region):
        """验证kyc的收益"""
        region_admin_addr, region_id, region_name, _ = setup_create_region

        user_addr = self.test_kyc.test_new_kyc_user(dict(region_id=region_id, region_admin_addr=region_admin_addr))

        delegate_info = self.handle_q.get_delegate(user_addr)['delegation']
        # kyc计算收益开始高度
        start_height = int(delegate_info['startHeight'])

        # kyc 每个块收益
        region_info = self.handle_q.get_region(region_id)['region']
        kyc_amt_uc = self.region_amt_uc * (calculate.to_usrc(1) / int(region_info['regionTotalUAC']))
        delegate_info = self.handle_q.get_delegate(user_addr)['delegation']
        end_height = self.handle_q.get_block()

        x = '{:.18f}'.format((end_height - start_height) * kyc_amt_uc)
        assert delegate_info['interestAmount'] == x, f"{delegate_info['interestAmount']} != {x}"

    def test_delegate1_reward(self, setup_create_region):
        """计算活期委托收益"""
        region_admin_addr, region_id, region_name, _ = setup_create_region
        user_addr = self.test_kyc.test_new_kyc_user(dict(region_id=region_id, region_admin_addr=region_admin_addr))
        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr}", amount="100", fees="1")
        self.test_bank.test_send(send_data)
        # kyc 每个块收益
        region_info = self.handle_q.get_region(region_id)['region']
        one_coin_reward_uc = self.region_amt_uc * (calculate.to_usrc(1) / int(region_info['regionTotalUAC']))
        logger.info(f"one_coin_reward_uc: {one_coin_reward_uc}")

        kyc_start_height = int(self.handle_q.get_delegate(user_addr)['delegation']['startHeight'])
        logger.info(f"kyc_start_height: {kyc_start_height}")

        # 发起活期质押后 会更新startHeight
        del_data = dict(region_user_addr=f"{user_addr}", amount="10", fees="1")
        self.test_del.test_delegate(del_data)

        time.sleep(10)

        delegate_info = self.handle_q.get_delegate(user_addr)['delegation']
        interest = delegate_info['interestAmount']
        end_height = self.handle_q.get_block()
        stage2_start_height = int(delegate_info['startHeight'])
        logger.info(f"stage2_start_height: {stage2_start_height}, end_height: {end_height}, interestAmount: {interest}")

        stage1_amt = ((stage2_start_height - 1) - kyc_start_height) * one_coin_reward_uc
        # 10 coin + 1 coin kyc
        stage2_amt = (end_height - stage2_start_height) * (one_coin_reward_uc * 11)
        reward = (stage1_amt * 1000000 + stage2_amt * 1000000) / 1000000
        logger.info(f"stage1_amt: {stage1_amt}, stage2_amt: {stage2_amt}, reward: {reward}")
        assert str(float(interest)) == str(reward)

    def test_delegate2_fixed(self, setup_create_region):
        """计算活期周期委托收益"""
        region_admin_addr, region_id, region_name, _ = setup_create_region
        user_addr = self.test_kyc.test_new_kyc_user(dict(region_id=region_id, region_admin_addr=region_admin_addr))
        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr}", amount="100", fees="1")
        self.test_bank.test_send(send_data)
        # kyc 每个块收益
        region_info = self.handle_q.get_region(region_id)['region']
        one_coin_reward_uc = self.region_amt_uc * (calculate.to_usrc(1) / int(region_info['regionTotalUAC']))
        logger.info(f"one_coin_reward_uc: {one_coin_reward_uc}")

        kyc_start_height = int(self.handle_q.get_delegate(user_addr)['delegation']['startHeight'])
        logger.info(f"kyc_start_height: {kyc_start_height}")

        # 发起活期质押后 会更新startHeight
        del_data = dict(region_user_addr=f"{user_addr}", amount=10, term=chain.delegate_term[1], fees=1)
        self.test_del.test_delegate_fixed(del_data)

        time.sleep(10)

        delegate_info = self.handle_q.get_delegate(user_addr)['delegation']
        interest = delegate_info['interestAmount']
        end_height = self.handle_q.get_block()
        stage2_start_height = int(delegate_info['startHeight'])
        logger.info(f"stage2_start_height: {stage2_start_height}, end_height: {end_height}, interestAmount: {interest}")

        stage1_amt = ((stage2_start_height - 1) - kyc_start_height) * one_coin_reward_uc
        # 10 coin + 1 coin kyc
        stage2_amt = (end_height - stage2_start_height) * (one_coin_reward_uc * 11)
        reward = (stage1_amt * 1000000 + stage2_amt * 1000000) / 1000000
        logger.info(f"stage1_amt: {stage1_amt}, stage2_amt: {stage2_amt}, reward: {reward}")
        assert str(float(interest)) == str(reward)

    def test_delegate3_fixed(self, setup_create_region):
        """计算活期永久委托收益"""
        region_admin_addr, region_id, region_name, _ = setup_create_region
        user_addr = self.test_kyc.test_new_kyc_user(dict(region_id=region_id, region_admin_addr=region_admin_addr))
        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr}", amount="100", fees="1")
        self.test_bank.test_send(send_data)
        # kyc 每个块收益
        region_info = self.handle_q.get_region(region_id)['region']
        one_coin_reward_uc = self.region_amt_uc * (calculate.to_usrc(1) / int(region_info['regionTotalUAC']))
        logger.info(f"one_coin_reward_uc: {one_coin_reward_uc}")

        kyc_start_height = int(self.handle_q.get_delegate(user_addr)['delegation']['startHeight'])
        logger.info(f"kyc_start_height: {kyc_start_height}")

        # 发起活期质押后 会更新startHeight
        del_data = dict(region_user_addr=f"{user_addr}", amount="10", fees="1")
        self.test_del.test_delegate_infinite(del_data)

        time.sleep(10)

        delegate_info = self.handle_q.get_delegate(user_addr)['delegation']
        interest = delegate_info['interestAmount']
        end_height = self.handle_q.get_block()
        stage2_start_height = int(delegate_info['startHeight'])
        logger.info(f"stage2_start_height: {stage2_start_height}, end_height: {end_height}, interestAmount: {interest}")

        stage1_amt = ((stage2_start_height - 1) - kyc_start_height) * one_coin_reward_uc
        # 10 coin + 1 coin kyc
        stage2_amt = (end_height - stage2_start_height) * (one_coin_reward_uc * 11)
        reward = (stage1_amt * 1000000 + stage2_amt * 1000000) / 1000000
        logger.info(f"stage1_amt: {stage1_amt}, stage2_amt: {stage2_amt}, reward: {reward}")
        assert str(float(interest)) == str(reward)

    def test_delegate_group(self, setup_create_region):
        """委托组合场景"""
        # TODO 待修复
        region_admin_addr, region_id, region_name, _ = setup_create_region
        user_addr = self.test_kyc.test_new_kyc_user(dict(region_id=region_id, region_admin_addr=region_admin_addr))
        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr}", amount="100", fees="1")
        self.test_bank.test_send(send_data)
        # kyc 每个块收益
        region_info = self.handle_q.get_region(region_id)['region']
        one_coin_reward_uc = self.region_amt_uc * (calculate.to_usrc(1) / int(region_info['regionTotalUAC']))
        logger.info(f"one_coin_reward_uc: {one_coin_reward_uc}")

        kyc_start_height = int(self.handle_q.get_delegate(user_addr)['delegation']['startHeight'])
        logger.info(f"kyc_start_height: {kyc_start_height}")

        # 发起活期质押后 会更新startHeight
        del_data = dict(region_user_addr=f"{user_addr}", amount="10", fees="1")
        self.test_del.test_delegate(del_data)
        time.sleep(10)
        delegate_info = self.handle_q.get_delegate(user_addr)['delegation']
        delegate_start_height = int(delegate_info['startHeight'])
        logger.info(f"stage2_start_height: {delegate_start_height}")
        stage1_amt = ((delegate_start_height - 1) - kyc_start_height) * one_coin_reward_uc

        del_data = dict(region_user_addr=f"{user_addr}", amount=10, term=chain.delegate_term[1], fees=1)
        self.test_del.test_delegate_fixed(del_data)
        time.sleep(10)
        delegate_fixed_info = self.handle_q.get_delegate(user_addr)['delegation']
        delegate_fixed_start_height = int(delegate_fixed_info['startHeight'])

        # 10 coin + 1 coin kyc
        stage2_amt = (delegate_fixed_start_height - delegate_start_height) * (one_coin_reward_uc * 11)

        del_data = dict(region_user_addr=f"{user_addr}", amount="10", fees="1")
        self.test_del.test_delegate_infinite(del_data)
        time.sleep(10)
        delegate_infinite_info = self.handle_q.get_delegate(user_addr)['delegation']
        delegate_infinite_start_height = int(delegate_infinite_info['startHeight'])

        # 20 coin + 1 coin kyc
        stage3_amt = (delegate_infinite_start_height - delegate_fixed_start_height) * (one_coin_reward_uc * 21)

        new_info = self.handle_q.get_delegate(user_addr)['delegation']
        interest = new_info['interestAmount']
        end_height = self.handle_q.get_block()
        print(f"块度相差 {int(new_info['startHeight'])} == {end_height}")

        stage4_amt = (end_height - delegate_infinite_start_height) * (one_coin_reward_uc * 31)

        reward = (stage1_amt * 1000000 + stage2_amt * 1000000 + stage3_amt * 1000000 + stage4_amt * 1000000) / 1000000
        logger.info(f"stage1_amt: {stage1_amt}, stage2_amt: {stage2_amt}, "
                    f"stage3_amt: {stage3_amt}, stage4_amt: {stage4_amt}, reward: {reward}")
        assert str(float(interest)) == str(reward)
