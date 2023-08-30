# -*- coding: utf-8 -*-
import time

import pytest
from loguru import logger

from cases import unitcases
from tools.compute import Compute, WaitBlock
from tools.parse_response import HttpResponse
from tools.rewards import Reward
from x.query import HttpQuery, Query
from x.tx import Tx


@pytest.mark.P0
class TestSendCoin(object):
    test_region = unitcases.Region()
    test_del = unitcases.Delegate()
    test_kyc = unitcases.Kyc()
    test_key = unitcases.Keys()
    test_bank = unitcases.Bank()
    test_validator = unitcases.Validator()
    base_cfg = test_bank.tx
    tx = Tx()
    hq = HttpQuery()
    q = Query()
    user_addr = None

    def test_different_fees_delegate(self):
        """
        在费率不同的验证者节点之间交叉委托、赎回
        @Desc
            - node1 和 node7 的节点费率不同
            - 用户通过node1节点验证委托
            - 用户通过node7节点验证赎回
            + expect:委托和赎回正常，收费费分别按对应的扣除
        """
        logger.info("TestSendCoin/test_different_fees_delegate")
        user_addr = self.test_key.test_add()['address']
        time.sleep(self.tx.sleep_time*2)

        self.base_cfg.Bank.send_to_admin(amount=(300 + 1))  # 怕管理员没钱，国库先转钱给管理员
        time.sleep(self.tx.sleep_time)

        # 超管给用户转100mec
        send_data = dict(from_addr=self.tx.super_addr, to_addr=user_addr, amount=300)
        self.test_bank.test_send(**send_data)

        before_balance = self.hq.bank.query_balances(user_addr)
        # 用户发起活期委托,使用节点node1进行验证
        delegate_amount = 100
        delegate_data = dict(from_addr=user_addr, amount=delegate_amount, node_ip=self.tx.node_id['node1'])
        resp = self.tx.staking.delegate(**delegate_data)
        code = self.hq.tx.query_tx(resp['txhash'])['code']
        assert code == 0

        # 查询用户的活期委托 拿到块高
        start_height = (HttpQuery.Staking.delegation(addr=user_addr))['startHeight']

        # 验证用户的余额应该 =  发起活期委托之前的余额 - 活期委托的金额 - 手续费
        after_balance = self.hq.bank.query_balances(user_addr)
        assert after_balance == before_balance - Compute.to_u(delegate_amount) - self.base_cfg.fees

        # 查询用户的非kyc委托 应该是发起活期委托的金额
        user_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user_delegate_info['unKycAmount']) == Compute.to_u(delegate_amount)

        # 赎回委托的金额,使用node7的节点进行验证，这里node7的基础手续费时200umec
        un_delegate_amount = delegate_amount
        un_del_data = dict(from_addr=user_addr, amount=un_delegate_amount, fees=self.base_cfg.fees*2,
                           node_ip=self.tx.node_id['node7'])
        result = self.test_del.test_undelegate_nokyc(**un_del_data)
        assert resp['code'] == 0

        # 计算收益
        end_height = int((Query.Tx.query_tx(tx_hash=result['txhash']))['height'])
        reward = Reward.reward_nokyc(stake=float(delegate_amount), start_height=start_height, end_height=end_height)

        # 赎回金额不会立马到帐，只有收益到帐  这里node7的基础手续费时200umec
        end_balance = self.hq.bank.query_balances(user_addr)
        assert end_balance + self.base_cfg.fees*2 - after_balance == reward

        self.tx.keys.delete(self.q.key.name_of_addre(user_addr))

    def test_no_kyc_to_kyc_fees(self):
        """
        验证一个用户从非kyc开始进行活期委托，然后赎回委托，然后认证为kyc，再进行委托，最后全部赎回
        @Desc
            - user 新增一个用户
            - 超管给用户发钱
            - 用户第一次进行活期委托
            + expect:活期委托交易成功，用户余额扣除活期委托金额和手续费，用户非kyc委托增加金额与委托金额一致
            - 用户第二次进行活期委托
            + expect:活期委托交易成功，计算之前已存在的活期委托收益，收益进入用户的余额账户
            - 用户认证为kyc用户，并进行活期委托
            + expect：用户同时存在kyc委托和非kyc委托，金额正确
            - 赎回所有委托
            + expect: kyc委托金额赎回即时到帐，收益也到帐,非kyc委托金额只有收益到帐
        """
        logger.info("TestRegionDelegate/test_no_kyc_to_kyc_user_more_delegate")
        user_addr = self.test_key.test_add()['address']
        time.sleep(self.tx.sleep_time)

        self.base_cfg.Bank.send_to_admin(amount=(500 + 1))  # 怕管理员没钱，国库先转钱给管理员
        time.sleep(self.tx.sleep_time)

        # 超管给用户转100mec
        send_data = dict(from_addr=self.tx.super_addr, to_addr=user_addr, amount=500)
        self.test_bank.test_send(**send_data)

        before_balance = self.hq.bank.query_balances(user_addr)
        # 用户第一次发起活期委托
        delegate_amount = 100
        delegate_data = dict(from_addr=user_addr, amount=delegate_amount)
        resp = self.tx.staking.delegate(**delegate_data)
        code = self.hq.tx.query_tx(resp['txhash'])['code']
        assert code == 0

        # 查询用户的活期委托 拿到块高
        start_height = (HttpQuery.Staking.delegation(addr=user_addr))['startHeight']

        # 验证用户的余额应该 =  发起活期委托之前的余额 - 活期委托的金额 - 手续费
        after_balance = self.hq.bank.query_balances(user_addr)
        assert after_balance == before_balance - Compute.to_u(delegate_amount) - self.base_cfg.fees

        # 查询用户的非kyc委托 应该是发起活期委托的金额
        user_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user_delegate_info['unKycAmount']) == Compute.to_u(delegate_amount)

        # 用户发起第二次活期委托，非kyc存在已有活期委托时再进行活期委托会先计算上一笔活期委托的所有收益
        delegate_amount = 100
        delegate_data = dict(from_addr=user_addr, amount=delegate_amount)
        resp = self.tx.staking.delegate(**delegate_data)
        code = self.hq.tx.query_tx(resp['txhash'])['code']
        assert code == 0

        # 查询用户的活期委托 拿到块高 这里的开始块高就是计算上一笔活期委托收益的结束块高
        end_height = (HttpQuery.Staking.delegation(addr=user_addr))['startHeight']
        reward = Reward.reward_nokyc(stake=float(delegate_amount), start_height=start_height, end_height=end_height)
        # 赎回金额不会立马到帐，只有收益到帐
        end_balance = self.hq.bank.query_balances(user_addr)
        # 计算出的收益与实际收益一致  余额+2次手续费+2次活期委托的金额-没有进行交易时的余额 = 收益
        assert end_balance + self.base_cfg.fees * 2 + Compute.to_u(delegate_amount * 2) - before_balance == reward

        kyc_start_balance = self.hq.bank.query_balances(user_addr)
        # 将用户认证成kyc
        self.test_kyc.test_new_kyc_user_not_in_node5(addr=user_addr)
        kyc_end_balance = self.hq.bank.query_balances(user_addr)
        # 完成kyc认证后会转入一笔费用到unmovable，所以也需要计算一次非kyc时候的活期委托
        kyc_height = (HttpQuery.Staking.delegation(addr=user_addr))['startHeight']
        un_kyc_reward1 = Reward.reward_nokyc(stake=float(delegate_amount * 2),
                                             start_height=end_height, end_height=kyc_height)

        # 认证完kyc后的余额
        kyc_delegate_before_balance = self.hq.bank.query_balances(user_addr)

        # 如果还有非kyc认证时候的委托，完成kyc人在后会产生收益吗？

        # 用户进行活期委托
        kyc_delegate_amount = 100
        kyc_delegate_data = dict(from_addr=user_addr, amount=kyc_delegate_amount)
        resp = self.tx.staking.delegate(**kyc_delegate_data)
        code = self.hq.tx.query_tx(resp['txhash'])['code']
        assert code == 0
        kyc_delegate_end_balance = self.hq.bank.query_balances(user_addr)
        # 当前活期委托数据应该等于委托数据
        user1_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user1_delegate_info['amount']) == Compute.to_u(delegate_amount)

        # 完成kyc活期委托后要计算一笔 非kyc时活期的收益
        kyc_start_height = (HttpQuery.Staking.delegation(addr=user_addr))['startHeight']
        un_kyc_reward2 = Reward.reward_nokyc(stake=float(delegate_amount * 2),
                                             start_height=kyc_height, end_height=kyc_start_height)

        # 赎回kyc活期委托，并计算收益
        result = Tx.Staking.undelegate_kyc(from_addr=user_addr, amount=float(kyc_delegate_amount))
        self.hq.tx.query_tx(result['txhash'])
        kyc_end_height = int((Query.Tx.query_tx(tx_hash=result['txhash']))['height'])
        # 计算出用户的活期委托收益
        reward = Reward.reward_kyc(stake=float(kyc_delegate_amount),
                                   start_height=kyc_start_height, end_height=kyc_end_height)

        # 完成赎回时也要计算一次非kyc时委托的收益
        un_kyc_reward3 = Reward.reward_nokyc(stake=float(delegate_amount * 2), start_height=kyc_height,
                                             end_height=kyc_start_height)
        un_kyn_reward = un_kyc_reward1 + un_kyc_reward2 + un_kyc_reward3
        kyc_delegate_after_balance = self.hq.bank.query_balances(user_addr)
        # 最后的余额 + 两次手续非 - 开始kyc认证前的余额 - 非kyc委托部分的收益 = kyc后活期委托的收益
        assert kyc_delegate_after_balance + self.base_cfg.fees * 2 - kyc_start_balance - un_kyn_reward == reward
        # 删除用户
        self.tx.keys.delete(self.q.key.name_of_addre(user_addr))

    # def test_ag_to_ac(self, setup_create_region):
    #     logger.info("TestSendCoin/test_ag_to_ac")
    #     region_admin_info, region_id, region_name = setup_create_region
    #     region_admin_addr = region_admin_info['address']
    #
    #     new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
    #     user_info = self.test_kyc.test_new_kyc_user(**new_kyc_data)
    #     user_addr = user_info['address']
    #
    #     send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=500)
    #     self.test_bank.test_send(**send_data)
    #
    #     region_info = HttpResponse.get_region(region_id)
    #     region_base_addr = region_info['region']['baseAccountAddr']
    #     base_uc_balance = HttpResponse.get_balance_unit(region_base_addr, self.base_cfg.coin['uc'])
    #     base_ug_balance = HttpResponse.get_balance_unit(region_base_addr, self.base_cfg.coin['ug'])
    #     logger.info(f"base_uc_balance: {base_uc_balance}, base_ug_balance: {base_ug_balance}")
    #
    #     fixed_data = dict(amount=200, period=self.base_cfg.period[1], from_addr=user_addr)
    #     self.test_fixed.test_create_fixed_deposit(**fixed_data)
    #
    #     # 验证用户余额
    #     user_balance_uc = HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])
    #     assert int(user_balance_uc['amount']) == Compute.to_u(500 - 200 - self.base_cfg.fees)
    #
    #     # 验证区金库信息
    #     region_fixed_addr = region_info['region']['fixedDepositAccountAddr']
    #     fixed_balance_uc = HttpResponse.get_balance_unit(region_fixed_addr, self.base_cfg.coin['uc'])
    #     assert int(fixed_balance_uc['amount']) == Compute.to_u(200)
    #
    #     # 查用户定期信息
    #     user_fixed_info = HttpResponse.get_fixed_deposit_by_addr(user_addr, self.base_cfg.fixed_type['all'])
    #     fixed_list = user_fixed_info['FixedDeposit']
    #     fixed_info = [i for i in fixed_list if i['account'] == user_addr][0]
    #     _fixed_id = fixed_info['id']
    #     _fixed_end_height = fixed_info['end_height']
    #     user1_fixed_info = [i for i in fixed_list if i['account'] == user_addr][0]
    #     assert int(user1_fixed_info['amount']) == Compute.to_u(200)
    #
    #     # 需要wait-block
    #     logger.info(f'{"到期赎回质押":*^50s}')
    #     WaitBlock.wait_block_for_height(height=_fixed_end_height)
    #     u_fees = Compute.to_u(self.base_cfg.fees)
    #
    #     fixed_data = dict(deposit_id=_fixed_id, from_addr=user_addr)
    #     self.test_fixed.test_withdraw_fixed_deposit(**fixed_data)
    #
    #     logger.info(f'{"返回质押本金+定期收益, 并且无定期质押":*^50s}')
    #     resp_user_uc = HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])
    #     assert int(resp_user_uc['amount']) == int(user_balance_uc['amount']) + Compute.to_u(200) - u_fees
    #     resp_user_ug = HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['ug'])
    #     # 计算定期收益 0.06 * 1 / 12 * (200 * 1000000) * 400 = 400000000ug  区金库:1100000000ug
    #     uac = Compute.to_u(Compute.interest(200, 1, self.base_cfg.annual_rate[1]))
    #     uag = Compute.ag_to_ac(number=uac, reverse=True)
    #     assert int(resp_user_ug['amount']) == uag
    #
    #     # ag to ac
    #     ag = Compute.to_u(uag, reverse=True)
    #     ag_data = dict(ag_amount=ag, from_addr=user_addr)
    #     self.test_kyc.tx.Staking.ag_to_ac(**ag_data)
    #     time.sleep(self.base_cfg.sleep_time)
    #
    #     # check balances
    #     to_uac = Compute.ag_to_ac(uag)
    #     resp2_user_uc = HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])
    #     assert int(resp2_user_uc['amount']) == int(resp_user_uc['amount']) - u_fees + to_uac
    #
    # def test_transfer(self, setup_create_region):
    #     logger.info("TestSendCoin/test_transfer")
    #     region_admin_info, region_id, region_name = setup_create_region
    #     region_admin_addr = region_admin_info['address']
    #
    #     user_info = self.test_keys.test_add()
    #     user_addr = user_info['address']
    #
    #     region_admin_uc = HttpResponse.get_balance_unit(region_admin_addr, self.base_cfg.coin['uc'])
    #
    #     data = dict(from_addr=region_admin_addr, to_addr=user_addr, amount=10)
    #     self.test_bank.test_send(**data)
    #
    #     region_admin_uc2 = HttpResponse.get_balance_unit(region_admin_addr, self.base_cfg.coin['uc'])
    #     expect_data = int(region_admin_uc['amount']) - Compute.to_u(10 + (self.base_cfg.fees * self.base_cfg.fee_rate))
    #     assert int(region_admin_uc2['amount']) == expect_data
    #
    #     user_uc = HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])
    #     assert int(user_uc['amount']) == Compute.to_u(10)
    #
    # def test_fee_rate(self, setup_create_region):
    #     """测试交易手续费收取比例"""
    #     region_admin_info, region_id, region_name = setup_create_region
    #     region_admin_addr = region_admin_info['address']
    #
    #     new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
    #     user_info = self.test_kyc.test_new_kyc_user(**new_kyc_data)
    #     user_addr = user_info['address']
    #
    #     send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=500)
    #     self.test_bank.test_send(**send_data)
    #
    #     start_region_uc = HttpResponse.get_balance_unit(region_admin_addr, self.base_cfg.coin['uc'])
    #
    #     send_data = dict(from_addr=user_addr, to_addr=region_admin_addr, amount=100)
    #     self.test_bank.test_send(**send_data)
    #
    #     region_admin_uc = HttpResponse.get_balance_unit(region_admin_addr, self.base_cfg.coin['uc'])
    #     user_uc = HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])
    #
    #     region_admin_expect_amt = Compute.to_u(self.base_cfg.fees * self.base_cfg.fee_rate) + Compute.to_u(100)
    #     assert int(region_admin_uc['amount']) - int(start_region_uc['amount']) == region_admin_expect_amt
    #     assert int(user_uc['amount']) == Compute.to_u(500 - 100 - self.base_cfg.fees)
