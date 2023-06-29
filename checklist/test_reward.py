# -*- coding: utf-8 -*-
import time

import pytest
from loguru import logger

from cases import unitcases
from tools.compute import Compute
from tools.parse_response import HttpResponse


# TODO
#  2.出块减产逻辑 - 5年后才减产,临时版本的项目生命周期预计不到5年,用例优先级不高


@pytest.mark.P0
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

    def test_mint_allot(self):
        """
        验证mint 出块奖励分配
        1.分配至superadmin
        2.分配至region
        """
        start_block_height = HttpResponse.get_current_block()
        superadmin_uc = int(HttpResponse.get_balance_unit(self.base_cfg.super_addr, self.base_cfg.coin['uc'])["amount"])
        superadmin_ug = int(HttpResponse.get_balance_unit(self.base_cfg.super_addr, self.base_cfg.coin['ug'])["amount"])

        all_region = HttpResponse.get_regin_list()
        all_region_total_as = 0
        if all_region:
            all_region_total_as = sum([float(i['regionTotalAS']) for i in all_region["region"]])
        # 计算所有region收益/块
        all_region_amt_uc = self.block_reward_uc * (all_region_total_as / self.base_cfg.total_as)
        # 计算superadmin收益/块
        superadmin_amt_uc = self.block_reward_uc - all_region_amt_uc
        superadmin_amt_ug = superadmin_amt_uc * 400

        time.sleep(10)
        end_block_height = HttpResponse.get_current_block()
        end_uc = int(HttpResponse.get_balance_unit(self.base_cfg.super_addr, self.base_cfg.coin['uc'])["amount"])
        end_ug = int(HttpResponse.get_balance_unit(self.base_cfg.super_addr, self.base_cfg.coin['ug'])["amount"])

        assert end_uc - superadmin_uc == (end_block_height - start_block_height) * superadmin_amt_uc
        assert end_ug - superadmin_ug == (end_block_height - start_block_height) * superadmin_amt_ug

    def test_kyc_reward(self, setup_create_region_and_kyc_user):
        """单独kyc收益"""
        region_admin_addr, region_id, region_name, user_addr = setup_create_region_and_kyc_user
        # kyc计算收益开始高度
        delegate_info = HttpResponse.get_delegate(user_addr)
        start_height = int(delegate_info['startHeight'])

        time.sleep(20)

        delegate_info = HttpResponse.get_delegate(user_addr)
        end_height = HttpResponse.get_current_block()

        x = float((end_height - start_height) * self.kyc_reward_uc)
        assert float(delegate_info['interestAmount']) == x, f"test_kyc_reward failed"

    def test_delegate1_reward(self, setup_create_region_and_kyc_user):
        """计算活期委托 + kyc 收益"""
        region_admin_addr, region_id, region_name, user_addr = setup_create_region_and_kyc_user

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
        self.test_bank.test_send(**send_data)

        kyc_start_height = int(HttpResponse.get_delegate(user_addr)['startHeight'])
        logger.info(f"kyc_start_height: {kyc_start_height}")

        # 发起活期质押后 会更新startHeight
        del_data = dict(from_addr=user_addr, amount=10)
        self.test_del.test_delegate(**del_data)
        time.sleep(10)

        delegate_info = HttpResponse.get_delegate(user_addr)
        interest = delegate_info['interestAmount']
        end_height = HttpResponse.get_current_block()
        stage2_start_height = int(delegate_info['startHeight'])
        logger.info(f"stage2_start_height: {stage2_start_height}, end_height: {end_height}, interestAmount: {interest}")

        stage1_amt = ((stage2_start_height - 1) - kyc_start_height) * self.kyc_reward_uc
        # 10 coin + 1 coin kyc
        stage2_amt = (end_height - stage2_start_height) * (
                self.kyc_reward_uc * 11 * self.base_cfg.precision) / self.base_cfg.precision
        reward = (stage1_amt * self.base_cfg.precision + stage2_amt * self.base_cfg.precision) / self.base_cfg.precision
        logger.info(f"stage1_amt: {stage1_amt}, stage2_amt: {stage2_amt}, reward: {reward}")
        assert str(float(interest)) == str(reward)

    def test_delegate2_fixed(self, setup_create_region_and_kyc_user):
        """计算活期周期委托 + kyc 收益"""
        region_admin_addr, region_id, region_name, user_addr = setup_create_region_and_kyc_user

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
        self.test_bank.test_send(**send_data)

        kyc_start_height = int(HttpResponse.get_delegate(user_addr)['startHeight'])
        logger.info(f"kyc_start_height: {kyc_start_height}")

        # 发起活期质押后 会更新startHeight
        del_data = dict(from_addr=user_addr, amount=10, term=self.base_cfg.delegate_term[1])
        self.test_del.test_delegate_fixed(**del_data)
        time.sleep(10)

        delegate_info = HttpResponse.get_delegate(user_addr)
        interest = delegate_info['interestAmount']
        end_height = HttpResponse.get_current_block()
        stage2_start_height = int(delegate_info['startHeight'])
        logger.info(f"stage2_start_height: {stage2_start_height}, end_height: {end_height}, interestAmount: {interest}")

        stage1_amt = ((stage2_start_height - 1) - kyc_start_height) * self.kyc_reward_uc
        # 10 coin + 1 coin kyc
        stage2_amt = (end_height - stage2_start_height) * (
                self.kyc_reward_uc * 11 * self.base_cfg.precision) / self.base_cfg.precision
        reward = (stage1_amt * self.base_cfg.precision + stage2_amt * self.base_cfg.precision) / self.base_cfg.precision
        logger.info(f"stage1_amt: {stage1_amt}, stage2_amt: {stage2_amt}, reward: {reward}")
        assert str(float(interest)) == str(reward)

    def test_delegate3_infinite(self, setup_create_region_and_kyc_user):
        """计算活期永久委托 + kyc 收益"""
        region_admin_addr, region_id, region_name, user_addr = setup_create_region_and_kyc_user

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
        self.test_bank.test_send(**send_data)

        kyc_start_height = int(HttpResponse.get_delegate(user_addr)['startHeight'])
        logger.info(f"kyc_start_height: {kyc_start_height}")

        # 发起活期质押后 会更新startHeight
        del_data = dict(from_addr=user_addr, amount=10)
        self.test_del.test_delegate_infinite(**del_data)
        time.sleep(10)

        delegate_info = HttpResponse.get_delegate(user_addr)
        interest = delegate_info['interestAmount']
        end_height = HttpResponse.get_current_block()
        stage2_start_height = int(delegate_info['startHeight'])
        logger.info(f"stage2_start_height: {stage2_start_height}, end_height: {end_height}, interestAmount: {interest}")

        stage1_amt = ((stage2_start_height - 1) - kyc_start_height) * self.kyc_reward_uc
        # 10 coin + 1 coin kyc
        stage2_amt = (end_height - stage2_start_height) * \
                     (self.kyc_reward_uc * 11 * self.base_cfg.precision) / self.base_cfg.precision
        reward = (stage1_amt * self.base_cfg.precision + stage2_amt * self.base_cfg.precision) / self.base_cfg.precision
        logger.info(f"stage1_amt: {stage1_amt}, stage2_amt: {stage2_amt}, reward: {reward}")
        assert str(float(interest)) == str(reward)

    def test_delegate123_group(self, setup_create_region_and_kyc_user):
        """委托组合场景收益计算"""
        region_admin_addr, region_id, region_name, user_addr = setup_create_region_and_kyc_user

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
        self.test_bank.test_send(**send_data)

        kyc_start_height = int(HttpResponse.get_delegate(user_addr)['startHeight'])
        logger.info(f"kyc_start_height: {kyc_start_height}")

        # 发起活期质押后 会更新startHeight
        del_data = dict(from_addr=user_addr, amount=10)
        self.test_del.test_delegate(**del_data)
        time.sleep(10)

        delegate_info = HttpResponse.get_delegate(user_addr)
        delegate_start_height = int(delegate_info['startHeight'])
        logger.info(f"delegate_start_height: {delegate_start_height}")
        # 第一部分 只有kyc收益
        stage1_amt = ((delegate_start_height - 1) - kyc_start_height) * self.kyc_reward_uc

        del_data = dict(from_addr=user_addr, amount=10, term=self.base_cfg.delegate_term[1])
        self.test_del.test_delegate_fixed(**del_data)
        time.sleep(10)
        delegate_fixed_info = HttpResponse.get_delegate(user_addr)
        delegate_fixed_start_height = int(delegate_fixed_info['startHeight'])

        # 第二部分 活期委托+kyc收益
        stage2_amt = ((delegate_fixed_start_height - 1) - delegate_start_height) * \
                     (self.kyc_reward_uc * 11 * self.base_cfg.precision) / self.base_cfg.precision

        del_data = dict(from_addr=user_addr, amount=10)
        self.test_del.test_delegate_infinite(**del_data)
        time.sleep(10)
        delegate_infinite_info = HttpResponse.get_delegate(user_addr)
        delegate_infinite_start_height = int(delegate_infinite_info['startHeight'])

        # 第三部分 活期委托+kyc收益+活期内周期收益
        stage3_amt = ((delegate_infinite_start_height - 1) - delegate_fixed_start_height) * \
                     (self.kyc_reward_uc * 21 * self.base_cfg.precision) / self.base_cfg.precision

        interest = HttpResponse.get_delegate(user_addr)['interestAmount']
        end_height = HttpResponse.get_current_block()

        # 第四部分 活期委托+kyc收益+活期内周期收益+永久活期收益
        stage4_amt = (end_height - delegate_infinite_start_height) * \
                     (self.kyc_reward_uc * 31 * self.base_cfg.precision) / self.base_cfg.precision

        reward = (stage1_amt * self.base_cfg.precision + stage2_amt * self.base_cfg.precision +
                  stage3_amt * self.base_cfg.precision + stage4_amt * self.base_cfg.precision) / self.base_cfg.precision
        logger.info(f"stage1_amt: {stage1_amt}, stage2_amt: {stage2_amt}, "
                    f"stage3_amt: {stage3_amt}, stage4_amt: {stage4_amt}, reward: {reward}")
        assert str(float(interest)) == str(reward)

    def test_delegate2_fixed_expire(self, setup_create_region_and_kyc_user):
        """活期周期委托到期后收益计算
            -> 到期之后 不提取的话 那质押本金还享受活期收益"""
        region_admin_addr, region_id, region_name, user_addr = setup_create_region_and_kyc_user

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
        self.test_bank.test_send(**send_data)

        kyc_start_height = int(HttpResponse.get_delegate(user_addr)['startHeight'])
        logger.info(f"kyc_start_height: {kyc_start_height}")

        # 发起活期质押后 会更新startHeight
        del_data = dict(from_addr=user_addr, amount=10, term=self.base_cfg.delegate_term[3])
        self.test_del.test_delegate_fixed(**del_data)

        time.sleep(90 + 10)  # 3 * 30 = 90天 90s < 100s 已到期

        delegate_info = HttpResponse.get_delegate(user_addr)
        interest = delegate_info['interestAmount']
        end_height = HttpResponse.get_current_block()
        stage2_start_height = int(delegate_info['startHeight'])
        logger.info(f"stage2_start_height: {stage2_start_height}, end_height: {end_height}, interestAmount: {interest}")

        stage1_amt = ((stage2_start_height - 1) - kyc_start_height) * self.kyc_reward_uc
        # 10 coin + 1 coin kyc  按最新块计算,即到期后不提取还享受活期收益
        stage2_amt = (end_height - stage2_start_height) * (
                (self.kyc_reward_uc * 11) * self.base_cfg.precision) / self.base_cfg.precision
        reward = (stage1_amt * self.base_cfg.precision + stage2_amt * self.base_cfg.precision) / self.base_cfg.precision
        logger.info(f"stage1_amt: {stage1_amt}, stage2_amt: {stage2_amt}, reward: {reward}")
        assert str(float(interest)) == str(reward)

    def test_delegate2_fixed_withdraw(self, setup_create_region_and_kyc_user):
        """活期内周期提取 -> 本金 + 利息收益 + (三种类型所有)活期收益"""
        region_admin_addr, region_id, region_name, user_addr = setup_create_region_and_kyc_user

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
        self.test_bank.test_send(**send_data)

        kyc_start_height = int(HttpResponse.get_delegate(user_addr)['startHeight'])
        logger.info(f"kyc_start_height: {kyc_start_height}")

        # 发起活期质押后 会更新startHeight
        del_data = dict(from_addr=user_addr, amount=10, term=self.base_cfg.delegate_term[3])
        self.test_del.test_delegate_fixed(**del_data)

        user_addr_balance_uc = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])
        logger.info(f"user_addr_balance_uc: {user_addr_balance_uc}")

        time.sleep(90 + 10)

        delegate_info = HttpResponse.get_delegate(user_addr)
        interest = delegate_info['interestAmount']
        stage2_start_height = int(delegate_info['startHeight'])

        fixed_delegate_info = HttpResponse.show_fixed_delegation(user_addr)
        fixed_delegation_id = fixed_delegate_info['items'][0]['id']
        undelegate_fixed_data = dict(from_addr=user_addr, fixed_delegation_id=fixed_delegation_id)
        self.test_del.test_undelegate_fixed(**undelegate_fixed_data)

        end_height = HttpResponse.get_current_block()
        logger.info(f"stage2_start_height: {stage2_start_height}, end_height: {end_height}, interestAmount: {interest}")

        stage1_amt = ((stage2_start_height - 1) - kyc_start_height) * self.kyc_reward_uc
        stage2_amt = (end_height - stage2_start_height) * (
                (self.kyc_reward_uc * 11) * self.base_cfg.precision) / self.base_cfg.precision

        reward = (stage1_amt * self.base_cfg.precision + stage2_amt * self.base_cfg.precision) / self.base_cfg.precision
        logger.info(f"stage1_amt: {stage1_amt}, stage2_amt: {stage2_amt}, reward: {reward}")
        accrual_u = Compute.interest(amount=Compute.to_u(10), period=3, rate=self.base_cfg.annual_rate[3])
        logger.info(f"accrual_uc: {accrual_u}")

        user_addr_balance_uc = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])
        user_addr_balance_ug = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['ug'])["amount"])
        logger.info(f"user_addr_balance_uc: {user_addr_balance_uc}, user_addr_balance_ug: {user_addr_balance_ug}")

        assert user_addr_balance_uc == Compute.to_u(100 - self.base_cfg.fees * 2) + int(accrual_u) + int(reward)
        assert user_addr_balance_ug == int(accrual_u) + int(reward)

    def test_tx_withdraw(self, setup_create_region_and_kyc_user):
        """主动提取收益(tx withdraw) """
        region_admin_addr, region_id, region_name, user_addr = setup_create_region_and_kyc_user

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=1000000, fees=101, gas=20200000)
        self.test_bank.test_send(**send_data)

        kyc_start_height = int(HttpResponse.get_delegate(user_addr)['startHeight'])
        logger.info(f"kyc_start_height: {kyc_start_height}")

        del_data = dict(from_addr=user_addr, amount=20000)
        resp1 = self.test_del.test_delegate(**del_data)
        resp2 = self.test_del.test_delegate_infinite(**del_data)
        logger.info(f"resp1: {resp1},\n resp2: {resp2}")

        time.sleep(10)

        resp3 = self.test_del.test_withdraw(**dict(addr=user_addr))
        logger.info(f"resp3: {resp3}")

        stage1_amt = (int(resp1['height']) - kyc_start_height) * self.kyc_reward_uc
        stage2_amt = (int(resp2['height']) - 1 - int(resp1['height'])) * \
                     (self.kyc_reward_uc * 20001 * self.base_cfg.precision) / self.base_cfg.precision
        stage3_amt = (int(resp3['height']) - 1 - int(resp2['height'])) * \
                     (self.kyc_reward_uc * 40001 * self.base_cfg.precision) / self.base_cfg.precision
        reward = (stage1_amt * self.base_cfg.precision + stage2_amt * self.base_cfg.precision
                  + stage3_amt * self.base_cfg.precision) / self.base_cfg.precision
        logger.info(f"stage1_amt: {stage1_amt}, stage2_amt: {stage2_amt}, stage3_amt: {stage3_amt}, reward: {reward}")

        user_addr_balance_uc = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])
        logger.info(f"user_addr_balance_uc: {user_addr_balance_uc}")
        user_addr_balance_ug = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['ug'])["amount"])
        logger.info(f"user_addr_balance_ug: {user_addr_balance_ug}")
        assert user_addr_balance_uc == Compute.to_u(1000000 - (20000 * 2) - (self.base_cfg.fees * 3)) + int(reward)
        assert user_addr_balance_ug == int(reward)
