# -*- coding: utf-8 -*-
import time

import pytest
from loguru import logger

from cases import package
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
    #  2.出块减产逻辑 - 5年后才减产,临时版本的项目生命周期预计不到5年,用例优先级不高

    def test_kyc_reward(self, setup_create_region):
        """单独kyc收益"""
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
        """计算活期委托 + kyc 收益"""
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
        stage2_amt = (end_height - stage2_start_height) * \
                     (one_coin_reward_uc * 11 * chain.float_precision) / chain.float_precision
        reward = (stage1_amt * chain.float_precision + stage2_amt * chain.float_precision) / chain.float_precision
        logger.info(f"stage1_amt: {stage1_amt}, stage2_amt: {stage2_amt}, reward: {reward}")
        assert str(float(interest)) == str(reward)

    def test_delegate2_fixed(self, setup_create_region):
        """计算活期周期委托 + kyc 收益"""
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
        stage2_amt = (end_height - stage2_start_height) * (
                one_coin_reward_uc * 11 * chain.float_precision) / chain.float_precision
        reward = (stage1_amt * chain.float_precision + stage2_amt * chain.float_precision) / chain.float_precision
        logger.info(f"stage1_amt: {stage1_amt}, stage2_amt: {stage2_amt}, reward: {reward}")
        assert str(float(interest)) == str(reward)

    def test_delegate3_infinite(self, setup_create_region):
        """计算活期永久委托 + kyc 收益"""
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
        stage2_amt = (end_height - stage2_start_height) * \
                     (one_coin_reward_uc * 11 * chain.float_precision) / chain.float_precision
        reward = (stage1_amt * chain.float_precision + stage2_amt * chain.float_precision) / chain.float_precision
        logger.info(f"stage1_amt: {stage1_amt}, stage2_amt: {stage2_amt}, reward: {reward}")
        assert str(float(interest)) == str(reward)

    def test_delegate123_group(self, setup_create_region):
        """委托组合场景收益计算"""
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
        logger.info(f"delegate_start_height: {delegate_start_height}")
        # 第一部分 只有kyc收益
        stage1_amt = ((delegate_start_height - 1) - kyc_start_height) * one_coin_reward_uc

        del_data = dict(region_user_addr=f"{user_addr}", amount=10, term=chain.delegate_term[1], fees=1)
        self.test_del.test_delegate_fixed(del_data)
        time.sleep(10)
        delegate_fixed_info = self.handle_q.get_delegate(user_addr)['delegation']
        delegate_fixed_start_height = int(delegate_fixed_info['startHeight'])

        # 第二部分 活期委托+kyc收益
        stage2_amt = ((delegate_fixed_start_height - 1) - delegate_start_height) * \
                     (one_coin_reward_uc * 11 * chain.float_precision) / chain.float_precision

        del_data = dict(region_user_addr=f"{user_addr}", amount="10", fees="1")
        self.test_del.test_delegate_infinite(del_data)
        time.sleep(10)
        delegate_infinite_info = self.handle_q.get_delegate(user_addr)['delegation']
        delegate_infinite_start_height = int(delegate_infinite_info['startHeight'])

        # 第三部分 活期委托+kyc收益+活期内周期收益
        stage3_amt = ((delegate_infinite_start_height - 1) - delegate_fixed_start_height) * \
                     (one_coin_reward_uc * 21 * chain.float_precision) / chain.float_precision

        interest = self.handle_q.get_delegate(user_addr)['delegation']['interestAmount']
        end_height = self.handle_q.get_block()

        # 第四部分 活期委托+kyc收益+活期内周期收益+永久活期收益
        stage4_amt = (end_height - delegate_infinite_start_height) * \
                     (one_coin_reward_uc * 31 * chain.float_precision) / chain.float_precision

        reward = (stage1_amt * chain.float_precision + stage2_amt * chain.float_precision +
                  stage3_amt * chain.float_precision + stage4_amt * chain.float_precision) / chain.float_precision
        logger.info(f"stage1_amt: {stage1_amt}, stage2_amt: {stage2_amt}, "
                    f"stage3_amt: {stage3_amt}, stage4_amt: {stage4_amt}, reward: {reward}")
        assert str(float(interest)) == str(reward)

    def test_delegate2_fixed_expire(self, setup_create_region):
        """活期周期委托到期后收益计算
            -> 到期之后 不提取的话 那质押本金还享受活期收益"""
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
        del_data = dict(region_user_addr=f"{user_addr}", amount=10, term=chain.delegate_term[3], fees=1)
        self.test_del.test_delegate_fixed(del_data)

        time.sleep(90 + 10)  # 3 * 30 = 90天 90s < 100s 已到期

        delegate_info = self.handle_q.get_delegate(user_addr)['delegation']
        interest = delegate_info['interestAmount']
        end_height = self.handle_q.get_block()
        stage2_start_height = int(delegate_info['startHeight'])
        logger.info(f"stage2_start_height: {stage2_start_height}, end_height: {end_height}, interestAmount: {interest}")

        stage1_amt = ((stage2_start_height - 1) - kyc_start_height) * one_coin_reward_uc
        # 10 coin + 1 coin kyc  按最新块计算,即到期后不提取还享受活期收益
        stage2_amt = (end_height - stage2_start_height) * (
                (one_coin_reward_uc * 11) * chain.float_precision) / chain.float_precision
        reward = (stage1_amt * chain.float_precision + stage2_amt * chain.float_precision) / chain.float_precision
        logger.info(f"stage1_amt: {stage1_amt}, stage2_amt: {stage2_amt}, reward: {reward}")
        assert str(float(interest)) == str(reward)

    def test_delegate2_fixed_withdraw(self, setup_create_region):
        """活期内周期提取 -> 本金 + 利息收益 + (三种类型所有)活期收益"""
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
        del_data = dict(region_user_addr=f"{user_addr}", amount=10, term=chain.delegate_term[3], fees=1)
        self.test_del.test_delegate_fixed(del_data)

        user_addr_balance_uc = int(self.handle_q.get_balance(user_addr, chain.coin['uc'])["amount"])
        logger.info(f"user_addr_balance_uc: {user_addr_balance_uc}")

        time.sleep(90 + 10)

        delegate_info = self.handle_q.get_delegate(user_addr)['delegation']
        interest = delegate_info['interestAmount']
        stage2_start_height = int(delegate_info['startHeight'])

        fixed_delegate_info = self.handle_q.q.staking.show_fixed_delegation(user_addr)
        fixed_delegation_id = fixed_delegate_info['items'][0]['id']
        undelegate_fixed_data = dict(from_addr=user_addr, fixed_delegation_id=fixed_delegation_id, fees=2, gas=400000)
        self.test_del.test_undelegate_fixed(undelegate_fixed_data)
        end_height = self.handle_q.get_block()
        logger.info(f"stage2_start_height: {stage2_start_height}, end_height: {end_height}, interestAmount: {interest}")

        stage1_amt = ((stage2_start_height - 1) - kyc_start_height) * one_coin_reward_uc
        stage2_amt = (end_height - stage2_start_height) * (
                (one_coin_reward_uc * 11) * chain.float_precision) / chain.float_precision

        reward = (stage1_amt * chain.float_precision + stage2_amt * chain.float_precision) / chain.float_precision
        logger.info(f"stage1_amt: {stage1_amt}, stage2_amt: {stage2_amt}, reward: {reward}")
        accrual = chain.annualRate[3] * 3 / 12 * (10 * 10 ** 6)
        logger.info(f"accrual: {accrual}uc")

        user_addr_balance_uc = int(self.handle_q.get_balance(user_addr, chain.coin['uc'])["amount"])
        user_addr_balance_ug = int(self.handle_q.get_balance(user_addr, chain.coin['ug'])["amount"])

        logger.info(f"user_addr_balance_uc: {user_addr_balance_uc}, user_addr_balance_ug: {user_addr_balance_ug}")

        assert user_addr_balance_uc == calculate.to_usrc(100 - 1 - 2) + int(accrual) + int(reward)
        assert user_addr_balance_ug == int(accrual) + int(reward)

    def test_tx_withdraw(self, setup_create_region):
        """主动提取收益(tx withdraw) """
        region_admin_addr, region_id, region_name, _ = setup_create_region
        user_addr = self.test_kyc.test_new_kyc_user(dict(region_id=region_id, region_admin_addr=region_admin_addr))
        send_data = dict(from_addr=chain.super_addr, to_addr=user_addr, amount=1000000, fees=101, gas=20200000)
        self.test_bank.test_send(send_data)

        kyc_start_height = int(self.handle_q.get_delegate(user_addr)['delegation']['startHeight'])
        logger.info(f"kyc_start_height: {kyc_start_height}")  # 4958

        del_data = dict(region_user_addr=f"{user_addr}", amount=20000, fees="1")
        resp1 = self.test_del.test_delegate(del_data)
        resp2 = self.test_del.test_delegate_infinite(del_data)
        logger.info(f"resp1: {resp1},\n resp2: {resp2}")  # 4962/4964

        time.sleep(10)

        resp3 = self.test_del.test_withdraw(dict(user_addr=user_addr, fees=2, gas=400000))
        logger.info(f"resp3: {resp3}")  # 4967

        stage1_amt = (int(resp1['height']) - kyc_start_height) * 0.008
        stage2_amt = (int(resp2['height']) - 1 - int(resp1['height'])) * \
                     (0.008 * 20001 * chain.float_precision) / chain.float_precision
        stage3_amt = (int(resp3['height']) - 1 - int(resp2['height'])) * \
                     (0.008 * 40001 * chain.float_precision) / chain.float_precision
        reward = (stage1_amt * chain.float_precision + stage2_amt * chain.float_precision
                  + stage3_amt * chain.float_precision) / chain.float_precision

        user_addr_balance_uc = int(self.handle_q.get_balance(user_addr, chain.coin['uc'])["amount"])
        logger.info(f"user_addr_balance_uc: {user_addr_balance_uc}")
        user_addr_balance_ug = int(self.handle_q.get_balance(user_addr, chain.coin['ug'])["amount"])
        logger.info(f"user_addr_balance_ug: {user_addr_balance_ug}")
        assert user_addr_balance_uc == calculate.to_usrc(1000000 - (20000 * 2 + 4)) + int(reward)
        assert user_addr_balance_ug == int(reward)
